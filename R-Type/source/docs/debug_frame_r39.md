# R39 completed-frame capture

Replace the complete RTYPE folder. On level3, when the lines appear, press
Caps Shift+D and allow the current update to finish. Photograph the diagnostic,
then press Space and photograph the frozen RAM view. Reset afterward.

This differs from r38: the IRQ only latches a request. Capture runs after the
main loop completes drawing, at the native868C frame wait. PC868F on the debug
screen is therefore expected. It avoids confusing a mid-sprite/mid-restoration
snapshot with persistent damage. It cannot capture a genuinely stuck main loop;
r38 remains available for that case. Active on levels2-8, not cached BOOT level1.

R38 hardware photos12829/12830 show artifacts surviving RAM replay. User confirms
second photo is the redraw. PC8D43 is normal sprite byte-copying, INPUT0200 and
JOYSFFFF neutral, ATTR003E/DRAW60C6 valid. This establishes artifacts existed in
the captured planes, but the capture was interrupted in the middle of drawing.
R39 tests whether the same artifacts remain after a complete update. This is
diagnostic only, not a claimed graphics fix or proof of a hardware cause.

Implementation: ROM0 IRQ poll sets HOMEF91C. New HOMEFCC8 frame hook in verified
FF padding preserves the displaced LD A,(7A8A) when no request. Cold source468C
patches the native main loop once; common code persists through cached levels.
The capture builds the same saved-frame layout as the prior IRQ diagnostic, then
reuses exact bitmap+ECM replay. No new scratch area, disk operation or asset map.

Reproduce python scripts/validate_debug_frame.py. Captured registers/PC/SP match
the main-hook entry exactly; Space restores both6144-byte planes byte-for-byte.
All8-level progression, ending/cache revisits, restarts and error controls pass.
Hardware confirmation remains pending.
