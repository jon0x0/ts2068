"""Host proof of schematic-aware fault text, not target firmware.

Own 3x5 block font. Each logical column occupies a byte, allowing surviving
pixel bit lanes to convey the same large glyph after a nibble failure.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw
from generate_design_assets import offset, standard_render

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/degraded-display'
FONT = {
 ' ': ['000']*5, 'R':['110','101','110','101','101'],
 'A':['010','101','111','101','101'], 'M':['101','111','111','101','101'],
 'F':['111','100','110','100','100'], 'I':['111','010','010','010','111'],
 'L':['100','100','100','100','111'], 'U':['101','101','101','101','111'],
 'P':['110','101','110','100','100'], 'T':['111','010','010','010','010'],
 'H':['101','101','111','101','101'], 'C':['111','100','100','100','111'],
 'O':['111','101','101','101','111'], 'D':['110','101','101','101','110'],
 'E':['111','100','110','100','111'],
 '0':['111','101','101','101','111'], '1':['010','110','010','010','111'],
 '2':['110','001','010','100','111'], '3':['110','001','010','001','110'],
 '6':['100','100','111','101','111'], '7':['111','001','010','010','010'],
 '8':['111','101','111','101','111']}


def page(chip, chip_code, healthy=255):
    pixels = bytearray(6144)
    # Top: black ink/yellow paper. Bottom: white ink/black paper.
    attrs = bytearray([0x30]*384 + [0x07]*384)
    def text(value, y):
        assert len(value)*4 <= 32
        start = (32-len(value)*4)//2
        for index,ch in enumerate(value):
            for row,line in enumerate(FONT[ch]):
                for col,on in enumerate(line):
                    for dy in range(3):
                        pixels[offset(start+index*4+col, y+row*3+dy)] = healthy if on=='1' else 0
    for base in (0,96):
        text('RAM FAIL',base+8)
        text(chip+' PATH',base+32)
        text('CODE 2 '+str(chip_code),base+56)
    return pixels,attrs


def force(data, mask, stuck):
    return bytes((v & (255 ^ mask)) | (stuck & mask) for v in data)


def attribute_page(chip, chip_code):
    # U6 faulty: known U7 pixels=0 use PAPER, whose high color bits are healthy.
    # U7 faulty: known U6 pixels=1 use INK; also vary PAPER's healthy low bit so
    # a forced FLASH inversion still has color contrast.
    pixels = bytearray([0 if chip=='U6' else 15]*6144)
    attrs = bytearray(768)
    on_attr = 0x30 if chip=='U6' else 0x0F
    for value,row in [('RAM FAIL',1),(chip+' PATH',8),('CODE 2 '+str(chip_code),15)]:
        start=(32-len(value)*4)//2
        for index,ch in enumerate(value):
            for y,line in enumerate(FONT[ch]):
                for x,on in enumerate(line):
                    attrs[(row+y)*32+start+index*4+x]=on_attr if on=='1' else 0
    return pixels,attrs


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cases=[]
    views=[]
    attribute_views=[]
    for chip,mask,code in [('U6',15,1),('U7',240,2)]:
        healthy=255^mask
        pixels,attrs=page(chip,code,healthy)
        (OUT/(chip+'-written-pixels.bin')).write_bytes(pixels)
        (OUT/(chip+'-written-attributes.bin')).write_bytes(attrs)
        # All constant failed-nibble values, not just zero/one extremes.
        for nibble in range(16):
            stuck=nibble if mask==15 else nibble<<4
            actual_pixels=force(pixels,mask,stuck)
            actual_attrs=force(attrs,mask,stuck)
            assert all((a&healthy)==(b&healthy) for a,b in zip(actual_pixels,pixels))
            contrast=[(a&7)!=((a>>3)&7) for a in (actual_attrs[0],actual_attrs[384])]
            assert any(contrast), 'one duplicated panel must retain ink/paper contrast'
            pair=force(bytes([0,0x30 if chip=='U6' else 0x0F]),mask,stuck)
            assert ((pair[0]>>3)&7)!=((pair[1]>>3)&7), 'paper-coded glyph must retain contrast'
            if chip=='U7':
                assert (pair[0]&7)!=(pair[1]&7), 'ink-coded glyph must retain contrast'
            cases.append(dict(chip=chip,forced_nibble=nibble,healthy_mask=healthy,
                              panel_contrast=contrast,healthy_pixels_preserved=True,
                              attribute_font_contrast=True,observed_off_on_attributes=list(pair)))
        for nibble in (0,15):
            stuck=nibble if mask==15 else nibble<<4
            actual_pixels,actual_attrs=force(pixels,mask,stuck),force(attrs,mask,stuck)
            name=f'{chip}-stuck-{nibble:x}'
            im=standard_render(actual_pixels,actual_attrs)
            im.save(OUT/(name+'.png'))
            # Bad U7 can force FLASH on: retain the inverse-phase preview too.
            standard_render(actual_pixels,actual_attrs,True).save(OUT/(name+'-flash-phase.png'))
            views.append((name,im))
            ap,aa=attribute_page(chip,code)
            actual_ap,actual_aa=force(ap,mask,stuck),force(aa,mask,stuck)
            ai=standard_render(actual_ap,actual_aa)
            ai.save(OUT/(name+'-attribute-font.png'))
            standard_render(actual_ap,actual_aa,True).save(OUT/(name+'-attribute-font-flash.png'))
            attribute_views.append((name,ai))
    montage=Image.new('RGB',(1088,888),'#182126');draw=ImageDraw.Draw(montage)
    for n,(label,im) in enumerate(views):
        x,y=20+(n%2)*544,24+(n//2)*432
        draw.text((x,y),label+'  (modeled failure)',fill='white')
        montage.paste(im.resize((512,384),Image.Resampling.NEAREST),(x,y+24))
    montage.save(OUT/'comparison.png')
    montage=Image.new('RGB',(1088,888),'#182126');draw=ImageDraw.Draw(montage)
    for n,(label,im) in enumerate(attribute_views):
        x,y=20+(n%2)*544,24+(n//2)*432
        draw.text((x,y),label+'  (attribute-coded glyphs)',fill='white')
        montage.paste(im.resize((512,384),Image.Resampling.NEAREST),(x,y+24))
    montage.save(OUT/'attribute-comparison.png')
    (OUT/'host-validation.json').write_text(json.dumps(dict(result='PASS',cases=cases,
        scope='Host constant-nibble fault model only; no target renderer implemented',
        limitations=['Arbitrary intermittent faults can corrupt presumed healthy bits',
                     'CPU readback does not prove SCLD display fetch/output',
                     'Glyph readability needs physical/user verification']),indent=2)+'\n')
    print('Checked32 constant-nibble faults: healthy pixel lanes preserved and at least one contrasting panel.')


if __name__=='__main__':
    main()
