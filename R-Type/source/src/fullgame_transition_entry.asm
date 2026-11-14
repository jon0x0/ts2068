; Called from level transition with baseline mapping9. Native8100 is scratch,
; never permanent executable code. Save only the graphics overwritten by driver.
        ORG $0A08
        DI
        LD HL,$A000
        LD DE,$8100
        LD BC,DRIVER_LENGTH
        LDIR
        LD HL,$0A30
        LD DE,$A000
        LD BC,DRIVER_LENGTH
        LDIR
        JP $A000
        ASSERT $ <= $0A30
