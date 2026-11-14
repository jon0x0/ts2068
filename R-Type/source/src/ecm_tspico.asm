; Live ECM TSPico RAM renderer. Original tile pipeline publishes its own 8x1
; colours; HOME3 is display attributes, writable DOCK3 is game workspace.
        ORG $1400
ecm_input:
        CALL $C2D6
        CALL $0D00
publish_hud:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD A,3
        OUT ($F4),A
        PUSH IY
        LD HL,$5A80
        LD DE,$7800         ; unused HOME tail, not mapped game workspace
        LD BC,128
        LDIR
        LD A,7
        OUT ($F4),A
        LD HL,$7800
        LD DE,$5800         ; retained bank tail after 6144-byte colour shadow
        LD IY,$7080
        LD B,128
hud_cell:
        LD A,(DE)
        CP (HL)
        JR Z,hud_unchanged
        LD A,(HL)
        LD (DE),A
        AND $7F
        PUSH DE
        LD D,IYH
        LD E,IYL
        DUP 7
        LD (DE),A
        INC D
        EDUP
        LD (DE),A
        POP DE
hud_unchanged:
        INC HL
        INC DE
        INC IYL
        DJNZ hud_cell
        POP IY
        LD A,9
        OUT ($F4),A
        POP HL
        POP DE
        POP BC
        POP AF
        EI
publish_done:
        RET
ecm_menu_input:
        DI
        CALL $1A00
        EI
        RET
ecm_title_input:
        ; Menu retains the original 8x8 colours and original bitmap movement.
        ; Never repaint/recolour the live logo on every input poll.
        DI
        CALL $1A00
        EI
        RET
ecm_menu_restore:
        LD A,$0B
        OUT ($F4),A
        PUSH HL
        PUSH BC
        LD HL,$5800
        LD BC,768
        XOR A
        CALL $FDF0
        POP BC
        POP HL
        XOR A
        LD ($3FF0),A
        OUT ($FF),A
        LD A,9
        OUT ($F4),A
        JP $73C2
ecm_game_init:
        CALL $86C3
        CALL $0D00
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        DI
        LD A,3
        OUT ($F4),A
        LD HL,$5800
        LD DE,$6000
        LD BC,768
        CALL mirror_attributes
        CALL $0FE0
        ; Separate retained background palette, initialized before world draw.
        LD A,7
        OUT ($F4),A
        LD HL,$6000
        LD DE,$4000
        LD BC,$1800
        LDIR
        LD HL,$5800
        LD DE,$5801
        LD BC,127
        LD (HL),$FF
        LDIR
        LD A,2
        LD ($3FF0),A
        OUT ($FF),A
        LD A,9
        OUT ($F4),A
        POP HL
        POP DE
        POP BC
        POP AF
        EI
        RET
mirror_attributes:
        LD A,(HL)
        AND $7F
        DUP 7
        LD (DE),A
        INC D
        EDUP
        LD (DE),A
        LD A,D
        SUB 7
        LD D,A
        INC E
        JR NZ,mirror_no_wrap
        LD A,D
        ADD A,8
        LD D,A
mirror_no_wrap:
        INC HL
        DEC BC
        LD A,B
        OR C
        JR NZ,mirror_attributes
        RET
paint_tile:
        PUSH BC
        ; Exact displaced original $8EA2-$8EC1 semantics, including attribute
        ; override at self-modified $8EB1, pointer advance and result flags.
        LD A,($7A9C)
        LD (DE),A
        LD A,D
        SUB 6
        LD D,A
        LD A,(DE)
        LD B,A
        LD A,($8EB1)
        AND A
        JR Z,original_attribute
        LD (DE),A
        JR attribute_done
original_attribute:
        LD A,(HL)
        CALL $0920 ; instance palette for initial terrain
        LD (DE),A
