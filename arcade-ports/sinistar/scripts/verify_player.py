"""Check the static player's cartridge and exact pinned upstream files."""
from pathlib import Path
import hashlib
import json
import argparse
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dpad', action='store_true', help='Verify the Berzerk-derived comparison player')
PLAYER = ROOT / ('play-dpad' if parser.parse_args().dpad else 'play')
version = json.loads((PLAYER / 'tsrun-version.json').read_text())
assert version.get('modifications', []) == []
actual = {p.relative_to(PLAYER / 'tsrun').as_posix()
          for p in (PLAYER / 'tsrun').rglob('*') if p.is_file()}
assert actual == set(version['files']), 'Missing or unexpected upstream files'
for name, expected in version['files'].items():
    assert hashlib.sha256((PLAYER / 'tsrun' / name).read_bytes()).hexdigest() == expected, name
cartridge = (PLAYER / 'assets/sinistar.dck').read_bytes()
assert cartridge == (ROOT / 'port/build/sinistar-mining.dck').read_bytes(), 'Player cartridge is stale'
assert len(cartridge) == 65545

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name not in ('href', 'src') or not value:
                continue
            link = urlsplit(value)
            if link.scheme or link.netloc or not link.path:
                continue
            assert not link.path.startswith('/'), 'Root-relative player link'
            assert (PLAYER / unquote(link.path)).exists(), value

Links().feed((PLAYER / 'index.html').read_text(encoding='utf-8'))
print(json.dumps({'upstream_commit': version['commit'], 'upstream_files': len(actual),
                  'cartridge_sha256': hashlib.sha256(cartridge).hexdigest(),
                  'local_links': 'pass', 'result': 'pass'}, indent=2))
