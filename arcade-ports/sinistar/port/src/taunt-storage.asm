; Foreground only. Source banks 0/1/7 plus world code in DOCK6.
; Expand at most three lossless transition deltas into unused HOME 7F00..7F34.
wb_transition_unpack:
 ld a,$d3
 ld ($78df),a
 out ($f4),a
 ld hl,($580a)
 call wb_transition_node
 ld hl,$7f00
 ld ($580a),hl
 ld a,$50
 ld ($78df),a
 out ($f4),a
 ret
wb_transition_node:
 ld a,(hl)
 inc hl
 or a
 jr nz,wb_transition_patch
 ld de,$7f00
 ld bc,53
 ldir
 ret
wb_transition_patch:
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 push hl
 ex de,hl
 call wb_transition_node
 pop ix
 push ix
 pop hl
 ld de,7
 add hl,de
 ld de,$7f00
 ld b,7
wb_transition_group:
 ld c,(ix+0)
 inc ix
 push bc
 ld b,8
wb_transition_bit:
 srl c
 jr nc,wb_transition_same
 ld a,(hl)
 inc hl
 ld (de),a
wb_transition_same:
 inc de
 djnz wb_transition_bit
 pop bc
 djnz wb_transition_group
 ret
