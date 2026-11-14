from pathlib import Path
import json,sys,numpy as np
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l1_walker_snake_r105';profiles=[];sheet=Image.open(R/'build/graphics/walker_review_r85/ai_round_sheet.png').convert('RGBA');slots=[];boxes=[]
for k in range(4):
 a=np.array(sheet.crop((k*sheet.width//4,0,(k+1)*sheet.width//4,sheet.height)));mask=(a[:,:,3]>112)&(a[:,:,:3].max(2)>35);ys,xs=np.where(mask);boxes.append((xs.min(),ys.min(),xs.max()+1,ys.max()+1));a[:,:,3]=mask*255;slots.append(Image.fromarray(a))
box=(min(v[0]for v in boxes),min(v[1]for v in boxes),max(v[2]for v in boxes),max(v[3]for v in boxes))
def add(name,im,size,settings):
 im=im.convert('RGBA');im.thumbnail(size,Image.Resampling.LANCZOS);can=Image.new('RGBA',size);can.alpha_composite(im,((size[0]-im.width)//2,size[1]-im.height));a=np.array(can);mask=(a[:,:,3]>=112)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;can.save(O/f'{name}_source.png');(O/f'{name}.rgb').write_bytes(rgb.tobytes());(O/f'{name}.mask').write_bytes(mask.astype('uint8').tobytes());profiles.append(dict(id=name,size=name,w=size[0],h=size[1],bright=True,strategy='segment-coverage',settings=settings))
for k in range(4):
 a=np.array(slots[k].crop(box));rgb=a[:,:,:3].astype(float);lum=rgb.mean(2);blue=(rgb[:,:,2]>rgb[:,:,0]*1.08)&(rgb[:,:,2]>rgb[:,:,1]*1.03)&(a[:,:,3]>0);rgb[blue& (lum<90)]=np.array([24,85,155]);a[:,:,:3]=rgb.clip(0,255).astype('uint8');add(f'metal24_{k}',Image.fromarray(a),(24,24),dict(brightness=56,contrast=54,saturation=78,gamma=1.65))
 # Two real walking cels plus explicitly authored one-pixel leg intermediates.
 im=Image.open(O/f'walker_arcade_{k%2}.png').convert('RGBA');a=np.array(im)
 if k>=2:
  old=a[23:].copy();a[23:]=0;delta=1 if k==2 else -1
  for x in range(32):
   dx=x+delta if x<16 else x-delta
   if 0<=dx<32:a[23:,dx]=old[:,x]
 for size in [24,32]:add(f'arcade{size}_{k}',Image.fromarray(a),(size,size),dict(brightness=52,contrast=54,saturation=65,gamma=1.5))
# Decode actual installed r104 frames, not an old preview.
B=R/'build/fullgame/full_plume_r104';meta=next(v for v in json.loads((B/'walker_runtime.json').read_text())if v['level']==1);raw=(B/'L1_runtime_art.bin').read_bytes();base=meta['assets'][0]['pointer'];pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8);bounds=[]
for item in meta['assets']:
 if item['key']!='round':continue
 off=item['pointer']-base;v=raw[off:off+item['bytes']];idx=np.zeros((24,24),np.uint8)
 for x in range(3):
  for y in range(24):
   bt,t=v[(x*24+y)*2:(x*24+y)*2+2]
   for bit in range(8):idx[y,x*8+bit]=(t&7)if bt&(128>>bit)else(t>>3)&7
 Image.fromarray(pal[idx]).save(O/f'current_{item["frame"]}.png');y,x=np.where(idx>0);bounds.append(dict(frame=item['frame'],visible=[int(x.max()-x.min()+1),int(y.max()-y.min()+1)]))
(O/'inputs.json').write_text(json.dumps(dict(profiles=profiles,old_visible=bounds,source_crop=list(map(int,box))),indent=2));s=(R/'scripts/convert_walkers_rpc_r85.mjs').read_text().replace('build/graphics/walker_review_r85','build/graphics/l1_walker_snake_r105');(R/'scripts/convert_l1_walker_r105.mjs').write_text(s)
print('Prepared three alternatives, same family settings per four-frame cycle. Actual bounds:',bounds)
