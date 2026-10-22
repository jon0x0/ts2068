"""Create an initial Fuse/JLO disk; never modify an existing image implicitly."""
import argparse
import json
from pathlib import Path
from make_disk import make_disk
from oliger_image import DISK_BYTES, encode_dsk

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory', type=Path, help='directory of CP/M 8.3 files; otherwise use the build manifest')
    p.add_argument('--blank', action='store_true', help='create an empty, initialized CP/M disk instead of copying build files')
    p.add_argument('--add', type=Path, action='append', default=[], help='additional file; may be repeated')
    p.add_argument('--output', type=Path, default=ROOT/'build/oliger-cpm.dsk')
    p.add_argument('--force', action='store_true', help='allow replacing the output image')
    p.add_argument('--size',type=int,choices=[160,320],default=160,help='KB; must match the cartridge geometry')
    a = p.parse_args()
    if a.output.exists() and not a.force:
        p.error('output already exists; choose another path or use --force to replace it')
    if a.blank and a.directory:
        p.error('--blank and --directory are mutually exclusive')
    if a.blank:
        files = []
    elif a.directory:
        files = [(f.name, f.read_bytes()) for f in sorted(a.directory.iterdir()) if f.is_file()]
    else:
        manifest = json.loads((ROOT/'build/manifest.json').read_text())
        files = [(f['name'], (ROOT/'build/sdcard/CPM/FILES'/f['name']).read_bytes()) for f in manifest['files']]
    files += [(f.name, f.read_bytes()) for f in a.add]
    sides=a.size//160
    block_size=1024 if sides==1 else 2048
    raw, manifest, free = make_disk(files, DISK_BYTES*sides, 128,block_size)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(encode_dsk(raw,sides))
    a.output.with_suffix('.manifest.json').write_text(json.dumps({'geometry':f'40x{sides}x16x256','block_size':block_size,'directory_entries':128,'free_bytes':free,'files':manifest}, indent=2)+'\n')
    print(f'{a.output}: {len(files)} files, {free//1024}KB free')

if __name__ == '__main__':
    main()
