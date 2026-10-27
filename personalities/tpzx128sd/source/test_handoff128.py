"""Actual Z80 handoff plus Pico sequencing contracts, without bus timing claims."""
from collections import deque
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from build_handoff128 import build
from rom_machine import Machine,Memory,PC


class GateMemory(Memory):
    def __init__(self,roms,owner):
        super().__init__(roms);self.owner=owner
        # On the real board DOCK bypasses GPIO22 and addresses SRAM's
        # low region, not either ROM half (see tspico-mapping-analysis.json).
        self.dock_low=[0x5a]*16384
    def __getitem__(self,address):
        if address<0x4000 and self.f4&(1<<(address>>13)):
            return self.dock_low[address]
        if address<0x4000 and self.owner.phase!='running':
            if self.owner.phase=='gate':
                self.owner.gate_reads+=1
                if self.owner.release and self.owner.gate_reads>=100:
                    self.owner.phase='running'
                    self.owner.release_pc=self.owner.cpu.registers[PC]
                    return super().__getitem__(address)
            return self.roms[1][address]
        return super().__getitem__(address)


class HandoffMachine(Machine):
    def __init__(self,mode,release=True,ack=True,dock_poll=False):
        rom=Path('build/rom/TPZX128.ROM' if mode=='zx128' else 'build/fs128-rom/TPZXSD.ROM').read_bytes()
        self.phase='stock';self.release=release;self.ack=ack;self.dock_poll=dock_poll
        self.gate_reads=0;self.ack_reads=0;self.packet=[];self.release_pc=None
        super().__init__([rom[:16384],rom[16384:]])
        self.memory=GateMemory([rom[:16384],rom[16384:]],self)
        # Simulator must retain the gate-aware memory object.
        from skoolkit.simulator import Simulator
        self.cpu=Simulator(self.memory,config={'fast_ldir':True,'fast_djnz':True,'frame_duration':58800,'int_active':32})
        self.cpu.set_tracer(self)
        code,_,self.manifest=build(mode)
        for offset,value in enumerate(code):self.memory[0x8000+offset]=value
        self.cpu.registers[PC]=0x8000
    def write_port(self,r,port,value,offset):
        low=port&255
        if low==14:
            assert self.phase=='stock'
            assert 0x8000<=r[PC]<0xa000
            self.packet.append(value)
        elif low==0xf4 and value in (0,3):
            self.memory.f4=value
            if value==3:assert self.phase=='gate'
        else:super().write_port(r,port,value,offset)
    def read_port(self,r,port):
        if port&255==14:
            self.ack_reads+=1
            if self.ack and self.ack_reads>=5:
                assert self.memory.f4==0
                self.phase='gate'
                if self.dock_poll:self.memory.f4=3
                return 0xa7
            return 0x5a
        return super().read_port(r,port)


