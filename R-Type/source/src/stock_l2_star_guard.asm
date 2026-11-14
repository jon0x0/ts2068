draw_guard:
 CALL protected
 JP Z,$16F7
 POP AF
 RET
cleanup_guard:
 CALL protected
 JP Z,$16FE
 DEC C
 LD A,1
 OR A
 RET
protected:
 LD A,($7A8E)
 OR A
 RET Z
 LD A,C
 AND $1F
 CP 8
 SBC A,A
 INC A
 RET
