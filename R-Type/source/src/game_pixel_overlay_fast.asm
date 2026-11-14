; Expanded-RAM gameplay player overlay. Bank7:E400, private data F680.
; IRQ uses selected native game keys; no fixed gameplay key assignment.
        ORG $E400
        JP tick
        JP prepare_copy
        JP restore_copy
        JP sync_player
X EQU $F680
Y EQU $F681
OX EQU $F682
OY EQU $F683
HAS EQU $F684
CX EQU $F685
CY EQU $F686
LEFT EQU $F687
TOP EQU $F688
ROW EQU $F689
COL EQU $F68A
BITS EQU $F68B
ATTR EQU $F68C
VB EQU $F68D
VA EQU $F68E
INDEX EQU $F68F
MASK EQU $F690
NEWBITS EQU $F691
PHASE EQU $F692
OLDPHASE EQU $F694
META EQU $F696
CELLID EQU $F69A
WASCOPY EQU $F69B
OLD EQU $F6C0
NEXT EQU $F700
WORLD EQU $F740
OWNERS EQU $F780
MAP EQU $F880
sync_player:
        LD A,($5BC2)
        OR A
        JR Z,initialize_player
        CALL capture_fire
        JP serve_fire
initialize_player:
        LD HL,$F6A0
        LD DE,$F6A1
        LD BC,19
        LD (HL),0
        LDIR
        XOR A
        LD ($F6B6),A
        LD ($F6B7),A
        LD A,($7AA1)
        CP 29
        RET NC
        OR A
        RET Z
        ADD A,A
        ADD A,A
        ADD A,A
        LD (X),A
        LD (OX),A
        LD A,($7AA2)
        CP 20
        RET NC
        ADD A,A
        ADD A,A
        ADD A,A
        LD (Y),A
        LD (OY),A
        XOR A
        LD (HAS),A
        LD ($5BC4),A
        INC A
        LD ($5BC2),A
        RET
tick:
        LD A,($7AA4)
        CP 2
        JP C,inactive
        CP 5
        JP NC,inactive
        LD A,($5BC2)
        OR A
        RET Z
        CALL capture_fire
        LD A,($F6A0)
        OR A
        JR Z,not_charging
        LD HL,$F6A1
        LD A,(HL)
        CP 64
        JR NC,not_charging
        INC (HL)
not_charging:
        LD A,($5BC4)
        OR A
        RET NZ
        CALL dispatch_normal_fire
        LD A,($5BC3)
        LD (WASCOPY),A
        OR A
        ; Input scan must execute with HOME common code visible (bank7 is safe).
        ; Gateway polls selected native controls before mapping bank7.
        LD A,($74FA)
        AND 15
        LD B,A
        ; Fine taps retain one-pixel positioning. Sustained input advances
        ; three pixels per publication, avoiding triple compositor cost.
        LD C,1
        LD A,($F6B6)
        CP B
        JR Z,same_direction
        LD A,B
        LD ($F6B6),A
        XOR A
        LD ($F6B7),A
same_direction:
        LD A,B
        OR A
        JR Z,movement_pixels
        LD A,($F6B7)
        CP 3
        JR NC,cruise_speed
        INC A
        LD ($F6B7),A
        JR movement_pixels
cruise_speed:
        LD C,3
movement_pixels:
        LD HL,X
        BIT 0,B
        JR Z,right
        LD A,(HL)
        CP 8
        JR Z,right
        DEC (HL)
right:
        BIT 1,B
        JR Z,down
        LD A,(HL)
        CP 224
        JR Z,down
        INC (HL)
down:
        INC HL
        BIT 2,B
        JR Z,up
        LD A,(HL)
        CP 152
        JR Z,up
        INC (HL)
up:
        BIT 3,B
        JR Z,pixel_step_done
        LD A,(HL)
        OR A
        JR Z,pixel_step_done
        DEC (HL)
pixel_step_done:
        DEC C
        JR NZ,movement_pixels
