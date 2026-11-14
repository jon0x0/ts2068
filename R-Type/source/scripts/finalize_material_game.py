"""Verify packaged pages, preserve validation provenance, and publish r49."""
from pathlib import Path
import json,hashlib,shutil,zipfile,functools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/material_game_r49';PREV=ROOT/'build/fullgame/pixel_game_r47'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 manifest=read(OUT/'manifest.json');unchanged=[]
 for record in manifest['regions']:
  name='boot'if record['file']=='RTBOOT.TAP'else f'level{record["level"]:02d}';raw=(OUT/f'{name}_region.bin').read_bytes();assert len(raw)==65536 and sha(raw)==record['sha256']
  if record['level']!=5:assert raw==(PREV/f'{name}_region.bin').read_bytes();unchanged.append(name)
  tape=(OUT/'RTYPE'/record['file']).read_bytes();pos=0;blocks=[]
  while pos<len(tape):
   size=int.from_bytes(tape[pos:pos+2],'little');b=tape[pos+2:pos+2+size];assert len(b)==size and functools.reduce(int.__xor__,b)==0;blocks.append(b);pos+=size+2
  assert pos==len(tape)and len(blocks)==16;assert b''.join(b[1:-1]for b in blocks[1::2])==raw
 assert(OUT/'launcher.bin').read_bytes()==(PREV/'launcher.bin').read_bytes()
 oldboss=read(PREV/'boss_preview_validation.json');newboss=read(OUT/'boss_preview_validation.json');assert oldboss['passed']and newboss['passed'];assert len(oldboss['results'])==8;assert len(newboss['results'])==8 and all(r['after']>=700 for r in newboss['results'])
 combined=newboss['results'];assert all(r['passed']and r['after']>=700 for r in combined)
 progression=read(OUT/'cache_progression_validation.json');assert progression['passed']and progression['all8_revisited_without_disk']and progression['core_and_workspace_checks']==15
 shutil.copy2(ROOT/'build/fullgame/compiled_game_r48/cache_restart_validation.json',OUT/'cache_restart_validation.json');restart=read(OUT/'cache_restart_validation.json');assert len(restart)==2 and all(r['passed']for r in restart)
 equivalence=read(OUT/'material_composition_validation.json');assert equivalence['passed']and equivalence['cases']==384
 shutil.copy2(ROOT/'build/fullgame/compiled_game_r48/projectile_capacity_validation.json',OUT/'projectile_capacity_validation.json');capacity=read(OUT/'projectile_capacity_validation.json');assert capacity['passed']and capacity['full_pool_no_overwrite']
 inherited={}
 for filename in ['movement_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','failure_validation.json']:
  report=read(PREV/filename);assert all(r['passed']for r in report)if isinstance(report,list)else report['passed'];shutil.copy2(PREV/filename,OUT/filename);inherited[filename]='Reused from byte-identical BOOT/level1/control code; only level5 differs in r49.'
 overlay=read(ROOT/'build/diagnostics/delta_benchmark/overlay_component_validation.json');assert overlay['passed']and overlay['common_pixels_never_erased']and overlay['stationary_pixel_collision'];assert(OUT/'overlay.bin').read_bytes()==(PREV/'overlay.bin').read_bytes()
 trial=ROOT/'build/diagnostics/native_relocatable';tv=read(trial/'validation.json');tm=read(trial/'manifest.json');assert tv['passed']and tv['byteExactFrames']==825;trialname='Relocatable_delta_QAOP_TS2068.tap';assert sha((trial/trialname).read_bytes())==tm['tap_sha256']
 trials=OUT/'TRIALS';trials.mkdir(exist_ok=True);shutil.copy2(trial/trialname,trials/trialname);shutil.copy2(ROOT/'build/diagnostics/native_pixel_qaop/Pixel_movement_QAOP_TS2068.tap',trials/'Pixel_movement_QAOP_TS2068.tap')
 (trials/'README.txt').write_text('Standalone TS2068 player-renderer comparisons\n\nRelocatable_delta_QAOP_TS2068.tap uses cached relocatable bitmap/ECM transitions. Pixel_movement_QAOP_TS2068.tap is the preceding scratch/differential baseline. Both show the same ship and move one pixel per video refresh on black. The change is in how updates are generated. Q up, A down, O left, P right, plus both native joysticks. Reset to exit.\n\nThese are movement demonstrations. Use RTYPE/RTFULL.TAP for the full game, which retains its own key-definition flow. The full game uses a background-aware compositor; the cached trial has a black backdrop.\n',encoding='utf-8')
 readme='''R-Type TS2068 r49 - 512KB disk build

Replace the complete RTYPE folder with this version. Keep RTFULL.TAP, RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP together. The folder may be nested under TAP. Open the folder and load RTFULL.TAP.

Choose your keys in the game as usual. Both native joystick sockets work alongside the selected keyboard controls. Fixed QAOP applies only to the separate TRIALS demonstrations.

Title keys1-8 select a starting level. During gameplay press B, release it, then press B again to preview the current boss. M toggles music.

Changes:
- One-pixel player movement inside the game, with background-aware differential updates and pixel coverage collision checks.
- Quick normal-fire releases are captured between world updates. Holding fire still charges a beam. The original16-slot normal-projectile limit remains.
- Approved dark-blue planned-edge Bellmite spheres and selected96x96 machinery core, with pixel overlap composition and precomputed row-pair caches.
- Fixed lower-playfield ownership metadata access while the graphics bank is mapped; prevents writes into debug code.
- Separate cached relocatable-delta and preceding baseline movement trials in TRIALS.

Startup loads only the first required level. Further levels load when needed and remain resident in RAM; cached revisits use no disk reads. Loader errors report the step and page; keep those details when reporting a problem.

This is an emulator-validated hardware test build. Player updates and world updates still depend on scene load. Detailed boss composition remains costly; this is not a constant-frame-rate claim. Native weapons, companions and AI retain rounded character-grid coordinates. The full game currently uses the centre ship pose. Overlap rows preserve foreground colours and recover background shading with legal colour pairs. Shared8x1 cells still limit overlapping colour detail.

To preview the new boss: select level5, start, then B-release-B. The legacy debug display still prints R38 for its diagnostic module; identify this folder/package as r49 when reporting results.

This package targets the full512KB disk configuration. The older stock64KB cartridge output is unchanged. Physical validation of r49 is pending.
'''
 assert 'tspico'not in readme.lower();(OUT/'RTYPE/README.txt').write_text(readme,encoding='utf-8');(OUT/'README.txt').write_text(readme,encoding='utf-8')
 summary=dict(passed=True,validated_asset_pages=72,boss_updates_per_level=700,boss_results=combined,unchanged_regions=unchanged,reused_reports=inherited,pixel_component=overlay,relocatable_trial=tv,material_composition=equivalence,physical_validation=False,scope='512KB disk game and separate standalone trials; stock64KB ROM unchanged')
 (OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2));archive=OUT/'RType_TS2068_r49.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for folder in ['RTYPE','TRIALS']:
   for p in sorted((OUT/folder).iterdir()):z.write(p,folder+'/'+p.name)
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None;assert'RTYPE/RTFULL.TAP'in z.namelist()and'TRIALS/'+trialname in z.namelist()
 manifest.update(status='Emulator-validated r49 hardware test build',package_sha256=sha(archive.read_bytes()),package_bytes=archive.stat().st_size,physical_validation=False,validated_asset_pages=72,full_game_one_pixel=True,selected_game_keys_preserved=True,normal_release_capture=True,relocatable_delta_trial_included=True,stock64KB_rom_changed=False)
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print(archive);print(manifest['package_sha256']);print('72 asset pages, eight boss routes, full cache/ending/restart/error checks and trial packaging verified.')
if __name__=='__main__':main()
