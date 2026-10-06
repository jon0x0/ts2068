; Bank 6 world extension; prepares changed scanner bytes after publication.
radar_entry:
 ld hl,$7e00
 ld de,$7e01
 ld bc,127
 ld (hl),0
 ldir
 ld hl,$7e80
 ld de,$7e81
 ld bc,127
 ld (hl),7
 ldir
 ; Camera viewport in the same 512x512 world as the contact markers.
 ld hl,($5886)
 ld de,64
 add hl,de
 ld a,l
 ld l,h
 ld c,a
 ld a,($5885)
 ld h,a
 ld a,c
 ld c,0
 push af
 ld a,($5884)
 ld c,a
 pop af
 ld de,$01e0
 call radar_relative_common
 ld a,($58ed)
 add a,31
 ld c,a
 ld a,($58ee)
 call radar_dot
 ld a,($58ed)
 ld c,a
 ld a,($58ee)
 add a,3
 call radar_dot
 ld a,($58ed)
 add a,31
 ld c,a
 ld a,($58ee)
 add a,3
 call radar_dot
 ld a,(rock_alive)
 or a
 jr z,radar_worker
 ld a,(rock_x)
 ld c,a
 ld a,(rock_y)
 ld de,$05c0
 ld hl,($586e)
 ld a,h
 ld h,l
 ld l,a
 ld a,(rock_y)
 call radar_relative_common
radar_worker:
 xor a
 ld ($58f3),a
radar_planets:
 ld a,($58f3)
 call wp_record
 ld a,(ix+7)
 or a
 jr z,radar_planet_next
 ld c,(ix+0)
 ld h,(ix+1)
 ld a,(ix+2)
 ld l,(ix+3)
 ld de,$05c0
 call radar_relative_common
radar_planet_next:
 ld hl,$58f3
 inc (hl)
 ld a,(hl)
 cp 17
 jr c,radar_planets
 ld a,(worker_alive)
 or a
 jr z,radar_face
 ld a,(worker_x)
 ld c,a
 ld a,(worker_y)
 ld de,$0280
 ld hl,($7c98)
 ld a,h
 ld h,l
 ld l,a
 ld a,(worker_y)
 call radar_relative_common
radar_face:
 ld a,(assembly_count)
 or a
 jr z,radar_player
 ld a,(bs_hits)
 cp 13
 jr nc,radar_player
 ld a,(face_x+1)
 ld c,a
 ld a,(face_y+1)
 ld de,$46e0
 ld hl,($7c9a)
 ld a,h
 ld h,l
 ld l,a
 ld a,(face_y+1)
 call radar_relative_common
radar_player:
 ld c,32
 ld a,8
 ld de,$47e0
 call radar_dot
 xor a
 ld ($5868),a
 ld ix,$5ea0
 ld de,$7e00
 ld b,0
radar_row:
 ld a,b
 and 7
 or $40
 ld h,a
 ld a,b
 and 8
 rlca
 rlca
 or 12
 ld l,a
 push bc
 ld b,8
radar_byte:
 ld a,(de)
 cp (hl)
 jr z,radar_same
 call radar_emit
radar_same:
 set 7,e
 set 5,h
 ld a,(de)
 cp (hl)
 jr z,radar_attr_same
 call radar_emit
radar_attr_same:
 res 7,e
 res 5,h
 inc de
 inc l
 djnz radar_byte
 pop bc
 inc b
 ld a,b
 cp 16
 jr nz,radar_row
radar_done:
 ret
radar_relative_common:
 ; C/A = low X/Y, H/L = high X/Y. Full 9-bit differences on both axes.
 push de
 push af
 ld a,l
 ld ($58ef),a
 ld l,c
 ld a,(px+1)
 ld e,a
 ld a,($7c96)
 ld d,a
 or a
 sbc hl,de
 ld a,h
 and 1
 ld h,a
 ld b,3
radar_xscale:
 srl h
 rr l
 djnz radar_xscale
 ld a,l
 add a,32
 and 63
 ld c,a
 ld ($58ed),a
 pop af
 ld l,a
 ld a,($58ef)
 ld h,a
 ld a,(py+1)
 ld e,a
 ld a,($7c97)
 ld d,a
 or a
 sbc hl,de
 ld a,h
 and 1
 ld h,a
 ld b,5
radar_yscale:
 srl h
 rr l
 djnz radar_yscale
 ld a,l
 add a,8
 and 15
 ld ($58ee),a
 pop de
 ; A=y, C=x, D=attribute, E=precomputed shape mask.
radar_dot:
 and 15
 rlca
 rlca
 rlca
 ld l,a
 ld a,c
 and 7
 ld b,a
 ld a,e
 jr z,radar_mask_ready
radar_shift:
 srl a
 djnz radar_shift
radar_mask_ready:
 push de
 ld e,a
 ld a,c
 srl a
 srl a
 srl a
 and 7
 or l
 ld l,a
 ld h,$7e
 set 7,l
 ld a,(hl)
 cp 7
 jr z,radar_color
 cp 1
 jr z,radar_color
 cp d
 jr z,radar_color
 ; Player is anchored; other conflicts shift down exactly one line.
 ld a,d
 cp $47
 jr z,radar_color
 ld a,l
 add a,8
 or $80
 ld l,a
radar_color:
 ld (hl),d
 res 7,l
 ld a,(hl)
 or e
 ld (hl),a
 pop de
 ret
radar_emit:
 push af
 ld a,($5868)
 cp 117
 jr c,radar_emit_room
 pop af
 ret
radar_emit_room:
 pop af
 ld (ix+0),l
 ld (ix+1),h
 ld (ix+2),a
 inc ix
 inc ix
 inc ix
 ld a,($5868)
 inc a
 ld ($5868),a
 ret
radar_end:
