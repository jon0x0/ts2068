        ORG NORMALIZE_ADDRESS
; Rich pair -> black plus ink while the world is still scrolling.
normalize_tile:
        LD DE,$C700
        LD IX,16
normalize_cell:
        LD A,(DE)
        CP 7
        JR Z,normalize_skip
        CP $20
        JR C,normalize_high
        SUB $90
        JR normalize_index
normalize_high:
        ADD A,$60
normalize_index:
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$2000
        ADD HL,BC
        LD A,$86
        LD (DE),A
        INC DE
        LD C,8
normalize_line:
        LD A,(HL)
        LD B,A
        AND $38
        JR Z,paper_black
        LD A,B
        AND 7
        LD A,(DE)
        JR NZ,filled
        CPL
        JR normalized
filled:
        LD A,$FF
        JR normalized
paper_black:
        LD A,B
        AND 7
        LD A,(DE)
        JR NZ,normalized
        XOR A
normalized:
        LD (DE),A
        INC DE
        INC HL
        DEC C
        JR NZ,normalize_line
        JR normalize_next
normalize_skip:
        LD HL,9
        ADD HL,DE
        EX DE,HL
normalize_next:
        DEC IXL
        JR NZ,normalize_cell
        RET
        ASSERT $ <= $84B4
