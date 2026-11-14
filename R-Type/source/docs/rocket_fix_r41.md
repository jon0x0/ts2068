# R41 rocket-induced renderer corruption fix

Replace the complete RTYPE folder with this package and play normally.
No further diagnostic capture is required to establish the reproduced bug.
The prior Caps Shift+D/Space diagnostic remains available; its R38 banner
identifies that unchanged capture engine, not the game-package revision.

The native shared projectile helper9C31 finishes at9C3C with ADD A,20h;
LD(BC),A. Ordinary bullet callers provide valid timer addresses7AF3..7AF5.
The special rocket path9C40 calls9C31 at9C88/9C90 without supplying a timer
address, leaving a screen coordinate inBC. Such writes land below4000 and were
ignored by Spectrum ROM. Our writable DOCK0 accepted them as code/data writes.

The old long L3trace catches9C3E writingB4 to1415 atrefresh6757, replacing the
high byte of the renderer's LD DE,7800. Later shots change it toFD. At7477 the
HUD copy1419 then writes colour bytes intoFD20 IRQ code; the next interrupt
executes damaged instructions. Other coordinate values can corrupt palette,
terrain and drawing code without immediately freezing the game. The native
rocket path queues a sound at9C96, matching the reported beep timing.

R41 replaces the three-byte ADD/store at9C3C with CALLFCF8. The helper reproduces
the ADD, preserves its exact A/flags, ignores destinations below4000, and retains
RAM stores at4000 or above. It preserves BC/DE/HL/IX/IY. Guard occupies verified
free high-RAM padding after r40's initialization helper, before IRQFD20. Patched
in cold common-code source5C3C/DC F8 and retained across all cached levels.
Read-only physical cartridge ROM already ignores these writes; this corrects
the writable expansion-RAM conversion. No sound effect is removed or muted.

Reproduce python scripts/validate_rocket_fix.py. Tests reproduce the old1415
overwrite, check all16384ROM destinations, valid RAM destinations, native rocket
records and all256accumulator arithmetic flags. watch_rocket_l3.mjs reruns the
formerly failing17000refresh route:60bad stores blocked, renderer DOCK0 unchanged,
1121updates by16500, no invalid jump or IRQ overwrite. Individual captures and
contact sheet under build/diagnostics/rocket_fix_r41 were rendered/inspected.
Full8-level progression, ending/cache revisits, selected3/8 restarts and disk
failure/page checks pass. Hardware confirmation remains pending.

This supersedes the r40 initialization-only explanation for the reported fault.
R40's late diagnostic invalid execution was a useful reproducer of the ROM-write
bug; it must not be dismissed as merely the artificial invulnerability bypass.
The r40 initialization correction remains, but was not sufficient to stop this.
