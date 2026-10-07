; Boot-copied HOME code, visible during every speech bank mapping.
; 7F53 is a refresh countdown; 7F60..7FCF reserved for this helper.
 INCLUDE "../build/boot-equ.asm"
 ORG $7f60
 jp roar_request
 jp roar_mix
 jp roar_shape
roar_request:
 ; Called inside ISR: duplicate roar requests are consumed atomically.
 cp 3
 ret nz
 ld a,(speech_active)
 cp 3
 jr nz,roar_accept
 ld a,(speech_left)
 or a
 jr z,roar_accept
 xor a
 ld (speech_pending),a
 ret
roar_accept:
 ld a,3
 ret
roar_mix:
roar_impact:
 ld a,(speech_active)
 cp 3
 jr nz,roar_done
 ld hl,$7f53
 ld a,(hl)
 or a
 jr z,roar_done
 dec (hl)
 ; A short descending noise attack shares C; A/B continue the roar.
 add a,3
 ld ($587e),a
 ld a,16
 sub (hl)
 ld ($587a),a
 ld a,($587b)
 and $1b
 or $24
 ld ($587b),a
roar_done:
 ld hl,$5874
 ret
roar_shape:
 ld a,(speech_active)
 cp 3
 ret nz
 ld a,($5881)
 cp 255
 ret z
 ld bc,$fff5
 ld e,13
 out (c),e
 inc c
 out (c),a
 ret
 ASSERT $ <= $7fd0
