from pathlib import Path
p=Path('scripts/preview_l2_organic_sierra.py');s=p.read_bytes().decode('utf-8',errors='surrogateescape').replace(chr(0xdc96),chr(0x2013));p.write_text(s,encoding='utf-8')
