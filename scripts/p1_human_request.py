"""Check a prepared human request; never accept a review or admit a reading."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPOSITORY='hawkinsnick/Eteocypriot'
REQUIRED_ROUTING={'ETE-IG150-QUARANTINE': ('source_edition_editor', 'CORRECTED_SOURCE_PENDING')}
def validate(root=ROOT,request=None):
    root=Path(root);r=request if request is not None else json.loads((root/'review/p1-human-request.json').read_text())
    if r['repository']!=REPOSITORY or r['status']!='PREPARED_NOT_REVIEWED' or r['format']!='corpus-p1-human-request-v1':raise ValueError('prepared request identity/state drift')
    if r['decisions'] or r['automatic_admission'] is not False or r['scientific_approval_granted'] is not False:raise ValueError('prepared request promoted to acceptance')
    for k in ['reviewer','affiliation','review_date','expertise_evidence','conflicts_and_source_dependence','signed_or_attributed_review_evidence']:
        if r[k] is not None:raise ValueError('prepared request falsely populated as independent review')
    p='research/p1-source-followup-2026-10-16.json';b=(root/p).read_bytes()
    if r['inputs']!=[{'path':p,'sha256':hashlib.sha256(b).hexdigest()}]:raise ValueError('source packet binding stale')
    d=json.loads(b);cases={c['id']:i for i,c in enumerate(d['cases'])};questions=r['questions']
    if len(questions)!=len(cases) or {q['id'] for q in questions}!=cases.keys():raise ValueError('question scope omitted or duplicated')
    for q in questions:
        if (q['role_required'],q['stage'])!=REQUIRED_ROUTING[q['id']]:raise ValueError('acquisition/maintainer/judgment routing confused')
        if q['source_packet_pointer']!='/cases/'+str(cases[q['id']]) or not q['evidence_prerequisites'] or not q['question'] or not q['effect_of_no_decision']:raise ValueError('exact question context absent')
        if set(q['decision_requested'])!={'supported_with_scope','rejected_with_counterevidence','inconclusive','additional_source_required'}:raise ValueError('inconclusive or negative decision erased')
    return {'status':'PASS_PREPARED_HUMAN_REQUEST','repository':REPOSITORY,'questions':len(questions),'human_review_performed':False,'scientific_acceptance_granted':False}
if __name__=='__main__':print(json.dumps(validate()))
