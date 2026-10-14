"""Finish the sparse DCK and exact 64KB physical image after launcher assembly."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
from dck_format import build_dck, parse_dck, flat_image

ap = argparse.ArgumentParser()
ap.add_argument('output',type=Path)
args = ap.parse_args()
out=args.output
manifest=json.loads((out/'manifest.json').read_text())
variant=manifest.get('runtime_variant','cartridge')
main=(ROOT/'build'/variant/'v2_home.bin').read_bytes()
service=(ROOT/'build'/variant/'v2_exrom.bin').read_bytes()
chunks={0:main[:8192],1:main[8192:],3:(out/'bytecode-chunk.bin').read_bytes(),
        4:(out/'launcher.bin').read_bytes(),6:service}
if manifest['bytecode_base']==0x4000: chunks[2]=(out/'bytecode-low.bin').read_bytes()
for index in (5,7):
    if manifest.get('packed_asset_bytes',0)>(6992 if index==5 else 15184): chunks[index]=(out/f'assets-{index}.bin').read_bytes()
descriptors=[2 if i in chunks else 0 for i in range(8)]
data=build_dck(descriptors,chunks)
physical=flat_image(parse_dck(data))
assert len(physical)==65536
(out/'program.dck').write_bytes(data)
(out/'program.bin').write_bytes(physical)
manifest['status']='assembled prototype; see execution.json for runtime verification'
manifest['sha256']={name:hashlib.sha256((out/name).read_bytes()).hexdigest()
                    for name in ('program.dck','program.bin','program.lbc')}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Packed DOCK chunks {",".join(str(i) for i in sorted(chunks))}; 64KB physical image verified')
