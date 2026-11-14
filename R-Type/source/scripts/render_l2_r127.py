from pathlib import Path
import numpy as np
from PIL import Image
O=Path('build/fullgame/l2_roles_restore_r127');pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)],np.uint8)
for p in list(O.glob('boss_probe_*.home.bin'))+list(O.glob('boss_ceasefire_*.home.bin'))+list(O.glob('ordinary_L2_col*.home.bin'))+list(O.glob('firing_*.home.bin')):
 b=p.read_bytes();im=np.zeros((192,256),np.uint8)
 for y in range(192):
  a=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(32):
   t=b[0x6000+a+x];v=b[0x4000+a+x]
   for k in range(8):im[y,x*8+k]=((t&7)if v&(128>>k)else(t>>3)&7)+(8 if t&64 else 0)
 Image.fromarray(pal[im]).resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'))
