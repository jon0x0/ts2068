        ORG $8A4D
        CALL $0F20
 IFNDEF ROM_ONLY
        LD A,$0D
        OUT ($F4),A
        LD HL,$A600
        LD DE,$4000
        LD BC,1344
        LDIR
 ENDIF
        XOR A
        LD ($FC51),A
        LD A,$FF
        LD ($FC54),A
        LD A,31
        LD ($FC5A),A
        LD A,248
delta_sweep:
        LD ($FC50),A
        CALL delta_step
        LD A,($FC50)
        SUB 4
        JR NC,delta_sweep
        LD A,1
        LD ($FC51),A
        XOR A
delta_spread:
        LD ($FC50),A
        CALL delta_step
        LD A,($FC50)
        ADD A,4
        CP 212
        JR C,delta_spread
 IFNDEF ROM_ONLY
        LD A,$0D
        OUT ($F4),A
        LD HL,$4000
        LD DE,$A600
        LD BC,1344
        LDIR
 ENDIF
        LD A,RUNTIME_MAP
        OUT ($F4),A
        RET
delta_step:
        LD A,RUNTIME_MAP
        OUT ($F4),A
        LD A,2
        OUT ($FF),A
        EI
        HALT
        DI
        CALL $1AB0
        EI
        RET
        ASSERT $ <= $8AE7

