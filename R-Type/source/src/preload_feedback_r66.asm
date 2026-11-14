        ORG FEEDBACK_ORIGIN
; An immediate, bitmap-preserving loading screen using standard attribute
; cells with identical ink/paper. The ECM bitmap and colours stay untouched.
loading_feedback:
        LD HL,$5800
        LD DE,$5801
        LD BC,767
        LD (HL),0
        LDIR
        LD HL,feedback_bits
        LD DE,$5900
        LD B,20
feedback_byte:
        PUSH BC
        LD A,(HL)
        LD B,8
feedback_pixel:
        RLCA
        PUSH AF
        SBC A,A
        AND $3F
        LD (DE),A
        INC DE
        POP AF
        DJNZ feedback_pixel
        INC HL
        POP BC
        DJNZ feedback_byte
        XOR A
        OUT ($FF),A
        RET
feedback_bits: DB 204,236,12,74,170,138,10,174,204,204,12,238,138,136,10,170,138,232,10,170
