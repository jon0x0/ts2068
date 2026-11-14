"""Real-ROM native input CPU contract harness; gameplay tested separately."""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ecm='--ecm' in sys.argv
 out=ROOT/('build/ecm_native' if ecm else 'build/native')
 syms={m[0]:int(m[1],16) for m in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(ROOT/'build/native/input.sym').read_text())}
 setup=['set $keys ($case / 2048) * 33','set 0x74fa $keys','set z80:iff1 ($case / 1024) & 1','set z80:iff2 ($case / 1024) & 1','set z80:de 0xbeef','set z80:hl 0xcafe','set z80:sp 0xf000',f'set z80:pc {syms["after_keyboard"]}']
 lines=['set $armed 0','set $case 0',f'breakpoint {syms["after_keyboard"]} if $armed == 0',f'breakpoint {syms["port1_value"]} if $armed == 1',f'breakpoint {syms["port2_value"]} if $armed == 1',f'breakpoint {syms["input_done"]} if $armed == 1 && $case < 4095',f'breakpoint {syms["input_done"]} if $armed == 1 && $case == 4095','commands 1','set $armed 1','out 255 64']+setup+['continue','end','commands 2','set z80:af (255 ^ ($case & 31)) * 256 + (z80:af & 255)','continue','end','commands 3','set z80:af (255 ^ (($case / 32) & 31)) * 256 + (z80:af & 255)','continue','end']
 for index in (4,5):
  lines += [f'commands {index}']+[f'print z80:{r}' for r in ('af','iff1','de','hl','sp')]
  if index==4:lines += ['set $case $case + 1']+setup+['continue','end']
  else:lines += ['exit','end']
 program='\n'.join(lines);(out/'input_cpu.commands').write_text(program)
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 try:
  p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(out/('RType_level1_ECM_TSPico_RAM.dck' if ecm else 'RType_level1_native_experimental.dck')),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=35,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
 except subprocess.TimeoutExpired as e:
  (out/'input_cpu_timeout.log').write_bytes((e.stdout or b'')+(e.stderr or b''));raise
 (out/'input_cpu.log').write_text(p.stdout+p.stderr)
 v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
 assert p.returncode==0 and len(v)==4096*5,(p.returncode,len(v))
 for case in range(4096):
  n=(case&31)|((case//32)&31)
  expected=(case//2048)*33|((n&1)<<3)|((n&2)<<1)|((n&4)>>2)|((n&8)>>2)|(n&16)
  af,iff,de,hl,sp=v[case*5:case*5+5]
  assert af>>8==expected,(case,hex(af),hex(expected))
  assert bool(af&0x40)==(expected==0),(case,'Z flag')
  assert (iff,de,hl,sp)==((case//1024)&1,0xbeef,0xcafe,0xf000),(case,iff,de,hl,sp)
 (out/'input_cpu.json').write_text(json.dumps(dict(pairs=1024,cases=4096,passed=True,coverage='Every two-port state, keyboard neutral/retained, interrupts off/on, DE/HL/SP and Z flag; real Fuse CPU'),indent=2))
 print('4096 CPU cases passed: native port pairs, keyboard union, interrupt state, flags and stack.')
if __name__=='__main__':main()
