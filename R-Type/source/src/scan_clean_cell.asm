; Skip a run of empty clean cells using parallel ID/dirty pointers.
; Nonempty or dirty cells rejoin the exact native dispatcher at886F.
        ORG $1F70
scan_clean_cell:
        OR A
        JP NZ,$8881
        LD B,D
        INC D
        INC D
        INC D
        LD A,(DE)
 IFDEF ROM_ONLY
        AND 1
 ELSE
        AND A
 ENDIF
        LD D,B
        JR NZ,scan_dirty_empty
        PUSH BC
        LD B,H
        LD H,D
        LD A,D
        ADD A,3
        LD D,A
scan_empty_run:
        DEC E
        DEC L
        LD A,E
        AND $1F
        JR Z,scan_run_row_done
        LD A,(HL)
        AND A
        JR NZ,scan_run_active
        LD A,(DE)
 IFDEF ROM_ONLY
        AND 1
 ELSE
        AND A
 ENDIF
        JR Z,scan_empty_run
scan_run_active:
        LD D,H
        LD H,B
        POP BC
        JP $886F
scan_run_row_done:
        LD D,H
        LD H,B
        POP BC
        JP $8846
scan_dirty_empty:
        XOR A
        JP $8881
        ASSERT $ <= $2000
