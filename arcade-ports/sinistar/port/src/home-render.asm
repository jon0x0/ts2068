; Boot-copied helpers in unused tail of HOME rock cache (A690-A7FF).
 INCLUDE "../build/home-render-equ.asm"
 ORG $a690
 jp hp_prepare
 jp hp_clear
 jp hp_draw
 jp hp_cover_player
 jp hp_face_identity
hp_prepare:
 ld a,($5bcd)
 ld ($5bca),a
 xor a
 ld ($5bcd),a
 ld ($5bce),a
 ld a,(game_mode)
 or a
 ret z
 call wb_pop_begin
 xor a
 ld ($58f4),a
wpp_prepare:
 ; Hidden objects still require one final old-image erase. Set the flag
 ; once; visible, unchanged projections may clear it below.
 ld a,($58f4)
 add a,$a0
 ld l,a
 ld h,$5b
 ld (hl),1
 ld a,($58f4)
 call wp_calc
 ld a,(rects+2)
 or a
 jr nz,hp_visible
 ld a,($58f4)
 call wp_cache
 inc hl
 inc hl
 ld (hl),0
 jr wpp_cache_done
hp_visible:
 ; Retain an aggregate for the next picture's final disappearance erase.
 ld ($5bca),a
 ld ($5bcd),a
 ld a,($58f4)
 call wp_cache
 ex de,hl
 ld hl,rects
 ld bc,4
 ldir
 ld hl,$7cd0
 ld bc,4
 ldir
 ld a,($58f0)
 ld (de),a
hp_flag:
 ; DE already points to the final byte of the freshly copied projection.
 ; Reuse it instead of looking up the cache address and visibility again.
 ex de,hl
 ld de,-8
 add hl,de
 push hl
 ld de,$bc80-$5b00
 or a
 sbc hl,de
 ex de,hl
 pop hl
 ld b,9
 ld c,0
wpp_cache_compare:
 ld a,(de)
 xor (hl)
 or c
 ld c,a
 ld a,(hl)
 ld (de),a
 inc hl
 inc de
 djnz wpp_cache_compare
 ld a,($58f4)
 push bc
 call wp_old
 inc hl
 inc hl
 ld a,(hl)
 pop bc
 or a
 ld a,1
 jr z,wpp_cache_flag
 ld a,c
wpp_cache_flag:
 ld c,a
 ld a,($58f4)
 ld l,a
 ld h,$5b
 ld a,l
 add a,$a0
 ld l,a
 ld (hl),c
wpp_cache_done:
 ld hl,$58f4
 inc (hl)
 ld a,(hl)
 cp 17
 jp c,wpp_prepare
 jp wb_pop_finish
hp_clear:
 ld a,($5bca)
 or a
 ret z
 ld hl,world_extension+75
 call world_call
pc_loop:
 ld hl,world_extension+78
 call world_call
 jr c,population_end
 ld a,($58f1)
 dec a
 srl a
 add a,$a0
 ld l,a
 ld h,$5b
 ld a,(hl)
 or a
 jr z,pc_loop
 ld a,($58f1)
 and 1
 jr nz,pc_erase
 call mark_object
 jr pc_loop
pc_erase:
 call clear_object
 jr pc_loop
hp_draw:
 ld a,($5bca)
 or a
 ret z
 ld hl,world_extension+75
 call world_call
pd_loop:
 ld hl,world_extension+81
 call world_call
 jr c,population_end
 jr z,pd_loop
 push hl
 ld a,($58f1)
 dec a
 add a,$a0
 ld l,a
 ld h,$5b
 ld a,(hl)
 ld ($78e4),a
 pop hl
 call draw_rock
 jr pd_loop
population_end:
 ld hl,world_extension+84
 jp world_call

; Optional experiment, enabled only by profiler/test at 5BCB.
; A whole 8x1 rectangle must be covered. Partial overlap keeps normal layering.
hp_cover_player:
 ld a,($5bcb)
 and 1
 ret z
 ld a,(awake_done)
 or a
 ret z
 ld a,(rects+22)
 cp 7
 ret nz
 ld a,(rects+23)
 cp 52
 ret nz
 ld hl,rects+20
 ld a,(rects+12)
 sub (hl)
 ret c
 cp 5
 ret nc
 inc hl
 ld a,(rects+13)
 sub (hl)
 ret c
 cp 41
 ret nc
 xor a
 ld (rects+14),a
 ret
hp_face_identity:
 ld a,(speech_pending)
 or a
 ret nz
 ld a,(speech_left)
 or a
 ret nz
 ld a,(awake_mouth)
 ld hl,awake_previous
 or (hl)
 ret nz
 ld a,(eye_phase)
 ld hl,eye_previous
 xor (hl)
 ld ($5bcc),a
 xor a
 ret
 ASSERT $ <= $a800
