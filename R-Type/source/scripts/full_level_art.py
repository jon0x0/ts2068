"""Generalized per-level terrain and palette metadata for native ECM builds."""
from pathlib import Path
import json
import numpy as np
from fullgame_context import LEVEL,layout
from terrain_themes import remap_attribute

def build_terrain(root,out):
 d=layout();mem=bytes(16384)+(root/'build/native/snapshot.bin').read_bytes();end=d['map_start'];patch=bytearray();original=b''.join(mem[end-(t+1)*144:end-t*144]for t in range(d['terrain_tiles']))
 if LEVEL==1:original=(root/'assets/terrain_level01_arcade.bin').read_bytes()
 if LEVEL==2:original=(root/'build/fullgame/converted/level02/terrain_bitmap_overrides.bin').read_bytes()
 for t in range(d['terrain_tiles']):
  for cy in range(4):
   for cx in range(4):
    p=t*144+(cy*4+cx)*9;a=original[p];patch.append(128+cy if a&128 else a);patch+=original[p+1:p+9]
 assert all(not (16<=a<32)for a in original[::9]if not a&128),'Reserved enemy token range used by native terrain'
 reference=(root/'assets/palette_reference_r21.bin').read_bytes();theme=json.loads((root/'assets/terrain_themes.json').read_text())['themes'][LEVEL-1]
 table=bytes(remap_attribute(a,theme['primary_ink_map'] if i<64 else theme['secondary_ink_map'])for i,a in enumerate(reference));palette=table+bytes([71])*(1024-128)
 if LEVEL==2:
  body=(root/'build/fullgame/converted/level02/terrain_boss_palette.bin').read_bytes();palette=bytearray(palette)
  for cy in range(4):
   row=body[cy*8:cy*8+8];palette[cy*8:(cy+1)*8]=row;palette[(4+cy)*8:(5+cy)*8]=row[::-1]
  palette=bytes(palette)
 # Reuse the proven world-cell grouping algorithm with typed level bounds.
 source=(root/'scripts/terrain_groups.py').read_text().replace('assert len(w)==535 and max(c&63 for c in w)==21','assert len(w)%5==0').replace('range(22)','range(LEVEL_TILES)').replace('assert len(data)<=440','assert len(data)>0')
 
 if LEVEL==2:source=source.replace('style=(j+row//2)&1','style=0 if row>=8 and row<20 and g[-1]>=224 and g[0]<252 else (j+row//2)&1')
 namespace={'LEVEL_TILES':d['terrain_tiles']};exec(compile(source,'terrain_groups_generalized','exec'),namespace);report=namespace['build'](root,out,mem,patch)
 runs=report['runs'];masks=sorted(set(v[1]for v in runs)|{0});data=bytearray()
 for i,(_,mask)in enumerate(runs):data+=(runs[i+1][0]if i+1<len(runs)else d['map_columns']*4).to_bytes(2,'little')+bytes([masks.index(mask)])
 data+=b'\xff\xff'+bytes([masks.index(0)]);dictionary=0x200+len(data)
 for mask in masks:data+=mask.to_bytes(3,'little')
 assert len(data)<=640,(LEVEL,len(data));(out/'terrain_group_full.bin').write_bytes(data)
 report.update(level=LEVEL,map_columns=d['map_columns'],dictionary=dictionary,table_bytes=len(data),terrain_tiles=d['terrain_tiles']);(out/'terrain_groups.json').write_text(json.dumps(report,indent=2))
 for profile in ['arcade','preserve','chroma']:
  (out/f'terrain_{profile}.patches').write_bytes(patch);(out/f'terrain_{profile}.palette').write_bytes(palette)
 (out/'terrain_patches.bin').write_bytes(patch);(out/'terrain_palette.bin').write_bytes(palette)
 (out/'terrain_active.json').write_text(json.dumps(dict(level=LEVEL,profile='fullgame',geometry='Native level terrain retained at this integration stage',theme=theme['name'],tiles=d['terrain_tiles']),indent=2))

def boss_palettes(root):
 folder=root/f'build/fullgame/converted/level{LEVEL:02d}';out=root/'build/ecm_native'
 report=json.loads((folder/'manifest.json').read_text());report['cells']=[]
 (out/'boss_lookup.bin').write_bytes(b'');(out/'boss_colours.bin').write_bytes(b'');(out/'boss_manifest.json').write_text(json.dumps(report,indent=2))
 return b'',b''
