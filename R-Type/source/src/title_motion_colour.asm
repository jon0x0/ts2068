        ORG $01C8
        LD A,($FC51)
        OR A
        JR Z,shared_colour
        CALL $01A0
        JR C,shared_colour
        LD A,H
        ADD A,6
        LD H,A
        LD A,(HL)
        RET
shared_colour:
        LD A,E
        AND 31
        LD B,A
        LD A,($FC50)
        RRCA
        RRCA
        RRCA
        AND 31
        ADD A,3
        CP B
        LD A,$07
        RET NC
        LD A,$05
        RET
        ASSERT $ <= $0200
