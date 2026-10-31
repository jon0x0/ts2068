"""Build a native Z80 mixed-resolution reveal demo for TSRun.

No assembler dependency. Pillow is used only for preparing the title image.
Both source images stay stationary; one scanline is replaced per frame.
"""
from pathlib import Path
import json, struct, math
from PIL import Image, ImageDraw, ImageFont
from render_scene import render_scene

ROOT = Path(__file__).resolve().parent
TAPE = ROOT / 'morpho1.tap'
if not TAPE.exists():
    TAPE = ROOT.parent / 'upload' / 'morpho1.tap'

def row(y):
    return ((y & 192) << 5) | ((y & 7) << 8) | ((y & 56) << 2)

def read_picture(tape=TAPE):
    data=Path(tape).read_bytes(); at=0; blocks=[]
    while at<len(data):
        n=struct.unpack_from('<H',data,at)[0]
        block=data[at+2:at+2+n]
        assert len(block)==n and n>=2
        checksum=0
        for b in block: checksum ^= b
        assert checksum==0, 'TAP checksum failure'
        blocks.append(block); at+=n+2
    assert at==len(data) and len(blocks)==4
    assert blocks[0][2:12]==b'ecm-atr   ' and blocks[2][2:12]==b'ecm-pix   '
    attr,pix=blocks[1][1:-1],blocks[3][1:-1]
    assert len(attr)==len(pix)==6144
    return pix,attr

