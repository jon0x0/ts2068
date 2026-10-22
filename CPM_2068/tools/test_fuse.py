"""Boot the real DCK in Fuse and read its transcript at keyboard wait."""
import argparse,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--fuse',required=True);p.add_argument('--command');p.add_argument('--expect',default='HELLO from a .COM');a=p.parse_args()
root=Path(__file__).resolve().parents[1]
symbols=(root/'build/bios.bin.sym').read_text()
conin=int(re.search(r'^conin: EQU 0x([0-9A-Fa-f]+)',symbols,re.M)[1],16)
prefix='';number=1
if a.command:
    command=a.command.upper().encode('ascii');assert len(command)<=127
    start=int(re.search(r'^start_ccp: EQU 0x([0-9A-Fa-f]+)',symbols,re.M)[1],16)
    prefix=f'tbreak 0x{start:x}\nbreakpoint 0x{conin:x}\ncommands 1\n'+''.join(f'set 0x{0xd007+i:x} {v}\n' for i,v in enumerate(bytes([len(command)])+command))+'continue\nend\n'
    number=2
else:
    prefix=f'breakpoint 0x{conin:x}\n'
commands=prefix+f'commands {number}\n'+''.join(f'print [0x{i:x}]\n' for i in range(0xf800,0xfe00))+'exit\nend'
result=subprocess.run([a.fuse,'--machine','ts2068','--no-sound','--speed','5000','--debugger-command',commands,'--dock',str(root/'build/ts2068-cpm.dck')],capture_output=True,text=True,timeout=45)
(root/'build/fuse-log.txt').write_text(result.stdout+result.stderr)
assert result.returncode==0,(result.returncode,result.stderr)
values=re.findall(r'^0x([0-9a-f]+)\s*$',result.stdout,re.M)
transcript=bytes(int(v,16) for v in values).replace(b'\0',b'')
assert a.expect.encode('ascii') in transcript,transcript
assert b'A>' in transcript,transcript
(root/'build/fuse-transcript.txt').write_bytes(transcript)
print(transcript.decode('ascii'));print('Fuse cartridge / command / prompt PASS')
