from pathlib import Path
import sys,shutil,re,subprocess,json,struct
import numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
from boss_motion_assets_r60 import pack,unpack
B=R/'build/fullgame/hardware_fire_r65';O=R/'build/fullgame/startup_r66';O.mkdir(exist_ok=True);(O/'rtype').mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
for p in (B/'rtype').iterdir():
 if p.is_file():shutil.copy2(p,O/'rtype'/p.name)
def asm(name,text):
 p=O/(name+'.asm');p.write_text(text);q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);p.with_suffix('.log').write_text(q.stdout+q.stderr);assert q.returncode==0 and 'warning:'not in(q.stdout+q.stderr).lower(),q.stdout+q.stderr
 sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
# Reuse the existing logo/data generator, simplify uniform logo colour rows.
p=R/'scripts/build_force_loading_r62.py';s=p.read_text();ns={'__file__':str(p)};exec(compile(s[:s.index('def main():')],'r66_ui','exec'),ns);ns['OUT']=O
src=s[s.index('def make_ui():'):s.index('def main():')].replace("text('LOADING',72,128,2)","text('READING FILES',24,128);text('SHIFT-L LOAD ALL',32,64)").replace('attrs[1:7].tobytes()','attrs[1:7,0].tobytes()');exec(compile(src,'r66_ui','exec'),ns);ns['make_ui']()
text=(B/'demand_loader.asm').read_text();a=text.index('; Cold startup only:');z=text.index('\nfont: INCBIN',a);text=text[:a]+(R/'src/responsive_startup_r66.asm').read_text()+text[z:]
text=re.sub(r'build/fullgame/[^"\n]+/(loading_ui.lz|loading_digits.bin|loading_logo_attrs.bin)',lambda m:'build/fullgame/startup_r66/'+m[1],text)
loader,sy=asm('demand_loader',text);oldlen=(B/'demand_loader.bin').stat().st_size;assert len(loader)<0x1800
import build_preload_helpers_r62 as h
ns=dict(vars(h));src=(R/'scripts/build_preload_helpers_r62.py').read_text().replace('level_hotkeys_r62.asm','level_hotkeys_r66.asm').replace('preload_snapshot_r62.asm','preload_snapshot_r64.asm').replace('preload_restore_r61.asm','preload_restore_r65.asm').replace('preload_feedback_r62.asm','preload_feedback_r66.asm');exec(compile(src,'r66_helpers','exec'),ns)
hot,hs,driver,restore=ns['build'](O,asm,len(loader),sy['preload_entry']);home,hsy,_,_=ns['build'](O,asm,len(loader),sy['preload_entry'],home=True);assert len(home)<=1024 and len(hot)<=1024
worker,_=asm('preload_worker',''.join(f'{k} EQU ${v:04X}\n'for k,v in {**sy,'PRELOAD_DRIVER_BYTES':driver,'PRELOAD_DRIVER_STATE':hs['preload_driver.state'],'RESTORE_BYTES':restore}.items()if '.'not in k)+(R/'src/preload_worker_r61.asm').read_text().replace('build/fullgame/startup_r61/','build/fullgame/startup_r66/'));(O/'rtype/RTPRELD.TAP').write_bytes(code('RTPRELOAD',worker.ljust(8192,b'\0'),0x8000))
pattern=bytes.fromhex('21 00 40 11 00 60 01')+oldlen.to_bytes(2,'little')+bytes.fromhex('ed b0')
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());at=b.find(pattern,0xa30,0xbc0);assert at>=0;b[at+7:at+9]=len(loader).to_bytes(2,'little')
 if n==5:
  b[0xa000:0xa400]=home.ljust(1024,b'\0');b[0xa400:0xa400+(O/'preload_feedback_home.bin').stat().st_size]=(O/'preload_feedback_home.bin').read_bytes()
  dispatcher,_=asm('hotkey_home_dispatch',f'        ORG $00DB\n        PUSH AF\n        DI\n        LD A,$21\n        OUT ($F4),A\n        LD HL,$A000\n        LD DE,$7B00\n        LD BC,{len(home)}\n        LDIR\n        CALL $7B00\n        LD A,9\n        OUT ($F4),A\n        EI\n        POP AF\n        RET\n        ASSERT $ <= $00F7\n');b[0xdb:0xdb+len(dispatcher)]=dispatcher
 else:b[0x3a00:0x3a00+len(hot)]=hot;b[0x3e00:0x3e00+(O/'preload_feedback.bin').stat().st_size]=(O/'preload_feedback.bin').read_bytes()
 p.write_bytes(b);(O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+s*1024:p*8192+(s+1)*1024],k)for k,(p,s)in enumerate((p,s)for p in[0,1,4,5,6,7]for s in range(8))))
bootstrap,_=asm('disk_bootstrap',f'        ORG $8000\n        DI\n        LD SP,$FFF0\n        XOR A\n        OUT ($F4),A\n        LD HL,resident\n        LD DE,$6000\n        LD BC,{len(loader)}\n        LDIR\n        JP ${sy["boot_entry"]:04X}\nresident:\n');launch=bootstrap+loader;(O/'launcher.bin').write_bytes(launch)
b=(B/'rtype/rt.tap').read_bytes();pos=0
for _ in range(2):pos+=2+int.from_bytes(b[pos:pos+2],'little')
(O/'rtype/rt.tap').write_bytes(b[:pos]+code('RTYPE LOAD',launch,32768));(O/'startup_contract.json').write_text(json.dumps({'loader_bytes':len(loader),'previous_loader_bytes':oldlen,'hot_bytes':len(hot),'home_hot_bytes':len(home),'startup_latch':'D623 -> cold image -> FDA6 -> hot_preload','graphics_changed':False,'snapshot_index_regs':'not modified; no longer redundantly saved','stages':['READING FILES','VERIFYING MEMORY','PREPARING GAME','PREP RAM']},indent=2));print('r66',len(loader),len(hot),len(home))
