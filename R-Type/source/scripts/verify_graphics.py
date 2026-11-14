"""Verify every graphics-proof page against byte-exact HOME RAM in Fuse."""
import argparse
import json
from pathlib import Path
import re
import subprocess

import numpy as np
from PIL import Image
from build_graphics import unpack, sha, ROOT


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,default=ROOT/'build/graphics')
    ap.add_argument('--fuse',type=Path,default=Path('C:/Program Files (x86)/Fuse/fuse.exe'))
    args=ap.parse_args();out=args.output
    meta=json.loads((out/'proof_manifest.json').read_text())
    dck=(out/'RType_ECM_graphics_proof.dck').read_bytes();raw=(out/'RType_ECM_graphics_proof.bin').read_bytes()
    assert len(raw)==65536 and len(dck)==65545 and dck[:9]==bytes([0]+[2]*8) and dck[9:]==raw
    assert raw[0x8000:0x8008]==bytes.fromhex('02 02 08 80 ef 01 00 00')
    results=[];all_logs=[]
    names=meta.get('names',('ecm_colour_emphasis','ecm_sierra','spectrum_8x8','ecm_ordered','title_ecm_sierra'))
    startup=None;flags=0
    if hasattr(subprocess,'STARTUPINFO'):
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
        flags=subprocess.CREATE_NO_WINDOW
    for number,name in enumerate(names):
        planes=[]
        for base in (0x4000,0x6000):
            data=bytearray()
            for offset in range(0,6144,1024):
                program='\n'.join([f'breakpoint {meta["labels"]["ready"+str(number)]}', 'commands 1']+
                    [f'print [{base+offset+i}]' for i in range(1024)]+['print z80:sp','exit','end'])
                result=subprocess.run([str(args.fuse),'--machine','ts2068','--dock',str(out/'RType_ECM_graphics_proof.dck'),
                    '--speed','5000','--no-sound','--no-loading-sound','--debugger-command',program],
                    capture_output=True,text=True,timeout=35,startupinfo=startup,creationflags=flags)
                values=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',result.stdout,re.M)]
                if result.returncode or len(values)!=1025 or values[-1]!=0x7fff:
                    raise SystemExit(f'Fuse frame {number}, plane {base:x} offset {offset} failed: {result.stdout} {result.stderr}')
                data.extend(values[:-1]);all_logs.append(f'{name} {base:04X}+{offset}: 1024 bytes; SP=7FFF; exit={result.returncode}')
            expected=(out/(name+('.pix' if base==0x4000 else '.atr'))).read_bytes()
            assert data==expected, f'Actual screen plane differs: {name} {base:x}'
            (out/f'fuse_{name}_{base:04x}.bin').write_bytes(data);planes.append(bytes(data))
        image=unpack(*planes);image.save(out/f'fuse_{name}.png')
        assert np.array_equal(np.asarray(image),np.asarray(Image.open(out/f'{name}.png')))
        results.append(dict(name=name,bitmap_sha256=sha(planes[0]),attributes_sha256=sha(planes[1]),
                            ram_match=True,stack=32767))
        print(name,'both live ECM planes match; stack and preview correct',flush=True)
    (out/'fuse_validation.log').write_text('\n'.join(all_logs)+'\n')
    (out/'fuse_validation.json').write_text(json.dumps(dict(machine='TS2068',frames=results,
        dck_sha256=sha(dck),bin_sha256=sha(raw),limitation='Graphics-only slideshow; not a playable game or measured scrolling renderer'),indent=2))


if __name__=='__main__':main()
