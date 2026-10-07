# Arcade taunts — v25

The cartridge now plays the complete eight archived recordings through speech2ay: “Beware! I live!”, “I am Sinistar!”, roar, “I hunger!”, “Beware, coward!”, “Run, coward!”, “Run! Run! Run!”, and “I hunger, coward!”. No words are spliced. Recordings come from Sean Riddle's Williams archive, https://seanriddle.com/willy2.html. The three newly added WAV files and regeneration script are retained in the project.

## Source behavior

The implementation translates FALS/N1ALL.SRC SinCon/TAUNT and SAM/FUNCTION.SRC RAND8 from the pinned original-source checkout. Every 64 physics ticks, a random byte at or below hexadecimal 38 permits a taunt attempt. Selection adds a second random value masked with 7F to the wrapping RnSpch accumulator. Inclusive thresholds 28, 50, 78, A0 and C8 select hunger, beware-coward, run-coward, triple-run and hunger-coward; the remainder selects the roar. Across all accumulator values the bins contain 41, 40, 40, 40, 40 and 55 values. This is not a guarantee of equal independent probabilities over time.

Ordinary taunts do not interrupt current speech. The roar may interrupt it, matching the executable Speak8 path in WITT/ANISINI.SRC. Pending speech and active speech retain priority over player shooting. Assembly, player death and Sinibomb hit requests remain connected to their existing gameplay events. Mouth poses and durations use the original AniSC tables, clocked with audio; there is no separate invented single “Run!” event.

The sector-entry hook calls the same taunt selector and suppresses ordinary out-of-sector speech. **The current wrapped 512×512 world is one scanner sector:** full arcade supersector transitions remain unported, so this hook does not yet produce natural sector-entry events. The RNG arithmetic matches the source, but its sequence differs because other port systems do not consume the same shared random streams. Respawn protection suppresses taunts as an adaptation of the original player-death gate. This is not a claim that all game logic or sound-board synthesis is arcade-identical.

## Storage and rendering

All 951 AY frames are preserved exactly using 11 bytes per pair, with six bytes for an odd final frame. The 5,233-byte speech payload is banked without hiding the ISR stack or resident code. Graphics transition streams and assembly deltas are also losslessly packed to keep the cartridge within eight 8 KB banks.

Speaking after awakening now uses the correct shifted mouth pose. Only rows 33–45 require runtime mouth shifting; the remaining body bitmap uses precomputed graphics. Palette handling and overlap composition remain unchanged. The continuous-speech/shooting fast-mode stress fixture improves from 9.08 to 9.79 displayed fps after this optimization. It remains below 10 fps and the 20 fps target; audio and physics timing are independent of displayed picture rate. The before/after figures refer to the two taunt candidates, not a comparison against v24's silent-mouth rendering.

## Verification

Current cartridge SHA-256: `4a765967525c1a4fb27c3d08b17e60ee48b5f824c1ad2f2ac105e61567552ca8`.

- Native decoder checks: all eight clips / 951 frames, exact AY register values, all selection bins, priority and sector gates, Task64 threshold, and 1,000 RNG steps.
- Lossless graphics checks: 216 transition cases and all 20 assembly stages; maximum transition expansion 11,217 T-states.
- Interrupt playback: all voices, native death/hit triggers, 12,675 AY writes; maximum measured speech decoder tick 2,350 T-states.
- Scrolling/reference comparison: 1,294 pictures including 1,150 clipping cases and 72 post-awakening mouth/phase/edge combinations, without ROM writes or late raster publication.
- Native lifecycle: earned ammunition, assembly, victory, restart, contact damage, respawn protection and loss. Worker combat, bounce toggle, scanner outline and speech priority checks also pass.

See the hash-matched JSON reports in build/. Hardware playback remains untested.


## v28: uninterrupted roar and simultaneous bomb impacts

Bomb hits still preempt ordinary speech with the roar. A hit or random roar request during an existing roar is consumed without resetting its pointer, mouth cursor, or remaining duration. The full 170-refresh recording (~2.83 seconds) finishes. A later hit can start a new roar. This intentionally adapts the source interruption rule at the user's request.

The previous harmonic conversion became excessively tonal. The complete archived recording was refitted with speech2ay's stateful Ayumi simulator at the native AY clock. The fitter can allocate channels A/B to pitched content and C to noise, including a fitted noise period; 140 of 170 frames select this combination. No recording was truncated. The other seven voice streams are unchanged. A lower numerical fit error is not a listening verdict; use the before/after comparison to judge the approximation.

Each bomb hit also adds a 12-refresh (~0.20 second) descending noise burst on channel C. A/B continue the current roar without interruption. This is a compact synthesized impact adaptation, not a second complete sample mixed with the roar. Since the AY has only one noise generator, the impact temporarily replaces the roar's C component. Shooting and worker effects still cannot interrupt speech. Repeated hits retrigger the short impact, never the roar.

The new noise routing uses the spare high bit in the existing paired-frame format; the unused C tone byte carries its noise period. Speech still occupies 5,233 cartridge bytes, and the complete cartridge remains 64K. A 78-byte HOME helper is copied safely through BC00 during boot, after unmapping its source bank. It occupies 7F60–7FAD; 7F53 holds the impact countdown. The verified regular stack low-water mark is 7FDB. Helper code remains below the reserved stack boundary 7FD0.

Validation: all 951 frames of all eight clips decode to exact expected registers. Duplicate requests at frames 12 and 169 leave the roar advancing normally; the final register frame gets its full refresh interval. Native collision tests play the entire roar across two hits, then start a new full roar on a later hit. Hybrid AY register writes are captured for the listening sample. The longest measured hybrid audio tick is 2,670 T-states (0.757 ms); solo max is 2,597 T-states. Full ISR and graphics costs are additional. Fast-mode play reaches victory, restart, and loss; 18,000-refresh graphics stress completes without ROM writes or late raster publications.

The revision's `audio/index.html` offers the original recording, previous AY conversion, new solo roar, and native two-impact hybrid. The rendered hybrid uses actual cartridge AY register writes and the same output model/gain as the new solo sample.
