        ORG ATTR_ENTRY
restore_tile_colours:
        DI
        PUSH DE
        PUSH BC
        PUSH HL
        PUSH IX
        LD IX,$C700
        LD A,4
        LD (rows),A
row:
        LD A,4
        LD (columns),A
cell:
        PUSH BC
        LD A,B
        AND $18
        OR $40
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
        LD B,8
line:
        LD A,(HL)
        LD (DE),A
        INC HL
        INC D
        DJNZ line
        LD DE,9
        ADD IX,DE
        POP BC
        INC C
        LD HL,columns
        DEC (HL)
        JR NZ,cell
        LD A,C
        SUB 4
        LD C,A
        INC B
        LD HL,rows
        DEC (HL)
        JR NZ,row
        POP IX
        POP HL
        POP BC
        POP DE
        LD A,9
        JP $1E1C
rows: DB 0
columns: DB 0
        ASSERT $ <= $B0DE
