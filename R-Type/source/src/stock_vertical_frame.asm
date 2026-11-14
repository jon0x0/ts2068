; Reconstruct an exact vertical TAP phase from its full bitmap parent.
 ORG VERTICAL_CODE
vertical_frame:
 LD A,(CTX+18)
 LD (CTX+32),A
 LD A,C
 LD (CTX+34),A
 LD (CTX+26),A
 CALL READ_STREAM_BYTE
 PUSH AF
 CALL READ_STREAM_BYTE
 LD (CTX+33),A
 LD (CTX+44),HL
 POP AF
 CALL DIRECT_FRAME
 LD A,E
 LD (CTX+30),A
 LD C,E
 LD B,D
 LD A,D
 LD (CTX+31),A
 XOR A
parent_count:
 ADD A,C
 DJNZ parent_count
 LD B,A
 LD HL,(BITS)
 LD DE,DENSE_PARENT
parent_cell:
 LD A,(HL)
 INC HL
 CP 54
 JR Z,parent_blank
 LD C,8
parent_byte:
 LD A,(HL)
 LD (DE),A
 INC HL
 INC DE
 DEC C
 JR NZ,parent_byte
 JR parent_next
parent_blank:
 XOR A
 LD C,8
parent_zero:
 LD (DE),A
 INC DE
 DEC C
 JR NZ,parent_zero
parent_next:
 DJNZ parent_cell
 LD HL,(CTX+44)
 LD A,(CTX+34)
 OR 3
 LD C,A
 CALL UNPACK_FRAME
 LD HL,CACHE+2
 LD A,(HL)
 INC HL
 ADD A,A
 LD E,A
 LD D,0
 ADD HL,DE
 LD (CTX+38),HL
 LD A,(CACHE)
 LD C,A
 LD A,(CACHE+1)
 LD B,A
 XOR A
metadata_count:
 ADD A,C
 DJNZ metadata_count
 LD B,A
 LD C,A
 PUSH HL
 POP DE
expand_size:
 LD A,(HL)
 INC HL
 INC DE
 CP 54
 JR Z,expand_size_next
 PUSH HL
 LD HL,8
 ADD HL,DE
 EX DE,HL
 POP HL
expand_size_next:
 DJNZ expand_size
 DEC HL
 DEC DE
 LD B,C
expand_cell:
 LD C,(HL)
 DEC HL
 LD A,C
 CP 54
 JR Z,expand_tag
 PUSH BC
 LD B,8
 XOR A
expand_zero:
 LD (DE),A
 DEC DE
 DJNZ expand_zero
 POP BC
expand_tag:
 LD A,C
 LD (DE),A
 DEC DE
 DJNZ expand_cell
 LD A,(CTX+32)
 LD (CTX+18),A
 LD HL,CACHE+2
 LD A,(HL)
 INC HL
 ADD A,A
 LD E,A
 LD D,0
 ADD HL,DE
 PUSH IX
 PUSH IY
 PUSH HL
 POP IY
 LD IX,DENSE_PARENT
 LD A,(CACHE)
 LD C,A
 LD A,(CACHE+1)
 LD B,A
 XOR A
target_count:
 ADD A,C
 DJNZ target_count
 LD B,A
 XOR A
 LD (CTX+35),A
 LD (CTX+37),A
shift_cell:
 LD A,(IY)
 INC IY
 CP 54
 JR Z,next_cell
 PUSH BC
 LD A,(CTX+33)
 LD B,A
 LD A,(CTX+35)
 OR A
 JR Z,previous_blank
 PUSH IX
 POP HL
 LD A,(CTX+30)
 ADD A,A
 ADD A,A
 ADD A,A
 LD E,A
 LD D,0
 OR A
 SBC HL,DE
 LD A,8
 SUB B
 LD E,A
 ADD HL,DE
 CALL copy_segment
 JR current_segment
previous_blank:
 CALL zero_segment
current_segment:
 LD A,(CTX+33)
 LD C,A
 LD A,8
 SUB C
 LD B,A
 LD A,(CTX+31)
 LD C,A
 LD A,(CTX+35)
 CP C
 JR NC,current_blank
 PUSH IX
 POP HL
 CALL copy_segment
 JR cell_done
current_blank:
 CALL zero_segment
cell_done:
 POP BC
next_cell:
 LD DE,8
 ADD IX,DE
 LD A,(CTX+37)
 INC A
 LD C,A
 LD A,(CTX+30)
 CP C
 LD A,C
 JR NZ,same_row
 XOR A
 LD C,A
 LD A,(CTX+35)
 INC A
 LD (CTX+35),A
 LD A,C
same_row:
 LD (CTX+37),A
 DJNZ shift_cell
 POP IY
 POP IX
 JP CACHED_FRAME
copy_segment:
 LD A,(HL)
 LD (IY),A
 INC HL
 INC IY
 DJNZ copy_segment
 RET
zero_segment:
 XOR A
zero_byte:
 LD (IY),A
 INC IY
 DJNZ zero_byte
 RET
