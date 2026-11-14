; Fixed-ROM pointer to a 256-row page of packed palette-pair IDs.
 ORG PALETTE_POINTER_CODE
palette_pointer:
 PUSH BC
 PUSH DE
 LD B,L
 LD E,H
 LD D,0
 LD L,H
 LD H,0
 ADD HL,HL
 ADD HL,DE
 LD DE,PALETTE_PAGE_DIRECTORY
 ADD HL,DE
 LD C,(HL)
 INC HL
 LD E,(HL)
 INC HL
 LD D,(HL)
 LD L,B
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,DE
 LD A,C
 POP DE
 POP BC
 RET
