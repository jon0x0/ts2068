; Packed speech2ay harmonic1 effects, HOME 5C40 below radar at 5EA0.
 INCLUDE "../build/effects-origin.asm"
; HOME stream data, resident scheduler, DOCK6 decoder; safe with high-RAM stack.
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
 jr sfx_request
sfx_explosion:
 push af
 ld a,5
sfx_request:
 push bc
 ld b,a
 ld a,(speech_left)
 ld c,a
 ld a,(speech_active)
 or c
 ld c,a
 ld a,(speech_pending)
 or c
 jr nz,sfx_reject
 ld a,b
 cp 1
 jr nz,sfx_accept
 ld a,(sfx_pending)
 cp 2
 jr nc,sfx_reject
 ld a,(sfx_active)
 ; Preserve the blast attack, but allow the next real shot to cut its tail.
 ; Explosion has 63 three-refresh blocks: left < 60 after ten refreshes.
 ; Other event sounds retain priority, and speech always wins above.
 cp 5
 jr nz,sfx_other_active
 ld a,(sfx_left)
 cp 60
 jr c,sfx_accept
 jr sfx_reject
sfx_other_active:
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
 ld ($5c26),a
 ld e,9
 call sfx_zero
 ld e,10
 call sfx_zero
sfx_continue:
 ld hl,$5c26
 ld a,(hl)
 or a
 jr z,sfx_hold_done
 dec (hl)
 ret
sfx_hold_done:
 ld a,(sfx_left)
 or a
 jr nz,sfx_frame
 ld a,(sfx_active)
 or a
 ret z
 cp 6
 jp z,player_impact_chain
 xor a
 ld (sfx_active),a
 ld e,8
 jp sfx_zero
sfx_frame:
 ld a,$50
 out ($f4),a
 ld hl,(sfx_ptr)
 call world_extension+105
 ld a,(sfx_active)
 cp 5
 jr nz,sfx_frame_done
 ld a,2
 ld ($5c26),a
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
