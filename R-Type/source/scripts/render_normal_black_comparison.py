from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'build/normal_black_audit'
# Deliberately distinct black/bright-black entries; no flattening or BW filter.
pal=[(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(51,51,51),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)]
def draw(name,mode):
 b=(O/name).read_bytes();im=Image.new('RGB',(256,192));px=im.load()
 for y in range(192):
  for cx in range(32):
   at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|cx;a=b[(0x6000+at)if mode==2 else(0x5800+(y//8)*32+cx)];bits=b[0x4000+at]
   for x in range(8):px[cx*8+x,y]=pal[((a&7)if bits&(128>>x)else((a>>3)&7))+(8 if a&64 else 0)]
 return im.resize((512,384),Image.Resampling.NEAREST)
out=Image.new('RGB',(1040,852),(24,24,24));d=ImageDraw.Draw(out)
for row,(label,base,frame,mode)in enumerate([('Cartridge title','stock',400,2),('TAP animated scores','tap',1000,0)]):
 for col,(state,text)in enumerate([('before','Previous'),('fixed','Fixed')]):
  x=col*520+4;y=row*426+4;d.text((x,y),label+' - '+text,fill='white');out.paste(draw(f'{base}_{state}_{frame}.ram',mode),(x,y+24))
out.save(O/'before_after.png');print(O/'before_after.png')
