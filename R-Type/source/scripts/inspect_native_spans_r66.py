from pathlib import Path
import sys
sys.path.insert(0,str(Path('../elite/tmp/pydeps').resolve()));from z80dis.z80 import decode,disasm
m=bytes(0x4000)+Path('build/fullgame/foundation/level02.raw').read_bytes();a=0xff7a
while a<0xfff0:
 d=decode(m[a:a+4],a);print(hex(a),disasm(d));a+=d.len or 1
