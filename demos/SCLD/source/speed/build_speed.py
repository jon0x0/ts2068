"""Native 7T same-address attribute-write phase sweep for TSRun."""
from pathlib import Path
import sys,struct,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import cartridge as common
common.ROOT=ROOT
row=common.row
def padding(t,value):
    for a in range(1,10):
        if t>=7*a and (t-7*a)%4==0:return bytes((0x3e,value))*a+bytes((t-7*a)//4)
    raise ValueError(t)
def build():
    ram=bytearray(65536);ram[0x4000:0x8000]=(ROOT/'scene.bin').read_bytes()
    # Remove old labels and divider; the sphere is retained as background.
    for y in list(range(32))+list(range(177,192))+list(range(94,98)):
        for c in range(32):ram[0x4000+row(y)+c]=0;ram[0x6000+row(y)+c]=71
    im=Image.new('1',(256,192));d=ImageDraw.Draw(im);font=ImageFont.truetype(common.FONT,10)
    for text,y in [('ATTRIBUTE SPEED LAB',3),('7T writes / phase sweep',18),('Max: 4 colors per 8x1 cell',177)]:d.text((8,y),text,font=font,fill=1)
    for y in list(range(32))+list(range(177,192)):
        for c in range(32):ram[0x4000+row(y)+c]=sum(128>>b for b in range(8) if im.getpixel((c*8+b,y)))
    # All pairs are disjoint, so two changes in a cell could show six colors.
    attrs=[64|1|(2<<3),64|4|(6<<3),64|3|(5<<3)]
    targets=[8,16,24];code=bytearray();params=[]
    for y in range(192):
        phase=(y-32)%7;values=attrs if 32<=y<177 else [71]*3
        code+=bytes((6,values[1],14,values[2])) # B/C preload: 14T
        code+=padding(35+phase,values[0])
        for c in targets:
            addr=0x6000+row(y)+c
            code+=bytes((0x21,addr&255,addr>>8,0x77,0x70,0x71))
            # LD HL,nn:10T; LD(HL),A/B/C:7T each. No reload between writes.
            ram[addr]=values[2]
            if 32<=y<177:ram[0x4000+row(y)+c]=0xaa if y%2==0 else 0x55
        code+=padding(72-phase,values[0])+bytes((0xc3,0,0))
        struct.pack_into('<H',code,len(code)-2,0x8000+len(code))
        params.append(dict(phase=phase,values=values,writeTimes=[[59+phase+g*31+i*7 for i in range(3)] for g in range(3)]))
    assert len(code)<16384
    common.save('attribute-speed-lab',ram,code,0x8000,8960-27-10)
    (ROOT/'speed-params.json').write_text(json.dumps(dict(targets=targets,rows=params)))
    print('Built',len(code),'kernel bytes')
if __name__=='__main__':build()
