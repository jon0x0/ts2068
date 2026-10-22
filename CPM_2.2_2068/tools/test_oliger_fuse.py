"""Run CP/M against the actual JLO/WD1770 implementation in a newer Fuse build."""
import argparse
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def symbol(name):
    text=(ROOT/'build/bios.bin.sym').read_text()
    return int(re.search(r'^'+name+r': EQU 0x([0-9A-Fa-f]+)',text,re.M)[1],16)

def run(fuse, command, expected, image, label):
    command=command.encode('ascii')
    prefix=f'tbreak 0x{symbol("start_ccp"):x}\nbreakpoint 0x{symbol("conin"):x}\n'
    prefix+='commands 1\n'+''.join(f'set 0x{0xd007+i:x} {v}\n' for i,v in enumerate(bytes([len(command)])+command+b'\0'))+'continue\nend\n'
    dump=''.join(f'print [0x{i:x}]\n' for i in range(0xf800,0xfe00))
    commands=prefix+'commands 2\n'+dump+'exit\nend\n'
    commands+='breakpoint time 500000000\ncommands 3\nprint z80:pc\n'+dump+'exit 1\nend\n'
    roms=ROOT.parent.parent/'TSRun/roms'
    args=[str(fuse),'--machine','ts2068','--no-sound','--speed','5000',
          '--jlo','--rom-jlo',str(ROOT/'build/analysis/fuse-jlo-source/roms/safe265.rom'),
          '--rom-ts2068-0',str(roms/'ts2068-0.rom'),'--rom-ts2068-1',str(roms/'ts2068-1.rom'),
          '--drive-jlo1-type','Double-sided 40 track' if image is not None and image.read_bytes()[49]==2 else 'Single-sided 40 track','--disk-try-merge','Never',
          '--dock',str(ROOT/'build/ts2068-cpm.dck'),
          '--debugger-command',commands]
    if image is not None:
        args += ['--jlo0disk',str(image)]
    result=subprocess.run(args,capture_output=True,text=True,timeout=90)
    (ROOT/f'build/oliger-{label}.log').write_text(result.stdout+result.stderr)
    values=re.findall(r'^0x([0-9a-f]+)\s*$',result.stdout,re.M)
    transcript=bytes(int(v,16)&255 for v in values).replace(b'\0',b'')
    (ROOT/f'build/oliger-{label}.txt').write_bytes(transcript)
    assert result.returncode==0,(result.returncode,result.stderr,transcript)
    assert expected.encode() in transcript,transcript
    if image is not None:
        assert b'A>' in transcript,transcript
    print(transcript.decode('ascii',errors='replace'))
    return transcript

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fuse',type=Path,required=True)
    p.add_argument('--command',default='DIR');p.add_argument('--expect',default='PIP')
    p.add_argument('--label',default='boot');p.add_argument('--image',type=Path,default=ROOT/'build/oliger-cpm.dsk')
    p.add_argument('--no-disk',action='store_true')
    a=p.parse_args()
    run(a.fuse.resolve(),a.command,a.expect,None if a.no_disk else a.image.resolve(),a.label)
    print('Actual Fuse JLO controller / CP/M command PASS')
