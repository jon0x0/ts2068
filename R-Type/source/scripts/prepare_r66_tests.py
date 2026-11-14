from pathlib import Path
s=Path('scripts/verify_boss_motion_game_r60.mjs').read_text().replace('boss_motion_fixture_r60','boss_motion_fixture_r66').replace("path.join(out,'generic_manifest.json')","path.join(root,'build/fullgame/force_loading_r62/generic_manifest.json')").replace('?239:255','?127:255').replace("process.env.RTYPE_BOSS_LEVELS||'1,2,3,4,5,6,7,8'","'2'")
# Select L2 while the cold loader is active, not through a later title animation.
s=s.replace('m.keyMatrix.fill(31);const t=frame-boot;','m.keyMatrix.fill(31);const t=frame-boot;if(boot<0&&frame>8&&m.ram[0xd610]===1)m.keyMatrix[3]&=~2;')
Path('scripts/probe_l2_boss_r66.mjs').write_text(s)
for a,b in [('verify_pause_r65','verify_pause_r66'),('verify_controls_r65','verify_controls_r66'),('verify_level_jumps_r65','verify_level_jumps_r66'),('verify_preload_title_r65','verify_preload_title_r66')]:
 s=Path('scripts/'+a+'.mjs').read_text().replace('boss_motion_fixture_r65','boss_motion_fixture_r66');Path('scripts/'+b+'.mjs').write_text(s)
