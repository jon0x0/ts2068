; Experimental L5 actor-local 2px presentation. Code in DOCK6:$DC50 tail.
; HOME assets are installed before caches borrow the DOCK6 source shadow.
        ORG $DC50
entry:
        LD (MAIN_SP),SP
        LD A,($5BE4)
        LD (MAIN_ID),A
        LD (MAIN_BC),BC
        LD A,$DD
        OUT ($F4),A
        LD SP,$5CF0
        PUSH IX
        PUSH IY
        LD A,(MAIN_ID)
        CP 8
        JR Z,is_core
        CP 30
        JP C,native
        CP 34
        JP NC,native
        SUB 30
        CP 3
        JR NZ,cel_ready
        LD A,1
cel_ready:
        LD (cel),A
        XOR A
        LD (mode),A
        JR selected
is_core:
        LD A,1
        LD (mode),A
        XOR A
        LD (cel),A
selected:
        ; Read and clear only orientation bits in caller's saved animation A.
        LD A,$5D
        OUT ($F4),A
        LD HL,(MAIN_SP)
        INC HL
        INC HL
        INC HL
        LD A,(HL)
        LD D,A
        AND $FC
        LD (HL),A
        LD A,$DD
        OUT ($F4),A
        LD A,D
        AND 3
        LD (flip),A
        LD A,($E3F0)
        OR A
        CALL Z,INIT_CACHE
        LD A,IYL
        DEC A
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
        LD L,A
        LD H,0
        ADD HL,HL
        LD DE,$E300
        ADD HL,DE
        PUSH HL
        POP IX
        LD BC,(MAIN_BC)
        LD A,C
        ADD A,A
        ADD A,A
        ADD A,A
        LD D,A
        LD A,(IX)
        CALL approach
        LD (IX),A
        LD E,A
        AND 6
        RRCA
        LD (phase_x),A
        LD A,E
        RRCA
        RRCA
        RRCA
        AND 31
        LD C,A
        LD A,B
        ADD A,A
        ADD A,A
        ADD A,A
        LD D,A
        LD A,(IX+1)
        CALL approach
        LD (IX+1),A
        LD E,A
        AND 6
        LD (phase_y),A
        LD A,E
        RRCA
        RRCA
        RRCA
        AND 31
        LD B,A
        LD (MAIN_BC),BC
        LD A,(mode)
        OR A
        JR NZ,core_base
        LD HL,$C000
no_flip_x:
        LD A,(cel)
        LD DE,768
        CALL add_a_de
        CALL orient_phase
        LD DE,192
        CALL add_a_de
        LD (cache_base),HL
        LD A,4
        LD (width),A
        LD A,24
        LD (height),A
        LD HL,$F3F1
        LD DE,$0404
        JR dimensions_ready
core_base:
        LD HL,$2400
        CALL orient_phase
        LD DE,1760
        CALL add_a_de
        LD (cache_base),HL
        LD A,11
        LD (width),A
        LD A,80
        LD (height),A
        LD HL,$EFA1
        LD DE,$0B0B
dimensions_ready:
        LD A,(phase_x)
        OR A
        JR NZ,width_ready
        DEC E
width_ready:
        LD A,E
        LD (width),A
        LD A,(phase_y)
        OR A
        JR NZ,finished
        DEC D
finished:
        CALL PREPARE_CELLS
        LD BC,(MAIN_BC)
        POP IY
        POP IX
        LD A,$5D
        OUT ($F4),A
        LD SP,(MAIN_SP)
        PUSH AF
        LD A,9
        JP $0E10
native:
        LD BC,(MAIN_BC)
        POP IY
        POP IX
        LD A,$5D
        OUT ($F4),A
        LD SP,(MAIN_SP)
        LD HL,$8E85
        PUSH HL
        LD A,(MAIN_ID)
        PUSH AF
        LD A,9
        JP $0E10
; Snap discontinuities; follow native one-cell travel at 2px per actor draw.
approach:
        CP $FF
        JR NZ,approach_valid
        LD A,D
        RET
approach_valid:
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
add_a_de:
        OR A
        RET Z
add_loop:
        ADD HL,DE
        DEC A
        JR NZ,add_loop
        RET
orient_phase:
        LD A,(flip)
        AND 1
        LD A,(phase_x)
        RET Z
        OR A
        RET Z
mirror_phase:
        NEG
        AND 3
        RET

warmup:
        LD (MAIN_SP),SP
        LD A,$DD
        OUT ($F4),A
        LD SP,$5CF0
        PUSH IX
        PUSH IY
        LD A,($E3F0)
        OR A
        CALL Z,INIT_CACHE
        POP IY
        POP IX
        LD A,$5D
        OUT ($F4),A
        LD SP,(MAIN_SP)
        PUSH AF
        LD A,9
        JP $0E11
restore_sources:
        LD (MAIN_SP),SP
        LD A,$DF
        OUT ($F4),A
        LD SP,$5CF0
        PUSH IX
        PUSH IY
        LD A,($E3F0)
        OR A
        JR Z,restore_done
        ; Only the first2304 packed bytes were replaced by raw sphere pairs.
        ; Recover those bitmap bytes from the raw core, retaining all other packed data.
        LD HL,$2400
        LD DE,$C000
        LD BC,2304
recover_prefix:
        LD A,(HL)
        LD (DE),A
        INC HL
        INC HL
        INC DE
        DEC BC
        LD A,B
        OR C
        JR NZ,recover_prefix
        LD HL,$C000
        LD DE,$2400
        LD BC,7136
        LDIR
        LD HL,$DBE0
        LD DE,$DFB0
        LD BC,16
        LDIR
        LD HL,$DF00
        LD DE,$DBD0
        LD BC,128
        LDIR
        XOR A
        LD ($E3F0),A
        LD A,$5D
        OUT ($F4),A
        LD HL,$E000
        LD DE,$C000
        LD BC,$187C
        LDIR
        ; Cell plans are scratch, not immutable native asset payload.
        LD HL,$CFA1
        LD DE,$CFA2
        LD BC,$04DF
        LD (HL),0
        LDIR
restore_done:
        POP IY
        POP IX
        LD A,$5D
        OUT ($F4),A
        LD SP,(MAIN_SP)
        LD HL,$A000
        PUSH AF
        LD A,9
        JP $0E11
        ASSERT $ <= $DF00
; One coordinate slot per actor IYL; native actor records have stride9.
mode EQU $8EE0
cel EQU $8EE1
flip EQU $8EE2
phase_x EQU $8EE3
phase_y EQU $8EE4
cache_base EQU $8EE6
width EQU $8EE8
height EQU $8EE9

MAIN_SP EQU $8EEA
MAIN_BC EQU $8EEC
MAIN_ID EQU $8EEE
