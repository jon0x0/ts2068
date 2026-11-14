from pathlib import Path
p=Path('src/responsive_startup_r66.asm');s=p.read_text().replace('        OUT ($F4),A\n        JP $8634\ncold_unpack:', '        OUT ($F4),A\n        LD HL,$8634\n        PUSH HL\n        JP $00DB\ncold_unpack:');p.write_text(s)
p=Path('scripts/boss_motion_fixture_r65.mjs');s=p.read_text().replace('hardware_fire_r65','startup_r66');Path('scripts/boss_motion_fixture_r66.mjs').write_text(s)
