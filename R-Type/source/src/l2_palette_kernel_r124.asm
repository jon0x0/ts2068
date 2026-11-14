        ORG $0100
fine_palette:
        PUSH HL
        PUSH BC
        LD A,3
        CALL row_palette
        LD B,8
fine_line:
        LD A,(HL)
        SET 5,D
        LD (DE),A
        RES 5,D
        INC D
        INC HL
        DJNZ fine_line
        LD A,D
        SUB 8
        LD D,A
        POP BC
        POP HL
        RET
row_palette:
        PUSH BC
        PUSH DE
        PUSH AF
        LD A,I
        PUSH AF
        DI
        LD A,$1B
        OUT ($F4),A
        LD A,D
        AND $18
        RLCA
        RLCA
        RLCA
        LD C,A
        LD A,E
        AND $E0
        RRCA
        RRCA
        OR C
        LD C,A
        LD A,D
        AND 7
        OR C
        LD E,A
        LD D,0
        LD HL,TERRAIN_INKS
        LD A,($7A84)
        CP 56
        JR C,palette_source
        LD A,E
        CP 56
        JR C,palette_source
        LD HL,BOSS_INKS-56
palette_source:
        ADD HL,DE
        LD DE,row_cache
        LD BC,8
        LDIR
        POP AF
        JP PO,palette_di
        POP AF
        OUT ($F4),A
        EI
        JR palette_exit
palette_di:
        POP AF
        OUT ($F4),A
palette_exit:
        POP DE
        POP BC
        LD HL,row_cache
        RET
row_cache: DS 8,0
keep_token:
        LD (DE),A
        JP $FF84
force_tile_draw:
        POP AF
        SCF
        RET
reveal_return:
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        LD A,($7A8A)
        RET
draw_background_copy:
        PUSH BC
        PUSH HL
        LD DE,$0404
        CALL $8CFD
        POP HL
        POP BC
        RET
        ASSERT $ <= $0190