move_done:
        LD A,(WASCOPY)
        OR A
        JR Z,step_in_patch
        LD A,(X)
        RRCA
        RRCA
        RRCA
        AND 31
        CP 28
        JR Z,check_patch_y
        LD E,A
        LD A,($F6B4)
        LD D,A
        LD A,E
        SUB D
        JR C,reject_step
        CP 6
        JR NC,reject_step
check_patch_y:
        LD A,(Y)
        CP 152
        JR Z,step_in_patch
        LD E,A
        LD A,($F6B5)
        LD D,A
        LD A,E
        SUB D
        JR C,reject_step
        CP 24
        JR C,step_in_patch
reject_step:
        LD A,(OX)
        LD (X),A
        LD A,(OY)
        LD (Y),A
        JP finish_tick
step_in_patch:
        LD A,(HAS)
        OR A
        JR Z,moving
        LD A,(OX)
        LD B,A
        LD A,(X)
        CP B
        JR NZ,moving
        LD A,(OY)
        LD B,A
        LD A,(Y)
        CP B
        JP Z,finish_tick
moving:
        LD A,(X)
        ADD A,4
        RRCA
        RRCA
        RRCA
        AND 31
        LD ($7AA1),A
        LD A,(Y)
        ADD A,4
        RRCA
        RRCA
        RRCA
        AND 31
        LD ($7AA2),A
        CALL render
finish_tick:
        LD A,(WASCOPY)
        OR A
        CALL NZ,fast_mark_owners
        RET
inactive:
        XOR A
        LD ($5BC2),A
        LD (HAS),A
        RET
phase_pointer:
        LD H,0
        AND 7
        LD L,A
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD D,H
        LD E,L
        ADD HL,HL
        ADD HL,DE
        LD DE,$ED80 ; centre pose cache
        ADD HL,DE
        RET
address:
        LD A,(CY)
        LD D,A
        AND 7
        OR $40
        LD H,A
        LD A,D
        AND $C0
        RRCA
        RRCA
        RRCA
        OR H
        LD H,A
        LD A,D
        AND $38
        RLCA
        RLCA
        LD L,A
        LD A,(CX)
        OR L
        LD L,A
        RET
collision:
        LD A,($7A98)
        OR A
        RET NZ
        LD A,(CY)
        AND $F8
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        LD A,(CX)
        LD E,A
        LD D,0
        ADD HL,DE
        LD DE,MAP
        ADD HL,DE
        LD A,(HL)
        CP $80
        RET C
        LD A,(ATTR)
        AND 7
        LD B,0
        JR Z,no_ink
        LD A,(BITS)
        LD B,A
no_ink:
        LD A,(ATTR)
        AND $38
        JR Z,no_paper
        LD A,(BITS)
        CPL
        OR B
        LD B,A
no_paper:
        LD A,(MASK)
        AND B
        RET Z
        LD A,1
        LD ($5BC4),A
        RET
render:
        LD A,(X)
        CALL phase_pointer
        LD (PHASE),HL
        LD A,(OX)
        CALL phase_pointer
        LD (OLDPHASE),HL
        LD A,(X)
        LD B,A
        LD A,(OX)
        CP B
        JR C,left_ready
        LD A,B
left_ready:
        RRCA
        RRCA
        RRCA
        AND 31
        LD (LEFT),A
        LD A,(Y)
        LD B,A
        LD A,(OY)
        CP B
        JR C,top_ready
        LD A,B
top_ready:
        LD (TOP),A
        LD (CY),A
        LD A,(Y)
        LD B,A
        LD A,(OY)
        SUB B
        JR NC,damage_height_positive
        NEG
damage_height_positive:
        ADD A,8
        LD ($F6B8),A
        LD A,(LEFT)
        LD (CX),A
        LD IX,$F800
        LD IY,$F790
        LD A,($F6B8)
        LD B,A
fill_row:
        CALL address
        LD (IX),L
        LD (IX+1),H
        INC IX
        INC IX
        LD A,(WASCOPY)
        OR A
        JP NZ,fill_backing_row
        PUSH HL
        LD C,5
