"""Execute patched ROMs against a functional model of the traced Timex wiring.

SkoolKit is a test dependency, not part of the TSPico firmware. No contention,
analog timing or PIO execution is simulated by this CPU harness.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/python'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC,T,IFF


class Memory:
    def __init__(self,roms):
        self.roms=[list(r) for r in roms]
        # Deliberately NONZERO power-on RAM. HOME is separate from ALL external pages.
        self.home=[0xa5]*49152
        self.banks=[[0x5a]*16384 for _ in range(8)]
        self.latch=0
        self.f4=0
        self.ff=0
    def __len__(self): return 65536
    def __getitem__(self,a):
        a &= 65535
        if a<0x4000:return self.roms[(self.latch>>4)&1][a]
        if a>=0xc000 and self.f4&0xc0==0xc0 and not self.ff&128:
            return self.banks[self.latch&7][a&0x3fff]
        return self.home[a-0x4000]
    def __setitem__(self,a,v):
        a &= 65535
        if a<0x4000:return
        if a>=0xc000 and self.f4&0xc0==0xc0 and not self.ff&128:
            self.banks[self.latch&7][a&0x3fff]=v
        else:self.home[a-0x4000]=v
    def page(self,value):
        if not self.latch&32:self.latch=value&63


KEYS={
    'shift':(0,0),'z':(0,1),'x':(0,2),'c':(0,3),'v':(0,4),
    'a':(1,0),'s':(1,1),'d':(1,2),'f':(1,3),'g':(1,4),
    'q':(2,0),'w':(2,1),'e':(2,2),'r':(2,3),'t':(2,4),
    '1':(3,0),'2':(3,1),'3':(3,2),'4':(3,3),'5':(3,4),
    '0':(4,0),'9':(4,1),'8':(4,2),'7':(4,3),'6':(4,4),
    'p':(5,0),'o':(5,1),'i':(5,2),'u':(5,3),'y':(5,4),
    'enter':(6,0),'l':(6,1),'k':(6,2),'j':(6,3),'h':(6,4),
    ' ':(7,0),'symbol':(7,1),'m':(7,2),'n':(7,3),'b':(7,4)}
SYMBOLS={'!':'1','"':'p','+':'k',',':'n','-':'j','=':'l',':':'z',';':'o','(':'8',')':'9','*':'b','/':'v'}


class Machine:
    def __init__(self,roms=None):
        roms=roms or [(ROOT/f'build/rom/tspico128-{i}.rom').read_bytes() for i in range(2)]
        self.memory=Memory(roms)
        self.cpu=Simulator(self.memory,config={'fast_ldir':True,'fast_djnz':True,
                                              'frame_duration':58800,'int_active':32})
        self.cpu.set_tracer(self)
        self.rows=[31]*8
        self.ay=[0]*16;self.ay_select=0;self.ay_events=[]
        self.events=[];self.output_counts=collections.Counter();self.rom_switches=0
        self.frame=0;self.border=0;self.coverage=set();self.operations=0
    def write_port(self,r,port,value,offset):
        low=port&255;self.output_counts[low]+=1
        if low==15:
            previous=self.memory.latch
            self.memory.page(value)
            if (previous^self.memory.latch)&16:self.rom_switches+=1
            if self.memory.latch&8:raise AssertionError('ROM requested unsupported shadow display')
            if len(self.events)<3000:self.events.append((r[PC],port,value,self.memory.latch))
        elif low==0xf4:
            if value!=0xc0:raise AssertionError(f'Unexpected F4 map {value:02X}')
            self.memory.f4=value
        elif low==0xff:
            if value:raise AssertionError(f'Unexpected video/EXROM control {value:02X}')
            self.memory.ff=value
        elif low==0xf5:self.ay_select=value&15
        elif low==0xf6:
            self.ay[self.ay_select]=value
            self.ay_events.append((self.ay_select,value))
        elif low==0xfe:self.border=value&7
        else:raise AssertionError(f'Unsupported OUT {port:04X}={value:02X} at {r[PC]:04X} ROM{(self.memory.latch>>4)&1}')
    def read_port(self,r,port):
        low=port&255
        if low==0xfe:
            v=31
            for row in range(8):
                if not port&(1<<(8+row)):v &= self.rows[row]
            return 0xe0|v
        if low==0xf6:return self.ay[self.ay_select]
        raise AssertionError(f'Unsupported IN {port:04X} at {r[PC]:04X}')
    def run_frames(self,n):
        r=self.cpu.registers;m=self.memory;ops=self.cpu.opcodes
        target=(self.frame+n)*58800
        while r[T]<target:
            pc=r[PC]
            self.coverage.add(((m.latch>>4)&1,pc))
            ops[m[pc]]();self.operations+=1
            if r[T]//58800>self.frame:
                self.frame=r[T]//58800
                if r[IFF]:self.cpu.accept_interrupt(r,m,pc)
    def press(self,*keys,frames=8):
        self.rows=[31]*8
        for key in keys:
            row,bit=KEYS[key.lower()];self.rows[row]&=~(1<<bit)
        self.run_frames(frames)
        self.rows=[31]*8;self.run_frames(6)
    def type_text(self,text):
        # Editor redraw/tokenization can still be busy after accepting the last line.
        self.run_frames(100)
        for c in text:
            if c=='\n':self.press('enter');self.run_frames(100)
            elif c in SYMBOLS:self.press('symbol',SYMBOLS[c])
            elif c.isupper():self.press('shift',c.lower())
            else:self.press(c.lower())
    def screenshot(self,path):
        from PIL import Image
        image=Image.new('RGB',(256,192))
        ram=self.memory.home
        for y in range(192):
            for x in range(256):
                b=ram[((y&0xc0)<<5)|((y&7)<<8)|((y&0x38)<<2)|(x>>3)]
                a=ram[0x1800+(y>>3)*32+(x>>3)]
                color=(a&7) if b&(128>>(x&7)) else ((a>>3)&7)
                level=255 if a&64 else 205
                image.putpixel((x,y),(level if color&2 else 0,level if color&4 else 0,level if color&1 else 0))
        image.resize((768,576)).save(path)
    def report(self):
        return {'pc':f'{self.cpu.registers[PC]:04X}','frames':self.frame,'operations':self.operations,
                'rom_switches':self.rom_switches,'paging_latch':self.memory.latch,
                'output_counts':{f'{k:02X}':v for k,v in self.output_counts.items()},
                'ay_events':len(self.ay_events),'ay_event_values':self.ay_events[:100],
                'paging_events':self.events,
                'model':'functional Z80 + separate HOME/SRAM; no bus timing or contention'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--frames',type=int,default=240)
    p.add_argument('--basic',action='store_true');a=p.parse_args()
    out=ROOT/'build/rom';m=Machine();m.run_frames(a.frames);m.screenshot(out/'boot.png')
    if a.basic:
        m.press('shift','6');m.press('enter');m.run_frames(60);m.screenshot(out/'basic.png')
    (out/'execution.json').write_text(json.dumps(m.report(),indent=2))
    print({k:v for k,v in m.report().items() if k!='paging_events'})


if __name__=='__main__':main()
