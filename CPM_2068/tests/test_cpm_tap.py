import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'firmware'),str(ROOT/'tools')]
from cpm_tap import TapVolume,save_tap
from cpm_directory import DirectoryVolume
from tspico_ram_image import encode_image,SIZE

class Tap(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.image=bytes(range(256))*(SIZE//256)
        self.path=self.root/'TEST.TAP';self.path.write_bytes(encode_image(self.image))
    def tearDown(self):self.tmp.cleanup()
    def test_mount_reads_writes_and_crc(self):
        v=TapVolume(str(self.path))
        for lba in (0,63,64,511,512,2559):self.assertEqual(v.read(lba),self.image[lba*128:(lba+1)*128])
        for lba in (0,63,64,2559):v.write(lba,b'\x17'*128)
        reloaded=TapVolume(str(self.path))
        for lba in (0,63,64,2559):self.assertEqual(reloaded.read(lba),b'\x17'*128)
        self.assertEqual(reloaded.read(62),self.image[62*128:63*128])
        with self.assertRaises(OSError):v.read(2560)
        with self.assertRaises(OSError):v.write(0,b'short')
    def test_export_snapshot_and_refuse_overwrite(self):
        v=TapVolume(str(self.path));v.write(2559,b'\xff'*128)
        destination=self.root/'SAVED.TAP';save_tap(v,str(destination))
        self.assertEqual(TapVolume(str(destination)).read(2559),b'\xff'*128)
        before=destination.read_bytes()
        with self.assertRaises(OSError):save_tap(v,str(destination))
        self.assertEqual(destination.read_bytes(),before)
    def test_native_directory_snapshot(self):
        folder=self.root/'FILES';folder.mkdir();data=bytes(range(256))*700
        (folder/'LARGE.BIN').write_bytes(data)
        v=DirectoryVolume(str(folder),327680,2048)
        snapshot=self.root/'NATIVE.TAP';save_tap(v,str(snapshot));tap=TapVolume(str(snapshot))
        for lba in (0,32,1024,2048,2559):self.assertEqual(tap.read(lba),v.read(lba))
    def test_corrupt_and_truncated_refused(self):
        original=self.path.read_bytes()
        for invalid in (original[:-1],original[:-1]+bytes((original[-1]^1,)),original+b'\0'):
            self.path.write_bytes(invalid)
            with self.assertRaises(OSError):TapVolume(str(self.path))

if __name__=='__main__':unittest.main()
