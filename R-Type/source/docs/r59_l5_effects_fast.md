# r59: L5 effect repair and prepared cells

## Result

r58 overwrote global sprite colour IDs while expanding its boss phases in DOCK1 2400..3FDF. Global bitmap data remained intact, but the native publisher at 1561 still read those colour IDs. This explains apparent garbage pixels as well as incorrect colours on sparks and explosions. r59 preserves all 617 nonempty global source tags in a collision-checked 715-byte sparse table at DOCK7 E000..E2CA and redirects only the L5 global lookup through ROM0 0040. Global native glyphs remain byte-identical to r57.

Actual native-renderer comparison: 2568 cases, 840 r58 mismatches, zero r59 mismatches against r57. The matrix covers all nonempty global glyphs in four orientations, with expanded explosion/spark cases for flash, foreground and edge placement. Native player-death effects were identified from the real death path, not guessed from glyph numbers. That route draws IDs 75,82..87,94,95,97,98 and reaches respawn. Effect type 28h is a sequence-table offset, not a global glyph ID; glyphs 40..43 are title letters.

## Drawing work

Once per boss part, prepare a variable-length native cell plan: tag54 for an empty/hidden cell, otherwise a pointer to raw phase pixels plus an eight-row validity mask. Painting avoids coordinate division and repeated source scans. Reject clipped cells and verified fully opaque foreground before source preparation. Ownership metadata 0/3 does not prove foreground: stale retained bytes must not hide fresh boss pixels. Per-raster foreground composition remains intact. Original 24px spheres, 80px machinery core, 25 parts and r58 two-pixel stepping are retained.

Plans reuse the already-copied HOME native source span EFA1..F480. Before cached level departure, restore the borrowed packed cache/source shadow/native transition tail and normalize mutable plan bytes back to their cold source representation. Bank6 DF00..DF7F holds transition tail, DF80/DF90 hold phase dictionaries and DFB0..DFBF holds packed tail. Actor state uses E300..E33F and cache flag E3F0; global IDs and phase workspace are disjoint. Preparation runs on private DOCK2 stack with the raw IRQ vector installed in HOME and DOCK2; I8F is set only with bank4 visible. The ROM0 lower-screen metadata read temporarily unmasks bank4 under DI. Native high HOME stack reads occur with bank7 removed.

## Measured scope

| Matched emulator workload | r58 | r59 |
|---|---:|---:|
| Player updates in 480 held-input display refreshes | 141 | 173 |
| Projectile updates in same interval | 138 | 172 |
| Short shots / charged beams | 8 / 1 | 8 / 1 |
| Component mean cycles, including new preparation | 204098 | 167702 |
| Elapsed display refreshes for 700 boss world updates | 36061 | 35862 |

Player opportunities rise 22.7%, projectile opportunities 24.6%; matched isolated native component work falls 17.8%. Overall 700-update route improves only 0.55%. r57 takes 26295 refreshes on that route, so this phase trial is still slower overall than r57. It does not introduce a separate boss timer. Do not convert these figures into a hardware FPS claim. Opportunities and short-tap capture depend on workload; the rapid-fire stress route captures 14 of 15 requested taps, with no late queued shots. Stationary single-shot order is forward, with 173 projectile phases and one shot.

## Validation and diagnostics

The frozen suite checks effects, 256 phase/orientation cases plus 96 foreground cases, 16 real IM2 injections, 700 actual L5 world updates and 25 actor histories, held-input profiling, custom keys and native joysticks, charged fire, real death/respawn, title, L1 snake, loader failures, rapid fire, single-shot order, actual boss/game-over/cached restart and all-eight-level loading/ending/cached progression. Extra independent raw-raster clipping checks exercise right/bottom, left/top wrap and lower metadata boundaries. All nine region hashes stay frozen throughout testing. Other levels including boot are byte-identical to r58, so their previous boss-render coverage remains applicable rather than being represented as a new hardware run.

Diagnostics: build/diagnostics/l5_effects_fast_r59/index.html and effects_comparison.png. These show isolated native retained bitmap/ECM captures, not asset-only conversions, full gameplay captures or hardware photos. The PNG was visually inspected: repaired sparks and red/yellow explosion frames match the reference, while the r58 column has displaced multicolour artifacts. Raw capture files effect_ID_0/1/2.bin are r57/r58/r59 respectively.

Implementation history: an initial candidate enabled preparation IRQs with I84 while bank4 hid the vector; rejected and corrected to I8F with vectors installed before EI. Test IRQ mode was verified IM2. An initial focus-label list mistakenly identified title glyphs as explosions; corrected from native sequence table 75DD and actual death tracing before final evidence. The broad all-global comparison already covered both. Early planning without foreground rejection gave slightly faster total route but fewer held-input updates; current measured candidate prioritizes interruptible input opportunities. No reference project, original source ZIP, stock cartridge or skill was modified.

## Try it

Use build/fullgame/l5_effects_fast_r59/RType_TS2068_r59.zip. Copy the complete RTYPE directory, reset, load RTFULL.TAP; keep separate from r57/r58. Select 5 before starting, then B-release-B in game for the L5 boss. Define controls normally. Hardware confirmation of the reported corruption and responsiveness remains pending.
