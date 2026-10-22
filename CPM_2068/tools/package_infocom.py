"""Package the local two-game Oliger disk with its matched cartridge."""
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    names=['build/infocom-cpm.dck','build/infocom-cpm.dsk','build/infocom-cpm.manifest.json',
           'tools/run_infocom.ps1','tools/run_oliger.ps1','LICENSE',
           'third_party/cpm22/LICENSE.txt','third_party/CPM_UTILITIES_NOTICE.md']
    files={name:(ROOT/name).read_bytes() for name in names}
    files['README.md']=(ROOT/'docs/infocom-disk.md').read_bytes()
    files['disk-tools.md']=(ROOT/'docs/disk-tools.md').read_bytes()
    files['startup.md']=(ROOT/'docs/startup.md').read_bytes()
    for name in ('cpm_disk.py','make_disk.py','oliger_image.py','tspico_ram_image.py','prepare_infocom.py'):
        files['tools/'+name]=(ROOT/'tools'/name).read_bytes()
    for name in ('using-cpm.md','tspico-firmware.md','picovideo.md'):
        files[name]=(ROOT/'docs'/name).read_bytes()
    checksums=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items()))
    for document in (ROOT/'docs').glob('*.md'):
        files.setdefault(''+document.name,document.read_bytes())
    files['checksums.txt']=checksums.encode('ascii')
    output=ROOT/'build/infocom-cpm-oliger.zip'
    with zipfile.ZipFile(output,'w') as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data)
    print(output)

if __name__=='__main__':main()
