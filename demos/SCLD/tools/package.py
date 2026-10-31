"""Regenerate gallery downloads and checksums after editing source or assets."""
from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parents[1]
def archive(name,files):
 with zipfile.ZipFile(R/'downloads'/name,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(files):z.write(p,p.relative_to(R))
catalog=json.loads((R/'catalog.json').read_text())
files=[R/v['cartridge'] for d in catalog['families'] for v in d['variants']]
archive('SCLD-cartridges.zip',files+[R/'README.md',R/'catalog.json'])
source=[p for folder in ['source','tools','player','validation','cartridges','taps','previews'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'captures' not in p.parts]
source += [R/n for n in ['README.md','catalog.json','gallery.js','gallery.css','index.html','package.json','.gitignore']]
archive('SCLD-sources.zip',source)
checks=[]
for folder in ['cartridges','taps','downloads']:
 for p in sorted((R/folder).glob('*')):
  if p.is_file():checks.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(R)))
(R/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n')
print('Packaged',len(files),'curated cartridges and source, with checksums.')
