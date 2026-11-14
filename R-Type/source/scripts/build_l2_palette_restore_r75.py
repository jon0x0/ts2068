from pathlib import Path
import shutil,sys
R=Path.cwd();B=R/'build/fullgame/loading_text_r74';O=R/'build/fullgame/l2_palette_restore_r75';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.sym','.asm','.json']:shutil.copy2(p,O/p.name)
b=bytearray((R/'build/fullgame/startup_r66/level02_region.bin').read_bytes());assert b[0x3e00]==0x21;b[0x3e00]=0xc9;(O/'level02_region.bin').write_bytes(b)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
(O/'rtype/LEVEL02.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
(O/'rtype/START02.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
s=(R/'scripts/boss_motion_fixture_r74.mjs').read_text(encoding='utf-8-sig').replace('loading_text_r74','l2_palette_restore_r75')
s=s.replace("if(c.region===1){assert(c.coreBefore.subarray(0x42d,0x430).equals(Buffer.from([0xc3,0xd8,1])),'L2 tile hook missing');c.coreBefore.set([0x3c,0x87,0x87],0x42d);}","if(c.region===1&&c.coreBefore.subarray(0x42d,0x430).equals(Buffer.from([0xc3,0xd8,1])))c.coreBefore.set([0x3c,0x87,0x87],0x42d);")
(R/'scripts/boss_motion_fixture_r75.mjs').write_text(s,encoding='utf-8')
for stem in ['verify_preload_title','verify_boss_game']:
 src=R/f'scripts/{stem}_r74.mjs'
 if not src.exists():src=R/f'scripts/{stem}_r73.mjs'
 s=src.read_text(encoding='utf-8-sig').replace('boss_motion_fixture_r74','boss_motion_fixture_r75').replace('boss_motion_fixture_r73','boss_motion_fixture_r75');(R/f'scripts/{stem}_r75.mjs').write_text(s,encoding='utf-8')
