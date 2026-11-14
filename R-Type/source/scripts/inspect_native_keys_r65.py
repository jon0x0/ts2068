from pathlib import Path
p=Path('scripts/inspect_keydef_r65.py');s=p.read_text().replace('[(0xbfc0,0xc081)]','[(0x8b00,0x8b91)]');p.write_text(s)
