; Compare only the small changing eyebrow band at publication. Body rows
; retain exact precomputed delta kernels. The guard reserves 16384 extra T,
; conservatively covering 16 rows x 2 planes x (72 + 427) T.
fast_eye_budget:
 ld a,($5bcc)
 or a
 ret z
 ex de,hl
 ld de,4096
 or a
 sbc hl,de
 ret c
 ld ($580c),hl
 ret
fast_eye_row:
 ld a,($5bcc)
 or a
 ret z
 ld a,(rects+21)
 ld l,a
 ld a,b
 sub l
 sub 11
 cp 16
 ret nc
 ld hl,fast_eye_kernel
 ld ($582c),hl
 ld ($582e),hl
 ret
fast_eye_kernel:
 push bc
 ld a,($5804)
 ld b,a
fek_cell:
 ld a,(de)
 cp (hl)
 jr z,fek_same
 ld (hl),a
fek_same:
 inc l
 inc de
 djnz fek_cell
 pop bc
 ret

