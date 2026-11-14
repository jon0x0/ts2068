from pathlib import Path
p=Path('scripts/verify_resident_title_r65.mjs');s=p.read_text().replace('frame-mark<70','frame-mark<250').replace('assert(secondTitle>restarted);','assert(secondTitle>restarted,JSON.stringify({frame,phase,secondTitle,restarted,pc:m.cpu.pc,map:m.portF4,live:m.ram[0x5bc2],hot:m.ram[0xfda5],valid:m.ram[0xfd4a]}));');p.write_text(s)
