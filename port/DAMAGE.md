# Sinistar piece removal — v27

Each successful Sinibomb hit now visibly removes the next outer piece. The twelve outer pieces disappear in the original reverse construction order; the remaining animated face disappears on hit thirteen. The existing impact explosion, roar, velocity reduction, stun and victory logic remain connected to the same hit event.

The order comes directly from SAM/SAMTABLE.SRC: construction finishes all twenty entries, then ADDPIEC resets the piece pointer to ALIVE, immediately after the twelve outer entries. SUBPIEC decrements that pointer one entry per hit. WITT/SUBPART.SRC handles the final face kill when the pointer reaches PIECETB.

Removal order: S5R, S6R, S6L, S5L, S4L, S4R, S3R, S2R, S3L, S2L, S1R, S1L, then the face. A compact 48-byte table is generated from the original image dimensions and piece offsets, with the vertical coordinate conversion used by this port. It does not store thirteen duplicate full sprites.

![Native staged damage](build/damage-preview.png)

[Animated removal sequence](build/damage-preview.gif). These are emulator display captures from a controlled fixture, held longer for inspection; the preview is not a performance recording.

## Rendering and performance

Removed-piece spans are cleared in the HOME bitmap/attribute shadow before other actors are composed. Edge-byte masks preserve neighboring pixels; clipped coordinates are checked before any writes. Changed final screen bytes retain the existing publication path. Stars may appear in exposed areas, and moving objects remain visible there.

The intact sprite retains its existing direct-update path. Damaged sprites use full composition: the intact transition tables and eye-only repair are unsuitable once parts are absent. This costs additional drawing time. The damage pass clips each piece once and walks vertical byte columns using Spectrum scanline stepping. Across the 560-case direct native test, its largest measured cost is 62,066 T-states (17.59 ms), compared with 144,495 T-states (40.96 ms) for the first implementation. This is the removal pass only, not total picture time or a universal worst-case budget.

Unused halo-render code and tables were reclaimed for this routine; speech and original explosion artwork remain present within the 64 KB cartridge. Scratch is HOME 7F45–7F48 and 7F50–7F52, separate from transition decoding at 7F00–7F34, the secondary previous rectangle at 7F40–7F43, and explosion staging scratch at 7F44.

## Verification and scope

- 560 direct Z80 cases check every hit count, all eight horizontal phases, clipping and exact bitmap removal against an independent pixel model, with zero ROM or direct display writes.
- Full scrolling/reference tests compare 1,911 pictures, including 1,772 controlled cases covering damage stages, mouth poses, overlaps, screen boundaries, disappearance and restoration. Zero late raster publications or ROM writes.
- An additional 18,000-refresh stress run completes 3,741 pictures without stale-pixel or raster failures.
- Native held-B tests, earned-ammunition victory, restart, player loss, worker explosions, bounce controls and all eight speech clips pass on this cartridge.

This implements visible removal for the awakened Sinistar. Detached pieces flying away, bomb attacks during construction, and collision contours that shrink to the remaining artwork are still unported. The source has those additional object/collision behaviors; this revision does not claim them. Multiple simultaneous Sinibombs also remain pending.

SHA-256: `6b467879bb67f431ceaf9b84ecf65b0dc8214a421db0cc9e9a531d09b97fd645`. Reports in build/ identify the same tested cartridge. Physical hardware remains untested.
