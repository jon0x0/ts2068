; Independent normal/spread bolt clock. Executes in DOCK2 with a private stack.
; Visible-screen and native-slot accesses cross banks only through DOCK0 shims.
        ORG $5880
        JP erase_all
        JP tick
        JP initialize
        JP fetch_hit
        JP tick_hidden
        JP redraw_all
CACHE EQU $5F80                 ; sixteen [type,x,y] records
HITS EQU $5FB0                  ; pending owner, consumed by main loop
MASKS EQU $5FC0                 ; exact bytes owned by each overlay
SLOT EQU $5FF0
MODE EQU $5FF1
COLOR EQU $5FF2
MCOUNT EQU $5FF3
FIRST EQU $5FF4
BULKMODE EQU $5FF7
HIDDEN EQU $5FF6
LIMIT EQU $5FF5
PEEK EQU $0190
POKE EQU $1E20
READ_SLOT EQU $19E3
WRITE_SLOT EQU $09B6
initialize:
        LD HL,CACHE
        LD DE,CACHE+1
        LD BC,127
        LD (HL),0
        LDIR
        RET
fetch_hit:                      ; B slot, A owner; releases native pool atomically
        LD H,HITS/256
        LD A,B
        ADD A,HITS&255
        LD L,A
        LD A,(HL)
        OR A
        RET Z
        LD (HL),0
        PUSH AF
        CP $FA
        JR NC,.release
        PUSH BC
        CALL signature
        EX DE,HL
        LD A,B
        ADD A,A
        ADD A,MASKS&255
        LD L,A
        LD H,MASKS/256
        LD A,(DE)
        CP (HL)
        JR NZ,.stale
        INC DE
        INC HL
        LD A,(DE)
        CP (HL)
        JR Z,.same
.stale: POP BC
        POP AF
        XOR A
        PUSH AF
        JR .release
.same:  POP BC
.release:
        CALL READ_SLOT
        XOR A
        CALL WRITE_SLOT
        POP AF
        RET
redraw_all:
        LD A,1
        JR service_all
erase_all:
        XOR A
service_all:
        LD (BULKMODE),A
        XOR A
        LD (SLOT),A
.loop: CALL select_cache
        LD A,(BULKMODE)
        OR A
        JR Z,bulk_paint
        ; A copy may finish after a slot was cleared or reused. Never replay
        ; a cached position/type that is no longer the native live shot.
        LD A,(SLOT)
        LD B,A
        CALL READ_SLOT
        CP (IX+0)
        JR NZ,bulk_next
        LD A,D
        CP (IX+1)
        JR NZ,bulk_next
        LD A,E
        CP (IX+2)
        JR NZ,bulk_next
        LD A,1
bulk_paint:
        CALL paint
bulk_next:
        LD HL,SLOT
        INC (HL)
        LD A,(HL)
        CP 16
        JR C,service_all.loop
        RET
tick_hidden:
        LD A,1
        JR tick_mode
tick:
        XOR A
tick_mode:
        LD (HIDDEN),A
        LD HL,FIRST
        LD A,(HL)
        AND 15
        LD (SLOT),A
        INC (HL)
        LD A,8                   ; bounded work even with all sixteen slots full
        LD (LIMIT),A
        LD A,16
        LD (MCOUNT),A
.loop: CALL select_cache
        LD B,(IX+0)
        XOR A
        CALL paint               ; erase only bytes actually published
        LD A,(SLOT)
        LD B,A
        CALL READ_SLOT
        OR A
        JP Z,.empty
        LD C,A
        LD A,(SLOT)
        ADD A,HITS&255
        LD L,A
        LD H,HITS/256
        LD A,(HL)
        OR A
        JP NZ,.empty
        LD A,C
        LD (IX+0),A
        LD B,E                   ; native D=x, E=y
        LD C,D
        LD A,(IX+0)
        CALL $C3D1               ; one 8-pixel native direction step, not 3x travel
        LD A,B
        CP 20
        JP NC,.expire
        LD A,C
        CP 30
        JP NC,.expire
        CALL $C0E4
        CP $80
        JR NC,.hit
        LD A,(IX+0)
        AND $F0
        CP $10
        JR NZ,.vertical
        INC C
        CALL $C0E4
        CP $80
        JR NC,.hit
        DEC C
        JR .checked
.vertical:
        LD A,B
        CP 19
        JP NC,.expire
        INC B
        CALL $C0E4
        CP $80
        JR NC,.hit
        DEC B
.checked: ; Both collision samples have already rejected owners >=80.
        LD (IX+1),C
        LD (IX+2),B
        LD D,C
        LD E,B
        LD A,(SLOT)
        LD B,A
        LD A,(IX+0)
        CALL WRITE_SLOT
