; Selected once per cell, avoiding per-row flash/direction memory reads.
        ORG $1A6E
        LD A,(FLASH)
        LD C,A
        LD A,(REVERSE_Y)
        OR A
        JP NZ,$0F57
        LD A,C
        OR A
        JP NZ,$0FC3
        LD B,8
forward_row:
        LD A,(HL)
        LD (DE),A
        INC HL
        RES 5,D
        LD A,(HL)
        LD (DE),A
        INC HL
        SET 5,D
        INC D
        DJNZ forward_row
        RET
        ASSERT $ <= $1AA0
