from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent))
from boss_motion_assets_r60 import ROOT,OUT as DIAG,PALETTE
from build_graphics import decode_roms,palette_ram
from decode_arcade_objects import render
from preview_enemy_sierra import convert
OUT=ROOT/'build/graphics/enemy_upgrades_r60'
def main():
 OUT.mkdir(parents=True,exist_ok=True);sprites,_=decode_roms();pal=palette_ram(ROOT/'build/fullgame/arcade_reference/frame007200_palette_sprite.bin')[64:80];records=[]
 for i,base in enumerate([832,848,864,880]):
  rgba=np.zeros((64,64,4),np.uint8)
  for half in range(2):
   for x in range(2):
    for y in range(4):
     tile=sprites[base+half*4+x*8+y];rgba[y*16:y*16+16,(half*2+x)*16:(half*2+x+1)*16,:3]=pal[tile];rgba[y*16:y*16+16,(half*2+x)*16:(half*2+x+1)*16,3]=np.where(tile,255,0)
  records.append((201+i,Image.fromarray(rgba),[40,40],dict(family='large walker',arcade_codes=[base,base+4],palette_frame=7200)))
 meta=json.loads((DIAG/'arcade_L1_objects.json').read_text())
 for ident,code,size in zip([21,22,23,24,25],[1570,1586,1602,1604,1604],[[32,24],[32,24],[32,24],[24,24],[24,24]]):
  row=next(r for r in meta if r['code']==code and r['colour']==4);_,objects=render(row['frame'],sprites);source=next(im for d,im in objects if d['code']==code and d['colour']==4);records.append((ident,source,size,dict(family='small walker',arcade_code=code,palette_frame=row['frame'])))
 gallery=Image.new('RGB',(900,((len(records)+5)//6)*260),'#111');draw=ImageDraw.Draw(gallery);result=[]
 for k,(ident,source,size,provenance)in enumerate(records):
  source.save(OUT/f'{ident}_arcade.png');scale=min(size[0]/source.width,size[1]/source.height);fit=source.resize((max(1,round(source.width*scale)),max(1,round(source.height*scale))),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',tuple(size));canvas.alpha_composite(fit,((size[0]-fit.width)//2,(size[1]-fit.height)//2));preview,bits,attrs=convert(canvas,tuple(size),np.ones((size[1],size[0]),bool),1.8,2.0,hsv=True);attrs&=63
  pixels=np.where(bits,np.repeat((attrs&7),8,axis=1),np.repeat((attrs>>3)&7,8,axis=1));preview=Image.fromarray(PALETTE[pixels].astype(np.uint8));preview.save(OUT/f'{ident}_ecm.png');np.save(OUT/f'{ident}.npy',pixels)
  x=k%6*150;y=k//6*260;draw.text((x+2,y+2),str(ident)+' '+provenance['family'],fill='white');s=source.copy();s.thumbnail((64,64),Image.Resampling.LANCZOS);gallery.paste(s,(x,y+22),s);im=preview.resize((size[0]*3,size[1]*3),Image.Resampling.NEAREST);gallery.paste(im,(x,y+100));result.append(dict(id=ident,size=size,colours=len(set(pixels.flatten())-{0}),**provenance))
 gallery.save(OUT/'comparison.png');(OUT/'manifest.json').write_text(json.dumps(result,indent=2));(OUT/'index.html').write_text('<meta charset="utf-8"><title>r60 arcade enemy upgrades</title><style>body{background:#111;color:white;font:18px system-ui}img{image-rendering:pixelated;max-width:100%}</style><h1>Four arcade walker poses and shaded small walkers</h1><p>Original ROM graphics above; native-size ECM conversion below. Scale before Sierra Lite, HSV saturation x2 and gamma1.8. Walkers retain40x40; small walkers retain their native32x24/24x24 cells with aspect-preserving fitting. This sheet is an asset preview, not gameplay or performance evidence.</p><img src="comparison.png">')
 print(result)
if __name__=='__main__':main()
