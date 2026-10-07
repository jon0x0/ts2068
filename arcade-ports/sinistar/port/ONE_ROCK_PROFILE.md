# Optional fast chase comparison v10

`build/fast-mode-profile.json` measures a naturally scrolling chase, rather than pinning rocks to fixed screen positions. F mode retires rocks after they leave and stops replenishment. The matched fixture improves 6.62 to 12.67 fps; its final ten seconds improve 7.34 to 13.47 fps. Shooting, speech, worker and damage are disabled in both cases. These measurements are not directly interchangeable with the controlled one-rock numbers below.

---

# Current performance revision: retained planetoids v6

Cartridge SHA-256: `cb3662e302606318170827fc35f74664044ddbd32ac29f3d05e2fae1ce19ce19`. Native TS2068 code, 64 KiB cartridge.

| Measured scene | v5 fps | v6 fps |
|---|---:|---:|
| One visible rock, no Sinistar | 19.26 | 19.26 |
| One visible rock and active Sinistar | 11.95 | 12.43 |
| Three visible rocks and active Sinistar | 7.93 | 11.49 |
| Continuous scrolling flight, variable population/clipping | 8.09 | 8.15 |

The controlled chase fixtures keep one/three planetoids at stable screen positions while native pursuit and player physics run. They disable combat, worker activity and speech. The three-rock improvement is 44.8%; it is not a claim that continuous scrolling is 45% faster. The 20 fps target remains unmet. Physics rate, world population, graphics, and camera behavior are unchanged.

Secondary planetoids now retain their nine-byte projection identity, including fine phase and clipping. An unchanged rock skips full restoration and dirty marking. Fully visible retained rocks redraw only rows intersecting existing damage bounds, so actors and stars crossing them are repaired in the original layer order. Movement, clipping changes, disappearance and return invalidate retention. The primary rock also benefits from row-level repair.

Other changes: four-byte packed final updates replace five-byte generated instructions; comparison constructs the list with stack writes, and publication uses an unrolled reader. Only changed final bitmap and ECM attribute bytes reach the screen. Clear kernels have no per-cell loop. Physics directly visits the current interleaved planetoid group instead of checking all 17 slots each tick, preserving the previous schedule.

Two experiments were rejected after profiling: separately tracking an empty central gap, and maintaining left/right dirty spans. Their bookkeeping and extra span dispatch cost more than the comparisons they removed.

In the three-rock chase, remaining CPU time is approximately 43.4% composition, 24.6% comparison, 17.4% physics, 8.5% refresh wait, 2.8% radar preparation, 2.3% publication, and 0.8% interrupts. Continuous camera motion still invalidates most retained graphics. A larger general scrolling improvement needs to reduce moving-object composition and comparison together; optimizing the final screen writer alone cannot close the gap.

Verification: 480 independent composition fixtures plus native scrolling (626 pictures), 23,030 skipped retained-rock rows, 600 rectangle-restoration cases, original velocity and pursuit tests, playable win/loss/restart, complete AY voice streams, and 216 direct-transition cases with overlap fallbacks. All eight final reports must match the cartridge hash. Tests run in TSRun; physical hardware remains unverified.

---

# One-visible-planetoid measurements

Latest incremental-overlap build bf381583: **19.261 / 11.952 / 7.932 fps** (one rock without Sinistar / one rock with Sinistar / three rocks with Sinistar). Current JSON matches this build; the v4 baseline remains in its saved revision. Earlier results below are historical.



Current compiled-planetoid revision (93b7974f): **19.261 / 11.371 / 7.704 fps** for one rock without Sinistar, one rock with Sinistar, and three rocks with Sinistar. Current JSON matches this build; the composition/endings baseline is preserved in `revisions/playable-compose-endings-v3/build/one-planetoid-profile-current.json`. The earlier results below are historical.



Current composition/endings revision (72c76a4e): one visible rock without Sinistar 14.446 fps; one rock with active Sinistar 9.357 fps; three rocks with active Sinistar 6.147 fps. Corresponding culling-v2 baseline: 14.163, 8.848, and 5.779 fps. Conditions below are unchanged. Current data is in `one-planetoid-profile-current.json`; the preserved baseline is `one-planetoid-profile-culling-v2.json`. Radar now prepares once per 24 ticks. These gains also include cheaper composition and indexed physics, so they do not isolate radar savings.



The historical v1/v2 comparison below remains for reference.



Native TSRun CPU timing at 3,528,000 T-states/second. See

`scripts/profile_one_planetoid.mjs` and `build/one-planetoid-profile-{current,v1}.json`.



Each controlled scene uses continuous right input and retains all 18 simulated

planetoids. Before each render, the fixture positions exactly one or three

rocks in view and the others offscreen. Sinistar uses native pursuit when

enabled. Worker, firing, speech and damage are suppressed. After 360 refreshes

of warm-up, 120 complete pictures are measured. These are controlled CPU

benchmarks, not a claim about every gameplay scene or physical hardware.



| Scene | Scrolling v1 (5cc08425) | Culling v2 (6de89b38) |

|---|---:|---:|

| One visible rock, no Sinistar | 13.38 fps | 14.16 fps |

| One visible rock, active Sinistar | 7.90 fps | 8.85 fps |

| Three visible rocks, active Sinistar | 5.17 fps | 5.78 fps |



For v2's one-rock active pursuit, exclusive time accounting is:



| Work | CPU time |

|---|---:|

| Compose/clear/stage graphics in shadow RAM | 43.9% |

| Physics, including all 18 world objects | 22.0% |

| Compare dirty areas and compile changed-byte writes | 21.5% |

| Prepare radar | 3.6% |

| Wait for display refresh | 6.8% |

| Publish screen changes | 1.4% |

| Interrupts | 0.8% |

| Other | 0.2% |



Sprite clipping/compaction alone uses about 0.1% in this particular trace.

Population projection/culling uses about 5.3%, included in composition above.

The Sinistar direct transition path was selected for **zero** of the 120

active-pursuit pictures. The pursuit fixture allows him to catch up and overlap

the player; this is not a deliberately separated fast-path benchmark.



The moving player measures 0.9844 world pixels per physics tick. Sinistar

averages 0.9961 and peaks at 1.3446 in the one-rock measured chase, after warm-up.

At the emulator's approximately 60.114 physics ticks per second, those are

about 59.2 pixels/second for the player and an 80.8 pixels/second Sinistar peak.

These are world speeds, not camera-relative screen speeds or global maxima.



The playable player adapter in `mining-scene.asm` directly doubles each signed

SINCOS component. It does not yet use the original acceleration path. The

original `SAM/EXECJNK.SRC` scales its long component fourfold and its short

component eightfold before acceleration, in the arcade coordinate system.

Sinistar retains the translated speed table and chase adjustment. Thus the

current player/Sinistar balance must not be described as arcade-accurate;

the coordinate scaling and full player movement need reconciliation together.

