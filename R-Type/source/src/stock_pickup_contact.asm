; Native pickup fallback for a fine player between main-loop IRQ publications.
; DE is the native pickup record; do not publish player owners into enemy physics.
 ORG PICKUP_CODE
 JP pickup
 JP force
pickup:
 LD A,($7A95)
 OR A
 RET NZ
 LD A,(PLAYER_FLAGS+2)
 OR A
 RET Z
 PUSH BC
 PUSH DE
 PUSH HL
 LD H,D
 LD L,E
 INC HL
 INC HL
 LD E,0
 JR contact_core
force:
 LD A,($7A95)
 OR A
 RET NZ
 LD A,($7AA3)
 OR A
 JR Z,force_active
 XOR A
 RET
force_active:
 LD A,(PLAYER_FLAGS+2)
 OR A
 RET Z
 PUSH BC
 PUSH DE
 PUSH HL
 LD HL,$7AA9
 LD A,($7AA8)
 OR A
 JR NZ,force_pointer
 LD HL,$7AAC
 LD A,($7AAB)
 OR A
 JR NZ,force_pointer
 LD HL,$7AAF
force_pointer:
 LD E,2
contact_core:
 LD B,(HL)
 INC HL
 LD C,(HL)
 LD A,(PLAYER_STATE)
 RRCA
 RRCA
 RRCA
 AND 31
 LD H,A
 LD A,B
 SUB H
 ADD A,2
 CP 6
 JR NC,miss
 LD A,(PLAYER_STATE+1)
 LD H,A
 AND 7
 LD L,A
 LD A,H
 RRCA
 RRCA
 RRCA
 AND 31
 LD H,A
 LD A,L
 OR A
 LD D,1
 JR Z,y_limit
 INC D
y_limit:
 LD A,E
 ADD A,D
 LD D,A
 LD A,C
 SUB H
 ADD A,E
 CP D
 JR NC,miss
contact:
 LD A,3
 LD ($7AD8),A
 LD A,1
 LD ($7A95),A
 JR finish
miss:
 XOR A
finish:
 POP HL
 POP DE
 POP BC
 RET
