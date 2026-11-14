from pathlib import Path
import shutil
from build_rocket_fix import code
src=Path('build/fullgame/detail_motion_r52');out=Path('build/fullgame/detail_motion_large_r52');out.mkdir(exist_ok=True,parents=True);shutil.copytree(src/'RTYPE',out/'RTYPE',dirs_exist_ok=True)
for p in src.glob('*_region.bin'):shutil.copy2(p,out/p.name)
for name in ['launcher.bin','demand_loader.sym','boss_preview.sym']:shutil.copy2(src/name,out/name)
b=bytearray(Path('build/fullgame/fast_boss_r51/level05_region.bin').read_bytes());engine=(src/'overlay.bin').read_bytes();b[0xe400:0xed80]=bytes([255])*0x980;b[0xe400:0xe400+len(engine)]=engine;(out/'level05_region.bin').write_bytes(b);(out/'RTYPE/LEVEL05.TAP').write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)))
s=Path('scripts/detail_motion_fixture.mjs').read_text().replace('detail_motion_r52','detail_motion_large_r52');Path('scripts/detail_motion_large_fixture.mjs').write_text(s)
s=Path('scripts/verify_detail_motion_boss.mjs').read_text().replace('./detail_motion_fixture.mjs','./detail_motion_large_fixture.mjs').replace("'1,2,3,4,5,6,7,8'", "'5'");Path('scripts/verify_detail_motion_large_boss.mjs').write_text(s)
