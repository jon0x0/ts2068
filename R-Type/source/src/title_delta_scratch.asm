; TSCodec-style retained raster replacement windows, prepared suffix phases.
        ORG $9D10
        LD A,($FC50)
        RRCA
        RRCA
        RRCA
        AND 31
        LD ($FC53),A
        LD (DELTA_BASE_OPERAND),A
        LD (DELTA_COLOUR_OFFSET_OPERAND),A
        LD C,A
        LD A,($FC51)
        OR A
        LD A,0
        JR Z,delta_suffix_ready
        LD HL,delta_stops
delta_find_suffix:
        LD A,(HL)
        CP C
        JR Z,delta_next_suffix
        JR NC,delta_suffix_found
delta_next_suffix:
        INC HL
        JR delta_find_suffix
delta_suffix_found:
        LD A,L
        SUB delta_stops&255
delta_suffix_ready:
        LD ($FC52),A
        LD E,A
        LD D,0
        LD HL,delta_prefix_ends
        ADD HL,DE
        LD A,(HL)
        LD (DELTA_PREFIX_OPERAND),A
        LD A,($FC52)
        CP 6
        LD A,($FC53)
        JR NZ,delta_colour_base_ready
        LD A,32
delta_colour_base_ready:
        LD (DELTA_COLOUR_BASE_OPERAND),A
        LD A,($FC52)
        LD C,A
        LD A,($FC54)
        CP C
        JR Z,delta_atlas_loaded
        LD A,C
        LD ($FC54),A
        CALL make_suffix
delta_atlas_loaded:
        CALL make_phase
        LD A,($FC53)
        LD C,A
        LD A,($FC5A)
        CP C
        JR C,delta_left_ready
        LD A,C
delta_left_ready:
        LD ($FC56),A
        LD E,A
        LD D,$90
        PUSH DE
        POP IX
        LD A,($FC5A)
        CP C
        JR NC,delta_right_ready
        LD A,C
delta_right_ready:
        ADD A,7
        CP 33
        JR C,delta_clip_ready
        LD A,32
delta_clip_ready:
        SUB E
        LD ($FC59),A
        LD A,C
        LD ($FC5A),A
        LD IY,$1100
        LD A,48
        LD ($FC61),A
delta_row:
        LD E,(IY+0)
        LD D,(IY+1)
        LD A,($FC56)
        ADD A,E
        LD E,A
        LD A,($FC56)
        LD C,A
        LD A,($FC59)
        LD B,A
        LD HL,($FC5E)
        PUSH HL
        CALL $FC80
        POP HL
        LD DE,7
        ADD HL,DE
        LD ($FC5E),HL
        LD A,($FC59)
        LD E,A
        LD A,32
        SUB E
        LD E,A
        LD D,0
        ADD IX,DE
        INC IY
        INC IY
        LD A,($FC61)
        DEC A
        LD ($FC61),A
        JR NZ,delta_row
        RET
delta_stops: DB 0,6,9,15,21,26,255
delta_prefix_ends: DB 0,6,9,15,21,26,32
; Scratch A600/A750 belongs to the title and is restored before gameplay.
; No source atlas aliases the bank7 player engine or caches.
make_suffix:
        LD IX,$9000
        LD IY,$A600
        LD B,48
suffix_row:
        PUSH BC
        PUSH IY
        POP HL
        XOR A
        LD C,7
suffix_clear:
        LD (HL),A
        INC HL
        DEC C
        JR NZ,suffix_clear
        LD A,($FC52)
        LD E,A
        LD D,0
        LD HL,glyphs
        ADD HL,DE
        ADD HL,DE
        LD A,6
        SUB E
        LD ($FC63),A
        JR Z,suffix_row_done
suffix_glyph:
        LD E,(HL)
        INC HL
        LD B,(HL)
        INC HL
        PUSH HL
        LD D,0
        PUSH IX
        POP HL
        ADD HL,DE
        PUSH IY
        POP DE
suffix_byte:
        LD A,(DE)
        OR (HL)
        LD (DE),A
        INC HL
        INC DE
        DJNZ suffix_byte
        POP HL
        LD A,($FC63)
        DEC A
        LD ($FC63),A
        JR NZ,suffix_glyph
suffix_row_done:
        LD DE,32
        ADD IX,DE
        LD DE,7
        ADD IY,DE
        POP BC
        DJNZ suffix_row
        RET
make_phase:
        LD HL,$A600
        LD ($FC5E),HL
        LD A,($FC50)
        AND 6
        LD C,A
        LD A,($FC51)
        OR A
        LD A,C
        JR Z,phase_amount
        AND 4
phase_amount:
        OR A
        RET Z
        LD ($FC62),A
        LD DE,$A750
        LD BC,336
        LDIR
        LD HL,$A750
        LD ($FC5E),HL
        LD B,48
phase_row:
        LD A,($FC62)
        LD E,A
phase_bit:
        PUSH HL
        LD C,7
        OR A
phase_byte:
        RR (HL)
        INC HL
        DEC C
        JR NZ,phase_byte
        POP HL
        DEC E
        JR NZ,phase_bit
        LD DE,7
        ADD HL,DE
        DJNZ phase_row
        RET
glyphs: DB 0,6,6,3,9,6,15,6,21,5,26,6
        ASSERT $ <= $9EA0
