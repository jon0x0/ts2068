"""Assemble the real firmware with MicroPython's assembler and model its instructions.

The scheduler has no input synchronizers, fractional-divider jitter or analog
delays. It validates logic and ordering, not an RP2040/Z80 timing guarantee.
"""
import collections
import array
import json
import sys
import types
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MASK=0xffffffff


def assemble(reference='references/rp2.py', native_dma=True, namespace=False, extra_file=None):
    names=('_rp2','rp2','machine','micropython','uarray')
    old={n:sys.modules.get(n) for n in names}
    try:
        low=types.ModuleType('_rp2')
        low.PIO=type('PIO',(),dict(OUT_LOW=2,OUT_HIGH=3,SHIFT_LEFT=0,SHIFT_RIGHT=1))
        low.StateMachine=object
        if native_dma:low.DMA=object
        machine=types.ModuleType('machine');machine.Pin=object;machine.freq=lambda x:x;machine.mem32={}
        micro=types.ModuleType('micropython');micro.const=lambda x:x
        sys.modules.update({'_rp2':low,'machine':machine,'micropython':micro})
        sys.modules['uarray']=array
        rp2=types.ModuleType('rp2');sys.modules['rp2']=rp2
        exec(compile((ROOT/reference).read_text(),reference,'exec'),rp2.__dict__)
        firmware={'__name__':'personality128_test'}
        exec(compile((ROOT/'firmware/personality128.py').read_text(),'firmware/personality128.py','exec'),firmware)
        if extra_file:
            exec(compile((ROOT/extra_file).read_text(),extra_file,'exec'),firmware)
        if namespace:return firmware
        return {name:firmware[name] for name in ('memory_enable','memory_enable_sram','memory_address','paging_write','paging_observer')}
    finally:
        for name,value in old.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value


class SM:
    def __init__(self,prog,bus,in_base=0,out_base=0,set_base=0,set_count=0,jmp_pin=0,side=None,out_count=32):
        self.prog=prog;self.words=list(prog[0]);self.bus=bus
        self.bottom=(prog[3]>>7)&31;self.top=(prog[3]>>12)&31
        self.in_right=bool(prog[4]&(1<<18));self.out_right=bool(prog[4]&(1<<19))
        self.in_base=in_base;self.out_base=out_base;self.set_base=set_base;self.set_count=set_count
        self.jmp_pin=jmp_pin;self.side=side
        self.out_count=out_count
        self.x=self.y=self.isr=self.osr=self.pc=self.delay=0
        self.rx=collections.deque();self.tx=collections.deque();self.dropped=0
    def pins(self):
        v=self.bus.inputs()
        return ((v>>self.in_base)|(v<<(32-self.in_base)))&MASK
    def source(self,src):
        return {0:self.pins(),1:self.x,2:self.y,3:0,6:self.isr,7:self.osr}[src]
    def dest(self,dest,value,count=None):
        if count is None:count=self.out_count
        if dest==0:self.bus.output(self.out_base,count,value)
        elif dest==1:self.x=value&MASK
        elif dest==2:self.y=value&MASK
        elif dest==3:pass
        elif dest==6:self.isr=value&MASK
        elif dest==7:self.osr=value&MASK
        else:raise AssertionError(('destination',dest))
    def step(self):
        if self.delay:self.delay-=1;return
        word=self.words[self.pc];op=word>>13
        if self.side is not None:self.bus.output(self.side,1,(word>>12)&1)
        delay=(word>>8)&(15 if self.side is not None else 31)
        nxt=self.bottom if self.pc==self.top else self.pc+1
        if op==0:
            cond=(word>>5)&7
            if cond==0:take=True
            elif cond==1:take=self.x==0
            elif cond==2:take=self.x!=0;self.x=(self.x-1)&MASK
            elif cond==4:take=self.y!=0;self.y=(self.y-1)&MASK
            elif cond==6:take=bool(self.bus.inputs()&(1<<self.jmp_pin))
            else:raise AssertionError(('condition',cond))
            if take:nxt=word&31
        elif op==1:
            src=(word>>5)&3;pin=word&31;pol=(word>>7)&1
            if src==0:
                if bool(self.bus.inputs()&(1<<pin))!=bool(pol):return
            elif src==2:
                if bool(self.bus.irq&(1<<pin))!=bool(pol):return
                if pol:self.bus.irq &= ~(1<<pin)
            else:raise AssertionError('Unsupported WAIT source')
        elif op==2:
            count=(word&31) or 32;value=self.source((word>>5)&7)&((1<<count)-1)
            if self.in_right:self.isr=((self.isr>>count)|(value<<(32-count)))&MASK
            else:self.isr=((self.isr<<count)|value)&MASK
        elif op==3:
            count=(word&31) or 32
            if self.out_right:value=self.osr&((1<<count)-1);self.osr>>=count
            else:value=self.osr>>(32-count);self.osr=(self.osr<<count)&MASK
            self.dest((word>>5)&7,value,count)
        elif op==4:
            if word&128:
                self.osr=self.tx.popleft() if self.tx else self.x
            else:
                if len(self.rx)<4:self.rx.append(self.isr)
                else:self.dropped+=1
                self.isr=0
        elif op==5:
            value=self.source(word&7);operation=(word>>3)&3
            if operation==1:value=(~value)&MASK
            elif operation:raise AssertionError('Unsupported MOV operation')
            self.dest((word>>5)&7,value)
        elif op==6:
            if word&0x40:self.bus.irq &= ~(1<<(word&7))
            else:self.bus.irq |= 1<<(word&7)
        elif op==7:
            dest=(word>>5)&7;value=word&31
            if dest==0:self.bus.output(self.set_base,self.set_count,value)
            else:self.dest(dest,value)
        else:raise AssertionError(('opcode',op))
        self.pc=nxt;self.delay=delay


