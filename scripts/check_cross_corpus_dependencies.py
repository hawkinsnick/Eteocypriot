"""Check literal source links and screen claims; no physical or linguistic certification."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_SHA='a8eabe18ad0998e458d83107b6229f3c7dbc779e0e6e23e0fec0bf61a7c0ce3d'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pointer(x,p):
 for k in p.strip('/').split('/') if p else []:x=x[int(k)] if isinstance(x,list) else x[k.replace('~1','/').replace('~0','~')]
 return x
def check(data,root=None):
 if digest(data)!=EXPECTED_SHA:raise ValueError('audited dependency projection or policy changed')
 if data['physical_identity_certified'] is not False or data['independence_established'] is not False:raise ValueError('unsupported identity/independence promotion')
 if root:
  for g in data['dependency_groups']:
   for participant in g['participants']:
    if participant['repository']!=data['repository']:continue
    for e in participant['evidence']:
     p=(Path(root)/e['path']).resolve()
     if not p.is_relative_to(Path(root).resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=e['sha256']:raise ValueError('dependency evidence digest drift')
     if pointer(json.loads(p.read_text()),e['pointer'])!=e['expected']:raise ValueError('source identifier/URL link drift')
 return {'status':'PASS_SOURCE_DEPENDENCY_GUARD','known_groups':len(data['dependency_groups']),'physical_identity_certified':False,'independence_established':False}
def screen(data,keys,claim='source_record_count'):
 check(data)
 if len(keys)!=len(set(keys)):raise ValueError('duplicate requested record key')
 registered={p['repository']+'::'+p['record_id'] for g in data['dependency_groups'] for p in g['participants']}
 overlapping=[g['group_id'] for g in data['dependency_groups'] if len(set(keys)&{p['repository']+'::'+p['record_id'] for p in g['participants']})>1]
 if claim!='source_record_count':raise ValueError('no pooled physical count, independent witness count or value transfer is authorized by this registry')
 return {'source_record_count':None if any(k not in registered for k in keys) else len(keys),'requested_key_count':len(keys),'known_dependency_groups_in_selection':overlapping,'unregistered_keys':[k for k in keys if k not in registered],'independent_witness_count':None,'physical_object_count':None,'warning':'Declared record rows only. Dependency groups flag shared source references; no physical deduplication or independent witness claim is established.'}
def validate(root=ROOT):return check(json.loads((Path(root)/'research/cross-corpus-dependencies.json').read_text()),root)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--records',nargs='*');p.add_argument('--claim',default='source_record_count');a=p.parse_args();data=json.loads((ROOT/'research/cross-corpus-dependencies.json').read_text());print(json.dumps(screen(data,a.records,a.claim) if a.records is not None else validate(),indent=2))
