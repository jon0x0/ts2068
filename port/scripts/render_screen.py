from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
ram=(root/'build/scrolling-screen.ram').read_bytes()
pixels=[]
for y in range(192):
    for x in range(256):
        offset=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3)
        bits,attr=ram[0x4000+offset],ram[0x6000+offset]
        color=(attr&7) if bits&(128>>(x&7)) else ((attr>>3)&7)
        level=255 if attr&64 else 205
        pixels.append((level if color&2 else 0,level if color&4 else 0,level if color&1 else 0))
im=Image.new('RGB',(256,192));im.putdata(pixels);im.resize((1024,768),Image.Resampling.NEAREST).save(root/'build/scrolling-screen.png')
