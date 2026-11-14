; Input scanning may execute EI. Mask the SCLD source for the whole IRQ,
; then unmask under DI immediately before restoring the interrupted context.
        IF SECTION == 0
        ORG $08E2
        IN A,($FF)
        OR $40
        OUT ($FF),A
        JP $BE26
        ASSERT $ <= $08F0
        ENDIF
        IF SECTION == 1
        ORG $0911
        DI
        IN A,($FF)
        AND $BF
        OUT ($FF),A
        LD A,($FBCA)
        JP $FD40
        ASSERT $ <= $0920
        ENDIF
