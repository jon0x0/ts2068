"""Capture actual 2019 R-Type release menu in Fuse Pentagon/TR-DOS."""
from pathlib import Path
import argparse,subprocess,re,json
from build_graphics import unpack,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/research/goodboy2019'
 for bank,entry in ((3,0x6008),(7,0x85fd)):
  stem=f'player_bank{bank}'
  program=(out/'pentagon_4000.commands').read_text()
  program=program.replace('set $p 16384','set $p 49152').replace('breakpoint time 100 if spectrum:frames == 4000',f'breakpoint {entry}').replace('$p < 23296','$p < 65536').replace('$p == 23296','$p == 65536')
  program=program.replace('set z80:iff1 0',f'out 32765 {16+bank}\nset z80:iff1 0')
  program+='\nbreakpoint 0x606d if spectrum:frames >= 4200 && spectrum:frames < 4220\ncommands 11\nset z80:af 0xfe00 + (z80:af & 255)\ncontinue\nend'
  (out/(stem+'.commands')).write_text(program)
  startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
  p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','pentagon','--rom-pentagon-0',str(out/'reference_pentagon0.rom'),'--rom-pentagon-1',str(out/'reference_pentagon1.rom'),'--rom-pentagon-2',str(out/'reference_pentagon_trdos.rom'),'--auto-load','--speed','5000','--no-sound','--debugger-command',program,str(out/'RTYPE_GT.SCL')],capture_output=True,text=True,timeout=40,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
  (out/(stem+'.log')).write_text(p.stdout+p.stderr)
  v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
  assert p.returncode==0 and len(v)==8200 and v[0]==0xcafe,(p.returncode,len(v),p.stderr)
  (out/(stem+'.bin')).write_bytes(b''.join(x.to_bytes(2,'little') for x in v[8:]))
  print(stem,hex(v[1]))
if __name__=='__main__':main()
