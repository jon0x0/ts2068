; First-wave N1ALL InPop0: primary rock + 17 persistent planetoids.
; Record: x16,y16,xfrac,yfrac,direction,mass,richter,type.
; Five population types currently share the pre-shifted IPLAN1 atlas.
wp_records:
 DW $79b0,$79ba,$79c4,$79ce,$79d8,$79e2,$79ec,$79f6
 DW $7db0,$7dba,$7dc4,$7dce,$7dd8,$7de2,$7dec,$7df6,$58b4
wp_seeds:
 DW 320,100,440,75,32,235,170,270,295,235,430,240
 DW 65,385,200,420,330,365,455,405,55,30,235,15
 DW 350,485,480,490,490,160,260,150,120,490
wp_record:
 add a,a
 ld l,a
 ld h,0
 ld de,wp_records
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 push de
 pop ix
 ret
wp_old:
 cp 16
 ld hl,$7cec
 ret z
 add a,a
 add a,a
 ld l,a
 ld h,$7d
 ret
wp_init:
 ld a,1
 ld ($5893),a
 ld hl,$7d00
 ld de,$7d01
 ld bc,63
 ld (hl),0
 ldir
 ld hl,0
 ld ($7cec),hl
 ld ($7cee),hl
 ld iy,wp_seeds
 ld b,17
wpi_each:
 push bc
 ld a,17
 sub b
 call wp_record
 ld a,(iy+0)
 ld (ix+0),a
 ld a,(iy+1)
 ld (ix+1),a
 ld a,(iy+2)
 ld (ix+2),a
 ld a,(iy+3)
 ld (ix+3),a
 ld (ix+4),0
 ld (ix+5),0
 pop bc
 ld a,b
 cp 9
 jr c,wpi_speed
 sub 9
wpi_speed:
 add a,a
 ld (ix+6),a
 ld (ix+7),96
 ld (ix+8),0
 ld a,1
 ld (ix+9),a
 ld de,4
 add iy,de
 djnz wpi_each
 ; Nine extra type 1, two each types 2..5, plus the primary type 1.
 ld a,2
 ld ($7dc3),a
 ld ($7dcd),a
 inc a
 ld ($7dd7),a
 ld ($7de1),a
 inc a
 ld ($7deb),a
 ld ($7df5),a
 inc a
 ld ($7dff),a
 ld ($58bd),a
 ret
wb_population:
 ; Retirement is final while chase suppression remains enabled. The previous
 ; projection records whether any secondary mass remains, including offscreen.
 ld a,($5bb2)
 or a
 jr z,wpp_population_live
 ld a,($5bce)
 or a
 ret z
wpp_population_live:
 ld a,($5893)
 or a
 call z,wp_init
 xor a
 ld ($5895),a
 ; Visit only this tick's interleaved group, in the original order.
 ld a,($5865)
 add a,2
 and 3
 add a,14
 ld b,a
wpp_each:
 push bc
 ld a,17
 sub b
 call wp_record
 ld a,(ix+7)
 or a
 jr nz,wpp_move
 ld a,($5bb2)
 or a
 jp nz,wpp_next
 ld a,($5865)
 and 60
 jp nz,wpp_next
 ld a,($5895)
 or a
 jp nz,wpp_next
 inc a
 ld ($5895),a
 ; Replenish at the far sector edge, at least 240 world units from player.
 ld a,6
 push ix
 call wb_get
 pop ix
 ld de,240
 add hl,de
 ld a,h
 and 1
 ld (ix+0),l
 ld (ix+1),a
 ld a,7
 push ix
 call wb_get
 pop ix
 ld (ix+2),l
 ld (ix+3),h
 ld (ix+7),96
 ld (ix+8),0
wpp_move:
 ld a,(ix+6)
 ld e,a
 ld d,0
 ld hl,wb_rock_speeds4
 add hl,de
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 push hl
 ld l,(ix+4)
 ld h,(ix+0)
 add hl,de
 ld (ix+4),l
 ld (ix+0),h
 ld a,(ix+1)
 adc a,0
 bit 7,d
 jr z,wpp_x_sign
 dec a
