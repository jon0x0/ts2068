# R-Type r49 implementation and validation

The full disk game now has one-pixel player movement, IRQ-sampled chosen keys and both native joystick sockets. It retains the original key-definition screen. QAOP is fixed only in the separate movement trials. Quick normal-fire releases are queued between world updates; held fire still charges the native beam. Original projectile capacity and rounded weapon/AI coordinates remain. The full game uses the centre ship pose and does not guarantee a fixed frame rate.

Level5 uses approved deep-shadow Bellmite spheres with the planned dark-blue top/right edge, and the selected96x96 machinery core. Cached source row pairs avoid repeated reversal/decoding. Overlap rows preserve foreground colours and visible coverage while recovering background shading when a legal ECM pair permits it. This reduces broad edge-colour bands, but cannot remove all shared8x1 colour limits.

R49 also fixes an ownership bank-visibility error discovered during validation: metadata rows16-19 live in HOME8000-807F, whereas the shader maps DOCK4 at8000. Reading/writing those cells inside the shader addressed code instead of metadata. The low gateway now captures ownership and commits new metadata before switching banks. The384-case compositor check validates all640 ownership cells, foreground RGB, union coverage, flips/clips/flash states, source caches and the DOCK4 debug-code prefix. R48 is superseded.

The relocatable-delta TAP and preceding baseline are included as separate stock-machine demonstrations. Their black-background cached transitions are not substituted blindly for the game's background-aware compositor. Future skill work should document relocatable coordinates, phase/direction caches, collision coverage, shared-cell colour ownership and bank visibility; no reference skill or project was edited here.

The stock64KB read-only cartridge remains unchanged. This release is the512KB disk game, with per-level loading and resident level reuse. Hardware validation remains pending. Original archive ZIPs and reference projects are unchanged. See validation_summary.json and TEST_HISTORY.md for measured tests and provenance.
