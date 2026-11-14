        ORG $0F57
        LD B,8
row:
        LD A,(HL)
        LD (DE),A
        INC HL
        RES 5,D
        LD A,C
        OR A
        JR NZ,attribute
        LD A,(HL)
attribute:
        LD (DE),A
        DEC HL
        DEC HL
        DEC HL
        SET 5,D
        INC D
        DJNZ row
        RET
        ASSERT $ <= $0F80
