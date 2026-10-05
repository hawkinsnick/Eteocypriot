import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('concordance', ROOT / 'scripts/audit_source_concordance.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ConcordanceBoundaries(unittest.TestCase):
    def mutate(self, path, change):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
            p = root / path
            data = json.loads(p.read_text(encoding='utf-8'))
            change(data)
            p.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError):
                audit.build(root)

    def test_scope_retains_native_denominators(self):
        data = audit.build()
        self.assertEqual(data['parsed_source_entries_replayed'], 25)
        self.assertEqual(data['component_targets'], 29)
        self.assertEqual(data['historical_candidate_joins'], 7)
        self.assertEqual(data['physical_objects_certified'], 0)

    def test_provenance_disagreement_cannot_overwrite_source(self):
        self.mutate('research/source-concordance-register.json',
                    lambda d: d['entries'][2]['reported_metadata'].update(site='unverified'))

    def test_reported_inventory_cannot_certify_native_object(self):
        self.mutate('research/source-concordance-register.json',
                    lambda d: d['entries'][4].update(physical_object_id='AM 799'))

    def test_historical_number_cannot_become_equal_ig_number(self):
        self.mutate('research/historical-concordance.json',
                    lambda d: d['candidate_joins'][0].update(candidate_native_record_id='ETEC-IGXV1-1'))

    def test_historical_join_cannot_become_independent(self):
        self.mutate('research/historical-concordance.json',
                    lambda d: d['candidate_joins'][0].update(independent_confirmation=True))

    def test_discovery_lead_cannot_add_native_reading(self):
        self.mutate('research/historical-concordance.json',
                    lambda d: d['discovery_leads'][0].update(native_record_added=True))

    def test_doubtful_language_lead_cannot_lose_qualification(self):
        self.mutate('research/historical-concordance.json',
                    lambda d: d['discovery_leads'][1].update(disposition='ETEOCYPRIOT_CONFIRMED'))

    def test_uninspected_page_cannot_support_assertion(self):
        self.mutate('research/historical-concordance.json',
                    lambda d: d['selected_critical_assertions'][0].update(page=80))

    def test_coin_comparison_cannot_admit_language(self):
        self.mutate('research/coin-source-comparison.json',
                    lambda d: d['entries'][3].update(language_adjudicated=True))

    def test_coin_parts_cannot_certify_historical_specimens(self):
        self.mutate('research/coin-source-comparison.json',
                    lambda d: d['historical_type_candidate'].update(part_equals_historical_specimen_verified=True))
