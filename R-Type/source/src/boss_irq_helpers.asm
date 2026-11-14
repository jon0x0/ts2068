; DOCK0 unused gaps, visible with every gameplay mapping. No source archive edited.
        ORG $01C8
        PUSH AF
        LD A,($5B5D)
        CP $FD
        JR Z,vector_ready
        PUSH HL
        LD HL,$20C3
        LD ($5B5B),HL
        LD A,$FD
        LD ($5B5D),A
        LD A,$1D
        OUT ($F4),A
        LD ($5B5B),HL
        LD A,$FD
        LD ($5B5D),A
        LD A,$19
        OUT ($F4),A
        POP HL
vector_ready:
        LD A,$5B
        LD ($9000),A
        LD A,$8F
        LD I,A
        POP AF
        EI
        RET
        ASSERT $ <= $0200
