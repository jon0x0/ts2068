"""RAM-bytecode Crown runtime: system $5B00, VM $C000, arena $CA00-$F100."""
from pathlib import Path
import shutil
import re
from cartridge_graphics import ADDRESSES

ROOT = Path(__file__).resolve().parents[1]
dest = ROOT/'build/combined-runtime'
shutil.copytree(ROOT/'build/runtime-only', dest, dirs_exist_ok=True)
# All fixed VM workspace addresses move together by $0A00. No ROM instructions
# reside in this address range in these source files.
for folder in ('rom','include','kernel'):
    for p in (dest/folder).rglob('*'):
        if p.suffix not in ('.asm','.inc'): continue
        s = p.read_text()
        s = re.sub(r'\$([0-9A-Fa-f]{4})\b', lambda m: '$%04X'%(int(m[1],16)+0xA00) if 0xB600<=int(m[1],16)<0xC000 else m[0], s)
        p.write_text(s)
sysvars = dest/'include/sysvars.inc'
s = sysvars.read_text().replace('    ORG $8000','    ORG $5B00',1)
s = s.replace('PROG_AREA_START:', '    ORG $CA00\nPROG_AREA_START:',1)
s = s.replace('PROG_AREA_MAX        EQU $C000','PROG_AREA_MAX        EQU $F100')
sysvars.write_text(s)
layout = dest/'include/v2_layout.inc'
s = layout.read_text().replace('V2_CODE_LIMIT   EQU $7F00','V2_CODE_LIMIT   EQU $BE00').replace('V2_CODE_SIZE    EQU $3F00','V2_CODE_SIZE    EQU $3E00')
s = s.replace('V2_SOURCE_END   EQU $C000','V2_SOURCE_END   EQU $F100')
# The secondary array arena is disabled; the larger primary arena is retained.
s = s.replace('ARR2_BASE:        equ $E000','ARR2_BASE:        equ $F100').replace('ARR2_LIMIT:       equ $E800','ARR2_LIMIT:       equ $F100')
layout.write_text(s)
layout.write_text(s.replace('    ASSERT ARR2_LIMIT <= SPRITE_SLOT_IMG_BUF','; Crown uses no sprite-buffer arena.'))
abi = dest/'include/v2_package_abi.inc'
s = abi.read_text()
s = re.sub(r'\$([0-9A-Fa-f]{4})\b', lambda m: '$%04X'%(int(m[1],16)-0x2500) if 0x8000<=int(m[1],16)<0x825A else m[0], s)
abi.write_text(s)
memory = dest/'kernel/memory/memory.asm'
s = memory.read_text().replace('ld   hl, $8000','ld   hl, $5B00',1).replace('PROG_AREA_MAX - $8000','PROG_AREA_MAX - $5B00',1)
# No line-store/editor operates in this cartridge. Keep generic fills/shifts.
s = s[:s.index('; MEM_LINE_FIRST')]+'\nMEM_LINE_FIRST:\nMEM_LINE_NEXT:\n    ld hl,0\n    ret\n'
memory.write_text(s)
ktab = dest/'include/v2_ktab.inc'
s = ktab.read_text()
s = re.sub(r'^.*V2_KTAB_ENTRY MEM_LINE_.*\n','',s,flags=re.M)
s = s.replace('V2_EXROM_ENTRY_ADDR EQU $C000','V2_EXROM_ENTRY_ADDR EQU $2800').replace('V2_EXROM_IMAGE_END EQU $E000','V2_EXROM_IMAGE_END EQU $3800')
ktab.write_text(s)
# Native display calls use HOME RAM directly; no graphics mapping veneers.
graphics = dest/'kernel/graphics/graphics.asm'
s = graphics.read_text()
for name,address in ADDRESSES.items():
    s = s.replace(f'{name} EQU ${address:04X}\nREAL_{name}:',f'{name}:')
graphics.write_text(s)
bank = dest/'kernel/bank/bank.asm'
bank.write_text('''BANK_PAGE_EXROM_IN:
    ld a,3
    ld ($F7E2),a
    out ($F4),a
    ret
BANK_PAGE_EXROM_OUT:
    ret
''')
# Prompt-time session recarving is unused in the source-free game runtime.
vm = dest/'rom/exrom_v2_vm_core.asm'
s = vm.read_text()
s = s[:s.index('VM_INIT_SESSION:')]+s[s.index('VM_CARVE_TABLES:'):]
vm.write_text(s)
print(dest)
