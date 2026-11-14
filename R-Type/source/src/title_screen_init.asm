        ORG $0F20
        DI
        LD A,$40
        OUT ($FF),A
        LD A,3
        OUT ($F4),A
        LD HL,$4000
        LD BC,$1800
        XOR A
        CALL $FDF0
        LD HL,$6000
        LD BC,$1800
        LD A,$47
        CALL $FDF0
        LD A,2
        LD (MODE_SHADOW),A
        LD A,RUNTIME_MAP
        OUT ($F4),A
        RET
        ASSERT $ <= $0F80
