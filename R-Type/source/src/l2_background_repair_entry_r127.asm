        ORG $1160
reveal_hook:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        LD A,I
        PUSH AF
        DI
        EX AF,AF'
        PUSH AF
        EX AF,AF'
        EXX
        PUSH BC
        PUSH DE
        PUSH HL
        EXX
        LD A,($7A8E)
        OR A
        JR NZ,stopped
        LD (reveal_index),A
        JR done
stopped:
        LD A,(reveal_index)
        CP 18
        JR NC,repair
        XOR A
        LD (repair_mode),A
        CALL paint_body_tile
        LD HL,reveal_index
        INC (HL)
        JR done
repair:
        LD A,($11CF)
        OR A
        JR Z,done
        LD A,$2B
        OUT ($F4),A
        CALL $B002
        XOR A
        LD ($11CF),A
done:
        EXX
        POP HL
        POP DE
        POP BC
        EXX
        EX AF,AF'
        POP AF
        EX AF,AF'
        POP AF
        JP PO,return_di
        EI
return_di:
        JP reveal_return
        ASSERT $ <= $11C9
