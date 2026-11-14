from pathlib import Path
import shutil,sys,json,subprocess
R=Path.cwd();B=R/'build/releases/r100';O=R/'build/fullgame/photo_exhaust_r102';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(v in p.name for v in ['.home.','scene_','startup_','validation','manifest']):shutil.copy2(p,O/p.name)
for name in ['generic_manifest.json','walker_runtime.json','global_tags.json']:shutil.copy2(B/name,O/name)
s=(R/'src/l3_photo_exhaust_bridge.asm').read_text()
(O/'plume_bridge.asm').write_text(s);v=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={O/"plume_bridge.bin"}',str(O/'plume_bridge.asm')],capture_output=True,text=True);assert v.returncode==0,v.stdout+v.stderr
b=bytearray((B/'level03_region.bin').read_bytes());bridge=(O/'plume_bridge.bin').read_bytes();assert b[0x1c8:0x200]==bytes([255])*56;assert b[0xd22d:0xd233]==bytes.fromhex('cd858ecdfd8c');b[0x1c8:0x1c8+len(bridge)]=bridge;b[0xd22d:0xd233]=bytes.fromhex('cdc801000000');(O/'level03_region.bin').write_bytes(b)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
for name in ['LEVEL03.TAP','START03.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[page*8192+t*1024:page*8192+(t+1)*1024]for page in[0,1,4,5,6,7]for t in range(8)]
 (O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
s=(R/'scripts/boss_motion_fixture_r100.mjs').read_text().replace('build/releases/r100','build/fullgame/photo_exhaust_r102');(R/'scripts/boss_motion_fixture_r102.mjs').write_text(s)
s=(R/'scripts/trace_ordinary_exhaust_r100.mjs').read_text().replace('boss_motion_fixture_r100','boss_motion_fixture_r102').replace("const out='build/graphics/exhaust_integration_audit'","const out='build/fullgame/photo_exhaust_r102'").replace("fs.readFileSync('build/releases/r100/walker_runtime.json')","fs.readFileSync('build/fullgame/photo_exhaust_r102/walker_runtime.json')");(R/'scripts/verify_photo_exhaust_r102.mjs').write_text(s)

from functools import reduce
old=b'R100 PREPARING  ';new=b'R102 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;v=p.read_bytes();assert v.count(old)==1;p.write_bytes(v.replace(old,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 size=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+size]).replace(old,new);block[-1]=reduce(int.__xor__,block[:-1],0);v[at+2:at+2+size]=block;at+=size+2
p.write_bytes(v)
print('Only L3 dedicated plume draw routed through existing compiled sprite gateway; bridge',len(bridge))
