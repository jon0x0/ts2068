; Stock HOME backend for the current player engine. Fixed entry jump table.
 ORG $0200
 JP to_work
 JP from_work
 JP future_attribute
 JP merge_player_attributes

to_work:
 PUSH AF
 LD A,H
 ADD A,$66
 LD H,A
 POP AF
 RET
from_work:
 PUSH AF
 LD A,H
 SUB $66
 LD H,A
 POP AF
 RET

; HL is a screen4000 or workingA600 raster address. Return clean source attr.
future_attribute:
 PUSH BC
 PUSH DE
 PUSH HL
 LD A,H
 CP $A0
 JR C,normal_address
 SUB $66
 LD H,A
normal_address:
 LD A,H
 AND 7
 LD B,A
 LD A,H
 AND $18
 RRCA
 RRCA
 RRCA
 ADD A,$78
 LD D,A
 LD E,L
 LD A,(DE)
 LD C,A
 LD A,D
 ADD A,9
 LD D,A
 LD A,(DE)
 BIT 5,A
 JR NZ,dictionary_attribute
 BIT 6,A
 JR NZ,terrain_attribute
 LD A,C
 AND $7F
 JR attribute_done
dictionary_attribute:
 LD D,A
 AND $80
 JR Z,dictionary_forward
 LD A,B
 XOR 7
 LD B,A
dictionary_forward:
 LD A,D
 AND 4
 RRCA
 RRCA
 LD H,A
 LD L,C
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,PALETTE_BASE
 ADD HL,DE
 LD E,B
 LD D,0
 ADD HL,DE
 LD A,$23
 OUT ($F4),A
 LD A,(HL)
 PUSH AF
 LD A,3
 OUT ($F4),A
 POP AF
 JR attribute_done
terrain_attribute:
 LD A,C
 AND $7F
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD DE,$FBD0
 ADD HL,DE
 LD E,B
 LD D,0
 ADD HL,DE
 LD A,(HL)
attribute_done:
 POP HL
 POP DE
 POP BC
 RET

; Called after native background colour publication, with original screen HL.
; The compact background tokens stay clean; merge the current ship per raster.
merge_player_attributes:
 LD A,($BE00)
 CP 2
 RET NZ
 LD A,(CLOCK_FLAGS+2)
 DEC A
 RET NZ
 LD A,(PLAYER_STATE+4)
 OR A
 RET Z
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IY
 LD A,(PLAYER_STATE)
 RRCA
 RRCA
 RRCA
 AND 31
 LD B,A
 LD A,L
 AND 31
 SUB B
 CP 4
 JR NC,merge_done
 LD IYH,A
 LD A,H
 AND $18
 RLCA
 RLCA
 RLCA
 LD E,A
 LD A,L
 AND $E0
 RRCA
 RRCA
 OR E
 LD E,A
 LD A,(PLAYER_STATE+1)
 LD D,A
 LD A,E
 SUB D
 LD IYL,A
 SET 5,H
 LD B,8
merge_row:
 LD A,IYL
 CP 8
 JR NC,next_row
 PUSH HL
 PUSH BC
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 LD A,IYH
 LD E,A
 LD D,0
 ADD HL,DE
 LD DE,(PLAYER_STATE+$12)
 ADD HL,DE
 PUSH HL
 LD DE,64
 ADD HL,DE
 LD A,(HL)
 OR A
 POP HL
 JR Z,empty_mask
 LD DE,32
 ADD HL,DE
 LD A,(HL)
 POP BC
 POP HL
 LD (HL),A
 JR next_row
empty_mask:
 POP BC
 POP HL
next_row:
 INC H
 INC IYL
 DJNZ merge_row
merge_done:
 POP IY
 POP HL
 POP DE
 POP BC
 RET
 ASSERT $ <= $0400
