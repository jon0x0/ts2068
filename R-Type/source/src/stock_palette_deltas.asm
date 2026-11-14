; Restore exact ascending global palette IDs after vertical metadata LZ.
 ORG PALETTE_DELTA_CODE
 LD HL,CACHE+2
 LD B,(HL)
 INC HL
 LD A,B
 OR A
 RET Z
 LD DE,0
palette_delta_next:
 LD A,(HL)
 ADD A,E
 LD E,A
 LD (HL),A
 INC HL
 LD A,(HL)
 ADC A,D
 LD D,A
 LD (HL),A
 INC HL
 DJNZ palette_delta_next
 RET
