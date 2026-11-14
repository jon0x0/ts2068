        ORG $8A4D
        CALL $0F20 ; initialize both HOME display planes before enabling ECM
 IFNDEF ROM_ONLY
        LD A,$0D
        OUT ($F4),A
        LD HL,$A600
        LD DE,$4000
        LD BC,$0C00
        LDIR
        LD A,RUNTIME_MAP
        OUT ($F4),A
 ENDIF
        LD HL,title_glyphs
        LD DE,$FC60
        LD BC,18
        LDIR
        XOR A
        LD ($FC51),A
        LD A,248
title_sweep:
        LD ($FC50),A
        CALL title_step
        LD A,($FC50)
        SUB 8
        JR NC,title_sweep
        LD A,1
        LD ($FC51),A
        XOR A
title_spread:
        LD ($FC50),A
        CALL title_step
        LD A,($FC50)
        ADD A,16
        CP 224
        JR C,title_spread
 IFNDEF ROM_ONLY
        LD A,$0D
        OUT ($F4),A
        LD HL,$4000
        LD DE,$A600
        LD BC,$0C00
        LDIR
        LD A,RUNTIME_MAP
        OUT ($F4),A
 ENDIF
        RET
title_step:
        LD A,RUNTIME_MAP
        OUT ($F4),A
        LD A,2
        OUT ($FF),A
        EI
        HALT
        DI
        LD A,$42
        OUT ($FF),A
        CALL $1AB0
        LD A,RUNTIME_MAP
        OUT ($F4),A
        LD A,2
        OUT ($FF),A
        EI
        RET
title_glyphs:
        DB 0,6,0, 6,3,6, 9,6,9, 15,6,15, 21,5,21, 26,6,26
        ASSERT $ <= $8AE7
