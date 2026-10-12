import copy,json,unittest
from check_cross_corpus_dependencies import ROOT,check,screen,validate
class DependencyTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((ROOT/'research/cross-corpus-dependencies.json').read_text())
 def test_valid(self):validate()
 def test_unknown_not_independent(self):
  d=screen(self.data,['unknown::record']);self.assertIsNone(d['independent_witness_count']);self.assertIsNone(d['physical_object_count'])
 def test_prohibited_claims(self):
  for claim in ['independent_witness_count','physical_object_count','phonetic_transfer']:
   with self.assertRaises(ValueError):screen(self.data,[],claim)
 def test_false_promotion_rejected(self):
  bad=copy.deepcopy(self.data);bad['independence_established']=True
  with self.assertRaises(ValueError):check(bad)
 def test_erased_dependency_rejected(self):
  bad=copy.deepcopy(self.data);bad['scope']='none'
  with self.assertRaises(ValueError):check(bad)
 def test_shared_selection_flagged(self):
  if self.data['dependency_groups']:
   g=self.data['dependency_groups'][0];keys=[p['repository']+'::'+p['record_id'] for p in g['participants']];self.assertIn(g['group_id'],screen(self.data,keys)['known_dependency_groups_in_selection'])
if __name__=='__main__':unittest.main()
