"""Run the actual BASIC directory UI, including keyboard continuation/cancel."""
from pathlib import Path
import unittest
from fs128_basic_model import BasicMachine
from rom_machine import PC


class DirectoryPagingTests(unittest.TestCase):
    def boot_listing(self,count):
        m=BasicMachine();m.run_frames(240)
        m.press('shift','6');m.press('enter');m.run_frames(50)
        m.wire.directory_listing=''.join(s.ljust(32) for s in ('Path:/TAP/128','SD: test','File Name','-'*32))
        m.wire.directory_listing+=''.join(('FILE%03d.TAP'%i).ljust(32) for i in range(count))
        m.type_text('load "tpi:dir"\n');m.run_frames(30)
        return m
    def pages(self,m):return [c for c in m.wire.commands if c.startswith('TPI:DIRPAGE ')]
    def test_continue_last_page_and_stop_are_outside_service(self):
        m=self.boot_listing(32)
        self.assertEqual(self.pages(m),['TPI:DIRPAGE 0000'])
        self.assertFalse(m.service)
        self.assertEqual(m.memory[0xb800],ord('+'))
        self.assertIn((1,m.manifest['symbols']['directory_wait']),m.coverage)
        m.screenshot(Path('build/fs128-rom/directory-page-1.png'))
        m.press('enter');m.run_frames(30)
        self.assertEqual(self.pages(m),['TPI:DIRPAGE 0000','TPI:DIRPAGE 0001'])
        self.assertFalse(m.service)
        m.press('enter');m.run_frames(30)
        self.assertEqual(self.pages(m)[-1],'TPI:DIRPAGE 0002')
        self.assertEqual(m.memory[0xb800],ord('.'))
        self.assertFalse(m.service)
        m.screenshot(Path('build/fs128-rom/directory-last-page.png'))
        m.press('enter');m.run_frames(30)
        self.assertEqual(m.memory[0xb7f1],0)
        self.assertFalse(m.service)
    def test_n_and_space_cancel_without_fetching_next_page(self):
        for key in ('n',' '):
            m=self.boot_listing(100)
            self.assertFalse(m.service)
            m.press(key);m.run_frames(30)
            self.assertEqual(self.pages(m),['TPI:DIRPAGE 0000'])
            self.assertEqual(m.memory[0xb7f1],0)
            self.assertFalse(m.service)


if __name__=='__main__':unittest.main()