wpp_x_sign:
 and 1
 ld (ix+1),a
 pop hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld l,(ix+5)
 ld h,(ix+2)
 add hl,de
 ld (ix+5),l
 ld (ix+2),h
 ld a,(ix+3)
 adc a,0
 bit 7,d
 jr z,wpp_y_sign
 dec a
wpp_y_sign:
 and 1
 ld (ix+3),a
 call wpp_hit
 call wpp_mine
wpp_next:
 pop bc
wpp_skipped:
 ld a,b
 sub 4
 ret c
 ret z
 ld b,a
 jp wpp_each
 ret
wpp_hit:
 ld a,(bullet_alive)
 or a
 ret z
 ld a,(bx+1)
 sub (ix+0)
 ld c,a
 ld a,($7c94)
 sbc a,(ix+1)
 and 1
 ret nz
 ld a,c
 cp 26
 ret nc
 ld a,(by+1)
 sub (ix+2)
 ld c,a
 ld a,($7c95)
 sbc a,(ix+3)
 and 1
 ret nz
 ld a,c
 cp 28
 ret nc
 ld a,(ix+8)
 ld b,(ix+7)
 call rock_add_vibration
 ld (ix+8),a
 ld hl,hits
 inc (hl)
 jp kill_bullet
wpp_mine:
 ld a,($5865)
 and 12
 ret nz
 ld a,(crystal_alive)
 or a
 jr nz,wpp_damp
 ld a,(seed)
 add a,73
 ld (seed),a
 ld c,a
 ld b,(ix+7)
 ld a,(ix+8)
 ld d,0
 call rock_try_crystal
 ld (ix+8),a
 ld (ix+7),b
 jr nc,wpp_damp
 ld l,(ix+0)
 ld h,(ix+1)
 ld de,13
 add hl,de
 ld a,h
 and 1
 ld ($7c92),a
 ld h,l
 ld l,0
 ld (cx),hl
 ld l,(ix+2)
 ld h,(ix+3)
 ld de,14
 add hl,de
 ld a,h
 and 1
 ld ($7c93),a
 ld h,l
 ld l,0
 ld (cy),hl
 ld a,1
 ld (crystal_alive),a
 ld hl,releases
 inc (hl)
wpp_damp:
 ld a,(ix+8)
 ld c,1
 call rock_damp
 ld (ix+8),a
 ld a,b
 cp 2
 ret nz
 ld (ix+7),0
 ret
wb_pop_begin:
 ld a,(game_mode)
 or a
 ret z
 ld hl,rects
 ld de,$7c84
 ld bc,4
 ldir
 ld hl,$7cd0
 ld bc,4
 ldir
 xor a
 ld ($58f1),a
 ret
wb_pop_finish:
 ld a,(game_mode)
 or a
 ret z
 ld hl,$7c84
 ld de,rects
 ld bc,4
 ldir
 ld de,$7cd0
 ld bc,4
 ldir
 xor a
 ld ($58f1),a
 ret
wp_calc:
 call wp_record
 ld a,(ix+7)
 or a
 jp z,wpc_hidden
 ld ($5bce),a
 ld l,(ix+0)
 ld h,(ix+1)
 ld de,($5884)
 or a
 sbc hl,de
 bit 0,h
 jr z,wpc_x_visible
 ld a,l
 cp 229
 jr c,wpc_hidden
wpc_x_visible:
 ld a,l
 and 7
 ld ($58f0),a
 ld a,h
 and 1
 ld ($7c8c),a
 ld a,l
 srl a
 srl a
 srl a
 ld (rects),a
 ld l,(ix+2)
 ld h,(ix+3)
 ld de,($5886)
 or a
 sbc hl,de
 bit 0,h
 jr nz,wpc_hidden
 ld a,l
 cp 37
 jr c,wpc_hidden
 cp 176
 jr nc,wpc_hidden
 ld (rects+1),a
 ld a,h
 and 1
 ld ($7c8d),a
 ld a,5
