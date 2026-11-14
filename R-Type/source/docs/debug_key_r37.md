# R37 hardware diagnostic

Replace the complete RTYPE folder with the r37 ZIP contents and load RTFULL.TAP.
Select level3 at the title, release the number, then start normally.

When corruption or stuck movement appears, hold Caps Shift+D briefly.
Photograph the complete R37 DEBUG screen. The game and music stop intentionally;
reset afterward. This is a diagnostic takeover, not a pause/resume feature.
It is active on levels2-8. Level1 uses the preserved cold bootstrap and ignores
the chord. It requires interrupts to continue; the reported continuing music
suggests that condition holds. If nothing appears, report that too.

The IRQ captures the main program's interrupted PC and pre-interrupt SP, AF/BC/DE/
HL/IX/IY, original F4 mapping, native input/keyboard decoder, world/object state,
render attributes/mode, cached-bank state, music pointers, raw joystick contacts,
timer and four main-stack words. All values are hexadecimal. Word fields pack
the lower-address byte at the right: LEVEL lowbyte is ASCII31..38; INPUT lowbyte
is native button bits, highbyte keyboard mode; CACHE lowbyte holder/highbyte
current; VALID lowbyte only; JOYS lowbyte stick1/highbyte stick2, FF means neutral.
GAME packs7AA3/7AA4; ATTR8EB0/8EB1; DRAW8EBE/8EBF. These are raw diagnostic words,
so unused adjacent bytes can be arbitrary. Photograph everything without decoding.

Implementation: IRQ entryFD20 calls ROM0 poll0DE0 with original AF/BC/DE stacked.
The chord selects current DOCK4 (F4=19) and jumps to8000. Diagnostics occupy
8000..8457, below music allocations84B4; no disk command or region switch occurs.
BOOT marker0D7F=0 prevents executing a diagnostic over the initial bootstrap;
regular level assets set it1. Capture copies the interrupted frame and samples
native DOCK3 variables before switching to standard HOME display. The snapshot
uses HOME7C00..7C61. IRQ stays disabled after capture; reset is required.

R37 also preserves the original BOOT ROM7 palette and title atlas. R36 incorrectly
treated source assetsE000..FB00 as a disposable display source. R37 restores them
exactly from the pre-r36 image; this does not establish a level3 crash fix.

Reproduce: python scripts/validate_debug_key.py.
verify_debug_key.mjs checks exact synthetic PC/SP/registers, chord and negative
keys. verify_debug_live.mjs proves real frame interrupts capture a deliberately
stuck main loop at8400 with pre-interrupt SPFFF0. Full8-level progression, cached
revisits, selected3/8 restarts, display guards and disk error controls pass.
Diagnostics build/diagnostics/debug_key_r37/captured.png and live_stall.png.
Hardware testing remains pending; the original corruption remains unresolved.
