"""Render the integration test's Spectrum-layout screen (requires Pillow)."""
from pathlib import Path
from PIL import Image
import sys

if '--hires' in sys.argv:
    name = 'desktop-512-windows' if '--windows' in sys.argv else 'desktop-512'
    data = Path(f'build/{name}.hires').read_bytes()
    assert len(data) == 12288
    im = Image.new('RGB', (512, 192))
    for y in range(192):
        row = ((y & 192) << 5) | ((y & 7) << 8) | ((y & 56) << 2)
        for x in range(512):
            col = x // 8
            bits = data[(col & 1)*6144 + row + col//2]
            v = 0 if bits & (128 >> (x & 7)) else 205
            im.putpixel((x,y), (v,v,v))
    im.resize((1024,384), Image.Resampling.NEAREST).save(f'build/{name}.png')
    sys.exit(0)

data = Path('build/desktop.scr').read_bytes()
assert len(data) == 6912
im = Image.new('RGB', (256, 192))
for y in range(192):
    row = ((y & 192) << 5) | ((y & 7) << 8) | ((y & 56) << 2)
    for x in range(256):
        attr = data[6144 + (y // 8) * 32 + x // 8]
        pixel = data[row + x // 8] & (128 >> (x & 7))
        color = (attr if pixel else attr >> 3) & 7
        intensity = 255 if attr & 64 else 205
        im.putpixel((x, y), tuple(intensity if color & bit else 0 for bit in (2, 4, 1)))
im.resize((768, 576), Image.Resampling.NEAREST).save('build/desktop.png')
