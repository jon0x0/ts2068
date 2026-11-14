from pathlib import Path
import shutil,json,sys
R=Path.cwd();B=R/'build/fullgame/l5_row_restore_r96';O=R/'build/fullgame/l5_cell_atomic_r97';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym'] and not any(x in p.name for x in ['.home.','failed','scene_','jump_']):shutil.copy2(p,O/p.name)
for name in ['global_tags.json','walker_runtime.json','generic_manifest.json']:
 shutil.copy2(B/name,O/name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
changes={}
for n in range(1,9):
 b=bytearray((B/f'level{n:02d}_region.bin').read_bytes()).replace(b'R96 DEBUG',b'R97 DEBUG')
 if n==5:
  # Keep all addresses fixed: only the two EI instructions become NOP.
  q=b.find(bytes.fromhex('d3f4fb'),0x8c00,0x8dc2);assert q>=0;b[q+2]=0
  p=b.find(bytes.fromhex('d3f4fb'),0x899d,0x8bf0);assert p>=0;b[p+2]=0
  changes['atomic_ei_sites']=[q+2,p+2]
  assert b[0x8907:0x890a]==bytes.fromhex('c32089')
  # Dead, unreachable gap: two preserving tail wrappers.
  b[0x890a:0x891c]=bytes.fromhex('f53e04d3fef1c3008cf53e05d3fef1c36e1a')
  for target,wrapper in [(0x8c00,0x890a),(0x1a6e,0x8913)]:
   q=b.find(b'\xcd'+target.to_bytes(2,'little'),0x8920,0x8a00);assert q>=0;b[q+1:q+3]=wrapper.to_bytes(2,'little')
  assert b[0x97b:0x986]==bytes.fromhex('3e84ed47af320090c9ffff');b[0x97b:0x986]=bytes.fromhex('3e84ed47afd3fe320090c9')
 (O/f'level{n:02d}_region.bin').write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+t*1024:page*8192+(t+1)*1024],k)for k,(page,t)in enumerate((page,t)for page in[0,1,4,5,6,7]for t in range(8))))
old=b'R96 ROW RESTORE ';new=b'R97 CELL TEST   ';assert len(old)==len(new)
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;b=p.read_bytes();assert b.count(old)==1;p.write_bytes(b.replace(old,new))
p=O/'rtype/rt.tap';b=bytearray(p.read_bytes());at=0
while at<len(b):
 size=int.from_bytes(b[at:at+2],'little');v=bytearray(b[at+2:at+2+size]).replace(old,new);c=0
 for x in v[:-1]:c^=x
 v[-1]=c;b[at+2:at+2+size]=v;at+=size+2
p.write_bytes(b)
(O/'atomic_patch.json').write_text(json.dumps(changes,indent=2))
for stem in ['boss_motion_fixture','verify_walker_game','stress_l5_boss','repro_l5_low_charge','verify_l5_row_components','verify_l5_empty_rows','verify_l5_clipping']:
 p=R/f'scripts/{stem}_r96.mjs'
 if p.exists():(R/f'scripts/{stem}_r97.mjs').write_text(p.read_text().replace('l5_row_restore_r96','l5_cell_atomic_r97').replace('boss_motion_fixture_r96','boss_motion_fixture_r97').replace('l5_low_charge_r96','l5_low_charge_r97'))
print(changes)
