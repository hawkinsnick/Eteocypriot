#!/usr/bin/env python3
import argparse,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument("output");a=p.parse_args();v=json.loads((R/"data/records.json").read_text());rows=v if isinstance(v,list) else v.get("records",[]);out=pathlib.Path(a.output);out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n");out.with_suffix(out.suffix+".manifest.json").write_text(json.dumps({"records":len(rows),"source_layer":"IG XV 1 digital","license":"CC BY 4.0","physical_objects_certified":0,"independent_epigraphic_review":False},indent=2)+"\n")
