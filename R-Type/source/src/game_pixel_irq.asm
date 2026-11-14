; IRQ entry must restore HOME mapping before storing the saved bank number.
; Mirrored at FD20 in HOME and bank7, including the exit after OUT(F4).
        ORG $FD20
        PUSH AF
        IN A,($F4)
        PUSH AF
        LD A,9
        OUT ($F4),A
        POP AF
        LD ($FBCA),A
        PUSH BC
        PUSH DE
        JP $BE26
        ASSERT $ <= $FD40
        DS $FD40-$,$FF
        LD A,($FBCA)
        OUT ($F4),A
        POP AF
        EI
        RET
        ASSERT $ == $FD48
