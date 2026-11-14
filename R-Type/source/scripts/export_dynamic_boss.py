"""Export reusable individual boss cels, not precomposed arrangements."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/boss_dynamic';OUT.mkdir(parents=True,exist_ok=True)
b=(ROOT/'build/fullgame/material_game_r49/level05_region.bin').read_bytes();sprites=[]
for cel in range(3):
 colours=[0]*1024
 for cell in range(16):
  cy,cx=divmod(cell,4)
  for y in range(8):
   q=0x8c00+(cel*16+cell)*16+y*2;px,a=b[q:q+2]
   for x in range(8):
    c=(a&7)if px&(128>>x)else((a>>3)&7);colours[(cy*8+y)*32+cx*8+x]=c+(8 if a&64 and c else 0)
 sprites.append(dict(width=32,height=32,colours=colours))
native=bytes(0xc000)+b[0xa000:0xe000];layout=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][4];d=layout['enemy_descriptors_start']+7*4;w,h=native[d:d+2];p=int.from_bytes(native[d+2:d+4],'little');colours=[0]*(w*h*64);dictionary=b[0x2000:0x2400]
for cy in range(h):
 for cx in range(w):
  a=native[p]
  if a==54:p+=1;continue
  for y in range(8):
   attr=dictionary[(a&127)*8+y];px=native[p+1+y]
   for x in range(8):
    c=(attr&7)if px&(128>>x)else((attr>>3)&7);colours[(cy*8+y)*w*8+cx*8+x]=c+(8 if attr&64 and c else 0)
  p+=9
sprites.append(dict(width=w*8,height=h*8,colours=colours))
(OUT/'sprites.json').write_text(json.dumps(sprites,separators=(',',':')));print([(s['width'],s['height'])for s in sprites])
