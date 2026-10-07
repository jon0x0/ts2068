; Two staggered existing explosion slots. Physics pauses while rendering/audio
; continue. HOME 7BFB kind (1 player,2 Sinistar), 7BFC timer, 7BFD wave.
; HOME 5E72..75 keeps the 9-bit world center, independent of camera projection.
death_start:
 ld ($7bfb),a
 ld b,a
 ld a,96
 ld ($7bfc),a
 xor a
 ld ($7bfd),a
 ld (bullet_alive),a
 ld a,(bs_active)
 or a
 jr z,death_no_bomb
 ld hl,bs_expired
 inc (hl)
death_no_bomb:
 xor a
 ld (bs_active),a
 ld (worker_mission),a
 ld (crystal_alive),a
 ld hl,0
 ld (pvx),hl
 ld (pvy),hl
 ld a,b
 cp 2
 ld a,($7c96)
 ld hl,px+1
 ld de,$7c97
 jr nz,death_center
 ld a,($7c9a)
 ld hl,face_x+1
 ld de,$7c9b
death_center:
 ld b,a
 ld c,(hl)
 ld ($5e72),bc
 inc hl
 inc hl
 ld c,(hl)
 ld a,(de)
 ld b,a
 ld ($5e74),bc
 jp death_attack
death_tick:
 ld hl,$7bfc
 dec (hl)
 jr z,death_finish
 ld a,(hl)
 cp 97
 jr nc,death_hold
 and 15
 call z,death_burst
 ld hl,$5c27
 ld a,(hl)
 or a
 jr z,death_hold
 dec (hl)
death_hold:
 scf
 ret
death_finish:
 ld a,($7bfb)
 push af
 xor a
 ld ($7bfb),a
 ld (worker_alive),a
 ld ($783e),a
 ld a,60
 ld (worker_delay),a
 pop af
 cp 2
 jr z,death_victory
 call game_death_done
 scf
 ret
death_victory:
 ld a,1
 ld (game_status),a
 scf
 ret
death_burst:
 ld a,2
 ld (worker_alive),a
 ld a,32
 ld ($5c27),a
 ld a,4
 ld ($783e),a
 ld a,10
 ld ($783f),a
 ; Player burst expands across the screen. Sinistar stays within his body.
 ld a,($7bfd)
 ld b,a
 add a,a
 add a,a
 add a,a
 ld c,a
 ld a,($7bfb)
 cp 2
 ld a,c
 jr z,death_radius
 add a,a
death_radius:
 ld e,a
 ld d,0
 ld hl,($5e72)
 push hl
 or a
 sbc hl,de
 ld a,l
 ld (worker_x),a
 ld a,h
 and 1
 ld ($7c98),a
 pop hl
 add hl,de
 ld a,l
 ld ($783c),a
 ld a,h
 and 1
 ld ($7c9e),a
 ld a,b
 and 3
 add a,a
 add a,a
 add a,a
 ld e,a
 ld hl,($5e74)
 add hl,de
 ld a,l
 ld (worker_y),a
 ld ($783d),a
 ld a,h
 and 1
 ld ($7c99),a
 ld ($7c9f),a
 ld hl,$7bfd
 inc (hl)
 jp death_sound
