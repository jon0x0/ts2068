"""Verify generated source-cell phase metadata in actual writable DOCK1."""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/ecm_native';m=bytes(0x4000)+(ROOT/'build/native/snapshot.bin').read_bytes()
 expected=bytearray(b'\xff'*8192);headers=0;nonempty=0
 indices=iter((out/'cache_ids.bin').read_bytes())
 for ident in range(1,112):
  a=0xbc67+(ident-1)*4;w,h=m[a:a+2];ptr=int.from_bytes(m[a+2:a+4],'little')
  for y in range(h):
   for x in range(w):
    assert 0xa000<=ptr<0xbfc0,(ident,hex(ptr))
    expected[ptr-0xa000]=next(indices);headers+=1
    attr=m[ptr];nonempty+=attr!=0x36
    if attr!=0x36 and not attr&0x38:
     for line in range(8):
      if m[ptr+1+line]==255:expected[ptr+1+line-0xa000]=1
    ptr+=1 if attr==0x36 else 9
 (out/'phase_lut_expected.bin').write_bytes(expected)
 lines=['set $p 8192','breakpoint 0x8634','breakpoint 0x4000 if $p < 16320','breakpoint 0x4000 if $p == 16320',
  'commands 1','set z80:iff1 0','set z80:iff2 0','out 244 11','set 0x4000 0xc3','set 0x4001 0','set 0x4002 0x40','set z80:pc 0x4000','continue','end',
  'commands 2','print [$p]+256*[$p+1]','set $p $p+2','continue','end','commands 3','exit','end']
 program='\n'.join(lines);(out/'phase_cpu.commands').write_text(program)
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(out/'RType_level1_ECM_TSPico_RAM.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=25,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/'phase_cpu.log').write_text(p.stdout+p.stderr)
 v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
 actual=b''.join(x.to_bytes(2,'little') for x in v)
 assert p.returncode==0 and actual==expected[:8128],(p.returncode,len(actual))
 (out/'phase_lut_actual.bin').write_bytes(actual)
 (out/'phase_validation.json').write_text(json.dumps(dict(headers=headers,nonempty_cells=nonempty,bytes_checked=8128,passed=True,reserved_tail='Last64 bytes are owned bootstrap stack/mode shadow, not sprite headers'),indent=2))
 print('Phase table matches actual DOCK1:',headers,'headers',nonempty,'nonempty cells;',len(actual),'bytes checked.')
if __name__=='__main__':main()
