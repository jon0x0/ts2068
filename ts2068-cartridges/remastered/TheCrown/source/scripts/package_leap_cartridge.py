"""Pack a compiler export into a DOCK cartridge and reusable bytecode file."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import shutil
import zlib
from cartridge_graphics import helper_assembly

ROOT = Path(__file__).resolve().parents[1]


def load_symbols(path):
    return {m[1]: int(m[2], 16) for line in path.read_text().splitlines()
            if (m := re.match(r'(\S+):\s+EQU\s+0x([0-9a-f]+)', line, re.I))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('export', type=Path)
    ap.add_argument('--output', type=Path, default=ROOT/'build/smoke')
    ap.add_argument('--runtime', type=Path, help='Assembled cartridge runtime directory')
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    export = json.loads(args.export.read_text())
    if export['format'] != 'leap-bytecode-v1' or export['base'] not in (0x4000,0x6000):
        raise ValueError('Unsupported compiler export format/base')
    code = bytes.fromhex(export['code'])
    wide=export['base']==0x4000
    if not 0 < len(code) <= (0x3F00 if wide else 0x1F00) or len(export['counts']) != 5:
        raise ValueError('Invalid bytecode size or symbol counts')
    host = ROOT/('build/wide-host' if wide else 'build/host')
    cart = ROOT/('build/wide-cartridge' if wide else 'build/cartridge')
    if args.runtime: cart = args.runtime.resolve()
    S = load_symbols(cart/'build/test_basic.sym')
    image = bytearray([255])*(16384 if wide else 8192)
    image[:len(code)] = code
    meta=0x3F00 if wide else 0x1F00
    image[meta:meta+7] = bytes(export['counts']) + struct.pack('<H', len(code))
    if wide: (out/'bytecode-low.bin').write_bytes(image[:8192])
    (out/'bytecode-chunk.bin').write_bytes(image[8192:] if wide else image)
    assets=Path(export['packedData']).read_bytes() if export.get('packedData') else b''
    if len(assets)>23376: raise ValueError('Packed assets exceed cartridge capacity')
    for i,start in enumerate((6992,15184),5):
        chunk=bytearray([255])*8192; part=assets[start:start+8192]; chunk[:len(part)]=part
        if part: (out/('assets-5.bin' if i==5 else 'assets-7.bin')).write_bytes(chunk)
    # Exact host-ROM identity makes this an explicitly versioned payload, not a universal ABI.
    identity = hashlib.sha256((host/'v2_home.bin').read_bytes()+(host/'v2_exrom.bin').read_bytes()).digest()
    header = b'LBC1'+struct.pack('<HH',export['base'],len(code))+bytes(export['counts'])+identity
    (out/'program.lbc').write_bytes(header+struct.pack('<I',zlib.crc32(header+code))+code)
    required = ['MEM_COLD_INIT','MEM_INIT','PORT_FF_SHADOW','EXT2_CLEAR_ALL','KBD_ISR_INIT',
                'BANK_PAGE_EXROM_IN','SYM_COUNTS','SYM_END_V','PROG_AREA_START','SESS_GAP',
                'PAS_END','ARR2_BASE','VM_INIT','VM_IP','VM_RUN','GFX_CLS','CURRENT_PAPER',
                'V2_SOURCE_END','VM_ERROR_CODE','VARS_START','ARRAYS_END']
    equs = ''.join(f'{name} EQU ${S[name]:04X}\n' for name in required)
    # Chunk 4 boot code hands off to HOME $5B00 before removing its own mapping.
    asm = equs + '''    DEVICE NOSLOT64K
    ORG $8000
    DB 2,2
    DW $8008
    DB $EF,1
    DW 0
boot:
    di
    ld sp,$FF00
    xor a
    out ($FF),a
    ld a,$10
    out ($F4),a
    ld hl,stub_source
    ld de,$5B00
    ld bc,stub_end-stub_source
    ldir
    ld hl,helper_source
    ld de,$F400
    ld bc,$200
    ldir
    jp $5B00
stub_source:
    DISP $5B00
runtime_start:
    ld a,$4B
    out ($F4),a
    call MEM_COLD_INIT
    xor a
    ld (PORT_FF_SHADOW),a
    call MEM_INIT
    ld hl,V2_SOURCE_END
    ld ($B809),hl                 ; SYM_LIMIT_V
    call EXT2_CLEAR_ALL
    ld a,$4B
    ld ($F7E2),a
    xor a
    ld ($F7D0),a
    call KBD_ISR_INIT
    im 1
    ei
    call BANK_PAGE_EXROM_IN
    ld hl,$7F00
    ld de,SYM_COUNTS
    ld bc,5
    ldir
    ld hl,PROG_AREA_START-SESS_GAP-1
    ld (SYM_END_V),hl             ; VM_INIT starts arrays at PROG_AREA_START
    ld hl,ARR2_BASE
    ld (PAS_END),hl               ; no persistent Array Store
    call VM_INIT
    ld a,7
    ld (CURRENT_PAPER),a
    call GFX_CLS
    ld hl,$6000
    ld (VM_IP),hl
    call VM_RUN
    ld hl,(VARS_START)
    ld de,(ARRAYS_END)
    or a
    sbc hl,de                    ; final debugger checkpoint: HL = free arena bytes
    jp $5BFE
    ASSERT $ <= $5BFE
    DS $5BFE-$,$00
runtime_done:
    jr runtime_done
    ENT
stub_end:
    ASSERT $ <= $A000
    IF $ < $A000
    DS $A000-$,$FF
    ENDIF
    SAVEBIN "launcher.bin",$8000,$2000
'''
    asm=asm.replace('    ld hl,$6000\n    ld (VM_IP),hl',f'    ld hl,${export["base"]:04X}\n    ld (VM_IP),hl')
    if wide:
        asm=asm.replace('ld a,$4B','ld a,$4F').replace('$5B00','$F600').replace('$5BFE','$F6FE')
    # Replace final padding with a 512-byte native bank-reader/display veneer image.
    old='''    ASSERT $ <= $A000
    IF $ < $A000
    DS $A000-$,$FF
    ENDIF
    SAVEBIN "launcher.bin",$8000,$2000
'''
    replacement='''    ASSERT $ <= $8200
    DS $8200-$,$FF
'''+helper_assembly(S,wide,len(assets))+'''
    ASSERT $ == $8400
    DS $84B0-$,$FF
'''
    if assets:
        (out/'assets-first.bin').write_bytes(assets[:6992])
        replacement+='    INCBIN "assets-first.bin"\n'
    replacement+='''    ASSERT $ <= $A000
    IF $ < $A000
    DS $A000-$,$FF
    ENDIF
    SAVEBIN "launcher.bin",$8000,$2000
'''
    if asm.count(old)!=1: raise ValueError('Bootstrap padding template mismatch')
    asm=asm.replace(old,replacement)
    (out/'launcher.asm').write_text(asm)
    for src, name in [(ROOT/'tools/tsrun/roms/ts2068-0.rom','stock-home.rom'),
                      (ROOT/'tools/tsrun/roms/ts2068-1.rom','stock-exrom.rom')]:
        shutil.copyfile(src,out/name)
    manifest = {
        'status':'prototype; assemble launcher then finish packaging',
        'leap_revision':'77f1baaf30424f2cec8cf31cae90513faa9c45c5',
        'code_bytes':len(code), 'symbol_counts':export['counts'],
        'bytecode_base':export['base'], 'runtime_pool_bytes':0xB600-0x825A,
        'runtime_variant':cart.name,'host_variant':host.name,'packed_asset_bytes':len(assets),'levels':export.get('levels',[]),
        'source_in_runtime_ram':False, 'compiler_symbol_names_in_runtime_ram':False,
        'host_rom_sha256':identity.hex(),
        'cartridge_rom_sha256':hashlib.sha256((cart/'v2_home.bin').read_bytes()+(cart/'v2_exrom.bin').read_bytes()).hexdigest(),
        'tsrun_modules_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'tools/tsrun').glob('*.js'))},
    }
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Wrote {out}/launcher.asm and program.lbc ({len(code)} bytes of code)')


if __name__ == '__main__':
    main()
