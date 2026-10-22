"""Bundle the matched Planetfall cartridge and floppy for a local GUI test."""
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    files={
        'README.md':ROOT/'docs/planetfall.md',
        'LICENSE':ROOT/'LICENSE',
        'third_party/cpm22/LICENSE.txt':ROOT/'third_party/cpm22/LICENSE.txt',
        'third_party/CPM_UTILITIES_NOTICE.md':ROOT/'third_party/CPM_UTILITIES_NOTICE.md',
    }
    for name in ['planetfall-cpm.dck','planetfall-cpm.dsk','planetfall-cpm.manifest.json']:
        files['build/'+name]=ROOT/'build'/name
    for name in ['run_planetfall.ps1','run_oliger.ps1']:
        files['tools/'+name]=ROOT/'tools'/name
    checksums=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+n+'\n' for n,p in sorted(files.items()))
    output=ROOT/'build/planetfall-cpm-oliger.zip'
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,p in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes())
        z.writestr('checksums.txt',checksums)
    print(output)

if __name__=='__main__':main()
