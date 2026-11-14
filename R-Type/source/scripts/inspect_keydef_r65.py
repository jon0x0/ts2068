from pathlib import Path
import sys
sys.path.insert(0,str(Path('../elite/tmp/pydeps').resolve()));from z80dis.z80 import decode,disasm
b=Path('build/fullgame/native_fit_r64/boot_region.bin').read_bytes();m=bytearray(65536);m[0x8000:0xc000]=b[0x4000:0x8000];m[0xc000:0x10000]=b[0xa000:0xe000]
for a,z in [(0x87d0,0x8895)]:
 while a<z:
  d=decode(bytes(m[a:a+4]),a);print(hex(a),disasm(d));a+=d.len or 1
