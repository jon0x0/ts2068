"""Split Personality: ECM left, 512-mode right, green/blue split borders."""
from pathlib import Path
import itertools, json, math, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
def row(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)

def artwork():
    # Left side occupies 128 native ECM pixels: half the physical screen.
    y,x=np.mgrid[0:192,0:128]
    rgb=np.zeros((192,128,3),dtype=np.uint8)
    rgb[:]=np.array((0,0,80),dtype=np.uint8)
    dx=(x-63.5)/35;dy=(y-99)/35;inside=dx*dx+dy*dy<=1
    z=np.sqrt(np.maximum(1-dx*dx-dy*dy,0))
    light=np.clip(-.35*dx-.5*dy+.8*z,.05,1)
    rgb[...,0]=np.where(inside,np.clip((.55+.45*dy)*light*255,0,255),0)
    rgb[...,1]=np.where(inside,np.clip((.9-.45*dy)*light*255,0,255),0)
    rgb[...,2]=np.where(inside,np.clip((.6-.5*dx)*light*255,0,255),80)
    # One-scanline attribute stripes make the extended color easy to identify.
    palette=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),
                      (0,205,0),(0,205,205),(205,205,0),(205,205,205),
                      (0,0,0),(0,0,255),(255,0,0),(255,0,255),
                      (0,255,0),(0,255,255),(255,255,0),(255,255,255)],dtype=np.uint8)
    for yy in range(163,189):
        for xx in range(8,120):rgb[yy,xx]=palette[8+1+((yy+xx//8)%7)]
    left=Image.fromarray(rgb);ld=ImageDraw.Draw(left)
    for text,yy,size in [('SPLIT',5,17),('PERSONALITY',25,13),('ECM',48,15),('16 COLORS / 8x1',138,8)]:
        f=ImageFont.truetype(str(FONT),size);b=ld.textbbox((0,0),text,font=f)
        ld.text(((128-(b[2]-b[0]))//2,yy),text,font=f,fill=(255,255,255))
    rgb=np.array(left,dtype=np.float32)
    ram=bytearray(65536)
    pairs=np.array([(bright,a,b) for bright in (0,8)
                    for a,b in itertools.combinations_with_replacement(range(8),2)])
    for yy in range(192):
        for c in range(16):
            cell=rgb[yy,c*8:c*8+8]
            dist=((cell[:,None,:]-palette[None,:,:].astype(float))**2).sum(axis=2)
            err=np.minimum(dist[:,pairs[:,0]+pairs[:,1]],dist[:,pairs[:,0]+pairs[:,2]]).sum(axis=0)
            bright,ink,paper=pairs[int(err.argmin())]
            bits=0
            for b in range(8):
                if dist[b,bright+ink]<dist[b,bright+paper]:bits|=128>>b
            offset=row(yy)+c
            ram[0x4000+offset]=bits
            ram[0x6000+offset]=int(ink|(paper<<3)|(64 if bright else 0))
    # Write the diagnostic bands directly so BRIGHT black is included as
    # palette entry 8, even though it looks identical to ordinary black.
    def solid(c,yy,index):
        offset=row(yy)+c;color=index&7
        ram[0x4000+offset]=0
        ram[0x6000+offset]=color|(color<<3)|(64 if index&8 else 0)
    # 16 swatches across: eight normal entries, then eight BRIGHT entries.
    for yy in range(148,156):
        for c in range(16):solid(c,yy,c)
    # A different palette entry on every one-pixel-high horizontal line.
    for yy in range(158,174):
        for c in range(16):solid(c,yy,yy-158)
    # Separators make individual scanline bands easier to identify.
    for yy in (156,157,174,175):
        for c in range(16):solid(c,yy,0)
    # Native ECM 1x1 checker pixels. Neighboring hues blend spatially;
    # the two-color pair progresses across columns and down scanlines.
    hues=[2,6,4,5,1,3]
    for yy in range(176,192):
        for c in range(16):
            h=(c//2+(yy-176)//4)%len(hues)
            ink,paper=hues[h],hues[(h+1)%len(hues)]
            offset=row(yy)+c
            ram[0x4000+offset]=0xaa if yy%2==0 else 0x55
            ram[0x6000+offset]=ink|(paper<<3)|(64 if yy>=184 else 0)
    # Right side occupies 256 narrow pixels in genuine 512x192 mode.
    hi=Image.new('1',(256,192));hd=ImageDraw.Draw(hi)
    font_data=(ROOT/'timex-font-8x8.bin').read_bytes()
    def romtext(text,x,y):
        for ch in text:
            for v in range(8):
                bits=font_data[(ord(ch)-32)*8+v]
                for u in range(8):
                    if bits&(128>>u):hi.putpixel((x+u,y+v),255)
            x+=8
    romtext('HIGH RESOLUTION',68,7)
    romtext('512 x 192 MODE',72,20)
    romtext('YELLOW ON BLUE',72,33)
    f=ImageFont.truetype(str(FONT),9)
    hd.text((12,50),'Fine proportional text: iii WWW 012345',font=f,fill=1)
    hd.text((12,62),'One-pixel curves and checkerboard',font=f,fill=1)
    points=[(round(128+112*math.sin(3*t)),round(112+32*math.sin(2*t)))
            for t in np.linspace(0,2*math.pi,2200)]
    hd.line(points,fill=1,width=1)
    hd.line((8,77,247,77),fill=1,width=1)
    for yy in range(155,185):
        for xx in range(8,248):
            if (xx+yy)&1:hi.putpixel((xx,yy),255)
    hd.rectangle((24,163,231,176),fill=0)
    romtext('ONE HIGH-RES PIXEL',56,166)
    for yy in range(192):
        for xx in range(256):
            if hi.getpixel((xx,yy)):
                fullx=256+xx
                address=0x4000+(((fullx>>3)&1)*0x2000)+row(yy)+(fullx>>4)
                ram[address]|=128>>(fullx&7)
    return ram

def build():
    ram=artwork();rom=bytearray(8192);pc=0x100;labels={};fixes=[]
    def emit(*values):
        nonlocal pc
        for v in values:rom[pc]=v;pc+=1
    def mark(name):labels[name]=pc
    def jump(op,name):emit(op,0,0);fixes.append((pc-2,name))
    rom[:3]=bytes((0xc3,0,1));rom[0x38]=0xc9
    emit(0xf3,0x31,0,0xff,0xed,0x56,0x3e,4,0xd3,0xfe)
    mark('frame');emit(0xfb,0x76,0xf3,0x16,240)
    # IRQ entry 13T + RET 10T + DI 4T + LD D,240 7T = 34T.
    # Align first loop start to line 15, T218 (absolute frame T3578).
    emit(6,255,0x10,0xfe,6,17,0x10,0xfe,0) # 3317 + 223 + 4 = 3544T
    mark('line')
    emit(0x3e,2,0xd3,0xff) # ECM at line T8, before left border starts at T16
    emit(0x3e,0,0x3e,0,*([0]*14)) # 70T
    emit(0x3e,0x36,0xd3,0xff) # yellow/blue 512 mode at T96: exact midpoint
    emit(*([0]*26),0x15);jump(0xc2,'line') # 104 + 4 + 10T
    # Total loop: 18 + 70 + 18 + 104 + 14 = 224T, one scanline.
    jump(0xc3,'frame')
    for at,name in fixes:struct.pack_into('<H',rom,at,labels[name])
    dck=bytes((255,2,0,3,3,0,0,0,0))+rom+ram[0x4000:0x8000]
    (ROOT/'split-personality.dck').write_bytes(dck)
    (ROOT/'initial-ram.bin').write_bytes(ram)
    (ROOT/'labels.json').write_text(json.dumps(labels,indent=2))
    print('Built split-personality.dck:',len(dck),'bytes; code ends',hex(pc))

if __name__=='__main__':build()
