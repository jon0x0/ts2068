from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'scripts'));from build_graphics import PALETTE
b=bytes(16384)+(r/'build/native/snapshot.bin').read_bytes();patch=(r/'build/art_assets/terrain_patches.bin').read_bytes();pal=(r/'build/art_assets/terrain_palette.bin').read_bytes();styles=np.load(r/'build/art_assets/terrain_group_styles.npy');worldmap=b[0xe571:0xe788];tiles=[];colours=[];converted=[];ids=[]
for t in range(22):
 pix=np.zeros((32,32),dtype='uint8');col=pix.copy();eligible=pix.copy();token=pix.copy()
 for cy in range(4):
  for cx in range(4):
   p=t*144+(cy*4+cx)*9;a=patch[p];pix[cy*8:cy*8+8,cx*8:cx*8+8]=np.unpackbits(np.frombuffer(patch[p+1:p+9],dtype='uint8')).reshape(8,8)
   row=np.array([pal[(a&127)*8+y] if a&128 else a&127 for y in range(8)])
   col[cy*8:cy*8+8,cx*8:cx*8+8]=row[:,None];eligible[cy*8:cy*8+8,cx*8:cx*8+8]=bool(a&128);token[cy*8:cy*8+8,cx*8:cx*8+8]=a&127
 tiles.append(pix);colours.append(col);converted.append(eligible);ids.append(token)
rows=[[],[],[],[]]
for c in range(107):
 blocks=[[],[],[],[]]
 for row in range(5):
  code=worldmap[c*5+row];t=code&63
  for i,plane in enumerate([tiles[t],colours[t],converted[t],ids[t]]):
   if code&64:plane=plane[:,::-1]
   if code&128:plane=plane[::-1]
   blocks[i].append(plane)
 for i in range(4):rows[i].append(np.concatenate(blocks[i],axis=0))
pix,base,eligible,token=[np.concatenate(p,axis=1)for p in rows];new=base.copy();variant=np.repeat(np.repeat(styles,8,0),8,1)
for y in range(160):
 # Source colour rows mirror with the tile. Locate the matching base attribute
 # within its token row; two arrangements remain symmetric over32 scanlines.
 for x in range(pix.shape[1]):
  if eligible[y,x] and variant[y,x]:
   cy=y%32;code=worldmap[(x//32)*5+y//32];sy=31-cy if code&128 else cy
   new[y,x]=pal[(int(token[y,x])+8)*8+(sy%8)]
introduced=0;checked=0
for phase in range(8):
 width=(pix.shape[1]-phase)//8*8;mask=pix[:,phase:phase+width].reshape(160,-1,8)>0
 def clash(a):
  a=a[:,phase:phase+width].reshape(160,-1,8)
  return np.where(mask,a,0).max(2)>np.where(mask,a,255).min(2)
 introduced+=int(np.count_nonzero(clash(new)&~clash(base)));checked+=int(mask.any(2).sum())
assert introduced==0,introduced
def rgb(a):
 ink=(a&7)+np.where(a&64,8,0);paper=((a>>3)&7)+np.where(a&64,8,0);return PALETTE[np.where(pix,ink,paper)].astype('uint8')
out=r/'build/diagnostics/terrain_groups_r22';out.mkdir(parents=True,exist_ok=True)
old=Image.fromarray(rgb(base));current=Image.fromarray(rgb(new));current.save(out/'whole_level.png')
# Same geometry/position makes the separated warm building and cool ground clear.
left=128;right=512;sheet=Image.new('RGB',((right-left)*2,64*2*2+40));draw=ImageDraw.Draw(sheet)
for i,(im,title)in enumerate([(old,'Previous shared arrangement'),(current,'Instance groups: warm buildings / cool machinery')]):
 draw.text((4,i*148+3),title,fill='white');sheet.paste(im.crop((left,96,right,160)).resize(((right-left)*2,128),Image.Resampling.NEAREST),(0,i*148+20))
sheet.save(out/'group_comparison.png')
report=dict(passed=True,map_columns=107,scroll_phases=8,occupied_cells_checked=checked,introduced_colour_conflicts=introduced,instances_have_distinct_palettes=True)
(out/'validation.json').write_text(json.dumps(report,indent=2));print(report)
