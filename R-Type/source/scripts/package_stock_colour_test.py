"""Export scoped cartridge color-refresh tests; never update stable/latest."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];W=R/'build/cartridges/integration_work';O=R/'build/cartridges/r153_colour_fix_test';O.mkdir(exist_ok=True)
levels=[]
for n in range(1,9):
 d=W/f'level{n:02d}';evidence={}
 for name in ['global_colour_validation.json','actor_ownership_validation.json','stock_retained_player_components.json','moving_player_validation.json','scroll_validation.json','repeated_fire_validation.json','stock_vector_validation.json','visible_collision_validation.json']:
  q=json.loads((d/name).read_text());assert q['passed'];evidence[name]=hashlib.sha256((d/name).read_bytes()).hexdigest()
 b=(d/f'L{n}_shared_cache_internal.rom').read_bytes();assert len(b)==65536
 for ext in ['rom','bin']:(O/f'rt_l{n}_r153_test.{ext}').write_bytes(b)
 (O/f'rt_l{n}_r153_test.dck').write_bytes(bytes([0]+[2]*8)+b)
 levels.append(dict(level=n,rom_sha256=hashlib.sha256(b).hexdigest(),evidence=evidence))
d=W/'level04';old=json.loads((d/'live_colour_baseline.json').read_text());new=json.loads((d/'live_colour_validation.json').read_text());assert len(old['blocks'])==7 and new['passed'] and not new['blocks']
for name in ['boss_runtime_validation.json','controls_validation.json','score_validation.json','title_validation.json','game_over_validation.json']:assert json.loads((d/name).read_text())['passed']
for name in ['l4_colour_before_after.png','colour_fixed.screen.png','boss_runtime.screen.png']:shutil.copy2(d/name,O/name)
(O/'test_manifest.json').write_text(json.dumps(dict(status='Scoped color-refresh test, not a full release',levels=levels,l4_old_spurious_blocks=7,l4_new_spurious_blocks=0,l4_boss_stress_updates=240,hardware_confirmed=False),indent=2))
(O/'README.txt').write_text('r153 color refresh test cartridges (all8 individually64KBread-only). For L4 use rt_l4_r153_test.rom or .bin; .dck is ROM-only emulator format. Fixes compact dictionary IDs being treated as raw color attributes by native global/adjacent-cell refresh. Current artwork unchanged, not replaced or reduced. Uses normal-black legacy attributes. All8 shared art/colour/scroll/player/fire/IRQ/damage regressions pass. Actual L4 menu-start: oldr1517spurious solid cells, new0. L4boss240update stress passes with documented player/death protection; no boss victory claim. L4title/score/gameover/controls pass. Emulator diagnostics included. Hardware confirmation and other remaining reports pending. This is not a full release or latest promotion; stable TAP and old archives unchanged.\n')
z=O/'RType_64K_colour_fix_tests_r153.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED)as archive:
 for file in sorted(O.iterdir()):
  if file.is_file()and file!=z:archive.write(file,file.name)
with zipfile.ZipFile(z)as archive:assert archive.testzip()is None
print(O/'rt_l4_r153_test.rom')
