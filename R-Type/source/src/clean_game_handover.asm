; A full black standard-video refresh forces caches to discard the title.
; Runs from DOCK0, keeps mapping/stack unchanged and preserves post-init AF.
        ORG $0CF0
        CALL $1485
        PUSH AF
        XOR A
        OUT ($FF),A
        EI
        HALT
        HALT
        LD A,2
        OUT ($FF),A
        POP AF
        RET
        ASSERT $ == $0D00
