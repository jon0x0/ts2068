"""Generate diagnostic data planes and previews; this does not build firmware.

Run: python scripts/generate_design_assets.py
Pillow is used only for host previews. All target planes are raw TS2068 bytes.
"""
from pathlib import Path
import colorsys
import hashlib
import json
import math
import zlib
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'video'
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = {}


def offset(xbyte, y):
    return ((y & 192) << 5) | ((y & 7) << 8) | ((y & 56) << 2) | xbyte


def color(code, bright=0):
    level = 255 if bright else 205
    return (level if code & 2 else 0, level if code & 4 else 0,
            level if code & 1 else 0)


def save(name, data, address, mode):
    data = bytes(data)
    expected_length = 768 if mode in (0, 1) and 'attributes' in name else 6144
    assert len(data) == expected_length, (name, len(data), expected_length)
    (OUT / name).write_bytes(data)
    MANIFEST[name] = dict(bytes=len(data), load_address=f'{address:04X}',
                          mode=mode, sha256=hashlib.sha256(data).hexdigest())


def standard_render(pixels, attrs, flash=False, ignore_bright=False):
    im = Image.new('RGB', (256, 192))
    for y in range(192):
        for xb in range(32):
            a = attrs[(y // 8) * 32 + xb]
            ink, paper = a & 7, (a >> 3) & 7
            if flash and a & 128:
                ink, paper = paper, ink
            b = pixels[offset(xb, y)]
            for bit in range(8):
                im.putpixel((xb * 8 + bit, y), color(ink if b & (128 >> bit) else paper, 0 if ignore_bright else (a >> 6) & 1))
    return im


def standard_card(secondary=False):
    pix, attrs = bytearray(6144), bytearray(768)
    for y in range(192):
        for xb in range(32):
            # Bit lanes, opposite diagonals and a full frame exercise addressing.
            x = xb * 8
            b = 0
            for bit in range(8):
                px = x + bit
                on = y in (0, 191) or px in (0, 255)
                if y < 96:
                    on |= (px + (y if secondary else -y)) % 24 < 8
                elif y < 160:
                    on |= (px % 8) == (y // 8) % 8
                else:
                    on |= (px // 4 + y // 4) % 2 == 0
                if on:
                    b |= 128 >> bit
            pix[offset(xb, y)] = b
    for cy in range(24):
        for xb in range(32):
            c = xb // 4
            if secondary:
                c = 7 - c
            # Upper/lower bar pairs; lower band is a flash test with visible contrast.
            attrs[cy * 32 + xb] = c | (((c ^ 7) if cy >= 20 else 0) << 3) | (64 if 6 <= cy < 12 or 16 <= cy < 20 else 0) | (128 if cy >= 20 else 0)
    return pix, attrs


def colorbar_card():
    """Solid PAPER bars: normal top, BRIGHT bottom; FLASH disabled.

    Fixed order black, blue, red, magenta, green, cyan, yellow, white.
    Monochrome label bands identify the halves even without BRIGHT output.
    Each corresponding attribute pair differs only by D6 (BRIGHT).
    """
    pix, attrs = bytearray(6144), bytearray(768)
    for cy in range(24):
        for xb in range(32):
            attrs[cy * 32 + xb] = ((xb // 4) << 3) | (64 if cy >= 12 else 0)
    # Original compact 3x5 font, drawn into target bitmap (not preview overlays).
    font = dict(zip('NORMALBGIHT=01', [
        '101111111111101', '111101101101111', '110101110101101',
        '101111111101101', '010101111101101', '100100100100111',
        '110101110101110', '111100101101111', '111010010010111',
        '101101111101101', '111010010010010', '000111000111000',
        '111101101101111', '010110010010111']))
    for cy, label in ((0, 'NORMAL'), (12, 'BRIGHT')):
        for row in (cy, cy + 1):
            attrs[row*32:(row+1)*32] = bytes([7 | (64 if cy else 0)])*32
        xstart = (256 - len(label)*8)//2
        for i, ch in enumerate(label):
            if ch == ' ':
                continue
            for y in range(5):
                for x in range(3):
                    if font[ch][y*3+x] == '1':
                        for dy in range(2):
                            for dx in range(2):
                                px, py = xstart+i*8+x*2+dx, cy*8+3+y*2+dy
                                pix[offset(px//8,py)] |= 128 >> (px & 7)
    assert not any(a & 128 for a in attrs)
    assert all(attrs[i + 384] == (attrs[i] ^ 64) for i in range(384))
    assert {a >> 3 & 7 for a in attrs} == set(range(8))
    return pix, attrs


def ecm_card():
    """Original gradient/disc; Sierra Filter Lite diffusion, constrained 8x1 pairs.

    Frankie Sierra's kernel: right 1/2, below-left 1/4, below 1/4.
    Reference: ImageSharp's preserved DHALF.TXT and Tanner Helland's diagrams.
    Palette-pair selection and TS2068 packing are original project code.
    """
    pix, attrs = bytearray(6144), bytearray(6144)
    pairs = [(bright,a,b,color(a,bright),color(b,bright))
             for bright in (0,1) for a in range(8) for b in range(a,8)]
    def target(x,y):
        u=(x/255+y/175)/2
        rgb=colorsys.hsv_to_rgb((.68-.85*u)%1,.96,.35+.65*u)
        dx,dy=x-171,y-86
        radius=math.hypot(dx,dy)
        if radius<=70:
            rgb=colorsys.hsv_to_rgb((math.atan2(dy,dx)/(2*math.pi))%1,min(1,radius/70),1)
        return [v*255 for v in rgb]
    errors=[[[0.0]*3 for x in range(256)] for y in range(177)]
    im=Image.new('RGB',(256,192))
    for y in range(192):
        for xb in range(32):
            at=offset(xb,y)
            if y>=176:
                c=xb//4; bright=int(y>=184)
                attrs[at]=c|(c<<3)|(bright<<6)
                for bit in range(8):im.putpixel((xb*8+bit,y),color(c,bright))
                continue
            values=[[target(xb*8+bit,y)[k]+errors[y][xb*8+bit][k] for k in range(3)] for bit in range(8)]
            # Choose a legal pair for the whole strip; then diffuse per-pixel error.
            def score(pair):
                return sum(min(sum((v[k]-pair[3][k])**2 for k in range(3)),
                               sum((v[k]-pair[4][k])**2 for k in range(3))) for v in values)
            bright,paper,ink,ca,cb=min(pairs,key=score)
            attrs[at]=ink|(paper<<3)|(bright<<6)
            for bit in range(8):
                x=xb*8+bit
                v=[target(x,y)[k]+errors[y][x][k] for k in range(3)]
                use_ink=sum((v[k]-cb[k])**2 for k in range(3))<sum((v[k]-ca[k])**2 for k in range(3))
                chosen=cb if use_ink else ca
                if use_ink:pix[at]|=128>>bit
                im.putpixel((x,y),chosen)
                error=[v[k]-chosen[k] for k in range(3)]
                for nx,ny,weight in [(x+1,y,.5),(x-1,y+1,.25),(x,y+1,.25)]:
                    if 0<=nx<256 and ny<176:
                        for k in range(3):errors[ny][nx][k]+=error[k]*weight
    # Verify each rendered pixel against the actual legal packed planes.
    for y in range(192):
        for x in range(256):
            at=offset(x//8,y);a=attrs[at]
            code=(a&7) if pix[at]&(128>>(x&7)) else (a>>3)&7
            assert im.getpixel((x,y))==color(code,(a>>6)&1)
    return pix,attrs,im


def hires_card():
    planes = [bytearray(6144), bytearray(6144)]
    im = Image.new('RGB', (512, 192), 'white')
    for y in range(192):
        for x in range(512):
            # Pixel aspect is 1:2 for a nominal 4:3 display.
            radius = math.hypot((x - 255.5) / 2, y - 95.5)
            on = (x in (0, 511, 255, 256) or y in (0, 191, 95, 96)
                  or x % 64 == 0 or y % 24 == 0 or abs(radius - 62) < .45
                  or abs((x / 2) - y * 4 / 3) < .45)
            if 144 <= y < 184 and 16 <= x < 496:
                panel = min(3, (x - 16) // 120)
                on = ((x - 16) // (1 << panel)) % 2 == 0
            if 8 <= y < 16:
                on = ((x // 8) & 1) == 0  # identify the first file's byte groups
            if 176 <= y < 184 and 16 <= x < 128:
                on = ((x // 8) & 1) == 1  # identify the second file
            if on:
                plane = (x // 8) & 1
                xb = x // 16
                planes[plane][offset(xb, y)] |= 128 >> (x & 7)
                im.putpixel((x, y), (0, 0, 0))
    # Independently reconstruct the packed planes, checking interleaving.
    for y in range(192):
        for x in range(512):
            b = planes[(x // 8) & 1][offset(x // 16, y)]
            assert bool(b & (128 >> (x & 7))) == (im.getpixel((x, y)) == (0, 0, 0))
    return planes, im


def attribute_128_card():
    """Independent overview inspired by Mark Miller's 128 Colors demo.

    Credit: https://www.timexsinclair.com/computer_media/128-colors/index.html
    Sixteen columns: eight inks, each normal/bright. Eight rows: paper 0..7.
    Each swatch is 16x24 pixels; all attributes 00..7F appear exactly six times.
    The original BASIC listing is not copied into this generator or firmware.
    """
    pix, attrs = bytearray(6144), bytearray(768)
    for y in range(192):
        for xb in range(32):
            pix[offset(xb, y)] = 0x55 if y % 2 == 0 else 0xAA
    for cy in range(24):
        paper = cy // 3
        for cx in range(32):
            swatch = cx // 2
            ink, bright = swatch // 2, swatch % 2
            attrs[cy*32+cx] = (bright << 6) | (paper << 3) | ink
    assert set(attrs) == set(range(128))
    assert all(attrs.count(a) == 6 for a in range(128))
    return pix, attrs


def main():
    addresses = {offset(xb, y) for y in range(192) for xb in range(32)}
    assert addresses == set(range(6144)), 'pixel address map must be bijective'
    previews = []
    for secondary in (False, True):
        pix, attrs = standard_card(secondary)
        name = 'secondary' if secondary else 'standard'
        base = 0x6000 if secondary else 0x4000
        save(name + '-pixels.bin', pix, base, int(secondary))
        save(name + '-attributes.bin', attrs, base + 0x1800, int(secondary))
        im = standard_render(pix, attrs)
        im.save(OUT / (name + '.png'))
        previews.append((name.title() + ' color bright and flash card', im))
        if not secondary:
            standard_render(pix, attrs, True).save(OUT / 'standard-flash-phase.png')
    pix, attrs, im = ecm_card()
    save('ecm-pixels.bin', pix, 0x4000, 2)
    save('ecm-attributes.bin', attrs, 0x6000, 2)
    assert not any(a & 128 for a in attrs)
    assert {a & 7 for a in attrs} == set(range(8))
    im.save(OUT / 'ecm-rainbow.png')
    previews.append(('ECM Sierra Lite gradient and color disc', im))
    planes, im = hires_card()
    save('hires-primary.bin', planes[0], 0x4000, 6)
    save('hires-secondary.bin', planes[1], 0x6000, 6)
    im.save(OUT / 'hires-calibration.png')
    previews.append(('512 by 192 calibration and plane ordering', im))
    montage = Image.new('RGB', (1088, 888), '#182126')
    draw = ImageDraw.Draw(montage)
    for i, (label, im) in enumerate(previews):
        x, y = 20 + (i % 2) * 544, 24 + (i // 2) * 432
        draw.text((x, y), label, fill='white')
        montage.paste(im.resize((512, 384), Image.Resampling.NEAREST), (x, y + 24))
    montage.save(OUT / 'testcard-overview.png')
    pix, attrs = attribute_128_card()
    save('attribute-128-pixels.bin', pix, 0x4000, 0)
    save('attribute-128-attributes.bin', attrs, 0x5800, 0)
    standard_render(pix, attrs).save(OUT / 'attribute-128.png')
    pix, attrs = colorbar_card()
    save('colorbar-pixels.bin', pix, 0x4000, 0)
    save('colorbar-attributes.bin', attrs, 0x5800, 0)
    standard_render(pix, attrs).resize((768, 576), Image.Resampling.NEAREST).save(OUT / 'colorbar-bright.png')
    standard_render(pix, attrs, ignore_bright=True).resize((768, 576), Image.Resampling.NEAREST).save(OUT / 'colorbar-no-bright.png')
    (OUT / 'manifest.json').write_text(json.dumps(MANIFEST, indent=2) + '\n')
    # Deterministic host identity records for the actual supplied reference ROMs.
    ref = ROOT.parent / 'David Anderson' / 'TS2068-Ref-Library' / '2068 ROMS'
    identities = []
    for name, role, stock in [('TS2068_U16.BIN', 'HOME', True), ('TS2068_U20.BIN', 'EXROM', True),
                              ('2068Home.BIN', 'HOME', False), ('2068Exrom.BIN', 'EXROM', False)]:
        p = ref / name
        data = p.read_bytes()
        identities.append(dict(file=str(p), role=role, stock=stock, bytes=len(data),
                               crc32=f'{zlib.crc32(data):08X}', sha1=hashlib.sha1(data).hexdigest(),
                               sha256=hashlib.sha256(data).hexdigest()))
    assert zlib.crc32(b'123456789') == 0xCBF43926
    assert identities[0]['crc32'] == 'BF44EC3F'
    assert identities[1]['crc32'] == 'AE16233A'
    (ROOT / 'docs' / 'rom-identities.json').write_text(json.dumps(identities, indent=2) + '\n')
    print('Verified pixel addressing, plane lengths, hires interleave, ECM palette and stock ROM identities.')
    print('Generated', len(MANIFEST), 'target planes, including the credited 128-attribute card, in', OUT)


if __name__ == '__main__':
    main()
