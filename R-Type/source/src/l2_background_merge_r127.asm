        ORG $A7C0
merge_cell:
        PUSH HL
        CALL $39F2
        LD DE,$2000
        ADD HL,DE
        EX DE,HL
        POP HL
        INC HL
        LD IX,CELL_PAIRS
        LD A,($A413)
        OR A
        JR Z,start_row
        LD IX,CELL_PAIRS+14
start_row:
        LD B,8
row:
        LD A,(DE)
        OR A
        JR NZ,background_row
        LD A,($A412)
        OR A
        JR Z,next
        LD (IX+1),A
        JR next
background_row:
        AND 7
        JR Z,inverse
        LD A,(IX+0)
        OR (HL)
        JR bits
inverse:
        LD A,(IX+0)
        CPL
        AND (HL)
bits:
        LD (IX+0),A
        LD A,(DE)
        LD (IX+1),A
next:
        INC HL
        INC DE
        LD A,($A413)
        OR A
        JR NZ,reverse_next
        INC IX
        INC IX
        JR row_done
reverse_next:
        DEC IX
        DEC IX
row_done:
        DJNZ row
        RET
        ASSERT $ <= $A816

