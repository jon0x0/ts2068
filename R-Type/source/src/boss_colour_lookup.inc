; One tag per8address bytes; nonempty9byte cells never conflict.
; Immutable sparse lookup, original level bitmap format unchanged.
boss_colour_lookup:
        PUSH BC
        PUSH HL
        LD A,H
        CP $D5
        JR NZ,level_general_tag
        LD A,L
        CP $50
        JR C,level_general_tag
        CP $74
        JR NC,level_general_tag
        AND 3
        LD C,A
 IFDEF ROM_ONLY
        LD A,($BE01)
 ELSE
        LD A,($3FF1)
 ENDIF
        ADD A,A
        ADD A,A
        ADD A,C
        ADD A,16
        JR level_palette_address
level_general_tag:
        LD A,H
        CP $C4
        JR C,boss_not_found
        CP $D8
        JR NC,boss_not_found
        CP $C4
        JR NZ,level_check_last
        LD A,L
        CP $CE
        JR C,boss_not_found
level_check_last:
        LD A,H
        CP $D7
        JR NZ,level_enemy_colour
        LD A,L
        CP $F9
        JR NC,boss_not_found
level_enemy_colour:
        LD A,H
        SUB $C4
        LD H,A
        DUP 3
        SRL H
        RR L
        EDUP
        LD BC,$0200
        ADD HL,BC
        LD A,(HL)
        CP $FF
        JR Z,boss_not_found
level_palette_address:
        POP HL
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$0C00
        ADD HL,BC
        POP BC
        SCF
        RET
boss_not_found:
        POP HL
        POP BC
        AND A
        RET
