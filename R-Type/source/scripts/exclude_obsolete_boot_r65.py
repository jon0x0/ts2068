from pathlib import Path
p=Path('scripts/finalize_ui_r65.py');s=p.read_text().replace("if p.is_file():z.write(p,'rtype/'+p.name)","if p.is_file() and p.name!='RTBOOT.TAP':z.write(p,'rtype/'+p.name)");p.write_text(s)
