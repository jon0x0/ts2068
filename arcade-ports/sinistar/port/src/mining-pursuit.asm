; Source chase core with Task8 decisions and per-tick position integration.
; Sector/orbit and camera adapters remain pending.
sini_think_phase EQU $5882
sini_stun EQU $5883
face_x EQU $78c6
face_y EQU $78c8
face_vx EQU $78ca
face_vy EQU $78cc
face_oldx EQU $78ce
face_oldy EQU $78cf
mining_pursuit_step:
 ld a,($5e7b)
 or a
 ret nz
 ld hl,world_extension+18
 jp world_call
