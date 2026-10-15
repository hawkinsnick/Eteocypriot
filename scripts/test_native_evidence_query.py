"""Loss, source-pin, identity, path and editorial-boundary tests for native queries."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import evidence_query as q


class NativeEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = q.Evidence()

    def test_committed_coverage_replays_without_pooled_counts(self):
        actual = json.loads((q.ROOT / q.REPORT).read_text())
        self.assertEqual(actual, self.evidence.coverage())
        self.assertIsNone(actual['alternative_pair_count'])
        self.assertIsNone(actual['independent_witness_count'])
        self.assertNotIn('total_inscriptions', actual)

    def test_every_registered_record_keeps_all_native_fields_and_exact_locator(self):
        for name, collection in self.evidence.collections.items():
            for record in collection['records']:
                result = self.evidence.dossier(record['id'], name)
                source = self.evidence.artifacts[collection['spec']['path']]['value']
                expected = q.pointer(source, record['pointer'])
                self.assertEqual(result['native_record'], expected)
                self.assertEqual(result['provenance']['pointer'], record['pointer'])
                self.assertEqual(result['provenance']['sha256'], collection['spec']['path'] and
                                 self.evidence.artifacts[collection['spec']['path']]['spec']['sha256'])
                self.assertIn('not all resources assert facts', result['context_resource_scope'])

    def test_no_fuzzy_or_unregistered_lookup(self):
        with self.assertRaisesRegex(ValueError, 'exact native ID absent'):
            self.evidence.dossier('__ABSENT_NATIVE_RECORD__')
        with self.assertRaisesRegex(ValueError, 'not registered'):
            self.evidence.artifact('../outside.json')
        with self.assertRaisesRegex(ValueError, 'unknown collection'):
            self.evidence.inventory('__ABSENT_COLLECTION__')

    def fixture(self, root):
        (root / 'research').mkdir()
        (root / 'scripts').mkdir()
        (root / 'scripts/evidence_query.py').write_bytes(Path(q.__file__).read_bytes())
        value = [{'id': 'A/1', 'text': '[ạ]? | b', 'restoration': None,
                  'reviewed': False, 'source': {'locator': 'p. 7', 'license': 'SOURCE-SPECIFIC'}}]
        raw = json.dumps(value, ensure_ascii=False).encode()
        (root / 'research/native.json').write_bytes(raw)
        profile = {'format': 'corpus-native-evidence-query-v1', 'repository': 'fixture/native',
                   'artifacts': [{'path': 'research/native.json', 'sha256': q.sha(raw),
                                  'encoding': 'json', 'role': 'fixture'}],
                   'collections': [{'name': 'native', 'path': 'research/native.json', 'pointer': '',
                                    'id_pointer': '/id', 'unit': 'source record', 'scope': 'fixture'}],
                   'scholarly_limits': ['No adjudication'], 'relations': []}
        self.save(root, profile)
        return profile, value

    def save(self, root, profile):
        (root / q.PROFILE).write_text(json.dumps(profile))

    def test_editorial_marks_unknowns_and_rights_are_literal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, value = self.fixture(root)
            result = q.Evidence(root).dossier('A/1', 'native')
            self.assertEqual(result['native_record'], value[0])
            self.assertEqual(result['native_record']['text'], '[ạ]? | b')
            self.assertIsNone(result['native_record']['restoration'])
            self.assertFalse(result['native_record']['reviewed'])
            with self.assertRaises(ValueError):
                q.Evidence(root).dossier('a/1', 'native')

    def test_source_corruption_rejected_before_query(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root)
            (root / 'research/native.json').write_text('[]')
            with self.assertRaisesRegex(ValueError, 'source pin mismatch'):
                q.Evidence(root)

    def test_duplicate_missing_or_ambiguous_identifiers_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            profile, value = self.fixture(root)
            profile['collections'].append(dict(profile['collections'][0], name='other-view'))
            self.save(root, profile)
            with self.assertRaisesRegex(ValueError, 'ambiguous ID'):
                q.Evidence(root).dossier('A/1')
            for bad, message in [(value + value, 'duplicate ID'), ([{'text': 'unknown'}], None)]:
                raw = json.dumps(bad).encode()
                (root / 'research/native.json').write_bytes(raw)
                profile['artifacts'][0]['sha256'] = q.sha(raw)
                self.save(root, profile)
                with self.assertRaises((ValueError, KeyError)):
                    q.Evidence(root)

    def test_path_escape_and_outside_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'repo'
            root.mkdir()
            profile, _ = self.fixture(root)
            outside = Path(td) / 'outside.json'
            outside.write_text('[]')
            (root / 'research/link.json').symlink_to(outside)
            for path in ['../outside.json', str(outside), 'research/link.json']:
                with self.assertRaisesRegex(ValueError, 'unsafe'):
                    q.local(root, path)

    def test_json_pointer_escaping_and_array_identity(self):
        self.assertEqual(q.pointer({'a/b': {'~t': ['[x]?']}}, '/a~1b/~0t/0'), '[x]?')
        for path in ['/a~2b', '/00', '/-1']:
            with self.assertRaises(ValueError):
                q.pointer(['x'], path)

    def test_links_use_only_declared_equal_keys_and_never_self_link(self):
        for name, collection in self.evidence.collections.items():
            for row in collection['records']:
                result = self.evidence.dossier(row['id'], name)
                for linked in result['explicitly_linked_records']:
                    rules = [r for r in self.evidence.profile.get('relations', [])
                             if r['from'] == name and r['to'] == linked['collection']]
                    self.assertTrue(any(q.pointer(row['value'], r['from_pointer']) ==
                                        q.pointer(linked['native_record'], r['to_pointer']) == linked['join_value']
                                        for r in rules))
                    self.assertFalse(linked['collection'] == name and linked['provenance']['pointer'] == row['pointer'])


if __name__ == '__main__':
    unittest.main()
