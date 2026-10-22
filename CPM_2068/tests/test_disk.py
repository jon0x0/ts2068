import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from make_disk import make_disk
class Disk(unittest.TestCase):
    def test_2k_blocks_and_32k_physical_extents(self):
        blob=bytes(i%251 for i in range(70000))
        disk,files,free=make_disk([('LARGE.DAT',blob)],327680,128,2048)
        self.assertEqual([disk[i*32+12] for i in range(3)],[1,3,4])
        self.assertEqual([disk[i*32+15] for i in range(3)],[128,128,35])
        self.assertEqual(list(disk[16:32]),list(range(2,18)))
        restored=b''.join(disk[b*2048:(b+1)*2048] for b in files[0]['blocks'])
        self.assertEqual(restored[:len(blob)],blob)
        self.assertEqual(free,(160-2-35)*2048)
    def test_extent_boundary(self):
        blob=bytes(i%251 for i in range(17000))
        disk,files,free=make_disk([('LARGE.COM',blob)])
        self.assertEqual(disk[12],0);self.assertEqual(disk[15],128)
        self.assertEqual(disk[32+12],1);self.assertEqual(disk[32+15],5)
        restored=b''.join(disk[b*1024:(b+1)*1024] for b in files[0]['blocks'])
        self.assertEqual(restored[:len(blob)],blob)
        self.assertEqual(len(disk),49152)
    def test_full_disk_is_rejected(self):
        with self.assertRaises(ValueError):make_disk([('HUGE.COM',bytes(48*1024))])
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):make_disk([('A.COM',b'a'),('a.com',b'b')])
    def test_text_record_padding(self):
        disk,files,_=make_disk([('A.TXT',b'abc')])
        start=files[0]['blocks'][0]*1024
        self.assertEqual(disk[start:start+5],b'abc\x1a\x1a')
