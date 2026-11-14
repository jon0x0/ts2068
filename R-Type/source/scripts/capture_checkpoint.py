"""Capture all 48KB and CPU state at the original post-level-load checkpoint.

After reaching the checkpoint, freeze in a 3-byte screen JP loop to stream RAM
through debugger expressions. Restore those saved 3 bytes in the captured file.
No gameplay state is forced before the checkpoint; only electrical key reads.
"""
import json
from pathlib import Path
import re
import subprocess

from build_graphics import ROOT,sha


def main():
    out=ROOT/'build/spectrum_baseline'
    media=out/'reference.tap'
    if not media.exists():raise SystemExit('Run capture_spectrum.py first')
    regs=('af','bc','de','hl',"af'","bc'","de'","hl'",'ix','iy','sp','pc','i','r','im','iff1','iff2')
    lines=['set $armed 0','set $address 16384',
        'breakpoint 0xbf5d if ((spectrum:frames >= 8100 && spectrum:frames < 8130) || (spectrum:frames >= 14500 && spectrum:frames < 14530)) && z80:bc == 0x7ffe',
        'breakpoint 0x8634 if $armed == 0',
        'breakpoint 0x4000 if $armed == 1 && $address < 65536',
        'breakpoint 0x4000 if $armed == 1 && $address == 65536',
        'breakpoint time 100 if spectrum:frames == 22000',
        'commands 1','set z80:af 0xfe00 + (z80:af & 255)','continue','end',
        'commands 2','print 0xcafe']
    lines += [f'print z80:{r}' for r in regs]
    lines += ['print spectrum:frames','print [0x4000]','print [0x4001]','print [0x4002]',
        'set $armed 1','set z80:iff1 0','set z80:iff2 0',
        'set 0x4000 0xc3','set 0x4001 0','set 0x4002 0x40','set z80:pc 0x4000','continue','end',
        'commands 3','print [$address] + 256*[$address+1]','set $address $address+2','continue','end',
        'commands 4','exit','end',
        'commands 5','print 0xdead','print z80:pc','exit 1','end']
    program='\n'.join(lines)
    (out/'postload_checkpoint.commands').write_text(program)
    startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    result=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','48','--tape',str(media),'--auto-load',
        '--speed','5000','--no-sound','--no-loading-sound','--debugger-command',program],capture_output=True,text=True,
        timeout=65,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
    (out/'postload_checkpoint.log').write_text(result.stdout+result.stderr)
    values=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',result.stdout,re.M)]
    header_count=1+len(regs)+4
    if result.returncode or len(values)!=header_count+24576 or values[0]!=0xcafe:
        raise SystemExit(f'Checkpoint capture failed: exit={result.returncode}, values={len(values)}; inspect log')
    memory=bytearray()
    for word in values[header_count:]:memory.extend(word.to_bytes(2,'little'))
    memory[:3]=bytes(values[header_count-3:header_count])
    cpu=dict(zip(regs,values[1:1+len(regs)]))
    frame=values[1+len(regs)]
    (out/'postload_4000_FFFF.bin').write_bytes(memory)
    (out/'postload_checkpoint.json').write_text(json.dumps(dict(cpu=cpu,frame=frame,memory_sha256=sha(memory),
        source='Original unmodified TAP on Spectrum 48, after level-loader return at $8634',
        capture='Post-checkpoint JP loop at $4000; saved first three bytes restored; interrupts frozen only after state capture'),indent=2))
    print('Original post-level-load checkpoint:',cpu,'frame',frame)


if __name__=='__main__':main()
