from pathlib import Path
p=Path('scripts/verify_key_definition_r65.mjs');s=p.read_text().replace('mode:m.dock','ff:m.portFF,iff1:m.cpu.iff1,iff2:m.cpu.iff2,frameCounter:m.dock[3][0x1a8a],mode:m.dock');p.write_text(s)
