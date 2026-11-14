from pathlib import Path
import subprocess,re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
results=[]
for target,relative in [('sram','build/ecm_native/RType_level1_ECM_TSPico_RAM_r22.dck'),('rom','build/readonly_ecm/RType_ECM_ROM_candidate.dck')]:
 cart=ROOT/relative;raw=cart.read_bytes();input_bytes=raw[9+0x1a00:9+0x1b00];port=0x1a00+input_bytes.index(bytes.fromhex('ed 78 57 06 02 ed 78'))+2
 program='\n'.join(['set $stage 0',
  f'breakpoint {port} if spectrum:frames >= 800 && spectrum:frames < 830',
  'breakpoint 0x11d5 if (spectrum:frames >= 900 && spectrum:frames < 930) || (spectrum:frames >= 1000 && spectrum:frames < 1030)',
  'breakpoint time 100 if $stage == 0 && spectrum:frames >= 950',
  'breakpoint time 100 if $stage == 1 && spectrum:frames >= 1050',
  'breakpoint time 100 if spectrum:frames >= 1200',
  'commands 1','set z80:af 0xef00+(z80:af & 255)','continue','end',
  'commands 2','set z80:af 0xfb00+(z80:af & 255)','continue','end',
  'commands 3','print 0xcafe','print [0xfd93]','set $stage 1','continue','end',
  'commands 4','print 0xbeef','print [0xfd93]','exit','end',
  'commands 5','print 0xdead','exit 1','end'])
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(cart),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=40,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
 out=ROOT/'build/diagnostics/music_toggle_r22';out.mkdir(parents=True,exist_ok=True);(out/(target+'.log')).write_text(p.stdout+p.stderr);(out/(target+'.commands')).write_text(program)
 values=[int(v,16)for v in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)];assert p.returncode==0 and values==[0xcafe,1,0xbeef,0],(target,p.returncode,values)
 results.append(dict(target=target,bin_sha256=hashlib.sha256(raw[9:]).hexdigest(),held_press_muted=values[1],second_press_unmuted=values[3],passed=True))
(out/'fuse_validation.json').write_text(json.dumps(results,indent=2));print(results)
