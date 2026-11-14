; Publish once after the original title movement and prompt printing finish.
title_publish:
        CALL $FDF0
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        DI
 IFNDEF ROM_ONLY
        LD A,$0B
        OUT ($F4),A
 ENDIF
        LD A,$40
        OUT ($FF),A
        LD HL,$7800
        LD DE,$5800
        LD BC,640
        LDIR
        LD A,$13
        OUT ($F4),A
        LD HL,$5800
        LD DE,$6000
        LD BC,768
        CALL mirror_attributes
        LD HL,$9000
        LD IYH,0
        CALL title_plane
        LD HL,$9600
        LD IYH,$20
        CALL title_plane
        LD A,2
        LD (MODE_SHADOW),A
        OUT ($FF),A
 IFDEF ROM_ONLY
        LD A,3
 ELSE
        LD A,9
 ENDIF
        OUT ($F4),A
        LD HL,$8281
        LD B,6
title_protect_row:
        PUSH BC
        LD C,30
title_protect_cell:
        LD (HL),1
        INC HL
        DEC C
        JR NZ,title_protect_cell
        INC HL
        INC HL
        POP BC
        DJNZ title_protect_row
 IFDEF TITLE_DELTA
        ; Text rows2..11, columns9..31: guard both lines of each moving star.
        LD HL,$8149
        LD B,10
title_text_guard_row:
        LD C,23
title_text_guard_cell:
        LD (HL),1
        INC HL
        DEC C
        JR NZ,title_text_guard_cell
        LD DE,9
        ADD HL,DE
        DJNZ title_text_guard_row
 ENDIF
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        EI
        RET
title_plane:
        LD IX,$1100
        LD IYL,48
title_copy_row:
        LD E,(IX+0)
        LD D,(IX+1)
        LD A,D
        ADD A,IYH
        LD D,A
        LD BC,32
        LDIR
        INC IX
        INC IX
        DEC IYL
        JR NZ,title_copy_row
        RET
title_scores_restore:
 IFNDEF ROM_ONLY
        LD A,$0B
        OUT ($F4),A
 ENDIF
        XOR A
        LD (MODE_SHADOW),A
        OUT ($FF),A
 IFDEF ROM_ONLY
        JP $BC90
 ELSE
        LD A,9
        OUT ($F4),A
        JP $7690
 ENDIF
