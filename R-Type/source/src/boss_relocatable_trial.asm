; Native Bellmite relocatable composed-object delta trial.
; Precomposed source poses retain overlapping parts and legal ECM pairs.
        ORG $8000
start:  DI
        LD SP,$FDE0
        XOR A
        OUT ($F4),A
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
        LD (origin_x),A
        LD (origin_y),A
        LD (paused),A
        LD (last_space),A
        CALL reset_image
        EI
main:   HALT
        LD BC,$F7FE
        IN A,(C)
        BIT 0,A
        JR Z,preset1
        BIT 1,A
        JR Z,preset2
        BIT 2,A
        JR Z,preset3
        JR keys_done
preset1:
        LD DE,0
        JR preset
preset2:
        LD DE,$1005
        JR preset
preset3:
        LD DE,$200B
preset: LD A,(origin_x)
        CP E
        JR NZ,change_origin
        LD A,(origin_y)
        CP D
        JR Z,keys_done
change_origin:
        LD A,E
        LD (origin_x),A
        LD A,D
        LD (origin_y),A
        CALL reset_image
keys_done:
        LD BC,$7FFE
        IN A,(C)
        AND 1
        LD B,A
        LD A,(last_space)
        CP B
        JR Z,space_done
        LD A,B
        LD (last_space),A
        OR A
        JR NZ,space_done
        LD A,(paused)
        XOR 1
        LD (paused),A
space_done:
        LD A,(paused)
        OR A
        JR NZ,main
        CALL advance
        JP main
irq:    EI
        RETI
reset_image:
        XOR A
        LD HL,$4000
        LD DE,$4001
        LD BC,$37FF
        LD (HL),A
        LDIR
        LD (pose),A
        LD A,1
        LD (direction),A
        LD HL,initial_stream
        CALL publish
        RET
advance:
        LD A,(pose)
        LD B,A
        LD A,(direction)
        CP 1
        JR NZ,reverse
        LD A,B
        CP 7
        JR NZ,forward_step
        LD A,$FF
        LD (direction),A
        JR reverse
forward_step:
        INC A
        LD (pose),A
        JR lookup
reverse:
        LD A,B
        OR A
        JR NZ,reverse_step
        LD A,1
        LD (direction),A
        XOR A
        JR forward_step
reverse_step:
        DEC A
        LD (pose),A
        INC A
lookup: ADD A,A
        LD E,A
        LD D,0
        LD HL,pointers
        ADD HL,DE
        LD E,(HL)
        INC HL
        LD D,(HL)
        EX DE,HL
        CALL publish
        RET
; HL -> row,column,length,(bitmap XOR,ECM XOR)*length. FF end.
; Actual origin variables participate in every destination calculation.
publish:
next_run:
        LD A,(HL)
        INC HL
        CP $FF
        RET Z
        LD B,A
        LD A,(origin_y)
        ADD A,B
        LD B,A
        AND 7
        OR $40
        LD D,A
        LD A,B
        AND $C0
        RRCA
        RRCA
        RRCA
        OR D
        LD D,A
        LD A,B
        AND $38
        RLCA
        RLCA
        LD E,A
        LD A,(origin_x)
        ADD A,E
        ADD A,(HL)
        INC HL
        LD E,A
        LD B,(HL)
        INC HL
next_byte:
        LD A,(HL)
        OR A
        JR Z,same_pixel
        LD A,(DE)
        XOR (HL)
        LD (DE),A
same_pixel:
        INC HL
        SET 5,D
        LD A,(HL)
        OR A
        JR Z,same_attr
        LD A,(DE)
        XOR (HL)
        LD (DE),A
same_attr:
        INC HL
        RES 5,D
        INC E
        DJNZ next_byte
        JP next_run
        ASSERT $ < $8400
        DS $8400-$,0
pointers:
        INCBIN "build/diagnostics/boss_relocatable/pointers.bin"
        DS $8800-$,0
initial_stream:
        INCBIN "build/diagnostics/boss_relocatable/streams.bin"
        ASSERT $ < $F200
origin_x EQU $F200
origin_y EQU $F201
pose EQU $F202
direction EQU $F203
paused EQU $F204
last_space EQU $F205