class Bus:
    def __init__(self,slot=3,dma_delay=3,rom_memory="flash"):
        p=assemble();self.programs=p;self.state=(7<<19)|(1<<12);self.irq=0
        self.host={0:1,1:1,10:1,11:0,13:1,14:1,26:1};self.data=0
        self.enable=SM(p['memory_enable_sram' if rom_memory=='sram' else 'memory_enable'],self,set_base=19,set_count=3,jmp_pin=26)
        self.address=SM(p['memory_address'],self,out_base=15,jmp_pin=26)
        self.latch=SM(p['paging_write'],self,in_base=2,out_base=22,jmp_pin=11,side=12)
        self.observer=SM(p['paging_observer'],self,in_base=2,jmp_pin=11)
        self.address.x=slot;self.latch.y=slot
        self.output(15,4,slot)
        self.pending=[];self.ticks=0;self.dma_delay=dma_delay
    def output(self,base,count,value):
        mask=((1<<count)-1)<<base
        self.state=(self.state&~mask)|((value<<base)&mask)
    def inputs(self):
        v=self.state
        for pin,value in self.host.items():
            if value:v|=1<<pin
            else:v&=~(1<<pin)
        # U6 only presents host data to Pico when enabled for a selected OUT.
        if not self.state&(1<<12) and self.host[11]:v|=self.data<<2
        return v
    def tick(self,n):
        for _ in range(n):
            self.ticks+=1
            for sm in (self.enable,self.address,self.latch,self.observer):sm.step()
            if self.latch.rx:
                self.pending.append((self.ticks+self.dma_delay,self.latch.rx.popleft()))
            if self.pending and self.pending[0][0]<=self.ticks:
                _,value=self.pending.pop(0)
                if len(self.address.tx)>=4:raise AssertionError('DMA TX FIFO overflow')
                self.address.tx.append(value)
    def write(self,value,port=15):
        self.data=value;self.host.update({11:1,14:0 if port&0xf0==0 else 1,10:port&1})
        self.tick(100)             # Hold selected I/O for a generous functional test interval.
        self.host.update({11:0,14:1});self.tick(30)
    def memory_cycle(self,address,dock=False,write=False):
        self.host.update({13:0,26:int(not dock),1:int(bool(address&0xc000) or write)})
        self.tick(40)
        result={'address_gpio_nibble':(self.state>>15)&15,
                'rom_half':(self.state>>22)&1,'control':(self.state>>19)&7}
        self.host[13]=1;self.tick(20)
        return result


def report():
    bus=Bus()
    result={'instruction_counts':{n:len(p[0]) for n,p in bus.programs.items()},
            'pio1_total':sum(len(bus.programs[n][0]) for n in ('memory_enable','memory_address','paging_observer')),
            'scope':'Real assembled PIO instruction logic; scheduler and DMA delay are modeled, not hardware measurements',
            'bank_cases':[]}
    for bank in range(8):
        bus.write(bank)
        result['bank_cases'].append(bus.memory_cycle(0xc000,True))
    Path('build/rom/pio-report.json').write_text(json.dumps(result,indent=2))
    return result


if __name__=='__main__':print(json.dumps(report(),indent=2))
