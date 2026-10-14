"""Rebuild and verify the released cartridge on Windows with WSL."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)


def run(*args):
    subprocess.run(list(map(str, args)), check=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    if sys.platform != 'win32':
        raise SystemExit('This build driver uses Windows Python and WSL; see README.md.')
    for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if sha(ROOT / name) != expected:
            raise SystemExit('Source checksum mismatch: ' + name)
    run('wsl', 'bash', '-c', 'make -C tools/sjasmplus USE_LUA=0 -j4 && gcc -O2 tools/ZX0/src/zx0.c tools/ZX0/src/optimize.c tools/ZX0/src/compress.c tools/ZX0/src/memory.c -o tools/ZX0/zx0 && gcc -O2 tools/ZX0/src/dzx0.c -o tools/ZX0/dzx0')
    shutil.copytree(ROOT / 'inputs/intro-locked', ROOT / 'build/intro-eight-locked', dirs_exist_ok=True)
    run(sys.executable, 'scripts/build_leap_program.py', 'original/TheCrown.bas', '--ts2068', '--profile', 'conversions/crown_level1.json', '--wide', '--no-run', '--output', 'build/crown', '--prepare')
    run('wsl', 'bash', 'scripts/build_combined_runtime.sh')
    run(sys.executable, 'scripts/build_crown_combined.py')
    expected = '481a5ada28700ce312b5b8388008195701a523da671f7a0fefe7f835a31540cd'
    actual = sha(ROOT / 'build/crown-combined/program.dck')
    if actual != expected:
        raise SystemExit(f'Release cartridge differs: {actual}')
    # BASIC line endings are platform dependent; compare the actual program text.
    if (ROOT / 'leap/TheCrown.leap.bas').read_text() != (ROOT / 'build/crown-combined/startup.leap.bas').read_text():
        raise SystemExit('Final Leap BASIC differs from the release snapshot')
    print('Verified exact release cartridge SHA256: ' + actual)
