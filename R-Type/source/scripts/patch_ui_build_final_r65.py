from pathlib import Path
p=Path('scripts/build_ui_r65.py');s=p.read_text().replace("for name in ['boot']+[f'level{n:02d}'for n in range(1,9)]:","for name in [f'level{n:02d}'for n in range(1,9)]:").replace('shim_at=0x1b17 if special else 0x1c8','shim_at=0x1b17').replace("bytes.fromhex('cd c8 01')","bytes.fromhex('cd 17 1b')");p.write_text(s)
