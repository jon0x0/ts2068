from pathlib import Path
import sys,json
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from decode_arcade_objects import render;from build_graphics import decode_roms
O=R/'build/graphics/l4_snake_converter';O.mkdir(exist_ok=True);sp,_=decode_roms();found={}
for fr in range(30000,42001,300):
 if not (R/f'build/fullgame/arcade_reference/frame{fr:06d}_sprites.bin').exists():continue
 _,objs=render(fr,sp)
 for desc,im in objs:
  if desc['width']>64 or desc['height']>64 or not im.getbbox():continue
  key=(desc['code'],desc['colour'],desc['width'],desc['height'])
  if key not in found:found[key]=(fr,desc,im)
items=list(found.values());sheet=Image.new('RGB',(1200,((len(items)+9)//10)*140),(18,22,28));d=ImageDraw.Draw(sheet)
for k,(fr,desc,im)in enumerate(items):
 x=k%10*120;y=k//10*140;d.text((x+3,y+3),f'{desc["code"]} p{desc["colour"]}',fill='white');d.text((x+3,y+17),str(fr),fill='white');a=im.copy();a.thumbnail((112,100));a=a.resize((min(112,a.width*2),min(100,a.height*2)),Image.Resampling.NEAREST);sheet.paste(a,(x+3,y+34),a);im.save(O/f'candidate_{desc["code"]}_p{desc["colour"]}_{fr}.png')
sheet.save(O/'arcade_candidates.png');(O/'arcade_inventory.json').write_text(json.dumps([dict(frame=fr,**de)for fr,de,im in items],indent=2));print(len(items))
