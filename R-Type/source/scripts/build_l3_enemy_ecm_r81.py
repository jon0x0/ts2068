from pathlib import Path
import sys,shutil,json,zipfile
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_reviewed_r72 import frames
from build_rocket_fix import code
B=R/'build/fullgame/offscreen_clip_r80';O=R/'build/fullgame/l3_enemy_ecm_r81';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
b=bytearray((B/'level03_region.bin').read_bytes());old=bytes(b);ds=frames(b,3);sel=[d for d in ds if 36<=d['id']<=39];used={t&127 for d in ds for p,t,r in d['cells']if t!=54};assert not used&{126,127}
# Normal black paper throughout; distinct per-scanline highlights, no bright-black.
patterns=[bytes([7,7,5,7,5,5,1,1]),bytes([7,3,3,2,3,3,1,1])]
for t,p in zip([126,127],patterns):b[0x2000+t*8:0x2008+t*8]=p
for d in sel:
 for k,(ptr,t,raw)in enumerate(d['cells']):
  if t==54:continue
  cy,cx=divmod(k,3);a=old[0x2000+(t&127)*8:0x2008+(t&127)*8];is_core=sum((v&7)==3 for v in a)>=4
  b[ptr-0x2000]=127 if is_core else 126
  assert b[ptr-0x2000+1:ptr-0x2000+9]==raw[1:]
for d in ds:
 if d['id']not in range(36,40):assert frames(b,3)[d['id']-1]['raw']==d['raw']
(O/'level03_region.bin').write_bytes(b)
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes();(O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',v[k*8192:(k+1)*8192],k)for k in range(8)));(O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',v[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
P=R/'build/graphics/l3_enemy_ecm_r81';P.mkdir(exist_ok=True);sheet=Image.new('RGB',(576,170));draw=ImageDraw.Draw(sheet);pal=[(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)]
for row,data in enumerate([old,b]):
 for col,d in enumerate(frames(data,3)[35:39]):
  im=Image.new('RGB',(24,24));pix=im.load()
  for k,(ptr,t,raw)in enumerate(d['cells']):
   if t==54:continue
   cy,cx=divmod(k,3)
   for y in range(8):
    a=data[0x2000+(t&127)*8+y]
    for x in range(8):pix[cx*8+x,cy*8+y]=pal[(a&7)if raw[1+y]&(128>>x)else(a>>3)&7]
  im.save(P/f'{"before"if row==0 else"after"}_{d["id"]}.png');sheet.paste(im.resize((72,72)),(col*144,row*85+12));draw.text((col*144,row*85),('Before 'if row==0 else'ECM ')+str(d['id']),fill='white')
sheet.save(P/'comparison.png')
s=(R/'scripts/boss_motion_fixture_r80.mjs').read_text().replace('offscreen_clip_r80','l3_enemy_ecm_r81');(R/'scripts/boss_motion_fixture_r81.mjs').write_text(s)
s=(R/'scripts/trace_l3_fragment_actors_r80.mjs').read_text().replace('boss_motion_fixture_r80','boss_motion_fixture_r81');(R/'scripts/trace_l3_fragment_actors_r81.mjs').write_text(s)
print('Built r81; unchanged silhouettes/frames/sizes, two unused dictionary rows, no code or timing changes')
