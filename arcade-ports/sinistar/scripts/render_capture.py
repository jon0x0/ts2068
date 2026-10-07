from pathlib import Path
from PIL import Image
for p in Path('build/capture').glob('*.ram'):
    b=p.read_bytes();im=Image.new('RGB',(256,192))
    for y in range(192):
        for x in range(256):
            off=((y&192)<<5)+((y&7)<<8)+((y&56)<<2)+x//8
            bits,attr=b[0x4000+off],b[0x6000+off]
            c=(attr&7) if bits&(128>>(x&7)) else ((attr>>3)&7);v=255 if attr&64 else 205
            im.putpixel((x,y),(v*((c>>1)&1),v*((c>>2)&1),v*(c&1)))
    im.resize((768,576),Image.Resampling.NEAREST).save(p.with_suffix('.png'))
