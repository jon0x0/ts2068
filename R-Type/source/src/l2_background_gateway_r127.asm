        ORG $381C
background_get:
        LD ($11C8),SP
        LD A,$3B
        OUT ($F4),A
        LD SP,$5CF0
        LD A,B
        LD HL,$0FB8
        PUSH HL
        JP $01D8
background_resume:
        LD A,C
        LD ($11CA),A
        LD HL,$C700
        LD DE,SCRATCH
        LD BC,144
        LDIR
        LD SP,($11C8)
        LD A,$3F
        JP $0FBF
        ASSERT $ <= $3848
