; Entry/exit mirrored in HOME and bank7. Raw interrupted stack stays in its bank.
        ORG $FD20
        PUSH AF
        PUSH BC
        IN A,($F4)
        LD B,A
        LD A,9
        OUT ($F4),A
        LD A,B
        LD ($FBCA),A
        LD ($5BCE),SP
        LD SP,$5BC0
        PUSH BC
        PUSH DE
        JP $BE26
        ASSERT $ <= $FD40
        DS $FD40-$,$FF
        OUT ($F4),A
        POP BC
        POP AF
        EI
        RET
        DS $FD48-$,$FF
