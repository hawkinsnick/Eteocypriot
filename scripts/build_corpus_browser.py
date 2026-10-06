#!/usr/bin/env python3
"""Build a self-contained, rights-aware offline corpus browser from explicit allowlisted sources."""
import csv,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
CFG=ROOT/"research/browser-sources.json"
def flatten(value,source):
 if isinstance(value,list): rows=value
 elif isinstance(value,dict):
  for k in ("records","items","inscriptions","occurrences","sources","signs"):
   if isinstance(value.get(k),list): rows=value[k];break
  else: rows=[value]
 else: rows=[]
 return [{"source":source,"record":r} for r in rows]
def load(path):
 p=ROOT/path
 if p.suffix.lower()==".csv":
  with p.open(encoding="utf-8",newline="") as f:return [{"source":path,"record":r} for r in csv.DictReader(f)]
 return flatten(json.loads(p.read_text(encoding="utf-8")),path)
def build():
 cfg=json.loads(CFG.read_text());rows=[]
 for p in cfg["sources"]: rows.extend(load(p))
 return {"format":"corpus-family-browser-v1","project":cfg["project"],"boundary":cfg["boundary"],"records":rows}
def html(data):
 payload=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c").replace("&","\\u0026")
 return """<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Corpus browser</title><style>body{font:16px system-ui;max-width:1200px;margin:auto;padding:24px;background:#f6f4ed;color:#18302d}input,select{font:inherit;padding:10px;margin:6px}table{width:100%;border-collapse:collapse;background:white}th,td{padding:9px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}.notice{padding:14px;background:#fff2d8;border-left:4px solid #a87920}.scroll{overflow:auto;max-height:72vh}</style><h1 id="title"></h1><p id="boundary" class="notice"></p><label>Search <input id="q" type="search" placeholder="identifier, site, sign, source, reading"></label><label>Source <select id="s"><option value="">All</option></select></label><p id="n"></p><div class="scroll"><table><thead><tr><th>Source</th><th>Record</th></tr></thead><tbody id="rows"></tbody></table></div><script id="data" type="application/json">"""+payload+"""</script><script>'use strict';const D=JSON.parse(document.getElementById("data").textContent),$=x=>document.getElementById(x);$("title").textContent=D.project+" corpus browser";$("boundary").textContent=D.boundary;for(const s of [...new Set(D.records.map(x=>x.source))]){let o=document.createElement("option");o.value=o.textContent=s;$("s").append(o)}function draw(){let q=$("q").value.toLowerCase(),s=$("s").value,a=D.records.filter(x=>(!s||x.source===s)&&(!q||JSON.stringify(x.record).toLowerCase().includes(q)));$("rows").replaceChildren();for(const x of a.slice(0,1500)){let tr=document.createElement("tr"),a1=document.createElement("td"),a2=document.createElement("td");a1.textContent=x.source;a2.textContent=JSON.stringify(x.record);tr.append(a1,a2);$("rows").append(tr)}$("n").textContent=a.length+" matches"+(a.length>1500?" (first 1500 shown)":"")} $("q").oninput=$("s").onchange=draw;draw();</script>"""
def main():
 data=build();(ROOT/"workbench").mkdir(exist_ok=True);(ROOT/"workbench/corpus-browser.html").write_text(html(data),encoding="utf-8");print("wrote",len(data["records"]),"records")
if __name__=="__main__":main()
