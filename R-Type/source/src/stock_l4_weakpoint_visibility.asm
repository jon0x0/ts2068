; The three native weakpoint children may overwrite their own parent hull only.
 ORG $0C12
 LD A,(DE)
 OR A
 JP Z,$8F0B
 PUSH BC
 LD B,A
 LD A,(IY+5)
 CP $3B
 JR Z,child
 CP $4B
 JR Z,child
 CP $5B
 JR NZ,reject
child:
 RRCA
 RRCA
 RRCA
 RRCA
 AND $0F
 NEG
 ADD A,$86
 CP B
 JR NZ,reject
 POP BC
 SCF
 RET
reject:
 POP BC
 OR A
 RET
 ASSERT $ <= $0C45
