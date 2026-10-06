; Frame-rate AY speech2ay streams from complete archived arcade recordings.
 INCLUDE "../build/speech-source.asm"
speech_left EQU $78f8
speech_ptr EQU $78fa
speech_started EQU $78fc
speech_pending EQU $78fd ; 1 assembly, 2 player death, 3 Sinibomb hit
speech_active EQU $78fe
speech_init:
 ld a,$10
 ld ($78df),a
 ret
; Foreground requests are a single-byte publication; ISR owns stream state.
speech_hit:
 push af
 ld a,7
 ld ($783f),a
 ld ($783e),a
 ld a,3
 ld (speech_pending),a
 pop af
 ret
speech_death:
 push af
 ld a,10
 ld ($783f),a
 ld ($783e),a
 ld a,(speech_left)
 or a
 jr nz,speech_death_end
 ld a,(speech_pending)
 or a
 jr nz,speech_death_end
 ld a,2
 ld (speech_pending),a
speech_death_end:
 pop af
 ret
speech_tick:
 ld a,(speech_pending)
 or a
 jr nz,speech_start
 ld a,(speech_left)
 or a
 jr nz,speech_frame
 ld a,(sinistar_built)
 or a
 ret z
 ld a,(speech_started)
 or a
 jr nz,speech_idle
 inc a
 ld (speech_started),a
speech_start:
 ld (speech_active),a
 dec a
 ld e,a
 add a,a
 add a,e
 ld e,a
 ld d,0
 ld hl,speech_clips
 add hl,de
 ld a,(hl)
 ld (speech_left),a
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld (speech_ptr),de
 xor a
 ld (speech_pending),a
speech_frame:
 ld a,speech_bank
 out ($f4),a
speech_bytes:
 call world_extension+12
 ld e,0
speech_register:
 ld a,(hl)
 inc hl
 ld bc,$fff5
 out (c),e
 ld bc,$fff6
 out (c),a
 inc e
 ld a,e
 cp 13
 jr nz,speech_register
speech_skip_shape:
 ld hl,speech_left
 dec (hl)
 ret
speech_idle:
 ld a,(speech_active)
 or a
 ret z
 xor a
 ld (speech_active),a
 ld e,8
speech_silence:
 ld bc,$fff5
 out (c),e
 ld bc,$fff6
 out (c),a
 inc e
 ld a,e
 cp 11
 ret z
 xor a
 jr speech_silence
