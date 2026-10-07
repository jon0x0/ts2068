 INCLUDE "frontend-state.asm"
front_tick:
 call hud_tick
 ld a,(front_demo)
 or a
 jr z,front_live
 di
 call front_fire
 ei
 jp z,front_start
 ld a,255
 ld (invulnerable),a
 ld a,(game_status)
 or a
 jp nz,title_boot
 call front_messages
 call front_ai
 ld hl,(frames)
 ld de,3000
 or a
 sbc hl,de
 jr c,front_continue
 xor a
 ld (front_demo),a
 jp title_boot
front_live:
 ld bc,$fbfe
 in a,(c)
 bit 3,a
 jp z,start
 ld a,(game_status)
 or a
 jr nz,front_result
 xor a
 ld (front_finished),a
front_continue:
 or a
 ret
front_result:
 ld a,(front_finished)
 or a
 jp nz,front_result_wait
 inc a
 ld (front_finished),a
 ld a,(game_status)
 cp 1
 call z,front_victory
 ld hl,(frames)
 ld (front_end_tick),hl
 ld hl,0
 ld (front_entry),hl
 ld (front_entry_two),hl
 call hud_score
 ld (front_score),hl
 ld ix,front_scores
 call front_insert
 ld hl,(front_entry)
 ld (front_entry_two),hl
 ld hl,0
 ld (front_entry),hl
 ld hl,(front_score)
 ld ix,front_today_scores
 call front_insert
 jp front_result_wait
 ; Shared live/final score, in five-point units.
hud_score:
 ld hl,0
 ld a,($5c24)
 ld de,30
 call front_add
 ld a,(crystals_taken)
 ld de,40
 call front_add
 ld a,(bs_hits)
 cp 13
 jr c,front_parts
 ld de,3000
 add hl,de
 ld a,12
front_parts:
 ld de,100
 call front_add
 ret
front_insert:
 ld a,1
 ld ($7bf4),a
 ld ($7bf5),a
 ld ($7bf6),a
 ld b,30
front_rank:
 ld e,(ix+0)
 ld d,(ix+1)
 or a
 sbc hl,de
 add hl,de
 jr z,front_rank_next
 jr c,front_rank_next
 push hl
 ld hl,(front_entry)
 ld a,h
 or l
 jr nz,front_rank_named
 push ix
 pop hl
 inc hl
 inc hl
 ld (front_entry),hl
front_rank_named:
 pop hl
 ld (ix+0),l
 ld (ix+1),h
 ex de,hl
 push hl
 push bc
 push ix
 pop de
 inc de
 inc de
 ld hl,$7bf4
 ld b,3
front_swap_name:
 ld a,(de)
 ld c,(hl)
 ld (hl),a
 ld a,c
 ld (de),a
 inc hl
 inc de
 djnz front_swap_name
 pop bc
 pop hl
front_rank_next:
 inc ix
 inc ix
 inc ix
 inc ix
 inc ix
 djnz front_rank
 ret
front_result_wait:
 ld hl,(frames)
 ld de,(front_end_tick)
 or a
 sbc hl,de
 ld de,180
 sbc hl,de
 jp nc,title_boot
 or a
 ret
front_add:
 or a
 ret z
 ld b,a
front_add_loop:
 add hl,de
 djnz front_add_loop
 ret

; Entered by the original title after drawing, interrupts disabled, SP=BFFF.
; ROM3+4+7 visible. All font and title pixels retain their original artwork.
front_start:
 xor a
 ld (front_demo),a
 jp start
front_wait:
 push hl
 call front_fire
 pop hl
 jp z,front_start
 ; ~one native refresh, independent of the gameplay interrupt clock.
 ld bc,2230
front_delay:
 dec bc
 ld a,b
 or c
 jr nz,front_delay
 dec hl
 ld a,h
 or l
 jr nz,front_wait
 ret
front_fire:
 call front_sound_key
 ld bc,$7ffe
 in a,(c)
 and 1
 ret z
 ld b,$bf
 in a,(c)
 and 1
 ret z
 ld a,14
 out ($f5),a
 ld bc,$01f6
 in a,(c)
 and $80
 ret
front_table:
 call front_clear
 jr front_table_text
front_clear:
 ld hl,$4000
 ld de,$4001
 ld bc,6143
 ld (hl),0
 ldir
 ld hl,$6000
 ld de,$6001
 ld bc,6143
 ld a,$90
 out ($f4),a
 ld (hl),7
 ldir
 ld a,$98
 out ($f4),a
 ld a,7
 ld ($5e7e),a
 ret
