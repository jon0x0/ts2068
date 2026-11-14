from pathlib import Path
p=Path('scripts/verify_key_definition_r65.mjs');s=p.read_text().replace('live,x0,x1,pc:m.cpu.pc','live,x0,x1,pc:m.cpu.pc,mode:m.dock[3][0x14fb],keyfn:Array.from(m.dock[3].slice(0x14fc,0x14fe)),bindings:Array.from(m.dock[3].slice(0x1780,0x178c)),state:m.dock[3][0x1aa4]');p.write_text(s)
