"""Derive an execution-only cartridge build without changing the host compiler."""
from pathlib import Path
import shutil
import re

ROOT = Path(__file__).resolve().parents[1]
dest = ROOT/'build/runtime-only'
shutil.copytree(ROOT/'build/wide-cartridge', dest, dirs_exist_ok=True)
home = dest/'rom/v2_home.asm'
s = home.read_text()
s = s.replace('    DEFINE V2_PRODUCTION', '    DEFINE V2_RST_VM_ONLY\n    DEFINE V2_PRODUCTION', 1)
for name in ('exrom_v2_compiler', 'v2_saveall', 'v2_session_undo'):
    s = re.sub(r'^.*INCLUDE "rom/'+name+r'\.asm".*\n', '', s, flags=re.M)
s = s.replace('    ASSERT $ <= $3FF0', "FOLD_UPPER:\n    cp 'a'\n    ret c\n    cp 'z'+1\n    ret nc\n    and $DF\n    ret\nHOME_RUNTIME_END:\n    ASSERT $ <= $3FF0")
home.write_text(s)
low = dest/'rom/v2_lowrom_fill.asm'
s = low.read_text()
s = re.sub(r'    ORG \$001B.*?(?=    ORG \$0035)', '', s, flags=re.S)
low.write_text(s)
ktab = dest/'include/v2_ktab.inc'
s = ktab.read_text()
s = re.sub(r'^.*V2_KTAB_ENTRY (COMPILER_INIT|COMPILE_PROGRAM|V2_GET_KEYWORD_TABLE|CHUNK_REFILL),.*\n', '', s, flags=re.M)
ktab.write_text(s)
ex = dest/'rom/v2_exrom.asm'
s = ex.read_text().replace('jp V2_COMMAND_LOOP', 'ret\n    nop\n    nop')
s = re.sub(r'^.*INCLUDE "kernel/storage/storage.asm".*\n', '', s, flags=re.M)
s = re.sub(r'^.*INCLUDE "rom/exrom_editor.asm".*\n', '', s, flags=re.M)
shell = (dest/'rom/exrom_v2_shell.asm').read_text()
clear = shell[shell.index('MEM_CLEAR_V2:'):shell.index('\nV2_MATCH_EXACT:')].replace('jp ARR_RUN_INIT', 'ld hl,ARR2_BASE\n    ld (ARR2_END),hl\n    ret')
s = re.sub(r'^.*INCLUDE "rom/exrom_v2_shell.asm".*\n', clear+'\nEXROM_RUNTIME_END:\n', s, flags=re.M)
ex.write_text(s)
arrays = dest/'rom/exrom_v2_arrstore.asm'
s = arrays.read_text()
slots = s[s.index('ARRSVC_TABLE:'):s.index('; ---- store iteration')]
slot = s[s.index('ARR_SLOT:'):s.index('; ARR_RUN_INIT --')]
dim = s[s.index('ARR_OP_DIM:'):s.index('; ---- tape side:')]
# No prompt-time persistent array store exists in an execution-only cartridge.
dim = dim.replace('    call ARR_AT_END', '    ld de,(PAS_END)\n    push hl\n    or a\n    sbc hl,de\n    pop hl\n    ccf')
arrays.write_text(slots+slot+dim)
cross = dest/'tools/write_v2_crossbank.py'
s = cross.read_text().replace('missing = set(NAMES) - symbols.keys()', 'missing = set()')
s = s.replace('for name in NAMES + tuple(n for n in OPTIONAL if n in symbols)', 'for name in NAMES + OPTIONAL if name in symbols')
cross.write_text(s)
print(dest)
