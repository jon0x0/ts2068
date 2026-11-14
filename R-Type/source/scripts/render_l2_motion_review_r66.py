from pathlib import Path
import numpy as np,json
from PIL import Image
O=Path('build/fullgame/startup_r66');G=Path('build/graphics/l2_geometry_review_r66');pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8);ims=[]
for r in json.loads((O/'L2_fine_approach.json').read_text())['fineShots']:
 b=(O/r['file']).read_bytes();im=np.zeros((192,256),np.uint8)
 for y in range(192):
  p=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(32):
   v=b[0x4000+p+x];a=b[0x6000+p+x];im[y,x*8:x*8+8]=[(a&7)if v&(128>>k)else(a>>3)&7 for k in range(8)]
 ims.append(Image.fromarray(pal[im]).resize((512,384),Image.Resampling.NEAREST))
ims[0].save(G/'normal_boss_arrival.gif',save_all=True,append_images=ims[1:],duration=180,loop=0)
p=G/'index.html';s=p.read_text();s+='<h2>Normal L2 boss arrival</h2><p>Actual emulator snapshots at the end of 32 consecutive world updates. Lower-body bands move1pixel per update. This does not capture intermediate writes during each update and is not physical-hardware evidence.</p><img src="normal_boss_arrival.gif">';p.write_text(s)
