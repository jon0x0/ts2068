from pathlib import Path
import json,zlib,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'build/fullgame/l5_effects_fast_r59';OUT=ROOT/'build/diagnostics/boss_motion_r60'
LAYOUTS=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels']
PALETTE=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],dtype=np.int32)
def decode(n,ident):
 b=(BASE/f'level{n:02d}_region.bin').read_bytes();mem=bytes(0xc000)+b[0xa000:0xe000];table=LAYOUTS[n-1]['enemy_descriptors_start'];q=table+(ident-1)*4;w,h=mem[q:q+2];ptr=int.from_bytes(mem[q+2:q+4],'little');p=ptr;im=np.zeros((h*8,w*8),np.uint8)
 for cy in range(h):
  for cx in range(w):
   tag=mem[p];p+=1
   if tag==54:continue
   for y in range(8):
    a=b[0x2000+(tag&127)*8+y];bits=mem[p+y];im[cy*8+y,cx*8:cx*8+8]=[(a&7)if bits&(128>>x)else(a>>3)&7 for x in range(8)]
   p+=8
 return im,ptr,p
# Backreference packets: literal1..127 bytes; high bit = len3..130, 16-bit backward distance; zero terminator.
def pack(raw):
 raw=bytes(raw)
 out=bytearray();literal=bytearray();index={};i=0
 def flush():
  while literal:chunk=literal[:127];out.append(len(chunk));out.extend(chunk);del literal[:127]
 while i<len(raw):
  key=raw[i:i+3];best=0;distance=0
  for pos in reversed(index.get(key,[])[-96:]):
   if i-pos>65535:continue
   length=3
   while length<130 and i+length<len(raw)and raw[pos+length]==raw[i+length]:length+=1
   if length>best:best=length;distance=i-pos
   if best==130:break
  size=best if best>=5 else 1
  if size>1:flush();out.append(128+size-3);out.extend(distance.to_bytes(2,'little'))
  else:literal.append(raw[i]);
  for j in range(i,i+size):index.setdefault(raw[j:j+3],[]).append(j)
  if len(literal)>=127:flush()
  i+=size
 flush();out.append(0);return bytes(out)
def unpack(raw):
 out=bytearray();p=0
 while raw[p]:
  c=raw[p];p+=1
  if c<128:out+=raw[p:p+c];p+=c
  else:
   d=int.from_bytes(raw[p:p+2],'little');p+=2
   for _ in range((c&127)+3):out.append(out[-d])
 return bytes(out)
def phases(im):
 h,w=im.shape;result=[]
 for shift in [0,2,4,6]:
  dst=np.zeros((h,w+8),np.uint8);dst[:,shift:shift+w]=im;raw=bytearray()
  for cx in range(w//8+1):
   for y in range(h):
    row=dst[y,cx*8:cx*8+8];cs=sorted(set(map(int,row)))
    if len(cs)>2:
     combos=[(p,q)for p in cs for q in cs if p<q and(0 not in cs or p==0)]
     p,q=min(combos,key=lambda t:np.minimum(((PALETTE[row]-PALETTE[t[0]])**2).sum(1),((PALETTE[row]-PALETTE[t[1]])**2).sum(1)).sum());sel=(((PALETTE[row]-PALETTE[q])**2).sum(1)<((PALETTE[row]-PALETTE[p])**2).sum(1));sel[row!=0]=True if p==0 else sel[row!=0]
    else:p=cs[0];q=cs[-1];sel=row==q if p!=q else np.zeros(8,bool)
    raw.extend([sum(128>>x for x in range(8)if sel[x]),p*8+q])
  result.append(bytes(raw))
 return result
SELECT={2:list(range(3,7)),3:[40]+list(range(101,107)),4:[25,26,27],6:list(range(18,26)),7:list(range(49,55)),8:list(range(42,47))}
def main():
 OUT.mkdir(parents=True,exist_ok=True);report=[]
 for n,ids in SELECT.items():
  compressed={};size=0
  for ident in ids:
   im,p,end=decode(n,ident)
   for phase,raw in enumerate(phases(im)):
    v=pack(raw);assert unpack(v)==raw
    compressed.setdefault(v,len(v))
  size=sum(compressed.values());report.append(dict(level=n,descriptors=ids,unique_phases=len(compressed),packed=size));print(report[-1],flush=True)
 (OUT/'phase_budget.json').write_text(json.dumps(report,indent=2))
 for n,l in enumerate(LAYOUTS,1):
  ids=range(1,len(l['enemies'])+1);sheet=Image.new('RGB',(1000,((len(l['enemies'])+9)//10)*110),'#111');d=ImageDraw.Draw(sheet);rows=[]
  for k,ident in enumerate(ids):
   im,p,e=decode(n,ident);cs=sorted(set(im.flatten())-{0});rows.append(dict(id=ident,size=[im.shape[1],im.shape[0]],colours=len(cs),pointer=p,end=e));pic=Image.fromarray(PALETTE[im].astype(np.uint8));pic.thumbnail((96,85),Image.Resampling.NEAREST);x=k%10*100;y=k//10*110;d.text((x,y),str(ident)+' '+str(len(cs))+'c',fill='white');sheet.paste(pic,(x,y+18))
  sheet.save(OUT/f'level{n}_atlas.png');(OUT/f'level{n}_audit.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
