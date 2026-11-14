from pathlib import Path
import numpy as np
from PIL import Image
R=Path.cwd();O=R/'build/fullgame/native_fit_r64';pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],dtype=np.uint8)
for p in list(O.glob('L6_id*.home.bin'))+list(O.glob('L7_id*.home.bin'))+list(O.glob('ordinary_L3_*.home.bin')):
 b=p.read_bytes();a=np.zeros((192,256),np.uint8)
 for y in range(192):
  at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(32):
   attr=b[0x6000+at+x];bits=b[0x4000+at+x]
   for k in range(8):a[y,x*8+k]=(attr&7) if bits&(128>>k) else (attr>>3)&7
 Image.fromarray(pal[a]).resize((768,576),Image.Resampling.NEAREST).save(p.with_name(p.name.replace('.home.bin','.png')))
