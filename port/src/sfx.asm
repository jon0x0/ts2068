; speech2ay harmonic1 effects, boot-cached in HOME 5C40..5E9C.
; All playback stays in HOME/resident code: safe during fast preparation.
sfx_pending EQU $5860
sfx_active EQU $5861
sfx_left EQU $5862
sfx_ptr EQU $5863
sfx_shot:
 push af
 ld a,1
 jr sfx_request
sfx_pickup:
 push af
 ld a,2
 jr sfx_request
sfx_assembly:
 push af
 ld a,3
 jr sfx_request
sfx_bomb:
 push af
 ld a,4
sfx_request:
 push bc
 ld b,a
 ld a,(speech_left)
 or a
 jr nz,sfx_reject
 ld a,(speech_active)
 or a
 jr nz,sfx_reject
 ld a,(speech_pending)
 or a
 jr nz,sfx_reject
 ld a,b
 cp 1
 jr nz,sfx_accept
 ld a,(sfx_pending)
 cp 2
 jr nc,sfx_reject
 ld a,(sfx_active)
 cp 2
 jr nc,sfx_reject
sfx_accept:
 ld a,b
 ld (sfx_pending),a
sfx_reject:
 pop bc
 pop af
 ret
sfx_tick:
 ld a,(speech_active)
 or a
 jr z,sfx_available
 xor a
 ld (sfx_pending),a
 ld (sfx_active),a
 ld (sfx_left),a
 ret
sfx_available:
 ld a,(sfx_pending)
 or a
 jr z,sfx_continue
 ld (sfx_active),a
 dec a
 ld e,a
 add a,a
 add a,e
 ld e,a
 ld d,0
 ld hl,sfx_clips
 add hl,de
 ld a,(hl)
 ld (sfx_left),a
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld (sfx_ptr),de
 xor a
 ld (sfx_pending),a
 ld e,9
 call sfx_zero
 ld e,10
 call sfx_zero
sfx_continue:
 ld a,(sfx_left)
 or a
 jr nz,sfx_frame
 ld a,(sfx_active)
 or a
 ret z
 xor a
 ld (sfx_active),a
 ld e,8
 jp sfx_zero
sfx_frame:
 ld hl,(sfx_ptr)
 ld e,0
sfx_register:
 ld a,(hl)
 inc hl
 ld bc,$fff5
 out (c),e
 inc c
 out (c),a
 inc e
 ld a,e
 cp 2
 jr nz,sfx_next
 ld e,6
sfx_next:
 cp 9
 jr nz,sfx_register
sfx_frame_done:
 ld (sfx_ptr),hl
 ld hl,sfx_left
 dec (hl)
 ret
sfx_zero:
 xor a
 ld bc,$fff5
 out (c),e
 inc c
 out (c),a
 ret
 INCLUDE "../build/sfx-clips.asm"
