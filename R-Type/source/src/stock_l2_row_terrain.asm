; Match TAP L2 fixed screen-row inks; native cell tokens retain the row index.
 ORG $08C0
 DS $08F0-$,$FF
select_group_row:
 PUSH BC
 PUSH HL
 LD C,A
 LD B,0
 LD HL,ROW_MAP
 LD A,($7A84)
 CP 56
 JR C,row_map_ready
 LD A,C
 CP 7
 JR C,row_map_ready
 LD HL,BOSS_MAP-7
row_map_ready:
 ADD HL,BC
 LD A,(HL)
 POP HL
 POP BC
 RET
 DS $0920-$,$FF
initial_group_attribute:
 BIT 7,A
 RET Z
 PUSH BC
 PUSH DE
 PUSH HL
 LD C,A
 LD A,(BODY_CONTEXT)
 CP 3
 JR Z,initial_done
 LD A,H
 CP TILE_START_HI
 JR C,initial_done
 CP TILE_END_HI
 JR NC,initial_done
 LD A,D
 AND 3
 RLCA
 RLCA
 RLCA
 LD B,A
 LD A,E
 AND $E0
 RLCA
 RLCA
 RLCA
 OR B
 CALL select_group_row
 OR $80
 LD C,A
initial_done:
 LD A,C
 POP HL
 POP DE
 POP BC
 RET
 DS $0990-$,$FF
prepare_group_column:
 LD HL,$5E00
 RET
 DS $09D0-$,$FF
apply_group_column:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 LD A,(HL)
 BIT 7,A
 JR Z,apply_done
 LD A,IXL
 SUB $80
 SRL A
 SRL A
 CALL select_group_row
 OR $80
 LD (HL),A
apply_done:
 POP HL
 POP DE
 POP BC
 POP AF
 RET
 DS $0A08-$,$FF
