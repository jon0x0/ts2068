import unittest
from fs128_probe_model import ProbeMachine,blocks
from rom_machine import PC
from z80_link import link


class ProbeTests(unittest.TestCase):
    def execute(self,broken=False):
        m=ProbeMachine(break_restore=broken)
        for _ in range(150):
            m.run_frames(1)
            if m.cpu.registers[PC] in (0x6305,m.probe['symbols']['pass']+5):break
        else:self.fail('Z80 diagnostic did not reach its terminal checkpoint')
        return m
    def test_real_z80_detect_load_save_reload_and_paging(self):
        m=self.execute()
        self.assertEqual(m.border,4)
        self.assertEqual(m.memory.home[0x1800+20*32:0x1800+21*32],[0x20]*32)
        self.assertEqual(blocks(m.wire.files['FSOUT.TAP'])[1][1:-1],bytes(range(256)))
        self.assertEqual(m.memory.banks[3][0],0x53)
        self.assertEqual(m.memory.banks[7][0],0x77)
        self.assertEqual(m.memory.latch,0x13)
        self.assertEqual(m.memory.home[0xC3A0-0x4000],1)
        self.assertTrue(m.wire.closed)
        self.assertFalse(m.wire.queue)
        self.assertEqual(m.wire.commands[0],'TPI:PATH')
        self.assertNotIn('TPI:CD /',m.wire.commands)
    def test_lost_paging_state_is_detected(self):
        m=self.execute(broken=True)
        self.assertEqual(m.border,2)
        self.assertNotEqual(m.memory.home[0x1800+20*32:0x1800+21*32],[0x20]*32)
    def test_linker_preserves_probe_checksum_expression(self):
        data,_=link("db $44^8^'t'^'p'^'i'^':'^'c'^'d'^' '^'/'")
        self.assertEqual(data,bytes([19]))
        with self.assertRaises(ValueError):link('db UNKNOWN_NAME')


if __name__=='__main__':unittest.main()
