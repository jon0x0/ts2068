"""Validate memory bounds and package a native CODE tape (not Spectrum BASIC)."""
from pathlib import Path
import struct
import sys
from functools import reduce
from operator import xor

root = Path(__file__).resolve().parents[1]
build = root / 'build'
name = sys.argv[1] if len(sys.argv) > 1 else 'zxdesk2068'
syms = {}
for line in (build / (name + '.sym')).read_text().splitlines():
    parts = line.split()
    if len(parts) == 3 and parts[1] == 'EQU':
        syms[parts[0]] = int(parts[2].rstrip('H'), 16)
data = (build / (name + '.bin')).read_bytes()
assert syms['SlowEnd'] <= syms['SLOWTOP'], 'slow code overlaps fast code'
assert syms['FastEnd'] <= syms['STACKTOP'] - 256, 'less than 256 bytes stack headroom'
assert syms['SLOWORG'] >= 0x6c00, 'native BASIC workspace overlap'
assert len(data) == syms['FastEnd'] - syms['SLOWORG']
if syms['SCRCOLS'] == 64:
    assert syms['SLOWORG'] >= 0x7800, 'code overlaps second bitmap'
assert syms['IRQTABLE'] + 257 <= syms['BUFBASE'], 'interrupt table overlaps buffers'

def block(flag, payload):
    b = bytes([flag]) + payload
    b += bytes([reduce(xor, b, 0)])
    return struct.pack('<H', len(b)) + b

header = bytes([3]) + b'ZXDesk2068' + struct.pack('<HHH', len(data), syms['SLOWORG'], 0x8000)
code_tape = block(0, header) + block(255, data)
(build / (name + '-code.tap')).write_bytes(code_tape)
# These ordinary BASIC tokens have the same values in the TS2068 HOME ROM.
# VAL strings avoid encoding floating-point numeric literals in the loader.
line = (b'\xfd\xb0"' + str(syms['SLOWORG'] - 1).encode() + b'":'
        b'\xef""\xaf:\xf9\xc0\xb0"' + str(syms['Main']).encode() + b'"\x0d')
basic = struct.pack('>H', 10) + struct.pack('<H', len(line)) + line
basic_header = bytes([0]) + b'ZXDesk2068' + struct.pack('<HHH', len(basic), 10, len(basic))
(build / (name + '.tap')).write_bytes(block(0, basic_header) + block(255, basic) + code_tape)
print(f"Native CODE TAP: LOAD address ${syms['SLOWORG']:04X}, entry ${syms['Main']:04X}")
print(f"Slow end ${syms['SlowEnd']:04X}; fast end ${syms['FastEnd']:04X}; stack ${syms['STACKTOP']:04X}")

