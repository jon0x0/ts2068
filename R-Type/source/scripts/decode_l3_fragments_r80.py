from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/diagnostics/l3_fragments_r80';b=(R/'build/fullgame/world_reset_r79/level03_region.bin').read_bytes();m=bytes(0xc000)+b[0xa000:0xe000];l=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][2];pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)],np.uint8);sheet=Image.new('RGB',(1200,((l['enemy_descriptors']+9)//10)*100),(20,24,30));d=ImageDraw.Draw(sheet)
for i in range(1,l['enemy_descriptors']+1):
 at=l['enemy_descriptors_start']+(i-1)*4;w,h=m[at:at+2]
 if not w or not h:continue
 p=int.from_bytes(m[at+2:at+4],'little');out=np.zeros((h*8,w*8),np.uint8)
 for cy in range(h):
  for cx in range(w):
   tag=m[p];p+=1
   if tag==54:continue
   for y in range(8):
    a=b[0x2000+(tag&127)*8+y];bank=8 if a&64 else 0
    for x in range(8):out[cy*8+y,cx*8+x]=((a&7)if m[p+y]&(128>>x)else(a>>3)&7)+bank
   p+=8
 im=Image.fromarray(pal[out]);im.save(O/f'native_{i:03d}.png');im.thumbnail((112,78),Image.Resampling.NEAREST);x=((i-1)%10)*120;y=((i-1)//10)*100;sheet.paste(im,(x,y+18));d.text((x,y),str(i)+' '+str(w*8)+'x'+str(h*8),fill='white')
sheet.save(O/'native_contact.png');print(l['enemy_descriptors'])
