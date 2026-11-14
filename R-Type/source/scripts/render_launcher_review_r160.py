from pathlib import Path
from PIL import Image,ImageDraw
import json
O=Path('build/launcher_review_r160');sheet=Image.new('RGB',(624,440),'#181818');d=ImageDraw.Draw(sheet)
for row,kind in enumerate(['before','after']):
 j=json.loads((O/kind/'launcher_live.json').read_text())
 for col,u in enumerate([28,34,43]):
  sample=next(s for s in j['screens']if s['updates']==u);r=next(r for r in j['records']if r['updates']==u and r['hl']>=0xc5de);b=(O/kind/sample['name']).read_bytes();im=Image.new('RGB',(256,192));ip=im.load()
  for y in range(192):
   for x in range(256):
    at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3);a=b[6144+at];c=(a&7)if b[at]&(128>>(x&7))else(a>>3&7);v=255 if a&64 else 205;ip[x,y]=(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
  x=max(0,min(208,r['x']*8-8));y=max(0,min(144,r['y']*8-8));sheet.paste(im.crop((x,y,x+48,y+48)).resize((192,192),Image.Resampling.NEAREST),(col*208,row*220+24));d.text((col*208+2,row*220+4),f'{kind}: pose {r["id"]}, update {u}',fill='white')
sheet.save(O/'launcher_before_after.png')
