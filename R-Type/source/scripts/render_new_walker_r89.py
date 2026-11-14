from pathlib import Path
from PIL import Image,ImageDraw
import json
O=Path('build/graphics/walker_selection_r89');variants=json.loads((O/'replacement_variants.json').read_text());can=Image.new('RGB',(1000,570),(16,22,28));d=ImageDraw.Draw(can)
for row,v in enumerate(variants):
 d.text((8,row*190+5),v['id']+' '+v['label'],fill='white')
 for k,p in enumerate(v['profiles']):
  w,h=p['w'],p['h'];im=Image.frombytes('RGB',(w,h),(O/(p['id']+'.rgb')).read_bytes());im.save(O/(p['id']+'.png'));can.paste(im.resize((w*4,h*4),Image.Resampling.NEAREST),(k*165+5,row*190+30))
can.save(O/'new_walker_options.png')
