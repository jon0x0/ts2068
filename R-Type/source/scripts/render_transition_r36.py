from pathlib import Path
from PIL import Image
from build_graphics import unpack,screen_offset
r=Path(__file__).resolve().parents[1];d=r/'build/diagnostics/transition_r36'
for p in d.glob('*.home.bin'):
 b=p.read_bytes();attrs=bytearray(6144)
 for y in range(192):
  for x in range(32):attrs[screen_offset(y)+x]=b[0x7800+(y//8)*32+x]
 unpack(b[0x6000:0x7800],attrs).resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'))
