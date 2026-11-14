from pathlib import Path
import sys,numpy as np
from PIL import Image
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from decode_arcade_objects import render
O=R/'build/graphics/l2_actors_r67';O.mkdir(exist_ok=True)
def save(name,im):
 im.save(O/f'{name}_source.png');v=np.array(im);m=v[:,:,3]>=112;rgb=np.round(v[:,:,:3].astype(float)*v[:,:,3:4]/255).astype('uint8');rgb[~m]=0;(O/f'{name}.rgb').write_bytes(rgb.tobytes());(O/f'{name}.mask').write_bytes(m.astype('uint8').tobytes())
alpha=np.array(Image.open(R/'build/graphics/l2_organic_sierra/arcade_body.png').convert('RGBA'))[:,:,3]
for i,f in enumerate([17400,17700,18000,18300]):
 a=np.array(Image.open(R/f'build/fullgame/arcade_reference/frame{f:06d}.png').convert('RGB').crop((64,100,320,240)));mask=alpha.copy();blue=(a[:,:,2].astype(int)>a[:,:,0].astype(int)+25)&(a[:,:,2]>110);yy,xx=np.indices(blue.shape);blue&=(xx>=100)&(xx<155)&(yy>=8)&(yy<58);mask[blue]=255
 rgba=Image.fromarray(np.dstack([a,mask]),'RGBA').resize((190,104),Image.Resampling.LANCZOS);full=Image.new('RGBA',(192,104));full.alpha_composite(rgba,(1,0));save(f'M{i}',full.crop((88,8,120,32)))
_,rs=render(16800);heads={i:next(im for d,im in rs if d['code']==c)for i,c in[(3,2470),(4,2464)]};heads[5]=heads[4].transpose(Image.Transpose.FLIP_LEFT_RIGHT);heads[6]=heads[3].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
for i,im in heads.items():
 canvas=Image.new('RGBA',(40,40));canvas.alpha_composite(im,(4,4));save(f'H{i}',canvas)
