from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_graphics import decode_roms
from decode_arcade_objects import render
from boss_motion_assets_r60 import decode,PALETTE
from preview_enemy_sierra import convert
OUT=ROOT/'build/graphics/l6_remaining_r62';OUT.mkdir(exist_ok=True,parents=True)
sp,_=decode_roms();objects=[]
for frame in range(47100,54001,300):
 for d,im in render(frame,sp)[1]:objects.append((frame,d,im))
records=[];sheet=Image.new('RGB',(800,13*140),(18,18,18));draw=ImageDraw.Draw(sheet)
for i,ident in enumerate(range(5,18)):
 code=([2758,2768,2772,2774][ident-5]if ident<=8 else [2850,2852,2854,2864,2850][ident-9]if ident<=13 else [324,340,336,324][ident-14])
 frame,d,source=next(v for v in objects if v[1]['code']==code);current=decode(6,ident)[0];h,w=current.shape
 source=source.crop(source.getbbox());scale=min(w/source.width,h/source.height);fitted=source.resize((max(1,round(source.width*scale)),max(1,round(source.height*scale))),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(w,h));canvas.alpha_composite(fitted,((w-fitted.width)//2,h-fitted.height))
 source.save(OUT/f'L6_{ident}_arcade.png');images=[source,Image.fromarray(PALETTE[current].astype('uint8'))]
 for label,gamma in [('A',1.8),('B',2.4)]:
  im,bits,attrs=convert(canvas,(w,h),np.ones((h,w),bool),gamma,2,hsv=True);attrs&=63;pixels=np.where(bits,np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1));im=Image.fromarray(PALETTE[pixels].astype('uint8'));im.save(OUT/f'L6_{ident}_{label}.png');np.save(OUT/f'L6_{ident}_{label}.npy',pixels);images.append(im)
 for j,im in enumerate(images):
  x=j*200;y=i*140;draw.text((x+4,y+3),f'L6 #{ident} '+['ARCADE','CURRENT','A HSV/GAMMA1.8','B HSV/GAMMA2.4'][j],fill='white');im=im.copy();im.thumbnail((180,100),Image.Resampling.NEAREST);factor=max(1,min(3,180//im.width,100//im.height));im=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST);sheet.paste(im.convert('RGB'),(x+4,y+25))
 records.append({'id':ident,'arcade_code':code,'capture_frame':frame,'palette':d['colour'],'size':[w,h],'mapping_status':'visual analogue proposal; user review required','arcade_alpha_crop':True})
sheet.save(OUT/'alternatives.png');(OUT/'manifest.json').write_text(json.dumps({'asset_preview_only':True,'records':records,'geometry':'Aspect fit before Sierra Lite; original runtime dimensions; no playable assets changed'},indent=2));(OUT/'index.html').write_text('<meta charset=utf-8><title>Level 6 minor enemy alternatives</title><style>body{background:#151515;color:white;font:17px system-ui}img{max-width:100%;image-rendering:pixelated}</style><h1>Level 6: remaining minor enemies</h1><p>Original arcade object, current game, A HSV/gamma 1.8, B gamma 2.4. Aspect fit at native sizes before Sierra Lite. These are proposals, not installed game graphics; arcade-to-native pose mappings need review.</p><img src=alternatives.png>')
