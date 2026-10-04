#!/usr/bin/env python3
"""Replay a source-bound work ledger; never infer scholarly approval or read outcomes."""
import argparse, collections, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIG='research/collection-readiness-inputs.json'
OUTPUTS=('research/collection-work-ledger.json','review/collection-packet.json','review/collection-decision-template.json')
DIMENSIONS=('object_identity','reading_and_layout','uncertainty','language_or_script_classification','source_independence','reuse_rights')
QUESTIONS={
 'object_identity':'Confirm the object, face and inventory concordance; distinguish source entries from physical objects.',
 'reading_and_layout':'Compare the exact edition rows, figures and layout; preserve competing readings with page/line locators.',
 'uncertainty':'Retain damage, restorations, unreadable signs and competing segmentations; do not silently normalize them.',
 'language_or_script_classification':'Attribute membership and classification to named authorities; preserve disagreement.',
 'source_independence':'Identify shared editorial and photographic lineage; a derivative is not an independent witness.',
 'reuse_rights':'Check the applicable license or permission for each component; project terms do not override upstream rights.'}
LEAD_KEYS={'source_id','reference','title','work','basic_corpus','digital_route','source','source_label','publication','primary_edition','reference_work','source_family','citation','citations','references','bibliography','source_url','url','doi','source_leads','locators','source_ids','edition','edition_locator','source_ref','source_refs'}
TASK_KEYS={'machine_resolvable','remaining_nonexpert_work','remaining_machine_work','human_only_boundary','human_only','external_or_expert','sealed_or_external','items','gaps','acquisition_queue','blockers'}
def digest(b):return hashlib.sha256(b).hexdigest()
def encode(d):return (json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def safe(root,path):
 p=(root/path).resolve()
 if p==root.resolve() or root.resolve() not in p.parents:raise ValueError('input path escapes repository')
 if any(x in path.lower() for x in ('prospective','prediction','outcome','gold-reveal')):raise ValueError('sealed inputs are excluded')
 return p
def pointer(data,p):
 for part in p.strip('/').split('/') if p else []:
  part=part.replace('~1','/').replace('~0','~');data=data[int(part)] if isinstance(data,list) else data[part]
 return data
def walk(d,p=''):
 if isinstance(d,dict):
  for k,v in d.items():
   q=p+'/'+k.replace('~','~0').replace('/','~1');yield k,v,q;yield from walk(v,q)
 elif isinstance(d,list):
  for i,v in enumerate(d):yield from walk(v,p+'/'+str(i))
def build(root=ROOT):
 root=Path(root);cfg=json.loads(safe(root,CONFIG).read_bytes());inputs={};data={}
 paths=sorted(set(cfg['source_files']+[x['path'] for x in cfg['record_sets'] if not x.get('local_only')]))
 if set(paths)&set(OUTPUTS):raise ValueError('recursive generated input')
 for p in paths:
  b=safe(root,p).read_bytes();inputs[p]=digest(b)
  if p.endswith('.json'):data[p]=json.loads(b)
 cfg_hash=digest(safe(root,CONFIG).read_bytes());builder_hash=digest(Path(__file__).read_bytes())
 fingerprint=digest(encode({'config':cfg_hash,'builder':builder_hash,'inputs':inputs}))
 records=[];views=[]
 names=[x['name'] for x in cfg['record_sets']]
 if len(names)!=len(set(names)):raise ValueError('duplicate record view name')
 for spec in cfg['record_sets']:
  if spec.get('local_only'):
   # Public generation deliberately never opens restricted local record files.
   expected=pointer(data[spec['count_path']],spec['count_pointer'])
   views.append({'view':spec['name'],'unit':spec['unit'],'enumerated':None,'native_reported_count':expected,'representation':'RESTRICTED_LOCAL_DERIVATIVE_NOT_READ_OR_REPUBLISHED','local_path':spec['path']});continue
  rows=pointer(data[spec['path']],spec.get('pointer',''))
  if spec.get('singleton'):rows=[rows]
  if not isinstance(rows,list):raise ValueError('record view must select a list')
  seen=set()
  for i,row in enumerate(rows):
   raw=row[spec['id_key']] if isinstance(row,dict) else row
   if raw is None or isinstance(raw,(dict,list,bool)) or str(raw)=='':raise ValueError('invalid record identifier')
   rid=str(raw)
   if rid in seen:raise ValueError('duplicate identifier inside record view')
   seen.add(rid);p=spec.get('pointer','')+('' if spec.get('singleton') else '/'+str(i))
   records.append({'record_key':spec['name']+':'+rid,'native_id':rid,'unit':spec['unit'],'source_path':spec['path'],'json_pointer':p,'source_file_sha256':inputs[spec['path']],'source_record_sha256':digest(encode(row)),'assessment':'NOT_ADJUDICATED_BY_COLLECTION_BUILDER','questions':list(DIMENSIONS),'source_lead_pointers':[p+q for k,v,q in walk(row) if k in LEAD_KEYS and v not in (None,[],{},'')]})
  v={'view':spec['name'],'unit':spec['unit'],'enumerated':len(rows),'representation':'PUBLIC_NATIVE_IDENTIFIERS_AND_POINTERS_ONLY'}
  if spec.get('count_path'):v['native_reported_count']=pointer(data[spec['count_path']],spec['count_pointer'])
  views.append(v)
 tasks=[];leads=[]
 for path,d in data.items():
  for key,value,p in walk(d):
   if key in LEAD_KEYS and value not in (None,[],{},''):
    for lead_pointer in [p+'/'+str(i) for i in range(len(value))] if isinstance(value,list) else [p]:
     leads.append({'source_path':path,'json_pointer':lead_pointer,'kind':key,'inspection':'REFER_TO_NATIVE_ASSERTION; NOT_INSPECTED_BY_BUILDING_THIS_LEDGER'})
   if key in TASK_KEYS and isinstance(value,list):
    for i,item in enumerate(value):
     human=key in {'human_only_boundary','human_only','external_or_expert','sealed_or_external'}
     status=item.get('status',item.get('state')) if isinstance(item,dict) else None
     task=item.get('task',item.get('action',item.get('decision',item.get('scope')))) if isinstance(item,dict) else item
     disposition='HUMAN_OR_EXTERNAL_NATIVE_BOUNDARY' if human else 'COMPLETE_NATIVE_ASSERTION' if status in {'COMPLETE','COMPLETED'} else 'OPEN_REQUIRES_DISPOSITION'
     tasks.append({'source_path':path,'json_pointer':p+'/'+str(i),'native_task_id':item.get('id') if isinstance(item,dict) else None,'task':task,'native_status':status,'collection_disposition':disposition,'blocker_is_not_established_by_a_label':True})
 ledger={'schema_version':'1.0','repository':cfg['repository'],'scope':'Declared native snapshots and source/task registers only; not a language-wide inventory','evidence_fingerprint':fingerprint,'input_sha256':inputs,'config_sha256':cfg_hash,'builder_sha256':builder_hash,'record_views':views,'records':records,'source_leads':leads,'tasks':tasks,'question_definitions':QUESTIONS,'review_dimensions':list(DIMENSIONS),'native_review_links':cfg['native_review_links'],'record_identity_is_not_object_identity':True,'scientific_approval_granted':False,'terminal_pre_expert_maximum_established':False,'completion_rule':'Enumeration is a completed work map, not completed collation. Resolve every open task using exact inspected evidence or a documented access/rights dependency; leave scientific adjudication to independent review.'}
 packet={'schema_version':'1.0','repository':cfg['repository'],'evidence_fingerprint':fingerprint,'ledger_path':OUTPUTS[0],'selection':'Select record_keys from ledger; for restricted A/B records use the existing local derivative and authenticated native audit','native_review_links':cfg['native_review_links'],'source_lead_count':len(leads),'enumerated_record_keys':len(records),'dimensions':QUESTIONS,'requests':['Record what evidence was actually accessed, with exact edition/page/line/figure locators.','Separate source assertions, project computations and independent scholarly judgments.','Submit inconclusive and negative decisions with the same revision binding as positive ones.'],'scientific_approval_granted':False,'automatic_admission':False,'rights':'Source-specific terms govern the linked evidence; no source scan, transcription or protected record payload is duplicated in this packet.'}
 template={'schema_version':'1.0','repository':cfg['repository'],'evidence_fingerprint':fingerprint,'record_key':None,'source_record_sha256':None,'reviewer':None,'reviewed_on':None,'inspected_evidence':[],'decisions':{k:{'status':'UNREVIEWED','rationale':None} for k in DIMENSIONS},'automatic_admission':False}
 return dict(zip(OUTPUTS,(ledger,packet,template)))
def replay(root=ROOT,write=False):
 out=build(root)
 for path,d in out.items():
  p=Path(root)/path;b=encode(d)
  if write:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  elif not p.exists() or p.read_bytes()!=b:raise ValueError('stale collection handoff: '+path)
 return out
def build_local(root=ROOT):
 root=Path(root);public=build(root)[OUTPUTS[0]];cfg=json.loads((root/CONFIG).read_bytes());records=[];private_inputs={}
 for spec in cfg['record_sets']:
  if not spec.get('local_only'):continue
  p=safe(root,spec['path'])
  if not spec['path'].startswith('data/generated/'):raise ValueError('restricted ledger must use ignored local derivatives')
  raw=p.read_bytes();rows=json.loads(raw);audit=json.loads(safe(root,spec['count_path']).read_bytes())
  if len(rows)!=pointer(audit,spec['count_pointer']):raise ValueError('restricted record count differs from authenticated audit')
  seen=set()
  for row in rows:
   rid=str(row[spec['id_key']])
   if rid in seen:raise ValueError('duplicate restricted record ID')
   seen.add(rid)
   if row.get('provenance',{}).get('input_sha256')!=audit['source_sha256']:raise ValueError('restricted source pin differs from authenticated audit')
   records.append({'record_key':spec['name']+':'+rid,'source_record_sha256':digest(encode(row)),'source_pointer':row['provenance'],'questions':list(DIMENSIONS),'scientific_approval_granted':False})
  private_inputs[spec['path']]=digest(raw)
 if not private_inputs:raise ValueError('no restricted record views declared')
 out={'public_evidence_fingerprint':public['evidence_fingerprint'],'private_input_sha256':private_inputs,'records':records,'scope':'LOCAL_ONLY; no source payload duplicated; source rights retained; no scientific approval'}
 p=root/'data/generated/collection-work-ledger-local.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encode(out));return out
def validate_decision(root,decision):
 out=build(root);ledger=out[OUTPUTS[0]]
 if decision.get('repository')!=ledger['repository']:raise ValueError('decision repository mismatch')
 if decision.get('evidence_fingerprint')!=ledger['evidence_fingerprint']:raise ValueError('stale decision fingerprint')
 records={r['record_key']:r for r in ledger['records']};row=records.get(decision.get('record_key'))
 if row is None:raise ValueError('unknown or restricted record key; use native local review')
 if decision.get('source_record_sha256')!=row['source_record_sha256']:raise ValueError('stale record hash')
 if decision.get('automatic_admission') is not False:raise ValueError('automatic admission prohibited')
 if set(decision.get('decisions',{}))!=set(DIMENSIONS):raise ValueError('incomplete review dimensions')
 if not decision.get('reviewer') or not decision.get('reviewed_on') or not decision.get('inspected_evidence'):raise ValueError('missing reviewer or inspected evidence')
 for evidence in decision['inspected_evidence']:
  if not isinstance(evidence,dict) or not isinstance(evidence.get('locator'),str) or not evidence['locator'].strip():raise ValueError('missing inspected evidence locator')
 for d in decision['decisions'].values():
  if d.get('status') not in {'SUPPORTED','DISPUTED','INCONCLUSIVE','NOT_APPLICABLE'} or not d.get('rationale'):raise ValueError('missing dimension decision/rationale')
 # Structural validation authenticates neither the reviewer nor the scientific conclusion.
 return True
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');a.add_argument('--decision',type=Path);a.add_argument('--local',action='store_true');args=a.parse_args()
 if args.local:build_local(ROOT);print('Restricted local record work map built; do not publish')
 elif args.decision:validate_decision(ROOT,json.loads(args.decision.read_bytes()));print('Decision structure PASS; no scholarly approval or admission granted')
 else:replay(write=args.write);print('Collection work ledger and review packet replay PASS')
