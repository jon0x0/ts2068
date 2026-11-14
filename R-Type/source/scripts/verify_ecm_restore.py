"""Check both original dirty-restore branches and interrupt states in Fuse."""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/ecm_native';results=[]
 gate=int(re.search(r'restore_background_colour: EQU 0x([0-9a-fA-F]+)',(out/'renderer.sym').read_text()).group(1),16)
 background=[0x42,0x46,0x47,0x72,0x32,0x45,0x44,0x41]
 for ident in (0,1):
  for iff in (0,1):
   name=f'restore_{ident}_{iff}'
   lines=['breakpoint 0x8634','breakpoint 0x8886','breakpoint 0x88b3','commands 1',
    'set z80:iff1 0','set z80:iff2 0',f'set 0x8883 0xcd',f'set 0x8884 {gate&255}',f'set 0x8885 {gate>>8}','out 244 11','set 0x3ff0 2','set 0x5945 0xc5','set 0x7f45 0x63','out 244 7']
   for y,a in enumerate(background):lines += [f'set {0x4845+y*256} {a}',f'set {0x6845+y*256} 0x2f']
   lines += ['out 244 9',f'set z80:af {ident*256}','set z80:bc 0x1234','set z80:de 0x7f45','set z80:hl 0x4845','set z80:ix 0x4567','set z80:iy 0x6789','set z80:sp 0xe000',f'set z80:iff1 {iff}',f'set z80:iff2 {iff}','set z80:pc 0x8881','continue','end']
   for index in (2,3):
    lines += [f'commands {index}']+[f'print z80:{r}' for r in ('af','bc','de','hl','ix','iy','sp','iff1')]
    lines += ['print [0xdffe]+256*[0xdfff]','print [0x7f45]','out 244 1']+[f'print [{0x6845+y*256}]' for y in range(8)]+['exit','end']
   lines+=['breakpoint time 100 if spectrum:frames == 2000','commands 4','exit 1','end']
   program='\n'.join(lines);(out/(name+'.commands')).write_text(program)
   startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
   p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(out/'RType_level1_ECM_TSPico_RAM.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=20,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
   (out/(name+'.log')).write_text(p.stdout+p.stderr)
   v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
   assert p.returncode==0 and len(v)==18,(name,p.returncode,v)
   assert v[:10]==[0x54 if not ident else 0x110,0x1234,0x7f45,0x4845,0x4567,0x6789,0xdffe,iff,0x4845,0x63],(name,v)
   expected=background if ident else [0x45]*8
   assert v[10:]==expected,(name,v[10:],expected)
   results.append(dict(background_id=ident,iff=iff,passed=True))
 (out/'restore_validation.json').write_text(json.dumps(results,indent=2));print('4 dirty-restore CPU cases pass: empty/retained palettes, conditional branch, stack, registers, flags, IRQ state and untouched collision ID.')
if __name__=='__main__':main()
