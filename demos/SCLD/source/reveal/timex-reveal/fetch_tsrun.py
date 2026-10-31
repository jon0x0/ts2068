"""Download the pinned emulator modules for the optional headless checks."""
from pathlib import Path
from urllib.request import urlopen

commit='41dbe3e41c692a1806f2cb900c5a0faa1549ae77'
target=Path(__file__).resolve().parent/'tsrun'
target.mkdir(exist_ok=True)
for name in ['machine.js','z80.js','dock.js','ay.js','tape.js']:
    url=f'https://raw.githubusercontent.com/josef-jelinek/TSRun/{commit}/{name}'
    with urlopen(url) as response:
        (target/name).write_bytes(response.read())
(target/'package.json').write_text('{"type":"module"}\n')
print('Run node test_demo.mjs after python build_demo.py')
