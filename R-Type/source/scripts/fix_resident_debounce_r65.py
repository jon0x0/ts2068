from pathlib import Path
p=Path('src/ui_controls_r65.asm');s=p.read_text().replace('        LD A,($FDA5)\n        CP 3\n        JR Z,check_pause','        LD A,($7AA4)\n        OR A\n        JR Z,check_pause').replace('        LD A,($5BC2)','        LD A,($7AA4)');p.write_text(s)
