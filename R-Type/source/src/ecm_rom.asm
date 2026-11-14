; Read-only ECM target. HOME A600-BDFF holds relocated 6000-77FF workspace.
; ROM1 contains immutable tagged sprite cells. No writable DOCK banks.
        ORG $1400
MODE EQU $BE00

ecm_input:
        CALL $C2D6
        CALL $0D00
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD HL,$5A80
        LD DE,$7080
        LD BC,128
        CALL mirror_attributes
        POP HL
        POP DE
        POP BC
        POP AF
publish_done:
        RET
ecm_menu_input:
ecm_title_input:
        JP $1A00
ecm_menu_restore:
        PUSH HL
        PUSH BC
        LD HL,$5800
        LD BC,768
        XOR A
        CALL $FDF0
        POP BC
        POP HL
        XOR A
        LD (MODE),A
        OUT ($FF),A
        JP $B9C2
ecm_game_init:
        CALL $86C3
        CALL $0D00
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD HL,$5800
        LD DE,$6000
        LD BC,768
        CALL mirror_attributes
        CALL $0FE0
        LD A,2
        LD (MODE),A
        OUT ($FF),A
        POP HL
        POP DE
        POP BC
        POP AF
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
        LD A,($7A9C)
        LD (DE),A
        LD A,D
        SUB 6
        LD D,A
        LD A,($8EB1)
        AND A
        JR NZ,selected_attribute
        LD A,(HL)
selected_attribute:
        LD C,A
        CALL $11B0
keep_background_token:
        INC HL
        LD B,$FF
        LD A,H
        CP $20
        JR C,raw_cell
        CP $40
        JR NC,raw_cell
        LD B,(HL)
        INC HL
raw_cell:
        PUSH BC
        LD A,D
        AND 3
        RLCA
        RLCA
        RLCA
        LD B,A
        LD A,($8EBF)
        ADD A,B
        AND A
        POP BC
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        PUSH AF ; keep frame layout; IRQ-safe code leaves IFF unchanged
        LD IX,0
        ADD IX,SP
        LD A,(MODE)
        AND A
        JP Z,paint_finish
        LD C,(IX+10)         ; selected original attribute
        LD A,(IX+13)
        AND $80
        JP NZ,paint_background_token
        LD A,(IX+13)
        ADD A,$20
        LD D,A
        LD A,(IX+11)
        CP $FF
        JR Z,paint_boss
        LD A,C
        AND $38
        JR NZ,paint_flat
        LD A,C
        AND 7
        JR Z,paint_flat
        LD A,(IX+11)
        CP $FF
        JR Z,paint_boss
        CALL cached_row
boss_palette_ready:
        CALL reverse_flag
        AND A
        JR NZ,paint_reverse
paint_forward:
        DUP 8
        LD A,(HL)
        LD (DE),A
        INC HL
        INC D
        EDUP
        JP paint_finish
paint_reverse:
        LD A,D
        ADD A,7
        LD D,A
        DUP 8
        LD A,(HL)
        LD (DE),A
        INC HL
        DEC D
        EDUP
        JP paint_finish
paint_boss:
        DEC HL
        CALL $0F80
        JR NC,paint_level_enemy
        CALL $1160
        LD A,3
        OUT ($F4),A
        JP boss_palette_ready
paint_level_enemy:
        CALL boss_colour_lookup
        JR C,boss_palette_ready
paint_flat:
        LD A,C
        AND $7F
        DUP 8
        LD (DE),A
        INC D
        EDUP
        JP paint_finish
paint_background_token:
        LD A,(IX+11)
        CP $FF
        JR Z,background_boss
        LD A,C
        AND $38
        JR NZ,background_flat
        LD A,C
        AND 7
        JR Z,background_boss
        LD A,(IX+11)
        CP $FF
        JR Z,background_boss
        OR $80
        LD (DE),A
        CALL reverse_flag
        LD C,A
        JR background_flip
background_boss:
        DEC HL
        CALL $0F80
        JR NC,background_level_enemy
        LD C,A
        CALL reverse_flag
        RRCA
        RRCA
        RRCA
        RRCA
        RRCA
        XOR C
        OR $80
        LD (DE),A
        LD C,$40
        JR background_flip
background_level_enemy:
        CALL boss_colour_lookup
        JR NC,background_flat
        ADD A,97
        OR $80
        LD (DE),A
        CALL reverse_flag
        LD C,A
        JR background_flip
background_flat:
        LD A,C
        AND $7F
        LD (DE),A
        LD C,0
background_flip:
        LD A,D
        ADD A,9
        LD D,A
        LD A,(DE)
        AND $3F
        OR C
        LD (DE),A
paint_finish:
        LD A,(MODE)
        OUT ($FF),A
        LD A,3
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
cached_row:
        PUSH BC
        LD BC,$1B20
        CP 97
        JR C,cached_row_address
        SUB 97
        LD BC,$0C00
cached_row_address:
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,BC
        POP BC
        RET
reverse_flag:
        LD A,(IX+16)
        CP $FD
        JR NZ,reverse_other
        LD A,(IX+17)
        CP $8D
        JR Z,reverse_yes
reverse_other:
        LD A,(IX+16)
        CP $57
        JR NZ,reverse_no
        LD A,(IX+17)
        CP $8E
        JR Z,reverse_yes
reverse_no:
        XOR A
        RET
reverse_yes:
        LD A,$80
        RET

restore_nonempty_colour:
        CALL restore_colour_core
        LD A,H
        ADD A,$66           ; display40 -> relocated bufferA6
        RET
