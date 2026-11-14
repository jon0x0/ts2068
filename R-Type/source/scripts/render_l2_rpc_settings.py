from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/graphics/l2_rpc_settings';m=json.loads((O/'manifest.json').read_text());sheet=Image.new('RGB',(1000,690),(16,16,16));dr=ImageDraw.Draw(sheet)
for j,p in enumerate(m['profiles']):
 w,h=p['w'],p['h'];a=np.frombuffer((O/f'{p["id"]}.rgb').read_bytes(),np.uint8).reshape(h,w,3);im=Image.fromarray(a);im.save(O/f'{p["id"]}.png');x=j%2*500;y=j//2*345;dr.text((x+8,y+8),f'{p["id"]}: {p["name"]}',fill='white');dr.text((x+8,y+24),f'{w}x{h} / {p["strategy"]}',fill='white');im=im.resize((w*3,h*3),Image.Resampling.NEAREST);im.thumbnail((490,300),Image.Resampling.NEAREST);sheet.paste(im,(x+5,y+42))
sheet.save(O/'comparison.png')
