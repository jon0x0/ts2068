from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path.cwd();O=R/'build/graphics/plume_diameter_r103';O.mkdir(exist_ok=True);profiles=[]
for k in range(4):
 im=Image.open(R/f'build/graphics/walker_runtime_r86/L3_exhaust_{k}_source.png').convert('RGBA');a=np.array(im);v=a.copy();valid=[x for x in range(40)if (a[:,x,3]>=112).any()]
 for x in range(6,40):
  sx=min(valid,key=lambda q:abs(q-x));ys=np.flatnonzero(a[:,sx,3]>=112);lo,hi=int(ys[0]),int(ys[-1])+1;original=hi-lo;amount=min(1,(x-6)/18);height=max(original,round(original+(16-original)*amount));top=(16-height)//2
  strip=Image.fromarray(a[lo:hi,sx:sx+1]).resize((1,height),Image.Resampling.LANCZOS);v[:,x]=0;v[top:top+height,x]=np.array(strip)[:,0]
 # The full16px nozzle mouth is retained; columns nearest it now share its diameter.
 name=f'L3_exhaust_{k}';Image.fromarray(v).save(O/f'{name}_source.png');mask=(v[:,:,3]>=112)&(v[:,:,:3].max(2)>0);rgb=v[:,:,:3].copy();rgb[~mask]=0;(O/f'{name}.rgb').write_bytes(rgb.tobytes());(O/f'{name}.mask').write_bytes(mask.astype('uint8').tobytes());profiles.append(dict(id=name,size=name,w=48,h=16,bright=True,strategy='segment-coverage',settings=dict(brightness=56,contrast=54,saturation=78,gamma=1.65)))
(O/'inputs.json').write_text(json.dumps(dict(profiles=profiles),indent=2));s=(R/'scripts/convert_walkers_rpc_r85.mjs').read_text().replace('build/graphics/walker_review_r85','build/graphics/plume_diameter_r103');(R/'scripts/convert_plume_diameter_r103.mjs').write_text(s)
