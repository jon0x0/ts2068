# r58: L5 two-pixel movement trial

This is a separate playable experiment for the expanded-memory disk build. Standard r57 and the stock 64 KB cartridge remain unchanged.

[Download the trial](../build/fullgame/l5_preshift_r58/RType_TS2068_r58_L5_preshift_trial.zip). SHA256: `bebe1f0acb9e0fb89ff769aa7f8f91e82271baa6ab9ca0019330d9ec4e94b387`.

Copy the entire RTYPE folder, reset, and load RTFULL.TAP. Select level 5 before starting. In gameplay, press B, release it, then press B again for the boss preview. The game still asks for control keys; keyboard and both native joystick sockets work together.

## What changes

All 25 Bellmite parts have actor-local pixel coordinates. Ordinary native 8-pixel target changes are approached in 2-pixel increments per axis on each existing boss update. Larger scripted relocations still snap, avoiding indefinite lag behind the original formation. Animation IDs and attack scripts remain. Spheres stay 24 pixels across and the core stays 80 pixels; padding cells do not enlarge the visible artwork.

Four compiled horizontal phases (0, 2, 4 and 6 pixels) use legal 8x1 colour pairs and preserve nonblack coverage. Vertical movement selects different source raster rows. Both flips are supported. The phase cache uses normal-brightness colours, avoiding bright black. Native enemy AI/collision retains its coarse conventions; this is not a complete pixel-collision rewrite.

The cache is prepared during level initialization, before play. No new arcade cels, music or sound effects are claimed. The player and projectile engines are unchanged.

## Measured tradeoff

The same double-B/700-world-update route takes 26,295 emulated display refreshes in r57 and 36,061 in r58: **37.14% more elapsed time**, including boot and entrance. This is not a faster boss clock. Keep the trial separate for comparison.

In the final 480-refresh held-input probe, r58 produces 141 player ticks, 138 projectile phases, 6 world updates, 8 short shots and one charged beam. r57's corresponding counts were 149, 150 and 9. The separate stationary single-shot probe reaches 8 world updates. Counts depend on the scene and workload. The rapid 15-tap probe catches 14 shots with no late catch-up, versus 15 in r57; do not claim universal tap capture or hardware FPS.

## Memory ownership

The cold cache contains 7,152 packed bytes. Most live in DOCK1:2400..3FDF; the final 16 bytes live at DOCK7:E1E0..E1EF. Small palette dictionaries occupy E1B0/E1C0. The existing 3FE0 scrolling stack slot is preserved.

After native assets have been installed in HOME:

1. Save the 128-byte DOCK6 transition tail (DBD0..DC4F) at DOCK7:E000.
2. Copy the packed cache to DOCK6:C000..DBEF.
3. Expand 7,040 core bytes into DOCK1:2400..3F7F.
4. Expand 2,304 sphere bytes into DOCK6:C000..C8FF. This overwrites only the first 2,304 packed bitmap bytes. The rest of the packed input is retained.

Runtime phase data total 9,344 bytes, within the existing 512 KB allocation. Isolated preparation costs 2,374,061 Z80 cycles, excluding I/O, and happens during loading.

Before changing cached level banks, recover that overwritten packed prefix from every other byte of the raw core. Restore the packed palette bank and its tail, then restore the borrowed native asset shadow from HOME and its saved transition tail. Set the phase flag cold. Unit comparisons verify these ranges byte for byte; actual boss/game-over/cached-boss restart and the complete eight-level cached revisit also pass.

Motion, warmup and restore code starts at DOCK6:DC50, past both the native source-copy limit D87C and the saved tail ending DC50. The cache helper replaces the retired unshifted cache at DOCK4:8C00..8EFF. Per-actor positions occupy DOCK7:E200..E3FF. HOME5BE0..5BE4 is short-lived main-loop gateway state. The renderer uses the existing DOCK2 private shader stack, separate from the HOME player IRQ stack. Source restoration returns with interrupts disabled. The warmup initializer regenerates the reversal table; its callers do not consume its scratch registers.

## Verification

- 256 native phase/orientation cases match independent raster decoding, with exact silhouette and normal-black checks. Another 256 cases include eight IM2 interrupt injections through mappings 5F and 1F.
- Cache expansion and packed/native-shadow/transition-tail restoration compare exactly.
- 700 actual L5 boss updates cover 25 actors and 16,075 motion samples, with 2-pixel assertions for ordinary target changes.
- Other bosses run for 200 updates on levels 1/2/3/4/6 and 700 on levels 7/8 to reach their later appearances.
- Chosen keys, both joysticks, functional firing, single-shot ordering, real death/respawn, all 116 title states, the snake route and four loader errors pass.
- Actual boss/game-over/cached-boss restart: 15,890 refreshes, with only RTBOOT and LEVEL05 mounted.
- Eight disk loads, ending and cache-only revisits: 59,431 refreshes, 128 blocks, 37,221 code/reversal audits and 15 core/workspace checks.
- All nine frozen region hashes, changed-byte ownership, 72 TAP page flags/XOR/reconstruction and archive integrity pass. Fifteen binary/cache files reproduce byte for byte. Shared bank7 player/projectile/audio/IRQ code after E400 is unchanged from r57.

Boss/cache probes use invulnerability and forced victories for coverage, not proof of unassisted completion. PicoVideo and real-hardware confirmation remain pending.

## Native comparison and development notes

The [native comparison](../build/diagnostics/l5_preshift_r58/index.html) contains two short GIFs with their measured emulated update spacing, plus comparison.png and the original HOME captures. There are 16 states per build. The loop jump is the excerpt restarting. The comparison PNG was visually inspected. These are emulator captures, not hardware photos or a video-codec performance result.

Rejected development paths and corrected tests are recorded in TEST_HISTORY entry 121. These include an initial physical-bank ownership error, slow in-frame unpacking, an empty-cell return that left I8F active, a neutral-coordinate branch returning zero, a diagnostic confusing banked 8CFD with HOME 8CFD, and an interrupt-enabled restoration path that disturbed the loader. The final IM2 fixture and later-boss coverage were corrected before release. Baseline diagnostics touched during investigation were restored with the full r57 eight-boss probe; its release archive remains unchanged.

The next performance opportunity is compiling phase-specific cell plans and avoiding repeated per-cell source-coordinate and empty checks. Cached pixels alone do not remove clipping, ECM composition, ownership or publication costs. This build is for evaluating finer movement, not a claimed speed improvement.
