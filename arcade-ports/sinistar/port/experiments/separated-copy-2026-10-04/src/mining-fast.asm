; Disjoint face bitmap path. Attributes retain the sparse changed-byte list.
; Scratch at HOME 5800 (outside both ECM planes).
fast_select:
 xor a
 ld ($78f6),a
 ld a,(awake_done)
 or a
 ret z
 ld a,(rects+22)
 ld hl,oldrects+22
 and (hl)
 cp 7
 ret nz
 ld hl,rects+20
 ld de,oldrects+20
 ld ix,$5800
 ld b,2
fs_bounds:
 ld a,(de)
 cp (hl)
 jr c,fs_min
 ld a,(hl)
fs_min:
 ld (ix+0),a
 ld a,(de)
 cp (hl)
 jr nc,fs_max
 ld a,(hl)
fs_max:
 ld c,7
 bit 0,b
 jr z,fs_size
 ld c,52
fs_size:
 add a,c
 ld (ix+1),a
 inc hl
 inc de
 inc ix
 inc ix
 djnz fs_bounds
 ld a,($5801)
 ld hl,$5800
 sub (hl)
 cp 9
 ret nc
 ld ($5804),a
 ld a,($5803)
 ld hl,$5802
 sub (hl)
 cp 55
 ret nc
 ld ($5805),a
 ; Test every other old/new ECM rectangle against the combined envelope.
 ld iy,rects
 call fs_objects
 ret nz
 ld iy,oldrects
 call fs_objects
 ret nz
 ld a,1
 ld ($78f6),a
 ret
fs_objects:
 ld b,7
fs_object:
 ld a,b
 cp 2
 jr z,fs_next
 ld a,(iy+2)
 or a
 jr z,fs_next
 ld c,a
 ld a,($5801)
 cp (iy+0)
 jr c,fs_next
 jr z,fs_next
 ld a,(iy+0)
 add a,c
 ld hl,$5800
 cp (hl)
 jr c,fs_next
 jr z,fs_next
 ld a,($5803)
 cp (iy+1)
 jr c,fs_next
 jr z,fs_next
 ld a,(iy+1)
 add a,(iy+3)
 ld hl,$5802
 cp (hl)
 jr c,fs_next
 jr z,fs_next
 ld a,1
 or a
 ret
fs_next:
 ld de,4
 add iy,de
 djnz fs_object
 xor a
 ret

compile_bitmap:
 ; Main BC is disposable here; caller saves scanline/column and pointers.
 ld a,($78f6)
 or a
 jp z,compile_span
 ld a,($5802)
 ld c,a
 ; Recover linear Y from the bitmap address.
 ld a,h
 and 7
 ld ($5807),a
 ld a,h
 and 24
 rlca
 rlca
 rlca
 ld c,a
 ld a,l
 and $e0
 rrca
 rrca
 or c
 ld c,a
 ld a,($5807)
 or c
 ld c,a
 ld a,($5802)
 cp c
 jp z,cb_inside
 jp nc,compile_span
cb_inside:
 ld a,($5803)
 cp c
 jp c,compile_span
 jp z,compile_span
 ; Split once per row, rather than testing every byte against the face.
 ld a,l
 and 31
 ld c,a
 add a,b
 ld ($5808),a
 ld a,($5800)
 sub c
 jr c,cb_skip
 jr z,cb_skip
 cp b
 jp nc,compile_span
 ld b,a
 call compile_span
cb_skip:
 ld a,l
 and 31
 ld c,a
 ld a,($5801)
 cp c
 jr nc,cb_use_right
 ld a,c
cb_use_right:
 ld c,a
 ld a,($5808)
 sub c
 ret c
 ret z
 ld b,a
 ld a,l
 and $e0
 or c
 ld l,a
 ld e,a
 jp compile_span

fast_publish:
 ld a,($78f6)
 or a
 ret z
 ld ix,fast_seven
 ld a,($5804)
 cp 8
 jr nz,fp_kernel
 ld ix,fast_cells
fp_kernel:
 ld a,($5802)
 ld b,a
 ld a,($5800)
 ld c,a
 ld a,($5805)
 ld ($5806),a
fast_row:
 call offset
 ld a,h
 or $40
 ld h,a
 xor $e0
 ld d,a
 ld e,l
 push bc
 call fast_dispatch
 pop bc
 inc b
 ld hl,$5806
 dec (hl)
 jr nz,fast_row
 ret
fast_dispatch:
 jp (ix)
fast_cells:
 ld a,(de)
 cp (hl)
 jr z,fc_eight_same
 ld (hl),a
fc_eight_same:
 inc l
 inc e
fast_seven:
 ld a,(de)
 cp (hl)
 jr z,fc_same_0
 ld (hl),a
fc_same_0:
 inc l
 inc e
 ld a,(de)
 cp (hl)
 jr z,fc_same_1
 ld (hl),a
fc_same_1:
 inc l
 inc e
 ld a,(de)
 cp (hl)
 jr z,fc_same_2
 ld (hl),a
fc_same_2:
 inc l
 inc e
 ld a,(de)
 cp (hl)
 jr z,fc_same_3
 ld (hl),a
fc_same_3:
 inc l
 inc e
 ld a,(de)
 cp (hl)
 jr z,fc_same_4
 ld (hl),a
fc_same_4:
 inc l
 inc e
 ld a,(de)
 cp (hl)
 jr z,fc_same_5
 ld (hl),a
fc_same_5:
 inc l
 inc e
 ld a,(de)
 cp (hl)
 jr z,fc_same_6
 ld (hl),a
fc_same_6:
 inc l
 inc e
 ret

; Only exposed edges of the old face require restoration. Its new rectangle
; is overwritten by the complete atlas blit before other objects are composed.
fast_clear_old:
 call mark_object
 ld b,(iy+1)
 ld c,(iy+0)
 ld a,52
 ld ($5809),a
fco_row:
 push bc
 ld e,7
 ld a,(rects+21)
 cp b
 jr z,fco_inside
 jr nc,fco_clear
fco_inside:
 add a,52
 cp b
 jr c,fco_clear
 jr z,fco_clear
 ld a,(rects+20)
 cp c
 jr z,fco_next
 ld e,1
 jr nc,fco_clear
 ; New face moved left: only the old rightmost cell remains exposed.
 ld a,c
 add a,6
 ld c,a
fco_clear:
 push de
 call offset
 ld a,h
 or $a0
 ld h,a
 xor $60
 ld d,a
 ld e,l
 pop bc
 ld b,c
 ld a,7
fco_cell:
 ld (hl),0
 ld (de),a
 inc l
 inc e
 djnz fco_cell
fco_next:
 pop bc
 inc b
 ld hl,$5809
 dec (hl)
 jr nz,fco_row
 ret
