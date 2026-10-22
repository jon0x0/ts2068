"""Extract address-correct UF2 payload and printable evidence; no device access."""
import argparse
import hashlib
from pathlib import Path
import re
import struct

p = argparse.ArgumentParser()
p.add_argument('uf2', type=Path)
p.add_argument('--output', type=Path, default=Path('build/analysis'))
a = p.parse_args()
raw = a.uf2.read_bytes()
assert len(raw) % 512 == 0
blocks = []
for i in range(0, len(raw), 512):
    h = struct.unpack_from('<8I', raw, i)
    assert h[:2] == (0x0A324655, 0x9E5D5157)
    assert struct.unpack_from('<I', raw, i + 508)[0] == 0x0AB16F30
    assert h[4] <= 476
    if not h[2] & 1:  # Ignore blocks explicitly not intended for main flash.
        blocks.append((h[3], raw[i + 32:i + 32 + h[4]]))
base = min(addr for addr, _ in blocks)
end = max(addr + len(data) for addr, data in blocks)
image = bytearray(b'\xff' * (end - base))
for addr, data in blocks:
    image[addr - base:addr - base + len(data)] = data
a.output.mkdir(parents=True, exist_ok=True)
(a.output / 'firmware-1.00.bin').write_bytes(image)
(a.output / 'firmware-1.00-strings.txt').write_text('\n'.join(
    f'{base + m.start():08x} {m.group().decode("ascii")}'
    for m in re.finditer(rb'[\x20-\x7e]{4,}', image)) + '\n')
print(f'SHA256 {hashlib.sha256(raw).hexdigest()}')
print(f'Payload {base:08x}..{end:08x}; strings are evidence, not proof of implemented commands.')
