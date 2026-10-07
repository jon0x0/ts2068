 INCLUDE "../build/world-equ.asm"
 INCLUDE "../build/frontend-title-equ.asm"
 INCLUDE "../build/frontend-world-equ.asm"
 ORG effects_origin
 jp ring_effect
 jp mode_filter
 jp fx_bounce
 jp fx_explosion
 jp front_tick
 jp front_title
 jp front_wait
 jp front_table
 jp front_clear
 jp front_start
 jp front_char
 jp front_fire
 jp front_text
 jp front_seed
 jp front_audio

 ; Stage the impact sprite only. No HALT, live-screen writes or effect delay.
ring_effect:
ring_red:
 ld a,($783c)
 and 7
 ld c,a
 ld a,($783e)
 dec a
 and 3
 xor 3
 jp fx_arcade_explosion

; Enter from DOCK2; switch HOME2 in only while executing DOCK7.
; $5bb1 enabled, $5bb2 active, $5bb3 F latch, $5bb4 saved primary
; mass, $5bb5..5bc5 saved secondary masses. Zero means not retired.
mode_filter:
 ld a,$90
 ld ($78df),a
 out ($f4),a
 ld bc,$fdfe
 in a,(c)
 and 8
 ld hl,$5bb3
 jr nz,mode_release
 ld a,(hl)
 or a
 jr nz,mode_desired
 inc (hl)
 ld a,($5bb1)
 xor 1
 ld ($5bb1),a
 xor a
 ld ($5c2d),a
 ld a,2
 ld ($5bc6),a
 jr mode_desired
mode_release:
 ld (hl),0
mode_desired:
 call mode_bounce_key
 call mode_notice
 ld a,($5bb1)
 or a
 jp z,mode_restore
 ld a,(game_status)
 or a
 jp nz,mode_restore
 ld a,(bs_hits)
 cp 13
 jp nc,mode_restore
 ; Refill suppression applies only after awakening. Before then, capped
 ; secondary slots recycle through ordinary far-sector replenishment.
 ld a,(awake_done)
 ld ($5bb2),a
 xor a
 ld ($5bc9),a
 ld a,(rects+2)
 or a
 jr z,mode_primary_hidden
 ld a,1
 ld ($5bc9),a
 jr mode_secondaries
mode_primary_hidden:
 ld a,(awake_done)
 or a
 jr z,mode_secondaries
 ld a,(rock_alive)
 or a
 jr z,mode_secondaries
 ld a,(mass)
 ld ($5bb4),a
 xor a
 ld (rock_alive),a
mode_secondaries:
 ld iy,mode_records
 ld ix,$bc80
 ld hl,$5bb5
 ld b,17
mode_retire_loop:
 ld e,(iy+0)
 ld d,(iy+1)
 ld a,(ix+2)
 or a
 jr z,mode_hidden
 ld a,($5bc9)
 cp 2
 jr nc,mode_retire
 inc a
 ld ($5bc9),a
 jr mode_retire_next
mode_hidden:
 ld a,(awake_done)
 or a
 jr z,mode_retire_next
mode_retire:
 ld a,(de)
 or a
 jr z,mode_retire_next
 ld (hl),a
 ld a,($5bb2)
 or a
 jr nz,mode_save_retired
 ld (hl),0
mode_save_retired:
 xor a
 ld (de),a
 ld (ix+2),a
 push hl
 ld a,17
 sub b
 add a,$a0
 ld l,a
 ld h,$5b
 ld (hl),1
 pop hl
mode_retire_next:
 inc hl
 inc iy
 inc iy
 ld de,9
 add ix,de
 djnz mode_retire_loop
 jr mode_exit
mode_restore:
 ld a,($5bb2)
 or a
 jr z,mode_exit
 xor a
 ld ($5bb2),a
 ld a,($5bb4)
 or a
 jp z,mode_restore_others
 ld (mass),a
 ld a,1
 ld (rock_alive),a
 xor a
 ld ($5bb4),a
