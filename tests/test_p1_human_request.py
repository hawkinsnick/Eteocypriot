import copy,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import p1_human_request as m
class RequestTests(unittest.TestCase):
    def setUp(self):self.r=json.loads((R/'review/p1-human-request.json').read_text())
    def test_current(self):self.assertIs(m.validate()['human_review_performed'],False)
    def test_acceptance_or_pretend_reviewer_rejected(self):
        for k,v in [('automatic_admission',True),('reviewer','AI'),('decisions',[{'approved':True}])]:
            r=copy.deepcopy(self.r);r[k]=v
            with self.assertRaises(ValueError):m.validate(request=r)
    def test_input_tampering_and_wrong_pointer_rejected(self):
        r=copy.deepcopy(self.r);r['inputs'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):m.validate(request=r)
        r=copy.deepcopy(self.r);r['questions'][0]['source_packet_pointer']='/cases/999'
        with self.assertRaises(ValueError):m.validate(request=r)
    def test_missing_scope_and_role_conflation_rejected(self):
        r=copy.deepcopy(self.r);r['questions'].pop()
        with self.assertRaises(ValueError):m.validate(request=r)
        r=copy.deepcopy(self.r);r['questions'][0]['role_required']='any_AI_or_human'
        with self.assertRaises(ValueError):m.validate(request=r)
    def test_negative_or_inconclusive_decisions_required(self):
        r=copy.deepcopy(self.r);r['questions'][0]['decision_requested']=['supported_with_scope']
        with self.assertRaises(ValueError):m.validate(request=r)
if __name__=='__main__':unittest.main()
