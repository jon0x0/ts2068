from pathlib import Path
p=Path('src/ui_controls_r65.asm');s=p.read_text(encoding='utf-8-sig');s=s.replace('        LD HL,$7C80\n        LD DE,$486D', '        LD HL,$7CE0\n        CALL mute\n        LD HL,$7C80\n        LD DE,$486D',1);s=s.replace('        LD A,UI_MAP\n        OUT ($F4),A','        LD HL,$7CE0\n        CALL volume\n        LD A,UI_MAP\n        OUT ($F4),A',1)
s=s.replace('title:\n','mute:\n        LD D,3\n        LD E,8\n        LD BC,$FFF5\nvol_save:\n        LD A,E\n        OUT (C),A\n        INC C\n        IN A,(C)\n        LD (HL),A\n        XOR A\n        OUT (C),A\n        INC HL\n        DEC C\n        INC E\n        DEC D\n        JR NZ,vol_save\n        RET\nvolume:\n        LD D,3\n        LD E,8\n        LD BC,$FFF5\nvol_restore:\n        LD A,E\n        OUT (C),A\n        INC C\n        LD A,(HL)\n        OUT (C),A\n        INC HL\n        DEC C\n        INC E\n        DEC D\n        JR NZ,vol_restore\n        RET\ntitle:\n');p.write_text(s)
s=Path('src/preload_restore_r61.asm').read_text();a=s.index('        LD HL,$FDC0');b=s.index('restore_error:',a);s=s[:a]+'''        LD A,($FD49)
        CP 4
        LD A,$0B
        LD HL,$3E43
        JR NZ,bridge_target
        LD A,$19
        LD HL,$9EA3
bridge_target:
        LD ($5E01),A
        LD ($5E05),HL
        LD A,$3E
        LD ($5E00),A
        LD HL,$F4D3
        LD ($5E02),HL
        LD A,$C3
        LD ($5E04),A
        JP $5E00
'''+s[b:];Path('src/preload_restore_r65.asm').write_text(s)
p=Path('src/level_hotkeys_r64.asm');s=p.read_text().replace('        CP $FF\n        JP Z,hot_done','        CP $FF\n        JP Z,$01D0');Path('src/level_hotkeys_r65.asm').write_text(s)
