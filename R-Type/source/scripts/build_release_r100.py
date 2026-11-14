"""Promote the immutable, hardware-confirmed r99 baseline to release r100."""
from pathlib import Path
import json,shutil,hashlib,zipfile,functools,sys
R=Path(__file__).resolve().parents[1];B=R/'build/fullgame/irq_layout_r99';O=R/'build/releases/r100';O.mkdir(parents=True,exist_ok=True)
z=B/'RType_TS2068_r99.zip';assert hashlib.sha256(z.read_bytes()).hexdigest()=='fa1d6a4d67b854f1acd5e3495dff564eac30bfc6b4d0b2175de00bbfdaa58c5a'
with zipfile.ZipFile(z)as f:
 assert f.testzip()is None
 for p in (B/'rtype').glob('*.TAP'):assert p.read_bytes()==f.read('rtype/'+p.name)
 assert (B/'rtype/rt.tap').read_bytes()==f.read('rtype/rt.tap')
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym']and not any(s in p.name for s in ['.home.','failed','scene_','jump_','startup_']):shutil.copy2(p,O/p.name)
for name in ['global_tags.json','generic_manifest.json','walker_runtime.json']:shutil.copy2(B/name,O/name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();assert a.count(b'R99 DEBUG')==1;b=a.replace(b'R99 DEBUG',b'R100 INFO');assert len(b)==65536
 (O/f'level{n:02d}_region.bin').write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+t*1024:page*8192+(t+1)*1024],k)for k,(page,t)in enumerate((page,t)for page in[0,1,4,5,6,7]for t in range(8))))
old=b'R99 PREPARING   ';new=b'R100 PREPARING  ';assert len(old)==len(new)==16
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;b=p.read_bytes();assert b.count(old)==1;p.write_bytes(b.replace(old,new))
p=O/'rtype/rt.tap';b=bytearray(p.read_bytes());at=0
while at<len(b):
 size=int.from_bytes(b[at:at+2],'little');v=bytearray(b[at+2:at+2+size]).replace(old,new);v[-1]=functools.reduce(int.__xor__,v[:-1],0);b[at+2:at+2+size]=v;at+=size+2
p.write_bytes(b)
for stem in ['boss_motion_fixture','verify_selected_startup','verify_cold_fire','verify_walker_game','verify_pause']:
 p=R/f'scripts/{stem}_r99.mjs';s=p.read_text().replace('irq_layout_r99','../../releases/r100').replace('build/fullgame/../../releases/r100','build/releases/r100').replace('boss_motion_fixture_r99','boss_motion_fixture_r100').replace('[99]','[100]');(R/f'scripts/{stem}_r100.mjs').write_text(s)
print('r100 promoted: only same-length release labels differ from confirmed r99.')
