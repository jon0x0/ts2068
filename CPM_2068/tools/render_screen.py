"""Render a captured TS2068 HOME RAM hires framebuffer, no emulator UI needed."""
import argparse
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('memory',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
m=a.memory.read_bytes();assert len(m)==65536
im=Image.new('RGB',(512,192));pixels=im.load()
for y in range(192):
    for x in range(512):
        addr=(0x6000 if (x//8)%2 else 0x4000)+((y&192)<<5)+((y&7)<<8)+((y&56)<<2)+x//16
        pixels[x,y]=(255,255,255) if m[addr]&(128>>(x%8)) else (0,0,0)
im.resize((1024,384)).save(a.output)
