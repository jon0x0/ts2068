from pathlib import Path
import sys,re,numpy as np
R=Path.cwd();O=R/'build/fullgame/loading_text_r74';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import pack,unpack
from build_rocket_fix import code
sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(O/'demand_loader.sym').read_text(),re.I)}
b=bytearray((O/'demand_loader.bin').read_bytes());start=sy['loading_screen']-0x6000;end=sy['loading_digits']-0x6000;ui=bytearray(unpack(b[start:end]));font=(R/'assets/fullgame_preloader_font.bin').read_bytes()
def off(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
for y in list(range(96,112))+list(range(152,168)):ui[off(y):off(y)+32]=bytes(32)
def text(s,x,y):
 for k,c in enumerate(s):
  for row,v in enumerate(font[(ord(c)-32)*8:(ord(c)-31)*8]):ui[off(y+row)+x//8+k]=v
text('LEVEL',120,96);text('OF',88,152);text('...',200,152)
compressed=pack(ui);assert len(compressed)<=end-start;b[start:end]=compressed.ljust(end-start,b'\0')
for n,c in enumerate('0123456789'):
 raw=bytearray(32)
 for y,v in enumerate(font[(ord(c)-32)*8:(ord(c)-31)*8]):raw[y*2]=v
 at=end+n*32;b[at:at+32]=raw
(O/'demand_loader.bin').write_bytes(b);(O/'loading_ui.lz').write_bytes(compressed);(O/'loading_digits.bin').write_bytes(b[end:end+320])
p=O/'launcher.bin';launch=bytearray(p.read_bytes());assert launch[-len(b):]==(R/'build/fullgame/terrain_restore_r73/demand_loader.bin').read_bytes();launch[-len(b):]=b;p.write_bytes(launch)
p=O/'rtype/rt.tap';old=p.read_bytes();pos=0
for _ in range(2):pos+=2+int.from_bytes(old[pos:pos+2],'little')
p.write_bytes(old[:pos]+code('RTYPE LOAD',launch,32768))
# Render the actual static loading UI for inspection.
from PIL import Image
a=np.zeros((192,256),np.uint8)
for y in range(192):
 for x in range(32):
  v=ui[off(y)+x]
  for k in range(8):a[y,x*8+k]=255 if v&(128>>k)else 0
Image.fromarray(a).resize((768,576),Image.Resampling.NEAREST).save(O/'loading_small_text.png')
print('All loading labels and numeric progress use 8x8 glyphs; loader size unchanged',len(b))
