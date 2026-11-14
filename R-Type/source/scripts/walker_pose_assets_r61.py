"""Correct arcade walk and raise poses at native TS2068 sizes."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'scripts');from build_graphics import decode_roms,palette_ram
from boss_motion_assets_r60 import PALETTE,decode
from preview_enemy_sierra import convert
out=Path('build/graphics/small_walker_comparison');sprites,_=decode_roms();pal=palette_ram(Path('build/fullgame/arcade_reference/frame004200_palette_sprite.bin'))[64:80];records=[]
for i,code,size in zip(range(21,26),[1570,1572,1574,1600,1602],[(32,24)]*3+[(24,24)]*2):
 a=np.block([[sprites[code],sprites[code+8]],[sprites[code+1],sprites[code+9]]]);rgba=np.concatenate([pal[a],np.where(a[:,:,None],255,0)],axis=2).astype(np.uint8);im=Image.fromarray(rgba);bbox=(0,7,32,32) if i<24 else im.getbbox();im=im.crop(bbox);scale=min(size[0]/im.width,size[1]/im.height);fit=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',size);canvas.alpha_composite(fit,((size[0]-fit.width)//2,size[1]-fit.height));_,bits,attrs=convert(canvas,size,np.ones((size[1],size[0]),bool),1.8,2,hsv=True);attrs&=63;pixels=np.where(bits,np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1));assert all(len(set(row[x:x+8]))<=2 for row in pixels for x in range(0,size[0],8));np.save(out/f'{i}_proposed.npy',pixels);Image.fromarray(PALETTE[pixels].astype(np.uint8)).save(out/f'{i}_proposed.png');records.append(dict(id=i,arcade_code=code,source_crop=bbox,target=size,pose='walking'if i<24 else'raising gun',asset_preview_only=True))
frames=[]
for i in [21,22,23,22]:frames.append(Image.open(out/f'{i}_proposed.png').resize((256,192),Image.Resampling.NEAREST))
frames[0].save(out/'proposed_walk.gif',save_all=True,append_images=frames[1:],duration=360,loop=0,disposal=2)
(out/'proposed_manifest.json').write_text(json.dumps(records,indent=2))
