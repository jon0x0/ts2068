import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import cpm_disk
from make_disk import make_disk


class DiskUtility(unittest.TestCase):
    def test_format_directory_sectors_on_native_files_backend(self):
        sys.path.insert(0,str(ROOT/'firmware'))
        from cpm_directory import DirectoryVolume
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            (folder/'BIG.COM').write_bytes(bytes(range(256))*180)
            (folder/'SMALL.TXT').write_bytes(b'test')
            volume=DirectoryVolume(str(folder),327680,2048)
            for lba in range(32):
                volume.write(lba,b'\xe5'*128)
                self.assertEqual(volume.read(lba),b'\xe5'*128)
            self.assertFalse((folder/'BIG.COM').exists())
            self.assertFalse((folder/'SMALL.TXT').exists())

    def test_create_copy_preserve_and_replace_all_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            first=folder/'BIG.COM';first.write_bytes(bytes(range(256))*180)
            second=folder/'NOTE.TXT';second.write_bytes(b'Hello\r\n')
            for kb in (160,320):
                for suffix in ('.dsk','.tap','.img'):
                    disk=folder/(str(kb)+suffix)
                    with patch.object(sys,'argv',['tool','create',str(disk),'--size',str(kb)]):cpm_disk.main()
                    raw=cpm_disk.decode(disk)
                    self.assertEqual(raw[:4096],b'\xe5'*4096)
                    self.assertEqual(len(raw),kb*1024)
                    with patch.object(sys,'argv',['tool','put',str(disk),str(first)]):cpm_disk.main()
                    files,_=cpm_disk.read_files(cpm_disk.decode(disk))
                    self.assertEqual(files['BIG.COM'],first.read_bytes())
                    # Preserve CP/M attributes and all records of a multi-extent file.
                    raw=bytearray(cpm_disk.decode(disk));raw[9]|=128
                    disk.write_bytes(cpm_disk.encode(disk,raw))
                    with patch.object(sys,'argv',['tool','put',str(disk),str(second)]):cpm_disk.main()
                    files,attrs=cpm_disk.read_files(cpm_disk.decode(disk))
                    self.assertEqual(files['BIG.COM'],first.read_bytes())
                    self.assertTrue(attrs['BIG.COM'][8]&128)
                    self.assertEqual(files['NOTE.TXT'],b'Hello\r\n'+b'\x1a'*121)
                    original=disk.read_bytes()
                    with patch.object(sys,'argv',['tool','put',str(disk),str(second)]),self.assertRaises(SystemExit):cpm_disk.main()
                    self.assertEqual(disk.read_bytes(),original)
                    second.write_bytes(b'Changed')
                    with patch.object(sys,'argv',['tool','put',str(disk),str(second),'--replace']):cpm_disk.main()
                    self.assertTrue(cpm_disk.read_files(cpm_disk.decode(disk))[0]['NOTE.TXT'].startswith(b'Changed'))
                    second.write_bytes(b'Hello\r\n')

    def test_disk_full_and_unknown_user_leave_image_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);disk=folder/'small.dsk';source=folder/'HUGE.COM'
            raw,_,_=make_disk([],163840,128,1024)
            disk.write_bytes(cpm_disk.encode(disk,raw));original=disk.read_bytes()
            source.write_bytes(bytes(163840))
            with patch.object(sys,'argv',['tool','put',str(disk),str(source)]),self.assertRaises(SystemExit):cpm_disk.main()
            self.assertEqual(disk.read_bytes(),original)
            raw=bytearray(raw);raw[0]=1
            with self.assertRaises(ValueError):cpm_disk.read_files(raw)
            with self.assertRaises(ValueError):cpm_disk.publish(disk,b'bad')
            self.assertEqual(disk.read_bytes(),original)


if __name__=='__main__':unittest.main()
