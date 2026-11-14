        ORG $3848
install:
        LD A,$0B
        OUT ($F4),A
        LD A,$C3
        LD ($882D),A
        LD HL,$01D8
        LD ($882E),HL
        LD A,$CD
        LD ($868C),A
        LD HL,reveal_hook
        LD ($868D),HL
        LD A,$C3
        LD ($FF81),A
        LD HL,keep_token
        LD ($FF82),HL
        JP $01F4
get_tile:
        POP AF
        PUSH AF
        PUSH BC
        PUSH IX
        LD (tile_id),A
        LD A,I
        PUSH AF
        DI
        LD A,$1B
        OUT ($F4),A
        LD A,(tile_id)
        CP 52
        JR C,tile_valid
        XOR A
        LD (tile_id),A
tile_valid:
        CALL tile_pointer
        LD A,H
        ADD A,A
        XOR H
        AND $80
        JR NZ,tile_raw
        LD A,(HL)
        INC HL
        PUSH HL
        CALL tile_pointer
        LD A,H
        XOR $40
        LD H,A
        LD DE,$C700
        CALL expand
        LD HL,$C700
        LD DE,SCRATCH
        LD BC,144
        LDIR
        POP HL
        LD DE,$C700
        CALL expand
        LD HL,$C700
        LD DE,SCRATCH
        LD B,144
tile_xor:
        LD A,(DE)
        XOR (HL)
        LD (HL),A
        INC DE
        INC HL
        DJNZ tile_xor
        JR tile_ready
tile_raw:
        LD A,H
        XOR $40
        LD H,A
        LD DE,$C700
        CALL expand
tile_ready:
        LD A,(tile_id)
        CP 34
        JR C,tile_done
        LD A,($7A8E)
        OR A
        CALL Z,normalize_tile
tile_done:
        LD A,$0B
        OUT ($F4),A
        POP AF
        JP PO,tile_keep_di
        EI
tile_keep_di:
        POP IX
        POP BC
        LD HL,$C700
        JP $01E8
tile_pointer:
        LD L,A
        LD H,0
        ADD HL,HL
        LD DE,tile_table
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD D,(HL)
        EX DE,HL
        RET
expand:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        LD C,A
        LD B,0
        BIT 7,A
        JR NZ,backref
        LDIR
        JR expand
backref:
        AND $7F
        ADD A,3
        LD C,(HL)
        INC HL
        LD B,(HL)
        INC HL
        PUSH HL
        LD H,D
        LD L,E
        OR A
        SBC HL,BC
        LD C,A
        LD B,0
        LDIR
        POP HL
        JR expand
restore_native:
        PUSH DE
        LD A,$6F
        OUT ($F4),A
        LD HL,$C700
        LD DE,$A458
        LD BC,$03F4
        LDIR
        LD A,$2F
        OUT ($F4),A
        LD HL,$A458
        LD DE,$C458
        LD BC,$03F4
        LDIR
        LD A,$6F
        OUT ($F4),A
        LD HL,$E000
        LD DE,$C000
        LD BC,$187C
        LDIR
        XOR A
        LD (snapshot_saved),A
        LD A,$3A
        LD ($868C),A
        LD HL,$7A8A
        LD ($868D),HL
        POP DE
        RET
save_native:
        LD A,(snapshot_saved)
        OR A
        RET NZ
        LD HL,$A458
        LD DE,$C700
        LD BC,$03F4
        LDIR
        LD A,1
        LD (snapshot_saved),A
        RET
tile_id: DB 0
tile_table:
        DW TILE_POINTERS
reverse_cache:
        PUSH BC
        PUSH DE
        LD DE,row_cache+7
        LD B,4
reverse_pair:
        LD A,(DE)
        LD C,(HL)
        LD (HL),A
        LD A,C
        LD (DE),A
        INC HL
        DEC DE
        DJNZ reverse_pair
        POP DE
        POP BC
        LD HL,row_cache
        RET
global_return:
        LD A,$0B
        OUT ($F4),A
        POP AF
        RET PO
        EI
        RET
        ASSERT $ <= $3A00
