; 80 compact cells replace 640 expanded raster attributes, preserving the64-row
; player movement window. Tokens and flags are captured together under DI.
snapshot_capture:
 LD A,(PLAYER_STATE+6)
 AND 7
 RET NZ
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IY
 LD A,64
 LD HL,PLAYER_STATE+9
 SUB (HL)
 RRCA
 RRCA
 RRCA
 AND 7
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 LD D,H
 LD E,L
 ADD HL,HL
 ADD HL,HL
 ADD HL,DE
 LD DE,SNAPSHOT_BASE
 ADD HL,DE
 EX DE,HL
 LD HL,(PLAYER_STATE+$1E)
 LD A,H
 SUB $66
 AND $18
 RRCA
 RRCA
 RRCA
 ADD A,$78
 LD H,A
 LD B,10
snapshot_cell:
 LD A,(IY)
 OR A
 JR Z,snapshot_empty
 CP 3
 JR Z,snapshot_empty
 LD C,(HL)
 PUSH HL
 LD A,H
 ADD A,9
 LD H,A
 LD A,(HL)
 POP HL
 JR snapshot_store
snapshot_empty:
 XOR A
 LD C,A
snapshot_store:
 PUSH AF
 LD A,C
 LD (DE),A
 INC DE
 POP AF
 LD (DE),A
 INC DE
 INC HL
 INC IY
 DJNZ snapshot_cell
 POP IY
 POP HL
 POP DE
 POP BC
 POP AF
 RET

snapshot_attribute:
 PUSH BC
 PUSH DE
 PUSH HL
 LD DE,BACKING_PIXELS
 OR A
 SBC HL,DE
 LD B,0
snapshot_row:
 LD DE,80
 OR A
 SBC HL,DE
 JR C,snapshot_row_ready
 INC B
 JR snapshot_row
snapshot_row_ready:
 ADD HL,DE
 LD A,L
 LD C,0
snapshot_raster:
 SUB 10
 JR C,snapshot_column
 INC C
 JR snapshot_raster
snapshot_column:
 ADD A,10
 ADD A,A
 LD E,A
 LD D,0
 PUSH DE
 LD L,B
 LD H,0
 ADD HL,HL
 ADD HL,HL
 LD D,H
 LD E,L
 ADD HL,HL
 ADD HL,HL
 ADD HL,DE
 POP DE
 ADD HL,DE
 LD DE,SNAPSHOT_BASE
 ADD HL,DE
 LD B,C
 LD C,(HL)
 INC HL
 LD A,(HL)
 JP attribute_dispatch
