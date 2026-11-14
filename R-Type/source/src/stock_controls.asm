; Native menu/game controls on permanent ROM; selected gameplay bindings retained.
 ORG CONTROL_CODE
main_poll:
 CALL pause_poll
 IF LEVEL_NUM == 4
 CALL recover_pickups
 ENDIF
 CALL boss_poll
 JP $8B06
pause_poll:
 LD A,($7AA4)
 OR A
 RET Z
 LD BC,$DFFE
 IN A,(C)
 AND 1
 RET NZ
 LD HL,$BD80
 LD B,6
binding:
 LD A,(HL)
 INC HL
 CP $DF
 JR NZ,next_binding
 LD A,(HL)
 CP 1
 JR NZ,next_binding
 LD BC,$FEFE
 IN A,(C)
 AND 1
 RET NZ
 JR pause
next_binding:
 INC HL
 DJNZ binding
pause:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 DI
 LD HL,PAUSE_AY
 CALL mute
 LD HL,PAUSE_PIXELS
 LD DE,$486D
 LD B,8
save_row:
 LD C,6
save_cell:
 LD A,(DE)
 LD (HL),A
 INC HL
 SET 5,D
 LD A,(DE)
 LD (HL),A
 INC HL
 LD A,7
 LD (DE),A
 RES 5,D
 INC E
 DEC C
 JR NZ,save_cell
 LD A,E
 SUB 6
 LD E,A
 INC D
 DJNZ save_row
 LD HL,font
 LD DE,$486D
 LD B,8
paint_row:
 LD C,6
paint_cell:
 LD A,(HL)
 INC HL
 LD (DE),A
 INC E
 DEC C
 JR NZ,paint_cell
 LD A,E
 SUB 6
 LD E,A
 INC D
 DJNZ paint_row
 CALL released
wait_press:
 CALL read_p
 JR NZ,wait_press
 CALL released
 LD HL,PAUSE_PIXELS
 LD DE,$486D
 LD B,8
restore_row:
 LD C,6
restore_cell:
 LD A,(HL)
 INC HL
 LD (DE),A
 SET 5,D
 LD A,(HL)
 INC HL
 LD (DE),A
 RES 5,D
 INC E
 DEC C
 JR NZ,restore_cell
 LD A,E
 SUB 6
 LD E,A
 INC D
 DJNZ restore_row
 LD HL,PAUSE_AY
 CALL volume
 POP HL
 POP DE
 POP BC
 POP AF
 ; Main-loop pause temporarily borrows the decoded frame cache, never font.
 ; No decoded frame remains valid after restoring its saved screen bytes.
 PUSH AF
 XOR A
 LD (FRAME_VALID),A
 POP AF
 EI
 RET
released:
 CALL read_p
 JR Z,released
 RET
read_p:
 LD BC,$DFFE
 IN A,(C)
 AND 1
 RET
mute:
 LD D,3
 LD E,8
 LD BC,$FFF5
save_volume:
 LD A,E
 OUT (C),A
 INC C
 IN A,(C)
 LD (HL),A
 XOR A
 OUT (C),A
 INC HL
 DEC C
 INC E
 DEC D
 JR NZ,save_volume
 RET
volume:
 LD D,3
 LD E,8
 LD BC,$FFF5
restore_volume:
 LD A,E
 OUT (C),A
 INC C
 LD A,(HL)
 OUT (C),A
 INC HL
 DEC C
 INC E
 DEC D
 JR NZ,restore_volume
 RET
boss_poll:
 LD A,($7AA4)
 SUB 2
 CP 3
 RET NC
 LD BC,$7FFE
 IN A,(C)
 AND $10
 JR NZ,boss_release
 LD A,($FD4B)
 CP 2
 JR Z,boss_jump
 OR A
 RET NZ
 INC A
 LD ($FD4B),A
 RET
boss_release:
 LD A,($FD4B)
 CP 1
 JR Z,boss_arm
 CP 2
 RET Z
 ; Cold HOME contains inherited code at FD4B, not initialized latch RAM.
 ; Neutral input clears both the completed chord and any invalid value.
 XOR A
 LD ($FD4B),A
 RET
boss_arm:
 INC A
 LD ($FD4B),A
 RET
boss_jump:
 DI
 LD A,3
 LD ($FD4B),A
 CALL $100F
 LD HL,EVENT_PTR
 LD ($C4AF),HL
 LD A,START_COLUMN
 LD ($C4AE),A
 CALL $1435
 CALL $8721
 LD A,PRIOR_SETTING
 LD ($7A9E),A
 CALL $8BAE
 CALL spawn_pickups
 RET
recover_pickups:
 LD A,($7A84)
 CP 73
 RET C
spawn_pickups:
 LD A,($7ABE)
 CP 2
 RET NC
 LD A,($7AC1)
 LD HL,$7AC5
 OR (HL)
 RET NZ
 LD HL,$0002
 LD ($7AC1),HL
 LD ($7AC5),HL
 LD HL,$0A0C
 LD ($7AC3),HL
 LD L,$0E
 LD ($7AC7),HL
 RET
font:
 INCBIN "build/fullgame/visible_hits_r145/level05_region.bin",$8B70,48
 ASSERT $ <= CONTROL_CODE+512
