"""Prepare reproducible host-compiler and cartridge-runtime source variants."""
from pathlib import Path
import shutil
import subprocess
from cartridge_graphics import ADDRESSES

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'references/2068-Leap'
REV = '77f1baaf30424f2cec8cf31cae90513faa9c45c5'
if (REF/'REVISION').read_text().strip() != REV:
    raise SystemExit('Leap reference revision differs from the audited revision')


def replace_once(path, old, new):
    text = path.read_text(encoding='utf-8')
    if text.count(old) != 1:
        raise ValueError(f'Expected exactly one matching source block in {path}: {old[:80]!r}')
    path.write_text(text.replace(old, new), encoding='utf-8')


for variant in ('host', 'cartridge','wide-host','wide-cartridge'):
    wide=variant.startswith('wide-')
    dest = ROOT / 'build' / variant
    dest.mkdir(parents=True, exist_ok=True)
    for name in ('rom', 'include', 'kernel', 'basic', 'tools'):
        shutil.copytree(REF / name, dest / name, dirs_exist_ok=True)
    (dest / 'build').mkdir(exist_ok=True)
    # v2.0.2-emu.1 includes the official nested array-kind fix (M-4).
    layout = dest / 'include/v2_layout.inc'
    replace_once(layout, 'V2_CODE_LIMIT   EQU $B600', 'V2_CODE_LIMIT   EQU $7F00')
    replace_once(layout, 'V2_CODE_SIZE    EQU 4011', 'V2_CODE_SIZE    EQU '+('$3F00' if wide else '$1F00'))
    replace_once(layout, 'V2_SOURCE_END   EQU V2_CODE_BASE', 'V2_SOURCE_END   EQU $B600')
    text=layout.read_text(encoding='utf-8')
    layout.write_text('; Cartridge prototype: code $6000-$7EFF, RAM arena ends at $B600.\n'
                      '; Historical upstream layout commentary below is retained for reference.\n'+text,
                      encoding='utf-8')
    replace_once(dest/'rom/v2_home.asm','    DS V2_HOME_IMAGE_END - $, $FF','''    ASSERT $ <= $3FF0
    ORG $3FF0
; A=requested DOCK mask, C=previous mask, HL=address. No stack use while chunk 7 is hidden.
CARTRIDGE_FAR_BYTE:
    out ($F4),a
    ld b,(hl)
    ld a,c
    out ($F4),a
    ld l,b
    ld h,0
    ret
    DS V2_HOME_IMAGE_END - $, $FF''')
    if variant.endswith('cartridge'):
        bank = dest / 'kernel/bank/bank.asm'
        bank_source='''; Cartridge service banking: both Leap images come from DOCK.
; Keep chunks 0, 1 and 3 mapped at every transition. Only chunk 6 changes.
; Interrupt vector/code are in DOCK 0; stack and state stay in HOME 7/4/5.
; AF destroyed; retains the upstream depth counter and DI/EI convention.
    IFNDEF KERNEL_BANK_ASM
    DEFINE KERNEL_BANK_ASM
BANK_PAGE_EXROM_IN:
    di
    ld a,(BANK_EXROM_DEPTH)
    inc a
    ld (BANK_EXROM_DEPTH),a
    cp 1
    jr nz,.already_paged_in
    ld a,(PORT_FF_SHADOW)
    and %01111111
    ld (PORT_FF_SHADOW),a
    out (PORT_SCLD),a
    ld a,%01001011
    out (PORT_BANK_HOME),a
.already_paged_in:
    ei
    ret
BANK_PAGE_EXROM_OUT:
    di
    ld a,(BANK_EXROM_DEPTH)
    or a
    jr z,.depth_already_zero
    dec a
    ld (BANK_EXROM_DEPTH),a
    jr nz,.still_nested
    ld a,%00001011
    out (PORT_BANK_HOME),a
.still_nested:
.depth_already_zero:
    ei
    ret
    ENDIF
'''
        if wide: bank_source=bank_source.replace('%01001011','%01001111').replace('%00001011','%00001111')
        bank.write_text(bank_source,encoding='utf-8')
        if wide:
            graphics=dest/'kernel/graphics/graphics.asm'
            for name,address in ADDRESSES.items():
                replace_once(graphics,'\n'+name+':',f'\n{name} EQU ${address:04X}\nREAL_{name}:')

# TSRun modules are included in tools/tsrun; see DEPENDENCIES.json.
print('Prepared host compiler and DOCK runtime; bytecode $6000-$7EFF, metadata $7F00, arena top $B600')
