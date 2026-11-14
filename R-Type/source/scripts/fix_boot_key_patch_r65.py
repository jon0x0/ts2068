from pathlib import Path
p=Path('scripts/build_ui_r65.py');s=p.read_text().replace("for name in ['boot']+[f'level{n:02d}'for n in range(1,9)]:", "for name in ['boot']:",1);p.write_text(s)
