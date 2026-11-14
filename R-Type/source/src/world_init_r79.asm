; Common world initializer: suppress the native star callback before clearing
; attributes. Native8721 calls73BC to re-enable it after scenery construction.
; Keep IRQs/audio/input available; do not synthesize ownership from pixels.
        ORG $0CF0
        CALL $73C2
        CALL $86C3
        PUSH HL
        LD HL,0
        LD ($FF81),HL
        POP HL
        RET
        DS $0D00-$,$45
        ASSERT $ == $0D00
