        ORG $01A0
        LD A,(IY+2)
        ADD A,(IY+1)
        CP 32
        JR C,threshold_ready
        LD A,26
threshold_ready:
        RLCA
        RLCA
        RLCA
        LD B,A
        LD A,($FC50)
        CP B
        RET
        ASSERT $ <= $01C0
