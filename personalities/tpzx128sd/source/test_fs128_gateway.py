"""Service entry, lock preservation, resource budget; no electrical timing claim."""
import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
from pio_model import assemble,SM
from test_stock128 import AdapterBus


class GatewayBus(AdapterBus):
    def __init__(self):
        super().__init__()
        ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        self.latch=SM(ns['_fs128_latch'],self,in_base=2,out_base=22,jmp_pin=11,side=12)
        self.latch.y=4


class GatewayTests(unittest.TestCase):
    def test_parked_start_preserves_initial_rom_one_gate(self):
        ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        control=Mock();address=Mock();latch=Mock();dma=Mock();new_latch=Mock()
        def reset(held,parked,half):
            self.assertEqual((held,parked,half),(False,True,1))
            ns['_stock128']=(control,address,latch,dma)
        ns.update(reset_stock128=reset,Pin=Mock(IN=0,OUT=1),PIO=Mock(),
                  StateMachine=Mock(return_value=new_latch),mem32={})
        ns['start_fs128'](host_parked=True,initial_rom_half=1)
        self.assertEqual(ns['_fs128_program_live'][5],(ns['PIO'].OUT_HIGH,))
        ns['StateMachine'].assert_called_once()
        new_latch.active.assert_called_once_with(1)

    def test_sd_command_crc_matches_initialization_vectors(self):
        ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        self.assertEqual(ns['_fs128_sd_crc'](0,0),0x95)
        self.assertEqual(ns['_fs128_sd_crc'](8,0x1aa),0x87)
        self.assertEqual(ns['_fs128_sd_crc'](17,0),0x55)
    def test_sd_failure_reports_commands_and_disconnects_bus_without_blink_loop(self):
        ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        class Card:
            def __init__(self,*args,**kwargs):
                self.baudrate=kwargs['baudrate']
                if self.baudrate!=100_000:raise AssertionError('Unexpected SD trial speed')
                for _ in range(15):self.cmd(41,0x40000000,0)
                raise OSError('timeout waiting for v2 card')
            def cmd(self,*args,**kwargs):return 1
        pins=Mock(IN=0,OUT=1);spi=Mock()
        fw=SimpleNamespace(MQ=Mock(),SDCard=Card)
        ns['Pin']=pins
        ns['_stock128']=(Mock(),None,None,None)
        with patch.dict('sys.modules',{'machine':SimpleNamespace(SoftSPI=Mock(return_value=spi))}):
            with self.assertRaisesRegex(RuntimeError,'last .*41, 1073741824, 1'):
                ns['_fs128_activate_sd'](fw)
        fw.MQ.active.assert_called_once_with(0)
        ns['_stock128'][0].active.assert_called_once_with(0)
        self.assertEqual(pins.call_args_list[0].args,(12,1))
        spi.deinit.assert_called_once_with()
    def test_sd_return_reassigns_memory_pins_before_resuming_controller(self):
        ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        registers={0x40014004+8*pin:5 for pin in (19,20,21)}
        controller=Mock()
        ns.update(mem32=registers,_stock128=(controller,None,None,None))
        ns['_fs128_resume_memory']()
        self.assertEqual(list(registers.values()),[7,7,7])
        controller.active.assert_called_once_with(1)
    def test_fits_entire_pio_zero(self):
        ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        self.assertEqual(len(ns['_fs128_latch'][0]),32)
        for half in (0,1):
            program=ns['_fs128_program'](half)
            self.assertEqual(program[5],(ns['PIO'].OUT_HIGH if half else ns['PIO'].OUT_LOW,))
            self.assertEqual(program[1:3],[-1,-1])
    def test_page_all_banks_then_cooperative_request(self):
        bus=GatewayBus()
        for half in (0,1):
            for bank in range(8):
                bus.write(bank|(half<<4));bus.memory_cycle(0x100);bus.memory_cycle(0x100)
                self.assertEqual(bus.memory_cycle(0xc000,True)['address_gpio_nibble'],bank*2)
                self.assertEqual((bus.state>>22)&1,half)
        word=bus.address.x
        bus.write(0,port=0x0e)
        self.assertEqual(bus.irq&5,1)
        self.assertEqual(bus.address.x,word)
        self.assertEqual(bus.state&(1<<12),1<<12)
        pc=bus.latch.pc;bus.tick(50)
        self.assertEqual(bus.latch.pc,pc)  # parked until gateway changes PIO0
    def test_locked_bank_ignores_odd_writes_but_allows_service(self):
        bus=GatewayBus()
        bus.write(0x35);bus.memory_cycle(0x100);bus.memory_cycle(0x100)
        for value in (0,1,7):bus.write(value)
        self.assertEqual(bus.irq,0)
        self.assertEqual(bus.memory_cycle(0xc000,True)['address_gpio_nibble'],10)
        bus.write(0,port=0x0e)
        self.assertEqual(bus.irq&5,5)
        self.assertEqual((bus.state>>22)&1,1)
    def test_old_runtime_matches(self):
        a=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        b=assemble('references/rp2-v1.20.0.py',native_dma=False,namespace=True,
                   extra_file='firmware/personality128_fs.py')
        self.assertEqual(list(a['_fs128_latch'][0]),list(b['_fs128_latch'][0]))
    def test_runtime_restores_bank_half_lock_without_restarting_memory_control(self):
        for half,locked,bank in ((0,False,0),(1,False,7),(1,True,5)):
            ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
            control=Mock();address=Mock();latch=Mock();dma=Mock();new_latch=Mock()
            address.tx_fifo.return_value=0;address.rx_fifo.return_value=0
            address.get.return_value=(bank<<5)|4;latch.rx_fifo.return_value=0
            regs={0x50200030:5 if locked else 1,0xd0000004:(half<<22)|(1<<14)}
            regs[0x50000800]=63
            def verify_dma_restart(**kwargs):
                self.assertEqual(regs[0x50000800],0)
            dma.config.side_effect=verify_dma_restart
            def sm_factory(index,*args,**kwargs):
                if args:args[0][1]=0
                return new_latch
            ns.update(_stock128=(control,address,latch,dma),mem32=regs,PIO=Mock(),
                      Pin=Mock(IN=0,OUT=1),StateMachine=Mock(side_effect=sm_factory))
            saved=ns['fs128_enter']()
            self.assertEqual(saved,{'word':(bank<<5)|4,'half':half,'locked':locked})
            self.assertFalse(control.active.called)
            result=ns['fs128_leave']()
            self.assertEqual(result['bank'],bank)
            self.assertEqual(result['rom_half'],half)
            self.assertEqual(result['locked'],locked)
            self.assertFalse(control.active.called)
            self.assertEqual(ns['_fs128_program_live'][5],
                             (ns['PIO'].OUT_HIGH if half else ns['PIO'].OUT_LOW,))
            if locked:
                self.assertIn('jmp(20)',[c.args[0] for c in new_latch.exec.call_args_list])
            self.assertIsNone(ns['_fs128_session'])
    def test_no_service_request_means_no_hardware_mutation(self):
        ns=assemble(namespace=True,extra_file='firmware/personality128_fs.py')
        ns.update(mem32={0x50200030:0},Pin=Mock(),PIO=Mock(),StateMachine=Mock())
        with self.assertRaises(RuntimeError):ns['fs128_enter']()
        ns['Pin'].assert_not_called();ns['StateMachine'].assert_not_called()


if __name__=='__main__':unittest.main()
