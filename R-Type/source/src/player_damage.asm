; Coverage-only damage; do not replay snapshot pixels outside the ship masks.
        ORG $F080
        JP clear
        JP restore_pixel
        JP old_mask
        JP rewind
        JP current_mask
        JP restore_attr
clear:
        PUSH HL
        PUSH BC
        LD HL,$F740
        LD A,($F6B8)
        LD B,A
        XOR A
clear_row:
        DUP 5
        LD (HL),A
        INC L
        EDUP
        DJNZ clear_row
        POP BC
        POP HL
        RET
old_mask:
        PUSH IY
        POP DE
        LD A,E
        SUB 65
        LD E,A
        LD BC,$0820
old_mask_row:
        DUP 4
        LDI
        EDUP
        INC DE
        DJNZ old_mask_row
        RET
rewind:
        DUP 5
        DEC DE
        EDUP
        RET
current_mask:
        LD HL,($F692)
        LD DE,64
        ADD HL,DE
        LD DE,$F740
        LD BC,32
        LDIR
        RET
restore_pixel:
        PUSH BC
        PUSH DE
        LD C,A
        LD A,IXL
        SUB $80
        LD E,A
        LD D,$F7
        LD A,(DE)
        LD B,A
        LD A,C
        XOR (HL)
        AND B
        XOR (HL)
        POP DE
        POP BC
        RET
restore_attr:
        PUSH BC
        PUSH DE
        LD C,A
        LD A,IXL
        SUB $80
        LD E,A
        LD D,$F7
        LD A,(DE)
        OR A
        LD A,C
        JR NZ,attr_ready
        LD A,(HL)
attr_ready:
        POP DE
        POP BC
        RET
        ASSERT $ <= $F100
