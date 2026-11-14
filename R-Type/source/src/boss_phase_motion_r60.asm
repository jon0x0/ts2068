; Actor-local two-pixel phased presentation, original target scripts retained.
        ORG $A000
entry:
        LD (MAIN_SP),SP
        LD A,($5BE4)
        LD (MAIN_ID),A
        LD (MAIN_BC),BC
        LD A,$ED
        OUT ($F4),A
        LD SP,$5CF0
        PUSH IX
        PUSH IY
 IF NO_SMOOTH
        LD A,(MAIN_ID)
        CP 43
        JR Z,walker
        CP 44
        JR NZ,walker_done
walker:
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
        AND 31
        LD E,A
        LD D,0
        LD HL,$E3D0
        ADD HL,DE
        LD A,(HL)
        INC A
        AND 3
        LD (HL),A
        ADD A,201
        LD (MAIN_ID),A
walker_done:
 ENDIF
        LD HL,$E350
find_entry:
        LD A,(HL)
        OR A
        JP Z,native
        LD A,(MAIN_ID)
        CP (HL)
        JR Z,selected
        LD DE,11
        ADD HL,DE
        JR find_entry
selected:
        INC HL
        LD A,(HL)
        LD B,A
        AND $80
        LD (lock_x),A
        LD A,B
        AND $6F
        LD (width),A
        INC HL
        LD A,(HL)
        ADD A,A
        ADD A,A
        ADD A,A
        LD (height),A
        INC HL
        LD (entry_ptr),HL
        LD A,$6D
        OUT ($F4),A
        LD HL,(MAIN_SP)
        INC HL
        INC HL
        INC HL
        LD A,(HL)
        LD D,A
        AND $FC
        LD (HL),A
        LD A,$ED
        OUT ($F4),A
        LD A,D
        AND 3
        LD (flip),A
 IF NO_SMOOTH
        XOR A
        LD (phase_x),A
        LD (phase_y),A
        JP coordinates_ready
 ENDIF
        LD IX,$E2D0
        LD B,32
find_state:
        LD A,(IX)
        CP $FF
        JR Z,new_state
        LD A,IYL
        CP (IX)
        JR NZ,next_state
 IF MULTIPART_KEYS
        LD A,(MAIN_ID)
 ELSE
        XOR A
 ENDIF
        CP (IX+1)
        JR Z,state_ready
next_state:
        LD DE,4
        ADD IX,DE
        DJNZ find_state
        LD IX,$E2D0
new_state:
        LD A,IYL
        LD (IX),A
 IF MULTIPART_KEYS
        LD A,(MAIN_ID)
 ELSE
        XOR A
 ENDIF
        LD (IX+1),A
        LD (IX+2),$FF
        LD (IX+3),$FF
state_ready:
        LD BC,(MAIN_BC)
        LD A,C
        ADD A,A
        ADD A,A
        ADD A,A
        LD D,A
        LD A,(lock_x)
        OR A
        LD A,D
        JR NZ,x_ready
        LD A,(IX+2)
        CALL approach
x_ready:
        LD (IX+2),A
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
        LD A,(IX+3)
        CALL approach
        LD (IX+3),A
        LD E,A
        AND 6
        LD (phase_y),A
        LD A,E
        RRCA
        RRCA
        RRCA
        AND 31
        LD B,A
        LD A,(MAIN_BC)
        BIT 7,A
        JR Z,x_unsigned
        LD A,C
        OR $E0
        LD C,A
x_unsigned:
        LD A,(MAIN_BC+1)
        BIT 7,A
        JR Z,y_unsigned
        LD A,B
        OR $E0
        LD B,A
y_unsigned:
        LD (MAIN_BC),BC
coordinates_ready:
        LD BC,(MAIN_BC)
        LD A,(phase_x)
        LD E,A
        LD A,(flip)
        AND 1
        LD A,E
        JR Z,phase_ready
        NEG
        AND 3
