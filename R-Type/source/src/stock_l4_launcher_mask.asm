 ORG MASK_CODE
 LD (PS+143),A
 LD B,9
 LD C,3
mask_cell:
 SRL D
 RR E
 LD A,(PS+143)
 BIT 0,A
 JR NZ,restore_owner
 LD A,(HL)
 CP $FA
 JR NZ,next_cell
 SET 0,D
 JR next_cell
restore_owner:
 JR NC,next_cell
 LD (HL),$FA
next_cell:
 INC HL
 DEC C
 JR NZ,mask_row_done
 LD C,3
 LD A,L
 ADD A,29
 LD L,A
 JR NC,mask_row_done
 INC H
mask_row_done:
 DJNZ mask_cell
 RET
