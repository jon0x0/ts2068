# r36 transition display correction

Replace the complete RTYPE folder with the r36 ZIP contents, then load RTFULL.TAP.
The loader helper now runs at HOME7B00 rather than inside the secondary screen's
attribute area at7800. Hidden secondary attributes stay black while scratch code
and metadata are moved. Loading and title screens are prepared before display.
Cold bootstrap copies a black bitmap and attributes. Retains the r35 mirrored
creature correction and all eight resident level banks.

Reproduce: python scripts/validate_transition_fix.py.
Negative control reproduces the previous visible scratch write. Full progression,
ending, cached revisits, restarts, blank-screen guards and error controls pass.
See TEST_HISTORY079 for diagnostic images and intermediate test failures.
Physical confirmation remains pending. Separate stuck-down/level3freeze reports
remain open. Standalone previews and64KB ROM are unchanged.
