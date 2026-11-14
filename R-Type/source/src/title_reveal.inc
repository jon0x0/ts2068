        DS $FC80-$,$FF
title_motion_draw:
        LD HL,$A600
        LD BC,$0C00
        XOR A
        CALL $FDF0
        LD A,($FC51)
        OR A
        JP Z,$9D10
        LD IY,$FC60
        LD A,6
        LD ($FC52),A
title_motion_glyph:
        LD A,($FC50)
        RRCA
        RRCA
        RRCA
        AND 31
        LD C,A
        LD A,($FC51)
        OR A
        LD A,C
        JR Z,title_motion_x
        CP (IY+2)
        JR C,title_motion_x
        LD A,(IY+2)
title_motion_x:
        LD ($FC53),A
        LD L,(IY+0)
        LD H,$90
        LD B,48
title_motion_row:
        PUSH BC
        PUSH HL
        LD A,H
        ADD A,$16
        LD D,A
        LD A,L
        SUB (IY+0)
        LD E,A
        LD A,($FC53)
        ADD A,E
        LD E,A
        LD C,(IY+1)
title_motion_cell:
        LD A,($FC53)
        ADD A,(IY+1)
        SUB C
        CP 32
        JR NC,title_motion_clip
        LD A,(HL)
        OR A
        JR Z,title_motion_clip
        LD A,(DE)
        OR (HL)
        LD (DE),A
        PUSH HL
        CALL $01C8
        LD B,A
        LD A,D
        ADD A,6
        LD D,A
        LD A,B
        LD (DE),A
        LD A,D
        SUB 6
        LD D,A
        POP HL
title_motion_clip:
        INC HL
        INC E
        DEC C
        JR NZ,title_motion_cell
        POP HL
        LD DE,32
        ADD HL,DE
        POP BC
        DJNZ title_motion_row
        LD DE,3
        ADD IY,DE
        LD A,($FC52)
        DEC A
        LD ($FC52),A
        JR NZ,title_motion_glyph
        JP $1AC0
        ASSERT $ <= $FD20
