from pathlib import Path
import sys,json,shutil,collections
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_reviewed_r72 import frames;from build_rocket_fix import code
B=R/'build/fullgame/l1_chosen_r107';O=R/'build/fullgame/l1_head_c_r109';A=R/'build/graphics/l1_head_c_r109';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(s in p.name for s in ['l1_','.home.','validation','route','native_jump']):shutil.copy2(p,O/p.name)
for name in ['generic_manifest.json','walker_runtime.json','global_tags.json']:shutil.copy2(B/name,O/name)
b=bytearray((B/'level01_region.bin').read_bytes());old=bytes(b);ds=frames(b,1);ids=set(range(30,34));used=set(range(16))|{t&127 for d in ds if d['id']not in ids for _,t,_ in d['cells']if t!=54};free=iter(sorted(set(range(128))-used-{54}));pool={old[0x2000+t*8:0x2008+t*8]:t for t in used};changes=[];dictionary=[];report=[];pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8);sheet=Image.new('RGB',(768,330),(20,25,30));draw=ImageDraw.Draw(sheet)
for i in range(4):
 d=ds[29+i];bits=np.frombuffer((A/f'L1_head_{i}.bits').read_bytes(),np.uint8).reshape(24,3);attrs=np.frombuffer((A/f'L1_head_{i}.attrs').read_bytes(),np.uint8).reshape(24,3);assert not np.any(attrs&192);lost=0;im=Image.new('RGB',(24,24));pix=im.load()
 for k,(ptr,t,raw)in enumerate(d['cells']):
  cy,cx=divmod(k,3);aa=attrs[cy*8:cy*8+8,cx].tobytes();bb=bits[cy*8:cy*8+8,cx].tobytes()
  if t==54:
   for y in range(8):
    for x in range(8):lost+=bool((aa[y]&7)if bb[y]&(128>>x)else(aa[y]>>3)&7)
   continue
  if aa not in pool:
   tag=next(free);pool[aa]=tag;b[0x2000+tag*8:0x2008+tag*8]=aa;dictionary.extend(range(0x2000+tag*8,0x2008+tag*8))
  tag=pool[aa];off=ptr-0x2000;b[off:off+9]=bytes([tag])+bb;changes.extend(range(off,off+9))
  for y in range(8):
   for x in range(8):pix[cx*8+x,cy*8+y]=tuple(pal[(aa[y]&7)if bb[y]&(128>>x)else(aa[y]>>3)&7])
 im.save(A/f'L1_head_{i}_installed.png');sheet.paste(im.resize((144,144)),(i*192+10,180));before=Image.new('RGB',(24,24));q=before.load()
 for k,(_,t,raw)in enumerate(d['cells']):
  if t==54:continue
  cy,cx=divmod(k,3)
  for y in range(8):
   at=old[0x2000+(t&127)*8+y]
   for x in range(8):q[cx*8+x,cy*8+y]=tuple(pal[(at&7)if raw[y+1]&(128>>x)else(at>>3)&7])
 sheet.paste(before.resize((144,144)),(i*192+10,24));report.append(dict(id=30+i,transparent_cell_clipped_pixels=lost))
allowed=set(changes+dictionary);assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(b,old)));assert all(d['raw']==e['raw']for d,e in zip(frames(b,1),ds)if d['id']not in ids);assert all(d['ptr']==e['ptr']and len(d['raw'])==len(e['raw'])for d,e in zip(frames(b,1),ds));draw.text((8,5),'BEFORE: L1 magenta-front shell',fill='white');draw.text((8,160),'AFTER: selected C, source scaled before RPC; 24x24 retained',fill='white');sheet.save(O/'head_c_comparison.png');(O/'level01_region.bin').write_bytes(b)
for name in ['LEVEL01.TAP','START01.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in [0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
oldlabel=b'R107 PREPARING  ';new=b'R109 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(oldlabel,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(oldlabel,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v);(O/'head_contract.json').write_text(json.dumps(dict(ids=sorted(ids),changedOffsets=sorted(allowed),dictionaryRows=len(dictionary)//8,frames=report,codeUnchanged=True,source='r88 head32 B, user-confirmed C comparison',settings=dict(brightness=52,contrast=59,saturation=82,gamma=.87)),indent=2))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_l1_fire','verify_l1_nofire']:
 s=(R/f'scripts/{stem}_r108.mjs').read_text().replace('l1_shared_ecm_r108','l1_head_c_r109').replace('boss_motion_fixture_r108','boss_motion_fixture_r109');(R/f'scripts/{stem}_r109.mjs').write_text(s)
print(report,'dictionary rows',len(dictionary)//8)
