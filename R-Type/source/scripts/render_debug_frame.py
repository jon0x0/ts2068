from pathlib import Path
from PIL import Image
from build_graphics import unpack,screen_offset
r=Path(__file__).resolve().parents[1];d=r/'build/diagnostics/debug_frame_r39';b=(d/'captured.home.bin').read_bytes();a=bytearray(6144)
for y in range(192):
 for x in range(32):a[screen_offset(y)+x]=b[0x5800+y//8*32+x]
unpack(b[0x4000:0x5800],a).resize((768,576),Image.Resampling.NEAREST).save(d/'captured.png')

p=d/'live_stall.home.bin'
if p.exists():
 b=p.read_bytes();a=bytearray(6144)
 for y in range(192):
  for x in range(32):a[screen_offset(y)+x]=b[0x5800+y//8*32+x]
 unpack(b[0x4000:0x5800],a).resize((768,576),Image.Resampling.NEAREST).save(d/'live_stall.png')

p=d/'ram_view.home.bin'
if p.exists():
 b=p.read_bytes();unpack(b[0x4000:0x5800],b[0x6000:0x7800]).resize((768,576),Image.Resampling.NEAREST).save(d/'ram_view.png')
