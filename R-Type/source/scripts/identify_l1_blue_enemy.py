from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from decode_arcade_objects import render;from build_graphics import decode_roms,palette_ram,sprite_image;import walker_review_r85 as n
n.B=R/'build/fullgame/l1_ghost_r114';O=R/'build/graphics/l1_blue_enemy_converter';O.mkdir(exist_ok=True);sp,_=decode_roms();items=[('Current L1 native41',n.current(1,41)[0].convert('RGBA'))];records=[]
for fr,code,pa in [(2400,246,6),(2700,246,11),(3900,246,2),(3000,256,11),(3300,258,7)]:
 _,ob=render(fr,sp);de,im=next((de,im)for de,im in ob if de['code']==code and de['colour']==pa);items.append((f'{code}p{pa} / f{fr}',im));records.append(dict(frame=fr,**de,pixelSHA=hashlib.sha256(im.tobytes()).hexdigest()));im.save(O/f'arcade_{code}_p{pa}.png')
pal=palette_ram(R/'build/fullgame/arcade_reference/frame003300_palette_sprite.bin')[7*16:8*16]
for code in [260,262]:
 im,_=sprite_image(sp,code,pal,2,2);items.append((f'{code}p7 ROM / boost pose',im));im.save(O/f'arcade_{code}_p7.png')
sheet=Image.new('RGB',(1000,440),(20,25,30));d=ImageDraw.Draw(sheet)
for i,(label,im)in enumerate(items):
 x=i%4*250;y=i//4*220;d.text((x+5,y+5),label,fill='white');im=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST);sheet.paste(im,(x+8,y+35),im)
sheet.save(O/'source_candidates.png');(O/'source_candidates.json').write_text(json.dumps(records,indent=2));print([(r['code'],r['colour'],r['pixelSHA'][:12])for r in records])
