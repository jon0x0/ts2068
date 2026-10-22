"""Convert public-domain font8x8 basic Latin to the console's MSB-first rows."""
from pathlib import Path
import re

def font_bytes():
    text=(Path(__file__).resolve().parents[1]/'third_party/font8x8/font8x8_basic.h').read_text()
    rows=re.findall(r'\{\s*((?:0x[0-9A-Fa-f]{2}\s*,?\s*){8})\}',text)
    if len(rows)!=128:
        raise ValueError('unexpected font8x8 source')
    data=bytes(int(f'{int(v,16):08b}'[::-1],2) for row in rows[32:128] for v in re.findall(r'0x[0-9A-Fa-f]{2}',row))
    assert len(data)==768
    return data
