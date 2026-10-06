#!/usr/bin/env python3
import argparse,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1];F={"records":"data/records.json","concordance":"research/source-concordance-register.json","disagreements":"research/disagreement-register.json","lineage":"research/source-lineage-register.json","coins":"research/coin-source-comparison.json"}
def rows(k):
 v=json.loads((R/F[k]).read_text())
 if isinstance(v,list):return v
 for z in ("records","entries","lineages","items"):
  if isinstance(v.get(z),list):return v[z]
 return [v]
p=argparse.ArgumentParser();p.add_argument("resource",choices=F);p.add_argument("--text",default="");p.add_argument("--limit",type=int,default=50);a=p.parse_args();q=a.text.casefold();x=[v for v in rows(a.resource) if not q or q in json.dumps(v,ensure_ascii=False).casefold()][:a.limit];print(json.dumps({"resource":a.resource,"records":x,"boundary":"Source-attributed digital edition evidence; language/object identity and independent epigraphic verification remain controlled."},ensure_ascii=False,indent=2))
