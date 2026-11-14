; Permanent stock-ROM0 lifecycle bridges, no expanded-RAM bank assumptions.
 ORG $1000
 JP initialize
 JP irq_player
 JP copy_player
 JP sync_player
 JP collision_player
 JP reset_player
initialize:
 DI
 LD A,3
 OUT ($F4),A
 CALL reset_player
 XOR A
 LD ($FC63),A
 EI
 JP $8634
reset_player:
 LD HL,PHASE_SOURCE
 LD DE,PHASE_DEST
 LD A,PHASE_MASK
 CALL $000A
 LD HL,$5B00
 LD BC,$1FF
 CALL clear_bytes
 LD HL,OWNER_MAP
 CALL clear_world_map
 LD HL,$7E00
 CALL clear_world_map
 LD HL,$8100
 CALL clear_world_map
 IF LEVEL_NUM == 2
 LD HL,BODY_STATE
 LD BC,319
 CALL clear_bytes
 ENDIF
; STOCK_MOTION_RESET_HOOK
 CALL $1B26
 RET
irq_player:
 CALL $F930
 LD A,(FLAGS+13)
 CP 2
 JR Z,irq_regular
 OR A
 JR NZ,busy_input
irq_regular:
 ; Match the TAP gateway: redraw on alternate IRQs, capture input on both.
 LD A,(FLAGS+5)
 XOR 1
 LD (FLAGS+5),A
 JR NZ,sample_input
 LD A,(FLAGS+2)
 OR A
 JR Z,irq_done
 CALL $8B06
 CALL $2400
 ; The fine-player engine submits short shots through FLAGS+8. Consume
 ; that request here, as the expanded gateway does, before advancing bolts.
 LD A,(FLAGS+8)
 OR A
 JR Z,no_short_shot
 XOR A
 LD (FLAGS+8),A
 LD DE,(FLAGS+9)
 CALL $9D5C
no_short_shot:
 JR projectile_clock
sample_input:
 LD A,(FLAGS+2)
 OR A
 JR Z,irq_done
 CALL $8B06
 CALL $240C
projectile_clock:
 LD A,(FLAGS+3)
 OR A
 LD A,1
 JR Z,clock_ready
 LD A,4
clock_ready:
 CALL $0D90
 JR irq_done
busy_input:
 LD A,(FLAGS+2)
 OR A
 JR Z,irq_done
 CALL $8B06
 CALL $240C
irq_done:
 LD HL,$7A8A
 RET
copy_player:
 PUSH AF
 DI
 IF LEVEL_NUM == 2
 CALL $0C09
 ENDIF
 CALL $2403
 XOR A
 CALL $0D90
 EI
 CALL $8842
 DI
 IF LEVEL_NUM == 2
 CALL $0C12
 ENDIF
 CALL $2406
 EI
 POP AF
 RET
sync_player:
 DI
 CALL $2409
 EI
 JP $9559
collision_player:
 LD A,(FLAGS+4)
 OR A
 JP NZ,$91F2
 JP $9577
clear_world_map:
 LD BC,639
clear_bytes:
 LD D,H
 LD E,L
 INC DE
 LD (HL),0
 LDIR
 RET
 ASSERT $ <= $10F0
