"""Stage the explicit public project files, pinned TSRun and reproducible ZIP.

Usage: python scripts/publish_site.py --hub publish --tsrun tsrun-current
Does not commit or push. Never traverses arbitrary workspace/private files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--hub',type=Path,required=True)
parser.add_argument('--tsrun',type=Path,required=True)
args=parser.parse_args()
dest=args.hub.resolve()/'ZXDesk2068'
runtime=args.tsrun.resolve()
dest.mkdir(parents=True,exist_ok=True)
source=[]
for folder in ('src','scripts','docs','web'):
    source.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
source.extend(root/n for n in ('README.md','LICENSE','ZXDesk_TS2068_TSPico_Port_Handoff.md','.gitignore'))
for p in source:
    target=dest/p.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
for p in (root/'web').iterdir():
    if p.is_file():shutil.copyfile(p,dest/p.name)
(dest/'images').mkdir(exist_ok=True)
for name in ('desktop.png','desktop-512-windows.png'):
    shutil.copyfile(root/'build'/name,dest/'images'/name)
downloads=dest/'downloads';downloads.mkdir(exist_ok=True)
for name in ('zxdesk2068.tap','zxdesk2068-512.tap'):
    shutil.copyfile(root/'build'/name,downloads/name)
snapshot=subprocess.check_output(['git','-C',str(runtime),'rev-parse','HEAD'],text=True).strip()
runtime_files=subprocess.check_output(['git','-C',str(runtime),'ls-files'],text=True).splitlines()
hashes={}
for name in runtime_files:
    p=runtime/name
    target=dest/'tsrun'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest()
(dest/'tsrun-version.json').write_text(json.dumps({'repository':'https://github.com/josef-jelinek/TSRun','commit':snapshot,'checked_on':'2026-10-29','modifications':'None; player wrapper and pointer controls are separate.','sha256':hashes},indent=2)+'\n',encoding='utf-8')
archive=downloads/'ZXDesk2068-source.zip'
artifacts=[root/'build'/n for n in ('zxdesk2068.tap','zxdesk2068.bin','zxdesk2068.sym','zxdesk2068-512.tap','zxdesk2068-512.bin','zxdesk2068-512.sym')]
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(source+artifacts):
        info=zipfile.ZipInfo('ZXDesk2068/'+p.relative_to(root).as_posix(),date_time=(2026,10,29,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        z.writestr(info,p.read_bytes())
(downloads/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(downloads.iterdir()) if p.suffix in ('.tap','.zip')),encoding='ascii')
print(f'Staged {len(source)} project source files and TSRun {snapshot} at {dest}')
