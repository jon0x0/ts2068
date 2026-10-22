"""Check the staged CP/M Pages tree and public artifact contents."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json, zipfile

ROOT=Path(__file__).resolve().parents[1]
HUB=ROOT/'build/publish-hub';SITE=HUB/'CPM_2068'

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src') and value:self.links.append(value)

missing=[]
for page in SITE.rglob('*.html'):
    parser=Links();parser.feed(page.read_text(encoding='utf-8'))
    for url in parser.links:
        parts=urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:continue
        target=(HUB/parts.path.lstrip('/') if parts.path.startswith('/') else page.parent/unquote(parts.path)).resolve()
        if target.is_dir():target=target/'index.html'
        if not target.exists():missing.append((str(page.relative_to(SITE)),url))
if missing:
    print('Missing relative links:',*missing,sep='\n')
    raise SystemExit(1)
downloads=SITE/'downloads'
for line in (downloads/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1)
    assert hashlib.sha256((downloads/name).read_bytes()).hexdigest()==digest,name
with zipfile.ZipFile(downloads/'cpm22-tspico-dual.zip') as z:
    assert 'TAP/CPM/CPM.DCK' in z.namelist()
    assert len([n for n in z.namelist() if n.startswith('TAP/CPM/CPM3200')])==8
    assert not any(n.endswith('.rom') for n in z.namelist())
with zipfile.ZipFile(downloads/'cpm22-source.zip') as z:
    assert 'tools/public_font.py' in z.namelist()
    assert not any('.codex' in n or n.endswith(('.rom','.z3')) or n.startswith('build/') for n in z.namelist())
print('Static document links, public checksums, package layout and source exclusions PASS')
