from pathlib import Path
import sys,json,shutil,subprocess,re,zipfile,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l2_integrated_r123';O=R/'build/fullgame/l2_scroll_projectile_r125';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.json','.asm','.sym']and not any(s in p.name for s in['.home.','validation','approach','mismatch','trace','timing','probe','final_l2','native_jump']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());original=bytes(16384)+(R/'build/fullgame/foundation/level02.raw').read_bytes();oldmanifest=json.loads((R/'build/graphics/l2_integrated_r67/manifest.json').read_text());tiles=[]
for n in range(34):
 v=bytearray(original[0xe762-(n+1)*144:0xe762-n*144]);v[::9]=bytes(0x86 if any(v[i+1:i+9]) else 7 for i in range(0,144,9));tiles.append(bytes(v))
for row in oldmanifest['tiles']:
 v=bytearray(unpack(b[row['pointer']-0x2000:]));assert len(v)==144
 for i in range(0,144,9):
  if v[i]<16:v[i]+=16
  tag=v[i];pi=tag+96 if tag<32 else tag-144;aa=(bytes(b[0x2000:0x2380])+bytes(b[0x2000:0x2080]))[pi*8:pi*8+8]
  visible=any(((at&7)!=0 and bit!=0)or(((at>>3)&7)!=0 and bit!=255)for at,bit in zip(aa,v[i+1:i+9]))
  if not visible:v[i]=7
 tiles.append(bytes(v))
# Copy the legacy sixteen patterns to legal high dictionary IDs112..127.
b[0x2380:0x2400]=b[0x2000:0x2080]
original_tiles=tiles;tiles=[bytes(t[::9])+bytes(v for i,v in enumerate(t)if i%9)for t in tiles];a=[np.frombuffer(t,np.uint8)for t in tiles];cost=[len(pack(t))for t in tiles];delta={}
for i in range(52):
 for k in range(i):delta[i,k]=len(pack((a[i]^a[k]).tobytes()))+1
bases=set();best=cost[:];mapping=list(range(52))
while True:
 opts=[]
 for k in range(52):
  if k in bases:continue
  gain=sum(max(0,best[i]-delta.get((max(i,k),min(i,k)),999))for i in range(52)if i!=k and i not in bases)-(cost[k]-best[k]);opts.append((gain,k))
 gain,k=max(opts)
 if gain<=0:break
 bases.add(k);best[k]=cost[k];mapping[k]=k
 for i in range(52):
  c=delta.get((max(i,k),min(i,k)),999)
  if i not in bases and c<best[i]:best[i]=c;mapping[i]=k
# Refine the bounded-depth dictionary against actual packet cost.
def fit(bs):
 mp=[];score=0
 for i in range(52):
  opts=[(cost[i],i)] if i in bs else [(cost[i],i)]+[(delta[max(i,k),min(i,k)],k)for k in bs if k!=i]
  c,k=min(opts);score+=c;mp.append(k)
 return score,mp
score,mapping=fit(bases)
for repeat in range(8):
 options=[(score,bases,mapping)]
 for k in range(52):
  trial=bases-{k} if k in bases else bases|{k};v,mp=fit(trial);options.append((v,trial,mp))
 for k in bases:
  for v in set(range(52))-bases:
   trial=(bases-{k})|{v};c,mp=fit(trial);options.append((c,trial,mp))
 new,bs,mp=min(options,key=lambda v:v[0])
 if new>=score:break
 score,bases,mapping=new,bs,mp
packets=[(b'' if mapping[i]==i else bytes([mapping[i]]))+pack(t if mapping[i]==i else(a[i]^a[mapping[i]]).tobytes())for i,t in enumerate(tiles)];aliases={};groups={}
for i,t in enumerate(tiles):groups.setdefault(t,[]).append(i)
for group in groups.values():
 leader=next((i for i in group if mapping[i]==i),group[0])
 for i in group:
  if i!=leader:aliases[i]=leader
total=sum(len(v)for i,v in enumerate(packets)if i not in aliases);print('PLANAR TOTAL',total);sys.exit(0)
