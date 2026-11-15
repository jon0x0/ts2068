; A is an actual decoded native attribute, never an encoded palette ID.
; Called only by the legacy flat restoration fallback. Preserve BC/DE/HL.
 ORG $0F50
 AND $7F
 BIT 6,A
 RET Z
 PUSH BC
 LD B,A
 AND 7
 JR Z,clear_bright
 LD A,B
 AND $38
 LD A,B
 JR NZ,done
clear_bright:
 LD A,B
 AND $BF
done:
 POP BC
 RET
 ASSERT $ <= $0F80
