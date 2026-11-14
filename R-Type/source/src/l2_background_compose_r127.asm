        ORG COMPOSITOR
compose_background:
        LD A,I
        PUSH AF
        DI
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        LD A,(REVEAL_INDEX)
        CP 18
        JR NC,active
        LD A,$FF
        LD ($11CA),A
        JP finish
active:
        LD A,D
        AND $E0
        CP $60
        JP NZ,finish
        LD A,D
        AND $18
        LD B,A
        LD A,E
        AND $E0
        RLCA
        RLCA
        RLCA
        OR B
        LD B,A
        LD A,E
        AND $1F
        LD C,A
        LD A,B
        AND $1C
        ADD A,A
        LD D,A
        LD A,C
        RRCA
        RRCA
        AND 7
        OR D
        LD (tile_key),A
        LD A,B
        AND 3
        ADD A,A
        ADD A,A
        LD B,A
        LD A,C
        AND 3
        OR B
        LD (cell_index),A
        LD A,($A413)
        OR A
        JR Z,forward_source
        LD DE,-14
        ADD HL,DE
forward_source:
        LD DE,cell_pairs
        LD BC,16
        LDIR
        LD A,$7F
        OUT ($F4),A
        LD HL,REVEAL_COORDS
        LD B,18
        LD C,34
find_tile:
        LD A,(tile_key)
        CP (HL)
        JR Z,found
        INC HL
        INC C
        DJNZ find_tile
        JP finish
found:
        LD A,($11CA)
        CP C
        JR Z,tile_ready
        LD B,C
        CALL $381C
tile_ready:
        LD A,$3F
        OUT ($F4),A
        LD A,(cell_index)
        LD L,A
        LD H,0
        LD D,H
        LD E,L
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,DE
        LD DE,SCRATCH
        ADD HL,DE
        LD A,(HL)
        CP 7
        JR Z,finish
        CALL $A7C0
        XOR A
        LD ($A412),A
        LD HL,cell_pairs
        LD A,($A413)
        OR A
        JR Z,forward_result
        LD HL,cell_pairs+14
forward_result:
        POP IX
        EX (SP),HL
        JR restore
finish:
        POP IX
restore:
        LD A,$6F
        OUT ($F4),A
        POP HL
        POP DE
        POP BC
        POP AF
        JP PO,composed_di
        EI
composed_di:
        LD A,($A412)
        RET
last_tile: DB $FF
tile_key: DB 0
cell_index: DB 0
cell_pairs: DS 16,0
        ASSERT $ <= $B0DE