fill_pixels:
        LD A,(HL)
        LD (IY),A
        INC HL
        INC IY
        DEC C
        JR NZ,fill_pixels
        POP HL
        SET 5,H
        DUP 5
        DEC IY
        EDUP
        LD A,$81
        OUT ($F4),A
        LD C,5
fill_attrs:
        LD A,(HL)
        LD (IY+55),A
        INC HL
        INC IY
        DEC C
        JR NZ,fill_attrs
        LD A,$89
        OUT ($F4),A
        LD HL,CY
        INC (HL)
        DJNZ fill_row
fill_complete:
        LD A,(WASCOPY)
        OR A
        JR NZ,old_removed
        LD A,(HAS)
        OR A
        JR Z,old_removed
        LD A,(OY)
        LD B,A
        LD A,(OX)
        CALL scratch_position
        LD HL,(OLDPHASE)
        LD DE,64
        ADD HL,DE
        LD IX,OLD
        LD B,8
remove_row:
        LD C,4
remove_cell:
        LD A,(HL)
        OR A
        JR Z,remove_empty
        LD E,A
        LD A,(IX)
        XOR (IY)
        AND E
        XOR (IY)
        LD (IY),A
        LD A,(IX+32)
        LD (IY+55),A
remove_empty:
        INC HL
        INC IX
        INC IY
        DEC C
        JR NZ,remove_cell
        INC IY
        DJNZ remove_row
old_removed:
        CALL check_collision_window
        LD A,(Y)
        LD B,A
        LD A,(X)
        CALL scratch_position
        LD IX,(PHASE)
        LD HL,NEXT
        LD DE,NEXT+32
        LD B,8
compose_row:
        LD C,4
compose_cell:
        LD A,(IY)
        LD (HL),A
        INC HL
        LD A,(IY+55)
        LD (DE),A
        INC DE
        LD A,(IX+64)
        CPL
        AND (IY)
        OR (IX)
        LD (IY),A
        LD A,(IX+64)
        OR A
        JR Z,new_empty
        LD A,(IX+32)
        LD (IY+55),A
new_empty:
        INC IX
        INC IY
        DEC C
        JR NZ,compose_cell
        INC IY
        DJNZ compose_row
        LD IX,$F800
        LD IY,$F790
        LD A,($F6B8)
        LD B,A
publish_row:
        LD L,(IX)
        LD H,(IX+1)
        INC IX
        INC IX
        PUSH HL
        LD A,($F6B8)
        SUB B
        LD C,A
        LD A,(TOP)
        ADD A,C
        CP 160
        JR C,publish_row_valid
        POP HL
        DUP 5
        INC IY
        EDUP
        DEC B
        JP NZ,publish_row
        JP publication_done
publish_row_valid:
        LD C,5
publish_pixels:
        LD A,(LEFT)
        CP 28
        JR C,publish_pixel_in_bounds
        LD A,C
        CP 1
        JR Z,keep_pixel
publish_pixel_in_bounds:
        LD A,(WASCOPY)
        OR A
        JR Z,visible_pixel_only
        SET 5,H
        LD A,(IY)
        LD (HL),A
        RES 5,H
visible_pixel_only:
        LD A,(IY)
        CP (HL)
        JR Z,keep_pixel
        LD (HL),A
keep_pixel:
        INC HL
        INC IY
        DEC C
        JR NZ,publish_pixels
        POP HL
        SET 5,H
        DUP 5
        DEC IY
        EDUP
        LD A,$81
        OUT ($F4),A
        LD C,5
publish_attrs:
        LD A,(LEFT)
        CP 28
        JR C,publish_attr_in_bounds
        LD A,C
        CP 1
        JR Z,keep_published_attr
publish_attr_in_bounds:
        LD A,(IY+55)
        CP (HL)
        JR Z,keep_published_attr
        LD (HL),A
keep_published_attr:
        INC HL
        INC IY
        DEC C
        JR NZ,publish_attrs
        LD A,$89
        OUT ($F4),A
        LD A,(WASCOPY)
        OR A
        JR Z,no_backing_attr_write
        LD L,(IX-2)
        LD H,(IX-1)
        DUP 5
        DEC IY
        EDUP
        LD A,$8D
        OUT ($F4),A
        LD C,5
