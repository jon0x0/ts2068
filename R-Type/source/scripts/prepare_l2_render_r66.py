from pathlib import Path
s=Path('scripts/render_native_fit_r64.py').read_text().replace('native_fit_r64','startup_r66');a=s.index('for p in list');z=s.index(':\n',a);s=s[:a]+"for p in list(O.glob('scene_L2_*.home.bin'))+list(O.glob('boss_level2.home.bin'))"+s[z:];Path('scripts/render_l2_r66.py').write_text(s)
