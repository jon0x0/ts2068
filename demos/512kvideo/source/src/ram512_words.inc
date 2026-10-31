; Expanded TSVideoCodec paired-cell records: address, two replacement bytes.
; Every 256-byte block holds 64 independent paired-word writes.
ram_words64:
        di
        ld (W_SAVED_SP),sp
        ld sp,(W_SOURCE)
        DUP 64
        pop hl
        pop de
        ld (hl),e
        inc l
        ld (hl),d
        EDUP
        ld (W_SOURCE),sp
        ld sp,(W_SAVED_SP)
        ld a,(IRQ_ALLOW)
        or a
        ret z
        ei
        ret
