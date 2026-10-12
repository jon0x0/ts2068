"""Reproducible v0.1 ROM-only build using the local SjASMPlus assembler.

Generates algorithm expansions and immutable menu data, not RAM-executed code.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
DEFAULT_ASSEMBLER = ROOT.parent / 'cartridgeconversion/sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'


def ram_source():
    lines, phases = [], []
    phase = 0
    def start(name, expected):
        nonlocal phase
        phase += 1
        phases.append(dict(phase=phase, name=name, expected=expected))
        lines.extend([f' ld a,{phase}', ' ld i,a', f' ld d,${expected:02x}',
                      ' ld a,6', ' out ($fe),a', ' ld hl,$4000'])
        return phase
    def finish_loop(label, direction):
        if direction == 'up':
            lines.extend([' inc hl', ' ld a,h', ' or l', f' jp nz,{label}'])
        else:
            lines.extend([' dec hl', ' ld a,h', ' cp $3f', f' jp nz,{label}'])
    for pat in (0,255,85,170,15,240,51,204):
        n = start('full-pattern', pat)
        lines.extend([f'fill_{n}:', ' ld (hl),d'])
        finish_loop(f'fill_{n}', 'up')
        lines.extend([' ld hl,$4000', f' ld iy,read_next_{n}', f'read_{n}:', ' jp compare_byte', f'read_next_{n}:'])
        finish_loop(f'read_{n}', 'up')
    for bit in range(8):
        for pat in (1 << bit, 255 ^ (1 << bit)):
            n = start('walking-bit-immediate', pat)
            lines.extend([f' ld iy,walk_next_{n}', f'walk_{n}:', ' ld (hl),d', ' jp compare_byte', f'walk_next_{n}:'])
            finish_loop(f'walk_{n}', 'up')
    lines.extend([" ex af,af'", ' ld b,a', " ex af,af'", ' ld a,b', ' cp 1', ' jp z,tests_done', 'march_start:'])
    n = start('march-initialize', 0)
    lines.extend([f'march_fill_{n}:', ' ld (hl),d'])
    finish_loop(f'march_fill_{n}', 'up')
    for direction, old, new in [('up',0,255),('up',255,0),('down',0,255),('down',255,0),('up',0,None)]:
        n = start('march-' + direction, old)
        if direction == 'down':
            lines.append(' ld hl,$ffff')
        lines.extend([f' ld iy,march_next_{n}', f'march_read_{n}:', ' jp compare_byte', f'march_next_{n}:'])
        if new is not None:
            lines.append(f' ld (hl),${new:02x}')
        finish_loop(f'march_read_{n}', direction)
    lines.append(' jp tests_done')
    return '\n'.join(lines) + '\n', phases


def make_menu():
    ref = ROOT.parent / 'David Anderson/TS2068-Ref-Library/2068 ROMS/TS2068_U16.BIN'
    rom = ref.read_bytes()
    assert hashlib.sha1(rom).hexdigest() == '1446cb2780a9dedf640404a639fa3ae518b2d8aa'
    font = rom[0x3d00:0x4000]
    pixels, attrs = bytearray(6144), bytearray([7]*768)
    def text(row, col, value, attr=7):
        assert col + len(value) <= 32
        for x, ch in enumerate(value, col):
            code = ord(ch)
            assert 32 <= code <= 127
            for y in range(8):
                py = row * 8 + y
                off = ((py & 192) << 5) | ((py & 7) << 8) | ((py & 56) << 2) | x
                pixels[off] = font[(code-32)*8+y]
            attrs[row*32+x] = attr
    attrs[:64] = bytes([0x4f]*64)
    text(0, 2, 'TS2068 DIAGNOSTICS', 0x4f)
    text(1, 2, 'ROM-ONLY BRING-UP     v0.1', 0x4f)
    text(3, 2, 'RAM SWEEP COMPLETE', 0x44)
    text(4, 2, 'All tested bytes matched', 7)
    text(6, 2, '1  Full RAM / walking / March', 0x46)
    text(8, 2, '2  Pattern and bit tests', 7)
    text(10, 2, '3  March C- RAM test', 7)
    text(13, 2, 'Tests overwrite all HOME RAM', 2)
    text(15, 2, 'Border / sound report faults', 5)
    text(17, 2, 'Other modules: not built yet', 7)
    text(20, 2, 'Full test runs at startup', 7)
    attrs[23*32:] = bytes([0x4f]*32)
    text(23, 2, 'PRESS 1, 2 OR 3 TO RUN', 0x4f)
    return bytes(pixels + attrs), hashlib.sha256(rom).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--assembler', type=Path, default=DEFAULT_ASSEMBLER)
    args = parser.parse_args()
    BUILD.mkdir(exist_ok=True)
    generated, phases = ram_source()
    (BUILD / 'ram-tests.asm').write_text(generated, encoding='ascii')
    source = (ROOT / 'src/archive/diagnostic-v01.asm').read_text(encoding='utf-8')
    # Safety-critical stack audit covers handwritten and generated assembly.
    code = '\n'.join(line.split(';')[0] for line in (source + generated).splitlines())
    assert not re.search(r'^\s*(call|ret\w*|push|pop|rst|halt|ei)\b', code, re.M | re.I)
    assert not re.search(r'^\s*(ld\s+sp\b|(?:inc|dec)\s+sp\b)', code, re.M | re.I)
    assert not re.search(r'ld\s*\(\$[0-9a-f]+\)', code, re.I), 'No absolute HOME state writes'
    subprocess.run([str(args.assembler), '--nologo', '--raw=' + str(BUILD/'low.bin'),
                    '--sym=' + str(BUILD/'symbols.txt'), str(ROOT/'src/archive/diagnostic-v01.asm')], cwd=ROOT, check=True)
    low = (BUILD / 'low.bin').read_bytes()
    assert len(low) == 8192
    menu, font_hash = make_menu()
    flat = bytearray([255]*65536)
    flat[:8192] = low
    flat[8192:8192+len(menu)] = menu
    # Separate high ROM anchor: entry disables IRQ and establishes both anchors,
    # then transfers to low kernel. It is not advertised as a HOME checksum yet.
    flat[0x8000:0x8008] = bytes.fromhex('f33e11d3f4c30001')
    assert len(flat) == 65536
    descriptors = bytes([2,2,0,0,2,0,0,0])
    dck = bytes([0]) + descriptors + b''.join(flat[n*8192:(n+1)*8192] for n,v in enumerate(descriptors) if v==2)
    (BUILD/'diagnostic-v01.bin').write_bytes(flat)
    (BUILD/'diagnostic-v01.dck').write_bytes(dck)
    manifest = dict(version='0.1', entry='0100', hsr_tests='01', decr='40', descriptors=list(descriptors),
                    dck_sha256=hashlib.sha256(dck).hexdigest(), bin_sha256=hashlib.sha256(flat).hexdigest(),
                    phases=phases, font_rom_sha256=font_hash,
                    source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                    generated_sha256=hashlib.sha256(generated.encode()).hexdigest(),
                    limitation='Post-LROS stackless tests; native launch depends on stock initialization; hardware validation pending')
    (BUILD/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Built ROM-only v0.1 DCK and 64K physical BIN; stack/control audit passed.')


if __name__ == '__main__':
    main()
