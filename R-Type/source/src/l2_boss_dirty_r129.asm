        ORG $B002
cached_boss:
        DI
        LD IX,$CB00
        LD IY,REVEAL_COORDS
        EXX
        LD D,18
        EXX
tile:
        LD A,$7F
        OUT ($F4),A
        LD A,(IY)
        INC IY
        LD D,A
        LD A,$6F
        OUT ($F4),A
        LD A,D
        AND 7
        ADD A,A
        ADD A,A
        LD C,A
        LD A,D
        AND $38
        RRCA
        LD B,A
        EXX
        LD B,4
        EXX
row:
        EXX
        LD C,4
        EXX
cell:
        CALL $A807
        PUSH BC
        LD L,B
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD B,0
        ADD HL,BC
        LD DE,$7E00
        ADD HL,DE
        LD A,(HL)
        LD (owner_flag),A
        OR A
        JR Z,metadata_done
dirty_cell:
        LD (HL),0
        LD A,H
        SUB 6
        LD H,A
        LD A,(IX)
        LD (HL),A
metadata_done:
        POP BC
        PUSH BC
        LD A,B
        AND $18
        OR $60
        LD D,A
        LD A,B
        AND 7
        RRCA
        RRCA
        RRCA
        OR C
        LD E,A
        LD A,(IX)
        SUB $90
        JR NC,index
        ADD A,$F0
index:
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$2000
        ADD HL,BC
        INC IX
        LD A,(owner_flag)
        OR A
        JR Z,front_setup
        LD B,8
line:
        LD A,(IX)
        LD (DE),A
        RES 5,D
        LD A,(HL)
        LD (DE),A
        SET 5,D
        INC IX
        INC HL
        INC D
        DJNZ line
        PUSH DE
        LD DE,-8
        ADD IX,DE
        POP DE
        LD BC,-8
        ADD HL,BC
        LD A,D
        SUB 8
        LD D,A
front_setup:
        RES 5,D
        LD A,$63
        OUT ($F4),A
        LD B,8
front_line:
        LD A,(IX)
        LD (DE),A
        SET 5,D
        LD A,(HL)
        LD (DE),A
        RES 5,D
        INC IX
        INC HL
        INC D
        DJNZ front_line
        LD A,$6F
        OUT ($F4),A
front_done:
        POP BC
next_cell:
        INC C
        EXX
        DEC C
        EXX
        JP NZ,cell
        LD A,C
        SUB 4
        LD C,A
        INC B
        EXX
        DEC B
        EXX
        JP NZ,row
        EXX
        DEC D
        EXX
        JP NZ,tile
        LD A,9
        JP $1E1C
owner_flag EQU $11C9
        ASSERT $ <= $B0DE