publish_backing_attr:
        LD A,(LEFT)
        CP 28
        JR C,publish_backing_in_bounds
        LD A,C
        CP 1
        JR Z,skip_backing_attr
publish_backing_in_bounds:
        LD A,(IY+55)
        LD (HL),A
skip_backing_attr:
        INC HL
        INC IY
        DEC C
        JR NZ,publish_backing_attr
        LD A,$89
        OUT ($F4),A
no_backing_attr_write:
        DEC B
        JP NZ,publish_row
publication_done:
        LD HL,NEXT
        LD DE,OLD
        LD BC,64
        LDIR
        LD A,(X)
        LD (OX),A
        LD A,(Y)
        LD (OY),A
        LD A,1
        LD (HAS),A
        RET
scratch_position:
        RRCA
        RRCA
        RRCA
        AND 31
        LD C,A
        LD A,(LEFT)
        LD E,A
        LD A,C
        SUB E
        LD C,A
        LD A,(TOP)
        LD E,A
        LD A,B
        SUB E
        LD E,A
        ADD A,A
        ADD A,A
        ADD A,E
        ADD A,C
        LD E,A
        LD D,0
        LD IY,$F790
        ADD IY,DE
        RET
check_collision_window:
        LD A,($7A98)
        OR A
        RET NZ
        LD A,(Y)
        AND $F8
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        LD A,(X)
        RRCA
        RRCA
        RRCA
        AND 31
        LD E,A
        LD D,0
        ADD HL,DE
        LD DE,MAP
        ADD HL,DE
        LD B,1
        LD A,(Y)
        AND 7
        JR Z,coarse_row
        INC B
coarse_row:
        LD C,4
coarse_cell:
        LD A,(HL)
        CP $80
        JR NC,detailed_collision
        INC HL
        DEC C
        JR NZ,coarse_cell
        LD DE,28
        ADD HL,DE
        DJNZ coarse_row
        RET
detailed_collision:
        LD A,(Y)
        LD B,A
        LD A,(X)
        CALL scratch_position
        LD IX,(PHASE)
        LD A,(Y)
        LD (CY),A
        LD A,8
        LD (ROW),A
collision_row:
        LD A,(X)
        RRCA
        RRCA
        RRCA
        AND 31
        LD (CX),A
        LD A,4
        LD (COL),A
collision_cell:
        LD A,(IY)
        LD (BITS),A
        LD A,(IY+55)
        LD (ATTR),A
        LD A,(IX+64)
        LD (MASK),A
        CALL collision
        INC IX
        INC IY
        LD HL,CX
        INC (HL)
        LD HL,COL
        DEC (HL)
        JR NZ,collision_cell
        INC IY
        LD HL,CY
        INC (HL)
        LD HL,ROW
        DEC (HL)
        JR NZ,collision_row
        RET
prepare_copy:
        LD A,($5BC2)
        OR A
        RET Z
        LD A,1
        LD ($5BCD),A
        LD HL,$7E00
        LD DE,MAP
        LD BC,640
        LDIR
        CALL cache_backing
overlay_only:
        DI
        LD A,1
        LD ($5BC3),A
        LD (WASCOPY),A
        CALL render
        CALL fast_mark_owners
        XOR A
        LD ($5BCD),A
        RET
restore_copy:
        LD A,($5BC3)
        OR A
        RET Z
        CALL backing_to_world
        XOR A
        LD (META),A
        CALL fast_retained_window
        LD A,(X)
        LD (OX),A
        LD A,(Y)
        LD (OY),A
        LD A,1
        LD (HAS),A
        XOR A
        LD ($5BC3),A
        RET
fast_retained_window:
        XOR A
        LD (ROW),A
        LD A,(Y)
        LD (CY),A
