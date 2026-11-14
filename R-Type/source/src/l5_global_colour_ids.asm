; Authoring-only zero-page table space; live palette kernels start at0100.
; Enter with F4=0B and interrupts disabled. High HOME stack remains visible
; again before any stack read; table itself is immutable in DOCK7.
        ORG $0040
        PUSH AF
        PUSH DE
        PUSH HL
        LD DE,$A600
        OR A
        SBC HL,DE
        SRL H
        RR L
        SRL H
        RR L
        SRL H
        RR L
        LD DE,$E000
        ADD HL,DE
        LD A,$8B
        OUT ($F4),A
        LD B,(HL)
        LD A,$0B
        OUT ($F4),A
        POP HL
        POP DE
        POP AF
        RET
        ASSERT $ <= $0080
