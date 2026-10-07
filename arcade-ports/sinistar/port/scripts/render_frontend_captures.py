"""Render native frontend bitmap/ECM captures written by verify_frontend.mjs."""
from pathlib import Path
from PIL import Image

for source in (Path(__file__).resolve().parents[1] / 'build').glob('frontend-*.bin'):
    raw = source.read_bytes()
    if len(raw) != 12288:
        continue
    frame = Image.new('RGB', (256, 192))
    pixels = frame.load()
    for y in range(192):
        for x in range(256):
            offset = ((y & 192) << 5) | ((y & 7) << 8) | ((y & 56) << 2) | (x >> 3)
            attribute = raw[6144 + offset]
            color = (attribute & 7) if raw[offset] & (128 >> (x & 7)) else ((attribute >> 3) & 7)
            level = 255 if attribute & 64 else 192
            pixels[x, y] = tuple(level if color & bit else 0 for bit in (2, 4, 1))
    frame.resize((768, 576), Image.Resampling.NEAREST).save(source.with_suffix('.png'))
