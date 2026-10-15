"""Integrity failures must block attribution queries, including unrelated cases."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from attribution_review import Review, ROOT, MANIFEST, REPORT, pointer


class AttributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.m = json.loads((ROOT/MANIFEST).read_text())
        for path in [MANIFEST, 'scripts/attribution_review.py'] + [x['path'] for x in self.m['inputs']]:
            p = self.root/path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((ROOT/path).read_bytes())

    def save(self):
        (self.root/MANIFEST).write_text(json.dumps(self.m))

    def test_recorded_report(self):
        self.assertEqual(Review().report(), json.loads((ROOT/REPORT).read_text()))

    def test_all_native_fields_preserved(self):
        r = Review(self.root)
        for key in r.cases:
            for x in r.case(key)['evidence']:
                original = json.loads((self.root/x['path']).read_text())
                self.assertEqual(x['native_evidence'], pointer(original, x['pointer']))

    def test_stale_evidence_blocks_every_case(self):
        p = self.root/self.m['inputs'][-1]['path']
        p.write_text(p.read_text()+'\n')
        with self.assertRaisesRegex(ValueError, 'stale evidence'):
            Review(self.root)

    def test_invalid_locus_blocks_query(self):
        self.m['cases'][0]['evidence'][0]['pointer'] = '/NO_SUCH_LOCUS'
        self.save()
        with self.assertRaises((KeyError, ValueError)):
            Review(self.root)

    def test_no_automatic_acceptance(self):
        self.m['cases'][0]['new_reading_admitted'] = True
        self.save()
        with self.assertRaisesRegex(ValueError, 'promotion'):
            Review(self.root)

    def test_gaps_required(self):
        self.m['cases'][0]['remaining_gap'] = ''
        self.save()
        with self.assertRaises(ValueError):
            Review(self.root)

    def test_no_duplicate_case(self):
        self.m['cases'].append(copy.deepcopy(self.m['cases'][0]))
        self.save()
        with self.assertRaises(ValueError):
            Review(self.root)

    def test_path_escape_rejected(self):
        self.m['inputs'][0]['path'] = '../outside.json'
        self.save()
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            Review(self.root)

    def test_no_repeated_primary_consultation_claim(self):
        self.m['consultation_this_pass'] = 'PRIMARY_PDF_READ_AGAIN'
        self.save()
        with self.assertRaises(ValueError):
            Review(self.root)

    def test_complete_selection_cannot_drop_case(self):
        selections = self.m['complete_selections']
        if not selections:
            self.skipTest('no claimed complete collection')
        s = selections[0]
        self.m['cases'] = [c for c in self.m['cases'] if not any(e['path']==s['path'] and e['pointer']==s['pointer']+'/0' for e in c['evidence'])]
        self.save()
        with self.assertRaisesRegex(ValueError, 'lacks review'):
            Review(self.root)


if __name__ == '__main__':
    unittest.main()
