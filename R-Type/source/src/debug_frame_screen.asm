        ORG $8000
debug_entry:
        DI
        PUSH HL
        PUSH IX
        PUSH IY
        LD HL,0
        ADD HL,SP
        LD A,$11
        OUT ($F4),A
        LD DE,$7C00
        LD BC,32
        LDIR
        LD HL,0
        ADD HL,SP
        LD DE,16
        ADD HL,DE
        LD ($7C20),HL
        LD A,($FBCA)
        LD ($7C22),A
        XOR A
        LD ($7C23),A
        LD IX,$7C40
        LD IY,sources
        LD B,16
capture_word:
        LD L,(IY+0)
        LD H,(IY+1)
        INC IY
        INC IY
        CALL $F910
        LD A,$11
        OUT ($F4),A
        LD (IX+0),E
        LD (IX+1),D
        INC IX
        INC IX
        DJNZ capture_word
        ; Native controls were captured before changing the AY register latch.
        LD BC,$00F5
        LD A,14
        OUT (C),A
        LD BC,$01F6
        IN A,(C)
        LD ($7C60),A
        LD B,2
        IN A,(C)
        LD ($7C61),A
        LD HL,$4000
        LD DE,$A000
        LD BC,$1800
        LDIR
        LD HL,$6000
        LD DE,$C000
        LD BC,$1800
        LDIR
        LD A,$40
        OUT ($FF),A
        LD HL,$4000
        LD DE,$4001
        LD BC,$17FF
        LD (HL),0
        LDIR
        LD HL,$5800
        LD DE,$5801
        LD BC,767
        LD (HL),7
        LDIR
        ; Takeover is deliberately terminal: game and audio stay frozen.
        LD BC,$00F5
        LD A,8
        OUT (C),A
        INC C
        XOR A
        OUT (C),A
        DEC C
        LD A,9
        OUT (C),A
        INC C
        XOR A
        OUT (C),A
        DEC C
        LD A,10
        OUT (C),A
        INC C
        XOR A
        OUT (C),A
        LD DE,$4001
        LD HL,heading
        CALL puts
        LD DE,$4021
        LD IX,fields
        LD A,28
        LD ($7C24),A
next_field:
        LD L,(IX+0)
        LD H,(IX+1)
        PUSH DE
        CALL puts
        LD L,(IX+2)
        LD H,(IX+3)
        LD C,(HL)
        INC HL
        LD A,(HL)
        CALL hex_byte
        LD A,C
        CALL hex_byte
        POP DE
        LD A,E
        ADD A,16
        LD E,A
        JR NC,row_next
        LD A,D
        ADD A,8
        LD D,A
row_next:
        LD BC,4
        ADD IX,BC
        LD HL,$7C24
        DEC (HL)
        JR NZ,next_field
debug_halt:
        LD BC,$7FFE
        IN A,(C)
        AND 1
        JR NZ,debug_halt
        LD HL,$A000
        LD DE,$4000
        LD BC,$1800
        LDIR
        LD HL,$C000
        LD DE,$6000
        LD BC,$1800
        LDIR
        LD A,$42
        OUT ($FF),A
ram_halt:
        HALT
        JR ram_halt
hex_byte:
        PUSH AF
        RRCA
        RRCA
        RRCA
        RRCA
        CALL hex_digit
        POP AF
hex_digit:
        AND 15
        ADD A,'0'
        CP '9'+1
        JR C,print_char
        ADD A,7
print_char:
        PUSH HL
        PUSH BC
        SUB 32
        LD L,A
        LD H,0
        ADD HL,HL
        ADD HL,HL
        ADD HL,HL
        LD BC,font
        ADD HL,BC
        LD B,8
glyph:
        LD A,(HL)
        LD (DE),A
        INC HL
        INC D
        DJNZ glyph
        LD A,D
        SUB 8
        LD D,A
        INC E
        POP BC
        POP HL
        RET
puts:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        CALL print_char
        JR puts
heading: DB 'R39 FRAME - SPACE FOR RAM',0
pc_label: DB 'PC ',0
sp_label: DB 'SP ',0
af_label: DB 'AF ',0
bc_label: DB 'BC ',0
de_label: DB 'DE ',0
hl_label: DB 'HL ',0
ix_label: DB 'IX ',0
iy_label: DB 'IY ',0
map_label: DB 'MAP ',0
level_label: DB 'LEVEL ',0
input_label: DB 'INPUT ',0
world_label: DB 'WORLD ',0
object_label: DB 'OBJECT ',0
cache_label: DB 'CACHE ',0
music_label: DB 'MSP ',0
joy_label: DB 'JOYS ',0
game_label: DB 'GAME ',0
seq_label: DB 'MSEQ ',0
st0: DB 'STACK 0 ',0
st1: DB 'STACK 1 ',0
st2: DB 'STACK 2 ',0
st3: DB 'STACK 3 ',0
decoder_label: DB 'KEYFN ',0
attr_label: DB 'ATTR ',0
draw_label: DB 'DRAW ',0
valid_label: DB 'VALID ',0
sfx_label: DB 'SFX ',0
timer_label: DB 'TIMER ',0
fields:
        DW pc_label,$7C0E,sp_label,$7C20,af_label,$7C0C,bc_label,$7C0A
        DW de_label,$7C08,hl_label,$7C04,ix_label,$7C02,iy_label,$7C00
        DW map_label,$7C22,level_label,$7C40,input_label,$7C42,world_label,$7C48
        DW object_label,$7C4A,cache_label,$7C50,music_label,$7C56,joy_label,$7C60
        DW game_label,$7C46,seq_label,$7C58,st0,$7C10,st1,$7C12,st2,$7C14,st3,$7C16
        DW decoder_label,$7C44,attr_label,$7C4C,draw_label,$7C4E
        DW valid_label,$7C52,sfx_label,$7C54,timer_label,$7C5A
sources:
        DW $719C,$74FA,$74FC,$7AA3,$7A90,$7A9C,$8EB0,$8EBE
        DW $FD48,$FD4A,$FBC0,$FD80,$FD82,$7A8A,$7A84,$7ABE
font: INCBIN "assets/fullgame_preloader_font.bin"
        ASSERT $ <= $84B4
