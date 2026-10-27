"""Real BASIC ROM against an independent legacy peer; no electrical timing."""
from build_fs128_rom import build
from rom_machine import Machine,PC,SYMBOLS
from fs128_probe_model import LegacyWire,xor


class BasicMachine(Machine):
    def __init__(self):
        SYMBOLS['.']='m'
        pair,self.image,self.manifest=build()
        super().__init__([pair[:16384],pair[16384:]])
        self.wire=LegacyWire();self.wire.queue=[]
        self.service=False;self.sessions=0
        self.saved_latch=None
        self.cpu.opcodes=list(self.cpu.opcodes)
        push_bc=self.cpu.opcodes[0xc5];ret=self.cpu.opcodes[0xc9]
        def skip_settle():
            if self.cpu.registers[PC]==self.manifest['symbols']['legacy_settle']:ret()
            else:push_bc()
        self.cpu.opcodes[0xc5]=skip_settle
    def write_port(self,r,port,value,offset):
        low=port&255
        if low==0x0e:
            if not self.service:
                self.service=True;self.sessions+=1
                self.saved_latch=self.memory.latch
                self.wire.closed=False
                self.wire.queue=[0xa5,1,7,1,len(self.image)&255,len(self.image)>>8]+list(self.image)+[xor(self.image)]
            else:
                if r[PC]<0xa000:raise AssertionError('Service request not executed in HOME workspace')
                self.wire.send(value)
        elif low==0x0f and self.service:
            raise AssertionError('Paging/SYNC during SD transaction')
        else:super().write_port(r,port,value,offset)
    def read_port(self,r,port):
        if port&255 in (0x0e,0x0f):
            value=self.wire.receive()
            if self.wire.closed and not self.wire.queue:
                self.service=False;self.memory.latch=self.saved_latch
            return value
        return super().read_port(r,port)


if __name__=='__main__':
    m=BasicMachine();m.run_frames(240)
    m.press('shift','6');m.press('enter');m.run_frames(50)
    m.type_text('load "tpi:FS128.TAP" code 32768\n');m.run_frames(100)
    m.screenshot(__import__('pathlib').Path('build/fs128-rom/basic-load.png'))
    print({'sessions':m.sessions,'commands':m.wire.commands,'headers':[p.hex() for p in m.wire.headers],
           'pc':hex(m.cpu.registers[PC]),'data':m.memory.home[0x4000:0x4010]})
