        ORG $0FC3
        LD B,8
row:
        LD A,(HL)
        LD (DE),A
        INC HL
        RES 5,D
        LD A,C
        LD (DE),A
        INC HL
        SET 5,D
        INC D
        DJNZ row
        RET
        ASSERT $ <= $0FE0
