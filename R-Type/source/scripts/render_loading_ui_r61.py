from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_l5_preshift import image
p=Path(__file__).resolve().parents[1]/'build/fullgame/startup_r61'
pal=[(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)]
for f in p.glob('ui_*.home.bin'):
 b=f.read_bytes();im=Image.new('RGB',(256,192));pix=im.load()
 for y in range(192):
  a=0x4000+((y&192)<<5)+((y&7)<<8)+((y&56)<<2)
  for x in range(256):
   attr=b[0x5800+(y//8)*32+x//8];pix[x,y]=pal[(attr&7)if b[a+x//8]&(128>>(x&7))else((attr>>3)&7)]
 im.resize((768,576),Image.Resampling.NEAREST).save(f.with_suffix('.png'))
files=sorted(p.glob('jump_*.home.bin'));contact=Image.new('RGB',(1024,384*((len(files)+1)//2)))
for i,f in enumerate(files):contact.paste(image(f.read_bytes()),((i%2)*512,(i//2)*384))
contact.save(p/'repeated_jumps.png')
