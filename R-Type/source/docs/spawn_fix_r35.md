# r35 mirrored sprite correction

Replace the complete RTYPE folder with the contents of
build/fullgame/spawn_fix_r35/RType_TS2068_spawn_fix_r35.zip and load RTFULL.TAP.
All eight loaded levels remain cached as in r34. No firmware change is required.

The L2 spawn uses horizontal-mirror drawing. Its HOME5D00 bit-reversal table
contained high-score text, producing exactly the photographed scrambled block.
Gameplay initialization now regenerates the table on every entry. All levels
share this correction. The earlier isolated drawing tests supplied a valid table
themselves and missed the initialization failure.

Reproduce: python scripts/validate_spawn_fix.py.
Normal gameplay and restart tests check the real table on every active update.
All8-level progression, cached revisits, selected3/8 restarts and failure controls
pass. See TEST_HISTORY077 and diagnostics/l2_spawn_r35/table_comparison.png.
Physical confirmation is pending. The separate level3 freeze is still open.
Standalone previews and the64KB cartridge are unchanged.
