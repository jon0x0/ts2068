"""Bundle the project-local TSRun launcher, without emulator ROMs or runtime."""
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    paths=['tools/run_tsrun.py','tools/cpm_disk.py','tools/prepare_infocom.py','tools/make_disk.py',
           'tools/oliger_image.py','tools/tspico_ram_image.py',
           'build/infocom-cpm.dck','build/infocom-cpm.dsk','build/infocom-cpm.manifest.json',
           'LICENSE','third_party/cpm22/LICENSE.txt','third_party/CPM_UTILITIES_NOTICE.md']
    paths += [str(path.relative_to(ROOT)).replace('\\','/') for path in (ROOT/'web/tsrun').glob('*') if path.is_file()]
    files={name:(ROOT/name).read_bytes() for name in paths}
    for name in ('startup.md','using-cpm.md','tspico-firmware.md','oliger.md','tspico-dual.md','tspico-ram.md','tspico-directory.md','disk-tools.md','picovideo.md'):
        files['docs/'+name]=(ROOT/'docs'/name).read_bytes()
    files['README.md']=b'# CP/M on TSRun\n\nRun `python tools/run_tsrun.py --tsrun PATH_TO_YOUR_TSRUN` and open http://127.0.0.1:8770/.\nThe TSRun checkout must include roms/ts2068-0.rom and ts2068-1.rom.\nThe emulator runtime and ROMs are not included.\n\nSee [startup instructions](docs/startup.md#tsrun-browser-emulator-with-the-same-oliger-disks).\nOpen DSK, CP/M TAP, or multi-file TAP sets. Download DSK/TAP before closing/reloading; use Download 1.00 TAP set for original firmware.\n'
    for document in (ROOT/'docs').glob('*.md'):
        files.setdefault('docs/'+document.name,document.read_bytes())
    files['checksums.txt']=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items())).encode()
    output=ROOT/'build/ts2068-cpm-tsrun.zip'
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,data)
    print(output)


if __name__=='__main__':main()