mode_restore_others:
 ld iy,mode_records
 ld hl,$5bb5
 ld b,17
mode_restore_loop:
 ld e,(iy+0)
 ld d,(iy+1)
 ld a,(hl)
 or a
 jp z,mode_restore_next
 ld (de),a
 ld (hl),0
mode_restore_next:
 inc hl
 inc iy
 inc iy
 djnz mode_restore_loop
mode_exit:
 ld a,$94
 ld ($78df),a
 out ($f4),a
 ret
mode_notice:
 ld a,($5bc6)
 or a
 ret z
 cp 2
 jr z,mode_notice_new
 ld a,($5bc7)
 ld b,a
 ld a,($7802)
 sub b
 cp 90
 ret c
 xor a
 ld ($5bc6),a
 ld hl,mode_on_text ; Clearing does not read a text bitmap.
 jr mode_notice_draw
mode_notice_new:
 ld a,($7802)
 ld ($5bc7),a
 ld a,1
 ld ($5bc6),a
 ld a,($5c2d)
 or a
 jr z,mode_notice_fast
 ld hl,mode_bounce_on
 ld a,($5c2b)
 or a
 jr z,mode_notice_draw
 ld hl,mode_bounce_off
 jr mode_notice_draw
mode_notice_fast:
 ld hl,mode_on_text
 ld a,($5bb1)
 or a
 jr nz,mode_notice_draw
 ld hl,mode_off_text
mode_notice_draw:
 ld a,52
 ld ($5bc8),a
mode_notice_row:
 push hl
 ld a,($5bc8)
 ld b,a
 ld c,9
 call offset
 set 6,h
 ex de,hl
 pop hl
 ld bc,13
 ld a,($5bc6)
 or a
 jr nz,mode_notice_copy
 ld b,c
mode_notice_clear:
 ld (de),a
 inc de
 djnz mode_notice_clear
 jr mode_notice_copied
mode_notice_copy:
 ld b,13
mode_nibble:
 ld a,(hl)
 bit 0,b
 jr z,mode_low_nibble
 rrca
 rrca
 rrca
 rrca
 jr mode_lookup
mode_low_nibble:
 inc hl
mode_lookup:
 and 15
 push hl
 push bc
 ld l,a
 ld h,0
 ld bc,mode_byte_table
 add hl,bc
 ld a,(hl)
 ld (de),a
 pop bc
 pop hl
 inc de
 djnz mode_nibble
 inc hl
mode_notice_copied:
 push hl
 ex de,hl
 ld de,-13
 add hl,de
 set 5,h
 ld a,7
mode_notice_color:
 ld b,13
mode_notice_attr:
 ld (hl),a
 inc l
 djnz mode_notice_attr
 pop hl
 ld a,($5bc8)
 inc a
 ld ($5bc8),a
 cp 59
 jr nz,mode_notice_row
 ret
; C is row FE, bit 3. One toggle per press, independent of F's latch.
; HOME 5C2B disabled, 5C2C C latch, 5C2D notice kind. Boot clears all.
mode_bounce_key:
 ld bc,$fefe
 in a,(c)
 and 8
 ld hl,$5c2c
 jr nz,mode_bounce_release
 ld a,(hl)
 or a
 ret nz
 inc (hl)
 ld a,($5c2b)
 xor 1
 ld ($5c2b),a
 xor a
 ld ($5c25),a ; Do not leave thrust locked out after disabling contact.
 inc a
 ld ($5c2d),a
 inc a
 ld ($5bc6),a
 ret
mode_bounce_release:
 ld (hl),0
 ret
 INCLUDE "../build/mode-notice.asm"
mode_records:
 DW $79b7,$79c1,$79cb,$79d5,$79df,$79e9,$79f3,$79fd
 DW $7db7,$7dc1,$7dcb,$7dd5,$7ddf,$7de9,$7df3,$7dfd,$58bb
 INCLUDE "gameplay-effects.asm"
 INCLUDE "frontend.asm"
