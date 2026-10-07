 INCLUDE "frontend-state.asm"
front_wait EQU effects_origin+18
front_table EQU effects_origin+21
front_help EQU effects_origin+24
front_start EQU effects_origin+27
front_char EQU effects_origin+30
front_fire EQU effects_origin+33
front_text EQU effects_origin+36
front_title:
 ld hl,(front_magic)
 ld de,$534a
 or a
 sbc hl,de
 jr z,front_ready
 call effects_origin+39
 ld de,$534a
 ld (front_magic),de
 ld hl,0
 ld (front_entry),hl
front_ready:
 xor a
 ld (front_demo),a
 ; Silence any interrupted game-over sound before the idle title cycle.
 ld e,8
front_silence:
 ld a,e
 out ($f5),a
 xor a
 out ($f6),a
 inc e
 ld a,e
 cp 11
 jr nz,front_silence
 ld hl,(front_entry)
 ld a,h
 or l
 jp nz,front_initials
 ld hl,480
 call front_wait
 call front_table
 ld hl,480
 call front_wait
 ld a,1
 ld (front_demo),a
 jp start
front_initials:
 call front_help
 ld a,7
 ld ($5e7e),a
 ld hl,front_name_prompt
 ld bc,48*256+100
 call front_text
 ld hl,front_name_keys
 ld bc,128*256+82
 call front_text
 ld iy,(front_entry)
 ld c,88
front_name_draw:
 ld a,(iy+0)
 push bc
 call front_big_char
 pop bc
front_name_release:
 call front_name_key
 or a
 jr nz,front_name_release
front_name_press:
 call front_name_key
 or a
 jr z,front_name_press
 cp 3
 jr z,front_name_next
 ld b,a
 ld a,(iy+0)
 dec b
 jr nz,front_name_down
 inc a
 cp 27
 jr c,front_name_store
 ld a,1
 jr front_name_store
front_name_down:
 dec a
 jr nz,front_name_store
 ld a,26
front_name_store:
 ld (iy+0),a
 jr front_name_draw
front_name_next:
 inc iy
 ld a,c
 add a,32
 ld c,a
 cp 184
 jr z,front_name_complete
 ld a,(iy-1)
 ld (iy+0),a
 jr front_name_draw
front_name_complete:
 ld hl,(front_entry)
 ld de,(front_entry_two)
 ld a,d
 or e
 jr z,front_name_single
 ld bc,3
 ldir
front_name_single:
 ld hl,0
 ld (front_entry),hl
front_name_finish:
 call front_name_key
 or a
 jr nz,front_name_finish
 jp title_boot
front_name_key:
 push bc
 call front_fire
 ld a,3
 jr z,front_key_return
 in a,(c)
 cpl
 and 3
 cp 3
 jr z,front_keyboard_name
 or a
 jr nz,front_key_return
front_keyboard_name:
 ld bc,$dffe
 in a,(c)
 cpl
 and 3
 cp 3
 jr nz,front_key_return
 xor a
front_key_return:
 pop bc
 ret
; Render a temporary six-row glyph, then expand it 2x into a separate screen.
front_big_char:
 push bc
 ld bc,0
 call front_char
 pop bc
 srl c
 srl c
 srl c
 ld hl,$4000
 ld b,88
front_big_row:
 ld a,(hl)
 ld (hl),0
 inc h
 push hl
 push bc
 ld de,0
 ld b,8
front_big_bits:
 add a,a
 push af
 rl e
 rl d
 pop af
 rl e
 rl d
 djnz front_big_bits
 pop bc
 call front_big_line
 inc b
 call front_big_line
 inc b
 pop hl
 ld a,b
 cp 100
 jr nz,front_big_row
 ret
front_big_line:
 push de
 call offset
 set 6,h
 pop de
 ld (hl),d
 inc l
 ld (hl),e
 ret
 INCLUDE "../build/frontend-instructions.asm"
