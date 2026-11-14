"""Count game updates, tile draws, repairs and IRQs over fixed emulated frames."""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/diagnostics/performance';out.mkdir(parents=True,exist_ok=True)
 timing=json.loads((out/'frame_period.json').read_text());hz=timing['display_hz']
 for label,dck in [('r9',ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r9.dck'),('r10',ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r10.dck'),('rom_r10',ROOT/'build/readonly_ecm/RType_ECM_ROM_candidate.dck')]:
  lines=['set $n 0','set $tile 0','set $repair 0','set $irq 0','breakpoint 0x1a28 if spectrum:frames >= 800 && spectrum:frames < 830','commands 1','set z80:af 0xef00 + (z80:af & 255)','continue','end']
  for i,(addr,var) in enumerate(((0x8649,'n'),(0x8ea2,'tile'),(0x8883,'repair'),(0xbe23,'irq')),2):
   lines += [f'breakpoint {addr} if spectrum:frames >= 1400 && spectrum:frames < 2000',f'commands {i}',f'set ${var} ${var}+1']
   if var=='n':lines+=['print spectrum:frames']
   lines+=['continue','end']
  lines+=['breakpoint time 100 if spectrum:frames == 2000','commands 6','print 0xcafe','print $n','print $tile','print $repair','print $irq','print z80:pc','exit','end']
  program='\n'.join(lines);(out/(label+'.commands')).write_text(program)
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
  p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(dck),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=55,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
  (out/(label+'.log')).write_text(p.stdout+p.stderr)
  v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)];m=v.index(0xcafe);ticks=v[:m];v=v[m+1:];assert len(v)==5,(v,p.stderr)
  result=dict(updates=v[0],tile_calls=v[1],restore_calls=v[2],irqs=v[3],pc=hex(v[4]),updates_per_second=v[0]/600*hz,frame_tstates=timing['frame_tstates'],display_hz=hz,frame_intervals=[b-a for a,b in zip(ticks,ticks[1:])]);(out/(label+'.json')).write_text(json.dumps(result,indent=2));print(label,result)
if __name__=='__main__':main()
