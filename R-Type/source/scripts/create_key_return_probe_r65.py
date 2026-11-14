from pathlib import Path
s=Path('scripts/verify_key_definition_r65.mjs').read_text().replace('const log=[],keys=','const pcs={},log=[],keys=').replace('if(a===0xbfe9','if(finished===3)pcs[a]=(pcs[a]||0)+1;if(a===0xbfe9').replace('mode:m.dock','sp:m.cpu.sp,pcs:Object.entries(pcs).sort((a,b)=>b[1]-a[1]).slice(0,15),mode:m.dock');Path('scripts/probe_key_return_r65.mjs').write_text(s)
