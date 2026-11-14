; Packed phase source decoder; one nibble/core and five bits/sphere per ECM row.
        ORG $8C00
select_cache:
        DI
        LD (saved_sp),SP
        LD SP,$5CF0
        LD A,(mode)
        OR A
        LD DE,$F3F1
        JR Z,source_base
        LD DE,$EFA1
source_base:
        OR A
        SBC HL,DE
        LD A,L
        LD C,A
        ADD A,A
        ADD A,A
        ADD A,A
        LD B,A
        ADD A,A
        ADD A,A
        ADD A,A
        SUB B
        ADD A,C
        LD C,A
        LD A,(width)
        LD E,A
        LD A,C
        LD D,0
cell_row:
        CP E
        JR C,cell_column
        SUB E
        INC D
        JR cell_row
cell_column:
        LD C,A
        LD A,(flip)
        AND 1
        LD A,C
        JR Z,column_unflipped
        LD C,A
        LD A,(width)
        DEC A
        SUB C
column_unflipped:
        LD (column),A
        LD A,D
        ADD A,A
        ADD A,A
        ADD A,A
        LD D,A
        LD A,(phase_y)
        LD E,A
        LD A,D
        SUB E
        LD (source_y),A
        LD A,(flip)
        AND 2
        JR Z,row_ready
        LD A,(height)
        DEC A
        LD D,A
        LD A,(source_y)
        LD E,A
        LD A,D
        SUB E
        LD (source_y),A
row_ready:
        LD HL,(cache_base)
        LD A,(height)
        ADD A,A
        LD E,A
        LD D,0
        LD A,(column)
        OR A
        JR Z,column_ready
column_loop:
        ADD HL,DE
        DEC A
        JR NZ,column_loop
column_ready:
        LD (column_base),HL
        ; Private stack in DOCK2, separate from the IRQ player stack in HOME.
        LD A,(mode)
        OR A
        LD A,$5F
        JR Z,source_map
        LD A,$1F
source_map:
        OUT ($F4),A
        EI
        LD A,(flip)
        AND 1
        JP NZ,boundary
        LD A,(source_y)
        LD D,A
        LD A,(flip)
        AND 2
        RRCA
        LD (reverse),A
        JR NZ,reverse_bounds
        LD A,D
        CP $F8
        JP NC,boundary
        LD A,(height)
        CP D
        JP C,empty
        JP Z,empty
        SUB 7
        CP D
        JP C,boundary
        JP Z,boundary
        JR interior
reverse_bounds:
        LD A,D
        CP $F8
        JP NC,empty
        LD A,D
        CP 7
        JP C,boundary
        LD A,(height)
        CP D
        JP C,boundary
        JP Z,boundary
interior:
        LD A,D
        ADD A,A
        LD E,A
        LD D,0
        LD HL,(column_base)
        ADD HL,DE
        LD (result),HL
        LD A,(reverse)
        OR A
        JR NZ,scan_reverse
        XOR A
        DUP 8
        INC HL
        OR (HL)
        INC HL
        EDUP
        LD C,A
        JP cache_done
scan_reverse:
        XOR A
        DUP 8
        INC HL
        OR (HL)
        DEC HL
        DEC HL
        DEC HL
        EDUP
        LD C,A
        JP cache_done
empty:
        LD C,0
        JP cache_done
boundary:
        LD IX,$8BF0
        LD B,8
        LD C,0
boundary_row:
        LD A,(source_y)
        LD E,A
        LD A,(height)
        CP E
        JR C,padding
        JR Z,padding
        LD D,0
        LD HL,(column_base)
        ADD HL,DE
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD A,(HL)
        LD (IX+1),A
        OR C
        LD C,A
        LD A,(flip)
        AND 1
        LD A,E
        JR Z,bits_ready
        DUP 8
        RRCA
        RL D
        EDUP
        LD A,D
bits_ready:
        LD (IX),A
        JR boundary_next
padding:
        XOR A
        LD (IX),A
        LD (IX+1),A
boundary_next:
        INC IX
        INC IX
        LD A,(flip)
        AND 2
        LD A,(source_y)
        JP Z,boundary_forward
        DEC A
        DEC A
boundary_forward:
        INC A
        LD (source_y),A
        DJNZ boundary_row
        LD HL,$8BF0
        LD (result),HL
        XOR A
        LD (reverse),A
cache_done:
        DI
        LD A,$19
        OUT ($F4),A
        LD SP,(saved_sp)
        LD HL,(result)
        LD A,C
        OR A
        SCF
        RET Z
        LD A,(reverse)
        OR A
        RET
saved_sp: DW 0
column_base: DW 0
result: DW 0
reverse: DB 0
source_y: DB 0
column: DB 0
init_cache:
        ; HOME native assets are already installed; borrow their source shadow.
        LD A,$DB
        OUT ($F4),A
        LD HL,$DBD0
        LD DE,$E000
        LD BC,128
        LDIR
        LD HL,$2400
        LD DE,$C000
        LD BC,7136
        LDIR
        LD HL,$E1E0
        LD DE,$DBE0
        LD BC,16
        LDIR
        LD HL,0
        LD IX,$2400
        LD BC,3520
unpack_core:
        PUSH HL
        CALL decode_pair
        LD (IX),E
        LD (IX+1),D
        INC IX
        INC IX
        POP HL
        INC HL
        DEC BC
        LD A,B
        OR C
        JR NZ,unpack_core
        LD IX,$C000
        LD BC,1152
unpack_spheres:
        PUSH HL
        CALL decode_pair
        LD (IX),E
        LD (IX+1),D
        INC IX
        INC IX
        POP HL
        INC HL
        DEC BC
        LD A,B
        OR C
        JR NZ,unpack_spheres
        LD A,1
        LD ($E1F0),A
        LD A,$D9
        OUT ($F4),A
        RET
decode_pair:
        PUSH BC
        PUSH HL
        LD DE,$C000
        ADD HL,DE
        LD A,(HL)
        LD (pixel),A
        POP HL
        LD DE,3520
        OR A
        SBC HL,DE
        JR NC,sphere_attr
        ADD HL,DE
        LD A,L
        AND 1
        LD C,A
        SRL H
        RR L
        LD DE,$D240
        ADD HL,DE
        LD A,(HL)
        LD B,A
        LD A,C
        OR A
        LD A,B
        JR Z,core_nibble
        RRCA
        RRCA
        RRCA
        RRCA
core_nibble:
        AND 15
        LD HL,$E1B0
        JR dictionary
sphere_attr:
        LD D,H
        LD E,L
        ADD HL,HL
        ADD HL,HL
        ADD HL,DE
        LD A,L
        AND 7
        LD C,A
        SRL H
        RR L
        SRL H
        RR L
        SRL H
        RR L
        LD DE,$D920
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD D,(HL)
        LD A,C
        OR A
        JR Z,sphere_nibble
shift_attr:
        SRL D
        RR E
        DEC C
        JR NZ,shift_attr
sphere_nibble:
        LD A,E
        AND 31
        LD HL,$E1C0
dictionary:
        LD E,A
        LD D,0
        ADD HL,DE
        LD D,(HL)
        LD A,(pixel)
        LD E,A
        POP BC
        RET
pixel: DB 0
        ASSERT $ <= $8EE0
        DS $8EE0-$,0
mode: DB 0
cel: DB 0
flip: DB 0
phase_x: DB 0
phase_y: DB 0
        DB 0
cache_base: DW 0
width: DB 0
height: DB 0
        ASSERT $ <= $8F00
