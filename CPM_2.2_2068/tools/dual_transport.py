"""Adapt the retained TAP client to the detected modern readiness transport."""
def adapt(source):
    source=source.replace('legacy_wait_ready:\n','legacy_wait_ready:\n        ld a,($eff3)\n        cp 2\n        jp z,dual_ready\n')
    source=source.replace('legacy_preheader:\n','legacy_preheader:\n        ld a,($eff3)\n        cp 2\n        jr nz,.legacy\n        push hl\n        call dual_reset\n        pop hl\n        ret c\n.legacy:\n')
    source=source.replace('LEGACY_BUDGET equ WORK_BASE+$3c0','LEGACY_BUDGET equ $f7c0')
    return source+'\n    include "../src/dual_transport.asm"\n'
