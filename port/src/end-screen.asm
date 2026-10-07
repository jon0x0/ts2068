; Native status in the reserved band. Draw once; require released fire before
; accepting restart, so the shot that ended play cannot dismiss the result.
wb_end_screen:
 ld a,($5897)
 or a
 jr nz,we_input
 inc a
 ld ($5897),a
 ld a,(game_status)
 cp 1
 ld hl,we_lost
 jr nz,we_message
 jr we_input ; frontend already drew the two-line arcade victory message
we_message:
 ld bc,24*256+11
 call we_text
 ld hl,we_prompt
 ld bc,40*256+8
 call we_text
we_input:
 ld bc,$7ffe
 in a,(c)
 and 1
 ld d,a
 di
 ld a,14
 out ($f5),a
 ld bc,$01f6
 in a,(c)
 ei
 and $80
 jr z,we_pressed
 ld a,d
 or a
 jr z,we_pressed
 ld a,2
 ld ($5897),a
 scf
 ret
we_pressed:
 ld a,($5897)
 cp 2
 jp z,title_boot
 scf
 ret
we_text:
 ld a,(hl)
 inc hl
 cp 255
 ret z
 push hl
 push bc
 ld l,a
 ld h,0
 ld e,l
 ld d,h
 add hl,hl
 add hl,hl
 add hl,hl
 or a
 sbc hl,de
 ld de,we_font
 add hl,de
 ex de,hl
 ld a,7
we_row:
 push af
 call offset
 ld a,h
 or $40
 ld h,a
 ld a,(de)
 ld (hl),a
 ld a,h
 xor $20
 ld h,a
 ld (hl),7
 inc de
 inc b
 pop af
 dec a
 jr nz,we_row
 pop bc
 inc c
 pop hl
 jr we_text
; SPACE A E F G I M N O R S T U V W Y (five-bit glyphs, seven rows).
we_font:
 DB 0,0,0,0,0,0,0
 DB $70,$88,$88,$f8,$88,$88,$88
 DB $f8,$80,$80,$f0,$80,$80,$f8
 DB $f8,$80,$80,$f0,$80,$80,$80
 DB $70,$88,$80,$b8,$88,$88,$70
 DB $70,$20,$20,$20,$20,$20,$70
 DB $88,$d8,$a8,$a8,$88,$88,$88
 DB $88,$c8,$a8,$98,$88,$88,$88
 DB $70,$88,$88,$88,$88,$88,$70
 DB $f0,$88,$88,$f0,$a0,$90,$88
 DB $78,$80,$80,$70,$08,$08,$f0
 DB $f8,$20,$20,$20,$20,$20,$20
 DB $88,$88,$88,$88,$88,$88,$70
 DB $88,$88,$88,$88,$88,$50,$20
 DB $88,$88,$88,$a8,$a8,$d8,$88
 DB $88,$88,$50,$20,$20,$20,$20
we_lost: DB 4,1,6,2,0,8,13,2,9,255
we_prompt: DB 3,5,9,2,0,11,8,0,9,2,10,11,1,9,11,255
