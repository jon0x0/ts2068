; No changes to native background or actor ownership planes.
        ORG $11B4
        DS $11BE-$,0
cleanup_guard:
        LD A,(BC)
        DEC C
        OR A
        RET NZ
        INC C
        CALL $10E2
        DEC C
        OR A
        RET
        ASSERT $ == $11C9
