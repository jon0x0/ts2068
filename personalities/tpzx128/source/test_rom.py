"""Functional prototype checks; none certify electrical timing or real hardware."""
import unittest
from pathlib import Path
from build_rom import patch_roms,HASHES
from pio_model import Bus,assemble
from rom_machine import Memory,Machine


class PIOTests(unittest.TestCase):
    def test_input_probe_first_four_writes(self):
        bus=Bus(4,rom_memory='sram')
        for value in (7,6,5,4,3):
            bus.write(value);bus.memory_cycle(0x1234)
        self.assertEqual([word&255 for word in bus.observer.rx],[7,6,5,4])
        self.assertEqual(bus.observer.dropped,1)
        p=assemble()
        self.assertLessEqual(sum(len(p[n][0]) for n in ('memory_enable','memory_address','paging_observer')),32)
    def test_trace_byte_preserves_original_capture(self):
        for value in (0,7,0x10,0x33,0x7b,0xf3,0xff):
            bus=Bus(4,rom_memory='sram');bus.write(value)
            bus.memory_cycle(0x1234)
            self.assertEqual(bus.address.x,(value<<8)|((value&7)<<5)|4)
            self.assertEqual((bus.state>>22)&1,(value>>4)&1)
    def test_program_budget(self):
        p=assemble()
        self.assertLessEqual(len(p['paging_write'][0]),32)
        self.assertLessEqual(len(p['memory_enable'][0])+len(p['memory_address'][0]),32)
    def test_all_banks_rom_halves_and_flash_slots(self):
        for slot in (0,3,15):
            bus=Bus(slot)
            for rom in (0,1):
                for bank in range(8):
                    bus.write(bank|(rom<<4))
                    ram=bus.memory_cycle(0xc000,True)
                    self.assertEqual(ram,dict(address_gpio_nibble=bank*2,rom_half=rom,control=5))
                    flash=bus.memory_cycle(0x1234)
                    self.assertEqual(flash,dict(address_gpio_nibble=slot,rom_half=rom,control=2))
    def test_sram_rom_all_banks_and_halves(self):
        p=assemble()
        self.assertLessEqual(len(p['memory_enable_sram'][0])+len(p['memory_address'][0]),32)
        for slot in range(0,16,2):
            bus=Bus(slot,rom_memory="sram")
            for rom in (0,1):
                for bank in range(8):
                    bus.write(bank|(rom<<4))
                    self.assertEqual(bus.memory_cycle(0x1234),dict(address_gpio_nibble=slot,rom_half=rom,control=1))
                    self.assertEqual(bus.memory_cycle(0xc000,True)['control'],5)
                    self.assertEqual(bus.memory_cycle(0,write=True)['control'],7)
                    # ROM pair occupies the lower 32K of this 64K block;
                    # the boot test writes only each block's uppermost 16K.
                    self.assertLess(slot*32768+32767,(slot//2)*65536+49152)

    def test_no_external_response_to_home_ram_or_rom_writes(self):
        bus=Bus()
        for addr in (0x4000,0x8000,0xbfff):
            self.assertEqual(bus.memory_cycle(addr)['control'],7)
        self.assertEqual(bus.memory_cycle(0x0000,write=True)['control'],7)
    def test_lock_and_decoder(self):
        bus=Bus();bus.write(0x35)
        before=bus.memory_cycle(0xc000,True)
        for value,port in ((0,15),(3,0xfd),(0,14)):
            bus.write(value,port)
            self.assertEqual(bus.memory_cycle(0xc000,True),before)
        bus=Bus();bus.write(2)
        before=bus.memory_cycle(0xc000,True)
        for port in (14,0xfd):
            bus.write(7,port)
            self.assertEqual(bus.memory_cycle(0xc000,True),before)
    def test_address_settles_before_sram_enable(self):
        bus=Bus();bus.write(7)
        bus.host.update({13:0,26:0,1:1})
        for _ in range(40):
            bus.tick(1)
            if (bus.state>>19)&7==5:
                self.assertEqual((bus.state>>15)&15,14)


class ROMTests(unittest.TestCase):
    def test_guards_and_reproducibility(self):
        originals=[Path(f'build/rom/original-{i}.rom').read_bytes() for i in range(2)]
        patched,manifest=patch_roms(originals)
        self.assertEqual(manifest['input_sha256'],list(HASHES))
        self.assertEqual(patched,[Path(f'build/rom/tspico128-{i}.rom').read_bytes() for i in range(2)])
        originals[0]=bytes(16384)
        with self.assertRaises(ValueError):patch_roms(originals)
    def test_memory_does_not_grant_unavailable_aliases(self):
        m=Memory([bytes(16384),bytes(16384)]);m.f4=0xc0
        for bank,addr in ((2,0x8000),(5,0x4000)):
            m.page(bank);m[addr]=0x42;m[0xc000]=0x23
            self.assertEqual(m[addr],0x42);self.assertEqual(m[0xc000],0x23)
    def test_patched_ram_templates(self):
        m=Machine();m.run_frames(240)
        self.assertEqual([m.memory[a] for a in range(0x5b02,0x5b05)],[1,15,127])
        # Template copied by editor startup, including its non-A OUT(C),D.
        m.press('shift','6');m.press('enter');m.run_frames(30)
        self.assertEqual(m.memory.banks[7][0x3caf:0x3cb2],[1,15,127])
    def test_keyboard_basic_play_and_ramdisk(self):
        from smoke_rom import smoke
        report=smoke()
        self.assertEqual(len(report['checks']),6)


if __name__=='__main__':unittest.main()
