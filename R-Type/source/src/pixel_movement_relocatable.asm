; Relocatable-delta movement trial. Standalone, not full-game integration.
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
        XOR A
        LD (erase),A
        CALL paint
        EI
loop:
        HALT
        LD A,(position_x)
        LD (old_x),A
        LD A,(position_y)
        LD (old_y),A
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
        CALL move_delta
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
        SET 5,H ; visible ECM at6000
        LD A,(erase)
        OR A
        LD A,0
        JR NZ,store_colour
        LD A,(IY)
store_colour:
        LD (HL),A
        RES 5,H ; visible bitmap at4000
        INC HL
        INC IX
        INC IY
        DJNZ paint_byte
        LD HL,scan_y
        INC (HL)
        POP BC
        DJNZ paint_row
        RET
move_delta:
        LD A,(position_x)
        LD B,A
        LD A,(old_x)
        LD C,A
        LD A,B
        SUB C
        INC A
        LD E,A
        LD A,(position_y)
        LD B,A
        LD A,(old_y)
        LD C,A
        LD A,B
        SUB C
        INC A
        LD B,A
        ADD A,A
        ADD A,B
        ADD A,E
        LD L,A
        LD H,0
        LD DE,directions
        ADD HL,DE
        LD A,(HL)
        CP $FF
        RET Z
        LD E,A
        LD A,(old_x)
        AND 7
        ADD A,A
        ADD A,A
        ADD A,A
        ADD A,E
        LD L,A
        LD H,0
        ADD HL,HL
        LD DE,delta_pointers
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD D,(HL)
        PUSH DE
        LD A,(old_x)
        LD B,A
        LD A,(position_x)
        CP B
        JR C,left_ready
        LD A,B
left_ready:
        RRCA
        RRCA
        RRCA
        AND 31
        LD C,A
        LD A,(old_y)
        LD B,A
        LD A,(position_y)
        CP B
        JR C,top_ready
        LD A,B
top_ready:
        POP HL
        JP publish_object
directions: DB 4,2,6,0,$FF,1,5,3,7
position_x: DB 40
position_y: DB 80
scan_y: DB 0
erase: DB 0
old_x: DB 40
old_y: DB 80
union_x: DB 5
        ASSERT $ < $8800
        DS $8800-$,0
        INCLUDE "build/diagnostics/native_relocatable/decoder.inc"
        ASSERT $ < $9000
        DS $9000-$,0
phases: INCBIN "build/diagnostics/pixel_movement_trial/ship_phases.bin"

        ASSERT $ <= $A000
        DS $A000-$,0
delta_pointers: INCBIN "build/diagnostics/native_relocatable/pointers.bin"
delta_streams: INCBIN "build/diagnostics/native_relocatable/streams.bin"
        ASSERT $ < $C000
