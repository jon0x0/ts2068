; Resident DOCK4 data remains readable while the DOCK6 SFX decoder runs.
; Placed before aligned scanline tables, using space freed from diagnostics.
player_impact_data:
 INCBIN "../../assets/sfx-player-impact-real.packed"
player_impact_chain:
 ; Called on the 31st audio interrupt: allow the selected half-second attack to finish.
 ld a,5
 ld (sfx_pending),a
 jp sfx_available
death_attack:
 ld a,($7bfb)
 cp 1
 jp nz,death_burst
 ; Show the death burst immediately; the audio lead-in is independent.
 call death_burst
 push af
 ld a,6
 jp sfx_request
death_sound:
 ; First player burst is already started by the interrupt-driven audio chain.
 ; Do not restart it or shorten the impact when physics catches up in a batch.
 ld a,($7bfb)
 cp 1
 jr nz,death_sound_blast
 ; Player death uses one alternating travelling burst per wave. Two stacked
 ; explosions at contact unnecessarily force extra Sinistar composition.
 xor a
 ld ($783e),a
 ld a,($7bfd)
 and 1
 jr nz,death_sound_player
 ld a,($783c)
 ld (worker_x),a
 ld a,($7c9e)
 ld ($7c98),a
death_sound_player:
 ld a,($7bfd)
 cp 1
 ret z
 ; Subsequent visual waves must not cut short the half-second attack.
 ld a,(sfx_active)
 cp 6
 ret z
 ld a,(sfx_pending)
 cp 6
 ret z
death_sound_blast:
 jp sfx_explosion
