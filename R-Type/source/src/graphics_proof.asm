; Human-readable equivalent of build_graphics.py:proof_cartridge.
; Only a graphics comparison viewer. Not the R-Type gameplay renderer.
; DOCK4 remains resident; HSR bit4 is set at every mapping transition.
        ORG $8000
        DB 2,2
        DW entry
        DB $EF,1
        DW 0
entry:  DI
        LD SP,$7FFF
        XOR A
        OUT ($FE),A
        LD A,2
        OUT ($FF),A
cycle:  LD IX,data0
        CALL copy
ready0: CALL delay
        LD IX,data1
        CALL copy
ready1: CALL delay
        LD IX,data2
        CALL copy
ready2: CALL delay
        LD IX,data3
        CALL copy
ready3: CALL delay
        LD IX,data4
        CALL copy
ready4: CALL delay
        JP cycle
copy:   LD B,48
packet: PUSH BC
        LD L,(IX+0)
        LD H,(IX+1)
        LD E,(IX+5)
        LD D,(IX+6)
        LD A,(IX+2)
        LD BC,$F4
        OUT (C),A
        ; Source may hide HOME stack, display or old source ROM.
        ; No CALL, PUSH, POP, RET or interrupt in this mapped interval.
        LD BC,256
        LDIR
        LD A,$10
        LD C,$F4
        OUT (C),A
        ; HOME stack and destination are visible again.
        LD L,(IX+5)
        LD H,(IX+6)
        LD E,(IX+3)
        LD D,(IX+4)
        LD BC,256
        LDIR
        LD DE,7
        ADD IX,DE
        POP BC
        DEC B
        JP NZ,packet
        RET
delay:  LD D,6
delayblock:
        LD BC,0
delayword:
        DEC BC
        LD A,B
        OR C
        JP NZ,delayword
        DEC D
        JP NZ,delayblock
        RET
data0:  INCBIN "build/graphics/proof_descriptors.bin",0,336
data1:  INCBIN "build/graphics/proof_descriptors.bin",336,336
data2:  INCBIN "build/graphics/proof_descriptors.bin",672,336
data3:  INCBIN "build/graphics/proof_descriptors.bin",1008,336
data4:  INCBIN "build/graphics/proof_descriptors.bin",1344,336
        ASSERT $ < $8800
