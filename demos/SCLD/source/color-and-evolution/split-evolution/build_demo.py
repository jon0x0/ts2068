"""Split Personality Evolution: native animated per-scanline mode boundaries."""
from pathlib import Path
import json, math, struct
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
KERNEL=0x40;STRIDE=85;PREFIX=0xe360;SUFFIX=0xe8e1
CHAINS=0xeba2;FASTTOP=0xedf0;FASTBOTTOM=0xf5e8
ACTIVE=0xfe00;ENTRY=0xfe01;HOLD=0xfe03;META=0xfe10
PL=META+1;PR=META+3;SL=META+5;SR=META+7
LM=META+9;RM=META+10;BORDER=META+11;PAD=META+12;FINAL=META+13
PARAM_SIZE=226
REPEAT_COUNT=0xfe38
NEXT=0xfe04;PREPARED=0xfe06;PENDING=0xfe07;CURRENT_FINAL=0xfe08;PATH=0xfe09;SAVED_SP=0xfe0a
TAILS=0xfe40

def row(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def ka(y,offset=0):return KERNEL+y*STRIDE+offset

def artwork():
    ram=bytearray(65536)
    glyphs=(ROOT/'timex-font-8x8.bin').read_bytes()
    def text_bitmap(text,width=128,height=96,x=None,y=6):
        im=Image.new('1',(width,height))
        x=(width-len(text)*8)//2 if x is None else x
        for ch in text:
            for v in range(8):
                bits=glyphs[(ord(ch)-32)*8+v]
                for u in range(8):
                    if bits&(128>>u):im.putpixel((x+u,y+v),255)
            x+=8
        return im
    # Two intentionally different ECM panels in opposite corners.
    hues=[2,6,4,5,1,3]
    for bottom in (False,True):
        xbase=16 if bottom else 0;ybase=96 if bottom else 0
        label=text_bitmap('RED ECM' if bottom else 'GREEN ECM')
        label2=text_bitmap('16 COLORS' if bottom else '8x1 CELLS',y=18)
        for y in range(96):
            for c in range(16):
                ink=hues[(c//3+y//8+(3 if bottom else 0))%6]
                paper=0 if y<29 else (hues[(c//4+y//13)%6] if bottom else 1)
                bits=0
                for b in range(8):
                    x=c*8+b
                    if y<29:on=label.getpixel((x,y)) or label2.getpixel((x,y))
                    elif bottom:on=((x//4+y//3)&1)^((x+y)//19&1)
                    else:on=(x-63)**2+(y-60)**2<28**2 and ((x+y*2)//5)%3!=0
                    if on:bits|=128>>b
                if y<29:ink,paper=7,0
                k=row(y+ybase)+c+xbase
                ram[0x4000+k]=bits;ram[0x6000+k]=ink|(paper<<3)|64
    # Complete independent ECM image: duplicate each panel into its other half.
    for y in range(192):
        src=16 if y>=96 else 0;dst=0 if y>=96 else 16
        for c in range(16):
            for base in (0x4000,0x6000):ram[base+row(y)+dst+c]=ram[base+row(y)+src+c]
    ecm=bytes(ram)
    ram=bytearray(65536)
    # Independent 512-mode image; both byte planes contain bitmap pixels.
    for bottom in (False,True):
        im=text_bitmap('HIRES CUBE' if bottom else 'HIRES RIBBON',256,96,y=6)
        second=text_bitmap('ONE PIXEL LINES' if bottom else '512 x 192',256,96,y=18)
        im=Image.frombytes('1',im.size,bytes(a|b for a,b in zip(im.tobytes(),second.tobytes())))
        d=ImageDraw.Draw(im)
        if bottom:
            # Isometric wire cube, a different image from the top-right ribbon.
            a=[(64,46),(128,32),(190,46),(128,61),(64,46)]
            d.line(a,fill=1,width=1)
            d.line([(64,46),(64,76),(128,91),(190,76),(190,46)],fill=1,width=1)
            d.line([(128,61),(128,91)],fill=1,width=1)
            for x in range(16,240,8):im.putpixel((x,94),255)
        else:
            pts=[(round(128+112*math.sin(3*t)),round(62+25*math.sin(2*t))) for t in [n*math.tau/1600 for n in range(1601)]]
            d.line(pts,fill=1,width=1)
        ybase=96 if bottom else 0;xbase=0 if bottom else 256
        for y in range(96):
            for x in range(256):
                fullx=x+xbase;k=row(y+ybase)+(fullx>>4)
                address=0x4000+((fullx>>3)&1)*0x2000+k
                mask=128>>(fullx&7)
                if im.getpixel((x,y)):ram[address]|=mask
                else:ram[address]&=255^mask
    for y in range(192):
        src=0 if y>=96 else 16;dst=16 if y>=96 else 0
        for c in range(16):
            for base in (0x4000,0x6000):ram[base+row(y)+dst+c]=ram[base+row(y)+src+c]
    return bytearray(ecm),bytes(ram)

def scanline(left,right,col,tail=None):
    b=bytearray((0x3e,left,0xd3,0xff,0x18,32-col))
    b+=bytes(32)+bytes((0x3e,right,0xd3,0xff,0x18,col))+bytes(32)+bytes(9)
    assert len(b)==85
    if tail is not None:b[76:85]=tail
    return b

def jump_tail(address):return bytes((3,0,0,0,0,0,0xc3,address&255,address>>8))

class Asm:
    def __init__(self,ram,at):self.ram=ram;self.pc=at;self.labels={};self.fixes=[]
    def emit(self,*v):
        for b in v:self.ram[self.pc]=b;self.pc+=1
    def label(self,n):self.labels[n]=self.pc
    def jump(self,op,n):self.emit(op,0,0);self.fixes.append((self.pc-2,n))
    def finish(self):
        for p,n in self.fixes:struct.pack_into('<H',self.ram,p,self.labels[n])

def build():
    ram,hires=artwork();ecm=bytes(ram);kernel=bytearray(16384)
    kernel[:3]=bytes((0xc3,0,0xe0));kernel[0x38]=0xc9
    for y in range(192):
        tail=bytes((0x3e,4,0xd3,0xfe,1,0,0,0,0)) if y==95 else None
        # 36T, like the other tails. Restore FE after the final visible pixels,
        # before the first bottom-border scanline. The final hold patches 4 to 2.
        if y==191:tail=bytes((0x3e,4,0xd3,0xfe,0,0,0xc3,0,0))
        kernel[ka(y):ka(y)+STRIDE]=scanline(2,0x36,32,tail)
    # One seam byte per row, rather than two redundant displacement bytes.
    for start,rows in [(PREFIX,range(128)),(SUFFIX,range(128,192))]:
        a=Asm(ram,start)
        for y in rows:
            a.emit(0x7e,0x23,0x32,ka(y,43)&255,ka(y,43)>>8,0x2f,0xc6,33,
                   0x32,ka(y,5)&255,ka(y,5)>>8)
        a.emit(0xc9)
    chains={};pc=CHAINS
    for name,rows,field in [('pl',range(96,128),1),('pr',range(96,128),39),('sl',range(128,192),1),('sr',range(128,192),39)]:
        chains[name]={}
        for y in rows:
            chains[name][y]=pc;ram[pc:pc+3]=bytes((0x32,ka(y,field)&255,ka(y,field)>>8));pc+=3
        chains[name][rows.stop]=pc;ram[pc]=0xc9;pc+=1
    assert pc<=FASTTOP
    for start,left,right,target in [(FASTTOP,2,0x36,KERNEL),(FASTBOTTOM,0x26,2,0)]:
        for n in range(24):ram[start+n*85:start+(n+1)*85]=scanline(left,right,16,jump_tail(target) if n==23 else None)
    assert FASTBOTTOM+24*85<0xfe00

    stages=[]
    def add(cols,hold=3,stage=0,threshold=192,final=False):
        stages.append(dict(cols=[max(0,min(32,round(c))) for c in cols],hold=hold,stage=stage,threshold=threshold,final=final))
    diagonal=[32*y/191 for y in range(192)]
    sine=lambda phase:[16+8*math.sin(y*math.tau/192+phase) for y in range(192)]
    add([32]*192,90)
    for n in range(17):add([32-n]*192,90 if n==16 else 3,1)
    for n in range(17):
        t=n/16;add([16*(1-t)+diagonal[y]*t for y in range(192)],90 if n==16 else 3,2)
    for n in range(17):
        t=n/16;add([diagonal[y]*(1-t)+sine(0)[y]*t for y in range(192)],90 if n==16 else 3,3)
    for n in range(1,25):add(sine(n*math.tau/24),8,4)
    for n in range(25):
        t=n/24;add([sine(0)[y]*(1-t)+16*t for y in range(192)],3,5,round(192-96*t),n==24)
    assert len(stages)==101

    # Delay tails make arbitrary exact cycle totals: 7T loads + 4T NOPs.
    tails={};at=TAILS
    for rem in range(32,56):
        for loads in range(8):
            if rem>=loads*7 and (rem-loads*7)%4==0:break
        data=bytes((0x3e,0))*loads+bytes((rem-loads*7)//4)+bytes((0xc3,KERNEL&255,KERNEL>>8))
        tails[rem]=at;ram[at:at+len(data)]=data;at+=len(data)
    assert at<=65536
    calibration=json.loads((ROOT/'timing-calibration.json').read_text()) if (ROOT/'timing-calibration.json').exists() else {}
    def wait(key):
        # 60T dispatch/load/jumps, 24T per BC loop, remainder 32..55T.
        cycles=calibration.get(key,116);n=(cycles-60-32)//24;rem=cycles-60-24*n
        assert n>=1 and rem in tails,(key,cycles)
        return struct.pack('<HH',n,tails[rem])

    dock=bytearray(65536);exrom=bytearray(65536)
    param_end=0x4000+len(stages)*PARAM_SIZE
    # Sources avoid HOME display addresses, allowing direct writes while POP
    # reads immutable patch records from the other mapped pages.
    regions=[(exrom,0,0x4000,0x73,0x82),(exrom,0x8000,0xe000,0x73,0x82),
             (ram,0xb000,0xe000,0,2),(dock,param_end,0xe000,0x70,2)]
    region_index=0;position=regions[0][1];patch_bytes=0;descriptors=[]
    def allocate(data,count):
        nonlocal region_index,position,patch_bytes
        if not count:return struct.pack('<HBBB',0,0,0,2)
        while position+len(data)>regions[region_index][2]:
            region_index+=1
            if region_index>=len(regions):raise ValueError('Patch stream exceeds cartridge capacity')
            position=regions[region_index][1]
        array,_,_,f4,ff=regions[region_index];pointer=position
        array[position:position+len(data)]=data;position+=len(data);patch_bytes+=len(data)
        return struct.pack('<HBBB',pointer,count,f4,ff)
    def ecm_at(s,y,c):return (c<s['cols'][y]) != (s['stage']==5 and y>=s['threshold'])
    for index,s in enumerate(stages):
        patches=[]
        if index:
            before=stages[index-1]
            for y in range(192):
                for c in range(32):
                    if ecm_at(before,y,c)==ecm_at(s,y,c):continue
                    address=0x4000+row(y)+c;source=ecm if ecm_at(s,y,c) else hires
                    if ecm[address]==hires[address] and ecm[address+0x2000]==hires[address+0x2000]:continue
                    patches.append(struct.pack('<HBB',address,source[address],source[address+0x2000]))
        assert len(patches)<=256
        first=min(112,len(patches))
        desc=allocate(b''.join(patches[:first]),first)+allocate(b''.join(patches[first:]),len(patches)-first)
        descriptors.append(desc)
        threshold=s['threshold'];quad=s['stage']==5
        pstart=max(96,min(128,threshold)) if quad else 96
        sstart=max(128,min(192,threshold)) if quad else 128
        meta=struct.pack('<BHHHHBBBBBBB',s['hold'],chains['pl'][pstart],chains['pr'][pstart],
                         chains['sl'][sstart],chains['sr'][sstart],0x26 if quad else 2,
                         2 if quad else 0x36,2 if quad else 4,0,int(s['final']),s['stage'],0)
        record=bytes(s['cols'])+meta+desc+wait('prep'+str(index))+wait('switch'+str(index))
        assert len(record)==PARAM_SIZE
        dock[0x4000+index*PARAM_SIZE:0x4000+(index+1)*PARAM_SIZE]=record
    ram[0x8000:0x9800]=ecm[0x4000:0x5800];ram[0x9800:0xb000]=ecm[0x6000:0x7800]

    a=Asm(ram,0xe000);e=a.emit;L=a.label;J=a.jump
    def load(addr):e(0x3a,addr&255,addr>>8)
    def save(addr):e(0x32,addr&255,addr>>8)
    def loadhl(addr):e(0x2a,addr&255,addr>>8)
    def storehl(addr):e(0x22,addr&255,addr>>8)
    def setbyte(addr,value):e(0x3e,value);save(addr)
    def active_bank():load(ACTIVE);e(0xf6,0x7c,0xd3,0xf4)
    def wait_from(addr):e(0xed,0x4b,addr&255,addr>>8);loadhl(addr+2);J(0xc3,'burn')
    e(0xf3,0x31,0,0xfe,0xed,0x56,0x3e,0x7c,0xd3,0xf4,
      0x3e,4,0xd3,0xfe,0x3e,2,0xd3,0xff)
    L('frame');e(0xfb,0x76,0xf3);load(PENDING);e(0xb7);J(0xc2,'switch')
    load(PREPARED);e(0xb7);J(0xca,'prepare')
    setbyte(PATH,0);wait_from(0xfe0c)
    L('prepare');setbyte(PATH,1);J(0xcd,'metadata')
    load(ACTIVE);e(0xee,3,0xf6,0x7c,0xd3,0xf4)
    loadhl(NEXT);e(0xcd,PREFIX&255,PREFIX>>8);J(0xcd,'prefix_modes')
    load(BORDER);save(ka(95,77));active_bank();setbyte(PREPARED,1)
    wait_from(META+26)
    L('switch');setbyte(PATH,2);e(0x21,(META+21)&255,(META+21)>>8);J(0xcd,'patch')
    load(ACTIVE);e(0xee,3);save(ACTIVE);e(0xf6,0x7c,0xd3,0xf4)
    loadhl(NEXT);storehl(ENTRY);e(0x11,PARAM_SIZE,0,0x19);storehl(NEXT)
    load(META);save(HOLD);load(FINAL);save(CURRENT_FINAL)
    setbyte(PENDING,0);setbyte(PREPARED,0);wait_from(META+30)
    # Reset the visible border immediately after active scanout. Otherwise
    # its last hires color persists on idle frames, while patch frames switch
    # to ECM during memory banking, making top/bottom borders flicker.
    L('post');e(0x3e,2,0xd3,0xff)
    load(CURRENT_FINAL);e(0xb7);J(0xc2,'enter_final')
    load(PATH);e(0xfe,1);J(0xc2,'suffix_done')
    load(ACTIVE);e(0xee,3,0xf6,0x7c,0xd3,0xf4)
    loadhl(NEXT);e(0x11,128,0,0x19,0xcd,SUFFIX&255,SUFFIX>>8)
    J(0xcd,'suffix_modes');active_bank()
    L('suffix_done');load(HOLD);e(0x3d);save(HOLD);J(0xc2,'frame')
    e(0x21,(META+16)&255,(META+16)>>8);J(0xcd,'patch');setbyte(PENDING,1);J(0xc3,'frame')
    L('metadata');loadhl(NEXT);e(0x11,192,0,0x19,0x11,META&255,META>>8,1,34,0,0xed,0xb0,0xc9)
    L('prefix_modes');e(0xe5);load(LM);loadhl(PL);J(0xcd,'dispatch');load(RM);loadhl(PR);J(0xcd,'dispatch');e(0xe1,0xc9)
    L('suffix_modes');e(0xe5);load(LM);loadhl(SL);J(0xcd,'dispatch');load(RM);loadhl(SR);J(0xcd,'dispatch');e(0xe1,0xc9)
    L('dispatch');e(0xe9)
    L('patch')
    e(0x5e,0x23,0x56,0x23,0x46,0x23,0x78,0xb7,0xc8) # zero-count return
    e(0x7e,0xd3,0xf4,0x23,0x7e,0xd3,0xff,0xed,0x73,SAVED_SP&255,SAVED_SP>>8,0xeb,0xf9)
    L('patch_loop');e(0xe1,0xd1,0x73,0xcb,0xec,0x72,0x10,0xf8) # 55T; final iteration 50T
    e(0xed,0x7b,SAVED_SP&255,SAVED_SP>>8,0x3e,2,0xd3,0xff);active_bank();e(0xc9)
    L('burn');e(0x0b,0x78,0xb1);J(0xc2,'burn');e(0xe9)
    L('enter_final');e(0x21,FASTBOTTOM&255,FASTBOTTOM>>8,0x22,ka(191,83)&255,ka(191,83)>>8)
    setbyte(ka(191,77),2)
    setbyte(REPEAT_COUNT,120);J(0xc3,'fast_frame')
    L('fast_frame');e(0xfb,0x76,0xf3,0x3e,4,0xd3,0xfe,0x3e,2,0xd3,0xff)
    e(6,255,0x10,0xfe,6,13,0x10,0xfe,0x3e,0,0,0xc3,FASTTOP&255,FASTTOP>>8)
    L('fast_end');load(REPEAT_COUNT);e(0x3d);save(REPEAT_COUNT);J(0xc2,'fast_frame')
    L('restart');e(0xf3,0x3e,4,0xd3,0xfe,0x3e,0,0xd3,0xff,0xd3,0xf4)
    # Normal-mode attributes are zero: the brief reset is a clean black frame.
    e(0x21,0,0x80,0x11,0,0x40,1,0,0x18,0xed,0xb0,0x21,0,0x98,0x11,0,0x60,1,0,0x18,0xed,0xb0)
    e(0x21,0,0x40);storehl(NEXT);storehl(ENTRY)
    e(0x3e,0x7c,0xd3,0xf4);J(0xcd,'metadata')
    for bank in (0x7c,0x7f):
        e(0x3e,bank,0xd3,0xf4,0x21,0,0x40,0xcd,PREFIX&255,PREFIX>>8);J(0xcd,'prefix_modes')
        e(0x21,128,0x40,0xcd,SUFFIX&255,SUFFIX>>8);J(0xcd,'suffix_modes')
        e(0x21,0,0);postfix=a.pc-2;e(0x22,ka(191,83)&255,ka(191,83)>>8);a.fixes.append((postfix,'post'))
        e(0x3e,4);save(ka(95,77))
        e(0x3e,4);save(ka(191,77))
    e(0x21,(0x4000+PARAM_SIZE)&255,(0x4000+PARAM_SIZE)>>8);storehl(NEXT)
    setbyte(ACTIVE,3);setbyte(HOLD,90);setbyte(PREPARED,0);setbyte(PENDING,0);setbyte(CURRENT_FINAL,0)
    J(0xc3,'frame')
    assert a.pc<PREFIX,hex(a.pc)
    a.finish()
    for y in [191]:struct.pack_into('<H',kernel,ka(y,83),a.labels['post'])
    struct.pack_into('<H',ram,FASTBOTTOM+23*85+83,a.labels['fast_end'])
    ram[ACTIVE]=0;ram[HOLD]=90;struct.pack_into('<H',ram,ENTRY,0x4000);struct.pack_into('<H',ram,NEXT,0x4000+PARAM_SIZE)
    ram[0xfe0c:0xfe10]=wait('idle')
    dock[:0x4000]=kernel
    home=bytes((255,3,3,3,3,3,3,3,3))+kernel+ram[0x4000:]
    db=bytes((0,3,3,2,2,2,2,2,0))+dock[:0xe000]
    eb=bytes((254,2,2,0,0,2,2,2,0))+exrom[:0x4000]+exrom[0x8000:0xe000]
    (ROOT/'split-personality-evolution.dck').write_bytes(home+db+eb)
    (ROOT/'initial-ram.bin').write_bytes(ram);(ROOT/'ecm-art.bin').write_bytes(ecm);(ROOT/'hires-art.bin').write_bytes(hires)
    (ROOT/'stages.json').write_text(json.dumps(stages,indent=2));(ROOT/'labels.json').write_text(json.dumps(a.labels,indent=2))
    print('Built',len(home+db+eb),'bytes; patches',patch_bytes,'runtime ends',hex(a.pc))

if __name__=='__main__':build()

