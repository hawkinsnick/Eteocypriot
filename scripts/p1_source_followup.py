"""Replay bounded source dispositions; never certify epigraphic acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKET='research/p1-source-followup-2026-10-16.json'
EXPECTED_REPOSITORY='hawkinsnick/Eteocypriot'
EXPECTED_CASES={'ETE-IG150-QUARANTINE'}
EXPECTED_INPUTS={'data/records.json', 'data/raw/150.xml', 'research/source-route-recheck-2026-10-05.json'}
LIMITS={'canonical_readings_added':0,'physical_identities_certified':0,'independent_reviews_added':0,'frozen_readings_changed':False,'source_files_redistributed':False,'literature_exhaustive':False}

def validate(root=ROOT, data=None):
    root=Path(root)
    d=data if data is not None else json.loads((root/PACKET).read_text())
    if d['format']!='corpus-p1-source-followup-v1' or d['repository']!=EXPECTED_REPOSITORY:
        raise ValueError('packet identity mismatch')
    if d['limits']!=LIMITS or any(type(d['limits'][k]) is not type(v) for k,v in LIMITS.items()):
        raise ValueError('unsupported acceptance or completeness claim')
    if len(d['inputs'])!=len(EXPECTED_INPUTS) or {x['path'] for x in d['inputs']}!=EXPECTED_INPUTS:raise ValueError('native inputs omitted or duplicated')
    for item in d['inputs']:
        p=(root/item['path']).resolve()
        if not p.is_relative_to(root.resolve()) or not p.is_file():raise ValueError('unsafe or missing input')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('stale native input')
    sources={s['id']:s for s in d['sources']}
    if len(sources)!=len(d['sources']):raise ValueError('duplicate source')
    for s in sources.values():
        if s.get('source_files_redistributed') is not False:raise ValueError('source redistribution unsupported')
        if 'sha256' in s and (len(s['sha256'])!=64 or s.get('bytes',0)<=0):raise ValueError('invalid byte receipt')
        ordinals=[]
        for page in s['page_inspections']:
            n=page['pdf_ordinal'];ordinals.append(n)
            if type(n) is not int or not 1<=n<=s['pdf_pages'] or page['render_redistributed'] is not False or len(page['render_sha256'])!=64:
                raise ValueError('invalid inspected-page receipt')
        if len(ordinals)!=len(set(ordinals)):raise ValueError('duplicate page receipt')
    cases=d['cases']
    if len(cases)!=len(EXPECTED_CASES) or {c['id'] for c in cases}!=EXPECTED_CASES:
        raise ValueError('missing or duplicate target disposition')
    for c in cases:
        if any(c[k] is not False for k in ['canonical_admission','physical_identity_certified','independent_review']):
            raise ValueError('unsupported case promotion')
        if not c['source_ids'] or not set(c['source_ids'])<=sources.keys() or not c['observations'] or not c['remaining_work']:
            raise ValueError('missing source or retained limitation')
        if c['id']=='PHR-TM1002268-ROLE' and c['object_specific_reading_support'] is not False:
            raise ValueError('general formula promoted to object reading')
        if c['id']=='ETE-IG150-QUARANTINE':
            if c['parsed_record_added'] is not False or c['raw_repaired'] is not False or not c['parse_error']:
                raise ValueError('quarantine bypass')
    return {'status':'PASS_BOUNDED_SOURCE_FOLLOWUP','repository':EXPECTED_REPOSITORY,'cases':len(cases),'inspected_pdf_pages':sum(len(s['page_inspections']) for s in sources.values()),'scientific_acceptance_granted':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--verify-source',nargs=2,metavar=('SOURCE_ID','LOCAL_FILE'));a=p.parse_args();result=validate()
    if a.verify_source:
        ident,path=a.verify_source;d=json.loads((ROOT/PACKET).read_text());s=next(s for s in d['sources'] if s['id']==ident);b=Path(path).read_bytes()
        if hashlib.sha256(b).hexdigest()!=s['sha256'] or len(b)!=s['bytes']:raise SystemExit('source byte mismatch: inspect before replacing receipt')
        result['source_bytes_match']=True
    print(json.dumps(result))
