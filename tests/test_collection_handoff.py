import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('collection_handoff',ROOT/'scripts/build_collection_handoff.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class HandoffTests(unittest.TestCase):
 def fixture(self,root):
  (root/'research').mkdir();(root/'data').mkdir()
  cfg={'repository':'example/corpus','record_sets':[{'name':'digital','path':'data/records.json','id_key':'id','unit':'source_entry'}],'source_files':['research/tasks.json'],'native_review_links':[]}
  (root/m.CONFIG).write_text(json.dumps(cfg));(root/'data/records.json').write_text(json.dumps([{'id':0,'reading':'uncertain'}]));(root/'research/tasks.json').write_text(json.dumps({'remaining_nonexpert_work':[{'id':'OPEN','action':'Inspect an edition','blocked_by':'source_access'}]}));return cfg
 def test_native_replay(self):m.replay(ROOT)
 def test_zero_id_and_access_label_do_not_approve(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);x=m.build(r)[m.OUTPUTS[0]];self.assertEqual(x['records'][0]['native_id'],'0');self.assertEqual(x['tasks'][0]['collection_disposition'],'OPEN_REQUIRES_DISPOSITION');self.assertFalse(x['terminal_pre_expert_maximum_established']);self.assertFalse(x['scientific_approval_granted'])
 def test_input_change_invalidates_committed_ledger(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);m.replay(r,True);(r/'data/records.json').write_text('[{"id":0,"reading":"changed"}]')
   with self.assertRaisesRegex(ValueError,'stale'):m.replay(r)
 def test_duplicate_source_id_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);(r/'data/records.json').write_text('[{"id":0},{"id":0}]')
   with self.assertRaisesRegex(ValueError,'duplicate identifier'):m.build(r)
 def test_overlapping_views_are_separate_units(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);cfg=self.fixture(r);other=copy.deepcopy(cfg['record_sets'][0]);other['name']='other';other['unit']='reading_version';cfg['record_sets'].append(other);(r/m.CONFIG).write_text(json.dumps(cfg));x=m.build(r)[m.OUTPUTS[0]];self.assertEqual(len(x['record_views']),2);self.assertTrue(x['record_identity_is_not_object_identity'])
 def test_sealed_input_and_path_escape_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   for p in ['research/prospective-outcomes.json','../outside.json']:
    with self.assertRaises(ValueError):m.safe(Path(d),p)
 def decision(self,r):
  out=m.build(r);x=copy.deepcopy(out[m.OUTPUTS[2]]);row=out[m.OUTPUTS[0]]['records'][0];x.update(record_key=row['record_key'],source_record_sha256=row['source_record_sha256'],reviewer='Fixture reviewer',reviewed_on='2026-10-04',inspected_evidence=[{'locator':'fixture p1'}]);x['decisions']={k:{'status':'INCONCLUSIVE','rationale':'Fixture uncertainty'} for k in m.DIMENSIONS};return x
 def test_stale_and_unknown_decisions_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);x=self.decision(r);self.assertTrue(m.validate_decision(r,x));x['record_key']='invented'
   with self.assertRaisesRegex(ValueError,'unknown'):m.validate_decision(r,x)
   x=self.decision(r);(r/'data/records.json').write_text('[{"id":0,"reading":"changed"}]')
   with self.assertRaisesRegex(ValueError,'stale'):m.validate_decision(r,x)
 def test_admission_and_empty_review_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);x=self.decision(r);x['automatic_admission']=True
   with self.assertRaisesRegex(ValueError,'admission'):m.validate_decision(r,x)
   x=self.decision(r);x['inspected_evidence']=[]
   with self.assertRaisesRegex(ValueError,'missing reviewer'):m.validate_decision(r,x)
 def test_restricted_records_are_not_opened_in_public_build(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);cfg=self.fixture(r);cfg['record_sets']=[{'name':'private','path':'data/generated/pre-expert/records.json','id_key':'record_id','unit':'restricted_record','local_only':True,'count_path':'research/tasks.json','count_pointer':'/documents'}];(r/m.CONFIG).write_text(json.dumps(cfg));(r/'research/tasks.json').write_text('{"documents":802}');x=m.build(r)[m.OUTPUTS[0]];self.assertEqual(x['records'],[]);self.assertIsNone(x['record_views'][0]['enumerated']);self.assertEqual(x['record_views'][0]['native_reported_count'],802)
 def test_duplicate_view_name_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);cfg=self.fixture(r);cfg['record_sets']*=2;(r/m.CONFIG).write_text(json.dumps(cfg))
   with self.assertRaisesRegex(ValueError,'duplicate record view'):m.build(r)
 def test_repository_and_locator_binding(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);x=self.decision(r);x['repository']='other/corpus'
   with self.assertRaisesRegex(ValueError,'repository'):m.validate_decision(r,x)
   x=self.decision(r);x['inspected_evidence']=['not a locator']
   with self.assertRaisesRegex(ValueError,'locator'):m.validate_decision(r,x)
 def test_restricted_source_pin_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);cfg=self.fixture(r);cfg['record_sets']=[{'name':'private','path':'data/generated/pre-expert/records.json','id_key':'record_id','unit':'restricted_record','local_only':True,'count_path':'research/tasks.json','count_pointer':'/documents'}];(r/m.CONFIG).write_text(json.dumps(cfg));(r/'research/tasks.json').write_text('{"documents":1,"source_sha256":"correct"}');p=r/'data/generated/pre-expert/records.json';p.parent.mkdir(parents=True);p.write_text('[{"record_id":"A","provenance":{"input_sha256":"wrong"}}]')
   with self.assertRaisesRegex(ValueError,'source pin'):m.build_local(r)
 def test_each_citation_and_record_lead_is_indexed(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.fixture(r);(r/'data/records.json').write_text('[{"id":0,"citations":["Edition p1","Edition p2"]}]');x=m.build(r)[m.OUTPUTS[0]];self.assertEqual(len(x['source_leads']),2);self.assertEqual(x['records'][0]['source_lead_pointers'],['/0/citations'])
if __name__=='__main__':unittest.main()
