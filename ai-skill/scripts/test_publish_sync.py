import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('publisher',Path(__file__).with_name('publish_sync.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PublicationTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.base=Path(self.t.name);self.remote=self.base/'remote.git';self.work=self.base/'work';self.other=self.base/'other'
  self.sh(['git','init','--bare','--initial-branch=main',str(self.remote)])
  self.sh(['git','clone',str(self.remote),str(self.work)])
  self.configure(self.work);p=self.work/'ai-skill/scripts';p.mkdir(parents=True);(p/'validate_bundle.py').write_text('pass\n');(self.work/'.gitignore').write_text('__pycache__/\n');(self.work/'canonical.txt').write_text('source\n');self.sh(['git','add','.'],self.work);self.sh(['git','commit','-m','source'],self.work);self.sh(['git','push','origin','main'],self.work);self.source=m.git(self.work,'rev-parse','HEAD')
  self.sh(['git','clone',str(self.remote),str(self.other)]);self.configure(self.other)
  p=self.work/'ai-skill/generated';p.mkdir()
  for n in ['research-bundle-index.json','source-state.json']:(p/n).write_text(json.dumps({'source_commit':self.source}))
 def tearDown(self):self.t.cleanup()
 def sh(self,args,cwd=None):return subprocess.run(args,cwd=cwd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 def configure(self,r):self.sh(['git','config','user.email','test@example.invalid'],r);self.sh(['git','config','user.name','Test'],r)
 def advance(self):
  (self.other/'canonical.txt').write_text('new source\n');self.sh(['git','add','.'],self.other);self.sh(['git','commit','-m','concurrent source'],self.other);self.sh(['git','push','origin','main'],self.other)
 def test_publish_exact_parent(self):
  d=m.publish(self.work,self.source);self.assertTrue(d['published']);self.assertEqual(m.git(self.work,'rev-parse','HEAD^'),self.source)
 def test_advanced_source_skips_without_rebase(self):
  self.advance();d=m.publish(self.work,self.source);self.assertFalse(d['published']);self.assertEqual(m.git(self.work,'rev-parse','HEAD'),self.source)
 def test_race_after_guard_cannot_push(self):
  with self.assertRaises(subprocess.CalledProcessError):m.publish(self.work,self.source,self.advance)
  self.assertEqual(subprocess.check_output(['git','--git-dir',str(self.remote),'rev-parse','main'],text=True).strip(),m.git(self.other,'rev-parse','HEAD'))
  self.assertEqual(m.git(self.other,'show','HEAD:canonical.txt'),'new source')
 def test_unrelated_changes_rejected(self):
  (self.work/'canonical.txt').write_text('tampered\n')
  with self.assertRaises(ValueError):m.publish(self.work,self.source)
 def test_mismatched_bundle_source_rejected(self):
  (self.work/'ai-skill/generated/source-state.json').write_text(json.dumps({'source_commit':'0'*40}))
  with self.assertRaises(ValueError):m.publish(self.work,self.source)
 def test_validation_failure_cannot_publish(self):
  (self.work/'ai-skill/scripts/validate_bundle.py').write_text('raise SystemExit(1)\n')
  self.sh(['git','add','ai-skill/scripts/validate_bundle.py'],self.work);self.sh(['git','commit','-m','bad validator'],self.work)
  source=m.git(self.work,'rev-parse','HEAD')
  for n in ['research-bundle-index.json','source-state.json']:(self.work/'ai-skill/generated'/n).write_text(json.dumps({'source_commit':source}))
  with self.assertRaises(subprocess.CalledProcessError):m.publish(self.work,source)
if __name__=='__main__':unittest.main()
