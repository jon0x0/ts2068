"""Native cartridge probes: one mid-cell change, adjacent-byte bursts, dense writes."""
from pathlib import Path
import struct,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
OLD=64|2|(1<<3);NEW=64|4|(6<<3)
def row(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def word(x):return bytes((x&255,x>>8))
def pad(t,value=0):
    for n in range(8):
        if t>=n*7 and (t-n*7)%4==0:return bytes((0x3e,value))*n+bytes((t-n*7)//4)
    raise ValueError(t)
def delay(t):
    data=bytearray()
    while t>3350:data+=bytes((6,255,0x10,0xfe));t-=3317
    for n in range(255,0,-1):
        if t>=13*n+2:
            try:rest=pad(t-(13*n+2))
            except ValueError:continue
            return data+bytes((6,n,0x10,0xfe))+rest
    return data+pad(t)
def artwork(kind):
    ram=bytearray(65536);im=Image.new('1',(256,192));d=ImageDraw.Draw(im)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',9)
    for text,y in [('TIMEX DYNAMIC ECM TEST',3),('RED/BLUE -> GREEN/YELLOW',17),
                   ('1  SINGLE CHANGE / PHASE SWEEP',31),
                   ('2  '+kind+' / ADJACENT CELLS',85),
                   ('3  DENSE TRIPLE / 7T STORES',133),
                   ('REFERENCE PAIRS AT BOTH SIDES',181)]:d.text((5,y),text,font=font,fill=1)
    for y in range(192):
        for c in range(32):
            k=row(y)+c
            ram[0x4000+k]=sum(128>>b for b in range(8) if im.getpixel((c*8+b,y)))
            ram[0x6000+k]=71
    for y in list(range(44,80))+list(range(98,130))+list(range(146,178)):
        targets=[15] if y<80 else ([14,15] if y<130 else [14,15,16])
        for c in [3,4,27,28]+targets:
            k=row(y)+c;ram[0x4000+k]=0xaa if y%2==0 else 0x55
            ram[0x6000+k]=NEW if c in (27,28) else OLD
    return ram
def hardware_cart(slug,ram,kernel):
    """Ordinary DOCK-only LROS: copy assets to HOME, then use a RAM IM2 handler."""
    dock=bytearray([255])*65536;program=bytearray()
    def emit(*v):program.extend(v)
    emit(0xf3,0x3e,0,0xd3,0xf4,0x31,0xff,0xbf)
    # All possible interrupt vectors address the same uncontended RET handler.
    emit(0x21,0,0xbc,0x36,0xbd,0x11,1,0xbc,1,0,1,0xed,0xb0,
         0x3e,0xc9,0x32,0xbd,0xbd,0x3e,0xbc,0xed,0x47,0xed,0x5e,
         0x3e,4,0xd3,0xfe,0x3e,2,0xd3,0xff)
    frame=0xb000+len(program)
    emit(0xfb,0x76,0xf3);program+=delay(8960-33-10);emit(0xc3,0,0x80)
    code=bytearray(kernel);code[-2:]=word(frame)
    dock[0:0x1800]=ram[0x4000:0x5800];dock[0x1800:0x3000]=ram[0x6000:0x7800]
    dock[0x3000:0x4000]=code[:4096];dock[0xe000:0xe000+len(code)-4096]=code[4096:]
    dock[0xc100:0xc100+len(program)]=program
    boot=bytearray((0xf3,0x3e,0xc3,0xd3,0xf4))
    for src,dst,n in [(0,0x4000,6144),(0x1800,0x6000,6144),(0x3000,0x8000,4096),(0xe000,0x9000,len(code)-4096),(0xc100,0xb000,len(program))]:
        boot+=bytes((0x21,))+word(src)+bytes((0x11,))+word(dst)+bytes((1,))+word(n)+bytes((0xed,0xb0))
    boot+=bytes((0xc3,0,0xb0));dock[0xc008:0xc008+len(boot)]=boot
    # LROS header at chunk 4: identifier, entry point, HOME chunk bitmap.
    dock[0x8000:0x8004]=bytes((1,8,0xc0,0x2c))
    pages=[0,1,4,6,7];flags=[2 if i in pages else 0 for i in range(8)]
    cart=bytes((0,*flags))+b''.join(dock[i*8192:(i+1)*8192] for i in pages)
    (ROOT/(slug+'-hardware.dck')).write_bytes(cart)
    (ROOT/(slug+'-hardware.bin')).write_bytes(dock)
def build(kind,slug):
    ram=artwork(kind);code=bytearray();params=[]
    for y in range(192):
        start=len(code);events=[];targets=[];phase=None
        if 44<=y<80:
            phase=(y-44)%8-4;c=15;a=0x6000+row(y)+c;newtime=92+phase
            code+=bytes((0x21,))+word(a)+bytes((0x36,OLD,0x3e,NEW)) # 27T
            code+=pad(newtime-27,NEW)+bytes((0x77,))+pad(207-newtime)
            events=[dict(address=a,time=10,value=OLD),dict(address=a,time=newtime,value=NEW)];targets=[c]
        elif 98<=y<130:
            phase=y-98;a=0x6000+row(y)+14;newtime=72+phase
            code+=bytes((0x3e,OLD,0x32))+word(a)+bytes((0x32,))+word(a+1)+bytes((0x21,NEW,NEW)) #43T
            extra=0;post=0;cost=16;addresses=[a,a+1]
            if kind=='PUSH':code+=bytes((0x31,))+word(a+2);extra=10;post=10;cost=11;addresses=[a+1,a]
            if kind=='EXCHANGE':code+=bytes((0x31,))+word(a);extra=10;post=10;cost=19
            code+=pad(newtime-43-extra)
            if kind=='STORE16':code+=bytes((0x22,))+word(a)
            elif kind=='PUSH':code+=bytes((0xe5,))
            else:code+=bytes((0xe3,))
            if post:code+=bytes((0x31,0,0xff))
            code+=pad(214-newtime-cost-post)
            events=[dict(address=a,time=7,value=OLD),dict(address=a+1,time=20,value=OLD)]+[dict(address=addr,time=newtime,value=NEW) for addr in addresses];targets=[14,15]
        elif 146<=y<178:
            phase=(y-146)%8-4;addresses=[0x6000+row(y)+c for c in (14,15,16)];newtime=88+phase
            code+=bytes((1,))+word(addresses[0])+bytes((0x11,))+word(addresses[1])+bytes((0x21,))+word(addresses[2])
            code+=bytes((0x3e,OLD,2,0x12,0x77,0x3e,NEW)) #65T
            code+=pad(newtime-65,NEW)+bytes((2,0x12,0x77))+pad(193-newtime)
            events=[dict(address=a,time=37+i*7,value=OLD) for i,a in enumerate(addresses)]+[dict(address=a,time=newtime+i*7,value=NEW) for i,a in enumerate(addresses)];targets=[14,15,16]
        else:code+=pad(214)
        code+=bytes((0xc3,))+word(0x8000+len(code)+3)
        params.append(dict(y=y,phase=phase,events=events,targets=targets,code=0x8000+start))
    assert len(code)<0x4000,len(code)
    # ROM boot and interrupt return. Each row is 224T without contention.
    rom=bytearray(8192);rom[:3]=bytes((0xc3,0,1));rom[0x38]=0xc9
    boot=bytes((0xf3,0x31,0,0xff,0xed,0x56,0x3e,0,0xd3,0xf4,0x3e,4,0xd3,0xfe,0x3e,2,0xd3,0xff))
    frame=0x100+len(boot);program=boot+bytes((0xfb,0x76,0xf3))+delay(8960-27-10)+bytes((0xc3,0,0x80))
    rom[0x100:0x100+len(program)]=program
    code[-2:]=word(frame);ram[0x8000:0x8000+len(code)]=code
    cart=bytes((255,2,0,3,3,3,3,0,0))+rom+ram[0x4000:0xc000]
    (ROOT/(slug+'.dck')).write_bytes(cart);(ROOT/(slug+'-ram.bin')).write_bytes(ram)
    (ROOT/(slug+'-schedule.json')).write_text(json.dumps(params,indent=2))
    hardware_cart(slug,ram,code)
    print(slug,len(cart),'bytes; kernel',len(code),'bytes')
if __name__=='__main__':
    for kind,slug in [('STORE16','timex-dynamic-ecm-probe'),('PUSH','timex-dynamic-ecm-push'),('EXCHANGE','timex-dynamic-ecm-exchange')]:build(kind,slug)
