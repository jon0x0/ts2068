from pathlib import Path
import sys,json,shutil
R=Path.cwd();sys.path.insert(0,'scripts');from build_rocket_fix import code
B=R/'build/fullgame/respawn_pickups_r141';O=R/'build/fullgame/l4_health_r142';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']and not any(k in p.name for k in['validation','summary','release_manifest']):shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
b=bytearray((B/'level04_region.bin').read_bytes());addresses=[0xcf5a,0xcf61,0xcf68]
for a in addresses:assert b[a]==32;b[a]=16
(O/'level04_region.bin').write_bytes(b)
for name in['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[k*8192+t*1024:k*8192+(t+1)*1024]for k in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
(O/'health_contract.json').write_text(json.dumps(dict(level=4,source_addresses=addresses,native_addresses=[a+0x2000 for a in addresses],old=32,new=16,targets=3,total_registered_hits=48,damage_code_unchanged=True),indent=2))
for name in['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R141',b'R142'))
p=O/'rtype/rt.tap';src=p.read_bytes();out=bytearray();a=0
while a<len(src):
 n=int.from_bytes(src[a:a+2],'little');q=bytearray(src[a+2:a+2+n]).replace(b'R141',b'R142');q[-1]=0
 for v in q[:-1]:q[-1]^=v
 out+=len(q).to_bytes(2,'little')+q;a+=n+2
p.write_bytes(out)
s=(R/'scripts/boss_motion_fixture_r141.mjs').read_text().replace('respawn_pickups_r141','l4_health_r142');(R/'scripts/boss_motion_fixture_r142.mjs').write_text(s)
s=(R/'scripts/probe_l4_settled_force_r137.mjs').read_text().replace('boss_motion_fixture_r137','boss_motion_fixture_r142').replace('l4_openings_r137','l4_health_r142').replace('<32','<16').replace('n===32','n===16');(R/'scripts/probe_l4_settled_force_r142.mjs').write_text(s)
