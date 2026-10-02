#!/usr/bin/env python3
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sha=os.environ.get("SOURCE_COMMIT") or subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
state={"schema_version":"1.0","source_commit":sha,"generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"policy":"The repository corpus is canonical; this generated state records the corpus/code commit that triggered synchronization.","skill_version":"0.1.0"}
out=root/"ai-skill"/"generated"/"source-state.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
