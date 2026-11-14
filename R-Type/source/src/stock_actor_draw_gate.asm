; Hold the shared decoded frame through selection AND the native painter.
;9172 has the native orientation AF immediately below its return address.
draw_actor:
 LD E,A
 LD A,(PLAYER_FLAGS+13)
 PUSH AF
 LD A,2
 LD (PLAYER_FLAGS+13),A
 LD HL,4
 ADD HL,SP
 LD A,(HL)
 INC HL
 LD H,(HL)
 LD L,A
 PUSH HL
 LD A,E
 CALL stock_select
 POP AF
 AND 3
 JR Z,draw_normal
 DEC A
 JR Z,draw_mirror
 DEC A
 JR Z,draw_invert
 CALL $8E29
 JR actor_drawn
draw_invert:
 CALL $8DD3
 JR actor_drawn
draw_mirror:
 CALL $8D65
 JR actor_drawn
draw_normal:
 CALL $8CFD
actor_drawn:
 POP AF
 LD (PLAYER_FLAGS+13),A
 ; The normal native tail may safely draw this one transparent cell.
return_blank:
 LD HL,draw_blank
 LD DE,$0101
 RET
draw_blank: DB 54
