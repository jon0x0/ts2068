"""Establish an unmodified Spectrum source baseline without desktop input."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import zipfile

import numpy as np
from PIL import Image
from build_graphics import ROOT,PALETTE,screen_offset,sha


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--frame',type=int,default=8000)
    ap.add_argument('--fuse',type=Path,default=Path('C:/Program Files (x86)/Fuse/fuse.exe'))
    ap.add_argument('--machine',choices=('48','128'),default='48')
    ap.add_argument('--press-start',action='store_true',help='inject Space at the observed original keyboard scanner after frame8100')
    args=ap.parse_args()
    out=ROOT/'build/spectrum_baseline';out.mkdir(exist_ok=True)
    if args.machine=='48':
        source=ROOT/'spectrum/R-Type (1988)(Electric Dreams Software).zip'
    else:
        source=next((ROOT/'spectrum').glob('*128K*.zip'))
    with zipfile.ZipFile(source) as z:
        name=z.namelist()[0];data=z.read(name)
    media=out/('reference.tap' if args.machine=='48' else 'torasoft128.tzx');media.write_bytes(data)
    prefix=f'spectrum{args.machine}_frame{args.frame}' + ('_started' if args.press_start else '')
    captured=bytearray();logs=[];registers=[]
    startup=None;flags=0
    if hasattr(subprocess,'STARTUPINFO'):
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;flags=subprocess.CREATE_NO_WINDOW
    for offset in range(0,6912,1024):
        count=min(1024,6912-offset)
        if args.press_start:
            if args.machine!='48':raise SystemExit('Start injection is verified only for original 48K source')
            lines=['breakpoint 0xbf5d if spectrum:frames >= 8100 && spectrum:frames < 8130 && z80:bc == 0x7ffe',
                   f'breakpoint time 100 if spectrum:frames == {args.frame}',
                   'commands 1','set z80:af 0xfe00 + (z80:af & 255)','continue','end','commands 2']
        else:
            lines=[f'breakpoint time 100 if spectrum:frames == {args.frame}','commands 1']
        lines += [f'print [{0x4000+offset+i}]' for i in range(count)]
        lines += [f'print z80:{r}' for r in ('pc','sp','af','bc','de','hl','i','im')]
        lines += ['exit','end']
        result=subprocess.run([str(args.fuse),'--machine',args.machine,'--tape',str(media),'--auto-load',
            '--speed','5000','--no-sound','--no-loading-sound','--debugger-command','\n'.join(lines)],
            capture_output=True,text=True,timeout=50,startupinfo=startup,creationflags=flags)
        values=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',result.stdout,re.M)]
        if result.returncode or len(values)!=count+8:raise SystemExit(result.stdout+result.stderr)
        captured.extend(values[:count]);registers=values[count:];logs.append(result.stdout+result.stderr)
    pixels=np.zeros((192,256,3),dtype=np.uint8)
    for y in range(192):
        for x in range(256):
            at=screen_offset(y)+x//8;a=captured[6144+(y//8)*32+x//8]
            bit=bool(captured[at]&(128>>(x&7)))
            if a&128 and (args.frame//16)&1:bit=not bit
            color=(a&7) if bit else ((a>>3)&7)
            pixels[y,x]=PALETTE[color+(8 if a&64 else 0)]
    (out/f'{prefix}.scr').write_bytes(captured)
    Image.fromarray(pixels).save(out/f'{prefix}.png')
    (out/f'{prefix}.log').write_text('\n'.join(logs))
    (out/f'{prefix}.json').write_text(json.dumps(dict(machine=args.machine,frame=args.frame,
        source=str(source.relative_to(ROOT)),media_sha256=sha(data),screen_sha256=sha(captured),
        registers=dict(zip(('pc','sp','af','bc','de','hl','i','im'),registers)),
        limitation='Unmodified source running on Spectrum model, not a native TS2068 port'),indent=2))
    print(prefix,dict(zip(('pc','sp','af','bc','de','hl','i','im'),registers)))


if __name__=='__main__':main()