def title(second=False):
    # Render in physical 4:3 proportions, then sample to Timex 512x192 pixels.
    scale=4
    im=Image.new('L',(512*scale,384*scale)); draw=ImageDraw.Draw(im)
    fonts=Path('/usr/share/fonts/truetype/dejavu')
    lines=[('TIMEX 2068',46,6,True),('512\u00d7192 high resolution',26,63,False)]
    if second:
        lines=[('TWO MODES, ONE DISPLAY',36,8,True),
               ('256\u00d7192 ECM meets 512\u00d7192',25,63,False)]
    for text,size,y,bold in lines:
        path=fonts/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
        font=ImageFont.truetype(str(path),size*scale)
        while draw.textbbox((0,0),text,font=font)[2]>476*scale:
            size-=1; font=ImageFont.truetype(str(path),size*scale)
        box=draw.textbbox((0,0),text,font=font)
        x=(512*scale-(box[2]-box[0]))//2-box[0]
        draw.text((x,y*scale-box[1]),text,font=font,fill=255)
    # Native high resolution is one-bit. Preserve fractional edge coverage with
    # a light, stationary 2x2 ordered dither; solid strokes remain solid.
    coverage=im.resize((512,192),Image.Resampling.LANCZOS)
    im=Image.new('1',(512,192))
    thresholds=((80,144),(176,112))
    for y in range(192):
        for x in range(512):
            if coverage.getpixel((x,y))>=thresholds[y&1][x&1]:
                im.putpixel((x,y),255)
    # Full 64-column samples: original Timex ROM glyphs, eight native pixels
    # per character. No vector-font approximation is used for these rows.
    glyphs=(ROOT/'timex-font-8x8.bin').read_bytes()
    assert len(glyphs)==96*8
    samples=[
        'TIMEX ROM FONT: 64 COLUMNS x 8 PIXELS = 512 PIXELS ACROSS',
        '1234567890'*6+'1234',
        ('AaBbCc 0123456789 !? @#$% & ()[] /\\ += -_ .' if not second else
         '64-column text: Every character occupies eight high-res pixels.')]
    for y,text in zip((50,60,70),samples):
        for column,ch in enumerate(text[:64].ljust(64)):
            for v in range(8):
                bits=glyphs[(ord(ch)-32)*8+v]
                for u in range(8):
                    im.putpixel((column*8+u,y+v),255 if bits&(128>>u) else 0)
    if second:
        # The second title replaces its upper text area with a shaded scene.
        # Its lower checkerboard, fine text, and white reference stay intact.
        im.paste(0,(0,0,512,96))
        im.paste(render_scene(),(0,12))
        caption='TWO MODES, ONE DISPLAY - DITHERED 3D GRAYSCALE'
        for column,ch in enumerate(caption):
            for v in range(8):
                bits=glyphs[(ord(ch)-32)*8+v]
                for u in range(8):
                    im.putpixel((12+column*8+u,2+v),255 if bits&(128>>u) else 0)
    else:
        # One-native-pixel interlaced knotwork, with alternating over/under
        # crossings. The gray field begins at y=96 and is not disturbed.
        knot=Image.new('1',(512,16));kd=ImageDraw.Draw(knot)
        strands=[]
        for sign in (1,-1):
            points=[(x,8+round(sign*6*math.sin((x-8)*math.pi/16))) for x in range(8,505)]
            kd.line(points,fill=1,width=1);strands.append(points)
        for n,x in enumerate(range(8,505,16)):
            kd.rectangle((x-2,6,x+2,10),fill=0)
            sign=1 if n%2==0 else -1
            over=[(u,8+round(sign*6*math.sin((u-8)*math.pi/16)))
                  for u in range(max(8,x-2),min(505,x+3))]
            kd.line(over,fill=1,width=1)
        im.paste(knot,(0,80))
    # A substantial simulated gray area: a 30-pixel-thick one-pixel
    # checkerboard frame. It remains a genuine two-color high-res bitmap.
    for y in range(96,192):
        for x in range(512):
            im.putpixel((x,y),255 if (x+y)&1 else 0)
    im.paste(0,(30,126,482,162))
    fine=Image.new('L',(452*4,36*4));fd=ImageDraw.Draw(fine)
    ff=ImageFont.truetype(str(fonts/'DejaVuSans.ttf'),9*4)
    fine_lines=(['Fine proportional text: Native 512-pixel lettering.',
                 'Thin strokes: iii lll ttt fff   Wide letters: WWW MMM @@@',
                 'The quick brown fox jumps over the lazy dog. 0123456789',
                 '30-pixel gray frame: a stationary 1 x 1 checkerboard.'] if not second else
                ['A second page of fine proportional text, with different words.',
                 'Minimum widths: iii lll ... Maximum widths: WWW MMM @@@',
                 '256 x 192 extended color meets native 512 x 192 text.',
                 'Random up/down wipes. Two pictures. Two different titles.'])
    for v,text in zip((1,12,23),fine_lines):
        fd.text((2*4,v*4),text,font=ff,fill=255)
    fine=fine.resize((452,36),Image.Resampling.LANCZOS).point(lambda v:255 if v>=112 else 0,'1')
    im.paste(fine,(30,126))
    # Full-width solid ink-white reference, leaving 30-pixel side borders.
    im.paste(255,(30,174,482,186))
    stem='highres-title-2' if second else 'highres-title'
    im.save(ROOT/(stem+'-512x192.png'))
    im.resize((512,384),Image.Resampling.NEAREST).save(ROOT/(stem+'-preview.png'))
    planes=[bytearray(6144),bytearray(6144)]
    for y in range(192):
        for x in range(512):
            if im.getpixel((x,y)):
                planes[(x>>3)&1][row(y)+(x>>4)] |= 128>>(x&7)
    return planes

class Assembler:
    def __init__(self):
        self.rom=bytearray(16384); self.pc=0x100; self.labels={}; self.fixes=[]
    def emit(self,*values):
        for v in values: self.rom[self.pc]=v; self.pc+=1
    def label(self,name): self.labels[name]=self.pc
    def jump(self,op,name):
        self.emit(op,0,0); self.fixes.append((self.pc-2,name))
    def loop224(self,name):
        # All iterations except the last: 224 T-states. Last: 219.
        self.label(name); self.emit(6,15,0x10,0xfe,0,0x3e,0,0x15,0x20,0)
        self.rom[self.pc-1]=(self.labels[name]-self.pc)&255
    def finish(self):
        for at,name in self.fixes:
            struct.pack_into('<H',self.rom,at,self.labels[name])
        assert self.pc<0x800
        for y in range(192): struct.pack_into('<H',self.rom,0x800+2*y,row(y))
        return self.rom

