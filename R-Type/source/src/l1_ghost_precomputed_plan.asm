 ORG $C100
fast_ghost_plan:
 LD A,($DF3E)
 CP 180
 JP C,$DCEF
 CP 183
 JP NC,$DCEF
 LD A,($DF33)
 OR A
 JP NZ,$DCEF
 LD A,($DF34)
 OR A
 JP NZ,$DCEF
 PUSH DE
 PUSH HL
 PUSH HL
 POP IX
 LD A,($DF3E)
 SUB 180
 LD L,A
 LD H,0
 DUP 4
 ADD HL,HL
 EDUP
 LD DE,$C000
 ADD HL,DE
 LD ($C2F6),HL
 LD A,($DF32)
 AND 1
 LD E,A
 ADD A,A
 ADD A,E
 LD E,A
 LD A,($DF32)
 AND 2
 ADD A,A
 LD D,A
 ADD A,A
 ADD A,D
 OR E
 LD ($C2F5),A
 LD A,16
 LD ($C2F2),A
 LD A,4
 LD ($C2F3),A
 LD A,($DF3C)
 LD ($DE27),A
 LD A,($DF3D)
 LD ($DE28),A
 LD A,$69
 OUT ($F4),A
 LD HL,$20C3
 LD ($5B5B),HL
 LD A,$FD
 LD ($5B5D),A
 LD A,$6F
 OUT ($F4),A
 LD ($5B5B),HL
 LD A,$FD
 LD ($5B5D),A
 LD A,$D8
 LD I,A
 EI
cell:
 CALL $0080
 LD A,0
 JR NC,not_clipped
 INC A
not_clipped:
 LD ($C2F4),A
 LD A,($C2F2)
 NEG
 ADD A,16
 LD E,A
 LD A,($C2F5)
 XOR E
 LD E,A
 LD D,0
 LD HL,($C2F6)
 ADD HL,DE
 LD A,(HL)
 PUSH AF
 LD A,E
 AND 3
 RRCA
 RRCA
 LD L,A
 LD A,E
 AND 12
 ADD A,A
 ADD A,A
 OR L
 LD L,A
 LD A,($DF32)
 AND 2
 JR Z,no_reverse_offset
 LD A,L
 ADD A,14
 LD L,A
no_reverse_offset:
 LD A,($DF37)
 LD H,A
 EX DE,HL
 LD C,$FF
 POP AF
 OR A
 JR NZ,empty
 LD A,($C2F4)
 OR A
 JR NZ,empty
 EX DE,HL
 CALL $A45E
 JR next
empty:
 CALL $A44D
next:
 LD A,$6F
 OUT ($F4),A
 LD HL,$DE27
 INC (HL)
 LD HL,$C2F3
 DEC (HL)
 JR NZ,row_ready
 LD (HL),4
 LD A,($DF3C)
 LD ($DE27),A
 LD HL,$DE28
 INC (HL)
row_ready:
 LD HL,$C2F2
 DEC (HL)
 JR NZ,cell
 DI
 LD A,$84
 LD I,A
 LD A,$ED
 OUT ($F4),A
 POP HL
 POP DE
 RET
 ASSERT $ <= $C2F0

