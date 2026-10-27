"""Independent legacy wire peer for executing the diagnostic's real Z80 code.

No PIO/SPI timing or Python handler scheduling is modeled here. Files are
actual TAP bytes; the peer validates the framing and checksums it receives.
"""
from build_fs128_probe import build,tape
from rom_machine import Machine,Memory,PC


class ServiceMemory(Memory):
    deny_cartridge=False
    def __getitem__(self,address):
        if self.deny_cartridge and address&65535<0x4000:
            raise AssertionError('Cartridge ROM read during SD service: %04X'%address)
        return super().__getitem__(address)


def xor(data):
    n=0
    for b in data:n^=b
    return n


def blocks(data):
    output=[];offset=0
    while offset<len(data):
        length=int.from_bytes(data[offset:offset+2],'little');offset+=2
        body=data[offset:offset+length];offset+=length
        if len(body)!=length or length<2 or xor(body):raise ValueError('Malformed TAP fixture')
        output.append(body)
    return output


class LegacyWire:
    def __init__(self):
        self.files={'FS128.TAP':tape('FS128',bytes(range(256)))}
        self.directory_listing=''.join(s.ljust(32) for s in ('Path:/TAP/128','SD card','File Name','-'*32,'FS128.TAP'))
        self.queue=[0xa5,1,7,0];self.state='header';self.buffer=[]
        self.mounted=[];self.index=0;self.closed=False;self.headers=[];self.commands=[]
    def send(self,value):
        self.buffer.append(value)
        if self.state=='header':
            if len(self.buffer)==1:self.queue.append(1)
            if len(self.buffer)<10:return
            pre=bytes(self.buffer);self.buffer=[]
            if xor(pre) or pre[2]!=255:raise AssertionError('Bad Z80 preheader')
            self.headers.append(pre)
            self.length=pre[7]|pre[8]<<8
            if pre[0]==66:
                self.direction=pre[1];self.queue.extend((0x40,1));self.state='command'
            elif pre[1] in (1,2,3):
                self.flag=pre[0];self.queue.append(0x40);self.state='echo'
            elif pre[0]==0 and pre[1]==0:
                self.queue.append(0x40);self.state='save_header'
            else:raise AssertionError('Unexpected preheader')
        elif self.state=='command':
            if len(self.buffer)<self.length+4:return
            body=bytes(self.buffer);self.buffer=[]
            if body[:3]!=bytes((68,self.length,0)) or xor(body):raise AssertionError('Bad command body')
            cmd=body[3:-1].decode('ascii').upper();self.commands.append(cmd)
            status=1
            message=None
            if cmd=='TPI:CD /':pass
            elif cmd=='TPI:PATH':message=b'/TAP/128\r'
            elif cmd=='TPI:DIR':message=b'FS128.TAP\r'
            elif cmd.startswith('TPI:DIRPAGE '):
                page=int(cmd[12:],16)
                header=self.directory_listing[:128];entries=self.directory_listing[128:]
                start=page*448
                more=start+448<len(entries)
                message=(('+' if more else '.')+header+entries[start:start+448]).encode('ascii')
            elif cmd=='TPI:CLOSE':self.mounted=[]
            elif cmd=='TPI:FSEND':self.closed=True
            elif self.direction==1 and cmd[4:] in self.files:
                self.mounted=blocks(self.files[cmd[4:]]);self.index=0
            else:status=5
            if message is None:self.queue.extend((0x40,status))
            else:self.queue.extend(bytes((0x40,0x81,status))+message+b'\0')
            self.state='header'
        elif self.state=='echo':
            self.buffer=[]
            if value!=self.flag:raise AssertionError('Wrong expected-flag echo')
            block=self.mounted[self.index];self.index+=1
            if len(block)!=self.length+2:raise AssertionError('Wrong requested payload length')
            self.queue.extend(block);self.state='residual'
        elif self.state=='residual':
            self.buffer=[]
            if value:raise AssertionError('Z80 reported a checksum mismatch')
            self.queue.extend((0x40,1));self.state='header'
        elif self.state=='save_header':
            if len(self.buffer)<21:return
            header=bytes(self.buffer);self.buffer=[]
            if xor(header) or header[:3]!=bytes((0,0,0)) or header[3]>3:
                raise AssertionError('Bad SAVE header')
            self.save_header=header;self.save_length=int.from_bytes(header[14:16],'little')
            self.queue.extend((0x40,1));self.state='save_data'
        elif self.state=='save_data':
            if len(self.buffer)<self.save_length+4:return
            body=bytes(self.buffer);self.buffer=[]
            if body[:3]!=bytes((255,0,0)) or xor(body):raise AssertionError('Bad SAVE payload')
            name=self.save_header[4:14].decode('ascii').rstrip()
            def wrap(block):return len(block).to_bytes(2,'little')+block
            tape_header=self.save_header[2:]
            tape_data=bytes([255])+body[3:-1]
            self.files[name+'.TAP']=wrap(tape_header)+wrap(tape_data+bytes([xor(tape_data)]))
            self.queue.extend((0x40,1));self.state='header'
    def receive(self):return self.queue.pop(0) if self.queue else 0


class ProbeMachine(Machine):
    def __init__(self,break_restore=False,fast_settle=True):
        roms,self.probe=build();super().__init__(roms)
        self.memory.__class__=ServiceMemory
        self.wire=LegacyWire();self.service=False;self.entered=False
        self.saved_latch=None;self.break_restore=break_restore
        if fast_settle:
            # This peer answers immediately; elide only the established
            # housekeeping delay, never handshake, parser or payload code.
            # The built hardware ROM retains the real delay unchanged.
            self.cpu.opcodes=list(self.cpu.opcodes)
            push_bc=self.cpu.opcodes[0xc5];ret=self.cpu.opcodes[0xc9]
            def skip_settle():
                if self.cpu.registers[PC]==self.probe['symbols']['legacy_settle']:ret()
                else:push_bc()
            self.cpu.opcodes[0xc5]=skip_settle
    def write_port(self,r,port,value,offset):
        low=port&255
        if low==0xf4:self.memory.f4=value
        elif low==0x0e:
            if not self.entered:
                self.entered=True;self.service=True;self.saved_latch=self.memory.latch
                self.memory.deny_cartridge=True
            else:self.wire.send(value)
        elif low==0x0f and self.service:
            raise AssertionError('Modern SYNC sent to legacy peer')
        else:super().write_port(r,port,value,offset)
    def read_port(self,r,port):
        if port&255 in (0x0e,0x0f):
            value=self.wire.receive()
            if self.wire.closed and not self.wire.queue:
                self.service=False
                self.memory.deny_cartridge=False
                self.memory.latch=0 if self.break_restore else self.saved_latch
            return value
        return super().read_port(r,port)
