        ORG $A7CC
capture_boss:
        PUSH BC
        PUSH HL
        DI
        LD A,$3B
        OUT ($F4),A
        LD HL,$C700
        LD DE,SCRATCH
        LD BC,144
        LDIR
        LD A,$7B
        OUT ($F4),A
        LD A,(reveal_index)
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD E,A
        LD D,0
        ADD HL,DE
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD DE,$CB00
        ADD HL,DE
        EX DE,HL
        LD HL,SCRATCH
        LD BC,144
        LDIR
        POP HL
        POP BC
        LD A,9
        JP $1E1C
        ASSERT $ <= $A816
