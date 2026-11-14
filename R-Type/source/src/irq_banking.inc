        DS $FD20-$,$FF
irq_bank_enter:
        PUSH AF
        IN A,($F4)
        LD ($FBCA),A
        LD A,RUNTIME_MAP
        OUT ($F4),A
        PUSH BC
        PUSH DE
        JP $BE26
        ASSERT $ <= $FD40
        DS $FD40-$,$FF
irq_bank_exit:
        LD A,($FBCA)
        OUT ($F4),A
        POP AF
        EI
        RET
        ASSERT $ <= $FDA5
