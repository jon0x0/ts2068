"""Desktop register-contract tests; not hardware timing validation."""
import types
import unittest
import sys
import array
from pathlib import Path
from unittest.mock import patch
from pio_model import assemble


class Registers(dict):
    def __init__(self):
        super().__init__();self.writes=[];self.stuck=False
    def __getitem__(self, address):
        return self.get(address, 0)
    def __setitem__(self, address, value):
        self.writes.append((address,value))
        if address==0x50000444 and not self.stuck:value=0
        if address==0x5000000c:value &= ~0x60000000
        super().__setitem__(address,value)


class DMATests(unittest.TestCase):
    def load(self):
        ns=assemble('references/rp2-v1.20.0.py',native_dma=False,namespace=True)
        self.assertEqual(ns['mem32'],{})
        ns['_sys']=types.SimpleNamespace(implementation=types.SimpleNamespace(_machine='Raspberry Pi Pico with RP2040'))
        regs=Registers();ns['mem32']=regs
        return ns,regs

    def test_old_assembler_matches_new(self):
        old=assemble('references/rp2-v1.20.0.py',native_dma=False)
        new=assemble()
        for name in old:self.assertEqual(list(old[name][0]),list(new[name][0]))
        self.assertEqual(assemble(namespace=True)['DMA_BACKEND'],'rp2.DMA')

    def test_configuration_and_close(self):
        ns,regs=self.load();dma=ns['DMA']()
        self.assertFalse(regs.writes)
        self.assertEqual(ns['DMA_BACKEND'],'RP2040 registers')
        ctrl=dma.pack_ctrl(size=2,inc_read=False,inc_write=False,treq_sel=4,high_pri=True)
        self.assertEqual(ctrl,0x22000b)
        dma.config(read=0x50200020,write=0x50300014,count=0xffffffff,ctrl=ctrl,trigger=True)
        self.assertEqual(regs.writes,[(0x5000000c,0x60000000),(0x50000000,0x50200020),
            (0x50000004,0x50300014),(0x50000008,0xffffffff),(0x5000000c,ctrl)])
        dma.close();self.assertEqual(regs[0x5000000c]&1,0)
        self.assertEqual(regs.writes[-1],(0x50000444,1))
        count=len(regs.writes);dma.close();self.assertEqual(len(regs.writes),count)
        with self.assertRaises(RuntimeError):dma.active(0)

    def test_platform_and_takeover_guards(self):
        ns,regs=self.load()
        ns['_sys']=types.SimpleNamespace(implementation=types.SimpleNamespace(_machine='RP2350'))
        with self.assertRaises(RuntimeError):ns['DMA']()
        with self.assertRaises(RuntimeError):ns['start'](4,rom_memory='sram')
        with self.assertRaises(ValueError):ns['start'](3,True,'sram')
        self.assertFalse(regs.writes)

    def test_abort_timeout(self):
        ns,regs=self.load();regs.stuck=True
        with self.assertRaisesRegex(RuntimeError,'timed out'):ns['_abort_dma'](0xfff)

    def test_repasting_preserves_active_objects_without_mmio(self):
        ns,regs=self.load();marker=object();ns['_keepalive']=marker
        rp2=types.ModuleType('rp2')
        for name in ('PIO','StateMachine','asm_pio'):setattr(rp2,name,ns[name])
        machine=types.ModuleType('machine')
        for name in ('Pin','freq','mem32'):setattr(machine,name,ns[name])
        with patch.dict(sys.modules,{'rp2':rp2,'machine':machine,'uarray':array}):
            exec(compile(Path('firmware/personality128.py').read_text(),'personality128.py','exec'),ns)
        self.assertIs(ns['_keepalive'],marker)
        self.assertFalse(regs.writes)

    def test_start_uses_stock_io_clock_and_fast_memory_clocks(self):
        ns,regs=self.load();configured={}
        class Pin:
            OUT=1;IN=0
            def __init__(self,*args,**kwargs):pass
        class PIO:
            def __init__(self,*args):pass
            def remove_program(self):pass
        class SM:
            def __init__(self,index,*args,**kwargs):
                if args:
                    if isinstance(args[0],list):
                        if args[0][1:3]!=[-1,-1]:raise AssertionError('Cached offsets were not invalidated')
                    configured[index]=kwargs
            def active(self,*args):pass
            def put(self,*args):pass
            def exec(self,*args):pass
        ns.update(Pin=Pin,PIO=PIO,StateMachine=SM)
        for name in ('memory_enable','memory_enable_sram','memory_address','paging_write','paging_observer'):
            ns[name][1]=5;ns[name][2]=9
        result=ns['start'](4,True,'sram')
        self.assertEqual(configured[0]['freq'],30_000_000)
        self.assertEqual(configured[4]['freq'],150_000_000)
        self.assertEqual(configured[5]['freq'],150_000_000)
        self.assertEqual(result[-2:],(4,'sram'))
        self.assertEqual(regs[0x5000000c],0x22000b)


if __name__=='__main__':unittest.main()