front_table_text:
 ld a,2
 ld ($5e7e),a
 ld hl,front_hero
 ld bc,8*256+172
 call front_text
 ld hl,front_heading
 ld bc,24*256+100
 call front_text
 ld hl,front_today
 ld bc,104*256+96
 call front_text
 ld a,6
 ld ($5e7e),a
 ld ix,front_scores
 ld bc,32*256+8
 call front_rows
 ld ix,front_today_scores
 ld bc,116*256+8
 call front_rows
 ld a,7
 ld ($5e7e),a
 ld ix,front_scores
 ld bc,8*256+128
 call front_name_fields
 ld bc,8*256+80
 jp front_number
front_rows:
 ld a,30
front_row:
 push af
 push bc
 ld e,a
 ld a,31
 sub e
 ld d,27
front_rank_tens:
 cp 10
 jr c,front_rank_units
 sub 10
 inc d
 jr front_rank_tens
front_rank_units:
 add a,27
 push af
 push bc
 ld a,d
 call front_char
 pop bc
 pop af
 inc c
 inc c
 inc c
 inc c
 push bc
 call front_char
 pop bc
 ld a,c
 add a,4
 ld c,a
 push bc
 ld a,39
 call front_char
 pop bc
 ld a,c
 add a,6
 ld c,a
 call front_name_fields
 ld a,c
 add a,12
 ld c,a
 call front_number
 ld de,5
 add ix,de
 pop bc
 pop af
 dec a
 ret z
 ld d,a
 cp 20
 jr z,front_column
 cp 10
 jr z,front_column
 ld a,b
 add a,7
 ld b,a
 ld a,d
 jr front_row
front_column:
 ld a,b
 sub 63
 ld b,a
 ld a,c
 add a,84
 ld c,a
 ld a,d
 jr front_row
front_name_fields:
 push bc
 ld a,(ix+2)
 call front_char
 pop bc
 ld a,c
 add a,6
 ld c,a
 push bc
 ld a,(ix+3)
 call front_char
 pop bc
 ld a,c
 add a,6
 ld c,a
 push bc
 ld a,(ix+4)
 call front_char
 pop bc
 ret
front_number:
 xor a
 ld ($5e69),a
 ld l,(ix+0)
 ld h,(ix+1)
 ld iy,front_divisors
 ld d,5
front_digit:
 push de
 ld e,(iy+0)
 ld d,(iy+1)
 ld a,26
front_subtract:
 inc a
 or a
 sbc hl,de
 jr nc,front_subtract
 add hl,de
 cp 27
 jr nz,front_significant
 ld a,($5e69)
 or a
 ld a,27
 jr nz,front_significant
 xor a
 jr front_number_draw
front_significant:
 push af
 ld a,1
 ld ($5e69),a
 pop af
front_number_draw:
 push hl
 push bc
 call front_char
 pop bc
 pop hl
 ld a,c
 add a,4
 ld c,a
 inc iy
 inc iy
 pop de
 dec d
 jr nz,front_digit
 ld a,l
 add a,a
 add a,a
 add a,l
 add a,27
 jp front_char
front_divisors:
 DW 20000,2000,200,20,2
front_text:
 ld a,(hl)
 inc hl
 cp 255
 ret z
 push hl
 push bc
 push af
 call front_char
 pop af
 pop bc
 pop hl
 ld d,4
 cp 13
 jr z,front_wide
 cp 23
 jr nz,front_advance
front_wide:
 ld d,6
front_advance:
 ld a,c
 add a,d
 ld c,a
 jr front_text
front_char:
 ld l,a
 ld h,0
 ld e,l
 ld d,h
 add hl,hl
 add hl,de
 ld de,front_font+16
 add hl,de
 ex de,hl
 ld a,6
front_glyph_row:
 push af
 ld a,(de)
 pop hl
 push hl
 bit 0,h
 jr z,front_glyph_low
 rrca
 rrca
 rrca
 rrca
 inc de
front_glyph_low:
 and 15
 ld l,a
 ld h,0
 push de
 ld de,front_font
 add hl,de
 ld a,(hl)
 ld ($5e68),a
 push bc
 ld a,c
 and 7
 ld e,$80
 jr z,front_mask_ready
front_mask_shift:
 srl e
 dec a
 jr nz,front_mask_shift
front_mask_ready:
 srl c
 srl c
 srl c
 call offset
 set 6,h
 ld d,5
front_cell_attr:
 set 5,h
 ld a,$90
 out ($f4),a
 ld a,($5e7e)
 ld (hl),a
 ld a,$98
 out ($f4),a
 res 5,h
front_pixel:
 ld a,($5e68)
 add a,a
 ld ($5e68),a
 ld a,e
 jr c,front_pixel_on
 cpl
 and (hl)
 jr front_pixel_store
front_pixel_on:
 or (hl)
front_pixel_store:
 ld (hl),a
 rrc e
 jr nc,front_pixel_next
 inc l
 dec d
 jr nz,front_cell_attr
 jr front_row_done
