from pathlib import Path
p=Path('scripts/verify_resident_title_r65.mjs');s=p.read_text().replace('if(phase===2&&frame-mark>500)','if(phase===2&&frame-mark>500&&m.ram[0x5bc2]&&m.dock[3][0x1aa4]>0)');p.write_text(s)
