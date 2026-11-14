from pathlib import Path
import sys
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_graphics import unpack
O=R/'build/fullgame/full_plume_r104';A=R/'build/fullgame/plume_diameter_r103';im=Image.new('RGB',(640,152),(15,20,25));d=ImageDraw.Draw(im)
for x,p,label in [(0,A/'ordinary_160.home.bin','r103: retained old exhaust section'),(320,O/'ordinary_160.home.bin','r104: photo plume reaches the rim')]:
 b=p.read_bytes();screen=unpack(b[0x4000:0x5800],b[0x6000:0x7800]);screen.resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'));im.paste(screen.crop((176,88,256,120)).resize((320,128),Image.Resampling.NEAREST),(x,24));d.text((x+5,5),label,fill='white')
im.save(O/'full_plume_comparison.png')
