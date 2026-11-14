from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'scripts'))
from build_graphics import PALETTE
b=bytes(0x4000)+(r/'build/native/snapshot.bin').read_bytes();patch=(r/'build/art_assets/terrain_patches.bin').read_bytes();pal=(r/'build/art_assets/terrain_palette.bin').read_bytes()
tiles=[];attrs=[];oldattrs=[]
for t in range(22):
 pix=np.zeros((32,32),dtype='uint8');col=pix.copy();old=pix.copy()
 for cy in range(4):
  for cx in range(4):
   p=t*144+(cy*4+cx)*9;a=patch[p];pix[cy*8:cy*8+8,cx*8:cx*8+8]=np.unpackbits(np.frombuffer(patch[p+1:p+9],dtype='uint8')).reshape(8,8)
   ca=np.array([pal[(a&127)*8+y] if a&128 else a&127 for y in range(8)])
   oa=np.array([pal[(a&119)*8+y] if a&128 else a&127 for y in range(8)])
   col[cy*8:cy*8+8,cx*8:cx*8+8]=ca[:,None];old[cy*8:cy*8+8,cx*8:cx*8+8]=oa[:,None]
 tiles.append(pix);attrs.append(col);oldattrs.append(old)
end=int.from_bytes(b[0xc4bc:0xc4be],'little');stop=int.from_bytes(b[0xc4be:0xc4c0],'little');world=b[end:stop];columns=len(world)//5;checked=0;introduced=0
for row in range(5):
 strips=[[],[],[]]
 for c in range(columns):
  code=world[c*5+row];t=code&63
  planes=[tiles[t],attrs[t],oldattrs[t]] if t<22 else [np.zeros((32,32),dtype='uint8')]*3
  for k,plane in enumerate(planes):
   if code&64:plane=plane[:,::-1]
   if code&128:plane=plane[::-1]
   strips[k].append(plane)
 pix,col,old=[np.concatenate(p,axis=1) for p in strips]
 for phase in range(8):
  width=(pix.shape[1]-phase)//8*8;mask=pix[:,phase:phase+width].reshape(32,-1,8)>0
  def clash(a):
   a=a[:,phase:phase+width].reshape(32,-1,8)
   return np.where(mask,a,0).max(2)>np.where(mask,a,255).min(2)
  introduced+=int(np.count_nonzero(clash(col)&~clash(old)));checked+=int(mask.any(2).sum())
assert introduced==0,introduced
out=r/'build/diagnostics/terrain_islands_r20';out.mkdir(parents=True,exist_ok=True)
sheet=Image.new('RGB',(768,640));draw=ImageDraw.Draw(sheet)
for t,(pix,col) in enumerate(zip(tiles,attrs)):
 ink=(col&7)+np.where(col&64,8,0);paper=((col>>3)&7)+np.where(col&64,8,0);rgb=PALETTE[np.where(pix,ink,paper)]
 im=Image.fromarray(rgb.astype('uint8')).resize((128,128),Image.Resampling.NEAREST);x=t%6*128;y=t//6*160;sheet.paste(im,(x,y+20));draw.text((x+3,y+3),f'Tile {t}',fill='white')
sheet.save(out/'terrain_atlas.png')
report=dict(passed=True,scroll_phases=8,map_columns=columns,occupied_cells_checked=checked,introduced_colour_conflicts=introduced,offline_only=True)
(out/'validation.json').write_text(json.dumps(report,indent=2));print(report)
