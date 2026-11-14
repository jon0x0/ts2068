from pathlib import Path
import numpy as np
from PIL import Image
from build_graphics import unpack,screen_offset
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'build/diagnostics/l4_boxes'
for p in out.glob('*.home.bin'):
 b=p.read_bytes();unpack(b[0x4000:0x5800],b[0x6000:0x7800]).resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'))
 blue=[]
 for y in range(160):
  for x in range(32):
   off=screen_offset(y)+x;a=b[0x6000+off];v=b[0x4000+off]
   if ((a>>3)&7)==1 or ((a&7)==1 and v):blue.append((x,y,v,a))
 print(p.name,'blue',len(blue),blue[:14])
