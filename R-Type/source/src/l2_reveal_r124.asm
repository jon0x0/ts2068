        ORG LOW_CODE
reveal_hook:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        EX AF,AF'
        PUSH AF
        EX AF,AF'
        EXX
        PUSH BC
        PUSH DE
        PUSH HL
        EXX
        LD A,($7AA4)
        OR A
        JR Z,reveal_done
        LD A,($7A8E)
        OR A
        JR NZ,reveal_stopped
        LD (reveal_index),A
        JR reveal_done
reveal_stopped:
        LD A,(reveal_index)
        CP 18
        JR NC,reveal_done
        LD C,A
        LD A,$1B
        OUT ($F4),A
        LD HL,REVEAL_COORDS
        LD B,0
        ADD HL,BC
        LD A,(HL)
        LD D,A
        AND 7
        ADD A,A
        ADD A,A
        LD C,A
        LD A,D
        AND $38
        RRCA
        LD B,A
        PUSH BC
        LD A,(reveal_index)
        ADD A,34
        LD B,A
        LD A,9
        OUT ($F4),A
        LD A,B
        CALL $882D
        POP BC
        LD A,($7A9C)
        PUSH AF
        XOR A
        LD ($7A9C),A
        PUSH HL
        LD HL,force_tile_draw
        LD ($FBA9),HL
        POP HL
        CALL draw_background_copy
        CALL $C3E5
        LD DE,$0404
        CALL $8CFD
        CALL $C3EE
        POP AF
        LD ($7A9C),A
        LD HL,$0D01
        LD ($FBA9),HL
        LD HL,reveal_index
        INC (HL)
reveal_done:
        EXX
        POP HL
        POP DE
        POP BC
        EXX
        EX AF,AF'
        POP AF
        EX AF,AF'
        JP reveal_return
snapshot_saved: DB 0
reveal_index: DB 0
        ASSERT $ <= $1E20
