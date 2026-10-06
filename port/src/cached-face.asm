inc_cached_face:
 ld a,($7ba1)
 or a
 jr z,face_normal
 ld hl,render_extension+6
 jp incremental_call
face_normal:
 ld a,(rects+22)
 or a
 ret z
 cp 7
 jp nz,face_clipped
 ld a,(rects+23)
 cp 52
 jp nz,face_clipped
 ; The face is the bottom layer over black. Write its complete rectangle in
 ; shadow RAM; later sprites still use masks and retain their overlap order.
 ld ($78e0),a
 push de
 pop ix
face_row:
 call offset
 ld a,h
 or $a0
 ld h,a
 push bc
 ld e,(ix+0)
 ld d,(ix+1)
 inc ix
 inc ix
 inc de
 ex de,hl
 push de
 DUP 7
 ldi
 EDUP
 ; Shared dictionary rows have a blank byte on each side of each plane.
 inc hl
 inc hl
 pop de
 ld a,d
 xor $60
 ld d,a
 DUP 7
 ldi
 EDUP
 pop bc
 inc b
 ld a,($78e0)
 dec a
 ld ($78e0),a
 jp nz,face_row
 ret
face_clipped:
 ; Pre-shifted atlas rows retain the normal fast path when fully visible.
 ld a,($7ce4)
 add a,a
 ld l,a
 ld h,0
 add hl,de
 push hl
 pop ix
 ld a,(rects+23)
 ld ($78e0),a
fc_row:
 call offset
 ld a,h
 or $a0
 ld h,a
 push bc
 push hl
 ld l,(ix+0)
 ld h,(ix+1)
 inc ix
 inc ix
 ld a,($7ce5)
 inc a
 ld e,a
 ld d,0
 add hl,de
 pop de
 push de
 ld a,(rects+22)
 ld c,a
 ld b,0
 ldir
 ld a,(rects+22)
 neg
 add a,9
 ld c,a
 add hl,bc
 pop de
 ld a,d
 xor $60
 ld d,a
 ld a,(rects+22)
 ld c,a
 ld b,0
 ldir
 pop bc
 inc b
 ld hl,$78e0
 dec (hl)
 jr nz,fc_row
 ret
