import sys,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'firmware'),str(ROOT/'tools')]
from cpm_dsk import DskVolume,save_dsk
from cpm_tap import TapVolume,save_tap
from oliger_image import encode_dsk,decode_dsk
from tspico_ram_image import encode_image,decode_image,encode_volumes,decode_volumes
import tspico_ram_image
import test_cpm_service

class DualGeometry(unittest.TestCase):
    def test_host_single_sided_chunk_export_ignores_stale_upper_chunks(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);raw=bytes(range(256))*640
            for i in range(40):
                data=raw[i*8192:(i+1)*8192] if i<20 else bytes(8192)
                (root/f'CPM{i:02}.TAP').write_bytes(tspico_ram_image.tap_code(f'CPM{i:02}',data))
            tap=root/'SAVED.TAP';dsk=root/'SAVED.DSK'
            with patch.object(sys,'argv',['tool','--chunks',folder,'--chunk-kb','160','--output',str(tap),'--dsk-output',str(dsk)]):
                tspico_ram_image.main()
            self.assertEqual(decode_image(tap.read_bytes()),raw)
            self.assertEqual(decode_dsk(dsk.read_bytes()),raw)
    def test_containers_and_boot_volumes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for sides in (1,2):
                raw=bytes(range(256))*(640*sides)
                dsk=root/'DISK.DSK';dsk.write_bytes(encode_dsk(raw,sides))
                disk=DskVolume(str(dsk));self.assertEqual(disk.sectors,1280*sides)
                for lba in (0,1,31,32,disk.sectors-1):self.assertEqual(disk.read(lba),raw[lba*128:lba*128+128])
                disk.write(disk.sectors-1,b'\x17'*128)
                updated=raw[:-128]+b'\x17'*128
                self.assertEqual(decode_dsk(dsk.read_bytes()),updated)
                tap=root/'DISK.TAP';save_tap(disk,str(tap))
                self.assertEqual(decode_image(tap.read_bytes()),updated)
                mounted=TapVolume(str(tap));self.assertEqual(mounted.sectors,disk.sectors)
                mounted.write(31,b'X'*128)
                back=root/'BACK.DSK';save_dsk(mounted,str(back))
                self.assertEqual(decode_dsk(back.read_bytes())[31*128:32*128],b'X'*128)
                before=back.read_bytes()
                with self.assertRaises(OSError):save_dsk(mounted,str(back))
                self.assertEqual(back.read_bytes(),before)
                with self.assertRaises(OSError):mounted.read(mounted.sectors)
                with self.assertRaises(OSError):disk.write(disk.sectors,bytes(128))
                volumes=root/str(sides);volumes.mkdir()
                for name,data in encode_volumes(updated).items():(volumes/name).write_bytes(data)
                self.assertEqual(decode_volumes(volumes),updated)
                tap.unlink();back.unlink()
    def test_dsk_invalid_layout_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'BAD.DSK';valid=encode_dsk(bytes(163840))
            for data in (valid[:-1],valid+b'X',valid[:280]+bytes(8)+valid[288:]):
                p.write_bytes(data)
                with self.assertRaises(OSError):DskVolume(str(p))

class Switching(test_cpm_service.Service):
    def test_mount_saved_single_tap_and_export_dsk_on_sd(self):
        root=Path(self.tmp.name);folder=root/'CPM/SAVE';folder.mkdir(parents=True)
        raw=bytes(range(256))*640;(folder/'CPMRAM.TAP').write_bytes(encode_image(raw))
        self.s.catalog.resolve=lambda cur,name:str(root/name.lstrip('/'))
        self.assertEqual(self.invoke('MOUNT',cmd='cmd SAVE/CPMRAM.TAP'),b'\x01')
        self.assertEqual(self.invoke('READ',1279)[2:-1],raw[-128:])
        self.assertEqual(self.invoke('SAVE',cmd='cmd SAVE/CPMRAM.DSK'),b'\x01')
        self.assertEqual(decode_dsk((folder/'CPMRAM.DSK').read_bytes()),raw)
        self.assertEqual(self.invoke('MOUNT',cmd='cmd SAVE/../EVIL.TAP'),b'\x03')
    def test_configured_dsk_and_tap_cold_mount(self):
        for storage,encode in [('dsk',lambda raw:encode_dsk(raw,1)),('tap',encode_image)]:
            raw=bytes(163840);self.path.write_bytes(encode(raw));self.s.STORAGE=storage
            self.assertEqual(self.invoke('CAP')[2:-1],b'CPM1\x01\x80\x00\x05')
            self.assertEqual(self.invoke('READ',1279)[2:-1],bytes(128))
            self.assertEqual(self.invoke('READ',1280),b'\x06')
    def test_mount_both_sizes_and_formats_and_preserve_failed_mount(self):
        root=Path(self.tmp.name);self.s.catalog.resolve=lambda cur,name:str(root/Path(name).name)
        self.invoke('CAP')
        for size in (163840,327680,163840):
            raw=bytes(range(256))*(size//256)
            for extension,encode in [('DSK',lambda raw:encode_dsk(raw,size//163840)),('TAP',encode_image)]:
                (root/('DISK.'+extension)).write_bytes(encode(raw))
                self.assertEqual(self.invoke('MOUNT',cmd='cmd DISK.'+extension),b'\x01')
                self.assertEqual(self.invoke('INFO')[2:-1],b'CPM1\x01\x80'+bytes((0,size//32768)))
                last=size//128-1
                self.assertEqual(self.invoke('READ',last)[2:-1],raw[-128:])
                self.assertEqual(self.invoke('READ',last+1),b'\x06')
                self.assertEqual(self.invoke('WRITE0',last,'cmd '+'58'*64),b'\x01')
                self.assertEqual(self.invoke('WRITE1',last,'cmd '+'58'*64),b'\x01')
                self.assertEqual(self.invoke('READ',last)[2:-1],b'X'*128)
                self.assertEqual(self.invoke('MOUNT',cmd='cmd MISSING.DSK'),b'\x03')
                self.assertEqual(self.invoke('READ',last)[2:-1],b'X'*128)

if __name__=='__main__':unittest.main()
