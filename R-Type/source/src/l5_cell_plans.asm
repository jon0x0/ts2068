; Cell plans remove per-cell coordinate division and empty checks from painting.
        ORG $8C00
select_cache:
        DI
        LD (paint_sp),SP
        LD SP,$5CF0
        INC HL
        LD E,(HL)
        INC HL
        LD D,(HL)
        INC HL
        LD C,(HL)
        EX DE,HL
        LD (result),HL
        LD A,(flip)
        AND 2
        RRCA
        LD (reverse),A
        LD A,(mode)
        OR A
        LD A,$5F
        JR Z,paint_map
        LD A,$1F
paint_map:
        OUT ($F4),A
        EI
        LD A,C
        CP $FF
        JR NZ,boundary
        LD A,(flip)
        AND 1
        JR Z,paint_done
boundary:
        LD IX,$8BF0
        LD B,8
paint_row:
        RRC C
        JR NC,padding
        LD E,(HL)
        INC HL
        LD A,(HL)
        DEC HL
        LD (IX+1),A
        LD A,(flip)
        AND 1
        LD A,E
        JR Z,paint_bits
        DUP 8
        RRCA
        RL D
        EDUP
        LD A,D
paint_bits:
        LD (IX),A
        JR paint_next
padding:
        XOR A
        LD (IX),A
        LD (IX+1),A
paint_next:
        INC IX
        INC IX
        LD A,(reverse)
        OR A
        JR NZ,paint_reverse
        INC HL
        INC HL
        JR paint_step_done
paint_reverse:
        DEC HL
        DEC HL
paint_step_done:
        DJNZ paint_row
        LD HL,$8BF0
        LD (result),HL
        XOR A
        LD (reverse),A
paint_done:
        DI
        LD A,$19
        OUT ($F4),A
        LD SP,(paint_sp)
        LD HL,(result)
        LD A,(reverse)
        OR A
        RET
; Called once per actor, with DOCK2 private stack already selected.
; HL=dummy/plan buffer, D=cell rows, E=cell columns. Preserve HL/DE.
prepare_cells:
        PUSH DE
        PUSH HL
        PUSH HL
        POP IX
        LD A,D
        LD (rows_left),A
        LD A,E
        LD (columns),A
        LD A,(phase_y)
        NEG
        LD (row_y),A
        LD A,(main_bc+1)
        LD (screen_y),A
        ; Both low banks need the raw IRQ vector before bank4 is visible.
        LD A,$59
        OUT ($F4),A
        LD HL,$20C3
        LD ($5B5B),HL
        LD A,$FD
        LD ($5B5D),A
        LD A,$5F
        OUT ($F4),A
        LD ($5B5B),HL
        LD A,$FD
        LD ($5B5D),A
        LD A,$5B
        LD ($9000),A
        LD A,$8F
        LD I,A
        EI
        LD HL,(cache_base)
        LD A,(height)
        ADD A,A
        LD E,A
        LD D,0
        LD (stride),DE
        LD A,(flip)
        AND 1
        JR Z,first_column
        LD A,(columns)
        DEC A
first_column_loop:
        ADD HL,DE
        DEC A
        JR NZ,first_column_loop
first_column:
        LD (first_base),HL
plan_row:
        LD A,(main_bc)
        LD (screen_x),A
        LD A,(row_y)
        LD E,A
        LD A,(flip)
        AND 2
        JR Z,source_y_ready
        LD A,(height)
        DEC A
        SUB E
        LD E,A
source_y_ready:
        LD A,E
        LD (source_y),A
        RLA
        SBC A,A
        LD D,A
        SLA E
        RL D
        LD HL,(first_base)
        ADD HL,DE
        LD (cell_ptr),HL
        LD A,(source_y)
        LD E,A
        LD B,8
        LD C,0
        LD D,1
mask_row:
        LD A,(height)
        CP E
        JR C,mask_invalid
        JR Z,mask_invalid
        LD A,C
        OR D
        LD C,A
mask_invalid:
        SLA D
        LD A,(flip)
        AND 2
        JR NZ,mask_reverse
        INC E
        JR mask_next
mask_reverse:
        DEC E
mask_next:
        DJNZ mask_row
        LD A,C
        LD (row_mask),A
        LD A,(columns)
        LD (cols_left),A
plan_cell:
        CALL $0080
        JR C,cell_empty
        LD HL,(cell_ptr)
        LD A,(row_mask)
        OR A
        JR Z,cell_empty
        LD C,A
        LD B,8
scan_row:
        RRC C
        JR NC,scan_next
        INC HL
        LD A,(HL)
        DEC HL
        OR A
        JR NZ,cell_visible
scan_next:
        LD A,(flip)
        AND 2
        JR NZ,scan_reverse
        INC HL
        INC HL
        JR scan_step
scan_reverse:
        DEC HL
        DEC HL
scan_step:
        DJNZ scan_row
cell_empty:
        LD (IX),54
        INC IX
        JR cell_next
cell_visible:
        LD (IX),0
        LD HL,(cell_ptr)
        LD (IX+1),L
        LD (IX+2),H
        LD A,(row_mask)
        LD (IX+3),A
        LD DE,9
        ADD IX,DE
cell_next:
        LD HL,screen_x
        INC (HL)
        LD DE,(stride)
        LD HL,(cell_ptr)
        LD A,(flip)
        AND 1
        JR NZ,column_reverse
        ADD HL,DE
        JR column_advanced
column_reverse:
        OR A
        SBC HL,DE
column_advanced:
        LD (cell_ptr),HL
        LD HL,cols_left
        DEC (HL)
        JR NZ,plan_cell
        LD HL,screen_y
        INC (HL)
        LD A,(row_y)
        ADD A,8
        LD (row_y),A
        LD HL,rows_left
        DEC (HL)
        JP NZ,plan_row
        DI
        LD A,$84
        LD I,A
        XOR A
        LD ($9000),A
        LD A,$DD
        OUT ($F4),A
        POP HL
        POP DE
        RET
paint_sp: DW 0
result: DW 0
reverse: DB 0
screen_x: DB 0
screen_y: DB 0
rows_left: DB 0
columns: DB 0
cols_left: DB 0
row_y: DB 0
source_y: DB 0
row_mask: DB 0
stride: DW 0
first_base: DW 0
cell_ptr: DW 0
init_cache:
        ; HOME native assets are already installed; borrow their source shadow.
        LD A,$DF
        OUT ($F4),A
        LD HL,$DBD0
        LD DE,$DF00
        LD BC,128
        LDIR
        LD HL,$2400
        LD DE,$C000
        LD BC,7136
        LDIR
        LD HL,$DFB0
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
        LD ($E3F0),A
        LD A,$DD
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
        LD HL,$DF80
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
        LD HL,$DF90
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
main_sp: DW 0
main_bc: DW 0
main_id: DB 0
        ASSERT $ <= $8F00
