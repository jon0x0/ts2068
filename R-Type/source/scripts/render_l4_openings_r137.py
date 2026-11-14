from pathlib import Path
import sys,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent));from build_graphics import unpack,screen_offset,PALETTE
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];p=R/'build/fullgame/l4_openings_r137';sheet=Image.new('RGB',(1024,832),'#141a23');d=ImageDraw.Draw(sheet)
for k,n in enumerate([120,200]):
 b=(p/f'Spectrum_L4_{n}.home.bin').read_bytes();a=np.zeros((192,256),np.uint8)
 for y in range(192):
  for x in range(32):
   bits=b[0x4000+screen_offset(y)+x];at=b[0x5800+(y//8)*32+x];br=(at>>6&1)*8;a[y,x*8:x*8+8]=[(at&7)+br if bits&(128>>z)else((at>>3)&7)+br for z in range(8)]
 native=Image.fromarray(PALETTE[a].astype('uint8'));native.save(p/f'Spectrum_L4_{n}.png');b=(p/f'L4_openings_{n}.home.bin').read_bytes();cur=unpack(b[0x4000:0x5800],b[0x6000:0x7800]);cur.save(p/f'L4_openings_{n}.png')
 for j,im in enumerate([native,cur]):
  sheet.paste(im.resize((512,384),Image.Resampling.NEAREST),(j*512,k*416+26));d.text((j*512+8,k*416+8),['Original Spectrum animation','Repaired ECM animation'][j]+f' - update{n}',fill='white')
sheet.save(p/'Spectrum_ECM_animation_comparison.png')
# Collision-owned target cells from the actual open-stage snapshot, not estimated boxes.
b=(p/'L4_openings_200.home.bin').read_bytes();im=unpack(b[0x4000:0x5800],b[0x6000:0x7800]);im=im.resize((1024,768),Image.Resampling.NEAREST);out=Image.new('RGB',(1024,828),'#151b25');out.paste(im,(0,28));draw=ImageDraw.Draw(out);grid=(p/'L4_openings_200.grid.bin').read_bytes();draw.text((16,8),'Restored openings - actual ECM gameplay, update200',fill='white')
for i,o in enumerate([132,135,138]):
 cells=[(k%32,k//32)for k,v in enumerate(grid)if v==o]
 if not cells:continue
 x0=min(x for x,y in cells)*32;y0=min(y for x,y in cells)*32+28;x1=(max(x for x,y in cells)+1)*32;y1=(max(y for x,y in cells)+1)*32+28;col=['#ffff00','#00ffff','#ff80ff'][i];draw.rectangle((x0,y0,x1-1,y1-1),outline=col,width=2);draw.text((x0,y0-13),str(i+1),fill=col)
draw.text((16,806),'1 front   2 middle   3 rear. Hull movement exposes and covers the openings.',fill='white');out.save(p/'targets_open_annotated.png')