attribute_done:
        LD C,A
        INC HL
        LD A,D
        AND 3
        RLCA
        RLCA
        RLCA
        PUSH BC
        LD B,A
        LD A,($8EBF)       ; game switches this between direct40/background60
        ADD A,B
        POP BC
        AND A
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        ; Stop the periodic source before sampling IFF2, avoiding the LD A,I
        ; interrupt-acknowledge P/V race. Mode shadow lives in owned DOCK1.
        LD A,$0B
        OUT ($F4),A
        PUSH AF ; keep frame layout; IRQ-safe code leaves IFF unchanged
        LD IX,0
        ADD IX,SP
        DEC HL
        LD A,($3FF0)
        AND A
        JR Z,paint_keep_native_attribute
        LD A,(IX+13)
        AND $20
        JR NZ,paint_keep_native_attribute
        LD A,($7A9C)
        AND A
        JR Z,paint_keep_native_attribute
        LD A,(IX+11)
        LD (DE),A
paint_keep_native_attribute:
        LD C,(IX+10)
        LD A,(IX+13)
        XOR $20           ; direct40 -> HOME ECM60; background60 -> DOCK2:40
        LD D,A
        PUSH DE
        LD A,($7A9C)
        LD B,A
        LD A,H
        CP $A0
        JP C,level_tile
        CP $C0
        JP NC,level_tile
        AND $1F
        OR $20
        LD H,A
        LD B,(HL)          ; precomputed deduplicated eight-colour row index
        POP DE
        LD A,C
        AND $38
        JP NZ,paint_flat
        LD A,C
        AND 7
        JP Z,paint_flat
        LD H,0
        LD L,B
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,$1B20
        ADD HL,BC
        CALL select_paint_bank
check_palette_flip:
        CALL palette_reverse_flag
        AND A
        JR NZ,paint_reverse
paint_forward:
        DUP 8
        LD A,(HL)
        LD (DE),A
        INC D
        INC HL
        EDUP
        JP paint_finish
paint_reverse:
        LD A,D
        ADD A,7
        LD D,A
        DUP 8
        LD A,(HL)
        LD (DE),A
        DEC D
        INC HL
        EDUP
        JP paint_finish
level_tile:
        POP DE
        CALL $0F80
        JR NC,level_enemy_row
        LD C,A
        PUSH DE
        LD A,(IX+13)
        AND $20
        JR NZ,terrain_store_native_attribute
        LD A,($7A9C)
        AND A
        JR NZ,terrain_native_attribute_done
terrain_store_native_attribute:
        LD E,(IX+8)
        LD D,(IX+9)
        CALL palette_reverse_flag
        XOR C
        OR $80
        LD (DE),A
terrain_native_attribute_done:
        POP DE
        CALL select_paint_bank
        JP check_palette_flip
level_enemy_row:
        CALL boss_colour_lookup
        JP NC,paint_flat
        CALL select_paint_bank
        JP check_palette_flip
paint_flat:
        CALL select_paint_bank
        LD A,C
        AND $7F
        DUP 8
        LD (DE),A
        INC D
        EDUP
paint_finish:
        LD A,($3FF0)
        OUT ($FF),A
        LD A,9
        OUT ($F4),A
        POP AF
paint_no_ei:
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        POP BC
        RET
palette_reverse_flag:
        LD A,(IX+16)
        CP $FD
        JR NZ,palette_reverse_other
        LD A,(IX+17)
        CP $8D
        JR Z,palette_reverse_yes
palette_reverse_other:
        LD A,(IX+16)
        CP $57
        JR NZ,palette_reverse_no
        LD A,(IX+17)
        CP $8E
        JR Z,palette_reverse_yes
palette_reverse_no:
        XOR A
        RET
palette_reverse_yes:
        LD A,$04
        RET
select_paint_bank:
        LD A,(IX+13)
        AND $20
        LD A,3
        JR Z,paint_bank_ready
        LD A,7
paint_bank_ready:
        OUT ($F4),A
        RET
restore_nonempty_colour:
        CALL restore_colour_core
        LD A,H             ; displaced $8886-$8888
        ADD A,$20
        RET
restore_empty_colour:
        PUSH AF
        XOR A
        CALL restore_colour_core
        POP AF
        XOR A              ; displaced $88BC-$88BE
        LD (HL),A
        INC H
        RET
