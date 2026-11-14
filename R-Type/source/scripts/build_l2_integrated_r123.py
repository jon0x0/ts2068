from pathlib import Path
import shutil,json
R=Path.cwd();B=R/'build/fullgame/l2_art_r121';O=R/'build/fullgame/l2_integrated_r123';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.json','.asm','.sym'] and '.home.' not in p.name and not any(t in p.name for t in ['validation','approach','mismatch','trace','probe','timing','diagnose','fire_','final_l2','native_jump']):shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
old=b'R116 PREPARING  ';new=b'R123 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;v=p.read_bytes();assert old in v;p.write_bytes(v.replace(old,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(old,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
for stem in ['boss_motion_fixture','probe_l2_full','probe_l2_short','verify_cold_l2_fire','verify_l2_revisits','verify_native_revisits']:
 p=R/f'scripts/{stem}_r121.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_art_r121','l2_integrated_r123').replace('boss_motion_fixture_r121','boss_motion_fixture_r123');(R/f'scripts/{stem}_r123.mjs').write_text(s,encoding='utf-8')
(R/'build/fullgame/l2_art_r122/DO_NOT_USE.txt').write_text('UNPUBLISHED palette experiment. Full background scan adds too much cost. Not included in r123.\n')
print(O)
