#!/usr/bin/env python3
"""Bounded native research delivery: evidence frames, replay and review forms."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
from evidence_query import Evidence, local, sha

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'analysis/research-delivery.json'
GUIDE = 'docs/RESEARCH-DELIVERY.md'
BOUNDARY = ('Source assertions, hypotheses and review tasks retain their native categories. '
            'Retrieval and byte replay establish neither scholarly completeness nor expert acceptance. '
            'Missing source attribution, access, permission and independent review remain open where recorded.')
REQUIRED = ['research/evidence-query-profile.json', 'scripts/evidence_query.py',
            'scripts/research_delivery.py', 'scripts/test_research_delivery.py', GUIDE, 'review/collection-packet.json',
            'ai-skill/SKILL.md', 'LICENSE', 'LICENSE-CODE', 'LICENSE-CONTENT.md',
            'LICENSING.md', 'NOTICE']


def inputs(root=ROOT):
    e = Evidence(root)
    if not e.profile.get('scholarly_limits'):
        raise ValueError('missing native scholarly limits')
    paths = set(REQUIRED) | set(e.artifacts)
    packet = json.loads(local(root, 'review/collection-packet.json').read_bytes())
    if packet['repository'] != e.profile['repository'] or packet['automatic_admission'] is not False or packet['scientific_approval_granted'] is not False:
        raise ValueError('native review identity or acceptance boundary drift')
    # Include native ledger/guides only when explicitly linked; never crawl private data.
    if packet.get('ledger_path'):
        paths.add(packet['ledger_path'])
    for path in packet.get('native_review_links', []):
        if not path.startswith(('http:', 'https:')):
            paths.add(path)
    return e, {p:local(root,p).read_bytes() for p in sorted(paths)}


def report(root=ROOT):
    e, files = inputs(root)
    coverage = e.coverage()
    return {'format':'native-research-delivery-v1', 'repository':e.profile['repository'],
            'status':'PASS_DELIVERY_CONTROLS_ONLY',
            'source_attribution_completeness':'NOT_CERTIFIED_BY_FILE_POINTERS',
            'facts_hypotheses_policy':'PRESERVE_NATIVE_CATEGORIES_NO_AUTOMATIC_PROMOTION',
            'scholarly_completeness':False, 'expert_acceptance_added':False,
            'model_behavior_empirically_validated':False,
            'collections':coverage['collections'], 'scholarly_limits':coverage['scholarly_limits'],
            'inputs':[{'path':p,'sha256':sha(b),'bytes':len(b)} for p,b in files.items()],
            'boundary':BOUNDARY}


def check(root=ROOT):
    result = report(root)
    if json.loads(local(root,REPORT).read_bytes()) != result:
        raise ValueError('research delivery report drift')
    return result


def search(text, root=ROOT, collection=None, limit=20):
    if not 1 <= limit <= 1000: raise ValueError('limit must be 1..1000')
    e = Evidence(root)
    if collection and collection not in e.collections: raise ValueError('unknown collection')
    hits=[]; matched=0
    for name,c in e.collections.items():
        if collection and name!=collection: continue
        for r in c['records']:
            if text.casefold() not in json.dumps(r['value'],ensure_ascii=False).casefold(): continue
            matched+=1
            if len(hits)<limit:
                hits.append({'repository':e.profile['repository'], 'collection':name,
                             'id':r['id'], 'native_unit':c['spec']['unit'], 'scope':c['spec']['scope'],
                             'provenance':e.provenance(c['spec']['path'],r['pointer']),
                             'native_record':r['value']})
    return {'matched_view_rows':matched, 'records':hits, 'unique_object_count':None,
            'independent_witness_count':None,'scientific_approval_granted':False,'boundary':BOUNDARY}


def answer(collection, identity, root=ROOT, request='retrieve'):
    if request!='retrieve':
        return {'status':'REFUSED_UNSUPPORTED_INFERENCE','request':request,
                'reason':'This interface can retrieve native assertions, not generate or admit a new reading.',
                'scientific_approval_granted':False}
    e=Evidence(root)
    return {'status':'NATIVE_EVIDENCE_ONLY','dossier':e.dossier(identity,collection),
            'new_claims':[], 'scientific_approval_granted':False, 'boundary':BOUNDARY}


def validate_answer(value, collection, identity, root=ROOT):
    if value != answer(collection,identity,root):
        raise ValueError('unsupported claim, citation, uncertainty or native-payload change')
    return {'status':'PASS_EXACT_EVIDENCE_RESPONSE_NOT_MODEL_EVALUATION'}


def review_template(collection,identity,root=ROOT):
    e=Evidence(root);d=e.dossier(identity,collection)
    return {'format':'native-review-submission-v1','repository':e.profile['repository'],
            'target':{'collection':collection,'id':identity,'provenance':d['provenance']},
            'profile_sha256':e.profile_hash,'status':'DRAFT_NOT_REVIEWED',
            'reviewer':{'name':'','affiliation':'','expertise':'','identity_reference':'','conflicts':'',
                        'source_dependence':'','date':''},
            'evidence_consulted':[], 'decision':'', 'reasoning':'','confidence':'',
            'counterevidence':'','unresolved_objections':'',
            'scientific_approval_granted':False,'native_changes_applied':False}


def validate_review(value,root=ROOT):
    if value.get('format')!='native-review-submission-v1': raise ValueError('invalid review format')
    target=value['target']; expected=review_template(target['collection'],target['id'],root)
    if any(value.get(k)!=expected[k] for k in ('repository','target','profile_sha256')):
        raise ValueError('review target or source revision drift')
    if value.get('status')!='SUBMITTED_FOR_MAINTAINER_CHECK' or value.get('scientific_approval_granted') is not False or value.get('native_changes_applied') is not False:
        raise ValueError('review is draft or improperly promotes acceptance')
    reviewer=value.get('reviewer',{})
    if set(reviewer)!=set(expected['reviewer']) or any(not isinstance(v,str) or not v.strip() for v in reviewer.values()):
        raise ValueError('missing reviewer disclosure')
    import datetime
    datetime.date.fromisoformat(reviewer['date'])
    if value.get('decision') not in ('SUPPORT','REJECT','INCONCLUSIVE','MORE_SOURCE_REQUIRED'):
        raise ValueError('invalid review decision')
    for key in ('reasoning','confidence','counterevidence','unresolved_objections'):
        if not isinstance(value.get(key),str) or not value[key].strip(): raise ValueError('missing review reasoning/disclosure')
    consulted=value.get('evidence_consulted')
    if not isinstance(consulted,list) or not consulted: raise ValueError('missing consulted sources')
    for source in consulted:
        for key in ('citation','locator','accessed_version','access_rights','dependence'):
            if not isinstance(source.get(key),str) or not source[key].strip(): raise ValueError('missing source disclosure')
    return {'status':'PASS_SUBMISSION_STRUCTURE_ONLY','identity_verified':False,
            'expertise_verified':False,'independence_verified':False,
            'maintainer_acceptance_required':True,'scientific_approval_granted':False,
            'boundary':'A complete form is not an authenticated review or accepted reading.'}


def package(root=ROOT):
    result=check(root); _, files=inputs(root)
    files[REPORT]=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    manifest={'format':'native-research-package-v1','repository':result['repository'],
              'redistribution_permission_granted':False,'scientific_approval_granted':False,
              'replay':'python scripts/research_delivery.py --package replay.zip',
              'files':[{'path':p,'sha256':sha(raw),'bytes':len(raw)} for p,raw in sorted(files.items())],
              'rights':'Local research packaging only. Preserve upstream licenses; this package grants no redistribution rights.'}
    files['research-package-manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as z:
        for path,raw in sorted(files.items()):
            info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,raw)
    return out.getvalue()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true')
    mode.add_argument('--search');mode.add_argument('--dossier');mode.add_argument('--review-template')
    mode.add_argument('--validate-review',type=Path);mode.add_argument('--package',type=Path)
    p.add_argument('--collection');p.add_argument('--limit',type=int,default=20)
    a=p.parse_args()
    if a.write:
        result=report();(ROOT/REPORT).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif a.check: result=check()
    elif a.search is not None: result=search(a.search,collection=a.collection,limit=a.limit)
    elif a.dossier:
        if not a.collection:p.error('--dossier requires --collection')
        result=answer(a.collection,a.dossier)
    elif a.review_template:
        if not a.collection:p.error('--review-template requires --collection')
        result=review_template(a.collection,a.review_template)
    elif a.validate_review:result=validate_review(json.loads(a.validate_review.read_bytes()))
    else:
        raw=package();a.package.write_bytes(raw)
        a.package.with_suffix(a.package.suffix+'.sha256').write_text(sha(raw)+'  '+a.package.name+'\n')
        result={'sha256':sha(raw),'bytes':len(raw),'redistribution_permission_granted':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    import sys
    try:
        main()
    except (ValueError, KeyError, IndexError, OSError) as error:
        print(json.dumps({'status':'EVIDENCE_REQUEST_REJECTED', 'error':str(error),
                          'scientific_approval_granted':False}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
