"""Decode original M72 sprite objects using the documented MAME word layout."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_graphics import decode_roms,palette_ram
def render(frame,sprites=None):
 if sprites is None:sprites,_=decode_roms()
 base=ROOT/f'build/fullgame/arcade_reference/frame{frame:06d}';words=np.frombuffer(base.with_name(base.name+'_sprites.bin').read_bytes(),dtype='<u2');palette=palette_ram(base.with_name(base.name+'_palette_sprite.bin'));objects=[];offset=0
 while offset+3<len(words):
  yy,code,flags,xx=map(int,words[offset:offset+4]);w=1<<((flags>>14)&3);h=1<<((flags>>12)&3);x=(xx&1023)-320;y=384-(yy&511)-h*16;colour=flags&15;fliph=bool(flags&0x800);flipv=bool(flags&0x400)
  if x<384 and x+w*16>0 and y<256 and y+h*16>0:
   indices=np.zeros((h*16,w*16),dtype='uint8')
   for cx in range(w):
    for cy in range(h):
     c=code+8*(w-1-cx if fliph else cx)+(h-1-cy if flipv else cy)
     if c>=len(sprites):continue
     tile=sprites[c]
     if fliph:tile=tile[:,::-1]
     if flipv:tile=tile[::-1]
     indices[cy*16:cy*16+16,cx*16:cx*16+16]=tile
   rgb=palette[colour*16+indices];rgba=np.concatenate([rgb,np.where(indices[:,:,None]!=0,255,0)],axis=2).astype('uint8');objects.append((dict(offset=offset,code=code,colour=colour,x=x,y=y,width=w*16,height=h*16),Image.fromarray(rgba,'RGBA')))
  offset+=4*w
 canvas=Image.new('RGBA',(384,256))
 for desc,im in reversed(objects):canvas.alpha_composite(im,(desc['x'],desc['y']))
 return canvas,objects
def main():
 sprites,_=decode_roms();out=ROOT/'build/fullgame/arcade_objects';out.mkdir(exist_ok=True);frames=[10200,17400,26400,36600,44700,54000,60300,72900];sheet=Image.new('RGB',(768,4*276));draw=ImageDraw.Draw(sheet)
 for level,frame in enumerate(frames,1):
  im,objects=render(frame,sprites);im.save(out/f'level{level:02d}_objects.png');(out/f'level{level:02d}_objects.json').write_text(json.dumps([v[0]for v in objects],indent=2));x=(level-1)%2*384;y=(level-1)//2*276;sheet.paste(im,(x,y+20),im);draw.text((x+4,y+3),f'Level{level} frame{frame}',fill='white')
 sheet.save(out/'contact.png');(out/'provenance.json').write_text(json.dumps(dict(source='Original local graphics ROM planes and captured sprite/palette RAM',layout_reference='https://github.com/mamedev/mame/blob/master/src/mame/irem/m72_v.cpp',method='Independent Python M72 object-word decoder. Visible origin x64,y0, sixteen-pixel cels, palette alpha index0.'),indent=2))
if __name__=='__main__':main()
