from pathlib import Path
import sys,re,json,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
from build_hardware_fire_r65 import main,OUT
from build_rocket_fix import code
main()
for name in ['boot']:
 p=OUT/f'{name}_region.bin';b=bytearray(p.read_bytes());assert b[0x7fa9:0x7fac]==bytes.fromhex('cd ef fd');b[0x7fa9:0x7fac]=bytes.fromhex('cd 72 00');p.write_bytes(b)
def asm(name,text):
 p=OUT/(name+'.asm');p.write_text(text);q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
 sy={k:int(v,16) for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
import build_preload_helpers_r62 as h
ns=dict(vars(h));src=(R/'scripts/build_preload_helpers_r62.py').read_text().replace('level_hotkeys_r62.asm','level_hotkeys_r64.asm').replace('preload_snapshot_r62.asm','preload_snapshot_r64.asm').replace('preload_restore_r61.asm','preload_restore_r65.asm');exec(compile(src,'r65helpers','exec'),ns)
sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(OUT/'demand_loader.sym').read_text(),re.I)}
hot,hs,driver,restore=ns['build'](OUT,asm,(OUT/'demand_loader.bin').stat().st_size,sy['preload_entry']);home,hsy,_,_=ns['build'](OUT,asm,(OUT/'demand_loader.bin').stat().st_size,sy['preload_entry'],home=True)
assert len(home)<=1024 and len(hot)<=1024
defs={**sy,'PRELOAD_DRIVER_BYTES':driver,'PRELOAD_DRIVER_STATE':hs['preload_driver.state'],'RESTORE_BYTES':restore}
worker,_=asm('preload_worker',''.join(f'{k} EQU ${v:04X}\n'for k,v in defs.items()if '.'not in k)+(R/'src/preload_worker_r61.asm').read_text().replace('build/fullgame/startup_r61/','build/fullgame/hardware_fire_r65/'));(OUT/'rtype/RTPRELD.TAP').write_bytes(code('RTPRELOAD',worker.ljust(8192,b'\0'),0x8000))
font=(R/'assets/fullgame_preloader_font.bin').read_bytes();glyph=b''.join(bytes(font[(ord(c)-32)*8+y]for c in 'PAUSED')for y in range(8));infos=[]
for name in [f'level{n:02d}'for n in range(1,9)]:
 p=OUT/f'{name}_region.bin';b=bytearray(p.read_bytes());special=name=='level05';origin=0x9ea0 if special else 0x3e40;f=0x8f10 if special else 0x3fc0;mapping=0x19 if special else 0x0b;key_origin=0x8f40 if special else 0x3f80
 ui,us=asm('ui_home'if special else'ui',f'UI_ORIGIN EQU ${origin:04X}\nFONT_ORIGIN EQU ${f:04X}\nUI_MAP EQU ${mapping:02X}\nKEY_ORIGIN EQU ${key_origin:04X}\n'+(R/'src/ui_controls_r65.asm').read_text());main_len=us['ui_end']-origin;key_len=len(ui)-main_len;assert main_len<=336 and key_len<=64
 if name!='boot':
  if special:b[0xa000:0xa000+len(home)]=home
  else:b[0x3a00:0x3a00+len(hot)]=hot
 # generic UI padding and L5 unused title/music padding; glyphs outside renderer and palette bounds.
 shim_at=0x1b17
 assert b[shim_at:shim_at+9]==bytes([255])*9
 shim=bytes([0xf5,0xf3,0x3e,mapping,0xd3,0xf4,0xc3,origin&255,origin>>8]);title=bytes([0x3e,mapping,0xd3,0xf4,0xc3,(origin+3)&255,(origin+3)>>8]);b[shim_at:shim_at+9]=shim
 b[origin:origin+main_len]=ui[:main_len];b[key_origin:key_origin+key_len]=ui[main_len:];assert b[0x1b03]==0xf5 and b[0x1b12]==0xf1;b[0x1b03]=0xf3;b[0x1b12]=0;b[f:f+48]=glyph;b[0xcc2:0xcc5]=bytes([0xcd,shim_at&255,shim_at>>8]);p.write_bytes(b);infos.append({'name':name,'origin':origin,'bytes':main_len,'key_origin':key_origin,'key_bytes':key_len,'font':f})
boot=(OUT/'boot_region.bin').read_bytes();common=bytearray(boot[0x4000:0x8000]);common[0x656:0x659]=bytes.fromhex('cd 17 1b');core=bytes(common)+boot[0x3400:0x3fe0].ljust(3072,b'\0')+boot[0x3000:0x33b0].ljust(1024,b'\0')+boot[0xa000:0xa4ae].ljust(2048,b'\0');(OUT/'rtype/RTCORE.TAP').write_bytes(b''.join(code(f'RTCORE{k:02X}',core[k*1024:(k+1)*1024],k)for k in range(22)))
for n in range(1,9):
 b=(OUT/f'level{n:02d}_region.bin').read_bytes();(OUT/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(OUT/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+s*1024:p*8192+(s+1)*1024],k)for k,(p,s)in enumerate((p,s)for p in[0,1,4,5,6,7]for s in range(8))))
(OUT/'ui_contract.json').write_text(json.dumps(infos,indent=2));print(infos)
