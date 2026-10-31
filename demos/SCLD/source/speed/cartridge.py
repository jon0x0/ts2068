"""Two independent native TS2068 cartridges; no host-rendered animation."""
from pathlib import Path
import math, json, struct, shutil, itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
def row(y): return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def save(name,ram,code,start,delay):
    rom=bytearray(8192);rom[:3]=bytes((0xc3,0,1));rom[0x38]=0xc9
    boot=bytes((0xf3,0x31,0,0xff,0xed,0x56,0x3e,0,0xd3,0xfe,0x3e,2,0xd3,0xff))
    frame=0x100+len(boot)
    # IRQ+RET+DI=27T. Delay is generated exactly from instruction timings.
    pad=bytearray();remaining=delay
    while remaining>3350: pad+=bytes((6,255,0x10,0xfe));remaining-=3317
    for n in range(255,0,-1):
        cost=13*n+2
        rest=remaining-cost
        if rest>=0 and any((rest-7*a)%4==0 and rest>=7*a for a in range(4)):
            pad+=bytes((6,n,0x10,0xfe));remaining=rest;break
    for a in range(4):
        if remaining>=7*a and (remaining-7*a)%4==0:
            pad+=bytes((0x3e,0))*a+bytes((remaining-7*a)//4);break
    else: raise ValueError(remaining)
    main=boot+bytes((0xfb,0x76,0xf3))+pad+bytes((0xc3,start&255,start>>8))
    rom[0x100:0x100+len(main)]=main
    # Kernel's final JP goes to EI/HALT frame loop.
    code[-2:]=struct.pack('<H',frame);ram[start:start+len(code)]=code
    flags=(255,2,0,3,3,3,3,0,0)
    dck=bytes(flags)+rom+ram[0x4000:0xc000]
    (ROOT/(name+'.dck')).write_bytes(dck)
    (ROOT/(name+'-ram.bin')).write_bytes(ram)

def atlas():
    ram=bytearray(65536)
    hi=Image.new('1',(256,192));d=ImageDraw.Draw(hi)
    names=['BLACK / WHITE','BLUE / YELLOW','RED / CYAN','MAGENTA / GREEN',
           'GREEN / MAGENTA','CYAN / RED','YELLOW / BLUE','WHITE / BLACK']
    for band in range(8):
        y0=band*24
        d.text((10,y0+2),names[band],font=ImageFont.truetype(FONT,11),fill=1)
        for y in range(y0+17,y0+23):
            for x in range(8,248):hi.putpixel((x,y),int(((x+y)&1) if x<128 else True))
        for y in range(y0,y0+24):
            for c in range(16):
                # Each band repeats all sixteen entries, interleaved with 1px texture.
                color=c&7;bright=64 if c>=8 else 0;k=row(y)+c
                ram[0x4000+k]=0xaa if y%2 else 0x55
                ram[0x6000+k]=color|(color<<3)|bright
                if y-y0>=16:ram[0x6000+k]=color|(((color+1)&7)<<3)|bright
    for y in range(192):
        for x in range(256):
            xx=x+256;k=row(y)+(xx>>4)
            if hi.getpixel((x,y)):ram[0x4000+((xx>>3)&1)*8192+k]|=128>>(xx&7)
    code=bytearray()
    for n in range(240):
        band=max(0,min(7,(n-24)//24));mode=6|(band<<3)
        code+=bytes((0x3e,2,0xd3,0xff,0x3e,band,0xd3,0xfe))
        code+=bytes((0x3e,0,0x3e,0))+bytes(14) #70T
        code+=bytes((0x3e,mode,0xd3,0xff))
        code+=bytes(25) if n<239 else bytes((3,))+bytes(21)+bytes((0xc3,0,0))
    assert len(code)==240*55
    save('timex-color-atlas',ram,code,0x8000,3560-27-10)

def race():
    ram=bytearray(65536);old=[];new=[];targets=[4,9,14,19,24]
    # A shaded sphere in a five-column mosaic. Each pair of adjacent hues
    # is chosen from image lighting; every test cell contains four pixels of each pair.
    hues=[1,3,2,6,4,5,7]
    for y in range(192):
        oo=[];nn=[]
        for c in range(32):
            x=c*8+4;dx=(x-128)/85;dy=(y-105)/75
            z=math.sqrt(max(0,1-dx*dx-dy*dy));inside=dx*dx+dy*dy<1
            shade=max(0,min(6,int((.25-.28*dx-.35*dy+.65*z)*6)))
            h=hues[shade] if inside else 1
            attr=h|(0<<3)|64;bits=0xaa if y%2 else 0x55
            if not inside:bits=0x11 if y%8==0 else 0
            k=row(y)+c;ram[0x4000+k]=bits;ram[0x6000+k]=attr
        for c in targets:
            # Four distinct colors and no FLASH; bright group shared.
            a=64|1|(2<<3);b=64|4|(6<<3)
            if y<96:b=a # Normal two-color control in upper half.
            elif y>=164:
                h=(y//12+c)%4
                pairs=[(1,2,4,6),(3,1,5,7),(2,6,3,7),(4,5,6,7)]
                p,q,r,s=pairs[h];a=64|p|(q<<3);b=64|r|(s<<3)
            oo.append(a);nn.append(b)
            ram[0x4000+row(y)+c]=0xaa if y%2==0 else 0x55
            ram[0x6000+row(y)+c]=a
        old.append(oo);new.append(nn)
    # Quantize a shaded 3D scene. Ordinary cells choose one pair for 8 pixels;
    # raced cells in the lower half choose independent pairs for each 4 pixels.
    palette=np.array([(0,0,0),(0,0,255),(255,0,0),(255,0,255),
                      (0,255,0),(0,255,255),(255,255,0),(255,255,255)],float)
    pairs=list(itertools.combinations_with_replacement(range(8),2))
    def quantize(rgb):
        dist=((np.array(rgb)[:,None,:]-palette[None,:,:])**2).sum(axis=2)
        a,b=min(pairs,key=lambda p:np.minimum(dist[:,p[0]],dist[:,p[1]]).sum())
        return 64|a|(b<<3),[dist[i,a]<dist[i,b] for i in range(len(rgb))]
    for y in range(32,164):
        for c in range(32):
            rgb=[]
            for x in range(c*8,c*8+8):
                dx=(x-128)/90;dy=(y-98)/63;r=dx*dx+dy*dy
                if r<1:
                    z=math.sqrt(1-r);light=max(.04,-.3*dx-.45*dy+.8*z)
                    spec=max(0,(-.25*dx-.4*dy+.85*z))**26
                    rgb.append([min(255,255*((.6+.4*dx)*light+spec)),min(255,255*((.6-.4*dx)*light+spec)),min(255,255*((.45+.4*dy)*light+spec))])
                else:
                    floor=y>128;v=35 if not floor else (80 if ((x//12+y//6)&1) else 15)
                    rgb.append((v*.4,v*.6,v))
            # Ordered spatial dithering supplies graded light rather than flat fills.
            bayer=((0,8,2,10),(12,4,14,6),(3,11,1,9),(15,7,13,5))
            rgb=[[max(0,min(255,v+(bayer[y%4][(c*8+i)%4]-7.5)*13)) for v in pixel] for i,pixel in enumerate(rgb)]
            target=targets.index(c) if c in targets else -1
            if target>=0 and y>=96:
                a,bits1=quantize(rgb[:4]);b,bits2=quantize(rgb[4:]);bits=bits1+bits2
            else:a,bits=quantize(rgb);b=a
            k=row(y)+c;ram[0x4000+k]=sum((128>>i) for i,on in enumerate(bits) if on);ram[0x6000+k]=a
            if target>=0:old[y][target]=a;new[y][target]=b
    # Labels are placed away from the active test cells.
    im=Image.new('1',(256,192));d=ImageDraw.Draw(im)
    for text,y in [('ATTRIBUTE RACE LAB',3),('2 colors per 8x1 cell',18),('4 colors per 8x1 cell',177)]:
        d.text((8,y),text,font=ImageFont.truetype(FONT,10),fill=1)
        for yy in range(y,min(192,y+13)):
            for c in range(1,31):
                bits=sum((128>>b) for b in range(8) if im.getpixel((c*8+b,yy)))
                ram[0x4000+row(yy)+c]=bits;ram[0x6000+row(yy)+c]=71
                if c in targets:old[yy][targets.index(c)]=new[yy][targets.index(c)]=71
    # Center the visible divider on the boundary between rows 95 and 96.
    # Black margins keep it distinct against both bright and dark artwork.
    for y in range(94,98):
        for c in range(1,31):
            ram[0x4000+row(y)+c]=255 if y in (95,96) else 0
            ram[0x6000+row(y)+c]=71
            if c in targets:old[y][targets.index(c)]=new[y][targets.index(c)]=71
    code=bytearray()
    for y in range(192):
        for values in (old[y],new[y]):
            for c,v in zip(targets,values):
                addr=0x6000+row(y)+c
                code+=bytes((0x3e,v,0x32,addr&255,addr>>8)) #20T
        code+=bytes((0x3e,0,0x3e,0,0xc3,0,0)) #14+10T
        struct.pack_into('<H',code,len(code)-2,0x8000+len(code))
    assert len(code)==57*192
    save('attribute-race-lab',ram,code,0x8000,8903-27-10)
    (ROOT/'race-params.json').write_text(json.dumps(dict(targets=targets,old=old,new=new)))

if __name__=='__main__':
    ROOT.mkdir(exist_ok=True);atlas();race()
