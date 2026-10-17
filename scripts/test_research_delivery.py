#!/usr/bin/env python3
"""Native delivery tests, including hostile claims and package replay."""
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
import research_delivery as d


class Delivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e=d.Evidence();cls.name=next(n for n,c in cls.e.collections.items() if c['records'])
        cls.row=cls.e.collections[cls.name]['records'][0]
        cls.identity=cls.row['id']

    def test_report_and_complete_records(self):
        r=d.check();self.assertFalse(r['expert_acceptance_added'])
        self.assertFalse(r['model_behavior_empirically_validated'])
        for name,c in self.e.collections.items():
            for row in c['records']:
                self.assertTrue(row['id']);self.assertTrue(c['spec']['unit'])
                self.assertEqual(self.e.provenance(c['spec']['path'],row['pointer'])['sha256'],self.e.artifacts[c['spec']['path']]['spec']['sha256'])

    def test_search_preserves_native_unit_record_and_provenance(self):
        q=d.search(self.identity,collection=self.name,limit=1000)
        row=next(r for r in q['records'] if r['id']==self.identity)
        self.assertEqual(row['native_record'],self.row['value'])
        self.assertIsNone(q['unique_object_count']);self.assertFalse(q['scientific_approval_granted'])
        for limit in (0,1001):
            with self.assertRaises(ValueError):d.search('',limit=limit)

    def test_answer_and_unsupported_inference(self):
        a=d.answer(self.name,self.identity)
        self.assertEqual(a['dossier']['native_record'],self.row['value'])
        d.validate_answer(a,self.name,self.identity)
        for request in ('decipher','invent_missing_reading','certify_independence','admit_review'):
            self.assertEqual(d.answer(self.name,self.identity,request=request)['status'],'REFUSED_UNSUPPORTED_INFERENCE')
        for field,value in [('new_claims',['invented translation']),('scientific_approval_granted',True),('boundary','')]:
            bad=copy.deepcopy(a);bad[field]=value
            with self.assertRaises(ValueError):d.validate_answer(bad,self.name,self.identity)
        bad=copy.deepcopy(a);bad['dossier']['provenance']['sha256']='0'*64
        with self.assertRaises(ValueError):d.validate_answer(bad,self.name,self.identity)
        bad=copy.deepcopy(a);bad['dossier']['native_record']={'invented':True}
        with self.assertRaises(ValueError):d.validate_answer(bad,self.name,self.identity)

    def submission(self):
        v=d.review_template(self.name,self.identity)
        v.update(status='SUBMITTED_FOR_MAINTAINER_CHECK',decision='INCONCLUSIVE',reasoning='Synthetic schema test only.',confidence='Undetermined',counterevidence='Not evaluated: fixture.',unresolved_objections='No real review performed.')
        v['reviewer']={k:'SYNTHETIC TEST ONLY' for k in v['reviewer']};v['reviewer']['date']='2026-10-17'
        v['evidence_consulted']=[{k:'SYNTHETIC TEST ONLY' for k in ('citation','locator','accessed_version','access_rights','dependence')}]
        return v

    def test_review_structure_never_confers_acceptance(self):
        v=self.submission();r=d.validate_review(v)
        self.assertFalse(r['identity_verified']);self.assertFalse(r['scientific_approval_granted'])
        self.assertTrue(r['maintainer_acceptance_required'])
        with self.assertRaises(ValueError):d.validate_review(d.review_template(self.name,self.identity))
        for change in ('source','identity','acceptance','missing-source','blank-disclosure'):
            bad=copy.deepcopy(v)
            if change=='source':bad['target']['provenance']['sha256']='0'*64
            elif change=='identity':bad['repository']='INVENTED'
            elif change=='acceptance':bad['scientific_approval_granted']=True
            elif change=='missing-source':bad['evidence_consulted']=[]
            else:bad['reviewer']['conflicts']=''
            with self.assertRaises(ValueError):d.validate_review(bad)

    def test_source_tamper_and_unsafe_paths_rejected(self):
        _,files=d.inputs()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for path,raw in files.items():
                p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            target=root/self.e.profile['collections'][0]['path'];target.write_bytes(target.read_bytes()+b' ')
            with self.assertRaises(ValueError):d.report(root)
            for path in ('../escape','/etc/passwd'):
                with self.assertRaises(ValueError):d.local(root,path)

    def test_package_exact_replay_and_manifest(self):
        raw=d.package();self.assertEqual(raw,d.package())
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                m=json.loads(z.read('research-package-manifest.json'))
                self.assertFalse(m['redistribution_permission_granted'])
                for e in m['files']:
                    self.assertEqual(d.sha(z.read(e['path'])),e['sha256'])
                self.assertFalse(any('/private/' in name or '/sealed/' in name for name in z.namelist()))
                z.extractall(root)
            subprocess.run([sys.executable,'scripts/research_delivery.py','--check'],cwd=root,capture_output=True,check=True)
            subprocess.run([sys.executable,'scripts/research_delivery.py','--package','replay.zip'],cwd=root,capture_output=True,check=True)
            self.assertEqual(raw,(root/'replay.zip').read_bytes())

if __name__=='__main__':unittest.main()
