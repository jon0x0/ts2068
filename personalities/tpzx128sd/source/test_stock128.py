"""Assembled PIO contracts; no claim about real bus propagation delays."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
from pio_model import assemble,Bus,SM

STOCK=Path(__file__).resolve().parent/'references/fs128/stock-pio.py'


def programs():
    ns=assemble(namespace=True,extra_file='firmware/personality128_stock.py')
    source=STOCK.read_text(encoding='utf-8');lines=source.splitlines()
    for node in ast.parse(source).body:
        if isinstance(node,ast.FunctionDef) and node.name in ('sel_bank','set_ctrl'):
            exec('\n'.join(lines[node.decorator_list[0].lineno-1:node.end_lineno]),ns)
    return ns


class AdapterBus(Bus):
    def __init__(self):
        super().__init__(slot=4,rom_memory='sram')
        p=programs()
        self.enable=SM(p['_stock128_control'],self,in_base=0,out_base=19,out_count=2,
                       set_base=21,set_count=1,jmp_pin=26)
        self.enable.tx.append(5)
        self.address=SM(p['sel_bank'],self,out_base=15,jmp_pin=26)
        self.address.x=4
        self.latch=SM(p['_stock128_latch'],self,in_base=2,out_base=22,jmp_pin=11,side=12)
        self.latch.y=4


class StockAdapterTests(unittest.TestCase):
    def test_controller_changes_only_stock_half_select_set_values(self):
        p=programs();old=list(p['set_ctrl'][0]);new=list(p['_stock128_control'][0])
        expected=[(word&~31)|(word&1) if word>>13==7 and (word>>5)&7==0 else word for word in old]
        self.assertEqual(new,expected)
        self.assertLessEqual(len(new)+len(p['sel_bank'][0]),32)
        self.assertLessEqual(len(p['_stock128_latch'][0]),32)
    def test_banks_halves_and_lock(self):
        bus=AdapterBus()
        for half in (0,1,0):
            for bank in range(8):
                bus.write(bank|(half<<4))
                # Stock selector caches before MREQ. The next ROM fetch
                # consumes its old cache; subsequent accesses use new data.
                bus.memory_cycle(0x100)
                self.assertEqual(bus.memory_cycle(0x200),
                                 dict(address_gpio_nibble=4,rom_half=half,control=1))
                self.assertEqual(bus.memory_cycle(0xc000,True),
                                 dict(address_gpio_nibble=bank*2,rom_half=half,control=5))
        bus.write(0x35);bus.memory_cycle(0x100);bus.memory_cycle(0x100)
        for value in (0,1,0x10,7):
            bus.write(value);bus.memory_cycle(0x100)
            self.assertEqual(bus.memory_cycle(0xc000,True),
                             dict(address_gpio_nibble=10,rom_half=1,control=5))
    def test_even_port_and_unselected_io_do_not_page(self):
        bus=AdapterBus()
        for port in (0x0e,0xfd):bus.write(0x37,port)
        bus.memory_cycle(0x100)
        self.assertEqual(bus.memory_cycle(0xc000,True)['address_gpio_nibble'],0)
        self.assertEqual((bus.state>>22)&1,0)
    def test_old_runtime_assembler_matches(self):
        a=assemble(namespace=True,extra_file='firmware/personality128_stock.py')
        b=assemble(reference='references/rp2-v1.20.0.py',native_dma=False,
                   namespace=True,extra_file='firmware/personality128_stock.py')
        for name in ('_stock128_control','_stock128_latch'):
            self.assertEqual(list(a[name][0]),list(b[name][0]))
    def test_start_owns_half_pin_only_in_paging_sm(self):
        ns=programs();machines={i:Mock() for i in range(8)}
        pin=Mock(IN=0,OUT=1,side_effect=lambda number,*args,**kwargs:number)
        ns.update(Pin=pin,StateMachine=Mock(side_effect=lambda i,*a,**k:machines[i]),
                  freq=lambda:270_000_000,PIO=Mock(),_abort_dma=Mock(),
                  mem32={0x5000000c+64*i:1 for i in range(12)})
        dma=Mock();dma.pack_ctrl.return_value=0x22000b;ns['DMA']=Mock(return_value=dma)
        with patch.dict('sys.modules',{'tspico_io':SimpleNamespace(sel_bank=ns['sel_bank'])}):
            with self.assertRaises(RuntimeError):ns['start_stock128']()
            result=ns['start_stock128'](True)
            calls=[c for c in ns['StateMachine'].call_args_list if c.args[1:]]
            self.assertEqual(calls[0].kwargs['set_base'],21)
            self.assertEqual(calls[0].kwargs['out_base'],19)
            self.assertEqual(calls[2].kwargs['out_base'],22)
            self.assertEqual(calls[2].kwargs['sideset_base'],12)
            self.assertEqual([i for i,m in machines.items() if m.active.call_args.args==(1,)],[0,4,5])
            machines[4].put.assert_called_once_with(5)
            machines[5].put.assert_called_once_with(4)
            self.assertEqual(result['rom_slot'],4)
            self.assertEqual(dma.config.call_args.kwargs['write'],0x50300014)
            ns['reset_stock128'](True)
            dma.close.assert_called_once()

    def test_parked_start_keeps_rom_one_gate_high_until_explicit_release(self):
        ns=programs();machines={i:Mock() for i in range(8)}
        pin=Mock(IN=0,OUT=1,side_effect=lambda number,*args,**kwargs:number)
        ns.update(Pin=pin,StateMachine=Mock(side_effect=lambda i,*a,**k:machines[i]),
                  freq=lambda:270_000_000,PIO=Mock(),_abort_dma=Mock(),
                  mem32={0x5000000c+64*i:1 for i in range(12)})
        dma=Mock();ns['DMA']=Mock(return_value=dma)
        with patch.dict('sys.modules',{'tspico_io':SimpleNamespace(sel_bank=ns['sel_bank'])}):
            result=ns['start_stock128'](host_parked=True,initial_rom_half=1)
        self.assertEqual(result['initial_rom_half'],1)
        half_calls=[c for c in pin.call_args_list if c.args[0]==22 and 'value' in c.kwargs]
        self.assertEqual([c.kwargs.get('value') for c in half_calls],[1])
        latch_call=[c for c in ns['StateMachine'].call_args_list if len(c.args)>1 and c.args[0]==0][0]
        self.assertEqual(latch_call.args[1][5],(ns['PIO'].OUT_HIGH,))


if __name__=='__main__':unittest.main()