fast_world_row:
        LD A,(X)
        RRCA
        RRCA
        RRCA
        AND 31
        LD (CX),A
        CALL address
        SET 5,H
        LD ($F69E),HL
        CALL fast_pointers
        LD HL,($F69E)
        LD A,(META)
        OR A
        JR Z,fast_restore_pixels
        LD C,4
fast_prepare_pixels:
        LD A,(HL)
        LD (DE),A
        LD A,(IY)
        OR A
        JR Z,fast_empty_pixel
        CP 3
        JR Z,fast_empty_pixel
        LD A,(IX+64)
        CPL
        AND (HL)
        OR (IX)
        JR fast_store_pixel
fast_empty_pixel:
        LD A,(IX)
fast_store_pixel:
        LD (HL),A
        INC HL
        INC DE
        INC IX
        INC IY
        DEC C
        JR NZ,fast_prepare_pixels
        JR fast_world_attributes
fast_restore_pixels:
        LD C,4
fast_restore_pixel:
        LD A,(DE)
        LD (HL),A
        LD (VB),A
        LD A,(IY)
        OR A
        JR Z,fast_sky_pixel
        CP 3
        JR Z,fast_sky_pixel
        LD A,(VB)
        JR fast_save_old_pixel
fast_sky_pixel:
        XOR A
fast_save_old_pixel:
        LD (IX),A
        INC HL
        INC DE
        INC IX
        INC IY
        DEC C
        JR NZ,fast_restore_pixel
fast_world_attributes:
        CALL fast_pointers
        LD HL,32
        ADD HL,DE
        EX DE,HL
        LD HL,($F69E)
        RES 5,H
        LD C,4
        LD A,(META)
        OR A
        JR Z,fast_restore_attrs
        LD A,$8D
        OUT ($F4),A
fast_prepare_attr:
        LD A,(HL)
        LD (DE),A
        LD (VB),A
        LD A,(IY)
        OR A
        JR Z,fast_empty_attr
        CP 3
        JR Z,fast_empty_attr
        LD A,(VB)
        JR fast_attr_background
fast_empty_attr:
        XOR A
fast_attr_background:
        LD (VB),A
        LD A,(IX+64)
        OR A
        JR Z,fast_background_attr
        LD A,(IX+32)
        JR fast_store_attr
fast_background_attr:
        LD A,(VB)
fast_store_attr:
        LD (HL),A
        INC HL
        INC DE
        INC IX
        INC IY
        DEC C
        JR NZ,fast_prepare_attr
        JR fast_attr_done
fast_restore_attrs:
        LD A,$8D
        OUT ($F4),A
fast_restore_attr:
        LD A,(DE)
        LD (HL),A
        LD (VB),A
        LD A,(IY)
        OR A
        JR Z,fast_sky_attr
        CP 3
        JR Z,fast_sky_attr
        LD A,(VB)
        JR fast_save_old_attr
fast_sky_attr:
        XOR A
fast_save_old_attr:
        LD (IX+32),A
        INC HL
        INC DE
        INC IX
        INC IY
        DEC C
        JR NZ,fast_restore_attr
fast_attr_done:
        LD A,$89
        OUT ($F4),A
        LD HL,CY
        INC (HL)
        LD HL,ROW
        INC (HL)
        LD A,(HL)
        CP 8
        JP NZ,fast_world_row
        JR fast_mark_entry
fast_mark_owners:
        LD A,1
        LD (META),A
fast_mark_entry:
        LD A,(Y)
        LD (CY),A
        AND 7
        LD B,1
        JR Z,fast_owner_row
        INC B
fast_owner_row:
        LD A,(X)
        RRCA
        RRCA
        RRCA
        AND 31
        LD (CX),A
        CALL metadata_address
        LD C,4
fast_owner_cell:
        LD A,(META)
        OR A
        JR Z,fast_clear_owner
        LD A,(HL)
        OR A
        JR NZ,fast_owner_next
        LD (HL),3
        JR fast_owner_next
fast_clear_owner:
        LD A,(HL)
        CP 3
        JR NZ,fast_owner_next
        LD (HL),0
fast_owner_next:
        INC HL
        DEC C
        JR NZ,fast_owner_cell
        LD A,(CY)
        ADD A,8
        LD (CY),A
        DJNZ fast_owner_row
        RET
