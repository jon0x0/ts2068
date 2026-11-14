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
        JP loop
irq:
        EI
        RETI
controls:
        LD D,0
        LD BC,$FDFE
        IN A,(C)
        BIT 0,A ; Q left
        JR NZ,key_right
        SET 0,D
key_right:
        BIT 1,A ; W right
        JR NZ,key_up
        SET 1,D
key_up:
        LD B,$DF
        IN A,(C)
        BIT 1,A ; O up
        JR NZ,key_down
        SET 3,D
key_down:
        LD B,$BF
        IN A,(C)
        BIT 2,A ; K down
        JR NZ,sticks
        SET 2,D
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
        SET 5,H
        LD A,(erase)
        OR A
        LD A,0
        JR NZ,store_colour
        LD A,(IY)
store_colour:
        LD (HL),A
        RES 5,H
        INC HL
        INC IX
        INC IY
        DJNZ paint_byte
        LD HL,scan_y
        INC (HL)
        POP BC
        DJNZ paint_row
        RET
position_x: DB 40
position_y: DB 80
scan_y: DB 0
erase: DB 0
        ASSERT $ < $9000
        DS $9000-$,0
phases: INCBIN "build/diagnostics/pixel_movement_trial/ship_phases.bin"
