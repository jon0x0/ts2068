from pathlib import Path
import json,shutil
from PIL import Image
import numpy as np
R=Path.cwd();O=R/'build/graphics/l2_rpc_settings';O.mkdir(exist_ok=True)
for name,src in [('rpc_reference.png','codex-clipboard-23baba77-713f-4191-a9a0-a952382be04d.png'),('rpc_settings.png','codex-clipboard-722820c4-274a-4c6b-a9fe-8d20d3e938bb.png')]:shutil.copy2(Path('C:/Users/Jon/AppData/Local/Temp')/src,O/name)
body=Image.open(R/'build/graphics/l2_organic_sierra/arcade_body.png').convert('RGBA')
for name,w,h in [('native',160,88),('larger',192,104)]:
 im=body.copy();im.thumbnail((w,h),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(w,h));canvas.alpha_composite(im,((w-im.width)//2,h-im.height));canvas.save(O/f'{name}_source.png');a=np.array(canvas);mask=a[:,:,3]>=112;rgb=np.round(a[:,:,:3].astype(float)*(a[:,:,3:4].astype(float)/255)).astype('uint8');rgb[~mask]=0;(O/f'{name}.rgb').write_bytes(rgb.tobytes());(O/f'{name}.mask').write_bytes(mask.astype('uint8').tobytes())
shutil.copy2(R/'../../retropixel/LICENSE',O/'RPC_LICENSE.txt')
print(O)
