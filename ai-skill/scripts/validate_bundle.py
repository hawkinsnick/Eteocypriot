#!/usr/bin/env python3
import json,sys
from pathlib import Path
d=json.loads((Path(__file__).resolve().parents[1]/"generated"/"research-bundle-index.json").read_text());e=[]
for k in ("schema_version","skill_version","source_commit","contract","artifacts"):
 if k not in d:e.append("missing "+k)
seen=set()
for a in d.get("artifacts",[]):
 if a.get("path") in seen:e.append("duplicate "+str(a.get("path")))
 seen.add(a.get("path"))
 if len(a.get("sha256",""))!=64:e.append("bad sha "+str(a.get("path")))
if e:print("\n".join(e));sys.exit(1)
print("AI bundle valid")
