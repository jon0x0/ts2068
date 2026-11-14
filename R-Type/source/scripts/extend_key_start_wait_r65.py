from pathlib import Path
p=Path('scripts/verify_key_definition_r65.mjs');s=p.read_text().replace('live,x0,x1,pc:m.cpu.pc','finished,accepted,live,x0,x1,pc:m.cpu.pc');s=s.replace('t<1400','t<4000').replace('t<350','t<1300');p.write_text(s)
