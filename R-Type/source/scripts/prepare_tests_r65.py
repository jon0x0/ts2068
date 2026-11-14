from pathlib import Path
p=Path('scripts/verify_title_preload_r64.mjs');s=p.read_text().replace('boss_motion_fixture_r64','boss_motion_fixture_r65');Path('scripts/verify_title_preload_r65.mjs').write_text(s)
