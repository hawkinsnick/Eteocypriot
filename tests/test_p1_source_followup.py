"""Adversarial checks for lost qualifications, altered inputs and exact query linkage."""
import copy,importlib.util,json,tempfile,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import p1_source_followup as p
import evidence_query as q
class FollowupTests(unittest.TestCase):
    def setUp(self):self.data=json.loads((ROOT/p.PACKET).read_text())
    def test_current_and_exact_query_preserve_all_cases(self):
        p.validate(ROOT,self.data);e=q.Evidence(ROOT)
        for c in self.data['cases']:
            d=e.dossier(c['id'],'p1-source-followup')
            self.assertEqual(d['native_record'],c)
            self.assertEqual(d['collection_context']['limits'],p.LIMITS)
            self.assertIn('sha256',d['provenance'])
        if p.EXPECTED_REPOSITORY.endswith('/Phrygian'):
            d=e.dossier('UD-TM1002268-1','ud-reference')
            joined=[x['native_record'] for x in d['explicitly_linked_records'] if x['collection']=='p1-source-followup']
            self.assertEqual(len(joined),1);self.assertIs(joined[0]['object_specific_reading_support'],False)
        if p.EXPECTED_REPOSITORY.endswith('/Sidetic'):
            d=e.dossier('sidetic:ediana:305','digital-reference')
            self.assertEqual(len([x for x in d['explicitly_linked_records'] if x['collection']=='p1-source-followup']),4)
    def test_promotions_and_missing_dispositions_rejected(self):
        for key in ['canonical_admission','physical_identity_certified','independent_review']:
            d=copy.deepcopy(self.data);d['cases'][0][key]=True
            with self.assertRaises(ValueError):p.validate(ROOT,d)
        d=copy.deepcopy(self.data);d['cases'].pop()
        with self.assertRaises(ValueError):p.validate(ROOT,d)
    def test_lost_limitation_or_bad_source_rejected(self):
        for mutation in ['remaining_work','source_ids']:
            d=copy.deepcopy(self.data);d['cases'][0][mutation]=[]
            with self.assertRaises(ValueError):p.validate(ROOT,d)
        d=copy.deepcopy(self.data);d['inputs']=[]
        with self.assertRaises(ValueError):p.validate(ROOT,d)
        d=copy.deepcopy(self.data);d['inputs'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):p.validate(ROOT,d)
    def test_page_inflation_and_numeric_boolean_rejected(self):
        d=copy.deepcopy(self.data);d['limits']['canonical_readings_added']=False
        with self.assertRaises(ValueError):p.validate(ROOT,d)
        for s in self.data['sources']:
            if s['page_inspections']:
                d=copy.deepcopy(self.data);source=next(x for x in d['sources'] if x['id']==s['id']);source['page_inspections'][0]['pdf_ordinal']=s['pdf_pages']+1
                with self.assertRaises(ValueError):p.validate(ROOT,d)
    def test_quarantine_and_formula_guard(self):
        for c in self.data['cases']:
            if c['id']=='PHR-TM1002268-ROLE':
                d=copy.deepcopy(self.data);d['cases'][0]['object_specific_reading_support']=True
                with self.assertRaises(ValueError):p.validate(ROOT,d)
            if c['id']=='ETE-IG150-QUARANTINE':
                d=copy.deepcopy(self.data);d['cases'][0]['raw_repaired']=True
                with self.assertRaises(ValueError):p.validate(ROOT,d)
if __name__=='__main__':unittest.main()
