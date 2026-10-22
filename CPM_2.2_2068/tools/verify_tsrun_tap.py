"""Check browser TAP exports against the Python host and TSPico firmware readers."""
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
from firmware.cpm_tap import TapVolume
from tspico_ram_image import decode_image,decode_saved_chunks


def main():
    for kb in (160,320):
        for kind in ('dsk','tap'):
            base=ROOT/'build/tsrun-tap-tests'/f'{kb}-{kind}'
            expected=base.with_suffix('.img').read_bytes()
            tap=base.with_suffix('.tap')
            assert decode_image(tap.read_bytes())==expected
            volume=TapVolume(str(tap))
            assert b''.join(volume.read(i) for i in range(volume.sectors))==expected
            with tempfile.TemporaryDirectory() as temporary,zipfile.ZipFile(base.with_suffix('.zip')) as archive:
                assert archive.testzip() is None
                folder=Path(temporary)
                for name in archive.namelist():
                    assert name in ['CPMSTATE.TAP']+[f'CPM{i:02}.TAP' for i in range(kb//8)]
                    (folder/name).write_bytes(archive.read(name))
                assert decode_saved_chunks(folder)==expected
            print(f'{kb}KB from {kind}: host TAP, firmware TapVolume, legacy ZIP/descriptor checksums PASS')


if __name__=='__main__':main()
