 INCLUDE "../build/world-equ.asm"
 INCLUDE "../build/effects-origin.asm"
 ORG effects_origin
 jp ring_effect
 jp mode_filter

; ECM halo with a protected radius-40 center. Row descriptors DC80, original attributes B800.
; INK=PAPER makes each selected cell solid without touching bitmap pixels.
ring_effect:
 ld a,$94
 ld ($78df),a
 out ($f4),a
 ld a,($783e)
 or a
 jp z,mode_exit
 ld b,a
 xor a
 ld ($783e),a
 ld a,b
 cp 10
 jp z,mode_exit
 ld a,(oldrects+22)
 or a
 jp z,mode_exit
 ld a,(oldrects+23)
 or a
 jp z,mode_exit
 ld a,(face_oldx)
 ld l,a
 ld h,0
 ld a,(oldrects+20)
 or a
 jr nz,ring_x_positive
 bit 7,l
 jr z,ring_x_positive
 dec h
ring_x_positive:
 ld de,24
 add hl,de
 ld ($7be8),hl
 ld a,(face_oldy)
 ld l,a
 ld h,0
 ld a,(oldrects+21)
 cp 64
 jr nz,ring_y_positive
 bit 7,l
 jr z,ring_y_positive
 dec h
ring_y_positive:
 ld de,-23
 add hl,de
 ld ($7bea),hl
 ld hl,0
 ld ($7bec),hl
 ld ix,$b800
 ld iy,ring_spans
 ld a,99
 ld ($7bee),a
ring_prepare:
 ld hl,($7bea)
 ld a,h
 or a
 jp nz,ring_next
 ld a,l
 cp 64
 jp c,ring_next
 cp 176
 jp nc,ring_next
 ld b,l
 ld e,(iy+0)
 ld d,0
 ld hl,($7be8)
 or a
 sbc hl,de
 bit 7,h
 jr z,ring_left_ok
 ld hl,0
ring_left_ok:
 ld a,h
 or a
 jp nz,ring_next
 ld c,l
 srl c
 srl c
 srl c
 ld hl,($7be8)
 add hl,de
 dec hl
 bit 7,h
 jp nz,ring_next
 ld a,h
 or a
 jr z,ring_right_ok
 ld l,255
ring_right_ok:
 ld a,l
 srl a
 srl a
 srl a
 ld ($7bef),a
 ld a,(iy+1)
 cp 255
 jr z,ring_whole
 ld e,a
 ld d,0
 ld hl,($7be8)
 or a
 sbc hl,de
 bit 7,h
 jr nz,ring_right_span
 ld a,h
 or a
 ld a,32
 jr nz,ring_left_end
 ld a,l
 srl a
 srl a
 srl a
ring_left_end:
 sub 1
 jr c,ring_right_span
 call ring_store
ring_right_span:
 ld e,(iy+1)
 ld d,0
 ld hl,($7be8)
 add hl,de
 dec hl
 bit 7,h
 jr nz,ring_whole
 ld a,h
 or a
 jp nz,ring_next
 ld a,l
 srl a
 srl a
 srl a
 inc a
 ld c,a
ring_whole:
 ld a,($7bef)
 call ring_store
 jr ring_next
ring_store:
 sub c
 ret c
 inc a
 push bc
 ld b,a
ring_record:
 push bc
 ld a,c
 and 31
 add a,a
 add a,a
 add a,a
 ld l,a
 ld h,0
 ld de,($7be8)
 or a
 sbc hl,de
 bit 7,h
 jr nz,ring_distance_left
 inc l
 jr ring_distance
ring_distance_left:
 ld de,7
 add hl,de
 bit 7,h
 jr z,ring_distance_zero
 xor a
 sub l
 ld l,a
 jr ring_distance
ring_distance_zero:
 ld l,0
ring_distance:
 ld e,l
 ld a,($7bee)
 sub 50
 jr nc,ring_dy
 neg
ring_dy:
 ld d,a
 call render_extension+18
 ld (ix+3),a
 pop bc
 push bc
 ld a,($7bea)
 ld b,a
 call offset
 set 5,h
 set 6,h
 ld (ix+0),l
 ld (ix+1),h
 ld a,(hl)
 ld (ix+2),a
 ld de,4
 add ix,de
 ld hl,($7bec)
 inc hl
 ld ($7bec),hl
 pop bc
 inc c
 djnz ring_record
 pop bc
 ret
ring_next:
 inc iy
 inc iy
 ld hl,($7bea)
 inc hl
 ld ($7bea),hl
 ld hl,$7bee
 dec (hl)
 jp nz,ring_prepare
 ld hl,($7bec)
 ld a,h
 or l
 jp z,mode_exit
 halt
 ld a,1
 ld ($783c),a
 ld de,$003f
 call ring_fill
ring_gray:
 halt
 ld de,$0176
 call ring_fill
ring_yellow:
 halt
 ld de,$0252
 call ring_fill
ring_red:
 halt
 ld de,$037f
 call ring_fill
ring_white:
 halt
ring_restore:
 ld ix,$b800
 ld bc,($7bec)
ring_restore_loop:
 ld l,(ix+0)
 ld h,(ix+1)
 ld a,(ix+2)
 ld (hl),a
 inc ix
 inc ix
 inc ix
 inc ix
 dec bc
 ld a,b
 or c
 jr nz,ring_restore_loop
 xor a
 ld ($783c),a
ring_done:
 jp mode_exit
ring_fill:
 jp render_extension+21

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
 ld a,2
 ld ($5bc6),a
 jr mode_desired
mode_release:
 ld (hl),0
mode_desired:
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
 ld hl,mode_blank
 jr mode_notice_draw
mode_notice_new:
 ld a,($7802)
 ld ($5bc7),a
 ld a,1
 ld ($5bc6),a
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
 ldir
 push hl
 ex de,hl
 ld de,-13
 add hl,de
 set 5,h
 ld a,($5bc6)
 or a
 ld a,7
 jr z,mode_notice_color
 ld a,71
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
 INCLUDE "../build/mode-notice.asm"
mode_records:
 DW $79b7,$79c1,$79cb,$79d5,$79df,$79e9,$79f3,$79fd
 DW $7db7,$7dc1,$7dcb,$7dd5,$7ddf,$7de9,$7df3,$7dfd,$58bb
 INCLUDE "../build/ring-points.asm"
