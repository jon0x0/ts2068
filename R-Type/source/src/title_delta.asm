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
        LD L,C
        LD H,0
        ADD HL,HL
        LD DE,delta_sources
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD D,(HL)
        EX DE,HL
        LD BC,672
        LD A,($FC52)
        OR A
        JR NZ,delta_copy_atlas
        LD BC,1344
delta_copy_atlas:
        LD A,$93
        OUT ($F4),A
        LD DE,$A600
        LDIR
        LD A,$13
        OUT ($F4),A
delta_atlas_loaded:
        LD A,($FC50)
        AND 6
        LD C,A
        LD A,($FC51)
        OR A
        JR Z,delta_fine_ready
        LD A,C
        AND 4
        RRCA
        LD C,A
delta_fine_ready:
        LD HL,$A600
        LD DE,336
        LD A,C
        SRL A
        JR Z,delta_phase_ready
delta_phase_add:
        ADD HL,DE
        DEC A
        JR NZ,delta_phase_add
delta_phase_ready:
        LD ($FC5E),HL
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
delta_sources: DW $E400,$E940,$EBE0,$EE80,$F120,$F3C0,$F660
        ASSERT $ <= $9EA0
