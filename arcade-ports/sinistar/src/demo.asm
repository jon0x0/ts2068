 ORG $8000
 DB $02,$02,$08,$80,$EF,$01,0,0
 INCLUDE "../build/constants.asm"
state EQU $7800
ticks EQU $7810
framecount EQU $7814
seqptr EQU $7812
mapping EQU $7819
face EQU $7830
ship EQU $7837
event EQU $783e
direction EQU $783f
start:
 di
 ld sp,$7fff
 ld a,$18
 out ($f4),a
 ld hl,$6000
 ld de,$a000
 ld bc,8192
 ldir
 ld a,$10
 out ($f4),a
 IF SEQUENCE_SIZE > 8192
 ld hl,sequence_tail
 ld de,$c000
 ld bc,SEQUENCE_SIZE-8192
 ldir
 ENDIF
 ld a,$14
 out ($f4),a
 ld hl,$4000
 ld de,$f000
 ld bc,AUDIO_SIZE
 ldir
 ld a,$10
 out ($f4),a
 ld a,2
 out ($ff),a
 xor a
 out ($fe),a
 ld hl,$7800
 ld de,$7801
 ld bc,$1ff
 ld (hl),a
 ldir
 ld hl,$4000
 ld de,$4001
 ld bc,$17ff
 ld (hl),0
 ldir
 ld hl,$6000
 ld de,$6001
 ld bc,$17ff
 ld (hl),7
 ldir
 ld hl,$7a00
 ld de,$7a01
 ld bc,256
 ld (hl),$7b
 ldir
 ld a,$c3
 ld ($7b7b),a
 ld ($7b80),a
 ld hl,isr
 ld ($7b7c),hl
 ld a,$7a
 ld i,a
 im 2
 call audio_init
 ld a,$10
 ld (mapping),a
 ld hl,$a000
 ld (seqptr),hl
 INCLUDE "../build/initial-attributes.asm"
 ld hl,SEQUENCE_END-32
 ld de,face
 ld bc,32
 ldir
 ld ix,ship
 ld hl,copy3
 call draw_sprite
 ld ix,face
 ld hl,copy7
 call draw_sprite
 ei
main:
 halt
go:
 ld hl,(seqptr)
 ld de,face
 ld bc,32
 ldir
 ld de,SEQUENCE_END
 or a
 sbc hl,de
 add hl,de
 jr nz,seq_ok
 ld hl,$a000
seq_ok:
 ld (seqptr),hl
 ld a,(event)
 cp 255
 jr z,no_speech
 or a
 ld hl,AUDIO0
 ld de,COUNT0
 jr z,speak
 ld hl,AUDIO1
 ld de,COUNT1
speak:
 di
 call ay_start
 ei
no_speech:
 ; Top-of-screen player updates precede stars and the central Sinistar.
 ld ix,$7845
 call color_delta
 ld ix,ship
 ld hl,copy3
 call draw_sprite
 call stars_update
 ld ix,$7840
 call color_delta
 ld ix,face
 ld hl,copy7
 call draw_sprite
frame_done:
 ld hl,(framecount)
 inc hl
 ld (framecount),hl
 jp main
draw_sprite:
 ld ($7b81),hl
 ld d,(ix+1)
 ld e,(ix+0)
 call screen
 ex de,hl
 ld l,(ix+5)
 ld h,(ix+6)
 ld a,(ix+4)
 ld (mapping),a
 out ($f4),a
 ld b,(ix+3)
sprite_row:
 call render_row
 djnz sprite_row
 ld a,$10
 ld (mapping),a
 out ($f4),a
 ret
render_row:
 call $7b80
 ld a,e
 sub (ix+2)
 ld e,a
 inc d
 ld a,d
 and 7
 jr nz,next_row
 ld a,e
 add a,32
 ld e,a
 jr c,next_row
 ld a,d
 sub 8
 ld d,a
next_row:
 ret
; Precomputed nonzero attribute XOR deltas at absolute display addresses.
color_delta:
 ld a,(ix+0)
 ld (mapping),a
 out ($f4),a
 ld l,(ix+1)
 ld h,(ix+2)
 ld a,(hl)
 inc hl
 or a
 jr z,color_end
 ld b,a
color_byte:
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld a,(de)
 xor (hl)
 ld (de),a
 inc hl
 djnz color_byte
color_end:
 ld a,$10
 ld (mapping),a
 out ($f4),a
 ret
screen:
 ld a,d
 and 7
 or $40
 ld h,a
 ld a,d
 and $c0
 rrca
 rrca
 rrca
 or h
 ld h,a
 ld a,d
 and $38
 rlca
 rlca
 or e
 ld l,a
 ret
stars_update:
 ld a,($784a)
 ld (mapping),a
 out ($f4),a
 ld hl,($784b)
 ld a,(hl)
 inc hl
 ld ($7827),a
 add a,a
 ld c,a
 ld a,($7827)
 add a,c
 ld c,a
 ld b,0
 or a
 jr z,stars_empty
 ld de,$7d00
 ldir
stars_empty:
 ld a,$10
 ld (mapping),a
 out ($f4),a
 ld a,($7827)
 or a
 ret z
 ld b,a
 ld hl,$7d00
star_op:
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld a,(de)
 xor (hl)
 ld (de),a
 inc hl
 djnz star_op
 ret
isr:
 push af
 push bc
 push de
 push hl
 ; A source bank can hide HOME speech. Restore it only while servicing AY.
 ld a,$10
 out ($f4),a
 ld a,(ticks)
 inc a
 ld (ticks),a
 call ay_tick
 ld a,(mapping)
 out ($f4),a
 pop hl
 pop de
 pop bc
 pop af
 ei
 reti
 INCLUDE "../build/audio.asm"
 INCLUDE "../build/fast-copy.asm"
sequence_tail:
 IF SEQUENCE_SIZE > 8192
 INCBIN "../build/sequence-tail.bin"
 ENDIF
