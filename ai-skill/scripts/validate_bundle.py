#!/usr/bin/env python3
import hashlib,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"ai-skill";e=[]
d=json.loads((A/"generated"/"research-bundle-index.json").read_text());m=json.loads((A/"manifest.json").read_text());p=json.loads((A/"references"/"authority-profile.json").read_text());s=(A/"SKILL.md").read_text();x=re.search(r"^version:\s*([^\s]+)",s,re.M)
if (x.group(1) if x else None)!=m.get("skill_version"):e.append("skill manifest mismatch")
if d.get("skill_version")!=m.get("skill_version"):e.append("bundle manifest mismatch")
if d.get("schema_version")!=m.get("bundle_schema"):e.append("bundle schema mismatch")
idx={a.get("path"):a for a in d.get("artifacts",[])}
for q in p.get("required_authorities",[]):
 f=R/q["path"];a=idx.get(q["path"])
 if not f.is_file():e.append("missing authority "+q["path"])
 elif not a:e.append("authority not indexed "+q["path"])
 elif a.get("sha256")!=hashlib.sha256(f.read_bytes()).hexdigest():e.append("authority hash mismatch "+q["path"])
if e:print("\n".join(e));sys.exit(1)
print(p["corpus"]+" AI integration validation PASS")
