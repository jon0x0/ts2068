from pathlib import Path
import shutil,json,sys,re
R=Path.cwd();B=R/'build/fullgame/l5_cell_atomic_r97';O=R/'build/fullgame/l5_cold_start_r98';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym']and not any(x in p.name for x in ['.home.','failed','scene_','jump_','startup_']):shutil.copy2(p,O/p.name)
for name in ['global_tags.json','walker_runtime.json','generic_manifest.json']:shutil.copy2(B/name,O/name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(O/'motion.sym').read_text(),re.I)}
for n in range(1,9):
 b=bytearray((B/f'level{n:02d}_region.bin').read_bytes()).replace(b'R97 DEBUG',b'R98 DEBUG')
 if n==5:
  assert b[0xd4:0xdb]==bytes.fromhex('3e59d3f4c3dcdd');b[0xd9:0xdb]=sy['warmup'].to_bytes(2,'little')
  for q in json.loads((B/'atomic_patch.json').read_text())['atomic_ei_sites']:assert b[q]==0;b[q]=0xfb
 (O/f'level{n:02d}_region.bin').write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+t*1024:page*8192+(t+1)*1024],k)for k,(page,t)in enumerate((page,t)for page in[0,1,4,5,6,7]for t in range(8))))
old=b'R97 CELL TEST   ';new=b'R98 START FIX   ';assert len(old)==len(new)
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;b=p.read_bytes();assert b.count(old)==1;p.write_bytes(b.replace(old,new))
p=O/'rtype/rt.tap';b=bytearray(p.read_bytes());at=0
while at<len(b):
 size=int.from_bytes(b[at:at+2],'little');v=bytearray(b[at+2:at+2+size]).replace(old,new);c=0
 for x in v[:-1]:c^=x
 v[-1]=c;b[at+2:at+2+size]=v;at+=size+2
p.write_bytes(b)
(O/'startup_patch.json').write_text(json.dumps(dict(old_target=0xdddc,new_target=sy['warmup'],cold_gateway=0xd4,interrupt_behavior_restored_r96=True,checkpoints_retained=True),indent=2))
for stem in ['boss_motion_fixture','verify_walker_game','stress_l5_boss']:
 p=R/f'scripts/{stem}_r97.mjs';(R/f'scripts/{stem}_r98.mjs').write_text(p.read_text().replace('l5_cell_atomic_r97','l5_cold_start_r98').replace('boss_motion_fixture_r97','boss_motion_fixture_r98').replace('if(boot>=0&&t>=600&&t<700)','if(frame>=30&&(boot<0||t<120))'))
s=(R/'scripts/compare_selected_startup_r97.mjs').read_text().replace('[96,97]','[98]').replace('l5_cell_atomic_r97','l5_cold_start_r98').replace('startup_selected_comparison.json','startup_selected_validation.json').replace('for(const level of [5])','for(const level of [1,5])').replace('r.titles>0&&!r.fatal','r.titles>0&&!r.fatal&&r.region===r.level-1');(R/'scripts/verify_selected_startup_r98.mjs').write_text(s)
print('Cold gateway corrected to',hex(sy['warmup']))
