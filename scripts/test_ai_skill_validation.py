"""Adversarial integrity and real CLI absence regression checks for the AI skill."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('skill_function', ROOT/'scripts/validate_ai_skill.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SkillValidation(unittest.TestCase):
    def test_changed_and_unbound_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'source.json';p.write_bytes(b'{}')
            entry={'path':'source.json','sha256':hashlib.sha256(b'{}').hexdigest(),'bytes':2}
            self.assertEqual(len(module.checked_artifacts(root,[entry])),1)
            p.write_bytes(b'[]')
            with self.assertRaisesRegex(ValueError,'changed'):module.checked_artifacts(root,[entry])
            with self.assertRaisesRegex(ValueError,'unbound'):module.checked_artifacts(root,[{'path':'source.json'}])
            with self.assertRaisesRegex(ValueError,'empty'):module.checked_artifacts(root,[])
    def test_escape_and_missing_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            for path in ('../outside','/etc/passwd','absent'):
                with self.subTest(path=path),self.assertRaises(ValueError):module.safe_file(folder,path)
    def test_missing_record_cli_withholds_evidence_without_traceback(self):
        if not (ROOT/'scripts/evidence_query.py').exists():
            import json
            rows=json.loads((ROOT/'data/manifest.json').read_bytes())['objects']
            self.assertNotIn('__AI_SKILL_MISSING_RECORD_20261020__',[r['object_id'] for r in rows])
            return
        for args in (['scripts/evidence_query.py','--record','__AI_SKILL_MISSING_RECORD_20261020__'],
                     ['scripts/research_delivery.py','--dossier','__AI_SKILL_MISSING_RECORD_20261020__','--collection','__UNKNOWN_COLLECTION__']):
            run=subprocess.run([sys.executable]+args,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(run.returncode,2,run.stderr)
            self.assertEqual(run.stdout,'')
            self.assertNotIn('Traceback',run.stderr)
            self.assertTrue(run.stderr.strip())

class StrictSourcePointers(unittest.TestCase):
    def resolve(self, pointer):
        import json
        with tempfile.TemporaryDirectory() as folder:
            raw=json.dumps({'array':['first','last'],'a/b':{'~key':False},'object':{'01':None}}).encode()
            (Path(folder)/'source.json').write_bytes(raw)
            return module.source_value(Path(folder),{'path':'source.json','sha256':hashlib.sha256(raw).hexdigest(),'encoding':'json','pointer':pointer})
    def test_negative_and_leading_zero_array_aliases_are_rejected(self):
        for pointer in ['/array/-1','/array/01','/array/+1','/array/ 1','/array/-']:
            with self.subTest(pointer=pointer),self.assertRaises(ValueError):self.resolve(pointer)
    def test_malformed_escapes_are_rejected(self):
        for pointer in ['/a~2b','/a~']:
            with self.subTest(pointer=pointer),self.assertRaises(ValueError):self.resolve(pointer)
    def test_valid_escapes_preserve_false_and_object_keys(self):
        self.assertIs(self.resolve('/a~1b/~0key'),False)
        self.assertIsNone(self.resolve('/object/01'))
        self.assertEqual(self.resolve('/array/1'),'last')
    def test_scalar_traversal_is_rejected(self):
        with self.assertRaises(ValueError):self.resolve('/array/0/child')
    def test_non_string_and_relative_pointers_are_rejected(self):
        for pointer in [None,0,'array/1']:
            with self.subTest(pointer=pointer),self.assertRaises(ValueError):self.resolve(pointer)

if __name__=='__main__':unittest.main()
