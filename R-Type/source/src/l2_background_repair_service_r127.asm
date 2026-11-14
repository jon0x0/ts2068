        ORG $106C
paint_body_tile:
        DI
        LD A,$1B
        OUT ($F4),A
        LD HL,REVEAL_COORDS
        LD A,(reveal_index)
        LD C,A
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
        LD A,$2B
        OUT ($F4),A
        CALL $A7CC
        LD A,($7A9C)
        PUSH AF
        XOR A
        LD ($7A9C),A
        PUSH HL
        LD HL,force_tile_draw
        LD ($FBA9),HL
        POP HL
        CALL draw_background_copy
        LD A,(repair_mode)
        OR A
        JR NZ,paint_done
        CALL $C3E5
        LD DE,$0404
        CALL $8CFD
paint_done:
        CALL $C3EE
        POP AF
        LD ($7A9C),A
        LD HL,$0D01
        LD ($FBA9),HL
        RET
take_dirty:
damage_lookup:
        LD A,1
        LD ($11CF),A
        LD A,H
        CP $C7
        RET
        ASSERT $ <= $10F0
