"""Measure Fuse's actual TS2068 frame period using a 10T JP loop, IRQs off."""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/diagnostics/performance';program='\n'.join(['set $n 0','set $armed 0','breakpoint 0x8634','breakpoint 0xc000 if $armed == 1 && spectrum:frames < $startframe+2','breakpoint 0xc000 if $armed == 1 && spectrum:frames >= $startframe+2','commands 1','set $armed 1','set z80:iff1 0','set z80:iff2 0','set 0xc000 0xc3','set 0xc001 0','set 0xc002 0xc0','set $t ula:tstates','set $startframe spectrum:frames','set z80:pc 0xc000','continue','end','commands 2','set $n $n+1','continue','end','commands 3','print $n+1','print $t','print ula:tstates','print $startframe','print spectrum:frames','exit','end'])
 (out/'frame_period.commands').write_text(program);si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r8.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=20,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/'frame_period.log').write_text(p.stdout+p.stderr);v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)];assert len(v)==5 and p.returncode==0 and 'Invalid debugger command' not in p.stderr,(v,p.stderr)
 period=(v[0]*10-v[2]+v[1])/(v[4]-v[3]);assert period.is_integer(),period
 result=dict(frame_tstates=int(period),cpu_hz=3528000,display_hz=3528000/period,method='IRQ-off10T JP loop over two frame boundaries; measured current Fuse1.7 TS2068')
 (out/'frame_period.json').write_text(json.dumps(result,indent=2));print(result)
if __name__=='__main__':main()