wpc_dead:
 ld (rects+2),a
 ld a,28
 ld (rects+3),a
 ld iy,rects
 ld ix,$7cd0
 ld hl,$7c8c
 ld b,1
 jp wc_object
wpc_hidden:
 xor a
 ld (rects+2),a
 ret
wb_pop_clear:
 ld a,(game_mode)
 or a
 scf
 ret z
 ld a,($58f1)
 cp 34
 ccf
 ret c
 ld c,a
 inc a
 ld ($58f1),a
 ld a,c
 srl a
 jr c,wpc_new
 call wp_old
 inc hl
 inc hl
 ld a,(hl)
 or a
 jp z,wb_pop_clear
 dec hl
 dec hl
 ld de,rects
 ld bc,4
 ldir
 jr wpc_ready
wpc_new:
 push af
 call wp_cache
 inc hl
 inc hl
 pop bc
 ld a,(hl)
 or a
 ld a,b
 jp z,wb_pop_clear
 call wp_load
wpc_ready:
 ld iy,rects
 ld a,(rects+2)
 or a
 jp z,wb_pop_clear
 ret
wb_pop_draw:
 ld a,(game_mode)
 or a
 scf
 ret z
 ld a,($58f1)
 cp 17
 ccf
 ret c
 push af
 call wp_cache
 inc hl
 inc hl
 pop bc
 ld a,(hl)
 or a
 ld a,b
 jr nz,wpd_visible
 ; Only the old width needs invalidating for a hidden rectangle. Avoid
 ; loading nine projection bytes and copying four old bytes for each slot.
 push af
 call wp_old
 inc hl
 inc hl
 ld (hl),0
 pop af
 inc a
 ld ($58f1),a
 jp wb_pop_draw
wpd_visible:
 push af
 call wp_load
 pop af
 push af
 call wp_old
 ex de,hl
 ld hl,rects
 ld bc,4
 ldir
 pop af
 inc a
 ld ($58f1),a
 ld a,($58f0)
 ld l,a
 ld h,1
 ld bc,420
 ld a,(rects+2)
 or a
 jp z,wb_pop_draw
 ret
wb_pop_overlap:
 ld a,($5bca)
 or a
 ret z
 ld a,(game_mode)
 or a
 ret z
 call wb_pop_begin
wpo_each:
 call wb_pop_clear
 jr c,wpo_clear
 ld a,(iy+2)
 or a
 jr z,wpo_each
 ld c,a
 ld a,($5801)
 cp (iy+0)
 jr c,wpo_each
 jr z,wpo_each
 ld a,(iy+0)
 add a,c
 ld hl,$5800
 cp (hl)
 jr c,wpo_each
 jr z,wpo_each
 ld a,($5803)
 cp (iy+1)
 jr c,wpo_each
 jr z,wpo_each
 ld a,(iy+1)
 add a,(iy+3)
 ld hl,$5802
 cp (hl)
 jr c,wpo_each
 jr z,wpo_each
 call wb_pop_finish
 ld a,1
 or a
 ret
wpo_clear:
 jp wb_pop_finish
; Project/cull once per picture. The stage scratch ends below BC80 even for
; a complete assembly image, leaving this 153-byte picture cache untouched.
wp_cache:
 ld l,a
 ld h,0
 ld e,l
 ld d,h
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,de
 ld de,$bc80
 add hl,de
 ret
wp_load:
 call wp_cache
 ld de,rects
 ld bc,4
 ldir
 ld de,$7cd0
 ld bc,4
 ldir
 ld a,(hl)
 ld ($58f0),a
 ret
wb_pop_prepare:
 ld a,($5bb2)
 or a
 jr z,wpp_prepare_live
 ld a,($5bce)
 ld hl,$5bcd
 or (hl)
 jr nz,wpp_prepare_live
 ld ($5bca),a
 ret
wpp_prepare_live:
 jp $a690
