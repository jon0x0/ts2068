"""Compare actual r5 repair hooks with displaced original instructions."""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/diagnostics/performance';results=[]
 for ident in (0,1):
  for dirty in (0,1):
   for iff in (0,1):
    samples=[]
    for patched in (False,True):
     lines=['breakpoint 0x8634','breakpoint 0x88cd','commands 1','set z80:iff1 0','set z80:iff2 0','out 244 11','set 0x3ff0 2','set 0x5945 0xc5',f'set 0x7f45 {ident}',f'set 0x8245 {dirty}']
     if not patched:lines+=['set 0x8886 0x7c','set 0x8887 0xc6','set 0x8888 0x20','set 0x88bc 0xaf','set 0x88bd 0x77','set 0x88be 0x24']
     lines+=['out 244 7']
     for y in range(8):lines += [f'set {0x4845+y*256} {y+65}',f'set {0x6845+y*256} 0x2f']
     lines+=['out 244 9']
     for y in range(8):lines += [f'set {0x4845+y*256} 0xaa',f'set {0x6845+y*256} {y*17}']
     lines+= [f'set z80:af {ident*256}','set z80:bc 0x1234','set z80:de 0x7f45','set z80:hl 0x4845','set z80:ix 0x4567','set z80:iy 0x6789','set z80:sp 0xe000',f'set z80:iff1 {iff}',f'set z80:iff2 {iff}','set z80:pc 0x8881','continue','end','commands 2']
     lines += [f'print z80:{r}' for r in ('af','bc','de','hl','ix','iy','sp','iff1')]+['print [0x7f45]','print [0x8245]']+[f'print [{0x4845+y*256}]' for y in range(8)]+['out 244 1']+[f'print [{0x6845+y*256}]' for y in range(8)]+['exit','end','breakpoint time 100 if spectrum:frames == 2000','commands 3','exit 1','end']
     program='\n'.join(lines);name=f'hook_{ident}_{dirty}_{iff}_{int(patched)}';(out/(name+'.commands')).write_text(program)
     si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
     p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=20,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
     (out/(name+'.log')).write_text(p.stdout+p.stderr)
     v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)];assert p.returncode==0 and len(v)==26,(name,v,p.stderr);samples.append(v)
    assert samples[0][:18]==samples[1][:18],(ident,dirty,iff,samples)
    expected=list(range(65,73)) if ident else [0x45]*8 if dirty else [0x2f]*8
    assert samples[1][18:]==expected,(ident,dirty,iff,samples[1][18:],expected)
    results.append(dict(id=ident,dirty=dirty,iff=iff,passed=True))
 (out/'hook_validation.json').write_text(json.dumps(results,indent=2));print('8 original-versus-r5 repair cases pass; registers, bitmap and dirty markers identical; clean colours untouched.')
if __name__=='__main__':main()
