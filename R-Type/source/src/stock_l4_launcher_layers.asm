; Temporary HOME predicate hooks for the launcher only. No projectile records
; are removed. Restore projectile ownership after visual drawing so native
; gameplay/contact decisions retain their previous inputs.
 ORG LAYER_CODE
 JP begin_launcher
 JP end_launcher
begin_launcher:
 CP 52
 RET C
 CP 55
 RET NC
 PUSH AF
 PUSH BC
 PUSH DE
 PUSH HL
 CALL $23AC
 LD (PS+141),HL
 LD DE,0
 XOR A
 CALL MASK_CODE
 LD (PS+139),DE
 LD HL,$12CD
 LD ($8ED6),HL
 LD A,$0C
 LD ($8ED8),A
 LD A,$C9
 LD ($8ED9),A
 XOR A
 LD ($8EDA),A
 LD HL,$15CD
 LD ($8F0B),HL
 LD A,$0C
 LD ($8F0D),A
 POP HL
 POP DE
 POP BC
 POP AF
 RET
end_launcher:
 LD A,(CTX+25)
 OR A
 RET NZ
 LD A,(CTX+24)
 CP 52
 RET C
 CP 55
 RET NC
 PUSH BC
 PUSH DE
 PUSH HL
 LD HL,(PS+141)
 LD DE,(PS+139)
 LD A,1
 CALL MASK_CODE
 LD HL,$A71A
 LD ($8ED6),HL
 LD HL,$3128
 LD ($8ED8),HL
 LD A,$C9
 LD ($8EDA),A
 LD HL,$1A1C
 LD ($8F0B),HL
 LD A,$1D
 LD ($8F0D),A
 POP HL
 POP DE
 POP BC
 RET
