from pathlib import Path
from PIL import Image
import sys
p=Path(sys.argv[1]);b=p.read_bytes();assert len(b)==12288
im=Image.new('RGB',(256,192));px=im.load()
for y in range(192):
 for x in range(256):
  off=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3)
  at=b[6144+off];c=at&7 if b[off]&(128>>(x&7)) else at>>3&7
  k=255 if at&64 else 205;px[x,y]=(k if c&2 else 0,k if c&4 else 0,k if c&1 else 0)
im.resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'))
print(p.with_suffix('.png'))
