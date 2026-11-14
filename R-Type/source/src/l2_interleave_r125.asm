        ORG INTERLEAVE
        LD HL,$C700
        LD DE,SCRATCH
        LD BC,144
        LDIR
        LD HL,SCRATCH+16
        LD IX,SCRATCH
        LD DE,$C700
        LD B,16
cell:
        LD A,(IX+0)
        INC IX
        OR A
        CALL Z,$39E0
        LD (DE),A
        INC DE
        PUSH BC
        LD BC,8
        LDIR
        POP BC
        DJNZ cell
        RET
        ASSERT $ <= $1E20
