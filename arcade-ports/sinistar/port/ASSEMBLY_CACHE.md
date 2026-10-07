# V21 retained-cache check

V21 preserves this cache design. On cartridge `524e906a1805b55789a0430daab31c33464e51af55208f1a34c12d8ff3635063`, the controlled changing-phase overlap fixture measures 9.84 fps, nineteen-piece fixed overlap 19.43 fps, and one rock without Sinistar 19.30 fps. Natural gameplay moves through the world faster now; its separate results are in FAST_MODE_PROFILE.md. All mask/reference tests pass. The v20 design and measurements below remain historical documentation.

---

# Precomputed assembly masks â€” v20

Cartridge SHA-256: `50ab05955433c7e3355f7a34069c8b7ca5f00450640b41b06cd4673240a971f5`.

All eight horizontal mask phases now build alongside the assembly bitmap cache. Changing scroll phase no longer shifts 364 mask cells at drawing time. Objects remain visible through unassembled gaps and outside Sinistar's silhouette; fully covered objects still skip drawing without changing game logic. Sinistar's attribute wins in partially shared 8x1 cells.

## Rendering changes

- Shared adjacent-byte mask patterns encode all eight phases. At most 99 patterns occur among the twenty stages; each cache reserves 100.
- A 100-byte selected-phase lookup is retained until stage or phase changes. Compressed sprite staging invalidates it when using the same scratch memory.
- Assembly composition intersects each row with its dirty minimum/maximum columns. Clean cells outside that intersection are skipped, and transparent cells preserve the background.
- Rows without object overlaps retain direct copies. Overlapping rows use masks; fully opaque coverage suppresses object staging/drawing, including covered stars.
- Compiled planetoid programs share repeated instruction tails, freeing 1,167 cartridge bytes at a cost of at most one additional jump per affected row.

The general dirty-region compiler still merges each row into one span. An experimental second-span journal cost more CPU than it saved and was removed. This revision narrows assembly composition, not every dirty span in the engine.

## Performance

Native 3.528 MHz emulation. Controlled fixtures use one rock with worker, combat and speech disabled, measuring 40 pictures after warmup. These are not general game-rate guarantees.

| Controlled fixture | v19 fps | v20 fps |
|---|---:|---:|
| Fixed assembly, player apart | 19.63 | 19.43 |
| Fixed assembly, player overlap | 19.00 | 18.53â€“18.82 |
| Changing scroll phase, player overlap | 8.62 | 9.81 |
| One rock, no Sinistar | 20.09 | 20.09 |

The targeted changing-phase case gains about 14% in frame rate: 409,230 to 359,473 T-states per picture. Fixed scenes are slightly slower. This does not yet meet 10 fps everywhere or the 20 fps goal.

Natural continuous-right flight, 360-refresh warmup and 120 completed pictures:

| Scene | v20 fps |
|---|---:|
| Normal assembly | 6.15 |
| Fast assembly | 8.48 |
| Normal pursuit | 6.17 |
| Fast pursuit | 15.04 |
| Fast pursuit, speech and shooting | 15.46 |

Natural runs sample different world positions as timing changes; use the controlled fixture for the direct optimization comparison. Fast mode still falls below 10 fps during assembly. Older hit-effect/lifecycle profiles are historical, not measurements of this cartridge.

## Memory and scheduling

Each 4 KB HOME cache at 8000 or 9000 contains:

| Offset | Contents |
|---|---|
| 0 | Eight 357-byte bitmap phases (51 rows Ã— 7); universally transparent row zero omitted |
| 2856 | 52 byte-sized overlap flags |
| 2912 | 364 pattern indices (52 Ã— 7) |
| 3276 | 100 eight-byte mask patterns |
| 4095 | Pattern count |

Front-image colors occupy DE00â€“DF6B. BF00â€“BF63 retains the selected mask lookup; BF80â€“BF86 is row scratch. A sixteen-slot pattern-interning accelerator occupies 5C14â€“5C23. No extra cartridge bank is required.

The back set builds over 52 row calls, two per picture, and swaps atomically after 26 picture updates. Construction changes restart the back set while the front remains valid. New pieces therefore appear after preparation finishes. Precomputing all phases increases the worst measured builder call from 9,275 to 52,298 T-states. This remains below one 58,688-T-state refresh but matters while pieces are being added.

## Verification

All twenty stages and 160 phase combinations passed independent bitmap/mask references, 160 patterned-background composition cases, narrow dirty-cell checks, 28 fully covered-object cases, and 21 atomic swaps. Maximum measured banked calls: build 52,298 T-states, prepare 378, draw 30,520, overlap/cull 13,618. Bank/stack restored, no ROM writes.

Scrolling/edge cleanup, covered-star rendering, 18,000-refresh fast-mode stress, and playable win/loss/restart checks passed. Stress recorded no late raster writes. These are emulator checks; physical hardware testing remains outstanding.

See README.md for the original-source audit of worker shooting, bounce, speed, scanner outline, taunts and visible body damage. Those gameplay changes are not implemented by this graphics revision.
