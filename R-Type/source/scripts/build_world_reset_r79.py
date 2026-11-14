from pathlib import Path
import shutil,sys,re,functools
R=Path.cwd();B=R/'build/fullgame/startup_bulk_r77';O=R/'build/fullgame/world_reset_r79';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
player=(R/'build/fullgame/world_owner_r78/overlay_protection.bin').read_bytes();(O/'overlay.bin').write_bytes(player)
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());assert b[0xcf0:0xcfc]==bytes.fromhex('cdc386e52100002281ffe1c9');b[0xcf0:0xd00]=bytes.fromhex('cdc273cdc386e52100002281ffe1c945');b[0xe400:0xed80]=player.ljust(2432,b'\xff');p.write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
s=(R/'scripts/boss_motion_fixture_r77.mjs').read_text(encoding='utf-8-sig').replace('startup_bulk_r77','world_reset_r79');(R/'scripts/boss_motion_fixture_r79.mjs').write_text(s,encoding='utf-8')
for stem,ver in [('verify_colour_jumps',76),('verify_boss_game',77),('verify_preload_title',77)]:
 s=(R/f'scripts/{stem}_r{ver}.mjs').read_text(encoding='utf-8-sig').replace(f'boss_motion_fixture_r{ver}','boss_motion_fixture_r79');(R/f'scripts/{stem}_r79.mjs').write_text(s,encoding='utf-8')
s=(R/'scripts/verify_colour_jumps_r79.mjs').read_text().replace('route=[2,3,2,3,1,3,2,3]','route=[2]');(R/'scripts/probe_one_jump_r79.mjs').write_text(s)

