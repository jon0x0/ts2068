from pathlib import Path
p=Path('scripts/inspect_keydef_r65.py');s=p.read_text().replace('[(0x8b00,0x8b91)]','[(0x87d0,0x8895)]');p.write_text(s)
