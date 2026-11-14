"""Build a same-bitmap comparison from the actual live explosion RAM capture."""
from pathlib import Path
from PIL import Image,ImageDraw
from collections import Counter
import json
from build_graphics import unpack,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/ecm_native';b=(out/'explosion_joy.bin').read_bytes();j=json.loads((out/'explosion_joy.json').read_text());bc=j['blast_info'][1];x=(bc&255)*8;y=(bc>>8)*8
 image=unpack(b[:6144],b[8192:8192+6144]);crop=image.crop((x,y,x+24,y+24));old=Image.new('RGB',(24,24))
 for yy in range(24):
  for xx in range(24):
   px=x+xx;py=y+yy;bit=crop.getpixel((xx,yy))!=(0,0,0)
   old.putpixel((xx,yy),(255,255,255) if bit else (0,0,0))
 canvas=Image.new('RGB',(640,370),(24,24,28));draw=ImageDraw.Draw(canvas);draw.text((24,18),'Same explosion silhouette: white / live ECM',fill='white')
 canvas.paste(old.resize((288,288),Image.Resampling.NEAREST),(16,48));canvas.paste(crop.resize((288,288),Image.Resampling.NEAREST),(336,48));draw.text((16,344),'White reference',fill='white');draw.text((336,344),'Actual Fuse ECM capture',fill='white')
 canvas.save(out/'explosion_comparison.png');crop.resize((288,288),Image.Resampling.NEAREST).save(out/'explosion_detail.png')
 counts=Counter(crop.getdata());colors=[c for c in counts if c!=(0,0,0)]
 assert len(colors)>=5 and (255,255,255) in colors and (255,0,0) in colors and (255,255,0) in colors
 rows=[[b[8192+screen_offset(py)+px] for px in range(x//8,x//8+3)] for py in range(y,y+24)]
 paired=[]
 for yy in range(y,y+24):
  for xx in range(x,x+24,8):
   attr=b[8192+screen_offset(yy)+xx//8];rgb=set(image.crop((xx,yy,xx+8,yy+1)).getdata())
   if attr&0x38 and len(rgb)>1 and (0,0,0) not in rgb:paired.append(dict(x=xx,y=yy,attribute=attr,colours=[list(c) for c in rgb]))
 assert paired,'No two-foreground cells in synchronized live capture'
 (out/'explosion_colour_validation.json').write_text(json.dumps(dict(bounds=[x,y,x+24,y+24],paired_foreground_strips=paired,visible_colours=[list(c)+[counts[c]] for c in colors],rows=rows,reference='White reference uses captured nonblack occupancy; ECM decoded live HOME RAM. Opaque strips contain two foreground colours.'),indent=2))
 # Confirm occupied pixels against unmodified source, not just a recoloured preview.
 source=bytes(0x4000)+(ROOT/'build/native/snapshot.bin').read_bytes()
 ident=j['blast_info'][2]>>8;at=0xbc67+(ident-1)*4;w,h=source[at:at+2];ptr=int.from_bytes(source[at+2:at+4],'little');checked=0
 for ty in range(h):
  for tx in range(w):
   attr=source[ptr];ptr+=1
   if attr==0x36:continue
   for yy in range(8):
    for xx in range(8):
     original=bool(source[ptr+yy]&(128>>xx));actual=crop.getpixel((tx*8+xx,ty*8+yy))!=(0,0,0)
     assert original==actual,(tx,ty,xx,yy)
     checked+=1
   ptr+=8
 (out/'explosion_silhouette_validation.json').write_text(json.dumps(dict(sprite_id=ident,source_pixels_checked=checked,mismatches=0,captured_frame=j['frame']),indent=2))
 print('Verified',len(colors),'nonblack explosion colours,',len(paired),'paired 8x1 strips,',checked,'source silhouette pixels.')
if __name__=='__main__':main()
