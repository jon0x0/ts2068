; Reuse fixed-width row copies when the old/new byte-cell envelopes are disjoint.
; Pixel separation alone is insufficient: ECM attributes belong to 8x1 cells.
separated_bounds:
 ld hl,(oldxy)
 ld de,(newxy)
 ld a,l
 cp e
 jr c,sb_xmin
 ld a,e
sb_xmin:
 ld ($78e4),a
 ld a,l
 cp e
 jr nc,sb_xmax
 ld a,e
sb_xmax:
 add a,3
 ld ($78e5),a
 ld a,h
 cp d
 jr c,sb_ymin
 ld a,d
sb_ymin:
 ld ($78e6),a
 ld a,h
 cp d
 jr nc,sb_ymax
 ld a,d
sb_ymax:
 add a,12
 ld ($78e7),a
 ld a,(oldface+2)
 ld hl,newface+2
 or (hl)
 ret z
 ld a,($78e1)
 ld hl,$78e4
 cp (hl)
 jr c,sb_yes
 jr z,sb_yes
 ld a,($78e5)
 ld hl,$78e0
 cp (hl)
 jr c,sb_yes
 jr z,sb_yes
 ld a,($78e3)
 ld hl,$78e6
 cp (hl)
 jr c,sb_yes
 jr z,sb_yes
 ld a,($78e7)
 ld hl,$78e2
 cp (hl)
 jr c,sb_yes
 jr z,sb_yes
 xor a
 ret
sb_yes:
 ld iy,$78e0
 call sb_shape
 ret z
 ld iy,$78e4
sb_shape:
 ld a,(iy+1)
 sub (iy+0)
 cp 11
 jr nc,sb_no
 ld a,(iy+3)
 sub (iy+2)
 cp 65
 jr nc,sb_no
 ld a,1
 or a
 ret
sb_no:
 xor a
 ret

 ; Independent fixed-width bitmap copies plus a sparse attribute list,
; mirroring the saved demo without baking in positions or trajectory.
separated_list:
 call separated_order
 call separated_box
 call separated_other
 call separated_box
 jp list_done
separated_order:
 ld iy,$78e0
 ld a,($78e2)
 ld hl,$78e6
 cp (hl)
 ret c
 ret z
 ld iy,$78e4
 ret
separated_other:
 ld a,iyl
 xor 4
 ld iyl,a
 ret
separated_box:
 ld a,iyl
 cp $e0
 jr nz,separated_full_box
 ld a,($78ed)
 or a
 jr z,separated_full_box
 push iy
 call relative_bitmap_list
 pop iy
 ret
separated_full_box:
 ld c,(iy+0)
 ld b,(iy+2)
 ld a,(iy+1)
 sub c
 ld hl,mono_table
 call select_loop
 call offset
 ld a,h
 or $a0
 ld h,a
 ld a,(iy+3)
 sub (iy+2)
 ld b,a
 jp fl_rows

separated_attributes:
 exx
 ld hl,$f000
 exx
 call relative_face_attributes
 or a
 jr nz,sa_ship
 ld iy,$78e0
 call separated_color_box
sa_ship:
 ld iy,$78e4
 call separated_color_box
 exx
 ld (hl),$c9
 ld ($78d4),hl
 exx
 ret
separated_color_box:
 ld c,(iy+0)
 ld b,(iy+2)
 ld a,(iy+1)
 sub c
 ld hl,delta_table
 call select_loop
 call offset
 ld a,h
 or $c0
 ld h,a
 ld a,(iy+3)
 sub (iy+2)
 ld b,a
scb_row:
 push hl
 ld a,h
 xor $a0
 ld d,a
 ld e,l
 call $7b80
 pop hl
 inc h
 ld a,h
 and 7
 jr nz,scb_next
 ld a,l
 add a,32
 ld l,a
 jr c,scb_next
 ld a,h
 sub 8
 ld h,a
scb_next:
 djnz scb_row
 ret

; Attribute stores cost exactly 20 T per five-byte instruction pair.
; Check both ends of each rectangle, including the cost of earlier rectangles.
separated_budget:
 ld hl,($78d4)
 ld de,$f000
 or a
 sbc hl,de
 add hl,hl
 add hl,hl
 ld de,3024
 add hl,de
 ld ($78da),hl
 call separated_order
 call separated_box_budget
 ret nz
 call separated_other
 jp separated_box_budget
separated_box_budget:
 ld a,(iy+1)
 sub (iy+0)
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 ld de,row_costs
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($78dc),de
 ld hl,($78da)
 add hl,de
 ld b,(iy+2)
 call separated_deadline
 ret nz
 ld a,(iy+3)
 sub (iy+2)
 ld b,a
 ld de,($78dc)
 call scale_cost
 ld de,($78da)
 add hl,de
 ld ($78da),hl
 ld b,(iy+3)
 dec b
separated_deadline:
 push hl
 ld l,b
 ld h,0
 add hl,hl
 ld de,separated_deadlines
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 pop hl
 ex de,hl
 or a
 sbc hl,de
 jr c,sd_late
 xor a
 ret
sd_late:
 ld a,1
 or a
 ret
separated_deadlines:
 INCLUDE "../build/scene-deadlines.asm"
