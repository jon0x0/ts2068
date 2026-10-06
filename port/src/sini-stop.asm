; WITT/SINI.SRC: decrement InStun, then SiStopChk.
; ScreenChk is supplied by the adapter until scanner workspaces are ported.
sini_stun EQU $78a0
sini_grave EQU $78a1
sini_attract EQU $78a2
sini_on_screen EQU $78a3
sini_stop_step:
 ld a,(sini_stun)
 or a
 jr z,sini_stop_check
 dec a
 ld (sini_stun),a
sini_stop_check:
 ld a,(sini_stun)
 or a
 jr nz,sini_stop
 ld a,(sini_grave)
 ld hl,sini_attract
 or (hl)
 jr z,sini_go
 ld a,(sini_on_screen)
 or a
 jr z,sini_go
sini_stop:
 ld hl,0
 ld (svx),hl
 ld (svy),hl
 scf
 ret
sini_go:
 or a
 ret

; Scripted stimulus only, not an arcade collision implementation.
; Once per 1024 physics ticks, pause pursuit for 60 ticks after countdown.
sini_demo_event:
 ld hl,(frames)
 ld a,l
 or a
 ret nz
 ld a,h
 and 3
 cp 2
 ret nz
 ld a,61
 ld (sini_stun),a
 ret