restore_background_colour:
        ; Retained contract entry for the original conditional gate fixture.
        CALL restore_colour_core
        RET NZ
        INC SP
        INC SP
        JP $88B3
restore_colour_core:
        ; CALL replaces JP Z,$88B3 after the original PUSH HL / AND A.
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD B,A             ; original background ID; zero means empty sky
        LD A,$0B
        OUT ($F4),A
        PUSH AF ; keep frame layout; IRQ-safe code leaves IFF unchanged
        LD A,B
        AND A
        JR Z,restore_empty_cell
        LD D,H
        LD E,L
        LD BC,$2000
        ADD HL,BC
        EX DE,HL
        LD A,7             ; DOCK2 background attrs + writable HOME3 attrs
        OUT ($F4),A
        DUP 8
        LD A,(HL)
        LD (DE),A
        INC H
        INC D
        EDUP
        JR restore_colour_done
restore_empty_cell:
        ; Empty cells must lose both old sprite paper and stale background ink.
        ; Keep the original legacy ink/brightness so isolated stars retain colour.
        LD A,H
        AND $18
        RRCA
        RRCA
        RRCA
        ADD A,$58
        LD D,A
        LD E,L
        LD A,(DE)
        OR A
        JP P,restore_empty_native
        LD A,$47
restore_empty_native:
        AND $47
        PUSH AF
        LD DE,$2000
        ADD HL,DE
        LD A,3
        OUT ($F4),A
        POP AF
        DUP 8
        LD (HL),A
        INC H
        EDUP
restore_colour_done:
        LD A,($3FF0)
        OUT ($FF),A
        LD A,9
        OUT ($F4),A
        POP AF
restore_no_ei:
        POP HL
        POP DE
        POP BC
        POP AF
        RET

; Scroll retained ECM with the original one-character background shift.
scroll_background_colour:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        LD A,$0B
        OUT ($F4),A
        PUSH AF ; keep frame layout; IRQ-safe code leaves IFF unchanged
        LD A,7
        OUT ($F4),A
        PUSH IY
        LD IX,$1E30
        LD IYL,160
scroll_colour_line:
        LD L,(IX+0)
        LD H,(IX+1)
        INC IX
        INC IX
        LD D,H
        LD E,L
        DEC E
        LD BC,30
        DUP 30
        LDI
        EDUP
        DEC IYL
        JR NZ,scroll_colour_line
        POP IY
        LD A,($3FF0)
        OUT ($FF),A
        LD A,9
        OUT ($F4),A
        POP AF
scroll_colour_no_ei:
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        LD DE,$7801        ; displaced original $8CDD
        RET
; The source column writer bypasses paint_tile. Publish its 8 colour rows.
new_column_colour:
        CALL $09D0 ; apply cached incoming group mask to staging token
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IY
        LD A,$0B
        OUT ($F4),A
        PUSH AF ; keep frame layout; IRQ-safe code leaves IFF unchanged
        LD A,(HL)
        LD C,A
        LD D,(IX+1)
        LD E,(IX+0)
        LD A,7
        OUT ($F4),A
column_flat:
        LD B,8
        LD IYL,0
column_flat_line:
        LD A,C
        CALL $0E00
        LD (DE),A
        PUSH DE
        SET 5,D
        XOR A
        LD (DE),A
        POP DE
        INC D
        INC IYL
        DJNZ column_flat_line
column_done:
        LD A,($3FF0)
        OUT ($FF),A
        LD A,9
        OUT ($F4),A
        POP AF
column_no_ei:
        POP IY
        POP HL
        POP DE
        POP BC
        LD A,(HL)         ; retain terrain palette marker in the back buffer
        RET
; Terrain pixel shifts bypass dirty sprite restoration. Publish the matching
; legacy terrain colours for each actual terrain run, preserving actor cells.
MODE_SHADOW EQU $3FF0
        INCLUDE "src/terrain_live_colour.inc"
        INCLUDE "src/boss_colour_lookup.inc"
        INCLUDE "src/title_publish.inc"
        ASSERT $ <= $1A00
