; Standalone TS2068 hardware movement proof, not full-game integration.
        ORG $8000
        DI
        LD SP,$FDE0
        XOR A
        OUT ($F4),A
        LD HL,$4000
        LD DE,$4001
        LD BC,$37FF
        LD (HL),A
        LDIR
        LD HL,$A000
        LD DE,$A001
        LD BC,$37FF
        LD (HL),0
        LDIR
        LD HL,$FE00
        LD DE,$FE01
        LD BC,256
        LD (HL),$FD
        LDIR
        LD A,$C3
        LD ($FDFD),A
        LD HL,irq
        LD ($FDFE),HL
        LD A,$FE
        LD I,A
        IM 2
        LD A,2
        OUT ($FF),A
        XOR A
        OUT ($FE),A
        EI
loop:
        HALT
        LD A,(position_x)
        LD (old_x),A
        LD A,(position_y)
        LD (old_y),A
        LD A,1
        LD (erase),A
        CALL paint
        CALL controls
        LD B,A
        LD HL,position_x
        BIT 0,B
        JR Z,no_left
        LD A,(HL)
        CP 8
        JR Z,no_left
        DEC (HL)
no_left:
        BIT 1,B
        JR Z,no_right
        LD A,(HL)
        CP 224
        JR Z,no_right
        INC (HL)
no_right:
        INC HL
        BIT 2,B
        JR Z,no_down
        LD A,(HL)
        CP 152
        JR Z,no_down
        INC (HL)
no_down:
        BIT 3,B
        JR Z,no_up
        LD A,(HL)
        OR A
        JR Z,no_up
        DEC (HL)
no_up:
        XOR A
        LD (erase),A
        CALL paint
        CALL publish_delta
        JP loop
irq:
        EI
        RETI
controls:
        LD D,0
        LD BC,$FBFE ; Q up
        IN A,(C)
        BIT 0,A
        JR NZ,key_down
        SET 3,D
key_down:
        LD B,$FD ; A down
        IN A,(C)
        BIT 0,A
        JR NZ,key_left
        SET 2,D
key_left:
        LD B,$DF ; O left, P right
        IN A,(C)
        BIT 1,A
        JR NZ,key_right
        SET 0,D
key_right:
        BIT 0,A
        JR NZ,sticks
        SET 1,D
sticks:
        LD BC,$00F5
        LD A,7
        OUT (C),A
        INC C
        IN A,(C)
        AND $BF
        OUT (C),A
        DEC C
        LD A,14
        OUT (C),A
        LD BC,$01F6
        IN A,(C)
        LD E,A
        INC B
        IN A,(C)
        AND E
        CPL
        BIT 0,A
        JR Z,joy_down
        SET 3,D
joy_down:
        BIT 1,A
        JR Z,joy_left
        SET 2,D
joy_left:
        BIT 2,A
        JR Z,joy_right
        SET 0,D
joy_right:
        BIT 3,A
        JR Z,controls_done
        SET 1,D
controls_done:
        LD A,D
        RET
paint:
        LD A,(position_x)
        AND 7
        LD H,0
        LD L,A
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL ; phase*32
        LD D,H
        LD E,L
        ADD HL,HL
        ADD HL,DE ; phase*96
        LD DE,phases+768 ; centre pose
        ADD HL,DE
        PUSH HL
        POP IX
        LD DE,32
        ADD HL,DE
        PUSH HL
        POP IY
        LD A,(position_y)
        LD (scan_y),A
        LD B,8
paint_row:
        PUSH BC
        LD A,(scan_y)
        LD D,A
        AND 7
        OR $40
        LD H,A
        SET 7,H ; build bitmap at A000, never erase the visible screen
        RES 6,H
        SET 5,H
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
        LD A,(position_x)
        RRCA
        RRCA
        RRCA
        AND 31
        OR L
        LD L,A
        LD B,4
paint_byte:
        LD A,(erase)
        OR A
        LD A,0
        JR NZ,store_pixel
        LD A,(IX)
store_pixel:
        LD (HL),A
        RES 5,H
        SET 6,H ; shadow ECM at C000
        LD A,(erase)
        OR A
        LD A,0
        JR NZ,store_colour
        LD A,(IY)
store_colour:
        LD (HL),A
        RES 6,H
        SET 5,H ; shadow bitmap at A000
        INC HL
        INC IX
        INC IY
        DJNZ paint_byte
        LD HL,scan_y
        INC (HL)
        POP BC
        DJNZ paint_row
        RET
publish_delta:
        ; Union of two one-pixel-separated 4x8 byte windows: at most 5x9.
        LD A,(old_x)
        LD B,A
        LD A,(position_x)
        CP B
        JR C,min_x_ready
        LD A,B
min_x_ready:
        RRCA
        RRCA
        RRCA
        AND 31
        LD (union_x),A
        LD A,(old_y)
        LD B,A
        LD A,(position_y)
        CP B
        JR C,min_y_ready
        LD A,B
min_y_ready:
        LD (scan_y),A
        LD B,9
delta_row:
        PUSH BC
        LD A,(scan_y)
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
        LD A,(union_x)
        OR L
        LD L,A
        LD B,5
delta_byte:
        LD A,L
        AND 31
        CP 31
        JR Z,delta_last_column
        CALL delta_cell
        INC HL
        DJNZ delta_byte
        JR delta_next_row
delta_last_column:
        CALL delta_cell
delta_next_row:
        LD HL,scan_y
        INC (HL)
        POP BC
        DJNZ delta_row
        RET
delta_cell:
        LD D,H
        LD E,L
        SET 7,D
        RES 6,D ; visible40 -> shadowA0
        SET 5,D
        LD A,(DE)
        XOR (HL) ; bitmap delta
        JR Z,pixel_same
        XOR (HL) ; apply delta to existing pixels, once
        LD (HL),A
pixel_same:
        SET 5,H ; visible ECM60
        RES 5,D
        SET 6,D ; shadow EC MC0
        LD A,(DE)
        CP (HL)
        JR Z,colour_same
        LD (HL),A
colour_same:
        RES 5,H
        RET
position_x: DB 40
position_y: DB 80
scan_y: DB 0
erase: DB 0
old_x: DB 40
old_y: DB 80
union_x: DB 5
        ASSERT $ < $9000
        DS $9000-$,0
phases: INCBIN "build/diagnostics/pixel_movement_trial/ship_phases.bin"
