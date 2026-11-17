"""Build/check/package all eight stock64KB cartridges. Stable r100 entry stays separate."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile,shutil
from check_stock_cartridge_release import check
R=Path(__file__).resolve().parents[1];W=R/'build/cartridges/integration_work'
p=argparse.ArgumentParser();p.add_argument('--validated',action='store_true',help='Use fresh hash-bound validation instead of rebuilding');p.add_argument('--version',default='r160',help='New stock release identifier; existing releases are protected');args=p.parse_args()
assert args.version.startswith('r') and args.version[1:].isdigit(), 'Use r followed by digits'
version=args.version
assert int(version[1:])>=157, 'Archived releases must not be overwritten'
O=R/'build/cartridges'/version
assert not O.exists(), 'Release folder already exists; use a new version'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not args.validated:subprocess.run([sys.executable,'scripts/validate_stock_integration.py'],cwd=R,check=True)
if not args.validated:subprocess.run([sys.executable,'scripts/refresh_stock_paired.py'],cwd=R,check=True)
subprocess.run([sys.executable,'scripts/summarize_current_stock_integration.py'],cwd=R,check=True)
subprocess.run([sys.executable,'scripts/verify_stock_release_contracts.py'],cwd=R,check=True)
comparison=json.loads((W/'current_integration_report.json').read_text());assert comparison['stock_component_package_ready']
accept=json.loads((W/'release_acceptance.json').read_text());assert accept['passed']and len(accept['levels'])==8
O.mkdir(parents=True,exist_ok=True);matrix=json.loads((W/'integration_status.json').read_text());manifest={'release':version,'target':'Eight individual stock TS2068 64KB read-only ECM cartridges','baseline':'r145 selected artwork/audio and current player/projectile adapters','physical_hardware_tested':False,'tap_cycle_pixel_equivalence':False,'l4_boss_motion':'exact fractional artwork and 2-pixel movement; immutable adjacent-row codec','paired_scenarios':16,'levels':[],'scope':'Native per-level gameplay and boss event scripts with stock HOME compressed-cache renderer; expanded-RAM bank caches and multi-level switching are separate.'}
for n in range(1,9):
 d=W/f'level{n:02d}';a=json.loads((d/'release_acceptance.json').read_text());assert a['passed'];assert a['rom_sha256']==sha(d/f'L{n}_shared_cache_internal.rom')
 dest=O/f'level{n}';dest.mkdir(exist_ok=True);b=(d/f'L{n}_shared_cache_internal.rom').read_bytes()
 for ext,data in [('rom',b),('bin',b),('dck',bytes([0]+[2]*8)+b)]:
  out=dest/f'rt_l{n}_{version}.{ext}';out.write_bytes(data);matrix['levels'][n-1][ext]={'path':out.relative_to(R).as_posix(),'sha256':sha(out)}
 evidence=dest/'acceptance.json';evidence.write_text(json.dumps(a,indent=2));proof={'path':evidence.relative_to(R).as_posix(),'sha256':sha(evidence)}
 for key in matrix['levels'][n-1]['requirements']:
  matrix['levels'][n-1]['requirements'][key]={'passed':True,'evidence':proof,'scope':'Stock single-level software acceptance; see acceptance.json for exact checks and hardware/coverage limits'}
 matrix['levels'][n-1]['status']='software_validated_stock_cartridge'
 manifest['levels'].append({'level':n,'bytes':len(b),'rom':matrix['levels'][n-1]['rom'],'bin':matrix['levels'][n-1]['bin'],'dck':matrix['levels'][n-1]['dck'],'graphics_frames':a['frames'],'palette_rows':a['palette_rows'],'frame_cache_bytes':a['frame_cache_bytes'],'native_frame_bytes':a['unique_frame_native_bytes'],'palette_bytes':a['palette_bytes']})
 for name in ['continuous_restart_validation.json','cleared_restore_validation.json','natural_clear_validation.json','normal_black_validation.json','normal_black_restore_contract.json','current_validation_summary.json','actor_draw_guard_validation.json','repeated_fire_validation.json','death_respawn_validation.json','l4_victory_validation.json','l4_recovery_validation.json','game_over_validation.json','stock_vector_validation.json','boss_runtime_validation.json','shared_cache_gameplay_validation.json','tap_motion_validation.json','compact_snapshot_validation.json','l4_procedural_validation.json','l4_constructor_irq_validation.json','l4_bank_windows_validation.json','rom_font_validation.json','launcher_layers_validation.json','launcher_actor_guard_validation.json','launcher_layer_contract.json','l4_stable_tokens.json','player_ram_layout.json']:
  if (d/name).exists():shutil.copy2(d/name,dest/name)
 if (d/'boss_runtime.screen.png').exists():shutil.copy2(d/'boss_runtime.screen.png',dest/'boss_snapshot.png')
shutil.copy2(W/'current_integration_report.json',O/'comparison_report.json')
shutil.copy2(W/'current_paired_completed.png',O/'comparison.png')
detail=W/f'l4_{version}_completed100.png'
if detail.exists():shutil.copy2(detail,O/'l4_completed100.png')
launcher_detail=R/f'build/launcher_review_{version}/launcher_before_after.png'
if launcher_detail.exists():shutil.copy2(launcher_detail,O/'launcher_comparison.png')
readme='''R-TYPE TS2068 - individual64KB ECM cartridges - RELEASE_VERSION

Each level is a separate true read-only64KB cartridge for a stock TS2068.
Use rt_lN_RELEASE_VERSION.bin or the identical .rom for PicoROM: exactly65536raw bytes,
DOCK banks0 through7 in ascending8KB order, without a header.
The .dck is for emulation:9byte header plus the same ROM, all8banks marked ROM.
Do not program the DCK header into a cartridge. No writable cartridge RAM is used.

Start with keyboard or native joystick fire; both joystick sockets remain active
alongside the selected keyboard controls. ENTER defines the six gameplay keys.
P pauses (Shift-P if P is one of the selected keys); M toggles music.
Press B, release, then B to preview the boss. Collect the offered weapon pickups;
they are not granted automatically. L4 offers replacements after equipment loss.
On completion, fire replays this cartridge; reset with another cartridge to change
levels. This target does not use a disk loader or load-all/level-jump commands.

Includes restored current r145 actor captures across all levels, corrected L2
painted-body/row-colour paths, L5 overlap composition and per-level AY tracks/effects,
fine player movement, independently clocked shots, title delta animation,
animated score colours, pause, native input and normal black in ECM space.
Release r161 also fixes native title clears/delta edges, both score entry paths,
and flat legacy restoration. Bright black remains valid; black-paper pairs use
normal black. Bright pairs with two nonblack colours are preserved.
No emulator palette flattening is required.
Release r162 additionally prevents cleared cells from resurrecting stale sprite
paper beside the moving/firing player; native owned shading stays unchanged.
Artwork expands from compressed ROM into a bounded HOME cache when needed.
All seven moving-boss ports L2/L3/L4/L5/L6/L7/L8 include fractional artwork
and two-pixel movement. L1 is static. L4 uses permanent adjacent-row colour
recipes, a bounded expanded-row cache and ROM-backed native font readers.
L4 twin-launcher poses now render in front of their dropped orbs; terrain and
other actors retain native occlusion, and projectile records are unchanged.
Event scripts are preserved. Elapsed world-update cadence differs from the TAP
version; the two editions are not cycle- or pixel-identical in live play.

Validation: all8 cold starts/firing; native direct/retained art comparisons;
8fine-scroll phases with pixel/colour checks; title, input, pause, music toggle;
actual deaths/respawns and five-life game-over-to-score flow; completion/replay;
all256computed IRQ targets per level and zero game writes to ROM.
Boss stress uses player invulnerability and does not prove every boss defeated.
Sixteen paired TAP/cartridge actor/event/control scenarios pass. The L7 paired
comparison has a shared coarse-death bypass and is not natural-survival proof.
L4 has a separate actual48-hit victory and two equipment-recovery tests.
Qualifying score and player-hit flags are seeded only in test fixtures.
IRQ probes explicitly inject computed targets in a fixed-FF emulator.
Physical PicoROM/PicoVideo hardware testing remains pending. Not all boss fights
or name-entry interactions were played through. See each acceptance.json.

The existing expanded-RAM r145 build and hardware-confirmed r99/r100 archives
are unchanged. This is the separate stock cartridge release, not a replacement
for the stable disk-release pointer. Create a new archive without overwriting this one:
python scripts/release_stock_cartridges.py --version NEXT_VERSION
'''
if int(version[1:])>=163:readme+='\nPost-game-over replay returns directly to this resident cartridge level, without the Spectrum side2 rewind prompt. All eight native restart paths are checked through title and fire to gameplay.\n'
readme=readme.replace('RELEASE_VERSION',version).replace('NEXT_VERSION','r'+str(int(version[1:])+1))
(O/'README.txt').write_text(readme,encoding='utf-8');(O/'manifest.json').write_text(json.dumps(manifest,indent=2));(O/'integration_status.json').write_text(json.dumps(matrix,indent=2))
errors=check(O/'integration_status.json');assert not errors,errors
checks=''.join(f'{sha(f)}  {f.relative_to(O).as_posix()}\n'for f in sorted(O.rglob('*'))if f.is_file()and f.name not in ['SHA256SUMS.txt','archive_sha256.txt',f'RType_TS2068_64K_cartridges_{version}.zip'])
(O/'SHA256SUMS.txt').write_text(checks)
archive=O/f'RType_TS2068_64K_cartridges_{version}.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,9)as z:
 for f in sorted(O.rglob('*')):
  if f.is_file()and f!=archive and f.name!='archive_sha256.txt':z.write(f,f.relative_to(O).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for n in range(1,9):
  b=z.read(f'level{n}/rt_l{n}_{version}.rom');assert len(b)==65536 and b==z.read(f'level{n}/rt_l{n}_{version}.bin')and z.read(f'level{n}/rt_l{n}_{version}.dck')==bytes([0]+[2]*8)+b
(W/'integration_status.json').write_text(json.dumps(matrix,indent=2))
(O/'archive_sha256.txt').write_text(sha(archive)+'  '+archive.name+'\n')
print('PASS all8 release gate, ZIP CRC, raw ROM/BIN identity, read-only DCK headers')
print(archive);print('SHA256',sha(archive))
