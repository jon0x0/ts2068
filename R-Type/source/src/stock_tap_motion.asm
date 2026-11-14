; Native-script targets retained; presentation approaches by two pixels per draw.
; The selector runs under DI and IX points to its saved BC/caller frame.
 ORG MOTION_CODE
 JP motion_select
 JP motion_reset
motion_reset:
 LD HL,MOTION_STATE
 LD DE,MOTION_STATE+1
 LD BC,STATE_BYTES-1
 LD (HL),$FF
 LDIR
 RET
motion_select:
 LD A,(CTX+25)
 OR A
 JP NZ,unhandled
 LD A,(CTX+24)
 CP MOTION_MAP_SIZE
 JP NC,unhandled
 LD L,A
 LD H,0
 LD DE,MOTION_TABLE
 ADD HL,DE
 LD A,MOTION_MASK
 CALL READ_BYTE
 CP $FF
 JP Z,unhandled
 LD (CTX+30),A
 IF MULTIPART_KEYS
 LD HL,MOTION_STATE
 LD B,32
find_motion_state:
 LD A,(HL)
 CP $FF
 JR Z,new_motion_state
 LD A,IYL
 CP (HL)
 JR NZ,next_motion_state
 INC HL
 LD A,(CTX+24)
 CP (HL)
 DEC HL
 JR Z,motion_state_found
next_motion_state:
 LD DE,4
 ADD HL,DE
 DJNZ find_motion_state
 LD HL,MOTION_STATE
new_motion_state:
 LD A,IYL
 LD (HL),A
 INC HL
 LD A,(CTX+24)
 LD (HL),A
 INC HL
 LD (HL),$FF
 INC HL
 LD (HL),$FF
 DEC HL
 JR motion_xy_ready
motion_state_found:
 INC HL
 INC HL
motion_xy_ready:
 ELSE
 LD A,IYL
 AND 31
 ADD A,A
 LD L,A
 LD H,0
 LD DE,MOTION_STATE
 ADD HL,DE
 ENDIF
 LD (CTX+32),HL
 LD A,(IX+2)
 ADD A,A
 ADD A,A
 ADD A,A
 LD D,A
 IF LOCK_X
 LD A,D
 ELSE
 IF MIXED_LOCK_X
 LD A,(CTX+24)
 CP 51
 LD A,D
 JR Z,mixed_x_ready
 ENDIF
 LD A,(HL)
 CALL approach
 IF MIXED_LOCK_X
mixed_x_ready:
 ENDIF
 ENDIF
 LD (HL),A
 LD E,A
 AND 6
 RRCA
 LD (CTX+34),A
 LD A,E
 RRCA
 RRCA
 RRCA
 AND 31
 BIT 7,(IX+2)
 JR Z,x_positive
 OR $E0
x_positive:
 LD (IX+2),A
 INC HL
 LD A,(IX+3)
 ADD A,A
 ADD A,A
 ADD A,A
 LD D,A
 LD A,(HL)
 CALL approach
 LD (HL),A
 LD E,A
 AND 6
 RLCA
 RLCA
 RLCA
 LD (CTX+35),A
 LD A,E
 RRCA
 RRCA
 RRCA
 AND 31
 BIT 7,(IX+3)
 JR Z,y_positive
 OR $E0
y_positive:
 LD (IX+3),A
 LD A,IYL
 AND PHASE_MASK
 LD L,A
 LD H,0
 LD DE,PHASES
 ADD HL,DE
 LD A,(HL)
 INC (HL)
 AND 3
 RRCA
 RRCA
 LD C,A
 LD A,(CTX+35)
 OR C
 LD C,A
 LD A,(CTX+34)
 ADD A,A
 ADD A,A
 OR C
 LD C,A
 LD A,(IX+9)
 AND 3
 OR C
 LD E,A
 LD D,0
 LD A,(CTX+30)
 LD L,A
 LD H,0
 ADD HL,HL
 LD BC,MOTION_TABLE+MOTION_MAP_SIZE
 ADD HL,BC
 LD A,MOTION_MASK
 CALL READ_BYTE
 LD C,A
 INC HL
 LD A,MOTION_MASK
 CALL READ_BYTE
 LD H,A
 LD L,C
 LD BC,MOTION_TABLE
 ADD HL,BC
 LD A,MOTION_MASK
 CALL READ_BYTE
 AND E
 LD E,A
 INC HL
 ADD HL,DE
 LD A,MOTION_MASK
 CALL READ_BYTE
 SCF
 RET
unhandled:
 LD A,(CTX+24)
 OR A
 RET
approach:
 CP $FF
 JR NZ,valid
 LD A,D
 RET
valid:
 LD E,A
 LD A,D
 SUB E
 JR NZ,have_distance
 LD A,D
 RET
have_distance:
 CP 9
 JR C,positive
 CP $F8
 JR NC,negative
 LD A,D
 RET
positive:
 CP 2
 LD A,D
 RET C
 LD A,E
 ADD A,2
 RET
negative:
 LD A,E
 SUB 2
 RET
