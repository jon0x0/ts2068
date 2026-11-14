; Precompiled bitmap/ECM row pairs for Bellmite. Expanded RAM only.
        ORG $88EB
        JP paint
paint:
        PUSH AF
        PUSH HL
        PUSH DE
        LD DE,$EFA1
        OR A
        SBC HL,DE
        JP C,reject
        ADD HL,DE
        LD DE,$F5A1
        OR A
        SBC HL,DE
        JP NC,reject
        POP DE
        POP HL
        POP AF
        ; Unowned core cells use the original fast renderer/dictionary.
        LD A,($5C82)
        OR A
        JR NZ,ours
        PUSH AF
        LD A,H
        CP $F3
        JP C,reject_core
        JR NZ,core_test_done
        LD A,L
        CP $F1
        JP C,reject_core
core_test_done:
        POP AF
ours:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        LD (src),HL
        LD (meta),DE
        LD A,($5C82)
        LD (owner),A
        LD IX,0
        ADD IX,SP
        LD A,(IX+12) ; 12 saved bytes, helper return, then native return
        CP $24
        JR NZ,not_normal_gate
        INC A
not_normal_gate:
        CP $25
        JR Z,gate_caller
        CP $8C
        JR Z,gate_caller
        CP $F8
        JR Z,gate_caller
        CP $52
        JR NZ,caller_ready
gate_caller:
        ADD A,5
caller_ready:
        LD (caller),A
        LD A,($5C81)
        AND $3F
        LD (flash),A
        LD A,(owner)
        OR A
        JR NZ,owner_done
        LD A,(HL)
        AND $7F
        CP 16
        JR C,flat_token
        ADD A,$90
        JR NC,token_ready
        ADD A,$10
        JR token_ready
flat_token:
        AND 7
token_ready:
        PUSH HL
        LD H,D
        LD L,E
        LD BC,-$600
        ADD HL,BC
        LD (HL),A
        POP HL
owner_done:
        ; An existing fully opaque foreground cell cannot expose any rear
        ; pixel. Reject it before decoding/reversing source rows.
        LD A,(owner)
        OR A
        JR Z,visible_source
        PUSH DE
        LD A,D
        SUB $7E
        RLCA
        RLCA
        RLCA
        ADD A,$40
        LD D,A
        LD A,$1D
        OUT ($F4),A
        LD B,8
opaque_row:
        LD A,(DE)
        AND 7
        JR Z,not_opaque
        LD A,(DE)
        AND $38
        JR Z,not_opaque
        INC D
        DJNZ opaque_row
        POP DE
        LD A,$19
        OUT ($F4),A
        JP return_saved
not_opaque:
        POP DE
        LD A,$19
        OUT ($F4),A
visible_source:
        CALL $01C8 ; only visible cells need the interruptible copy
        LD DE,$F3F1
        OR A
        SBC HL,DE
        JR C,core
        ; Exact division by9 using its inverse57 modulo256.
        LD A,L
        LD C,A
        ADD A,A
        ADD A,A
        ADD A,A
        LD B,A
        ADD A,A
        ADD A,A
        ADD A,A
        SUB B
        ADD A,C
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD DE,$8C00
        LD A,(caller)
        CP $91
        JR Z,horizontal_cache
        CP $57
        JR NZ,cache_base_ready
horizontal_cache:
        LD DE,$F380
cache_base_ready:
        ADD HL,DE
        XOR A
        LD (reverse_y),A
        LD A,(caller)
        CP $FD
        JR Z,cache_reverse_y
        CP $57
        JR NZ,cache_ready
cache_reverse_y:
        LD DE,14
        ADD HL,DE
        LD A,1
        LD (reverse_y),A
cache_ready:
        LD (cache),HL
        JP start_copy
core:
        ; Build the uncommon core overlap cell into a16-byte private cache.
        LD HL,(src)
        LD A,(HL)
        AND $7F
        INC HL
        LD (core_src),HL
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD DE,$2000
        ADD HL,DE
        LD IX,$8BF0
        LD A,(caller)
        CP $FD
        JR Z,core_reverse_y
        CP $57
        JR NZ,core_row_start
core_reverse_y:
        LD IX,$8BFE
core_row_start:
        LD DE,(core_src)
        LD A,$1B
        OUT ($F4),A
        LD B,8
core_row:
        LD A,(DE)
        LD C,A
        LD A,(caller)
        CP $91
        JR Z,core_reverse_bits
        CP $57
        LD A,C
        JR NZ,core_bits_ready
core_reverse_bits:
        PUSH HL
        LD H,$5D
        LD L,C
        LD A,(HL)
        POP HL
core_bits_ready:
        LD (IX),A
        LD A,(HL)
        LD (IX+1),A
        INC HL
        INC DE
        LD A,(caller)
        CP $FD
        JR Z,core_step_back
        CP $57
        JR Z,core_step_back
        INC IX
        INC IX
        JR core_next
core_step_back:
        DEC IX
        DEC IX
