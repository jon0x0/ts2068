; A one-level ROM cannot insert the next cartridge. Present an honest endpoint.
 ORG COMPLETE_CODE
 DI
 XOR A
 LD ($7AA4),A
 LD (FLAGS+2),A
 LD ($FBC0),A
 LD ($FBC1),A
 LD BC,$FFF5
 LD A,8
 OUT (C),A
 INC C
 XOR A
 OUT (C),A
 DEC C
 LD A,9
 OUT (C),A
 INC C
 XOR A
 OUT (C),A
 DEC C
 LD A,10
 OUT (C),A
 INC C
 XOR A
 OUT (C),A
 LD HL,$6000
 LD BC,$1800
 CALL $FDF0
 LD A,COMPLETE_MASK
 LD HL,COMPLETE_SOURCE
 LD DE,$4000
 CALL $000A
 LD HL,$4000
 LD DE,$6000
 LD BC,$1800
colour:
 LD A,(HL)
 OR A
 JR Z,next
 LD A,7
 LD (DE),A
next:
 INC HL
 INC DE
 DEC BC
 LD A,B
 OR C
 JR NZ,colour
 LD A,2
 LD ($BE00),A
 OUT ($FF),A
release:
 CALL $1A00
 AND 16
 JR NZ,release
press:
 CALL $1A00
 AND 16
 JR Z,press
 LD A,$13
 OUT ($F4),A
 JP $8008
 ASSERT $ <= COMPLETE_CODE+160
