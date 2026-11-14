"""Optional original-sized spheres/80px core, preserving larger approved r51 build."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
from build_rocket_fix import code
from build_graphics import PALETTE
from preview_bellmite_detail import legal
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/compact_boss_r51'
def main():
 src=ROOT/'build/fullgame/fast_boss_r51';OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(src/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 b=bytearray((src/'level05_region.bin').read_bytes());native=bytearray(65536);native[0xc000:]=b[0xa000:0xe000];dictionary=bytes(b[0x2000:0x2400]);layout=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][4];table=layout['enemy_descriptors_start'];d=table+7*4;w,h=native[d:d+2];p=int.from_bytes(native[d+2:d+4],'little');rgb=np.zeros((h*8,w*8,3),np.uint8)
 for cy in range(h):
  for cx in range(w):
   tag=native[p]
   if tag==54:p+=1;continue
   for y in range(8):
    a=dictionary[(tag&127)*8+y];px=native[p+1+y]
    for x in range(8):
     c=(a&7)if px&(128>>x)else((a>>3)&7);rgb[cy*8+y,cx*8+x]=PALETTE[c+(8 if a&64 else 0)]
   p+=9
 core=np.asarray(Image.fromarray(rgb).resize((80,80),Image.Resampling.LANCZOS),dtype=float);mask=core.max(2)>35;core[~mask]=0;payload=bytearray();fitted=np.zeros((80,80,3),np.uint8)
 for cy in range(10):
  for cx in range(10):
   target=core[cy*8:cy*8+8,cx*8:cx*8+8];visible=mask[cy*8:cy*8+8,cx*8:cx*8+8]
   if not visible.any():payload.append(54);continue
   choices=[]
   for idx in range(128):
    if idx==54:continue
    a=np.frombuffer(dictionary[idx*8:idx*8+8],np.uint8);br=np.where(a&64,8,0);pi=((a>>3)&7)+br;qi=(a&7)+br
    if np.any((~visible).any(1)&(pi%8!=0)):continue
    paper=PALETTE[pi];ink=PALETTE[qi];pe=((target-paper[:,None])**2).sum(2);ie=((target-ink[:,None])**2).sum(2);bits=ie<pe;bits[~visible]=False;error=np.minimum(pe,ie)[visible].sum();choices.append((error,idx,bits,paper,ink))
   _,idx,bits,paper,ink=min(choices,key=lambda q:q[0]);payload.append(idx);payload+=np.packbits(bits,axis=1).tobytes();fitted[cy*8:cy*8+8,cx*8:cx*8+8]=np.where(bits[:,:,None],ink[:,None],paper[:,None])
 assert len(payload)<=0x450;native[0xefa1:0xf3f1]=bytes([54])*0x450;native[0xefa1:0xefa1+len(payload)]=payload;native[d:d+4]=bytes([10,10])+bytes.fromhex('a1 ef');Image.fromarray(fitted).save(OUT/'core80.png')
 pairs=bytearray(768);flipped=bytearray(768)
 for cel in range(3):
  im=Image.open(ROOT/f'build/graphics/bellmite_blue_rim_feedback/H_sphere{cel}.png').convert('RGBA').resize((24,24),Image.Resampling.LANCZOS);a=np.array(im);mask=a[:,:,3]>=128;preview=legal(a[:,:,:3],mask);preview.save(OUT/f'sphere{cel}_24.png');target=np.array(preview);raw=bytearray(144)
  for cy in range(3):
   for cx in range(3):
    cell=cy*3+cx;rowbits=[]
    for y in range(8):
     colours=target[cy*8+y,cx*8:cx*8+8];choices=[]
     for bright in range(2):
      for paper in range(8):
       for ink in range(8):
        if bright and(paper==0 or ink==0):continue
        pi=paper+bright*8;ii=ink+bright*8;pb=np.all(colours==PALETTE[pi],axis=1);ib=np.all(colours==PALETTE[ii],axis=1)
        if np.all(pb|ib):choices.append((paper*8+ink+bright*64,int(np.packbits(ib)[0])))
     assert choices;attr,px=choices[0];q=(cel*16+cell)*16+y*2;pairs[q:q+2]=bytes([px,attr]);flipped[q:q+2]=bytes([int(f'{px:08b}'[::-1],2),attr]);rowbits.append(px)
    raw[cell*9+1:cell*9+9]=rowbits
  pos=0xf3f1+cel*144;native[pos:pos+144]=raw
 for ident,cel in zip(range(30,34),[0,1,2,1]):
  q=table+(ident-1)*4;native[q:q+4]=bytes([3,3])+(0xf3f1+cel*144).to_bytes(2,'little')
 b[0xa000:0xe000]=native[0xc000:];b[0x8c00:0x8f00]=pairs;b[0xf380:0xf680]=flipped;records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  data=b if n==5 else(src/f'{name}_region.bin').read_bytes();(OUT/f'{name}_region.bin').write_bytes(data);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',data[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(data).hexdigest()))
 for name in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','overlay.bin','overlay.sym','gateway.bin','gateway.sym','irq.bin','irq.sym','compositor.bin','compositor.sym']:shutil.copy2(src/name,OUT/name)
 (OUT/'native_level5.bin').write_bytes(native);(OUT/'enemy_palette.bin').write_bytes(dictionary);(OUT/'manifest.json').write_text(json.dumps(dict(status='Compact candidate; validation pending',regions=records,sphere_size=[24,24],core_size=[80,80],native_sphere_size=[24,24],native_core_size=[64,64],core_payload_bytes=len(payload),sphere_cell_budget=9,core_cell_budget=100,movement_anchors_unchanged=True),indent=2));print('compact core bytes',len(payload))
if __name__=='__main__':main()
