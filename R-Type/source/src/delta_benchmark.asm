        ORG $8000
raw:
        LD DE,$4000
        LD BC,$1800
        LDIR
        LD DE,$6000
        LD BC,$1800
        LDIR
        RET
scan:
        LD DE,$4000
        LD BC,$1800
        CALL scan_plane
        LD DE,$6000
        LD BC,$1800
        CALL scan_plane
        RET
scan_plane:
        LD A,(DE)
        CP (HL)
        JR Z,scan_same
        LD A,(HL)
        LD (DE),A
scan_same:
        INC DE
        INC HL
        DEC BC
        LD A,B
        OR C
        JR NZ,scan_plane
        RET
xor:
        LD DE,$4000
        CALL xor_plane
        LD DE,$6000
        CALL xor_plane
        RET
xor_plane:
        LD A,(HL)
        INC HL
        OR A
        RET Z
        JP M,xor_literal
        PUSH HL
        LD L,A
        LD H,0
        ADD HL,DE
        EX DE,HL
        POP HL
        JR xor_plane
xor_literal:
        AND $7F
        INC A
        LD C,A
xor_bytes:
        LD A,(DE)
        XOR (HL)
        LD (DE),A
        INC HL
        INC DE
        DEC C
        JR NZ,xor_bytes
        JR xor_plane
sparse:
        CALL sparse_plane
        CALL sparse_plane
        RET
sparse_plane:
        LD C,(HL)
        INC HL
        LD B,(HL)
        INC HL
        LD A,B
        OR C
        RET Z
sparse_bytes:
        LD E,(HL)
        INC HL
        LD D,(HL)
        INC HL
        LD A,(HL)
        INC HL
        LD (DE),A
        DEC BC
        LD A,B
        OR C
        JR NZ,sparse_bytes
        RET
