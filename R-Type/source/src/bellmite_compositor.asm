; Stage-five only. Runs in DOCK4 free music-layout gap, never from IRQ.
        ORG $88EB
        JP prepare
        JP paint
        JP restore_registers
prepare:
        PUSH IX
        PUSH IY
        PUSH BC
        PUSH DE
        PUSH HL
        CALL restore
        POP HL
        POP DE
        POP BC
        LD A,C
        LD (left),A
        LD A,B
        LD (top),A
        LD A,E
        LD (width),A
        LD A,D
        LD (height),A
        LD A,1
        LD ($5C80),A
        LD A,1
        LD (operation),A
        CALL walk
        POP IY
        POP IX
        RET
restore_registers:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        CALL restore
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        RET
restore:
        LD A,($5C80)
        CP 1
        RET NZ
        XOR A
        LD (operation),A
        CALL walk
        XOR A
        LD ($5C80),A
        RET
walk:
        LD A,(top)
        LD (cy),A
        LD A,(height)
        LD (rows_left),A
        LD IX,$5BC0
walk_row:
        LD A,(left)
        LD (cx),A
        LD A,(width)
        LD (cols_left),A
walk_cell:
        LD A,(cy)
        CP 20
        JR NC,walk_skip
        LD A,(cx)
        OR A
        JR Z,walk_skip
        CP 31
        JR NC,walk_skip
        CALL metadata
        LD A,(operation)
        OR A
        JR Z,walk_restore
        LD A,(HL)
        LD (IX),A
        CP $80
        JR C,walk_skip
        CP $DC
        JR NC,walk_skip
        LD (HL),0
        JR walk_skip
walk_restore:
        LD A,(HL)
        OR A
        JR NZ,walk_skip
        LD A,(IX)
        LD (HL),A
walk_skip:
        INC IX
        LD A,(cx)
        INC A
        LD (cx),A
        LD A,(cols_left)
        DEC A
        LD (cols_left),A
        JR NZ,walk_cell
        LD A,(width)
        LD E,A
        LD A,16
        SUB E
        LD E,A
        LD D,0
        ADD IX,DE
        LD A,(cy)
        INC A
        LD (cy),A
        LD A,(rows_left)
        DEC A
        LD (rows_left),A
        JR NZ,walk_row
        RET
metadata:
        LD A,(cy)
        RRCA
        RRCA
        RRCA
        AND 3
        ADD A,$7E
        LD H,A
        LD A,(cy)
        AND 7
        RRCA
        RRCA
        RRCA
        LD L,A
        LD A,(cx)
        OR L
        LD L,A
        RET
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
        LD A,($5C80)
        CP 1
        JP NZ,not_ours
        POP DE
        POP HL
        POP AF
        PUSH IX
        LD IX,0
        ADD IX,SP
        LD A,(IX+4) ; helper call return, then native paint return
        POP IX
        LD (caller),A
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        LD (src),HL
        LD (meta),DE
        ; Convert metadata address back into target row/column.
        LD A,E
        AND 31
        LD C,A
        LD A,(left)
        LD B,A
        LD A,C
        SUB B
        LD C,A
        LD A,D
        SUB $7E
        ADD A,A
        ADD A,A
        ADD A,A
        LD B,A
        LD A,E
        RLCA
        RLCA
        RLCA
        AND 7
        OR B
        LD B,A
        LD A,(top)
        LD E,A
        LD A,B
        SUB E
        ADD A,A
        ADD A,A
        ADD A,A
        ADD A,A
        ADD A,C
        LD E,A
        LD D,0
        LD HL,$5BC0
        ADD HL,DE
        LD A,(HL)
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


