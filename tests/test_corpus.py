import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from etec.core import ROOT, audit, language_decision, parse_record, read_json, render, tokens, validate
from etec.__main__ import export, frequencies, verify_export
from etec.family import validate_family

class ComponentSemantics(unittest.TestCase):
    def test_uncertain_translation_overrides_title(self):
        c = language_decision('eteokyprisch', '[eteokyprisch?]', ET.fromstring('<ab>a-na</ab>'))
        self.assertEqual(c['code'], 'uncertain')
        self.assertFalse(c['analysis_eligible'])

    def test_alternative_language_title_excluded(self):
        c = language_decision('eteokyprisch oder syllabisch?', '[eteokyprisch]', ET.fromstring('<ab>a-na</ab>'))
        self.assertEqual(c['code'], 'uncertain')

    def test_question_about_object_type_does_not_invent_language_uncertainty(self):
        c = language_decision('Besitzerinschrift?, eteokyprisch', '[eteokyprisch]', ET.fromstring('<ab>a-na</ab>'))
        self.assertEqual(c['code'], 'eteocypriot')

    def test_no_label_is_not_admitted(self):
        self.assertFalse(language_decision('eteokyprisch', '', ET.fromstring('<ab>a-na</ab>'))['analysis_eligible'])

    def test_greek_parallel_is_not_counted_as_eteocypriot(self):
        c = language_decision('eteokyprisch und griechisch', 'City', ET.fromstring('<ab>ἡ πόλις</ab>'), True)
        self.assertEqual(c['code'], 'grc')
        self.assertFalse(c['analysis_eligible'])

    def test_unsupported_greek_parallel_rejected(self):
        with self.assertRaises(ValueError):
            language_decision('eteokyprisch und griechisch', 'City', ET.fromstring('<ab>a-na</ab>'), True)

    def test_damaged_and_metadata_spans_excluded(self):
        inventory = read_json(ROOT / 'data/signs.json')
        text = 'a-na a-ṇạ [a]-na a-na..\nvacat a'
        part = ET.fromstring('<ab/>')
        rows = tokens(part, text, inventory)
        self.assertEqual([r['raw'] for r in rows if r['syllabic_labels']], ['a-na'])

    def test_semantic_supplied_element_excluded(self):
        inventory = read_json(ROOT / 'data/signs.json')
        part = ET.fromstring('<ab><supplied>a-na</supplied></ab>')
        self.assertFalse(any(r['syllabic_labels'] for r in tokens(part, render(part), inventory)))

class SourceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = read_json(ROOT / 'data/records.json')
        cls.acquisition = read_json(ROOT / 'data/acquisition.json')

    def test_full_source_replay(self):
        self.assertEqual(validate(), [])

    def test_bilingual_components_have_cited_assignments(self):
        for n in [1, 2, 7]:
            r = next(r for r in self.records if r['source_id'] == f'IG XV 1, {n}')
            self.assertEqual([(c['source_part'], c['language']['code']) for c in r['components']], [('I', 'eteocypriot'), ('II', 'grc')])
            self.assertTrue(all(c['source_language_evidence'] for c in r['components']))

    def test_110_is_uncertain(self):
        r = next(r for r in self.records if r['source_id'] == 'IG XV 1, 110')
        self.assertEqual(r['components'][0]['language']['code'], 'uncertain')

    def test_fragment_labels_not_collapsed(self):
        r = next(r for r in self.records if r['source_id'] == 'IG XV 1, 16')
        self.assertEqual([c['source_part'] for c in r['components']], ['A', 'B'])

    def test_quarantine_not_parsed(self):
        self.assertNotIn('IG XV 1, 150', {r['source_id'] for r in self.records})
        self.assertEqual(audit()['quarantined_entries'], ['IG XV 1, 150'])

    def test_exact_token_offsets(self):
        for r in self.records:
            for c in r['components']:
                for t in c['tokens']:
                    self.assertEqual(c['text'][t['start']:t['end']], t['raw'])

    def test_published_subset_frequency_excludes_parallel_and_uncertain(self):
        sample = copy.deepcopy(self.records)
        before = frequencies(sample)
        for r in sample:
            for c in r['components']:
                if not c['language']['analysis_eligible']:
                    c['tokens'] = [{'status': 'conservative_clear', 'syllabic_labels': ['za'] * 999}]
        self.assertEqual(frequencies(sample), before)

    def test_unknown_objects_not_fabricated(self):
        self.assertTrue(all(r['object_id'] is None and r['independent_witness_id'] is None for r in self.records))

    def test_wrong_source_identity_rejected(self):
        r = copy.deepcopy(self.acquisition[0]);r['id'] = 'WRONG'
        with self.assertRaises(ValueError):
            parse_record(ROOT / r['path'], r, read_json(ROOT / 'data/signs.json'))

    def test_changed_language_assignment_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);shutil.copytree(ROOT / 'data', root / 'data')
            rs = read_json(root / 'data/records.json')
            rs[0]['components'][0]['language']['code'] = 'grc'
            (root / 'data/records.json').write_text(json.dumps(rs))
            self.assertIn('Records differ from deterministic source replay', validate(root))

    def test_changed_raw_source_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);shutil.copytree(ROOT / 'data', root / 'data')
            path = root / self.acquisition[0]['path'];path.write_bytes(path.read_bytes() + b'\n')
            self.assertTrue(any('hash differs' in e for e in validate(root)))

    def test_unsafe_source_path_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);shutil.copytree(ROOT / 'data', root / 'data')
            rows = read_json(root / 'data/acquisition.json');rows[0]['path'] = '../outside.xml'
            (root / 'data/acquisition.json').write_text(json.dumps(rows))
            self.assertTrue(any('Unsafe source path' in e for e in validate(root)))

    def test_unknown_quarantine_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);shutil.copytree(ROOT / 'data', root / 'data')
            (root / 'data/source-defects.json').write_text('[]')
            self.assertTrue(any('Unregistered source quarantine' in e for e in validate(root)))

    def test_lossless_export_and_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'export';export(self.records, target)
            self.assertEqual(read_json(target / 'corpus.json')['records'], self.records)
            self.assertEqual(verify_export(target), [])
            (target / 'components.csv').write_text('tampered')
            self.assertTrue(verify_export(target))

    def test_manifest_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp);(target / 'manifest.json').write_text('{"files":{"../out":"bad"}}')
            self.assertTrue(verify_export(target))

    def test_unlisted_export_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp);export(self.records, target)
            (target / 'unlisted.txt').write_text('extra')
            self.assertTrue(verify_export(target))

    def test_family_source_and_gate_reconciliation(self):
        self.assertEqual(validate_family(), [])

    def test_shared_source_cannot_become_independent_witness(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / 'data', root / 'data')
            shutil.copytree(ROOT / 'research', root / 'research')
            p = root / 'research/family/shared-source-identities.json'
            links = read_json(p);links[0]['independent_witnesses_created'] = 1
            p.write_text(json.dumps(links))
            self.assertIn('Shared source was promoted to an independent witness', validate_family(root))

if __name__ == '__main__':
    unittest.main()
