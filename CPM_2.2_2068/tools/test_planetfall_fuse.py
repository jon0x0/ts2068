"""Boot Planetfall, enter LOOK through the BIOS FIFO, and capture its screen."""
import argparse
from pathlib import Path
import re
import subprocess
from test_oliger_fuse import ROOT, symbol

def main():
    p=argparse.ArgumentParser();p.add_argument('--fuse',type=Path,required=True)
    p.add_argument('--save-restore',action='store_true')
    p.add_argument('--image',type=Path,default=ROOT/'build/planetfall-cpm.dsk')
    p.add_argument('--game',choices=['PLANET','ZORK1'],default='PLANET')
    a=p.parse_args()
    input_bytes=b'SAVE\r\r\rRESTORE\r\r\r' if a.save_restore else b'LOOK\r'
    symbols=(ROOT/f'build/planetfall/{a.game}.COM.sym').read_text()
    cin=int(re.search(r'^CIN1: EQU 0x([0-9a-f]+)',symbols,re.I|re.M)[1],16)
    readb1=int(re.search(r'^READB1: EQU 0x([0-9a-f]+)',symbols,re.I|re.M)[1],16)
    caller=f'([z80:sp+6] | ([z80:sp+7] << 8)) == {readb1+3}'
    empty=f'[0x{symbol("qhead"):x}] == [0x{symbol("qtail"):x}]'
    commands=f'set $phase 1\nset $next 0\ntbreak 0x{symbol("start_ccp"):x}\n'
    commands+=f'breakpoint 0x{cin:x} if $phase == 1 && [0x103] == 63\n'
    commands+=f'breakpoint 0x{cin:x} if $phase == 2 && $next < {len(input_bytes)} && {empty}\n'
    commands+=f'breakpoint 0x{symbol("conin"):x} if $phase == 2 && $next < {len(input_bytes)} && {empty}\n'
    commands+=f'breakpoint 0x{cin:x} if $phase == 2 && $next == {len(input_bytes)} && {empty} && {caller}\n'
    command=a.game.encode('ascii')
    commands+='commands 1\n'+''.join(f'set 0x{0xd007+i:x} {v}\n' for i,v in enumerate(bytes([len(command)])+command+b'\0'))+'continue\nend\n'
    dump=''.join(f'print [0x{i:x}]\n' for i in range(0xf800,0xfe00))
    commands+='commands 2\n'+dump
    commands+=''.join(f'set 0x{0xf750+i:x} {v}\n' for i,v in enumerate(input_bytes))
    commands+='set $phase 2\ncontinue\nend\n'
    feed=f'set 0x{symbol("keyqueue"):x} [0xf750+$next]\nset 0x{symbol("qtail"):x} 0\nset 0x{symbol("qhead"):x} 1\nset $next $next+1\ncontinue\nend\n'
    commands+='commands 3\n'+feed+'commands 4\n'+feed
    commands+='breakpoint 0xf700 if $addr < 30720\nbreakpoint 0xf700 if $addr == 30720\n'
    commands+='commands 5\n'+dump+'print 65534\nout 244 3\nset $addr 16384\nset 63232 0\nset 63233 195\nset 63234 0\nset 63235 247\nset z80:pc 63232\ncontinue\nend\n'
    commands+='commands 6\nprint [$addr]\nset $addr $addr+1\ncontinue\nend\ncommands 7\nexit\nend\n'
    commands+='breakpoint time 1000000000\ncommands 8\nprint z80:pc\n'+dump+'exit 1\nend\n'
    roms=ROOT.parent.parent/'TSRun/roms'
    args=[str(a.fuse.resolve()),'--machine','ts2068','--no-sound','--speed','5000','--jlo',
          '--rom-jlo',str(ROOT/'build/analysis/fuse-jlo-source/roms/safe265.rom'),
          '--rom-ts2068-0',str(roms/'ts2068-0.rom'),'--rom-ts2068-1',str(roms/'ts2068-1.rom'),
          '--drive-jlo1-type','Double-sided 40 track','--disk-try-merge','Never',
          '--jlo0disk',str(a.image.resolve()),'--dock',str(a.image.resolve().with_suffix('.dck')),
          '--debugger-command',commands]
    (ROOT/'build/planetfall-debugger.txt').write_text(commands)
    result=subprocess.run(args,capture_output=True,text=True,timeout=90)
    (ROOT/('build/planetfall-save-fuse.log' if a.save_restore else 'build/planetfall-fuse.log')).write_text(result.stdout+result.stderr)
    before,separator,after=result.stdout.partition('0xfffe\n')
    values=re.findall(r'^0x([0-9a-f]+)\s*$',before,re.M)
    transcript=bytes(int(v,16)&255 for v in values).replace(b'\0',b'')
    (ROOT/('build/planetfall-save-transcript.txt' if a.save_restore else 'build/planetfall-transcript.txt')).write_bytes(transcript)
    print(transcript.decode('ascii',errors='replace'))
    assert result.returncode==0,(result.returncode,result.stderr)
    assert separator,'game did not reach its second input prompt'
    assert (b'PLANETFALL' if a.game=='PLANET' else b'ZORK I') in transcript,transcript
    if not a.save_restore: assert b'>LOOK' in transcript,transcript
    values=bytes(int(v,16) for v in re.findall(r'^0x([0-9a-f]+)\s*$',after,re.M))
    assert len(values)==14336,len(values)
    ram=bytearray(65536);ram[0x4000:0x7800]=values
    (ROOT/('build/planetfall-save-screen.bin' if a.save_restore else 'build/planetfall-screen.bin')).write_bytes(ram)
    if a.save_restore:
        assert b'RESTORE' in transcript and transcript.count(b'Ok.')>=2,transcript
    print('Planetfall boot / '+('SAVE + RESTORE / ' if a.save_restore else 'LOOK / ')+'screen capture PASS')

if __name__=='__main__':main()
