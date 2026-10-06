# Latest graphics revision: precomputed assembly masks (v20)

See [ASSEMBLY_CACHE.md](ASSEMBLY_CACHE.md) for current measurements and verification. Changing-phase assembly overlap improves from 8.62 to 9.81 fps. Natural fast assembly averages 8.48 fps; fast pursuit 15.04 fps, or 15.46 with speech/shooting. Some fast-mode assembly remains below 10 fps. The older results below describe their named revisions, not v20.

---

> v19: Shape-aware assembly compositing and fully hidden object culling replace the black rectangle. Stationary one-rock overlap measures 19.00 fps; constant phase-changing overlap measures 8.62 fps. See [ASSEMBLY_CACHE.md](ASSEMBLY_CACHE.md) for the current results and limitations. Earlier entries below are historical.

> v18: Assembly uses double-buffered shifted graphics. Controlled player-overlap: 6.01 -> 19.75 fps at fixed phase 7; changing phase every picture: 7.33 -> 12.40 fps. See [ASSEMBLY_CACHE.md](ASSEMBLY_CACHE.md) for current measurements, preparation latency, memory and verification. Earlier results below are historical.

> v17 changes only clipped-rectangle cleanup. The measurements below are the saved v16 performance baseline, not a new v17 benchmark. See SCROLLING.md for the reproduced failure and regression results.

# Empty populations, eye updates and star occlusion — v16

Cartridge SHA-256: `ce687c43ea195017ac1b1321d96d2b2878a2548320fdd8a050e76ffdeffe064e`.

## Implemented

- Dead secondary planetoids bypass projection. Hidden projections store only a zero width. A current/previous visibility aggregate skips empty clear/draw/overlap loops, while retaining the last disappearance erase.
- Once every secondary planetoid is retired during fast pursuit, projection and population physics return immediately. Offscreen live rocks still count. Turning fast mode off restores the normal population; pre-awakening replenishment is preserved.
- Eye changes can use the direct renderer: body rows retain their precomputed kernels, while the small eyebrow band compares live cells and writes only changes. A conservative extra 16,384-T-state publication allowance gates this path. Of 432 eye/movement fixture cases, 48 use this path (stationary eye transitions); other cases retain the verified fallback. Moving-eye updates still need a tighter measured budget or precomputed eye deltas.
- Background stars inside awakened Sinistar's ECM rectangle are skipped using coordinates, before pixel composition. Fast-path overlap checks accept stars covered by both old and new rectangles. Stars crossing an edge use normal composition and reappear cleanly. This is rectangular occlusion, including black gaps in the artwork, not a silhouette mask.
- Optional player coverage uses a stricter full-rectangle containment test. Fully covered player sprites are omitted; partial overlaps use the normal renderer. This is disabled in the saved game. Player coordinates, movement and collisions are unchanged.

## Whole-game measurements

Native Z80 execution at 3,528,000 T/s. Continuous right input, 360-refresh warmup, then 120 completed pictures. No world-rock repositioning. Chase uses an invulnerable pilot and disables workers; the busy case holds fire and repeats speech. These are whole-game workloads, not renderer-only timings. Different frame durations change world sampling, so these are not identical snapshots.

| Scenario | v15 fps | v16 fps |
|---|---:|---:|
| normal assembly | 5.78 | 5.78 |
| fast assembly | 8.67 | 8.43 |
| normal chase | 6.17 | 6.17 |
| fast chase | 12.46 | 15.38 |
| fast chase with speech and shooting | 12.30 | 15.46 |

The assembly scenarios do not gain consistently: normal assembly is essentially unchanged and fast assembly is slightly slower in this workload. The main improvement is retired-population pursuit. No physics rates or screen refresh rates were increased.

## Layering comparison on the same v16 cartridge

| Rendering policy | fps | Direct pictures |
|---|---:|---:|
| fast chase original layering | 15.12 | 0/120 |
| fast chase covered player only | 16.00 | 18/120 |
| fast chase stars hidden | 15.38 | 0/120 |
| fast chase stars and covered player | 16.48 | 94/120 |

Skipping covered stars adds about 1.7% with the player kept visible, or 3.0% with the fully covered player also omitted. Both changes together add about 9.0% over the optimized original-layering case. The default is stars hidden and player visible.

Player-only coverage leaves 93 star-overlap rejections. Covering both reduces that to one and permits 94 direct pictures. This does not translate into an equally large fps gain: the general direct path still constructs per-row publication records on the Z80. Its selection/preparation costs about 42,374 T per picture averaged over the combined experiment; dirty comparison still costs about 43,708 T. Preparing fewer records or using ROM templates is the next useful target.

The comparison classifier in `fastPathGateCounts` records candidate states, including eye changes; an eye-change entry is no longer itself a rejection. `overlapRejections` records actual failed overlap checks.

## Default fast-chase breakdown

| Work | Exclusive share |
|---|---:|
| physics | 10.7% |
| composition | 38.0% |
| dirty comparison | 31.9% |
| radar preparation | 1.8% |
| screen publication | 2.8% |
| refresh wait | 13.6% |
| interrupts | 0.8% |
| other | 0.2% |

Default pursuit averages 229,337 T per picture. Twenty fps requires 176,400 T, a further 23.1% reduction. Even the optional combined result, 16.48 fps, remains below that goal. Speech still prevents the direct path because its temporary stack and speech bank mapping conflict; the empty-population savings nevertheless apply while speech plays.

## Validation and reproduction

Native world/reference compositor tests include scrolling, clipping, radar, disappearing and returning sprites, and covered-star/player pursuit (67 direct pictures plus 480 clipping fixtures). Eye tests cover all 432 eye/movement combinations. Separate 216-case movement and 216-case player-coverage runs include entry, partial overlap, and exit. These validate final bitmap/attributes, changed-only publication, ROM safety and raster timing. Full mining, replenishment, assembly, victory, restart, loss, speech and halo tests remain included.

Use `node scripts/profile_fast_detailed.mjs` for the default game; `--stars` compares all four layering policies. HOME 5BCB bit 0 enables the covered-player experiment and bit 1 enables star occlusion. The game boots with bit 1 only; these are diagnostic bits, not new keyboard settings. `node scripts/verify_scrolling.mjs --fast --cover` verifies the combined policy. `node scripts/verify_mining_scene.mjs 22000 --transitions --eyes` verifies eye updates.

Raw results: `build/fast-detailed-profile.json`, `build/fast-stars-profile.json`. Earlier revisions are unchanged. Impact-flash pauses are excluded from these ordinary pursuit timings.
