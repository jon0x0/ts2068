; Runtime L4 prescroll from a cached unshifted detailed frame.
; Row palette mapping is precomputed (1024-byte 2-bit LUT); no pixel search.
        ORG $A300
synth_row:
        PUSH HL
        PUSH BC
        LD (cur_attr),A
        LD A,E
        LD (cur_bits),A
        LD A,(phase_x)
        LD D,A
        LD A,($DF32)
        AND 1
        LD A,D
        JR Z,synth_phase_ready
        NEG
        AND 3
synth_phase_ready:
        LD (synth_phase),A
        LD A,(synth_phase)
        OR A
        JP Z,synth_unshifted
        LD A,(height)
        ADD A,A
        LD E,A
        LD D,0
        OR A
        SBC HL,DE
        PUSH HL
        LD DE,($DF36)
        OR A
        SBC HL,DE
        POP HL
        LD DE,0
        JR C,previous_ready
        LD E,(HL)
        INC HL
        LD D,(HL)
previous_ready:
        LD A,E
        LD (prev_bits),A
        LD A,D
        LD (prev_attr),A
        LD A,(cur_bits)
        LD E,A
        LD A,(cur_attr)
        CALL coverage
        LD (cover),A
        LD A,(prev_bits)
        LD E,A
        LD A,(prev_attr)
        CALL coverage
        LD D,A
        LD A,(cover)
        LD E,A
        CALL merge
        LD A,E
        LD (cover),A
        LD A,(synth_phase)
        CP 3
        LD A,(cur_attr)
        JR C,palette_selected
        LD A,(prev_attr)
palette_selected:
        OR A
        JR NZ,palette_nonzero
        LD A,(cur_attr)
        LD D,A
        LD A,(prev_attr)
        OR D
palette_nonzero:
        LD D,A
        LD A,(cover)
        CP $FF
        LD A,D
        JR Z,palette_ready
        AND 7
        JR NZ,palette_ready
        LD A,D
        RRCA
        RRCA
        RRCA
        AND 7
palette_ready:
        AND $3F
        LD (target_attr),A
        LD A,(cur_bits)
        LD E,A
        LD A,(cur_attr)
        CALL mapped
        LD A,E
        LD (result_bits),A
        LD A,(prev_bits)
        LD E,A
        LD A,(prev_attr)
        CALL mapped
        LD D,E
        LD A,(result_bits)
        LD E,A
        CALL merge
        LD A,(target_attr)
        POP BC
        POP HL
        RET
synth_unshifted:
        LD A,(cur_bits)
        LD E,A
        LD A,(cur_attr)
        POP BC
        POP HL
        RET
coverage:
        LD D,A
        LD C,E
        AND 7
        JR NZ,ink_visible
        LD E,0
ink_visible:
        LD A,D
        AND $38
        LD A,E
        RET Z
        LD A,C
        CPL
        OR E
        RET
merge:
        LD A,(synth_phase)
        ADD A,A
        LD B,A
merge_loop:
        SRL D
        RR E
        DJNZ merge_loop
        RET
mapped:
        LD B,E
        LD C,A
        AND $3F
        SRL A
        SRL A
        LD E,A
        LD D,0
        LD A,(target_attr)
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,DE
        LD DE,$2400
        ADD HL,DE
        LD A,C
        AND 3
        LD C,A
        LD A,(HL)
        JR Z,mapping_ready
mapping_rotate:
        RRCA
        RRCA
        DEC C
        JR NZ,mapping_rotate
mapping_ready:
        AND 3
        LD E,B
        CP 1
        RET Z
        CP 2
        JR Z,invert_bits
        CP 3
        LD E,0
        RET NZ
        DEC E
        RET
invert_bits:
        LD A,E
        CPL
        LD E,A
        RET
        ASSERT $ <= $A450
phase_x EQU $DF33
height EQU $DF39
cur_bits EQU $DF45
cur_attr EQU $DF46
prev_bits EQU $DF47
prev_attr EQU $DF48
target_attr EQU $DF49
result_bits EQU $DF4A
cover EQU $DF4C

synth_phase EQU $DF4D
