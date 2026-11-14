from pathlib import Path
import sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from build_graphics import unpack
O=R/'build/fullgame/photo_exhaust_r102';A=R/'build/graphics/exhaust_integration_audit';im=Image.new('RGB',(640,152),(15,20,25));d=ImageDraw.Draw(im)
for x,p,label in [(0,A/'ordinary_160.home.bin','r100: original draw path'),(320,O/'ordinary_160.home.bin','r102: photo-based artwork in game')]:
 b=p.read_bytes();screen=unpack(b[0x4000:0x5800],b[0x6000:0x7800]);screen.resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'));crop=screen.crop((176,88,256,120)).resize((320,128),Image.Resampling.NEAREST);im.paste(crop,(x,24));d.text((x+5,5),label,fill='white')
im.save(O/'plume_gameplay_comparison.png')
