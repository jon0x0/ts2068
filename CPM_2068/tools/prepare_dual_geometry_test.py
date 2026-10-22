"""Create small CP/M disks for native Z80 mount integration tests."""
import sys
from pathlib import Path
from make_disk import make_disk
from oliger_image import encode_dsk
from tspico_ram_image import encode_image,encode_volumes
root=Path(sys.argv[1]);profile=Path('build/profiles/tspico-dir')
names=['HELLO.COM','CPMDISK.COM','PIP.COM','STAT.COM','COLOR.COM','FORMAT.COM']
files=[(name,(profile/'files'/name).read_bytes()) for name in names]
for kb in (160,320):
    raw,_,_=make_disk(files,kb*1024,128,1024 if kb==160 else 2048)
    (root/f'DISK{kb}.DSK').write_bytes(encode_dsk(raw,kb//160))
    (root/f'DISK{kb}.TAP').write_bytes(encode_image(raw))
    if kb==160:
        saver=Path('build/profiles/tspico-ram/tpsave.bin')
        stock_files=[(n,(Path('build/profiles/tspico-ram/files/FORMAT.COM').read_bytes() if n=='FORMAT.COM' else d)) for n,d in files]+([('TPSAVE.COM',saver.read_bytes())] if saver.exists() else [])
        raw,_,_=make_disk(stock_files,163840,128,1024)
        target=root/'stock160';target.mkdir(exist_ok=True)
        for name,data in encode_volumes(raw).items():(target/name).write_bytes(data)
        (target/'CPM320.TAP').write_bytes(encode_image(raw))
        (target/'drive-a.img').write_bytes(raw)
