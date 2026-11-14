from pathlib import Path
import ast,json,subprocess
R=Path.cwd();out=R/'build/graphics/l6_flash_capture';out.mkdir(parents=True,exist_ok=True)
t=ast.parse((R/'scripts/capture_all_arcade.py').read_text());func=next(n for n in t.body if isinstance(n,ast.FunctionDef));assign=next(n for n in func.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='lua' for v in n.targets));lua=assign.value.func.value.value
lua=lua.replace('OUTDIR',json.dumps(out.as_posix())).replace('frame>=1200 and frame%300==0','frame>=47700 and frame<=49500 and frame%4==0').replace('  m.screens[":screen"]:snapshot(base..".png")','').replace('dump(base,"palette_tile",0xcc000,0xc00)','').replace('dump(base,"state",0x42f00,0x100)','')
(out/'capture.lua').write_text(lua)
for name in ['cfg','nvram','snap']:(out/name).mkdir(exist_ok=True)
cmd=['C:/apps/games/MAME/mame.exe','rtype','-noreadconfig','-rompath',str(R/'arcade')+';'+str(R/'build/mame_archival_standins_ff'),'-video','none','-sound','none','-nothrottle','-skip_gameinfo','-seconds_to_run','910','-autoboot_delay','0','-autoboot_script',str(out/'capture.lua'),'-cfg_directory',str(out/'cfg'),'-nvram_directory',str(out/'nvram'),'-snapshot_directory',str(out/'snap')]
p=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=300);(out/'mame.log').write_text(p.stdout+p.stderr);print('exit',p.returncode,'captures',len(list(out.glob('*sprites.bin'))));assert p.returncode==0 and len(list(out.glob("*sprites.bin")))>0
