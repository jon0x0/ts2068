        ORG $9D10
        LD A,($FC50)
        AND 4
        LD HL,$9D80
        LD C,6
        JR Z,sweep_atlas_ready
        LD HL,$9EA0
        INC C
sweep_atlas_ready:
        LD A,C
        LD ($FC55),A
        LD A,($FC50)
        RRCA
        RRCA
        RRCA
        AND 31
        LD ($FC53),A
        LD E,A
        LD D,$A6
        LD B,48
sweep_row:
        PUSH BC
        PUSH DE
        LD A,($FC55)
        LD C,A
sweep_byte:
        LD A,($FC53)
        LD B,A
        LD A,($FC55)
        ADD A,B
        SUB C
        CP 32
        JR NC,sweep_skip
        LD A,(HL)
        OR A
        JR Z,sweep_skip
        LD (DE),A
        PUSH HL
        CALL $01C8
        LD B,A
        LD A,D
        ADD A,6
        LD D,A
        LD A,B
        LD (DE),A
        LD A,D
        SUB 6
        LD D,A
        POP HL
sweep_skip:
        INC HL
        INC E
        DEC C
        JR NZ,sweep_byte
        POP DE
        LD A,E
        ADD A,32
        LD E,A
        JR NC,sweep_next
        INC D
sweep_next:
        POP BC
        DJNZ sweep_row
        JP $1AC0
        ASSERT $ <= $9D80
