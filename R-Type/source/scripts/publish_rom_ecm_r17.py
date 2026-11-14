"""Publish only the exact read-only ECM binary covered by CPU/Fuse checks."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/readonly_ecm'
raw=(out/'RType_ECM_ROM_candidate.bin').read_bytes()
sha=hashlib.sha256(raw).hexdigest()
assert len(raw)==65536
cart=(out/'RType_ECM_ROM_candidate.dck').read_bytes()
assert cart==bytes([0]+[2]*8)+raw
for name in ('runtime_validation','sprite_validation','background_validation'):
 r=json.loads((out/(name+'.json')).read_text())
 assert r['bin_sha256']==sha,(name,'stale validation')
 if name=='runtime_validation':assert r['frames']>=8000 and r['romWrites']==0 and r['immutableBanks'] and r['updates']>=100
 else:assert r['passed']
phase=json.loads((ROOT/'build/diagnostics/terrain_motion/validation_1200_rom_r17.json').read_text())
for r in phase['rom_r17']:
 assert not r['mismatches']
 capture=json.loads((out/(r['probe']+'.json')).read_text())
 assert capture['cartridge_sha256']==sha
integration=json.loads((ROOT/'build/diagnostics/terrain_motion/scroll_integration_r17.json').read_text())
assert any(r['target']=='rom' and r['bin_sha256']==sha and r['passed'] and len(r['phases'])==8 for r in integration)
for relative in ('build/art_assets/title_validation.json','build/art_assets/orb_validation.json','build/diagnostics/terrain_art/validation.json'):
 report=json.loads((ROOT/relative).read_text())
 rows=report if isinstance(report,list) else report['results']
 assert any(r['target']=='rom' and r['bin_sha256']==sha and r['passed'] for r in rows),relative
motion=json.loads((ROOT/'build/diagnostics/terrain_motion_r17/trace_extended_detail.json').read_text())
assert any(r['target']=='rom_r17' and r['bin_sha256']==sha and r['frames']>=8000 and r['checked']>400000 and r['bitmap_mismatches']==0 and r['colour_motion_mismatches']==0 for r in motion),'rigid terrain motion'
initial=json.loads((ROOT/'build/diagnostics/initial_terrain_r17/validation.json').read_text())
assert any(r['target']=='rom_r17' and r['bin_sha256']==sha and r['solid']>50 and r['missing']==0 and r['categoryErrors']==0 and r['checked']>30000 and r['bitmap_mismatches']==0 for r in initial),'initial world ownership and full coverage'
for relative in ('build/audio/arcade_sfx_validation_r17.json','build/audio/live_validation.json','build/diagnostics/title_motion_r17/validation.json'):
 report=json.loads((ROOT/relative).read_text());rows=report if isinstance(report,list) else report['results']
 assert any(r['target']=='rom' and r['bin_sha256']==sha and r['passed'] for r in rows),relative
assert json.loads((ROOT/'build/audio/irq_banking_validation.json').read_text())['passed']
assert json.loads((ROOT/'build/diagnostics/r17/background_rows_validation.json').read_text())['passed']
music=json.loads((ROOT/'build/audio/music_validation_r17.json').read_text())
assert any(v['target']=='rom' and v['bin_sha256']==sha and v['frames']>=4611 and v['passed'] for v in music)
effects=json.loads((ROOT/'build/audio/arcade_sfx_validation_r17.json').read_text())
assert effects['passed'] and len([v for v in effects['results'] if v['target']=='rom' and v['bin_sha256']==sha and v['passed']])==21
mix=json.loads((ROOT/'build/audio/mixing_validation_r17.json').read_text())
assert mix['passed'] and mix['death_music_C_maintained'] and mix['death_ticks']==56
assert json.loads((ROOT/'build/audio/unchanged_effects_r17.json').read_text())['passed']
name='RType_level1_ECM_64K_PicoROM_r17'
for ext in ('rom','bin'):(out/(name+'.'+ext)).write_bytes(raw)
(out/(name+'.dck')).write_bytes(cart)
manifest=json.loads((out/'manifest.json').read_text())
manifest.update(status='Emulator-validated read-only level-one ECM cartridge; physical hardware validation pending',published_files=[name+'.rom',name+'.bin',name+'.dck'])
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Published',name,sha)
