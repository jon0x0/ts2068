; Temporary HOME5E00 code; native staging is regenerated before reuse.
        ORG $5E00
        LD A,8
        OUT ($F4),A
        LD HL,$4000
        LD DE,$6000
        LD BC,$2000
        LDIR
        LD A,$20
        OUT ($F4),A
        LD HL,$A4AE
        LD DE,$C4AE
        LD BC,$1B52
        LDIR
        LD A,$40
        OUT ($F4),A
        LD HL,$C000
        LD DE,$E000
        LD BC,$187C
        LDIR
        LD HL,$DBD0
        LD DE,$FBD0
        LD BC,128
        LDIR
        LD A,$80
        OUT ($F4),A
        LD HL,$FB00
        LD DE,$5B00
        LD BC,512
        LDIR
        XOR A
        OUT ($F4),A
        LD HL,$8100
        LD DE,$A000
        LD BC,DRIVER_LENGTH
        LDIR
        LD A,9
        OUT ($F4),A
        XOR A
        LD ($FBC0),A
        LD ($FBC1),A
        LD ($FBC2),A
        LD ($FD92),A
        CALL $1485
        EI
        RET
        ASSERT $ <= $5EB4
