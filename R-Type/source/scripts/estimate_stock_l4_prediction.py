"""Lossless predictive byte-plane budget for full exact L4 phase frames."""
from pathlib import Path
import json
from pack_optimal_r87 import pack_optimal
from stock_frame_packets import frame_packets
prefix=Path('scripts/estimate_stock_l4_grammar.py').read_text().split('seq=[]',1)[0];exec(prefix)
used=sorted({pi for f in j['frames']for pi in f['rows']if pi>=0});pm={old:i for i,old in enumerate(used)};j['palette']=[j['palette'][i]for i in used]
for f in j['frames']:f['rows']=[pm[p]if p>=0 else -1 for p in f['rows']]
raws=[];records=[]
for fi,f in enumerate(j['frames']):
 local=sorted(set(f['rows'])-{-1});mapping={pi:i+(i>=54)for i,pi in enumerate(local)};local=local[:54]+([0]+local[54:]if len(local)>54 else []);native=bytearray(f['bits']);offset=0
 for pi in f['rows']:
  if pi<0:offset+=1
  else:native[offset]=mapping[pi];offset+=9
 plain=bytes([f['w'],f['h'],len(local)])+b''.join(pi.to_bytes(2,'little')for pi in local)+native;best=(len(pack_optimal(plain)),0,plain)
 for pal in (False,True):
  for tags in (False,True):
   if tags and len(local)>=128:continue
   for pred in (0,1,2,4):
    mode=int(pal)|(int(tags)<<1)|({0:0,1:1,2:2,4:3}[pred]<<2);buf=bytearray([f['w']|128,f['h'],len(local),mode]);prev=0
    for pi in local:
     value=(pi-prev)&65535 if pal else pi;buf+=value.to_bytes(2,'little');prev=pi
    offset=0;prevtag=0
    for pi in f['rows']:
     tag=native[offset];offset+=1
     if tag==54:buf.append(54);continue
     buf.append(128|((tag-prevtag)&127)if tags else tag);prevtag=tag
     pixels=native[offset:offset+8];offset+=8
     buf.extend(value^(pixels[y-pred]if pred and y>=pred else 0)for y,value in enumerate(pixels))
    packet=pack_optimal(buf)
    if len(packet)<best[0]:best=(len(packet),mode,bytes(buf))
 raws.append(best[2]);records.append(dict(frame=fi,plain=len(pack_optimal(plain)),packed=best[0],mode=best[1]))
packets,saved=frame_packets(raws,[(f['w'],f['h'])for f in j['frames']]);print('frames',len(raws),'palette',len(j['palette']),'pixels+metadata',sum(len(p['data'])for p in packets),'sparse saved',saved,'plain LZ',sum(r['plain']for r in records),'predict LZ',sum(r['packed']for r in records),flush=True)
Path('build/cartridges/integration_work/level04/predictive_budget.json').write_text(json.dumps(dict(records=records,frames=len(raws),palette_rows=len(j['palette']),bytes=sum(len(p['data'])for p in packets),raws=[list(r)for r in raws])))
