; IRQ.SRC uses ten camera-relative stars. Screen positions wrap at the
; adapted 256x112 playfield, preserving their phase across the world seam.
wb_stars_update:
 ld a,(game_mode)
 or a
 ret z
 ld a,($5892)
 or a
 jr nz,ws_initialized
 inc a
 ld ($5892),a
 ld hl,ws_seeds
 ld de,$58c0
 ld bc,20
 ldir
ws_initialized:
 ld hl,$58c0
 ld de,$58d4
 ld bc,20
 ldir
 ld hl,($5888)
 ld de,($5884)
 ld ($5888),de
 or a
 sbc hl,de
 ld c,l
 ld hl,($588a)
 ld de,($5886)
 ld ($588a),de
 or a
 sbc hl,de
 ld a,h
 and 1
 neg
 ld h,a
 ; Reduce camera Y displacement once, not separately for every star.
 ; H/L hold the signed wrapped displacement in -256..255.
 ld de,112
ws_negative:
 bit 7,h
 jr z,ws_positive
 add hl,de
 jr ws_negative
ws_positive:
 ld a,h
 or a
 jr nz,ws_subtract
 ld a,l
 cp 112
 jr c,ws_normalized
ws_subtract:
 or a
 sbc hl,de
 jr ws_positive
ws_normalized:
 ld e,l
 ld hl,$58c0
 ld b,10
ws_each:
 ld a,(hl)
 add a,c
 ld (hl),a
 inc hl
 ld a,(hl)
 add a,e
 cp 112
 jr c,ws_y_done
 sub 112
ws_y_done:
 ld (hl),a
 inc hl
 djnz ws_each
 ret
ws_seeds:
 DB 13,7,47,83,71,33,99,101,121,61,147,19,173,93,201,43,223,3,249,73
wb_star_overlap:
 ld a,(game_mode)
 or a
 ret z
 ld hl,$58c0
 ld b,20
wso_each:
 ld a,(hl)
 inc hl
 rrca
 rrca
 rrca
 and 31
 ld c,a
 ld a,($5800)
 cp c
 jr z,wso_right
 jr nc,wso_next
wso_right:
 ld a,($5801)
 cp c
 jr c,wso_next
 jr z,wso_next
 ld a,(hl)
 add a,64
 ld c,a
 ld a,($5802)
 cp c
 jr z,wso_bottom
 jr nc,wso_next
wso_bottom:
 ld a,($5803)
 cp c
 jr c,wso_next
 jr z,wso_next
 ; Stars hidden by both poses cannot interfere with the changed-cell stream.
 push bc
 ld b,c
 dec hl
 ld a,(hl)
 inc hl
 rrca
 rrca
 rrca
 and 31
 ld c,a
 call ws_cover_current
 jr c,wso_reject
 ld iy,oldrects+20
 call ws_cover_rect
 pop bc
 jr nc,wso_next
 jr wso_hit
wso_reject:
 pop bc
wso_hit:
 ld a,1
 or a
 ret
wso_next:
 inc hl
 djnz wso_each
 xor a
 ret

; Only previously drawn star cells need erasure. New positions are tested
; against the composed shadow image by stars_draw; clearing them first
; unnecessarily damages retained sprites and widens dirty intervals.
stars_mark:
 ld l,b
 ld h,$79
 ld a,c
 cp (hl)
 jr nc,sm_max
 ld (hl),a
sm_max:
 inc a
 ld h,$7d
 cp (hl)
 ret c
 ld (hl),a
 ret
stars_clear:
 ld a,(game_mode)
 or a
 ret z
 ld hl,$58d4
 ld d,10
sc_each:
 ld a,(hl)
 inc hl
 rrca
 rrca
 rrca
 and 31
 ld c,a
 ld a,(hl)
 inc hl
 add a,64
 ld b,a
 push hl
 call stars_mark
 push de
 call offset
 ld a,h
 or $a0
 ld h,a
 ld (hl),0
 call stars_attribute
 pop de
 pop hl
 dec d
 jr nz,sc_each
 ret
stars_draw:
 ld a,(game_mode)
 or a
 ret z
 ld ix,$58c0
 ld d,10
sd_each:
 ld a,(ix+0)
 ld c,a
 and 7
 ld e,a
 ld a,$80
 jr z,sd_mask
sd_shift:
 srl a
 dec e
 jr nz,sd_shift
sd_mask:
 push af
 srl c
 srl c
 srl c
 ld a,(ix+1)
 add a,64
 ld b,a
 call ws_cover_current
 jr nc,sd_hidden
 push de
 call offset
 ld a,h
 or $a0
 ld h,a
 pop de
 pop af
 ld e,a
 ld a,(hl)
 or a
 jr nz,sd_next
 ld (hl),e
 push hl
 call stars_mark
 pop hl
 call stars_attribute
 jr sd_next
sd_hidden:
 pop af
sd_next:
 inc ix
 inc ix
 dec d
 jr nz,sd_each
 ret

; BC = screen row / byte column. Preserve HL, DE and IX; carry = exposed.
ws_cover_current:
 ld a,(bs_hits)
 or a
 scf
 ret nz
 ld a,($5bcb)
 and 2
 scf
 ret z
 ld a,(awake_done)
 or a
 jr nz,ws_awake_cover
 ld a,(sinistar_built)
 or a
 scf
 ret nz
 ld a,(rects+22)
 or a
 scf
 ret z
 ld a,($5bd0)
 or a
 scf
 ret z
 push hl
 ld a,ixl
 and 31
 ld l,a
 ld h,$5c
 ld a,(hl)
 sub 1
 pop hl
 ret
ws_awake_cover:
 ld iy,rects+20
ws_cover_rect:
 ld a,c
 sub (iy+0)
 ret c
 cp (iy+2)
 ccf
 ret c
 ld a,b
 sub (iy+1)
 ret c
 cp (iy+3)
 ccf
 ret
