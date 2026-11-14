from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from decode_arcade_objects import render;from build_graphics import decode_roms
O=R/'build/graphics/l1_ghost_converter';O.mkdir(exist_ok=True);sp,_=decode_roms();found={}
for fr in range(1200,8101,300):
 _,objects=render(fr,sp)
 for desc,im in objects:
  if desc['width']>64 or desc['height']>64 or not im.getbbox():continue
  key=(desc['code'],desc['colour'],desc['width'],desc['height'])
  if key not in found:found[key]=(fr,desc,im)
items=list(found.values());sheet=Image.new('RGB',(1000,((len(items)+9)//10)*115),(20,25,30));d=ImageDraw.Draw(sheet)
for i,(fr,desc,im)in enumerate(items):
 x=i%10*100;y=i//10*115;d.text((x,y),f'{desc["code"]} p{desc["colour"]}',fill='white');a=im.copy();a.thumbnail((90,85));a=a.resize((min(90,a.width*2),min(85,a.height*2)),Image.Resampling.NEAREST);sheet.paste(a,(x,y+20),a)
sheet.save(O/'arcade_identity_contact.png');(O/'arcade_inventory.json').write_text(json.dumps([dict(frame=fr,**desc)for fr,desc,im in items],indent=2));print('Unique objects',len(items));print([(fr,de)for fr,de,im in items if fr==6900])
