        ORG $1AC0
        LD HL,$A600
        LD IX,$1100
        LD B,48
title_publish_motion_row:
        PUSH BC
        PUSH HL
        LD E,(IX+0)
        LD D,(IX+1)
        LD BC,32
        LDIR
        POP HL
        PUSH HL
        LD DE,$0600
        ADD HL,DE
        LD E,(IX+0)
        LD D,(IX+1)
        SET 5,D
        LD BC,32
        LDIR
        POP HL
        LD BC,32
        ADD HL,BC
        INC IX
        INC IX
        POP BC
        DJNZ title_publish_motion_row
        RET
        ASSERT $ <= $1B00
