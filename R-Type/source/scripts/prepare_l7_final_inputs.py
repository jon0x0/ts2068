from pathlib import Path
import json,sys,zipfile,numpy as np
R=Path.cwd();sys.path.insert(0,'scripts');from boss_motion_assets_r60 import unpack
from pack_optimal_r87 import pack_optimal as pack
B=R/'build/fullgame/highscore_r138';O=R/'build/graphics/l7_final_inputs';O.mkdir(exist_ok=True);b=(B/'level07_region.bin').read_bytes();w=next(v for v in json.loads((B/'walker_runtime.json').read_text())if v['level']==7);t=w['preload_table'];cache=bytearray(4864)
for k in range(b[t]):
 p=int.from_bytes(b[t+1+k*4:t+3+k*4],'little');d=int.from_bytes(b[t+3+k*4:t+5+k*4],'little')-0xc000;v=unpack(b[p:]);cache[d:d+len(v)]=v
raw=bytearray((B/'L7_runtime_art.bin').read_bytes());entries=[];assets=[];selections=[]
for key,file,ids,poses,destcache in [('white','rtype-l7-walker-assets.zip',[14,15,16,17],[0,1,2,1],None),('cyan','cyanwalker.rtype-l7-walker-variant-assets.zip',[30,31,32],[0,1,2],0xc980),('orb','L7asteroid.rtype-l1-walker-assets.zip',[35],[0],None),('round','rtype-l1-walker-assets.redyelgrn.zip',[37],[0],None),('emergence','L7emergingmech.rtype-l1-walker-assets.zip',[51],[0],None),('wall','rtype-l7-wall-assembled-assets.zip',[42,43,44,45],[0,1,2,3],0xcb30)]:
 z=zipfile.ZipFile(R/'convref'/file);doc=json.loads(z.read('choices.json'));fam=doc['families']['walker'];seen={}
 for ident,k in zip(ids,poses):
  f=fam['frames'][k];ww,hh=f['width'],f['height'];v=z.read(f'walker/frame_{k:02d}.pairs.bin')
  if k not in seen:
   ptr=(destcache+sum(fam['frames'][j]['pairBytes']for j in range(k)))if destcache else 0xb200+len(raw);seen[k]=ptr
   if destcache:cache[ptr-0xc000:ptr-0xc000+len(v)]=v
   else:raw+=v
  ptr=seen[k];entries.append(dict(id=ident,width=16 if key=='wall' else ww,height=hh,ptr=ptr,key=key,frame=k,sha256=__import__('hashlib').sha256(v).hexdigest()));assets.append(dict(id=ident,key=key,frame=k,pointer=ptr,bytes=len(v),size=[ww,hh]));(O/f'{key}_{k}.pairs').write_bytes(v);(O/f'{key}_{k}.png').write_bytes(z.read(f'walker/frame_{k:02d}.png'))
 selections.append(dict(key=key,file=file,settings=fam['settings']))
# Static housing uses the right half of the chosen rest frame; the moving actor
# renders the complete assembly so its overlap/colours match the chosen result.
entries.append(dict(id=41,width=16,height=32,ptr=0xcbb0,key='wall_body',frame=0));assert len(raw)<=0xe00 and 0xcf30<=0xcf80
(O/'cache.bin').write_bytes(cache);(O/'raw.bin').write_bytes(raw);(O/'entries.json').write_text(json.dumps(entries,indent=2));(O/'assets.json').write_text(json.dumps(assets,indent=2));(O/'selections.json').write_text(json.dumps(selections,indent=2));planar=cache[0::2]+cache[1::2];print('raw',len(raw),'cache',len(cache),'planar',len(pack(planar)),'interleaved',len(pack(cache)),'rawpack',len(pack(raw)))
for split in[512,640]:print('split',split,len(pack(planar[:split])),len(pack(planar[split:split+384])),len(pack(planar[split+384:])))