class HandoffTests(unittest.TestCase):
    def test_queue_has_no_reset_jobs_and_preserves_dependency_order(self):
        import tempfile,json
        from start_handoff128 import queue_handoff
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch('pico_debug.time.time_ns',return_value=1234567890000000000):
                jobs=queue_handoff(root,'zx128')
            self.assertEqual(len(jobs),7)
            self.assertFalse(any(j['requires_reset'] for j in jobs))
            ordered=[json.loads(p.read_text())['id'] for p in sorted((root/'pending').glob('*.json'))]
            self.assertEqual(ordered,[j['id'] for j in jobs])
            self.assertEqual(jobs[-1]['action'],'handoff128-stock-run')
            with self.assertRaises(RuntimeError):queue_handoff(root,'zx128')

    def test_both_modes_reach_128_menu_without_reset(self):
        for mode,number in (('zx128',1),('zx128sd',2)):
            with self.subTest(mode=mode):
                m=HandoffMachine(mode);m.run_frames(240)
                self.assertEqual(m.packet,[0x48,0x31,number,0x48^0x31^number])
                self.assertEqual(m.phase,'running')
                self.assertEqual(m.manifest['rom_poll_f4'],0)
                self.assertTrue(0x8000<=m.release_pc<0xa000)
                self.assertGreater(m.rom_switches,0)
                m.screenshot(Path('build/handoff128/'+mode+'-menu.png'))
                m.press('shift','6');m.press('enter');m.run_frames(50)
                m.type_text('print 1+2\n');m.run_frames(50)
                self.assertFalse(getattr(m,'service',False))
                # Result '3' at text row 1, column 0, using the ROM glyph.
                self.assertEqual([m.memory[0x4020+256*y] for y in range(8)],
                                 m.memory.roms[1][0x3c00+ord('3')*8:0x3c00+ord('3')*8+8])
                m.screenshot(Path('build/handoff128/'+mode+'-basic.png'))
    def test_no_ack_stays_in_home_without_mapping_dock(self):
        m=HandoffMachine('zx128',ack=False);m.run_frames(30)
        self.assertEqual(m.phase,'stock')
        self.assertEqual(m.memory.f4,0)
        self.assertTrue(0x8000<=m.cpu.registers[PC]<0xa000)
    def test_no_gate_release_fails_red_without_entering_rom(self):
        m=HandoffMachine('zx128',release=False);m.run_frames(300)
        self.assertEqual(m.phase,'gate')
        self.assertEqual(m.border,2)
        self.assertTrue(any(pc==m.manifest['symbols']['failed'] for _,pc in m.coverage))

    def test_original_low_dock_mapping_reproduces_red_timeout(self):
        m=HandoffMachine('zx128',dock_poll=True);m.run_frames(300)
        self.assertEqual(m.phase,'gate')
        self.assertEqual(m.memory.f4,3)
        self.assertEqual(m.border,2)
        self.assertEqual(m.gate_reads,0)
        self.assertTrue(any(pc==m.manifest['symbols']['failed'] for _,pc in m.coverage))

    def test_pico_acknowledges_only_after_memory_disabled_and_releases_last(self):
        for mode,number,resume in (('zx128',1,False),('zx128sd',2,False),('zx128',1,True)):
            events=[];packet=deque((0x48,0x31,number,0x48^0x31^number))
            mq=SimpleNamespace(rx_fifo=lambda:len(packet),tx_fifo=lambda:0,get=packet.popleft,
                               put=lambda value:events.append(('ack',value)),active=lambda value:events.append(('io',value)))
            # First FIFO check must see idle; the host sends its packet after arming.
            rx=mq.rx_fifo;first=[not resume]
            def rx_fifo():
                if first[0]:first[0]=False;return 0
                return rx()
            mq.rx_fifo=rx_fifo
            class Pin:
                OUT=1
                def __init__(self,pin,*args,**kwargs):events.append(('pin',pin,kwargs.get('value')))
            class SM:
                def __init__(self,index):self.index=index
                def active(self,value):events.append(('sm',self.index,value))
                def exec(self,code):events.append(('exec',code))
            ns={'_stock128':None,'mem32':{0x50300000:3,0xd0000004:1<<14},'Pin':Pin,'StateMachine':SM,
                'asm_pio':lambda **kwargs:lambda fn:fn,'PIO':SimpleNamespace(OUT_HIGH=1,SHIFT_LEFT=0)}
            def start(**kwargs):
                events.append(('start',kwargs));ns['_stock128']=(SM(4),SM(5),SM(0),None)
                return {'started':True}
            ns.update(start_stock128=start,start_fs128=start,fs128_run_basic=lambda:events.append(('serve',)))
            exec(Path('firmware/handoff128.py').read_text(),ns)
            import time
            fake_time=SimpleNamespace(ticks_ms=lambda:0,ticks_diff=lambda a,b:0,sleep_ms=lambda n:None)
            with patch.dict('sys.modules',{'tspico':SimpleNamespace(MQ=mq,TSP=SimpleNamespace(zx48=False)),'time':fake_time}):
                ns['handoff128_wait'](mode,resume=resume)
            self.assertLess(events.index(('pin',22,1)),events.index(('ack',0xa7)))
            start_index=next(i for i,e in enumerate(events) if e[0]=='start')
            self.assertEqual(events[start_index][1],{'host_parked':True,'initial_rom_half':1})
            self.assertGreater(events.index(('exec','out(pins,1)')),start_index)
            self.assertEqual(('serve',) in events,mode=='zx128sd')

    def test_rom_probe_preserves_memory_controller_and_decodes_capture(self):
        from pio_model import assemble
        from unittest.mock import Mock
        ns=assemble(namespace=True,extra_file='firmware/handoff128.py')
        control,address,latch,dma=[Mock() for _ in range(4)]
        probe=Mock()
        ns.update(_stock128=(control,address,latch,dma),Pin=Mock(IN=0,OUT=1),
                  PIO=Mock(),StateMachine=Mock(return_value=probe))
        with self.assertRaises(RuntimeError):ns['handoff128_probe_arm']()
        ns['StateMachine'].assert_not_called()
        ns['handoff128_probe_arm'](True)
        control.active.assert_not_called();address.active.assert_not_called()
        latch.active.assert_called_once_with(0);dma.active.assert_called_once_with(0)
        self.assertEqual(len(ns['_handoff128_rom_probe'][0]),6)
        probe.rx_fifo.return_value=1
        probe.get.return_value=0xf3|(4<<13)|(1<<17)|(1<<24)
        sample=ns['handoff128_probe_read']()['first_rom_reads'][0]
        self.assertEqual((sample['data'],sample['address_nibble'],sample['enables'],sample['rom_half'],sample['roscs']),
                         ('0xf3',4,1,0,1))

if __name__=='__main__':unittest.main()
