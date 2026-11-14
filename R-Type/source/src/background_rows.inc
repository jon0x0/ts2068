        ASSERT $ <= $FA50
        DS $FA50-$,$FF
; Whole clean sky rows have neither background owners nor dirty cells.
; Reproduce the original8859 row setup, and scan31bytes with unrolled ORs.
scan_background_row:
        LD A,D
        ADD A,$26
        LD D,A
        LD E,(IX+2)
        LD H,(IX+1)
        LD L,E
        LD BC,4
        ADD IX,BC
        PUSH HL
        LD H,D
        LD L,E
        XOR A
        DUP 31
        OR (HL)
        DEC L
        EDUP
        OR A
        JR NZ,scan_row_needed
        LD A,H
        ADD A,3
        LD H,A
        LD L,E
        XOR A
        DUP 31
        OR (HL)
        DEC L
        EDUP
        OR A
        JR NZ,scan_row_needed
        POP HL
        LD A,E
        AND $E0
        LD E,A
        LD L,A
        LD B,D
        JP $8846
scan_row_needed:
        POP HL
        JP $8869
