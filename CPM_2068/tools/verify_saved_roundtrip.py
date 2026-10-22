"""Validate native-Z80 TPSAVE exports with the host and firmware disk readers."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from firmware.cpm_tap import TapVolume
from tspico_ram_image import decode_image, decode_saved_chunks
from oliger_image import encode_dsk, decode_dsk


def main():
    for kb in (160, 320):
        for mode in ('legacy', 'modern', 'modern-split', 'modern-service'):
            folder = ROOT / 'build' / f'saved-roundtrip-{kb}-{mode}'
            expected = (folder / 'expected.img').read_bytes()
            single = folder / 'CPMRAM.TAP'
            if single.exists():
                actual = decode_image(single.read_bytes())
                volume = TapVolume(str(single))
                assert b''.join(volume.read(i) for i in range(volume.sectors)) == expected
            else:
                actual = decode_saved_chunks(folder)
            assert actual == expected, folder
            assert decode_dsk(encode_dsk(actual, kb // 160)) == expected
            print(f'{kb}KB {mode}: host, firmware TAP reader where applicable, Fuse DSK conversion PASS')


if __name__ == '__main__':
    main()
