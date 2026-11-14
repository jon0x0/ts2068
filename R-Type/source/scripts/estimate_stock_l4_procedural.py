"""Measure exact L4 metadata with procedural pixel reconstruction."""
from pathlib import Path
import json
from pack_optimal_r87 import pack_optimal
from stock_frame_packets import frame_packets
prefix=Path('scripts/estimate_stock_l4_grammar.py').read_text().split('seq=[]',1)[0];exec(prefix)
# Prefix keeps frame set but not a remap; identify normalized source frames again.
def find(f):return next(i for i,g in enumerate(j['frames'])if all(f[k]==g[k]for k in ('w','h','bits','rows')))
mi={}
for v in m['variants']:
 f=m['frames'][v['frame']];f=dict(f,rows=[pmap[p]if p>=0 else -1 for p in f['rows']]);mi[v['id'],v['anim'],v['px'],v['py'],v['flip']]=find(f)
used=sorted({pi for f in j['frames']for pi in f['rows']if pi>=0});pm={old:i for i,old in enumerate(used)};j['palette']=[j['palette'][i]for i in used]
for f in j['frames']:f['rows']=[pm[p]if p>=0 else -1 for p in f['rows']]
raws=[];metadata={};parents=set();specs={}
for key,fi in mi.items():
 ident,anim,x,y,flip=key;parent=mi[ident,anim,0,0,flip];parents.add(parent)
 if x or y:
  dx=(8-2*x)%8 if flip&1 else 2*x;dy=(8-2*y)%8 if flip&2 else 2*y;spec=(parent,dx,dy)
  assert fi not in specs or specs[fi]==spec
  specs[fi]=spec
for fi,f in enumerate(j['frames']):
 local=sorted(set(f['rows'])-{-1});mapping={pi:i+(i>=54)for i,pi in enumerate(local)};local=local[:54]+([0]+local[54:]if len(local)>54 else []);native=bytearray(f['bits']);tags=[];offset=0;prev=0
 for pi in f['rows']:
  if pi<0:tags.append(54);offset+=1
  else:tag=mapping[pi];native[offset]=tag;tags.append(128|((tag-prev)&127));prev=tag;offset+=9
 raw=bytes([f['w'],f['h'],len(local)])+b''.join(pi.to_bytes(2,'little')for pi in local)+native;raws.append(raw)
 if fi in specs:
  runs=[]
  for pi in local:
   if runs and runs[-1][0]+runs[-1][1]==pi and runs[-1][1]<255:runs[-1][1]+=1
   else:runs.append([pi,1])
  meta=bytes([f['w'],f['h'],len(local),len(runs)])+b''.join(p.to_bytes(2,'little')+bytes([count])for p,count in runs)+bytes(tags)
  metadata[fi]=dict(spec=specs[fi],raw=list(meta),bytes=len(pack_optimal(meta))+3)
packets,saved=frame_packets(raws,[(f['w'],f['h'])for f in j['frames']]);total=0;ordinary=parentbytes=metabytes=0
for fi,p in enumerate(packets):
 if fi in metadata:total+=metadata[fi]['bytes'];metabytes+=metadata[fi]['bytes']
 else:
  if p['base']in specs or fi in parents:p=dict(base=None,data=pack_optimal(raws[fi]))
  total+=len(p['data'])
  if fi in parents:parentbytes+=len(p['data'])
  else:ordinary+=len(p['data'])
print(dict(total=total,ordinary=ordinary,parents=parentbytes,metadata=metabytes,phase_frames=len(metadata),palette_rows=len(j['palette'])),flush=True)
Path('build/cartridges/integration_work/level04/procedural_budget.json').write_text(json.dumps(dict(total=total,ordinary=ordinary,parents=parentbytes,metadata_bytes=metabytes,metadata=metadata,frames=j['frames'],palette=j['palette'])))
