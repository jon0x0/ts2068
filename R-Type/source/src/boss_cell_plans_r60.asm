; Cell plans remove per-cell coordinate division and empty checks from painting.
        ORG $DC50
select_cache:
        DI
        LD (paint_sp),SP
        LD SP,$5CF0
        CALL PLAN_READ
        LD (result),HL
        LD A,(flip)
        AND 2
        RRCA
        LD (reverse),A
        LD A,$6F
        JR paint_map
paint_map:
        OUT ($F4),A
        LD A,$D8
        LD I,A
        EI
        LD A,(mode)
        CP 2
        JR Z,boundary
        LD A,C
        CP $FF
        JR NZ,boundary
        LD A,(flip)
        AND 1
        JR Z,paint_done
boundary:
        LD IX,$D910
        LD B,8
paint_row:
        RRC C
        JR NC,padding
        LD E,(HL)
        INC HL
        LD A,(HL)
        DEC HL
        CALL maybe_synth
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
        LD HL,$D910
        LD (result),HL
        XOR A
        LD (reverse),A
paint_done:
        DI
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
        LD A,$69
        OUT ($F4),A
        LD HL,$20C3
        LD ($5B5B),HL
        LD A,$FD
        LD ($5B5D),A
        LD A,$6F
        OUT ($F4),A
        LD ($5B5B),HL
        LD A,$FD
        LD ($5B5D),A
        LD A,$D8
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
        LD E,(HL)
        INC HL
        LD A,(HL)
        DEC HL
        CALL maybe_synth
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
        CALL PLAN_EMPTY
        JR cell_next
cell_visible:
        LD HL,(cell_ptr)
        LD A,(row_mask)
        LD C,A
        CALL PLAN_VISIBLE
cell_next:
        LD A,$6F
        OUT ($F4),A
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
        LD A,$ED
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
maybe_synth:
        PUSH AF
        LD A,(mode)
        CP 2
        JR Z,do_synth
        POP AF
        RET
do_synth:
        POP AF
        JP SYNTH_ENTRY
restore_packed:
        LD A,$6F
        OUT ($F4),A
        CALL decompress
        LD A,$6F
        OUT ($F4),A
        RET
decompress:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        JP M,backreference
        LD C,A
        LD B,0
        LDIR
        JR decompress
backreference:
        AND $7F
        ADD A,3
        LD C,(HL)
        INC HL
        LD B,(HL)
        INC HL
        PUSH HL
        LD H,D
        LD L,E
        OR A
        SBC HL,BC
        LD C,A
        LD B,0
        LDIR
        POP HL
        JR decompress
mapped:
        LD B,E
        LD C,A
        AND $3F
        SRL A
        SRL A
        LD E,A
        LD D,0
        LD A,(target_attr)
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,DE
        LD DE,$2400
        ADD HL,DE
        LD A,C
        AND 3
        LD C,A
        LD A,(HL)
        JR Z,mapping_ready
mapping_rotate:
        RRCA
        RRCA
        DEC C
        JR NZ,mapping_rotate
mapping_ready:
        AND 3
        LD E,B
        CP 1
        RET Z
        CP 2
        JR Z,invert_bits
        CP 3
        LD E,0
        RET NZ
        DEC E
        RET
invert_bits:
        LD A,E
        CPL
        LD E,A
        RET
preload:
        LD A,$6F
        OUT ($F4),A
        LD IX,PRELOAD_TABLE
        LD B,(IX)
        INC IX
preload_loop:
        LD L,(IX)
        LD H,(IX+1)
        LD E,(IX+2)
        LD D,(IX+3)
        PUSH BC
        CALL decompress
        POP BC
        INC IX
        INC IX
        INC IX
        INC IX
        DJNZ preload_loop
        LD A,$ED
        OUT ($F4),A
        RET
install_motion:
        DI
        LD A,$63
        OUT ($F4),A
        LD HL,MOTION_PTR
        LD DE,$A000
        LD BC,MOTION_BYTES
        LDIR
        LD A,$69
        OUT ($F4),A
        JP WARMUP_ENTRY
        ASSERT $ <= $DF30
        DS $DF30-$,0
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
        DS $DF50-$,0
target_attr EQU $DF49