def build():
    pix,attr=read_picture(); frogpix,frogattr=read_picture(ROOT/'frog.tap')
    hi0,hi1=title(); hi20,hi21=title(True); ram=bytearray(65536)
    for address,buf in [(0x4000,pix),(0x6000,attr),(0x8000,hi0),(0xa000,hi1),
                        (0xc000,pix),(0xe000,attr)]: ram[address:address+6144]=buf
    # split, hold, phase, space latch, top mode, bottom mode, picture, paused.
    # Phases: 0 ECM hold, 1 reveal title, 2 title hold, 3 reveal next ECM.
    ram[0x7c00:0x7c08]=bytes((0,240,0,0,0x3e,2,0,0))
    ram[0x7c08]=1 # toggles to first title when its first wipe starts
    ram[0x7c09]=0 # direction: 0 down, 1 up
    ram[0x7c0a]=0x5d # nonzero 8-bit pseudo-random state
    struct.pack_into('<HH',ram,0x7c10,0xc000,0xe000)
    a=Assembler(); e=a.emit; L=a.label; J=a.jump
    def load(v):e(0x3a,v,0x7c)
    def save(v):e(0x32,v,0x7c)
    a.rom[:3]=bytes((0xc3,0,1));a.rom[0x38]=0xc9
    e(0xf3,0x31,0,0xff,0xed,0x56,0xaf,0xd3,0xfe)
    L('frame');e(0xfb,0x76,0xf3);load(4);e(0xd3,0xff)
    load(0);e(0xc6,39,0x57);a.loop224('raster')
    e(6,10,0x10,0xfe,0,0);load(5);e(0xd3,0xff)
    # Finish scanning the stationary picture before replacing any row.
    load(0);e(0x47,0x3e,192,0x90);J(0xca,'keys');e(0x57);a.loop224('bottom')
    L('keys')
    # Q/A move the current dividing line and pause automatic motion.
    e(0x3e,0xfb,0xdb,0xfe,0xe6,1);J(0xca,'manual_up')
    e(0x3e,0xfd,0xdb,0xfe,0xe6,1);J(0xca,'manual_down')
    e(0x3e,0xf7,0xdb,0xfe,0xe6,8);J(0xca,'resume') # R
    e(0x3e,0x7f,0xdb,0xfe,0xe6,1);J(0xca,'space')
    e(0xaf);save(3);J(0xc3,'auto')
    L('space');load(3);e(0xb7);J(0xc2,'auto')
    e(0x3e,1);save(3);load(7);e(0xee,1);save(7);J(0xc3,'frame')
    L('resume');e(0xaf);save(7);J(0xc3,'frame')
    L('manual_up');e(0x3e,1);save(7);J(0xc3,'up')
    L('manual_down');e(0x3e,1);save(7);J(0xc3,'down')
    L('auto');load(7);e(0xb7);J(0xc2,'frame')
    load(2);e(0xe6,1);J(0xc2,'auto_move')
    load(1);e(0x3d);save(1);J(0xc2,'frame')
    load(2);e(0xb7);J(0xc2,'start_ecm')
    # A full ECM image is visible. Reset progress invisibly, reveal title.
    e(0x3e,1);save(2)
    load(8);e(0xee,1);save(8);e(0xb7);J(0xca,'title_one')
    e(0x3e,0x30);J(0xc3,'title_bank')
    L('title_one');e(0xaf)
    L('title_bank');e(0xd3,0xf4)
    e(6,0x3e,0x0e,2);J(0xcd,'prepare_wipe');J(0xc3,'frame')
    L('start_ecm')
    # Title is fully visible. Alternate the hidden ECM source, then put ECM
    # above the boundary. Frog lives in cartridge ROM; no extra RAM is needed.
    load(6);e(0xee,1);save(6);e(0xb7);J(0xca,'butterfly_source')
    e(0x21,0,0x10,0x22,0x10,0x7c,0x21,0,0x28,0x22,0x12,0x7c);J(0xc3,'ecm_ready')
    L('butterfly_source');e(0x21,0,0xc0,0x22,0x10,0x7c,0x21,0,0xe0,0x22,0x12,0x7c)
    L('ecm_ready');e(0x3e,3);save(2)
    e(6,2,0x0e,0x3e);J(0xcd,'prepare_wipe');J(0xc3,'frame')
    L('auto_move');load(9);e(0xb7);J(0xca,'down');J(0xc3,'up')
    L('up');load(0);e(0xb7);J(0xca,'end_wipe')
    e(0x3d);save(0);e(0xf5);load(5);e(0x47,0xf1);J(0xcd,'copy_mode')
    load(0);e(0xb7);J(0xc2,'frame');J(0xc3,'end_wipe')
    L('down');load(0);e(0xfe,192);J(0xca,'end_wipe')
    e(0xf5,0x3c);save(0);load(4);e(0x47,0xf1);J(0xcd,'copy_mode')
    load(0);e(0xfe,192);J(0xc2,'frame')
    L('end_wipe');load(7);e(0xb7);J(0xc2,'frame')
    load(2);e(0x3c,0xe6,3);save(2);e(0x3e,240);save(1);J(0xc3,'frame')
    L('prepare_wipe')
    # Right-shift Galois LFSR, feedback polynomial mask B8. Each transition
    # gets a fresh pseudo-random direction; consecutive repeats are allowed.
    load(10);e(0xcb,0x3f,0x30,2,0xee,0xb8);save(10);e(0xe6,1);save(9)
    e(0xb7);J(0xca,'prepare_down')
    e(0x3e,192);save(0);e(0x79);save(4);e(0x78);save(5);e(0xc9)
    L('prepare_down');e(0xaf);save(0);e(0x78);save(4);e(0x79);save(5);e(0xc9)
    L('copy_mode');e(0x4f,0x78,0xfe,2,0x79);J(0xca,'copy_ecm');J(0xc3,'copy_hi')
    for name,base in [('copy_hi',0x80),('copy_ecm',None)]:
        L(name);e(0x6f,0x26,0,0x29,0x11,0,8,0x19,0x5e,0x23,0x56,0xeb,0xe5)
        for plane in range(2):
            if plane:e(0xe1)
            e(0x54,0x5d,0x7a,0xf6,0x40+plane*0x20,0x57)
            if base is None:e(0xed,0x4b,0x10+plane*2,0x7c,0x09)
            else:e(0x7c,0xf6,base+plane*0x20,0x67)
            e(1,32,0,0xed,0xb0)
        e(0xc9)
    rom=a.finish()
    rom[0x1000:0x2800]=frogpix;rom[0x2800:0x4000]=frogattr
    dck=bytes((255,2,2,3,3,3,3,3,3))+rom+ram[0x4000:]
    # The alternate title occupies two DOCK ROM chunks at CPU 8000/BFFF.
    # Port F4 maps only those source chunks; the live screen remains in HOME.
    alternate=bytearray(16384)
    alternate[:6144]=hi20;alternate[8192:8192+6144]=hi21
    dck+=bytes((0,0,0,0,0,2,2,0,0))+alternate
    (ROOT/'timex-ecm-highres-reveal.dck').write_bytes(dck)
    (ROOT/'labels.json').write_text(json.dumps(a.labels,indent=2))
    (ROOT/'initial-ram.bin').write_bytes(ram)
    (ROOT/'second-title.bin').write_bytes(alternate)
    print('DCK',len(dck),'bytes; code ends',hex(a.pc))

if __name__=='__main__':build()
