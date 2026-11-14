from pathlib import Path
p=Path('src/ui_controls_r65.asm');s=p.read_text();s=s.replace('        LD BC,$DFFE\n        IN A,(C)\n        AND 1\n        JP NZ,done', '''        LD A,($FD4A)
        CP $FF
        JR NZ,check_pause
        LD A,($FDA5)
        CP 3
        JR Z,check_pause
        LD BC,$BFFE
        IN A,(C)
        AND 2
        JR NZ,check_pause
        LD BC,$FEFE
        IN A,(C)
        AND 1
        JP Z,title
check_pause:
        LD BC,$DFFE
        IN A,(C)
        AND 1
        JP NZ,done''',1);p.write_text(s)
