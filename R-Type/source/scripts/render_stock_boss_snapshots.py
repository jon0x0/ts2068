from pathlib import Path
import json
from PIL import Image,ImageDraw
O=Path('build/cartridges/integration_work');sheet=Image.new('RGB',(1024,424),(18,22,30));dr=ImageDraw.Draw(sheet)
def off(y):return((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def rgb(c,bright):v=255 if bright else 205;return(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
for n in range(1,9):
 p=O/f'level{n:02d}'/'boss_runtime.screen.bin'
 if not p.exists():continue
 b=p.read_bytes();im=Image.new('RGB',(256,192));px=im.load()
 for y in range(192):
  for x in range(256):
   a=off(y)+(x>>3);v=b[a];at=b[6144+a];c=at&7 if v&(128>>(x&7))else at>>3&7;px[x,y]=rgb(c,at&64)
 im.save(p.with_suffix('.png'));x=((n-1)%4)*256;y=((n-1)//4)*212;dr.text((x+5,y+4),f'Level {n} - ECM memory snapshot',fill='white');sheet.paste(im,(x,y+20))
sheet.resize((2048,848),Image.Resampling.NEAREST).save(O/'boss_contact_sheet.png')
