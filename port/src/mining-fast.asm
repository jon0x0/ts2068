; Relocatable transition fast path; source banks 0/1/7 are ROM-only.
; 5800..5859 scratch; descending records below DB00, after assembly.
 INCLUDE "../build/fast-tables.asm"
fast_select:
 xor a
 ld ($78f6),a
 ld a,($580f)
 ld ($7bac),a
 or a
 ld a,0
 ld ($580f),a
 ret nz
 ld a,(awake_done)
 or a
 ret z
 ; Preparation temporarily uses a HOME D800 stack. The speech ISR maps
 ; DOCK6, so wait for speech completion before borrowing that stack.
 call $a69c
 ret nz
 ld a,(rects+23)
 cp 52
 ret nz
 ld a,(oldrects+23)
 cp 52
 ret nz
 ld a,(rects+22)
 ld hl,oldrects+22
 and (hl)
 cp 7
 ret nz
 ld a,(face_x+1)
 ld hl,face_oldx
 sub (hl)
 inc a
 cp 3
 ret nc
 ld ($5806),a
 ld a,(face_y+1)
 ld hl,face_oldy
 sub (hl)
 inc a
 cp 3
 ret nc
 ld ($5807),a
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
 ; Transition index: eye*72 + old phase*9 + (dy+1)*3 + dx+1.
 ld hl,world_extension+63
 call world_call
 ret nz
 ld hl,world_extension+87
 call world_call
 ret nz
 ld a,(face_oldx)
 and 7
 ld c,a
 ld a,(eye_phase)
 add a,a
 add a,a
 add a,a
 add a,c
 ld l,a
 ld h,0
 ld d,h
 ld e,l
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,de
 ld a,($5807)
 ld c,a
 add a,a
 add a,c
 ld c,a
 ld a,($5806)
 add a,c
 ld e,a
 ld d,0
 add hl,de
 add hl,hl
 push hl
 ld a,$93
 ld ($78df),a
 out ($f4),a
 ld de,fast_transition_table
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($580a),de
 pop hl
 ld de,fast_budget_table
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($580c),de
 call fast_eye_budget
 jr nc,fs_eye_budget_ok
 ld a,$10
 ld ($78df),a
 out ($f4),a
 ret
fs_eye_budget_ok:
 ; New shut-mouth pose, independently indexed by eye and fine X phase.
 ld a,(eye_phase)
 add a,a
 add a,a
 add a,a
 ld c,a
 ld a,(face_x+1)
 and 7
 or c
 ld l,a
 ld h,0
 add hl,hl
 ld de,fast_pose_table
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 push de
 pop ix
 ld a,(rects+20)
 ld hl,$5800
 sub (hl)
 xor 1
 ld ($580e),a
 call fast_prepare
fast_prepared:
 ld a,$10
 ld ($78df),a
 out ($f4),a
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

fast_prepare:
fast_prepare_general:
 ld iy,($580a)
 ld ($5832),sp
 ld sp,$db00
 xor a
 ld ($582a),a
 ld a,($5802)
 ld b,a
 ld a,($5800)
 ld c,a
fpr_row:
 push bc
 ld a,(iy+0)
 inc iy
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 ld de,fast_pair_table
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld ($582c),de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($582e),de
 pop bc
 ; The new pose has 52 rows; the exposed old edge uses a padded blank row.
 ld de,fast_blank_row
 ld a,(rects+21)
 cp b
 jr z,fpr_image
 jr nc,fpr_source
 add a,52
 cp b
 jr c,fpr_source
 jr z,fpr_source
fpr_image:
 ld e,(ix+0)
 ld d,(ix+1)
 inc ix
 inc ix
fpr_source:
 ld a,($580e)
 or a
 jr z,fpr_source_ready
 inc de
fpr_source_ready:
 ld ($5822),de
 call offset
 ld a,h
 or $40
 ld h,a
 ld ($5820),hl
 ld ($5830),bc
 call fast_eye_row
 ld hl,($582c)
 ld de,fast_empty_kernel
 or a
 sbc hl,de
 jr z,fpr_no_bitmap
 add hl,de
 push hl
 ld hl,($5822)
 push hl
 ld hl,($5820)
 push hl
 ld hl,$582a
 inc (hl)
fpr_no_bitmap:
 ld hl,($5820)
 ld a,h
 xor $20
 ld h,a
 ld ($5820),hl
 ld hl,($5822)
 ld de,9
 add hl,de
 ld ($5822),hl
 ld hl,($582e)
 ld de,fast_empty_kernel
 or a
 sbc hl,de
 jr z,fpr_no_attr
 add hl,de
 push hl
 ld hl,($5822)
 push hl
 ld hl,($5820)
 push hl
 ld hl,$582a
 inc (hl)
fpr_no_attr:
 ld bc,($5830)
 inc b
 ld a,($5803)
 cp b
 jp nz,fpr_row
 ld ($5834),sp
 ld sp,($5832)
 ret

fast_publish:
 ld a,($78f6)
 or a
 ret z
 ld a,($582a)
 or a
 ret z
 ld b,a
 ; The entire bounded publication fits before the next interrupt. No ISR can
 ; borrow the record stack. Normal SP and mapping are restored before EI.
 di
 ld ($580a),sp
 ld sp,($5834)
 ld a,$93
 ld ($78df),a
 out ($f4),a
fast_record_loop:
 pop hl
 pop de
 pop ix
 call fast_jump
 djnz fast_record_loop
 ld sp,($580a)
 ld a,$10
 ld ($78df),a
 out ($f4),a
 ei
 ret
fast_jump:
 jp (ix)