phase_ready:
        ADD A,A
        LD E,A
        LD D,0
        LD HL,(entry_ptr)
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD D,(HL)
 IF PRELOADED
        LD (cache_base),DE
 ELSE
        LD HL,(last_cache)
        OR A
        SBC HL,DE
        JR Z,cache_ready
        LD (last_cache),DE
        EX DE,HL
        LD DE,$C000
        LD A,$6F
        OUT ($F4),A
        CALL DECOMPRESS
 ENDIF
cache_ready:
        LD A,$ED
        OUT ($F4),A
        LD A,SYNTH_MODE
        LD (mode),A
 IF NOT PRELOADED
        LD HL,$C000
        LD (cache_base),HL
 ENDIF
        LD A,(width)
        LD E,A
        INC A
        LD (width),A
        LD A,(phase_x)
        OR A
        JR Z,width_ready
        INC E
width_ready:
        LD A,(height)
        RRCA
        RRCA
        RRCA
        AND 31
        LD D,A
        LD A,(phase_y)
        OR A
        JR Z,height_ready
        INC D
height_ready:
        LD HL,PLAN_START
        CALL PREPARE_CELLS
        LD BC,(MAIN_BC)
        POP IY
        POP IX
        LD A,$6D
        OUT ($F4),A
        LD SP,(MAIN_SP)
        PUSH AF
        LD A,9
        JP $0E10
native:
        LD BC,(MAIN_BC)
        POP IY
        POP IX
        LD A,$6D
        OUT ($F4),A
        LD SP,(MAIN_SP)
        LD HL,$8E85
        PUSH HL
        LD A,(MAIN_ID)
        PUSH AF
        LD A,9
        JP $0E10
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

warmup:
        LD (MAIN_SP),SP
        LD A,$ED
        OUT ($F4),A
        LD SP,$5CF0
        PUSH IX
        PUSH IY
 IF PRELOADED
        LD A,($E3F0)
        OR A
        CALL Z,PRELOAD_ENTRY
 ENDIF
        LD HL,$D800
        LD DE,$D801
        LD BC,256
        LD (HL),$5B
        LDIR
        LD HL,0
        LD (last_cache),HL
        LD HL,$E2D0
        LD DE,$E2D1
        LD BC,127
        LD (HL),$FF
        LDIR
        LD A,1
        LD ($E3F0),A
        JR restore_exit
restore_sources:
        LD (MAIN_SP),SP
        LD A,$EF
        OUT ($F4),A
        LD SP,$5CF0
        PUSH IX
        PUSH IY
        LD A,($E3F0)
        OR A
        JR Z,restore_exit
 IF BACKUP_PTR
        LD HL,BACKUP_PTR
        LD DE,PLAN_START
        CALL RESTORE_PACKED
 ELSE
        LD HL,PLAN_START-$2000
        LD DE,PLAN_START
        LD BC,PLAN_BYTES
        LD A,$2F
        OUT ($F4),A
        LDIR
        LD A,$6F
        OUT ($F4),A
 ENDIF
        LD A,$6D
        OUT ($F4),A
        LD HL,$E000
        LD DE,$C000
        LD BC,$187C
        LDIR
        LD A,$ED
        OUT ($F4),A
        XOR A
        LD ($E3F0),A
restore_exit:
        POP IY
        POP IX
        LD A,$6D
        OUT ($F4),A
        LD SP,(MAIN_SP)
        LD HL,$A000
        PUSH AF
        LD A,9
        JP $0E11
        ASSERT $ <= $A500
mode EQU $DF30
flip EQU $DF32
phase_x EQU $DF33
phase_y EQU $DF34
cache_base EQU $DF36
width EQU $DF38
height EQU $DF39
MAIN_SP EQU $DF3A
MAIN_BC EQU $DF3C
MAIN_ID EQU $DF3E
entry_ptr EQU $DF40
last_cache EQU $DF42

lock_x EQU $DF44
