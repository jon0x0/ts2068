from pathlib import Path
import shutil,sys,json
R=Path.cwd();B=R/'build/fullgame/terrain_restore_r73';O=R/'build/fullgame/loading_text_r74';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.sym','.asm','.json']:shutil.copy2(p,O/p.name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());at=0xa400 if n==5 else 0x3e00;assert b[at:at+3]==bytes.fromhex('210058');b[at]=0xc9;p.write_bytes(b)
 assert sum(a!=c for a,c in zip(b,(B/p.name).read_bytes()))==1
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
for name in ['preload_feedback','preload_feedback_home']:
 p=O/(name+'.bin')
 if p.exists():b=bytearray(p.read_bytes());b[0]=0xc9;p.write_bytes(b)
 p=O/(name+'.asm')
 if p.exists():s=p.read_text(encoding='utf-8-sig');s=s.replace('loading_feedback:','loading_feedback:\n        RET ; r74: keep existing loading UI and normal PREPARING GAME text');p.write_text(s,encoding='utf-8')
fixture=(R/'scripts/boss_motion_fixture_r73.mjs').read_text(encoding='utf-8-sig').replace('terrain_restore_r73','loading_text_r74');(R/'scripts/boss_motion_fixture_r74.mjs').write_text(fixture,encoding='utf-8')
p=R/'scripts/verify_preload_title_r72.mjs';s=p.read_text(encoding='utf-8-sig').replace('boss_motion_fixture_r72','boss_motion_fixture_r74');(R/'scripts/verify_preload_title_r74.mjs').write_text(s,encoding='utf-8')
print('r74: one-byte feedback suppression per level; artwork and loader unchanged')
