from pathlib import Path
import sys,json,shutil
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_reviewed_r72 import frames;from build_rocket_fix import code
B=R/'build/fullgame/l1_chosen_r107';O=R/'build/fullgame/l1_shared_ecm_r108';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(s in p.name for s in ['l1_','.home.','validation','route','native_jump']):shutil.copy2(p,O/p.name)
for name in ['generic_manifest.json','walker_runtime.json','global_tags.json']:shutil.copy2(B/name,O/name)
b=bytearray((B/'level01_region.bin').read_bytes());old=bytes(b);src=(B/'level03_region.bin').read_bytes();ds=frames(b,1);es=frames(src,3);used={t&127 for d in ds for p,t,r in d['cells']if t!=54};assert not used&{126,127};changes=[]
for t in [126,127]:b[0x2000+t*8:0x2008+t*8]=src[0x2000+t*8:0x2008+t*8];assert all(v&0xf8==0 for v in b[0x2000+t*8:0x2008+t*8])
for ident in range(30,34):
 d=ds[ident-1];e=es[ident+5];assert (d['w'],d['h'])==(e['w'],e['h'])==(3,3)
 for (ptr,t,raw),(_,st,sraw) in zip(d['cells'],e['cells']):
  assert raw[1:]==sraw[1:]
  if t==54:assert st==54;continue
  assert st&127 in [126,127];b[ptr-0x2000]=st;changes.append(ptr-0x2000)
for d,e in zip(frames(b,1),ds):
 if d['id']not in range(30,34):assert d['raw']==e['raw']
allowed=set(changes)|set(range(0x23f0,0x2400));assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(b,old)));(O/'level01_region.bin').write_bytes(b)
for name in ['LEVEL01.TAP','START01.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in [0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
old=b'R107 PREPARING  ';new=b'R108 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(old,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(old,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v);(O/'shared_ecm_contract.json').write_text(json.dumps(dict(nativeIDs=[30,31,32,33],sourceIDs=[36,37,38,39],tagOffsets=changes,dictionaryOffsets=list(range(0x23f0,0x2400)),bitmapIdentity=True,codeUnchanged=True),indent=2))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_l1_fire','verify_l1_nofire']:
 s=(R/f'scripts/{stem}_r107.mjs').read_text().replace('l1_chosen_r107','l1_shared_ecm_r108').replace('boss_motion_fixture_r107','boss_motion_fixture_r108');(R/f'scripts/{stem}_r108.mjs').write_text(s)
print('L1 native30..33 restored to existing L3 ECM shading; no renderer/runtime layout changes')
