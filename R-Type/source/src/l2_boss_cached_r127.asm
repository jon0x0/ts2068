        ORG $B002
cached_boss:
        DI
        LD A,$7F
        OUT ($F4),A
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
        EXX
        LD E,0
        EXX
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
        LD DE,$7800
        ADD HL,DE
        LD A,(IX)
        LD (HL),A
        LD A,H
        ADD A,6
        LD H,A
        EX (SP),HL
        LD B,H
        LD C,L
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
        LD B,8
line:
        LD A,(IX)
        LD C,A
        LD A,(DE)
        XOR C
        EXX
        OR E
        LD E,A
        EXX
        LD A,C
        LD (DE),A
        RES 5,D
        LD A,(HL)
        LD C,A
        LD A,(DE)
        XOR C
        EXX
        OR E
        LD E,A
        EXX
        LD A,C
        LD (DE),A
        SET 5,D
        INC IX
        INC HL
        INC D
        DJNZ line
        POP BC
        POP HL
        EXX
        LD A,E
        EXX
        OR A
        JR Z,unchanged
        LD (HL),0
unchanged:
        INC C
        EXX
        DEC C
        EXX
        JR NZ,cell
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
        ASSERT $ <= $B0DE
