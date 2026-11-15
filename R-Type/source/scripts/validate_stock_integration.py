"""Rebuild and verify internal stock integration. Never package or publish."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,os
from stock_tap_motion_config import enabled as tap_motion_enabled, composition_enabled, compact_snapshot_enabled, procedural_enabled
R=Path(__file__).resolve().parents[1]
O=R/'build/cartridges/integration_work'
NODE=Path('C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
levels=[int(v)for v in sys.argv[1:]]or list(range(1,9))
reports=[]
for n in levels:
 folder=O/f'level{n:02d}';start=time.monotonic()
 commands=[[sys.executable,'scripts/'+s,str(n)]for s in ['plan_stock_player_ram.py','prepare_stock_terrain.py','build_stock_level_base.py','compile_stock_engines.py','build_stock_shared_cache.py']]
 commands += [[str(NODE),'scripts/'+s,str(n)]+(['--pause']if s=='verify_stock_death_respawn.mjs'else[])for s in ['verify_stock_normal_black.mjs','verify_stock_actor_draw_guard.mjs','verify_stock_world_reset.mjs','verify_stock_global_colours.mjs','verify_stock_moving_player.mjs','verify_stock_irq_schedule.mjs','verify_stock_repeated_fire.mjs','verify_stock_engine_components.mjs','verify_stock_retained_player.mjs','verify_stock_shared_cache.mjs','verify_stock_actor_ownership.mjs','verify_stock_visible_collision.mjs','verify_stock_terrain.mjs','verify_stock_scroll.mjs','verify_stock_scores.mjs','verify_stock_death_respawn.mjs','verify_stock_game_over.mjs','verify_stock_title.mjs','verify_stock_controls.mjs','verify_stock_live_boss_key.mjs','verify_stock_completion.mjs','verify_stock_vectors.mjs','verify_stock_shared_gameplay.mjs']]
 if tap_motion_enabled(n):commands.append([str(NODE),'scripts/verify_stock_tap_motion.mjs',str(n)])
 if compact_snapshot_enabled(n)and tap_motion_enabled(n):commands.append([str(NODE),'scripts/verify_stock_compact_snapshot.mjs',str(n)])
 if composition_enabled(n):
  commands.append([str(NODE),'scripts/verify_stock_dynamic_palette.mjs'])
  commands.append([str(NODE),'scripts/verify_stock_overlap.mjs'])
 if procedural_enabled(n):commands.extend([[str(NODE),'scripts/'+name]for name in ['verify_stock_l4_procedural.mjs','verify_stock_l4_rom_font.mjs','verify_stock_l4_constructor_irq.mjs','verify_stock_l4_bank_windows.mjs']])
 if n==4:
  commands.extend([[str(NODE),'scripts/verify_stock_l4_launcher_layers.mjs'],[str(NODE),'scripts/verify_stock_actor_draw_guard.mjs','4','--launcher']])
  commands.extend([[str(NODE),'scripts/probe_stock_l4_orbs.mjs',str(folder/'L4_shared_cache_internal.dck')],[str(NODE),'scripts/verify_stock_l4_orb_erase.mjs']])
 if n==1:
  commands.append([str(NODE),'scripts/verify_player_clear_r162.mjs'])
  commands.append([str(NODE),'scripts/verify_player_natural_r162.mjs'])
  commands.extend([[str(NODE),'scripts/verify_stock_l1_walker_cells.mjs'],[str(NODE),'scripts/verify_stock_l1_walker_pilot.mjs'],[str(NODE),'scripts/verify_stock_l1_walker_pilot.mjs','--charged']])
 if n==2:
  commands.append([str(NODE),'scripts/verify_stock_l2_body.mjs'])
  commands.append([str(NODE),'scripts/verify_stock_l2_row_palette.mjs'])
 if n==4:
  commands.append([str(NODE),'scripts/verify_stock_live_colours.mjs','4'])
  commands.append([str(NODE),'scripts/verify_stock_l4_victory.mjs'])
  commands.append([str(NODE),'scripts/verify_stock_l4_recovery.mjs'])
 commands.append([str(NODE),'scripts/verify_stock_boss_runtime.mjs',str(n)])
 with (folder/'current_validation.log').open('w')as log:
  for command in commands:
   result=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
   if result.returncode:
    print('FAILED',n,command,flush=True);sys.exit(result.returncode)
 artifacts=['normal_black_validation.json','actor_draw_guard_validation.json','world_reset_validation.json','global_colour_validation.json','moving_player_validation.json','irq_schedule_validation.json','repeated_fire_validation.json','stock_engine_components.json','stock_retained_player_components.json','shared_cache_validation.json','actor_ownership_validation.json','visible_collision_validation.json','terrain_validation.json','scroll_validation.json','score_validation.json','death_respawn_validation.json','game_over_validation.json','title_validation.json','controls_validation.json','live_boss_key_validation.json','completion_validation.json','stock_vector_validation.json','shared_cache_gameplay_validation.json']
 if procedural_enabled(n):artifacts.extend(['l4_procedural_validation.json','rom_font_validation.json','l4_constructor_irq_validation.json','l4_bank_windows_validation.json'])
 artifacts.append('boss_runtime_validation.json')
 if composition_enabled(n):artifacts.extend(['dynamic_palette_validation.json','overlap_validation.json'])
 if tap_motion_enabled(n):artifacts.append('tap_motion_validation.json')
 if compact_snapshot_enabled(n)and tap_motion_enabled(n):artifacts.append('compact_snapshot_validation.json')
 if n==1:artifacts.extend(['cleared_restore_validation.json','natural_clear_validation.json','walker_live_cells_validation.json','walker_live_pilot.json','walker_charged_pilot.json'])
 if n==2:artifacts.extend(['l2_body_validation.json','l2_row_palette_validation.json'])
 if n==4:artifacts.extend(['launcher_layers_validation.json','launcher_actor_guard_validation.json','orb_erase_validation.json','live_colour_validation.json','l4_victory_validation.json','l4_recovery_validation.json'])
 assert all(json.loads((folder/a).read_text())['passed']for a in artifacts)
 record=dict(level=n,passed=True,seconds=round(time.monotonic()-start,2),rom_sha256=sha(folder/f'L{n}_shared_cache_internal.rom'),evidence={a:sha(folder/a)for a in artifacts},scope='Current actor/common cache, player and independent projectile lifecycle component suite; package acceptance additionally requires source/data/RAM/audio contracts and hash-bound TAP comparisons; not hardware or all-boss survival certification')
 (folder/'current_validation_summary.json').write_text(json.dumps(record,indent=2));reports.append(record)
 print('PASS internal L'+str(n),record['seconds'],'seconds',flush=True)
(O/'current_component_run.json').write_text(json.dumps(dict(passed=True,levels=reports,publish_ready=False),indent=2))
