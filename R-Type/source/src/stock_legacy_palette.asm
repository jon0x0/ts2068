; Global native colour refresh must recognize compact dictionary cells.
dictionary_cell EQU DICT_CODE
 ORG LEGACY_CODE
single:
 CALL dictionary_cell
 JR NC,plain_single
 PUSH HL
 LD H,D
 LD L,E
 CALL $0206
 POP HL
 RET
plain_single:
 BIT 7,A
 JR NZ,indexed
 AND $3F
 RET
indexed:
 PUSH HL
 PUSH BC
 AND $7F
 LD L,A
 LD H,0
 ADD HL,HL
 ADD HL,HL
 ADD HL,HL
 LD BC,$FBD0
 ADD HL,BC
 LD C,IYL
 LD B,0
 ADD HL,BC
 LD A,(HL)
 POP BC
 POP HL
 RET
bulk:
 CALL dictionary_cell
 JR NC,plain_bulk
 PUSH HL
 PUSH BC
 LD B,8
row:
 PUSH BC
 LD H,D
 LD L,E
 CALL $0206
 SET 5,D
 LD (DE),A
 RES 5,D
 INC D
 POP BC
 DJNZ row
 LD A,D
 SUB 8
 LD D,A
 POP BC
 POP HL
 RET
plain_bulk:
 BIT 7,A
 JP NZ,$0E44
 AND $3F
 JP $0E7B
 ASSERT $ <= LEGACY_CODE+96
