; FALS/N1ALL.SRC SinCon/TAUNT, SAM/FUNCTION.SRC RAND8, WITT/ANISINI.SRC.
; HOME 5C2E voice mapping, 2F Task64 timer, 30 RnSpch, 31..34 RNG,
; 35 out-of-sector, 36 prior out-of-sector, 37..38 mouth cursor,
; 3A awakening clock. The current wrapped world is one scanner sector.
wb_speech_start:
 ld a,(speech_active)
 dec a
 ld l,a
 ld h,0
 add hl,hl
 push hl
 add hl,hl
 ld de,wb_speech_clips
 add hl,de
 ld a,(hl)
 ld (speech_left),a
 inc hl
 ld a,(hl)
 ld ($5c2e),a
 inc hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld (speech_ptr),de
 pop hl
 ld de,wb_mouth_tables
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld ($5c37),de
 xor a
 ld (awake_timer),a
 ld ($5c3d),a
 ld ($5c3c),a
 ret
wb_taunt_step:
 ld a,($5c3d)
 ld (awake_mouth),a
 ld a,(awake_done)
 or a
 jr nz,wb_taunt_clock
 ld hl,$5c3a
 inc (hl)
 ld a,(hl)
 cp wb_awakening_ticks
 jr c,wb_taunt_clock
 ld a,1
 ld (awake_done),a
wb_taunt_clock:
 ld a,($5c35)
 ld hl,$5c36
 cp (hl)
 ld (hl),a
 jr z,wb_taunt_periodic
 or a
 jr z,wb_taunt_choose
wb_taunt_periodic:
 ld hl,$5c2f
 inc (hl)
 ld a,(hl)
 and 63
 ret nz
 ld hl,$5c33
 call wb_taunt_random
 cp $39
 ret nc
wb_taunt_choose:
 ld hl,$5c31
 call wb_taunt_random
 and $7f
 ld hl,$5c30
 add a,(hl)
 ld (hl),a
wb_taunt_select:
 ld b,4
 cp $29
 jr c,wb_taunt_request
 inc b
 cp $51
 jr c,wb_taunt_request
 inc b
 cp $79
 jr c,wb_taunt_request
 inc b
 cp $a1
 jr c,wb_taunt_request
 inc b
 cp $c9
 jr c,wb_taunt_request
 ld b,3
wb_taunt_request:
 di
 call wb_taunt_guard
 ei
 ret
wb_taunt_guard:
 ld a,(sinistar_built)
 or a
 ret z
 ld a,(game_status)
 ld c,a
 ld a,($5c35)
 or c
 ld c,a
 ld a,(invulnerable)
 or c
 ret nz
 ld a,(lives)
 or a
 ret z
 ld a,(bs_hits)
 cp 13
 ret nc
 ld a,(speech_pending)
 or a
 ret nz
 ld a,b
 cp 3
 jr z,wb_taunt_publish ; AniSCS allows a roar to interrupt speech.
 ld a,(speech_left)
 ld c,a
 ld a,(speech_active)
 or c
 ret nz
wb_taunt_publish:
 ld a,b
 ld (speech_pending),a
 ret
; Exact RAND8 feedback and high-byte result; independent nonzero seeds.
; Other arcade systems also consume its shared seeds; draw order is adapted.
wb_taunt_random:
 push hl
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld a,d
 or e
 jr nz,wb_random_seeded
 ld de,$ace1
wb_random_seeded:
 ld a,d
 add a,a
 xor d
 add a,a
 add a,a
 rl e
 rl d
 pop hl
 ld (hl),e
 inc hl
 ld (hl),d
 ld a,d
 ret
wb_mouth_tick:
 ld a,(speech_active)
 or a
 ret z
 ld a,(speech_left)
 or a
 ret z
 ld hl,awake_timer
 ld a,(hl)
 or a
 jr z,wb_mouth_next
 dec (hl)
 ret nz
wb_mouth_next:
 ld hl,($5c37)
 ld a,(hl)
 cp 255
 ret z
 ld ($5c3d),a
 inc hl
 ld a,(hl)
 ld (awake_timer),a
 inc hl
 ld ($5c37),hl
 ret
 INCLUDE "../build/taunt-tables.asm"
