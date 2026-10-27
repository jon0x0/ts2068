"""Real 128 BASIC parser, ROM hooks, and independent TAP peer."""
from pathlib import Path
import unittest
from fs128_basic_model import BasicMachine
from fs128_probe_model import blocks,xor,tape
from build_fs128_rom import build
from rom_machine import PC


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.machine=BasicMachine()
        self.machine.run_frames(240)
        self.machine.press('shift','6');self.machine.press('enter')
        self.machine.run_frames(50)

    def command(self,text):
        self.machine.type_text(text+'\n');self.machine.run_frames(100)
        self.assertFalse(self.machine.service,'BASIC left a file session open')
    def acknowledge(self):
        self.machine.press('enter');self.machine.run_frames(50)

    def test_01_load_save_reload_verify_and_program(self):
        m=self.machine
        self.assertEqual(m.memory[0x5cb3],0x9f)
        self.command('load "tpi:FS128.TAP" code 32768')
        self.assertEqual(bytes(m.memory.home[0x4000:0x4100]),bytes(range(256)))
        self.acknowledge()
        self.command('save "tpi:ROUND" code 32768,256')
        self.assertIn('ROUND.TAP',m.wire.files)
        self.assertEqual(blocks(m.wire.files['ROUND.TAP'])[1][1:-1],bytes(range(256)))
        self.acknowledge()
        m.memory.home[0x4000:0x4100]=[0]*256
        self.command('load "tpi:ROUND.TAP" code 32768')
        self.assertEqual(bytes(m.memory.home[0x4000:0x4100]),bytes(range(256)))
        self.acknowledge()
        self.command('verify "tpi:ROUND.TAP" code 32768')
        self.acknowledge()
        self.command('load "tpi:path"')
        self.assertEqual(m.wire.commands[-2:],['TPI:PATH','TPI:FSEND'])
        self.acknowledge()
        self.command('load "tpi:dir"')
        self.assertEqual(m.wire.commands[-2:],['TPI:DIRPAGE 0000','TPI:FSEND'])
        self.acknowledge()  # Final page acknowledgement, then normal BASIC status.
        self.acknowledge()
        self.command('10 print 42')
        self.command('save "tpi:BASIC"')
        self.assertEqual(blocks(m.wire.files['BASIC.TAP'])[0][1],0)
        self.acknowledge()
        self.command('new')
        m.press('shift','6');m.press('enter');m.run_frames(50)
        self.command('load "tpi:BASIC.TAP"')
        prog=m.memory[0x5c53]|m.memory[0x5c54]<<8
        self.assertEqual([m.memory[prog],m.memory[prog+1]],[0,10])
        self.acknowledge()
        self.command('run')
        m.screenshot(Path('build/fs128-rom/basic-roundtrip.png'))

    def test_99_reserved_code_transfer_is_rejected_without_overwriting_driver(self):
        m=self.machine
        self.acknowledge()
        self.command('load "tpi:FS128.TAP" code 40960')
        _,blob,_=build()
        self.assertEqual(bytes(m.memory.home[0xa000-0x4000:0xa000-0x4000+len(blob)]),blob)
        self.acknowledge()
        self.command('clear 60000')
        self.assertLess(m.memory[0x5cb2]|m.memory[0x5cb3]<<8,0xa000)

    def test_03_numeric_array_roundtrip_and_merge(self):
        m=self.machine
        program=bytes.fromhex('000a0a00f534320e00002a00000d')
        fixture=bytearray(tape('BASIC',program));fixture[3]=0
        fixture[18:20]=len(program).to_bytes(2,'little')
        fixture[20]=xor(fixture[2:20])
        m.wire.files['BASIC.TAP']=bytes(fixture)
        self.command('dim a(3)')
        self.acknowledge()
        self.command('let a(2)=42')
        self.acknowledge()
        self.command('save "tpi:ARRAY" data a()')
        original=blocks(m.wire.files['ARRAY.TAP'])
        self.assertEqual(original[0][1],1)
        self.acknowledge()
        self.command('clear')
        self.acknowledge()
        self.command('load "tpi:ARRAY.TAP" data a()')
        self.acknowledge()
        self.command('save "tpi:ARRAY2" data a()')
        self.assertEqual(blocks(m.wire.files['ARRAY2.TAP'])[1],original[1])
        self.acknowledge()
        self.command('10')
        self.command('20 print 7')
        self.command('merge "tpi:BASIC.TAP"')
        prog=m.memory[0x5c53]|m.memory[0x5c54]<<8
        self.assertEqual([m.memory[prog],m.memory[prog+1]],[0,10])
        next_line=prog+4+m.memory[prog+2]+256*m.memory[prog+3]
        self.assertEqual([m.memory[next_line],m.memory[next_line+1]],[0,20])


class RegionTests(unittest.TestCase):
    def test_actual_z80_guard_boundaries_and_wrap(self):
        from rom_machine import Machine
        pair,blob,manifest=build()
        for start,length,valid in ((0x3fff,1,False),(0x4000,0x6000,True),
                                   (0x9fff,1,True),(0x9fff,2,False),(0xa000,0,False),
                                   (0xbfff,1,False),(0xc000,0x4000,True),
                                   (0xc000,0x4001,False),(0xffff,1,True),(0xffff,2,False)):
            m=Machine([pair[:16384],pair[16384:]])
            m.memory.home[0x6000:0x6000+len(blob)]=blob
            for address,value in ((0xb704,start),(0xb706,length),(0x8000,0x9000)):
                m.memory[address]=value&255;m.memory[address+1]=value>>8
            m.cpu.registers[12]=0x8000  # SP
            m.cpu.registers[PC]=manifest['symbols']['valid_region']
            for _ in range(40):
                if m.cpu.registers[PC]==0x9000:break
                m.cpu.opcodes[m.memory[m.cpu.registers[PC]]]()
            else:self.fail('Region check failed to return')
            self.assertEqual(not bool(m.cpu.registers[1]&1),valid,(start,length))


if __name__=='__main__':unittest.main()
