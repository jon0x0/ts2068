; One bounded HOME tile cache serves moving silhouette and stopped rich body.
 ORG BODY_CODE
 JP get_tile
 JP repair
 JP cleanup
get_tile:
 CP 34
 JP C,native_tile
 CP 52
 JR C,moving
 XOR A
 JP native_tile
moving:
 PUSH BC
 PUSH IY
 SUB 34
 LD (CTX+69),A
 LD A,($BE00)
 OR $40
 OUT ($FF),A
 LD A,I
 PUSH AF
 DI
 LD A,(CTX+69)
 LD E,A
 LD D,0
 LD HL,frames
 ADD HL,DE
 LD A,(HL)
 CALL $2006
 LD HL,(PALPTR)
 LD DE,CTX+32
 LD A,(CACHE+2)
 ADD A,A
 LD C,A
 LD B,0
 LDIR
 LD HL,CTX+32
 LD (PALPTR),HL
 LD HL,(BITS)
 LD (CTX+64),HL
 LD HL,CACHE
 LD (CTX+66),HL
 XOR A
 LD (CTX+68),A
cell:
 LD HL,(CTX+64)
 LD A,(HL)
 INC HL
 LD (CTX+64),HL
 LD L,A
 LD H,0
 ADD HL,HL
 LD DE,CTX+32
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 CALL PALETTE_READ
 LD IY,(CTX+64)
 LD DE,(CTX+66)
 INC DE
 XOR A
 LD (CTX+71),A
 LD C,8
line:
 LD B,(HL)
 LD A,B
 AND $38
 JR Z,paper_black
 LD A,B
 AND 7
 LD A,(IY)
 JR Z,invert
 LD A,$FF
 JR store
invert:
 CPL
 JR store
paper_black:
 LD A,B
 AND 7
 LD A,(IY)
 JR NZ,store
 XOR A
store:
 LD (DE),A
 INC DE
 LD B,A
 LD A,(CTX+71)
 OR B
 LD (CTX+71),A
 INC HL
 INC IY
 DEC C
 JR NZ,line
 LD (CTX+64),IY
 LD (CTX+66),DE
 LD HL,-9
 ADD HL,DE
 PUSH HL
 LD A,(CTX+71)
 OR A
 LD A,7
 JR Z,header
 LD A,$86
header:
 POP HL
 LD (HL),A
 LD A,(CTX+68)
 INC A
 LD (CTX+68),A
 CP 16
 JP C,cell
 LD A,3
 LD (CTX+25),A
 XOR A
 LD (CTX+17),A
 LD A,($BE00)
 OUT ($FF),A
 POP AF
 JP PO,keep_di
 EI
keep_di:
 POP IY
 POP BC
 LD HL,CACHE
 RET
native_tile:
 DB NATIVE_GETTER
repair:
 LD A,($7AA4)
 OR A
 RET Z
 LD A,($7A8E)
 OR A
 RET Z
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IX
 PUSH IY
; IRQ input/music may run while repairing, but must not replace CACHE.
 LD A,(PLAYER_FLAGS+13)
 LD (STATE+10),A
 LD A,1
 LD (PLAYER_FLAGS+13),A
 CALL clear_entrance
 LD A,($7A9C)
 LD (STATE),A
 LD A,($8EBF)
 LD (STATE+1),A
 XOR A
 LD (STATE+2),A
repair_tile:
 XOR A
 LD (STATE+3),A
 LD (STATE+4),A
repair_cell:
 CALL cell_position
 LD L,A
 LD A,D
 ADD A,$7E
 LD H,A
 LD (STATE+8),HL
 LD A,(HL)
 CP $DC
 JR NC,damaged
 OR A
 JP NZ,next_cell
 LD A,H
 ADD A,3
 LD H,A
 LD A,(HL)
 AND 3
 JP Z,next_cell
damaged:
 LD A,(STATE+3)
 OR A
 JR NZ,cached_tile
 DI
 XOR A
 LD (CTX+25),A
 LD A,(STATE+2)
 LD E,A
 LD D,0
 LD HL,frames
 ADD HL,DE
 LD A,(HL)
 CALL $2006
 LD (STATE+6),HL
 LD A,1
 LD (STATE+3),A
cached_tile:
 CALL cell_position
 LD A,C
 CP 31
 JP NC,next_cell
 PUSH BC
 LD A,(STATE+4)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD E,A
 LD D,0
 ADD HL,DE
 LD DE,(STATE+6)
 ADD HL,DE
 LD A,(HL)
 INC HL
 LD (STATE+13),HL
 LD L,A
 LD H,0
 ADD HL,HL
 LD DE,(PALPTR)
 ADD HL,DE
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD (STATE+15),DE
 ; Publish a stable global palette ID, never the frame-local tag.
 LD HL,(STATE+8)
 LD (HL),$FF
 LD A,H
 SUB 6
 LD H,A
 LD (HL),E
 ADD A,9
 LD H,A
 LD A,D
 ADD A,A
 ADD A,A
 OR $21
 LD (HL),A
 ; Write only this background cell into the retained world plane.
 ; Real actor owners were rejected above; the player merges after repair.
 LD A,B
 AND $18
 ADD A,$A6
 LD D,A
 LD A,B
 AND 7
 RRCA
 RRCA
 RRCA
 OR C
 LD E,A
 LD (STATE+17),DE
 LD DE,(STATE+15)
 CALL PALETTE_READ
 PUSH HL
 POP IX
 LD DE,(STATE+17)
 LD HL,(STATE+13)
 LD B,8
 EI
