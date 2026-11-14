; Relocatable paired-plane XOR publisher, fed ALREADY COMPOSED local deltas.
; A=min raster Y, C=left byte column, HL=record stream.
; Nine row groups: count, then (column offset, bitmap XOR, attribute XOR) records.
; No full-screen scan. Row table handles all Spectrum address discontinuities.
; Caller owns background composition/overlap and interrupt/bank visibility.
        ORG $8200
publish_object:
        PUSH HL
        LD ($9100),A
        LD IX,$9000
        LD B,9
build_rows:
        LD A,($9100)
        LD D,A
        AND 7
        OR $40
        LD H,A
        LD A,D
        AND $C0
        RRCA
        RRCA
        RRCA
        OR H
        LD H,A
        LD A,D
        AND $38
        RLCA
        RLCA
        OR C
        LD L,A
        LD (IX),L
        LD (IX+1),H
        INC IX
        INC IX
        LD HL,$9100
        INC (HL)
        DJNZ build_rows
        POP HL
        LD IX,$9000
        LD B,9
next_row:
        LD E,(IX)
        LD D,(IX+1)
        INC IX
        INC IX
        LD A,E
        LD IYL,A
        LD A,(HL)
        INC HL
        OR A
        JR Z,row_done
        LD C,A
next_cell:
        LD A,(HL)
        INC HL
        ADD A,IYL
        LD E,A
        LD A,(HL)
        OR A
        JR Z,bitmap_same
        LD A,(DE)
        XOR (HL)
        LD (DE),A
bitmap_same:
        INC HL
        SET 5,D
        LD A,(HL)
        OR A
        JR Z,attribute_same
        LD A,(DE)
        XOR (HL)
        LD (DE),A
attribute_same:
        INC HL
        RES 5,D
        DEC C
        JR NZ,next_cell
row_done:
        DJNZ next_row
        RET
