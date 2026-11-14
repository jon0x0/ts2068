# R38 captured-RAM diagnostic

Replace the complete RTYPE folder. Select level3 and play normally.
When the dots appear, release other keys and hold Caps Shift+D briefly.
Photograph the R38 diagnostic screen, then press Space and photograph the
redisplayed game screen. Reset afterward. Both views are frozen, not resumable.
The chord works on levels2-8; it remains disabled on BOOT/cached level1.

Before clearing the display, this version copies the actual HOME bitmap4000..57FF
toA000..B7FF and ECM attributes6000..77FF toC000..D7FF, with the correct bank map.
Space writes both captured planes back in full, selects mode42 (ECM, interrupts
inhibited) and halts. No music or game writes occur during this redraw. If the
RAM redraw is clean when the original view had dots, that points toward capture/
bank visibility rather than dots stored in those captured planes. Identical dots
would direct investigation back to game RAM; neither result alone proves firmware.

R37 PC photo was18DE, not160E/180E. It is OR A in full_enemy_source after loading
DE=C4CE, with sourceHL=C993. User confirms game was not frozen. Controls0200 and
raw sticksFFFF are neutral. ATTR/DRAW in r37 read from overlaid DOCK4, so those
two values were invalid; r38 reads HOME8EB0/8EBE via an IRQ-disabled HOMEF910
mapping helper. Other r37 snapshot fields were not affected by that overlay.

Reproduce python scripts/validate_debug_ram.py. Synthetic register capture and
native renderer-byte checks pass; actual interrupt test captures a stuck loop,
then proves Space restores all6144 bitmap and6144 ECM bytes exactly. All8-level
progression/cache/restart/error tests pass. Diagnostic images live_stall.png and
ram_view.png are under build/diagnostics/debug_ram_r38. Physical retest pending;
this is a diagnostic, not a claimed corruption fix.
