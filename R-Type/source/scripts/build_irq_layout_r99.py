from pathlib import Path
import shutil,re,subprocess,sys,json
R=Path.cwd();B=R/'build/fullgame/l5_bank_guard_r93';O=R/'build/fullgame/irq_layout_r99';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']and not any(x in p.name for x in ['.home.','failed','scene_','jump_','validation']):shutil.copy2(p,O/p.name)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
src=(B/'ui_home.asm').read_text();newsrc=src.replace('FONT_ORIGIN EQU $8F10','FONT_ORIGIN EQU $8B70').replace('KEY_ORIGIN EQU $8F40','KEY_ORIGIN EQU $8B30');assert newsrc!=src
p=O/'ui_home.asm';p.write_text(newsrc);v=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={O/"ui_home.bin"}',f'--sym={O/"ui_home.sym"}',str(p)],capture_output=True,text=True);assert v.returncode==0,v.stdout+v.stderr;ui=(O/'ui_home.bin').read_bytes();assert len(ui)==365
for n in range(1,9):
 b=bytearray((B/f'level{n:02d}_region.bin').read_bytes()).replace(b'R38 DEBUG',b'R99 DEBUG')
 if n==5:
  assert b[0x8b30:0x8ba0]==bytes([255])*112
  glyph=b[0x8f10:0x8f40];b[0x8f00:0x9000]=bytes([0x5b])*256
  b[0x8b30:0x8b62]=ui[315:];b[0x8b70:0x8ba0]=glyph;b[0x9ea0:0x9fdb]=ui[:315]
 (O/f'level{n:02d}_region.bin').write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+t*1024:page*8192+(t+1)*1024],k)for k,(page,t)in enumerate((page,t)for page in[0,1,4,5,6,7]for t in range(8))))
# Full rollback to r93 execution, except moving UI out of the raw IM2 table.
old=b'PREPARING GAME  ';new=b'R99 PREPARING   ';assert len(old)==len(new)
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;b=p.read_bytes();assert b.count(old)==1;p.write_bytes(b.replace(old,new))
p=O/'rtype/rt.tap';b=bytearray(p.read_bytes());at=0
while at<len(b):
 size=int.from_bytes(b[at:at+2],'little');v=bytearray(b[at+2:at+2+size]).replace(old,new);c=0
 for x in v[:-1]:c^=x
 v[-1]=c;b[at+2:at+2+size]=v;at+=size+2
p.write_bytes(b)
for stem in ['boss_motion_fixture','verify_walker_game','stress_l5_boss']:
 p=R/f'scripts/{stem}_r98.mjs';s=p.read_text().replace('l5_cold_start_r98','irq_layout_r99').replace('boss_motion_fixture_r98','boss_motion_fixture_r99');(R/f'scripts/{stem}_r99.mjs').write_text(s)
for oldname,newname in [('verify_selected_startup_r98','verify_selected_startup_r99'),('repro_cold_fire_r98','verify_cold_fire_r99')]:
 s=(R/f'scripts/{oldname}.mjs').read_text().replace('[98]','[99]').replace('l5_cold_start_r98','irq_layout_r99').replace('boss_motion_fixture_r98','boss_motion_fixture_r99');(R/f'scripts/{newname}.mjs').write_text(s)
print('r93 execution restored; UI key bridge8B30/font8B70; raw IM2table8F00..8FFF clear of code.')
