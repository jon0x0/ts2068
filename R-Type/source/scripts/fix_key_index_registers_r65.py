from pathlib import Path
p=Path('src/ui_controls_r65.asm');s=p.read_text().replace('        JP NZ,done\n        LD HL,key_return','        JP NZ,done\n        PUSH IX\n        PUSH IY\n        LD HL,key_return').replace('key_return:\n        DI','key_return:\n        DI\n        POP IY\n        POP IX');p.write_text(s)
