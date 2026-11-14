; Stage-five sparse overlap compositor. Ordinary owner gating stays native.
        ORG $88EB
        JP paint
        JP paint
paint:
        ; Test source before touching registers/flags used by original fallback.
        PUSH AF
        PUSH HL
        PUSH DE
        LD DE,$EFA1
        OR A
        SBC HL,DE
        JP C,not_ours
        ADD HL,DE
        LD DE,$F87C ; actual pool ends before AY code
        OR A
        SBC HL,DE
        JP NC,not_ours
        POP DE
        POP HL
        POP AF
        PUSH IX
        LD IX,0
        ADD IX,SP
        LD A,(IX+4) ; helper call return, then native paint return
        POP IX
        CP $24
        JR NZ,caller_not_normal_gate
        ADD A,1
caller_not_normal_gate:
        CP $24
        JR C,caller_ready
        CP $25
        JR Z,caller_gate
        CP $8C
        JR Z,caller_gate
        CP $F8
        JR Z,caller_gate
        CP $52
        JR NZ,caller_ready
caller_gate:
        ADD A,5
caller_ready:
        LD (caller),A
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        LD (src),HL
        LD (meta),DE
        LD A,(DE)
        LD (owner),A
        ; Leave the first actor's collision owner in place for shared cells.
        OR A
        JR NZ,owner_ready
        LD A,($7A9C)
owner_ready:
        LD HL,(meta)
        LD (HL),A
        LD A,(owner)
        OR A
        JR NZ,token_done
        LD HL,(src)
        LD A,(HL)
        AND $7F
        CP 16
        JR C,token_flat
        ADD A,$90
        JR NC,token_store
        ADD A,$10
        JR token_store
token_flat:
        AND 7
token_store:
        LD HL,(meta)
        LD DE,-$600
        ADD HL,DE
        LD (HL),A
token_done:
        LD HL,(src)
        LD DE,$F3F1
        OR A
        SBC HL,DE
        JR C,dictionary_row
        LD DE,432
        OR A
        SBC HL,DE
        JR NC,dictionary_row
        ADD HL,DE
        ; Exact tile offsets are multiples of9. 57 is9's inverse modulo256.
        ; The tile index is0..47, so the low byte gives the exact quotient.
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
        LD BC,$8C00
        ADD HL,BC
        LD DE,(src)
        INC DE
        LD (src),DE
        JR palette_ready
dictionary_row:
        LD HL,(src)
        LD A,(HL)
        AND $7F
        INC HL
        LD (src),HL
        LD H,0
        LD L,A
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD DE,$2000
        ADD HL,DE
palette_ready:
        LD DE,(src)
        LD IX,pixels
        LD IY,colours
        LD A,(caller)
        CP $FD
        JR Z,reverse_start
        CP $57
        JR NZ,source_start
reverse_start:
        LD IX,pixels+7
        LD IY,colours+7
source_start:
        LD A,$1B
        OUT ($F4),A
        LD B,8
source_row:
        LD A,(DE)
        LD C,A
        LD A,(caller)
        CP $91
        JR Z,reverse_bits
        CP $57
        LD A,C
        JR NZ,bits_ready
reverse_bits:
        PUSH HL
        LD H,$5D
        LD L,C
        LD A,(HL)
        POP HL
bits_ready:
        LD (IX),A
        LD A,($5C81)
        AND A
        JR Z,source_colour
        AND $3F
        JR colour_ready
source_colour:
        LD A,(HL)
colour_ready:
        LD (IY),A
        INC HL
        INC DE
        LD A,(caller)
        CP $FD
        JR Z,reverse_step
        CP $57
        JR Z,reverse_step
        INC IX
        INC IY
        JR source_next
reverse_step:
        DEC IX
        DEC IY
source_next:
        DJNZ source_row
        LD HL,(meta)
        LD A,H
        SUB $7E
        RLCA
        RLCA
        RLCA
        ADD A,$60
        LD H,A
        LD IX,pixels
        LD IY,colours
        LD A,$1F
        OUT ($F4),A
        LD B,8
blend_row:
        LD A,(HL)
        LD (previous),A
        LD D,H
        LD E,L
        RES 5,D
        LD A,(DE)
        LD (previous_colour),A
        LD A,(owner)
        OR A
        JR Z,replace_row
        LD A,(previous_colour)
        AND $38
        JR Z,old_paper_black
        LD A,(previous_colour)
        AND 7
        JR NZ,blend_next ; two opaque colours: fully covered
        CALL source_mask
        CPL
        LD C,A
        LD A,(previous)
        AND C
        LD (HL),A
        JR blend_next
old_paper_black:
        LD A,(previous_colour)
        AND 7
        JR Z,replace_row
        CALL source_mask
        LD C,A
        LD A,(previous)
        OR C
        LD (HL),A
        JR blend_next
replace_row:
        LD A,(IX)
        LD (HL),A
        LD A,(IY)
        LD (DE),A
blend_next:
        INC H
        INC IX
        INC IY
        DJNZ blend_row
        LD A,$19
        OUT ($F4),A
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        XOR A
        SCF
        RET
source_mask:
        LD A,(IY)
        AND $38
        JR Z,source_black_paper
        LD A,(IY)
        AND 7
        LD A,$FF
        RET NZ
        LD A,(IX)
        CPL
        RET
source_black_paper:
        LD A,(IY)
        AND 7
        RET Z
        LD A,(IX)
        RET
not_ours:
        POP DE
        POP HL
        POP AF
        OR A
        RET
left: DB 0
top: DB 0
width: DB 0
height: DB 0
cx: DB 0
cy: DB 0
rows_left: DB 0
cols_left: DB 0
operation: DB 0
caller: DB 0
owner: DB 0
src: DW 0
meta: DW 0
previous: DB 0
previous_colour: DB 0
pixels: DS 8,0
colours: DS 8,0
        ASSERT $ <= $8C00


