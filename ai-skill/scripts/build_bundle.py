#!/usr/bin/env python3
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/"ai-skill"/"generated";O.mkdir(parents=True,exist_ok=True)
sha=os.environ.get("SOURCE_COMMIT") or subprocess.check_output(["git","rev-parse","HEAD"],cwd=R,text=True).strip()
c=[("current_status","analysis/current-status.json"),("audit","exports/audit.json"),("coverage","data/coverage.json"),("claims","release/CLAIM-REGISTRY.csv"),("corpus_json","exports/corpus.json"),("corpus_jsonl","exports/corpus.jsonl"),("greek_subset","exports/greek-subset.json"),("eteocypriot_components","exports/eteocypriot-components.json"),("rights_matrix","DATA-LICENSE-MATRIX.md"),("rights","docs/RIGHTS.md"),("rights_and_licensing","docs/RIGHTS-AND-LICENSING.md"),("notice","NOTICE"),("method","docs/METHOD.md"),("third_party","THIRD-PARTY-NOTICES.md"),("ig_xv1_authority","research/ig-xv1-authority.json"),("pre_expert_maximum","research/pre-expert-maximum.json"),("pre_expert_source_exhaustion","research/pre-expert-source-exhaustion.json")]
a=[]
for role,rel in c:
 p=R/rel
 if p.is_file():
  b=p.read_bytes();a.append({"role":role,"path":rel,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)})
d={"schema_version":"0.3.1","skill_version":"0.3.1","source_commit":sha,"canonical_repository":True,"generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"contract":{"corpus_is_authoritative":True,"missing_means_unknown":True,"cross_corpus_equivalence_requires_explicit_evidence":True,"preserve_uncertainty":True,"preserve_source_independence":True,"preserve_rights":True},"artifacts":a}
(O/"research-bundle-index.json").write_text(json.dumps(d,indent=2)+"\n");(O/"source-state.json").write_text(json.dumps({"schema_version":"1.0","source_commit":sha,"skill_version":"0.3.1","bundle_index":"ai-skill/generated/research-bundle-index.json"},indent=2)+"\n")
