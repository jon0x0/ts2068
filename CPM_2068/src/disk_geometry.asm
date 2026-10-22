single_dpb:
    dw 16
    db 3,7,0
    dw 159,127
    db $f0,0
    dw 0,0
; A is the high byte of the count of 128-byte sectors: 5 or 10.
select_geometry:
    cp 5
    ld hl,single_dpb
    ld a,80
    jr z,geometry_selected
    ld hl,dpb
    ld a,160
geometry_selected:
    ld (dph+10),hl
    ld (disk_tracks),a
    ret
