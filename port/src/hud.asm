; Native static trim and changed-score-only display. No playfield composition.
; Cached score HOME 7BF9..7BFA; initialized on the first physics tick.
hud_tick:
 ld hl,(frames)
 ld a,h
 or l
 call z,hud_init
 ld a,(frames)
 and 15
 ret nz
 call hud_ammo
 call hud_score
 ld de,($7bf9)
 or a
 sbc hl,de
 ret z
 add hl,de
 ld ($7bf9),hl
 ld iy,front_divisors
 ld c,1
hud_digit:
 ld e,(iy+0)
 ld d,(iy+1)
 xor a
hud_sub:
 inc a
 or a
 sbc hl,de
 jr nc,hud_sub
 add hl,de
 dec a
 call hud_glyph
 inc iy
 inc iy
 inc c
 ld a,c
 cp 6
 jr nz,hud_digit
 ld a,l
 add a,a
 add a,a
 add a,l
 jp hud_glyph
hud_glyph:
 push hl
 push bc
 ld l,a
 ld h,0
 ld d,h
 ld e,l
 add hl,hl
 add hl,hl
 add hl,de
 ld de,hud_digits
 add hl,de
 ld d,$42
 ld e,c
 ld b,5
hud_glyph_row:
 ld a,(hl)
 ld (de),a
 inc hl
 ld a,d
 add a,$20
 ld d,a
 ld a,7
 ld (de),a
 ld a,d
 sub $1f
 ld d,a
 djnz hud_glyph_row
 pop bc
 pop hl
 ret
hud_init:
 ld hl,$ffff
 ld ($7bf9),hl
 ld ($7bfe),hl ; cached ammo plus reserved padding byte
 ; Chevron fins and tapered filled cap; scanner moved down eight rows.
 ld de,hud_ribs
 ld b,0
hud_trim:
 push bc
 push de
 ld c,10
 call offset
 set 6,h
 pop de
 ld c,2
hud_fin_byte:
 ld a,(de)
 inc de
 ld (hl),a
 set 5,h
 ld (hl),65
 res 5,h
 push hl
 push de
 ld e,a
 ld d,0
 ld b,8
hud_reverse:
 rr e
 rl d
 djnz hud_reverse
 ld a,l
 xor 31
 ld l,a
 ld (hl),d
 set 5,h
 ld (hl),65
 pop de
 pop hl
 inc l
 dec c
 jr nz,hud_fin_byte
 pop bc
 inc b
 ld a,b
 and 3
 jr nz,hud_fin_next
 ld a,b
 cp 8
 jr c,hud_fin_next
 ld de,hud_ribs+16
hud_fin_next:
 ld a,b
 cp 24
 jr nz,hud_trim
 ; Fill the center above the radar, including its bright blue top edge.
 ld b,0
hud_cap_row:
 push bc
 ld c,12
 call offset
 set 6,h
 ld b,8
hud_cap_byte:
 ld (hl),255
 set 5,h
 ld (hl),65
 res 5,h
 inc l
 djnz hud_cap_byte
 pop bc
 inc b
 ld a,b
 cp 8
 jr nz,hud_cap_row
 ; y63, immediately above the clipped y64..175 playfield.
hud_divider:
 ld hl,$47e0
 ld de,$67e0
 ld b,32
hud_line:
 ld (hl),255
 ld a,65
 ld (de),a
 inc l
 inc e
 djnz hud_line
 ret
hud_ribs:
 DB 255,255,255,255,255,255,255,255,255,255,15,255,0,255,0,15,248,1,15,129,0,249,0,15
hud_digits:
 DB $70,$50,$50,$50,$70
 DB $20,$60,$20,$20,$70
 DB $70,$10,$70,$40,$70
 DB $70,$10,$70,$10,$70
 DB $50,$50,$70,$10,$10
 DB $70,$40,$70,$10,$70
 DB $70,$40,$70,$50,$70
 DB $70,$10,$20,$20,$20
 DB $70,$50,$70,$50,$70
 DB $70,$50,$70,$10,$70
 DB $60,$50,$60,$50,$60 ; B label
hud_ammo:
 ld a,(bombs)
 ld hl,$7bfe
 cp (hl)
 ret z
 ld (hl),a
 ld b,255
hud_ammo_tens:
 inc b
 sub 10
 jr nc,hud_ammo_tens
 add a,10
 push af
 ld a,b
 ld c,35
 call hud_glyph
 pop af
 inc c
 call hud_glyph
 ld a,10
 ld c,33
 jp hud_glyph
