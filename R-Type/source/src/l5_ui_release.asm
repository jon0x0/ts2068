UI_ORIGIN EQU $9EA0
FONT_ORIGIN EQU $8B70
UI_MAP EQU $19
KEY_ORIGIN EQU $8B30
; UI lives in reserved bank-specific padding. No graphics/AI allocation changes.
        ORG UI_ORIGIN
        JP poll
        JP title
poll:
        PUSH BC
        PUSH DE
        PUSH HL
        LD A,($FD4A)
        CP $FF
        JR NZ,check_pause
        LD A,($7AA4)
        OR A
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
        LD A,($7AA4)
        OR A
        JP Z,title_keys
        LD BC,$DFFE
        IN A,(C)
        AND 1
        JP NZ,done
        ; P remains a defined gameplay key. Shift-P pauses in that case.
        LD HL,$7780
        LD B,6
bindings:
        LD A,(HL)
        INC HL
        CP $DF
        JR NZ,next
        LD A,(HL)
        CP 1
        JR NZ,next
        LD BC,$FEFE
        IN A,(C)
        AND 1
        JP NZ,done
        JR pause
next:   INC HL
        DJNZ bindings
pause:
        DI
        LD A,UI_MAP-8
        OUT ($F4),A
        LD HL,$7CE0
        CALL mute
        LD HL,$7C80
        LD DE,$486D
        LD B,8
save_row:
        LD C,6
save_cell:
        LD A,(DE)
        LD (HL),A
        INC HL
        SET 5,D
        LD A,(DE)
        LD (HL),A
        INC HL
        LD A,7
        LD (DE),A
        RES 5,D
        INC E
        DEC C
        JR NZ,save_cell
        LD A,E
        SUB 6
        LD E,A
        INC D
        DJNZ save_row
        LD HL,ui_font
        LD DE,$486D
        LD B,8
paint_row:
        LD C,6
paint_cell:
        LD A,(HL)
        INC HL
        LD (DE),A
        INC E
        DEC C
        JR NZ,paint_cell
        LD A,E
        SUB 6
        LD E,A
        INC D
        DJNZ paint_row
        CALL released
wait_press:
        CALL read_p
        JR NZ,wait_press
        CALL released
        LD HL,$7C80
        LD DE,$486D
        LD B,8
restore_row:
        LD C,6
restore_cell:
        LD A,(HL)
        INC HL
        LD (DE),A
        SET 5,D
        LD A,(HL)
        INC HL
        LD (DE),A
        RES 5,D
        INC E
        DEC C
        JR NZ,restore_cell
        LD A,E
        SUB 6
        LD E,A
        INC D
        DJNZ restore_row
        LD HL,$7CE0
        CALL volume
        LD A,UI_MAP
        OUT ($F4),A
done:
        POP HL
        POP DE
        POP BC
        POP AF
        PUSH HL
        LD HL,$00DB
        EX (SP),HL
        PUSH AF
        LD A,9
        JP $0E10
released:
        CALL read_p
        JR Z,released
        RET
read_p:
        LD BC,$DFFE
        IN A,(C)
        AND 1
        RET
mute:
        LD D,3
        LD E,8
        LD BC,$FFF5
vol_save:
        LD A,E
        OUT (C),A
        INC C
        IN A,(C)
        LD (HL),A
        XOR A
        OUT (C),A
        INC HL
        DEC C
        INC E
        DEC D
        JR NZ,vol_save
        RET
volume:
        LD D,3
        LD E,8
        LD BC,$FFF5
vol_restore:
        LD A,E
        OUT (C),A
        INC C
        LD A,(HL)
        OUT (C),A
        INC HL
        DEC C
        INC E
        DEC D
        JR NZ,vol_restore
        RET
title:
        XOR A
        LD ($7AA4),A
        LD ($5BC2),A
        LD ($5BC3),A
        LD ($71D1),A
        LD A,3
        LD ($FDA5),A
        LD SP,$FFFE
        LD HL,$8634
        PUSH HL
        PUSH AF
        LD A,9
        JP $0E10
ui_end:
        ASSERT ui_end-UI_ORIGIN <= 336
ui_font EQU FONT_ORIGIN

        ORG KEY_ORIGIN
title_keys:
        LD BC,$BFFE
        IN A,(C)
        AND 1
        JP NZ,done
        PUSH IX
        PUSH IY
        LD HL,key_return
        PUSH HL
        XOR A
        PUSH AF
        LD HL,$0E11
        PUSH HL
        LD A,UI_MAP
        PUSH AF
        LD HL,$0E13
        PUSH HL
        LD HL,$BF99
        PUSH HL
        XOR A
        PUSH AF
        LD A,9
        JP $0E10
key_return:
        DI
        POP IY
        POP IX
        JP done
        ASSERT $ <= KEY_ORIGIN+64
