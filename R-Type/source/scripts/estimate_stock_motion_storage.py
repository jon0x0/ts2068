"""Lossless storage estimate for all captured TAP fractional artwork."""
from pathlib import Path
import json
from stock_frame_packets import frame_packets
O=Path('build/cartridges/integration_work');reports=[]
for n in range(2,9):
 base=json.loads((O/f'level{n:02d}/combined_frames.json').read_text());motion=json.loads((O/f'L{n}_tap_motion_frames.json').read_text());j=json.loads(json.dumps(base));pmap=[]
 for row in motion['palette']:
  row=[a&~64 if a&64 and(not a&7 or not a&56)else a for a in row]
  if row not in j['palette']:j['palette'].append(row)
  pmap.append(j['palette'].index(row))
 for f in motion['frames']:
  f=dict(f,rows=[pmap[p]if p>=0 else -1 for p in f['rows']])
  if f not in j['frames']:j['frames'].append(f)
 raws=[]
 for f in j['frames']:
  local=sorted(set(f['rows'])-{-1});mapping={pi:i+(i>=54)for i,pi in enumerate(local)};local=local[:54]+([0]+local[54:]if len(local)>54 else []);native=bytearray(f['bits']);off=0
  for pi in f['rows']:
   if pi<0:off+=1
   else:native[off]=mapping[pi];off+=9
  raws.append(bytes([f['w'],f['h'],len(local)])+b''.join(pi.to_bytes(2,'little')for pi in local)+native)
 packets,saved=frame_packets(raws,[(f['w'],f['h'])for f in j['frames']]);pairs=list(dict.fromkeys(tuple(row[i:i+2])for row in j['palette']for i in range(0,8,2)));assert len(pairs)<=256
 bpack,bsaved=frame_packets(raws[:len(base['frames'])],[(f['w'],f['h'])for f in base['frames']]);old=sum(len(p['data'])for p in bpack);new=sum(len(p['data'])for p in packets);layout=json.loads((O/f'level{n:02d}/shared_cache_layout.json').read_text());free=sum(e-a for a,e in layout['free_segments']);raw=bytes(255 if v['frame']<0 else v['frame']for v in base['variants']);size=64 if n==2 else 16;rows=[raw[i:i+size]for i in range(0,len(raw),size)];unique=list(dict.fromkeys(rows));vpacked=len(rows)+2*len(unique)+sum(1+next(p for p in (1,2,4,8,16,32,64)if p<=size and all(row[k]==row[k%p]for k in range(size)))for row in unique);vsave=0 if n==2 else len(raw)-vpacked
 r=dict(level=n,frames=len(j['frames']),palette_rows=len(j['palette']),max_cache=max(map(len,raws)),old_packets=old,new_packets=new,palette_pairs=len(pairs),palette_pair_bytes=4*len(j['palette'])+2*len(pairs),additional_art_bytes=new-old+4*len(j['palette'])+2*len(pairs)-8*len(base['palette']),rom_free=free,additional_variant_saving=vsave,scope='Exact frame-packet roundtrip and storage estimate; excludes new runtime/phase lookup code and page directory, not release eligible');reports.append(r);print(r,flush=True)
(O/'motion_storage_estimate.json').write_text(json.dumps(reports,indent=2))