restore_empty_pixels:
        XOR A
        CALL restore_colour_core
        XOR A
        DUP 7
        LD (HL),A
        INC H
        EDUP
        LD (HL),A
        LD A,(DE)
        AND $C0
        LD (DE),A
        JP $88CD
restore_colour_core:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD B,A
        LD A,(MODE)
        AND A
        JP Z,restore_done
        LD D,H
        LD E,L
        PUSH DE
        LD A,H
        AND $18
        RRCA
        RRCA
        RRCA
        ADD A,$78
        LD D,A
        LD A,B
        AND A
        JR Z,restore_empty
        LD A,(DE)
        BIT 7,A
        JR Z,restore_uniform
        LD C,A
        LD A,D
        ADD A,9
        LD D,A
        LD A,(DE)
        BIT 6,A
        JR NZ,restore_terrain_token
        AND $80
        PUSH AF
        LD A,C
        AND $7F
        CALL cached_row
        POP AF
        LD C,A
        POP DE
        SET 5,D
        LD A,C
        AND A
        JR NZ,restore_reverse
        DUP 8
        LD A,(HL)
        LD (DE),A
        INC HL
        INC D
        EDUP
        JR restore_done
restore_reverse:
        LD A,D
        ADD A,7
        LD D,A
        DUP 8
        LD A,(HL)
        LD (DE),A
        INC HL
        DEC D
        EDUP
        JR restore_done
restore_terrain_token:
        LD A,C
        POP DE
        CALL $0F00
        JP restore_done
restore_empty:
        LD A,D
        SUB $20
        LD D,A
        LD A,(DE)
        OR A
        JP P,restore_empty_native
        LD A,$47
restore_empty_native:
        AND $47
        JR restore_uniform
restore_uniform:
        AND $7F
        POP DE
        SET 5,D
        DUP 8
        LD (DE),A
        INC D
        EDUP
restore_done:
        POP HL
        POP DE
        POP BC
        POP AF
        RET
mark_dirty:
        LD A,(DE)
        AND $C0
        OR 1
        LD (DE),A
        LD A,1
        RET
test_dirty:
        LD A,(DE)
        AND 1
        JP Z,$88CD
        JP restore_empty_pixels
star_dirty_guard:
        LD A,(BC)
        AND 1
        RET Z
        INC SP
        INC SP
        RET
star_neighbor_dirty:
        LD A,(BC)
        DEC C
        AND 1
        RET

copy_front_colour_row:
        LD BC,30
        PUSH AF
        LD A,(MODE)
        AND A
        JR NZ,copy_front_tokens
        POP AF
        LDDR
        JP $8859
copy_front_tokens:
        PUSH IX
        PUSH IY
        LD IXL,30
copy_front_token:
        LD A,(HL)
        BIT 7,A
        JR Z,copy_front_emit
        LD C,A
        PUSH HL
        LD A,H
        ADD A,9
        LD H,A
        BIT 6,(HL)
        POP HL
        LD A,C
        JR NZ,copy_front_emit
        PUSH HL
        AND $7F
        CALL cached_row
        LD A,(HL)
        POP HL
copy_front_emit:
        LD (DE),A
        DEC HL
        DEC DE
        DEC IXL
        JR NZ,copy_front_token
        POP IY
        POP IX
        POP AF
        LD BC,0
        JP $8859

scroll_background_colour:
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        LD IX,$8101
        LD IYL,20
scroll_flip_row:
        LD B,30
scroll_flip_cell:
        LD A,(IX+1)
        AND $C0
        LD C,A
        LD A,(IX+0)
        AND $3F
        OR C
        LD (IX+0),A
        INC IX
        DJNZ scroll_flip_cell
        INC IX
        INC IX
        DEC IYL
        JR NZ,scroll_flip_row
        POP IY
        POP IX
        POP HL
        POP DE
        POP BC
        POP AF
        LD DE,$7801
        RET
new_column_colour:
        CALL $09D0 ; apply cached incoming group mask to staging token
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD A,(MODE)
        AND A
        JR Z,column_done
        LD A,(HL)
        AND $80
        RRCA
        LD C,A
        LD A,(IX+3)
        ADD A,$29
        LD D,A
        LD E,(IX+0)
        LD A,(DE)
        AND $3F
        OR C
        LD (DE),A
        LD D,(IX+1)
        LD E,(IX+0)
        SET 5,D
        XOR A
        DUP 8
        LD (DE),A
        INC D
        EDUP
column_done:
        POP HL
        POP DE
        POP BC
        POP AF
        LD A,(HL)
        RET

skip_cell_one:
        CALL skip_index
        DUP 8
        INC HL
        EDUP
        JP $8D4C
skip_cell_two:
        CALL skip_index
        DUP 8
        INC HL
        EDUP
        JP $8DBA
skip_cell_three:
        CALL skip_index
        DUP 8
        INC HL
        EDUP
        JP $8E10
skip_cell_four:
        CALL skip_index
        DUP 8
        INC HL
        EDUP
        JP $8E6C
skip_index:
        PUSH AF
        LD A,H
        CP $20
        JR C,skip_index_done
        CP $40
        JR NC,skip_index_done
        INC HL
skip_index_done:
        POP AF
        RET

        DEFINE ROM_ONLY 1
MODE_SHADOW EQU MODE
        INCLUDE "src/terrain_live_colour.inc"
        INCLUDE "src/boss_colour_lookup.inc"
        INCLUDE "src/title_publish.inc"
        ASSERT $ <= $1A00