.draw: LD A,(HIDDEN)
        OR A
        JR NZ,.count
        INC A                    ; HIDDEN was zero
        CALL paint
.count:LD HL,LIMIT
        DEC (HL)
        JR NZ,.next
        LD A,(SLOT)
        INC A
        LD (FIRST),A
        RET
.next: LD HL,SLOT
        INC (HL)
        LD A,(HL)
        AND 15
        LD (HL),A
        LD HL,MCOUNT
        DEC (HL)
        JP NZ,.loop
        RET
.hit:  PUSH AF
        LD D,C
        LD E,B
        LD A,(SLOT)
        LD B,A
        LD A,(IX+0)
        CALL WRITE_SLOT
        POP DE
        LD A,(SLOT)
        ADD A,HITS&255
        LD L,A
        LD H,HITS/256
        LD (HL),D
        LD A,D
        CP $FA
        JR NC,.empty
        CALL signature
        LD A,(SLOT)
        ADD A,A
        ADD A,MASKS&255
        LD E,A
        LD D,MASKS/256
        LDI
        LDI
        JR .empty
.expire:
        LD A,(SLOT)
        LD B,A
        XOR A
        CALL WRITE_SLOT
.empty:LD (IX+0),0
        JR .next
select_cache:
        LD A,(SLOT)
        LD E,A
        LD D,0
        LD HL,CACHE
        ADD HL,DE
        ADD HL,DE
        ADD HL,DE
        PUSH HL
        POP IX
        RET
signature:
        CP $DC
        JR C,.native
        SUB $DC
.native:
        CALL $8FCB
        LD DE,5
        ADD HL,DE
        RET
paint:                           ; A=0 erase, 1 draw. Two native 8x8 glyph cells.
        LD (MODE),A
        OR A
        JR Z,paint_has_type
        ; Never put bolt pixels inside the independently composited ship patch.
        LD A,($7AA1)
        SUB (IX+1)
        ADD A,4
        CP 9
        JR NC,paint_has_type
        LD A,($7AA2)
        SUB (IX+2)
        ADD A,3
        CP 7
        RET C
paint_has_type:
        LD A,(IX+0)
        OR A
        RET Z
        PUSH AF
        LD A,(SLOT)
        ADD A,A
        ADD A,MASKS&255
        LD L,A
        LD H,MASKS/256
        PUSH HL
        POP IY
        POP AF
        AND $70
        RRCA
        RRCA
        RRCA
        RRCA
        DEC A
        LD HL,$B05B
        LD DE,18
        JR Z,.source
        ADD HL,DE
        DEC A
        JR Z,.source
        ADD HL,DE
.source:
        EX DE,HL
        LD A,(IX+2)
        AND 7
        RRCA
        RRCA
        RRCA
        ADD A,(IX+1)
        LD L,A
        LD A,(IX+2)
        AND $18
        OR $40
        LD H,A
        CALL cell
        LD A,(IX+0)
        AND $70
        CP $10
        JR NZ,.down
        INC L
        JR .second
.down: LD A,L
        ADD A,32
        LD L,A
        JR NC,.second
        LD A,H
        ADD A,8
        LD H,A
.second:
        INC IY
cell:  LD A,(DE)
        AND 7
        LD (COLOR),A
        INC DE
        LD A,8
.row:  PUSH AF
        LD A,(DE)
        INC DE
        PUSH DE
        LD D,A
        CALL PEEK                 ; B visible bits, C visible attr, HL unchanged
        LD A,(MODE)
        OR A
        JR Z,.erase
        SLA (IY+0)
        JR NC,.new_row
        LD A,B
        AND D
        CP D
        JR NZ,.new_row
        LD A,(COLOR)
        CP C
        JR NZ,.new_row
        SET 0,(IY+0)
        JR .done
.new_row:
        LD A,D
        OR A
        JR Z,.done
        LD A,B
        OR A
        JR NZ,.done
        LD A,C
        AND $38
        JR NZ,.done
        SET 0,(IY+0)
        LD B,D
        LD A,(COLOR)
        LD C,A
        CALL POKE
        JR .done
.erase:
        SLA (IY+0)
        JR NC,.done
        ; Preserve any newly written non-bolt bits (stars, for example).
        LD A,D
        CPL
        AND B
        LD B,A
        JR NZ,.keep_attr
        LD C,0                    ; normal black, never bright black paper
.keep_attr:
        CALL POKE
.done: POP DE
        INC H
        POP AF
        DEC A
        JR NZ,.row
        LD A,H
        SUB 8
        LD H,A
        RET
        ASSERT $ <= $5B5B