fast_pointers:
        LD A,(ROW)
        ADD A,A
        ADD A,A
        LD E,A
        LD D,0
        LD A,(META)
        OR A
        LD IX,OLD
        JR Z,fast_pointer_base
        LD IX,(PHASE)
fast_pointer_base:
        ADD IX,DE
        LD HL,WORLD
        ADD HL,DE
        LD ($F69C),HL
        LD A,(CY)
        AND $F8
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        LD A,(CX)
        LD E,A
        LD D,0
        ADD HL,DE
        LD DE,MAP
        ADD HL,DE
        PUSH HL
        POP IY
        LD DE,($F69C)
        RET
capture_fire:
        LD A,($74FA)
        AND $10
        LD B,A
        LD A,($F6A0)
        CP B
        JR Z,fire_edge_done
        LD A,B
        LD ($F6A0),A
        OR A
        JR Z,fire_released
        XOR A
        LD ($F6A1),A
        JR fire_edge_done
fire_released:
        LD A,($F6A4)
        CP 4
        JR NC,fire_edge_done
        INC A
        LD ($F6A4),A
        LD A,($F6A3)
        LD E,A
        LD D,0
        LD HL,$F6B0
        ADD HL,DE
        LD A,($F6A1)
        ADD A,A
        JR NZ,fire_charge_ready
        LD A,2
fire_charge_ready:
        LD (HL),A
        LD A,E
        INC A
        AND 3
        LD ($F6A3),A
fire_edge_done:
        LD A,($F6A5)
        OR A
        RET Z
        LD HL,$74FA
        RES 4,(HL)
        RET
serve_fire:
        LD A,($F6A5)
        OR A
        JR Z,serve_next
        LD A,($7ABF)
        OR A
        RET NZ
        LD ($F6A5),A
serve_next:
        LD A,($F6A4)
        OR A
        RET Z
        DEC A
        LD ($F6A4),A
        LD A,($F6A2)
        LD E,A
        LD D,0
        LD HL,$F6B0
        ADD HL,DE
        LD A,($7ABF)
        CP (HL)
        JR NC,serve_charge
        LD A,(HL)
serve_charge:
        LD ($7ABF),A
        LD A,E
        INC A
        AND 3
        LD ($F6A2),A
        LD A,1
        LD ($F6A5),A
        LD HL,$74FA
        RES 4,(HL)
        RET
fill_backing_row:
        LD A,(CY)
        PUSH BC
        PUSH IX
        LD A,(LEFT)
        LD (CX),A
        CALL backing_address
        LD C,5
backing_fill_cell:
        LD A,(HL)
        LD (IY),A
        PUSH HL
        LD DE,320
        ADD HL,DE
        LD A,(HL)
        LD (IY+55),A
        POP HL
        INC HL
        INC IY
        DEC C
        JR NZ,backing_fill_cell
        POP IX
        POP BC
        LD HL,CY
        INC (HL)
        DEC B
        JP NZ,fill_row
        JP fill_complete
backing_address:
        LD A,(CY)
        LD E,A
        LD A,($F6B5)
        LD D,A
        LD A,E
        SUB D
        LD L,A
        LD H,0
        ADD HL,HL
        LD D,H
        LD E,L
        ADD HL,HL
        ADD HL,HL
        ADD HL,DE
        LD A,(CX)
        LD E,A
        LD A,($F6B4)
        LD D,A
        LD A,E
        SUB D
        LD E,A
        LD D,0
        ADD HL,DE
        LD DE,$F100
        ADD HL,DE
        RET
cache_backing:
        EI
        LD A,(X)
        RRCA
        RRCA
        RRCA
        AND 31
        SUB 3
        JR NC,patch_left_nonnegative
        XOR A
patch_left_nonnegative:
        CP 22
        JR C,patch_left_ready
        LD A,22
patch_left_ready:
        LD ($F6B4),A
        LD A,(Y)
        SUB 12
        JR NC,patch_top_nonnegative
        XOR A
