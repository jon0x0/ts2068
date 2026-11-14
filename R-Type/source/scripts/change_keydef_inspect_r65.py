from pathlib import Path
p=Path('scripts/inspect_keydef_r65.py');s=p.read_text().replace('[(0xbf40,0xbfc0),(0xc210,0xc340)]','[(0xbfc0,0xc081)]');p.write_text(s)