core_next:
        DJNZ core_row
        LD HL,$8BF0
        LD (cache),HL
        XOR A
        LD (reverse_y),A
start_copy:
        DI
        LD (saved_sp),SP
        LD SP,$5CF0
        LD A,$1F
        LD HL,(cache)
        BIT 6,H
        JR Z,cache_mapping_ready
        LD A,$9F
cache_mapping_ready:
        OUT ($F4),A
        EI
        LD DE,(meta)
        LD A,D
        SUB $7E
        RLCA
        RLCA
        RLCA
        ADD A,$60
        LD D,A
        LD A,(owner)
        OR A
        JR NZ,blend_start
        CALL $1A6E ; specialized forward/reverse/flash copies
        JP finish
blend_start:
        PUSH DE
        LD A,(reverse_y)
        OR A
        LD DE,$0023 ; INC HL / NOP / NOP
        LD C,0
        JR Z,step_ready
        LD DE,$2B2B ; DEC HL three times
        LD C,$2B
step_ready:
        LD (row_step),DE
        LD A,C
        LD (row_step+2),A
        POP DE
        LD B,8
blend_row:
        LD A,(DE)
        LD (old_bits),A
        RES 5,D
        LD A,(DE)
        LD (old_attr),A
        SET 5,D
        AND $38
        JR Z,old_black_paper
        LD A,(old_attr)
        AND 7
        JR NZ,occluded_row
        CALL get_row
        LD A,(old_attr)
        RRCA
        RRCA
        RRCA
        AND 7
        LD (foreground),A
        LD A,(old_bits)
        CPL
        LD (front_mask),A
        CALL combine_pair
        JR C,blend_next
        CALL mask
        CPL
        LD C,A
        LD A,(old_bits)
        AND C
        LD (DE),A
        JR blend_next
old_black_paper:
        CALL get_row
        LD A,(old_attr)
        AND 7
        JR Z,replace
        LD (foreground),A
        LD A,(old_bits)
        LD (front_mask),A
        CALL combine_pair
        JR C,blend_next
        CALL mask
        LD C,A
        LD A,(old_bits)
        OR C
        LD (DE),A
        JR blend_next
replace:
        LD A,(source_bits)
        LD (DE),A
        RES 5,D
        LD A,(source_attr)
        LD (DE),A
        SET 5,D
blend_next:
        INC D
        DJNZ blend_row
        JR finish
occluded_row:
        INC HL
        CALL row_step
        JR blend_next
finish:
        DI
        LD A,$19
        OUT ($F4),A
        LD SP,(saved_sp)
return_ours:
        DI
        CALL $097B ; restore normal vector and title source byte
return_saved:
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        XOR A
        SCF
        RET
get_row:
        LD A,(HL)
        LD C,A
        LD (source_bits),A
        INC HL
        LD A,(flash)
        OR A
        JR NZ,flash_attr
        LD A,(HL)
flash_attr:
        LD (source_attr),A
row_step:
        INC HL
        NOP
        NOP
        RET
combine_pair:
        LD A,(front_mask)
        OR A
        JR Z,replace_empty_row
        CP $FF
        JR Z,pair_handled
        LD C,A
        CALL mask
        OR C
        CP $FF
        JR NZ,pair_not_possible
        LD A,(source_attr)
        AND $38
        JR Z,back_ink
        LD A,(source_attr)
        AND 7
        JR Z,back_paper
        LD A,(source_bits)
        LD C,A
        LD A,(front_mask)
        OR C
        CP $FF
        JR Z,back_ink
back_paper:
        LD A,(source_attr)
        AND $38
        RRCA
        RRCA
        RRCA
        JR back_colour_ready
back_ink:
        LD A,(source_attr)
        AND 7
back_colour_ready:
        RLCA
        RLCA
        RLCA
        LD C,A
        LD A,(foreground)
        OR C
        RES 5,D
        LD (DE),A
        SET 5,D
        LD A,(front_mask)
        LD (DE),A
pair_handled:
        SCF
        RET
replace_empty_row:
        LD A,(source_bits)
        LD (DE),A
        RES 5,D
        LD A,(source_attr)
        LD (DE),A
        SET 5,D
        SCF
        RET
pair_not_possible:
        OR A
        RET
mask:
        LD A,(source_attr)
        AND $38
        JR Z,source_black_paper
        LD A,(source_attr)
        AND 7
        LD A,$FF
        RET NZ
        LD A,(source_bits)
        CPL
        RET
source_black_paper:
        LD A,(source_attr)
        AND 7
        RET Z
        LD A,(source_bits)
        RET
reject_core:
        POP AF
        OR A
        RET
reject:
        POP DE
        POP HL
        POP AF
        OR A
        RET
src: DW 0
meta: DW 0
cache: DW 0
core_src: DW 0
saved_sp: DW 0
caller: DB 0
owner: DB 0
flash: DB 0
reverse_y: DB 0
source_bits: DB 0
source_attr: DB 0
old_bits: DB 0
old_attr: DB 0
foreground: DB 0
front_mask: DB 0
        ASSERT $ <= $8BF0

