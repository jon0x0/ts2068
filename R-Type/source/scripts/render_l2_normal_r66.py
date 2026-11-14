from pathlib import Path
p=Path('scripts/render_l2_r66.py');s=p.read_text().replace("list(O.glob('boss_level2.home.bin'))","list(O.glob('boss_level2.home.bin'))+list(O.glob('ordinary_L2_col*.home.bin'))");p.write_text(s)
