import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from oliger_image import DISK_BYTES, encode_dsk, decode_dsk

class OligerImage(unittest.TestCase):
    def test_all_logical_records(self):
        raw=b''.join(bytes([lba & 255,lba >> 8])*64 for lba in range(DISK_BYTES//128))
        encoded=encode_dsk(raw)
        self.assertEqual(decode_dsk(encoded),raw)
        for cyl in (0,1,39):
            pos=256+cyl*4352
            self.assertEqual(encoded[pos+256:pos+512],raw[cyl*4096:cyl*4096+256])
    def test_truncated_and_bad_sector(self):
        encoded=bytearray(encode_dsk(bytes(DISK_BYTES)))
        with self.assertRaises(ValueError): decode_dsk(encoded[:-1])
        encoded[256+26]=0
        with self.assertRaises(ValueError): decode_dsk(encoded)
    def test_wrong_capacity(self):
        with self.assertRaises(ValueError): encode_dsk(bytes(49152))
    def test_both_sides(self):
        raw=b''.join(bytes([i%256])*256 for i in range(1280))
        encoded=encode_dsk(raw,2)
        self.assertEqual(encoded[49],2)
        self.assertEqual(encoded[256+4352+17],1)
        self.assertEqual(encoded[256+8704+16],1)
        self.assertEqual(decode_dsk(encoded),raw)
