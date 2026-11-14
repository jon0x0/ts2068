from pathlib import Path
from PIL import Image
import shutil,json,numpy as np
R=Path.cwd();O=R/'build/graphics/walker_review_r85';G=Path('C:/Users/Jon/.codex/generated_images/01a19855-5e8b-7c01-9834-206ac0fda11a')
for name,file in [('ai_round_sheet.png','exec-aafba3f2-be99-455b-a17c-1fef61043f5c.png'),('ai_yellow_source.png','exec-1c5ef6da-d807-459d-9555-99689b438128.png')]:shutil.copy2(G/file,O/name)
m=json.loads((O/'inputs.json').read_text());sheet=Image.open(O/'ai_round_sheet.png').convert('RGBA');poses=[]
for k in range(4):
 im=sheet.crop((k*sheet.width//4,0,(k+1)*sheet.width//4,sheet.height));a=np.array(im);box=Image.fromarray((a[:,:,3]>128).astype('uint8')*255).getbbox();poses.append(im.crop(box))
yellow=Image.open(O/'ai_yellow_source.png').convert('RGBA');yellow=yellow.crop(yellow.getbbox())
for r in m['records']:
 if r['kind']not in['round','yellow']:continue
 r['has_ai_proposal']=True
 for k,f in enumerate(r['frames']):
  w,h=f['size'];im=yellow.copy()if r['kind']=='yellow'else poses[k%4].copy();ratio=min(w/im.width,h/im.height);im=im.resize((max(1,round(im.width*ratio)),max(1,round(im.height*ratio))),Image.Resampling.LANCZOS);can=Image.new('RGBA',(w,h));can.alpha_composite(im,((w-im.width)//2,h-im.height));a=np.array(can);mask=(a[:,:,3]>=112)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;key=f['key']+'_C';can.save(O/f'{key}_input.png');(O/f'{key}.rgb').write_bytes(rgb.tobytes());(O/f'{key}.mask').write_bytes(mask.astype('uint8').tobytes());m['profiles'].append(dict(id=key,size=key,w=w,h=h,bright=True,strategy='segment-coverage',settings=dict(brightness=56,contrast=54,saturation=78,gamma=1.65)))
(O/'inputs.json').write_text(json.dumps(m,indent=2));print(len(m['profiles']),'profiles including AI proposals')