copy_raster:
 LD A,(HL)
 LD (DE),A
 LD C,A
 LD A,D
 SUB $66
 LD D,A
 LD A,C
 LD (DE),A
 SET 5,D
 LD A,(IX)
 LD (DE),A
 RES 5,D
 LD A,D
 ADD A,$66
 LD D,A
 INC IX
 INC HL
 INC D
 DJNZ copy_raster
 DI
 POP BC
 CALL ticket_pointer
 LD (HL),1
next_cell:
 LD A,(STATE+4)
 INC A
 LD (STATE+4),A
 CP 16
 JP C,repair_cell
 LD A,(STATE+2)
 INC A
 LD (STATE+2),A
 CP 18
 JP C,repair_tile
 LD A,(STATE)
 LD ($7A9C),A
 LD A,(STATE+1)
 LD ($8EBF),A
 LD A,(STATE+10)
 LD (PLAYER_FLAGS+13),A
 POP IY
 POP IX
 POP HL
 POP DE
 POP BC
 POP AF
 RET
; Retire the scrolling entrance once. The fixed reveal replaces its old extent.
clear_entrance:
 LD A,(STATE+19)
 OR A
 RET NZ
 INC A
 LD (STATE+19),A
 LD BC,0
clear_world_cell:
 LD A,B
 RRCA
 RRCA
 RRCA
 AND 3
 ADD A,$7E
 LD D,A
 LD A,B
 AND 7
 RRCA
 RRCA
 RRCA
 OR C
 LD E,A
 LD A,(DE)
 CP $FF
 JR NZ,clear_world_next
 XOR A
 LD (DE),A
 LD A,D
 SUB 6
 LD H,A
 LD L,E
 LD (HL),7
 ADD A,9
 LD H,A
 LD (HL),1
 LD A,B
 AND $18
 ADD A,$40
 LD D,A
 PUSH BC
 LD B,8
clear_world_raster:
 XOR A
 LD (DE),A
 SET 5,D
 LD A,7
 LD (DE),A
 RES 5,D
 LD A,D
 ADD A,$66
 LD D,A
 XOR A
 LD (DE),A
 LD A,D
 SUB $66
 LD D,A
 INC D
 DJNZ clear_world_raster
 POP BC
clear_world_next:
 INC C
 LD A,C
 CP 32
 JR NZ,clear_world_cell
 LD C,0
 INC B
 LD A,B
 CP 20
 JR NZ,clear_world_cell
 RET
; BC is the cell coordinate. A is its compact low byte and B its page offset.
cell_position:
 LD A,(STATE+2)
 LD E,A
 LD D,0
 LD HL,coords
 ADD HL,DE
 LD A,(HL)
 LD D,A
 AND 7
 ADD A,A
 ADD A,A
 LD C,A
 LD A,D
 AND $38
 RRCA
 LD B,A
 LD A,(STATE+4)
 LD D,A
 AND 3
 ADD A,C
 LD C,A
 LD A,D
 RRCA
 RRCA
 AND 3
 ADD A,B
 LD B,A
 AND 7
 RRCA
 RRCA
 RRCA
 OR C
 PUSH AF
 LD A,B
 RRCA
 RRCA
 RRCA
 AND 3
 LD D,A
 POP AF
 RET
ticket_pointer:
 LD A,(STATE+2)
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD A,(STATE+4)
 LD E,A
 LD D,0
 ADD HL,DE
 LD DE,TICKETS
 ADD HL,DE
 RET
; Native8842 leaves repaired background cells marked as foreground. Clear only
; our tickets, preserving real actor footprints for the next erase/repair pass.
cleanup:
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 XOR A
 LD (STATE+2),A
clear_tile:
 XOR A
 LD (STATE+4),A
clear_cell:
 CALL ticket_pointer
 LD A,(HL)
 OR A
 JR Z,clear_next
 LD (HL),0
 CALL cell_position
 LD L,A
 LD A,D
 ADD A,$7E
 LD H,A
 LD (HL),0
 ADD A,3
 LD H,A
 LD A,(HL)
 AND $FC
 LD (HL),A
clear_next:
 LD A,(STATE+4)
 INC A
 LD (STATE+4),A
 CP 16
 JR C,clear_cell
 LD A,(STATE+2)
 INC A
 LD (STATE+2),A
 CP 18
 JR C,clear_tile
 POP HL
 POP DE
 POP BC
 POP AF
 RET
frames: DB FRAME_IDS
coords: DB BODY_COORDS
 ASSERT $ <= BODY_CODE+928
