from pathlib import Path
from PIL import Image
import numpy as np
O=Path('build/fullgame/startup_r66');p=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)],np.uint8)
for f in O.glob('queue_L*.home.bin'):
 b=f.read_bytes();a=np.zeros((192,256),np.uint8)
 for y in range(192):
  off=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(32):
   at=b[0x5800+(y//8)*32+x];bits=b[0x4000+off+x];a[y,x*8:x*8+8]=[(at&7)+(8 if at&64 else 0)if bits&(128>>k)else((at>>3)&7)+(8 if at&64 else 0)for k in range(8)]
 Image.fromarray(p[a]).resize((768,576),Image.Resampling.NEAREST).save(f.with_name(f.name.replace('.home.bin','.png')))
