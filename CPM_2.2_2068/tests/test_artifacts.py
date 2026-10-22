import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from dck import parse
from convert8080 import convert
class Artifacts(unittest.TestCase):
    def test_cartridge(self):
        data=(ROOT/'build/ts2068-cpm.dck').read_bytes(); blocks=parse(data)
        profile=json.loads((ROOT/'build/manifest.json').read_text())['profile']
        self.assertEqual(blocks[0][1],[3,3,3,3,2,2,2,2 if profile=='tspico-ram' else 0])
        if profile=='oliger':
            self.assertEqual(len(blocks),1)
            from oliger_image import decode_dsk
            self.assertEqual(decode_dsk((ROOT/'build/oliger-cpm.dsk').read_bytes()),(ROOT/'build/drive-a.img').read_bytes())
        elif profile.startswith('tspico-'):
            self.assertEqual(len(blocks),1)
            self.assertEqual((ROOT/'build/drive-a.img').stat().st_size,327680)
        else:
            self.assertEqual(len(data),106514)
            self.assertEqual(blocks[1][1],[0,3,3,3,3,3,3,0])
            self.assertEqual(b''.join(blocks[1][2]),(ROOT/'build/drive-a.img').read_bytes())
        for cut in (1,8,9,100,len(data)-1):
            with self.assertRaises(ValueError):parse(data[:cut])
    def test_empty_ram_has_no_payload(self):
        self.assertEqual(parse(bytes([0,1,1,0,0,0,0,0,0]))[0][2],[b'']*8)
    def test_hashes(self):
        for line in (ROOT/'build/checksums.txt').read_text().splitlines():
            digest,name=line.split();self.assertEqual(hashlib.sha256((ROOT/'build'/name).read_bytes()).hexdigest(),digest)
    def test_immediate_8080_expression(self):
        self.assertIn('ld hl,nxtrec-reccnt',convert('\tlxi h,(nxtrec-reccnt)',0))
    def test_sections(self):
        self.assertLessEqual((ROOT/'build/ccp.bin').stat().st_size,0x800)
        self.assertLessEqual((ROOT/'build/bdos.bin').stat().st_size,0xe00)
        self.assertLessEqual((ROOT/'build/bios.bin').stat().st_size,0x1200)
        self.assertEqual((ROOT/'build/ts2068-cpm-system.bin').stat().st_size,0x3000)
if __name__=='__main__':unittest.main()
