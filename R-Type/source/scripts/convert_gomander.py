"""Arcade tile-layer boss mapped into native level2 terrain slots19..31."""
from pathlib import Path
import numpy as np,json
from PIL import Image
from build_graphics import PALETTE,quantize
ROOT=Path(__file__).resolve().parents[1]
def build():
 d=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][1];mem=bytes(16384)+(ROOT/'build/fullgame/foundation/level02.raw').read_bytes();end=d['map_start'];patch=bytearray(b''.join(mem[end-(t+1)*144:end-t*144]for t in range(d['terrain_tiles'])))
 src=Image.open(ROOT/'build/fullgame/arcade_reference/frame017400.png').convert('RGB').crop((64,96,320,240));a=np.asarray(src).astype(int);mask=(a[:,:,0]>a[:,:,2]+12)&(a[:,:,1]>a[:,:,2]+5)&(a.max(2)>12);a[~mask]=0;src=Image.fromarray(a.astype('uint8')).resize((224,96),Image.Resampling.LANCZOS);rgb=np.asarray(src).astype(float)
 # A coherent32-scanline ramp keeps horizontally scrolling cells compatible.
 colors=[]
 for y in range(32):
  row=rgb[y::32].reshape(-1,3);on=row.max(1)>20;v=row[on].mean(0)if on.any()else np.array([180,90,50]);colors.append(int(np.argmin(((PALETTE[1:]-v)**2).sum(1)))+1)
 attrs=np.array([(c&7)|(64 if c>=8 else 0)for c in colors],dtype='uint8');pairs=np.zeros((96,28,2),dtype=int);pairs[:,:,1]=np.tile(colors,3)[:,None];bits,_,_=quantize(src,pairs=pairs);bits[rgb.max(2)<12]=0
 world=mem[d['map_start']:d['map_end']];done=set()
 for col in range(56,63):
  for row in range(2,5):
   code=world[col*5+row];ident=code&63
   if ident not in range(19,32)or ident in done or code&192:continue
   b=bits[(row-2)*32:(row-1)*32,(col-56)*32:(col-55)*32]
   for cy in range(4):
    for cx in range(4):
     p=ident*144+(cy*4+cx)*9
     # Retain native solidity and empty-cell envelope.
     if patch[p]&128:patch[p+1:p+9]=np.packbits(b[cy*8:cy*8+8,cx*8:cx*8+8],axis=1).tobytes()
   done.add(ident)
 assert done==set(range(19,32)),done
 out=ROOT/'build/fullgame/converted/level02';(out/'terrain_bitmap_overrides.bin').write_bytes(patch);(out/'terrain_boss_palette.bin').write_bytes(attrs);src.save(out/'gomander_arcade.png');Image.fromarray(PALETTE[np.where(bits,np.tile(colors,3)[:,None],0)].astype('uint8')).save(out/'gomander_ecm.png');report=json.loads((out/'manifest.json').read_text());report['background_boss_pending']=False;report['background_boss']={'tiles':sorted(done),'source_frame':17400,'native_solid_flags_preserved':True,'palette_policy':'Coherent32-row flesh palette; connected terrain groups retain one palette during fine scroll'};(out/'manifest.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':build()
