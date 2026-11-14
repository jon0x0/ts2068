; Per-level-instance colour groups. No writes to cartridge ROM.
        ORG $08C0
; DE=world8-pixel column. HL returns pointer to its20-bit row mask.
lookup_group:
        LD HL,$0200
lookup_next:
        LD C,(HL)
        INC HL
        LD B,(HL)
        INC HL
        LD A,D
        CP B
        JR C,lookup_found
        JR NZ,lookup_skip
        LD A,E
        CP C
        JR C,lookup_found
lookup_skip:
        INC HL
        JR lookup_next
lookup_found:
        LD A,(HL)
        LD L,A
        LD H,0
        LD C,A
        LD B,0
        ADD HL,HL
        ADD HL,BC
        LD BC,GROUP_DICTIONARY
        ADD HL,BC
        RET
        ASSERT $ <= $08F0
        DS $08F0-$,$FF
; HL=row mask, A=screen cell row. C preserved. Returns style bit3.
select_group_row:
        CP 20
        JR NC,select_zero
        LD E,A
        AND 7
        LD B,A
        LD A,E
        SRL A
        SRL A
        SRL A
        LD E,A
        LD D,0
        ADD HL,DE
        LD A,(HL)
        INC B
select_rotate:
        RRCA
        DJNZ select_rotate
        AND $80
        RLCA
        RLCA
        RLCA
        RLCA
        RET
select_zero:
        XOR A
        RET
        ASSERT $ <= $0920
        DS $0920-$,$FF
; A=attribute, HL=source cell, DE=native attribute destination.
initial_group_attribute:
        BIT 7,A
        RET Z
        PUSH BC
        PUSH DE
        PUSH HL
        LD C,A
        LD A,($7A9C)
        AND A
        JR NZ,initial_group_done
        LD A,H
        CP $D9
        JR C,initial_group_done
        CP $E6
        JR NC,initial_group_done
        LD A,D
        AND 3
        RLCA
        RLCA
        RLCA
        LD B,A
        LD A,E
        AND $E0
        RLCA
        RLCA
        RLCA
        OR B
        LD B,A
        PUSH BC
        LD A,($7A84)
        SUB 8
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        LD A,E
        AND 31
        LD E,A
        LD D,0
        ADD HL,DE
        EX DE,HL
        CALL lookup_group
        POP BC
        LD A,B
        PUSH BC
        CALL select_group_row
        POP BC
        LD B,A
        LD A,C
        AND $F7
        OR B
        LD C,A
initial_group_done:
        LD A,C
        POP HL
        POP DE
        POP BC
        RET
        ASSERT $ <= $0990
        DS $0990-$,$FF
prepare_group_column:
        PUSH AF
        PUSH BC
        PUSH DE
        LD A,($7A84)
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        LD A,($7A83)
        LD E,A
        LD D,0
        ADD HL,DE
        DEC HL
        EX DE,HL
        CALL lookup_group
        LD DE,$FC50
        LD BC,3
        LDIR
        POP DE
        POP BC
        POP AF
        LD HL,$5E00
        RET
        ASSERT $ <= $09D0
        DS $09D0-$,$FF
apply_group_column:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD A,(HL)
        BIT 7,A
        JR Z,apply_group_skip
        LD C,A
        LD A,IXL
        SUB $80
        SRL A
        SRL A
        PUSH BC
        LD HL,$FC50
        CALL select_group_row
        POP BC
        LD B,A
        LD A,C
        AND $F7
        OR B
        POP HL
        LD (HL),A
        JR apply_group_restore
apply_group_skip:
        POP HL
apply_group_restore:
        POP DE
        POP BC
        POP AF
        RET
        ASSERT $ <= $0A08
        DS $0A08-$,$FF
