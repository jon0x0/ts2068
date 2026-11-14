 ORG DICT_CODE
dictionary_cell:
 PUSH HL
 PUSH AF
 LD A,D
 AND $18
 RRCA
 RRCA
 RRCA
 ADD A,$81
 LD H,A
 LD L,E
 BIT 5,(HL)
 JR Z,ordinary
 POP AF
 POP HL
 SCF
 RET
ordinary:
 POP AF
 POP HL
 OR A
 RET
 ASSERT $ <= DICT_CODE+40
