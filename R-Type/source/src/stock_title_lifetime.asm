; Permanent code. Rebuild suffix phases from the final logo already in ROM4.
 ORG TITLE_CODE
 JP prepare_title
 JP restore_level
prepare_title:
 CALL $0F20
 DI
 LD A,$13
 OUT ($F4),A
 XOR A
 LD ($FC64),A
 LD DE,$C700
suffix:
 LD ($FC68),DE
 LD IX,$9000
 LD A,48
 LD ($FC67),A
row:
 PUSH DE
 PUSH DE
 POP HL
 LD B,7
 XOR A
clear_row:
 LD (HL),A
 INC HL
 DJNZ clear_row
 LD A,($FC64)
 LD L,A
 LD H,0
 ADD HL,HL
 LD BC,glyphs
 ADD HL,BC
 LD ($FC6A),HL
 LD A,($FC64)
 LD C,A
 LD A,6
 SUB C
 LD ($FC6C),A
 OR A
 JR Z,glyphs_done
glyph:
 LD HL,($FC6A)
 LD C,(HL)
 INC HL
 LD B,(HL)
 INC HL
 LD ($FC6A),HL
 PUSH IX
 POP HL
 LD A,L
 ADD A,C
 LD L,A
 JR NC,source_ready
 INC H
source_ready:
 POP DE
 PUSH DE
combine:
 LD A,(DE)
 OR (HL)
 LD (DE),A
 INC DE
 INC HL
 DJNZ combine
 LD A,($FC6C)
 DEC A
 LD ($FC6C),A
 JR NZ,glyph
glyphs_done:
 POP DE
 LD HL,7
 ADD HL,DE
 EX DE,HL
 LD BC,32
 ADD IX,BC
 LD A,($FC67)
 DEC A
 LD ($FC67),A
 JR NZ,row
 ; Generate shifted rows from the suffix's unshifted phase.
 LD A,($FC64)
 OR A
 LD A,4
 JR NZ,phase_first
 LD A,2
phase_first:
 LD ($FC65),A
phase:
 LD HL,($FC68)
 LD BC,336
 PUSH DE
 LDIR
 POP HL
 ; HL first copied row, DE next free destination.
 PUSH DE
 LD A,48
 LD ($FC67),A
shift_row:
 LD A,($FC65)
 LD C,A
shift_once:
 PUSH HL
 LD B,7
 OR A
shift_byte:
 RR (HL)
 INC HL
 DJNZ shift_byte
 POP HL
 DEC C
 JR NZ,shift_once
 LD BC,7
 ADD HL,BC
 LD A,($FC67)
 DEC A
 LD ($FC67),A
 JR NZ,shift_row
 POP DE
 LD A,($FC64)
 OR A
 JR NZ,next_suffix
 LD A,($FC65)
 ADD A,2
 LD ($FC65),A
 CP 8
 JR C,phase
next_suffix:
 LD A,($FC64)
 INC A
 LD ($FC64),A
 CP 7
 JP C,suffix
 LD A,1
 LD ($FC63),A
 LD A,3
 OUT ($F4),A
 RET
restore_level:
 LD A,($FC63)
 CP 1
 JP NZ,$86C3
 DI
 ; Native8696 has already selected the starting checkpoint/event pointer.
 ; Restoring borrowed title RAM must not reset that live four-byte header.
 LD HL,($C4AE)
 PUSH HL
 LD HL,($C4B0)
 PUSH HL
 LD HL,$A000
 LD DE,$C000
 LD A,$23
 CALL $000A
 POP HL
 LD ($C4B0),HL
 POP HL
 LD ($C4AE),HL
 CALL $100F
 XOR A
 LD ($FC63),A
 EI
 JP $86C3
glyphs: DB 0,6,6,3,9,6,15,6,21,5,26,6
 ASSERT $ <= TITLE_CODE+512
