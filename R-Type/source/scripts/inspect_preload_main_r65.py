from pathlib import Path
p=Path('scripts/verify_preload_title_r65.mjs');s=p.read_text().replace('passed:true,level:n','passed:true,main_call:Array.from(m.ram.slice(0x8656,0x8659)),low_shim:Array.from(m.dock[0].slice(0x1b17,0x1b20)),level:n');p.write_text(s)
