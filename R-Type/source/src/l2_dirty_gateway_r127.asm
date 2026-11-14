        ORG $3820
mark_gateway:
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        CALL MARK_ENTRY
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        PUSH BC
        PUSH DE
        EXX
        PUSH HL
        LD HL,$8D00
        EX (SP),HL
        LD A,9
        JP PO,$1E1C
        JP $1E18
        ASSERT $ <= $3848
