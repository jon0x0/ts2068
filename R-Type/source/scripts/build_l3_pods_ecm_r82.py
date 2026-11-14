from pathlib import Path
import sys,shutil,json,zipfile,hashlib,functools
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_reviewed_r72 import frames
from build_rocket_fix import code
B=R/'build/fullgame/l3_enemy_ecm_r81';O=R/'build/fullgame/l3_pods_ecm_r82';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(s in p.name for s in['.home','trace','actors','captures']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level03_region.bin').read_bytes());old=bytes(b);ds=frames(b,3);ids=set(range(22,28))|set(range(31,36))|set(range(88,94));allowed=set()
for d in ds:
 if d['id']not in ids:continue
 for k,(ptr,t,raw)in enumerate(d['cells']):
  if t==54:continue
  cy,cx=divmod(k,d['w'])
  if d['id']in[34,35]:tag=92 if cx<3 else(30 if cy==0 else 126)
  elif 31<=d['id']<=33:tag=101 if cy==0 else(126 if cx else 127)
  elif 22<=d['id']<=24:tag=101 if cy==0 else 126
  elif 25<=d['id']<=27:tag=127 if cy==0 else 126
  else:tag=126 if cy==0 else 127
  b[ptr-0x2000]=tag;allowed.add(ptr-0x2000)
assert all(i in allowed for i,(a,c)in enumerate(zip(old,b))if a!=c)
for d in ds:
 e=frames(b,3)[d['id']-1];assert len(e['raw'])==len(d['raw'])
 for (p,t,r),(pp,tt,rr)in zip(d['cells'],e['cells']):assert r[1:]==rr[1:] and(t==54)==(tt==54)
(O/'level03_region.bin').write_bytes(b)
for name,data in [('LEVEL03.TAP',b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8))),('START03.TAP',b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))]:(O/'rtype'/name).write_bytes(data)
P=R/'build/graphics/l3_pods_ecm_r82';P.mkdir(exist_ok=True);reps=[22,25,31,34,35,88];sheet=Image.new('RGB',(768,360));draw=ImageDraw.Draw(sheet);pal=[(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)]
for row,data in enumerate([old,b]):
 for col,ident in enumerate(reps):
  d=frames(data,3)[ident-1];im=Image.new('RGB',(d['w']*8,d['h']*8));pix=im.load()
  for k,(ptr,t,raw)in enumerate(d['cells']):
   if t==54:continue
   cy,cx=divmod(k,d['w'])
   for y in range(8):
    a=data[0x2000+(t&127)*8+y]
    for x in range(8):pix[cx*8+x,cy*8+y]=pal[(a&7)if raw[1+y]&(128>>x)else(a>>3)&7]
  im.save(P/f'{"before"if row==0 else"after"}_{ident}.png');im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST);sheet.paste(im,(col*128,row*160+25));draw.text((col*128,row*160+5),('Before 'if row==0 else'ECM ')+str(ident),fill='white')
sheet.save(P/'comparison.png')
s=(R/'scripts/boss_motion_fixture_r81.mjs').read_text().replace('l3_enemy_ecm_r81','l3_pods_ecm_r82');(R/'scripts/boss_motion_fixture_r82.mjs').write_text(s)
s=(R/'scripts/trace_l3_fragment_actors_r81.mjs').read_text().replace('boss_motion_fixture_r81','boss_motion_fixture_r82');(R/'scripts/trace_l3_fragment_actors_r82.mjs').write_text(s)
print('r82 built: existing ECM dictionary reused, bitmap and code unchanged')