patch_top_nonnegative:
        CP 128
        JR C,patch_top_ready
        LD A,128
patch_top_ready:
        LD ($F6B5),A
        LD (CY),A
        LD A,32
        LD (ROW),A
        LD DE,$F100
cache_patch_row:
        LD A,($F6B4)
        LD (CX),A
        PUSH DE
        CALL address
        SET 5,H
        LD ($F69E),HL
        CALL cache_map_pointer
        POP DE
        LD HL,($F69E)
        LD C,10
cache_pixel:
        LD A,(IY)
        OR A
        JR Z,cache_empty_pixel
        CP 3
        JR Z,cache_empty_pixel
        LD A,(HL)
        JR cache_write_pixel
cache_empty_pixel:
        XOR A
cache_write_pixel:
        LD (DE),A
        INC HL
        INC DE
        INC IY
        DEC C
        JR NZ,cache_pixel
        LD ($F69C),DE
        PUSH DE
        CALL cache_map_pointer
        POP DE
        LD HL,310
        ADD HL,DE
        EX DE,HL
        LD HL,($F69E)
        RES 5,H
        DI
        LD A,$8D
        OUT ($F4),A
        LD C,10
cache_attr:
        LD A,(IY)
        OR A
        JR Z,cache_empty_attr
        CP 3
        JR Z,cache_empty_attr
        LD A,(HL)
        JR cache_write_attr
cache_empty_attr:
        XOR A
cache_write_attr:
        LD (DE),A
        INC HL
        INC DE
        INC IY
        DEC C
        JR NZ,cache_attr
        LD A,$89
        OUT ($F4),A
        EI
        LD DE,($F69C)
        LD HL,CY
        INC (HL)
        LD HL,ROW
        DEC (HL)
        JP NZ,cache_patch_row
        DI
        RET
cache_map_pointer:
        LD A,(CY)
        AND $F8
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        LD A,(CX)
        LD E,A
        LD D,0
        ADD HL,DE
        LD DE,MAP
        ADD HL,DE
        PUSH HL
        POP IY
        RET
backing_to_world:
        LD A,(Y)
        LD (CY),A
        LD A,8
        LD (ROW),A
        LD IX,WORLD
backing_world_row:
        LD A,(X)
        RRCA
        RRCA
        RRCA
        AND 31
        LD (CX),A
        CALL backing_address
        LD C,4
backing_world_cell:
        LD A,(HL)
        LD (IX),A
        PUSH HL
        LD DE,320
        ADD HL,DE
        LD A,(HL)
        LD (IX+32),A
        POP HL
        INC HL
        INC IX
        DEC C
        JR NZ,backing_world_cell
        LD HL,CY
        INC (HL)
        LD HL,ROW
        DEC (HL)
        JR NZ,backing_world_row
        RET
dispatch_normal_fire:
        LD A,($F6A5)
        OR A
        RET NZ
        LD A,($F6A4)
        OR A
        RET Z
        LD A,($F6A2)
        LD E,A
        LD D,0
        LD HL,$F6B0
        ADD HL,DE
        LD A,(HL)
        CP 12
        RET NC
        LD A,($F6A4)
        DEC A
        LD ($F6A4),A
        LD A,E
        INC A
        AND 3
        LD ($F6A2),A
        XOR A
        LD ($7ABF),A
        LD A,(X)
        ADD A,4
        RRCA
        RRCA
        RRCA
        AND 31
        INC A
        LD ($5BC9),A
        LD A,(Y)
        ADD A,4
        RRCA
        RRCA
        RRCA
        AND 31
        LD ($5BCA),A
        LD A,1
        LD ($5BC8),A
        RET
metadata_address:
        LD A,(CY)
        RRCA
        RRCA
        RRCA
        RRCA
        RRCA
        RRCA
        AND 3
        ADD A,$7E
        LD H,A
        LD A,(CY)
        AND $38
        RLCA
        RLCA
        LD L,A
        LD A,(CX)
        OR L
        LD L,A
        RET
        ASSERT $ <= $ED80


