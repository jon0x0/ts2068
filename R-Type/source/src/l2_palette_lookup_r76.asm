        ORG $0F80
        LD A,H
        CP $C7
        JR NZ,ordinary
        LD A,(HL)
        CP $90
        JR C,no
        SUB $90
        PUSH BC
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$2000
        ADD HL,BC
        ADD A,$90
        POP BC
        SCF
        RET
ordinary:
        LD A,H
        CP $DC
        JR C,no
        BIT 7,(HL)
        JR Z,no
        LD A,(HL)
        AND $7F
        PUSH BC
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$FBD0
        ADD HL,BC
        POP BC
        SCF
        RET
no:
        OR A
        RET
keep_dictionary_token:
store:
        LD (DE),A
        JP $FF84
        ASSERT $ <= $0FC3
