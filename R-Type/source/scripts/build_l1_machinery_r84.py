from pathlib import Path
import sys,shutil,json
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_reviewed_r72 import frames
from build_rocket_fix import code
B=R/'build/fullgame/l1_machinery_r83';O=R/'build/fullgame/l1_machinery_r84';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(s in p.name for s in['.home','trace','actors','captures']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level01_region.bin').read_bytes());before=bytes(b);old=(R/'build/fullgame/l2_rpc_r67/level01_region.bin').read_bytes();ds=frames(b,1);d=ds[7];od=frames(old,1)[7];used={t&127 for f in ds for p,t,r in f['cells']if t!=54};free=iter(sorted(set(range(16,128))-used-{54}));pool={bytes(b[0x2000+t*8:0x2008+t*8]):t for t in range(128)if t!=54};changes=[]
for k,((ptr,t,raw),(op,ot,orr))in enumerate(zip(d['cells'],od['cells'])):
 if t==54 or ot==54:continue
 cy,cx=divmod(k,d['w']);attrs=bytearray(b[0x2000+(t&127)*8:0x2008+(t&127)*8]);bits=bytearray(raw[1:]);rows=[]
 for y in range(8):
  yy=cy*8+y
  # Only complete 8x1 cells strictly inside the two openings may change.
  oa=old[0x2000+(ot&127)*8+y]
  if 9<=cx<=11 and (56<=yy<80 or 88<=yy<124) and (oa&63)==7:
   bits[y]=orr[1+y];attrs[y]=old[0x2000+(ot&127)*8+y]&63;rows.append(yy)
 if not rows:continue
 key=bytes(attrs)
 if key not in pool:
  nt=next(free);pool[key]=nt;b[0x2000+nt*8:0x2008+nt*8]=key
 nt=pool[key];b[ptr-0x2000:ptr-0x2000+9]=bytes([nt])+bits;changes.append(dict(cell=[cx,cy],rows=rows))
assert changes
(O/'level01_region.bin').write_bytes(b)
for name,data in [('LEVEL01.TAP',b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8))),('START01.TAP',b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))]:(O/'rtype'/name).write_bytes(data)
P=R/'build/graphics/l1_machinery_r84';P.mkdir(exist_ok=True);sheet=Image.new('RGB',(672,320));dr=ImageDraw.Draw(sheet)
for col,(label,data)in enumerate([('Before',before),('Restored machinery',b),('Earlier conversion',old)]):
 f=frames(data,1)[7];im=Image.new('RGB',(112,144));pix=im.load()
 for k,(p,t,raw)in enumerate(f['cells']):
  if t==54:continue
  cy,cx=divmod(k,14)
  for y in range(8):
   a=data[0x2000+(t&127)*8+y];v=255 if a&64 else 205
   for x in range(8):
    c=(a&7)if raw[1+y]&(128>>x)else(a>>3)&7;pix[cx*8+x,cy*8+y]=(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
 im.save(P/f'candidate_{col}.png');sheet.paste(im.resize((224,288),Image.Resampling.NEAREST),(col*224,25));dr.text((col*224,5),label,fill='white')
sheet.save(P/'comparison.png');(O/'machinery_patch.json').write_text(json.dumps(changes,indent=2))
s=(R/'scripts/boss_motion_fixture_r83.mjs').read_text().replace('l1_machinery_r83','l1_machinery_r84');(R/'scripts/boss_motion_fixture_r84.mjs').write_text(s)
s=(R/'scripts/verify_boss_game_r80.mjs').read_text().replace('boss_motion_fixture_r80','boss_motion_fixture_r84');(R/'scripts/verify_boss_game_r84.mjs').write_text(s)
print(changes)
