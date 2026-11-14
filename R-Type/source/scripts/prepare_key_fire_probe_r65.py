from pathlib import Path
s=Path('scripts/verify_key_definition_r65.mjs').read_text().replace('if(a===0xbfe9', 'if(finished===3&&m.keyMatrix[7]===30&&(a===0x1a6d||a===0xc014))console.log("SPACE",frame,a,m.cpu.a,m.dock[3][0x14fa]);if(a===0xbfe9');Path('scripts/probe_key_fire_r65.mjs').write_text(s)
