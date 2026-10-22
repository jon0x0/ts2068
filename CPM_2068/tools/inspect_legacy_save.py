"""Decode the original 1.00 frozen SAVE routines without executing firmware.

Requires the official MicroPython v1.20.0 tools/mpy-tool.py and
py/makeqstrdata.py under build/analysis/micropython-1.20 (or --decoder).
Run inspect_legacy_uf2.py first. Addresses apply only to the checked payload.
"""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import struct
import sys

PAYLOAD_SHA256 = 'd77de8db3372e7f4c368d17d04facabf295b4fec60c2a24c3d2ac3f166dee5c6'
BASE = 0x10000000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='Decode every frozen function, including CDIR and SEND_MSG')
    parser.add_argument('--image', type=Path, default=Path('build/analysis/firmware-1.00.bin'))
    parser.add_argument('--decoder', type=Path, default=Path('build/analysis/micropython-1.20/tools/mpy-tool.py'))
    parser.add_argument('--output', type=Path, default=Path('build/analysis/firmware-1.00-save-bytecode.txt'))
    args = parser.parse_args()
    image = args.image.read_bytes()
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA256:
        raise SystemExit('Not the audited original 1.00 payload; fixed addresses are unsafe.')
    sys.path.insert(0, str(args.decoder.resolve().parent))
    spec = importlib.util.spec_from_file_location('legacy_mpy_decoder', args.decoder)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    word = lambda offset: struct.unpack_from('<I', image, offset)[0]
    short = lambda offset: struct.unpack_from('<H', image, offset)[0]
    qstrs = {}
    for pool in (0x3b378, 0x47a18):
        for index in range(word(pool + 12)):
            offset = word(pool + 24 + 4 * index) - BASE
            qstrs[word(pool + 4) + index] = image[offset:image.index(0, offset)].decode('utf8')
    # Frozen tspico.py module: qstr table, object table, root raw-code pointer.
    qtable, objects, root = (word(0x4345c + i) - BASE for i in (0, 4, 8))
    qname = lambda index: qstrs[short(qtable + index * 2)]
    functions = []
    for record in range(0x484bc, root + 1, 16):
        start = word(record + 4) - BASE
        prelude = decoder.extract_prelude(image, start)
        functions.append((qname(prelude[-1][0]), start, prelude[4]))
    lines = ['Original 1.00 payload SHA256 ' + PAYLOAD_SHA256,
             'Decoded with official MicroPython v1.20.0 bytecode definitions.',
             'Offsets below are original flash addresses; this is static analysis.']
    selected = {name for name, _, _ in functions} if args.all else {'SAVE_TS', 'SAVE_ZX', 'SA_NOT_IMP', 'PROCESS_CMD'}
    for index, (name, start, ip) in enumerate(functions[:-1]):
        if name not in selected:
            continue
        end = functions[index + 1][1]
        lines.append(f'\nFUNCTION {name} @{BASE + start:08x}')
        while ip < end:
            fmt, size, arg, _ = decoder.mp_opcode_decode(image, ip)
            opcode = image[ip]
            if fmt == decoder.MP_BC_FORMAT_QSTR:
                arg = repr(qname(arg))
            elif opcode == decoder.Opcode.MP_BC_LOAD_CONST_OBJ:
                value = word(objects + 4 * arg)
                if value & 3 == 2:
                    arg = repr(qstrs[value >> 3])
                elif 0x10042b00 < value < 0x10042d9c and word(value - BASE) == 0x10038b74:
                    offset = value - BASE
                    data = word(offset + 12) - BASE
                    arg = repr(image[data:data + word(offset + 8)])
                else:
                    arg = f'object@{value:08x}'
            elif fmt == decoder.MP_BC_FORMAT_OFFSET:
                arg = f'{arg:+} -> {BASE + ip + size + arg:08x}'
            elif fmt == decoder.MP_BC_FORMAT_BYTE:
                arg = ''
            lines.append(f'{BASE + ip:08x} {image[ip:ip + size].hex():<8} {decoder.Opcode.mapping[opcode]} {arg}')
            ip += size
        assert ip == end, (name, ip, end)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(lines) + '\n')
    print(args.output)
    print('SAVE_TS: header -> open wb -> write -> close; data -> open ab -> write -> close.')
    print('Every subsequent SAVE_TS executes wb again, replacing the previous TAP.')


if __name__ == '__main__':
    main()