front_pixel_next:
 dec d
 jr nz,front_pixel
front_row_done:
 pop bc
 pop de
 inc b
 pop af
 dec a
 jr nz,front_glyph_row
 ret

front_help:
 ret ; obsolete standalone help page; attract uses front_help_draw
front_help_draw:
front_help_line:
 ld a,(hl)
 inc hl
 cp 255
 ret z
 ld c,a
 ld b,(hl)
 inc hl
 ld a,(hl)
 inc hl
 ld ($5e7e),a
 push bc
 call front_text
 pop bc
 jr front_help_line


 INCLUDE "attract-ai.asm"

front_seed:
 xor a
 ld ($5e6e),a
 ld ($5e6f),a
 ld hl,front_seed_data
 ld de,front_scores
 ld bc,150
 ldir
 ld hl,front_scores
 ld de,front_today_scores
 ld bc,150
 ldir
 ld ix,front_today_scores
 ld b,30
front_seed_today:
 ld l,(ix+0)
 ld h,(ix+1)
 ld de,4000
 or a
 sbc hl,de
 ld (ix+0),l
 ld (ix+1),h
 ld de,5
 add ix,de
 djnz front_seed_today
 ret

front_seed_data:
 INCBIN "../build/frontend-seeds.bin"

; Attract messages share the unused band between scanner and playfield.
; ROM3 fonts are mapped only with IRQs disabled and a temporary HOME5 stack.
front_messages:
 ld hl,(frames)
 ld a,h
 or l
 jr nz,front_message_time
 ld a,255
 ld ($7bf8),a
front_message_time:
 ld de,600
 xor a
front_message_phase:
 or a
 sbc hl,de
 jr c,front_message_select
 inc a
 cp 2
 jr c,front_message_phase
front_message_select:
 ld hl,$7bf8
 cp (hl)
 ret z
 ld (hl),a
 ld hl,front_mining_help
 or a
 jr z,front_message_map
 ld hl,front_firing_help
 dec a
 jr z,front_message_map
 ld hl,front_sinistar_help
front_message_map:
 di
 ld ($5e6c),sp
 ld sp,$bfff
 ld a,$98
 out ($f4),a
 push hl
 ld bc,24*256
front_message_clear:
 push bc
 call offset
 set 6,h
 ld d,h
 ld e,l
 inc de
 ld bc,31
 ld (hl),0
 ldir
 pop bc
 inc b
 ld a,b
 cp 63
 jr nz,front_message_clear
 pop hl
 call front_help_draw
 ld a,7
 ld ($5e7e),a
 ld hl,front_prompt
 ld bc,56*256+88
 call front_text
 ld a,$d0
 out ($f4),a
 ld sp,($5e6c)
 call hud_divider
 ei
 ret

; S is active-low bit 1 on the ASDFG keyboard row. Persist across games.
front_sound_key:
 ld bc,$fdfe
 in a,(c)
 and 2
 ld hl,$5e6f
 jr z,front_sound_pressed
 ld (hl),0
 ret
front_sound_pressed:
 ld a,(hl)
 or a
 ret nz
 inc (hl)
 ld a,($5e6e)
 xor 1
 ld ($5e6e),a
 ret
front_audio:
 call front_sound_key
 ld a,($5e6e)
 ld hl,front_demo
 or (hl)
 ret z
 ; NEWTUNE.SRC rejects non-coin sounds during AMDEMO. Drop requests so
 ; muting cannot accumulate a speech/SFX backlog to play after unmuting.
 xor a
 ld (speech_pending),a
 ld (speech_left),a
 ld (speech_active),a
 ld ($5860),a
 ld ($5861),a
 ld ($5862),a
 ld ($7f53),a
 ld ($5c3d),a
 ld a,(sinistar_built)
 ld (speech_started),a
 xor a
 ld e,8
 call speech_silence
 scf
 ret
 INCLUDE "hud.asm"
; Original STATUS.SRC wording and white ink, centered in the reserved band.
front_victory:
 di
 ld ($5e6c),sp
 ld sp,$bfff
 ld a,$98
 out ($f4),a
 ld a,7
 ld ($5e7e),a
 ld hl,front_congratulations
 ld bc,24*256+98
 call front_text
 ld hl,front_defeated
 ld bc,40*256+78
 call front_text
 ld a,$d0
 out ($f4),a
 ld sp,($5e6c)
 ei
 ret
front_congratulations:
 DB 3,15,14,7,18,1,20,21,12,1,20,9,15,14,19,255
front_defeated:
 DB 25,15,21,0,4,5,6,5,1,20,5,4,0,20,8,5,0,19,9,14,9,19,20,1,18,255
