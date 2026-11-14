from pathlib import Path
from PIL import Image,ImageDraw
from build_graphics import unpack
r=Path(__file__).resolve().parents[1];d=r/'build/diagnostics/l3_photo';ps=list(d.glob('frame*.home.bin'));im=Image.new('RGB',(5*256,((len(ps)+4)//5)*210));dr=ImageDraw.Draw(im)
for i,p in enumerate(ps):
 b=p.read_bytes();a=unpack(b[0x4000:0x5800],b[0x6000:0x7800]);a.save(p.with_suffix('.png'));x=(i%5)*256;y=(i//5)*210;im.paste(a,(x,y+14));dr.text((x,y),p.stem,fill='white')
im.save(d/'contact.png')
