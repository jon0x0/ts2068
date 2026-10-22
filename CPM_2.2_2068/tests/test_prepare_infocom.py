import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from prepare_infocom import prepare


class InfocomPreparation(unittest.TestCase):
    def test_reject_wrong_story_and_interpreter(self):
        for story in (b'',bytes([5])+bytes(63),bytes([3])+bytes(131072)):
            with self.assertRaises(ValueError):prepare(story,bytes(8443),'ZORK2')
        with self.assertRaises(ValueError):prepare(bytes([3])+bytes(63),bytes(8443),'ZORK2')

    def test_patch_changes_only_story_basename(self):
        path=ROOT/'build/planetfall/PLANET.COM'
        if not path.exists():self.skipTest('build project interpreter first')
        original=path.read_bytes();story=bytes([3])+bytes(63)
        result,data=prepare(story,original,'ZORK2')
        self.assertEqual(result[:5],original[:5]);self.assertEqual(result[5:13],b'ZORK2   ')
        self.assertEqual(result[13:],original[13:]);self.assertEqual(data,story)
        self.assertEqual(prepare(story,original.ljust(8448,b'\0'),'ZORK2')[0],result)
        with self.assertRaises(ValueError):prepare(story,original,'TOO_LONG_NAME')


if __name__=='__main__':unittest.main()
