from pathlib import Path
import json,shutil,hashlib
R=Path.cwd();B=R/'build/fullgame/l4_speed_r92';O=R/'build/fullgame/l5_bank_guard_r93';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.sym','.asm','.json']and not any(x in p.name for x in ['.home.','failed','trace','scene_','jump_']):shutil.copy2(p,O/p.name)
P=R/'build/fullgame/bank5_restore_r91'
for name in ['level05_region.bin']:shutil.copy2(P/name,O/name)
for name in ['LEVEL05.TAP','START05.TAP']:shutil.copy2(P/'rtype'/name,O/'rtype'/name)
a=(P/'level05_region.bin').read_bytes();b=(B/'level05_region.bin').read_bytes();diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert diff and all(0x3a00<=p<0x3e00 for p in diff)
(O/'regression_repair.json').write_text(json.dumps(dict(r92_overwritten_bytes=len(diff),range_start=hex(min(diff)),range_end=hex(max(diff)+1),l5_exact_r91=True,l5_region_sha256=hashlib.sha256(a).hexdigest(),cause='Generic hotkey installer ignored L5 HOME_VARIANT exception and overwrote occupied boss phase payload in DOCK1.',hardware_lockup_not_reproduced=True),indent=2))
p=R/'scripts/finish_l4_keys_r92.py';s=p.read_text().replace('for n in range(1,9):\n',"for n in range(1,9):\n if n==5:continue # L5 DOCK1 is boss phase payload; its HOME hotkey variant stays unchanged.\n",1);p.write_text(s)
for stem in ['boss_motion_fixture','verify_walker_game','verify_native_revisits','verify_restore_helper','verify_four_frame','stress_l5_boss','repro_l4_l5_boss']:
 p=R/f'scripts/{stem}_r92.mjs'
 if p.exists():
  s=p.read_text().replace('l4_speed_r92','l5_bank_guard_r93').replace('boss_motion_fixture_r92','boss_motion_fixture_r93');(R/f'scripts/{stem}_r93.mjs').write_text(s)
print('Repaired L5 bytes',len(diff),'exact original region and tapes restored')
