"""Explicit opt-in full-game build context. Default r22 builds remain unchanged."""
from pathlib import Path
import os,json
ROOT=Path(__file__).resolve().parents[1]
FULL=os.environ.get('RTYPE_FULLGAME')=='1'
LEVEL=int(os.environ.get('RTYPE_LEVEL','1'))
def layout():
 return json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][LEVEL-1]
def raw_snapshot():
 return (ROOT/f'build/fullgame/foundation/level{LEVEL:02d}.raw').read_bytes() if FULL else (ROOT/'build/spectrum_baseline/postload_4000_FFFF.bin').read_bytes()
def transform(source,text):
 if not FULL:return text
 d=layout();start=d['terrain_start'];end=d['map_start'];last=json.loads((ROOT/f'build/fullgame/converted/level{LEVEL:02d}/manifest.json').read_text())['enemy_lookup_end']
 if source.name=='terrain_palette.asm':return (ROOT/'src/terrain_palette_full.asm').read_text()
 if source.name=='terrain_fast.asm':
  a=text.index('        LD A,IXL');b=text.index('        LD A,(DE)',a)
  text=text[:a]+'''        LD A,IXL
        CALL $0E78
        PUSH HL
        LD A,IXH
        CALL $0E78
        PUSH HL
        POP IX
        POP HL
        POP BC
'''+text[b:]
 if source.name=='animate_orb.asm' and LEVEL!=1:return '        ORG $0D00\n        RET\n'
 if source.name=='restore_terrain_palette.asm':
  text=text.replace('$D9',f'${start>>8:02X}').replace('$E6',f'${(end>>8)+1:02X}').replace('$E5',f'${end>>8:02X}').replace('CP $11',f'CP ${start&255:02X}').replace('CP $71',f'CP ${end&255:02X}')
 if source.name in ('ecm_tspico.asm','ecm_rom.asm'):
  # Full-game enemies carry one of16 palette-row IDs in ink/bright bits.
  text=text.replace('INCLUDE "src/boss_colour_lookup.inc"','INCLUDE "src/full_boss_colour_lookup.inc"')
  converted=json.loads((ROOT/f'build/fullgame/converted/level{LEVEL:02d}/manifest.json').read_text())
  defines=f'SOURCE_ENEMY_END EQU ${d["enemy_descriptors_start"]:04X}\n'
  if converted['pool_start']is not None:defines+=f'ENEMY_POOL_START EQU ${converted["pool_start"]:04X}\nENEMY_POOL_END EQU ${converted["pool_end"]:04X}\n'
  if converted['pool_start']is None:defines+='ENEMY_POOL_START EQU 0\nENEMY_POOL_END EQU 0\n'
  text=defines+text
 return text
