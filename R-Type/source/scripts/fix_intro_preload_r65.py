from pathlib import Path
p=Path('src/ui_controls_r65.asm');s=p.read_text();s=s.replace('        LD A,($5BC2)\n        OR A\n        JP Z,done\n','',1).replace('check_pause:\n','check_pause:\n        LD A,($5BC2)\n        OR A\n        JP Z,done\n',1);p.write_text(s)
