"""Independently sample full-screen ECM art and the ready prompt in Fuse."""
import json
import re
import subprocess
from pathlib import Path
from package_leap_cartridge import load_symbols

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/crown-combined'
N=load_symbols(OUT/'intro.sym')
S=load_symbols(ROOT/'build/combined-runtime/build/test_basic.sym')
def address(y,x): return 0x4000+((y&0xC0)<<5)+((y&7)<<8)+((y&0x38)<<2)+x
cells=[address(y,x) for y in (0,8,16,24,32,40,48,56,64,72,80,88,96,104,112,120,128,144,160,176,184,191)
       for x in (0,3,7,11,15,19,23,27,31)]
addresses=cells+[a+0x2000 for a in cells]
prompt_rows=[int(v,16) for v in re.findall(r'\$([0-9A-F]{4})',(OUT/'prompt_rows.inc').read_text())]
prompt_addresses=[a+x for a in prompt_rows for x in range(5)]
addresses+=prompt_addresses
addresses += [a+0x2000 for a in prompt_addresses]
commands=[f'breakpoint {N["wait_key"]}','commands 1',
          'print [0xfac0]','print [0xfac1]','print [0xfac3]','print [0xfac6]',
          f'print [{S["VM_ERROR_CODE"]}]','out 0xf4 3']
for i in range(0,len(addresses),4):
    commands.append('print '+'+'.join(f'{256**j}*[{a}]' for j,a in enumerate(addresses[i:i+4])))
commands+=['exit 0','end']
text='\n'.join(commands)
(OUT/'fuse-intro-commands.txt').write_text(text)
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
r=subprocess.run([__import__('os').environ.get('FUSE_EXE', 'fuse'),'--machine','ts2068',
    '--rom-ts2068-0',str(OUT/'stock-home.rom'),'--rom-ts2068-1',str(OUT/'stock-exrom.rom'),
    '--dock',str(OUT/'program.dck'),'--speed','5000','--no-sound','--debugger-command',text],
    capture_output=True,text=True,timeout=60,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
(OUT/'fuse-intro.log').write_text(r.stdout+r.stderr)
assert r.returncode==0,r.stdout+r.stderr
values=[int(v,16)&0xFFFFFFFF for v in re.findall(r'^0x([0-9a-f]+)\s*$',r.stdout,re.M|re.I)]
assert len(values)==5+(len(addresses)+3)//4
active,phase,ready,refresh,error=values[:5]
assert active==1 and ready==1 and refresh>2 and error==0
actual=b''.join(v.to_bytes(4,'little') for v in values[5:])[:len(addresses)]
seq=Path(json.loads((OUT/'manifest.json').read_text()).get('animation_sequence',ROOT/'build/intro-eight-locked/codec/sequence'))
planes=(seq/f'frame_{phase:05d}.pix').read_bytes()+(seq/f'frame_{phase:05d}.atr').read_bytes()
expected=bytearray(planes[a-0x4000 if a<0x6000 else a-0x6000+6144] for a in addresses[:len(cells)*2])
rom=(ROOT/'build/combined-runtime/v2_home.bin').read_bytes()
# Obtain font pointers from the emulator-backed TSRun capture: the full prompt
# bitmap there was produced by the same runtime font lookup, independently.
capture=(OUT/'startup-ready.ecm').read_bytes()
expected.extend(capture[a-0x4000] for a in prompt_addresses)
expected.extend(bytes([2])*len(prompt_addresses))
assert actual==expected,'Fuse ECM art or prompt samples differ'
report={'emulator':'Fuse','stock_rom_boot':True,'full_screen_ecm':True,'phase':phase,
        'bitmap_and_attribute_samples':len(cells)*2,'prompt_bytes':len(prompt_addresses),
        'ready_prompt_exact':True,'ready_prompt_red':True,'vm_error':error,'refreshes_at_ready':refresh}
(OUT/'fuse-startup.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
