from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/l5_effects_fast_r59'
def raster(data):
 im=Image.new('RGB',(256,192));p=im.load()
 for y in range(192):
  at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(256):
   bits=data[at+(x>>3)];a=data[6144+at+(x>>3)];c=(a&7)if bits&(128>>(x&7))else(a>>3)&7;v=255 if a&64 else 205;p[x,y]=(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
 return im

def main():
 ids=[75, 76, 78, 81, 82, 84, 87, 94, 95, 97, 99, 100, 101, 102, 103, 104, 105, 106];cellw=220;rowh=160;canvas=Image.new('RGB',(770,50+rowh*len(ids)),'#111');d=ImageDraw.Draw(canvas)
 for c,text in enumerate(['r57 reference','r58 corruption','r59 repaired']):d.text((104+c*cellw,12),text,fill='white')
 for row,ident in enumerate(ids):
  y=42+row*rowh;d.text((8,y+12),('Explosion 'if ident<99 else'Sparks ')+str(ident),fill='white')
  for c in range(3):
   data=(OUT/f'effect_{ident}_{c}.bin').read_bytes();im=raster(data).crop((40,24,104,72)).resize((192,144),Image.Resampling.NEAREST);canvas.paste(im,(104+c*cellw,y))
 canvas.save(OUT/'effects_comparison.png')
 (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>R-Type r59 effect repair</title><style>body{background:#111;color:#eee;font:17px system-ui;margin:28px}img{image-rendering:pixelated;max-width:100%;height:auto}p{max-width:850px;line-height:1.5}</style><h1>Native firing sparks and explosions</h1><p>Each cell is drawn by the actual native renderer. Left: r57 reference. Middle: r58 after its phase cache overwrites ordinary sprite colour IDs. Right: r59 with the repaired cache. The repaired retained bitmap and ECM planes match r57 byte for byte. These are isolated renderer captures, not hardware photographs or full gameplay captures.</p><img src="effects_comparison.png">')
 print(OUT/'effects_comparison.png')
if __name__=='__main__':main()
