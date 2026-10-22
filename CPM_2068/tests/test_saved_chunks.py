import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'firmware')]
from tspico_ram_image import tap_code,decode_saved_chunks,page_checksum

class SavedChunks(unittest.TestCase):
    def prepare(self,root,kb=160):
        raw=bytes(range(256))*(kb*4)
        descriptor=bytearray(128);descriptor[:8]=b'CPMSAV1\0';descriptor[8:11]=bytes((1,kb//32,kb//8))
        for i in range(kb//8):
            page=raw[i*8192:(i+1)*8192]
            (root/f'CPM{i:02}.TAP').write_bytes(tap_code(f'CPM{i:02}',page))
            descriptor[12+i*2:14+i*2]=page_checksum(page).to_bytes(2,'little')
        (root/'CPMSTATE.TAP').write_bytes(tap_code('CPMSTATE',descriptor))
        return raw,descriptor
    def test_geometry_auto_and_refuse_mismatched_geometry(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);raw,_=self.prepare(root)
            self.assertEqual(decode_saved_chunks(root),raw)
            with self.assertRaises(ValueError):decode_saved_chunks(root,320)
    def test_incomplete_missing_and_mixed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);raw,descriptor=self.prepare(root)
            descriptor[8]=0;(root/'CPMSTATE.TAP').write_bytes(tap_code('CPMSTATE',descriptor))
            with self.assertRaises(ValueError):decode_saved_chunks(root)
            descriptor[8]=1;(root/'CPMSTATE.TAP').write_bytes(tap_code('CPMSTATE',descriptor))
            page=root/'CPM19.TAP';page.unlink()
            with self.assertRaises(ValueError):decode_saved_chunks(root)
            page.write_bytes(tap_code('CPM19',b'X'*8192))
            with self.assertRaises(ValueError):decode_saved_chunks(root)

if __name__=='__main__':unittest.main()
