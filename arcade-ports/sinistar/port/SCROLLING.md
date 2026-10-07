# Latest playable checkpoint: worker combat (v21)

Shootable workers, carried-crystal release, worker replacement, fragment explosions, speech2ay QBANG-style effects, gradual faster acceleration, planetoid bounce, and a complete camera-relative scanner outline are now included. Saved viewer: `/port/revisions/playable-worker-combat-v21/mining-web/`. See README.md for details and limitations, FAST_MODE_PROFILE.md for current timings. V20 remains saved and tagged separately.

---

# Latest graphics revision: precomputed assembly masks (v20)

See [ASSEMBLY_CACHE.md](ASSEMBLY_CACHE.md) for current measurements and verification. Changing-phase assembly overlap improves from 8.62 to 9.81 fps. Natural fast assembly averages 8.48 fps; fast pursuit 15.04 fps, or 15.46 with speech/shooting. Some fast-mode assembly remains below 10 fps. The older results below describe their named revisions, not v20.

---

> v19: Shape-aware assembly compositing and fully hidden object culling replace the black rectangle. Stationary one-rock overlap measures 19.00 fps; constant phase-changing overlap measures 8.62 fps. See [ASSEMBLY_CACHE.md](ASSEMBLY_CACHE.md) for the current results and limitations. Earlier entries below are historical.

> v18: Assembly uses double-buffered shifted graphics. Controlled player-overlap: 6.01 -> 19.75 fps at fixed phase 7; changing phase every picture: 7.33 -> 12.40 fps. See [ASSEMBLY_CACHE.md](ASSEMBLY_CACHE.md) for current measurements, preparation latency, memory and verification. Earlier results below are historical.

# Sustainable fast-mode assembly v15

Cartridge `2689d68ab4f0330deea395d68a86ca579959190bb94b81b350d90961c5fe1569`. Fast-mode replenishment is now suppressed only after Sinistar awakens. Before pursuit, excess visible secondary planetoids recycle through normal far-sector refill; the primary mine can regenerate. The two-visible-rock cap remains. Six repeated cull/refill cycles and a complete fast-mode mining/build/win/restart/loss sequence pass.

New natural-world profiles: normal/fast assembly 5.78/8.67 fps; normal/fast chase 6.17/12.46 fps; fast chase with repeated speech and shooting 12.30 fps. See FAST_MODE_PROFILE.md and build/fast-detailed-profile.json for conditions, non-overlapping routine timing, and prioritized optimization candidates. No speed improvement beyond the resource-policy fix is claimed in this revision.

Before awakening, HOME 5BB2 is zero (refills enabled) even when fast mode is enabled at 5BB1. Pre-chase culled slots do not retain saved masses. During awakened pursuit, 5BB2 becomes one and the previous retirement/restoration behavior applies. Sprite/halo geometry and memory layout otherwise remain unchanged.

Fourteen verification reports match this cartridge. Legacy profile files identify earlier cartridge hashes; the new detailed profile is current. Earlier saved revisions remain intact.

---

# Moving attribute color bands v14

Cartridge `828dc1ca0e89616df50bb8b874574c6ede36243010b09f44e4aefc4e286abd63`. The artwork-centered expanding halo now contains a repeating yellow/white/red/white pattern in 8-by-1 ECM cells. Adding the refresh phase to scanline Y shifts the horizontal bands upward one pixel per refresh. Outer diameters still expand 86, 90, 94, 98 pixels across four complete visible frames; original attributes restore on frame five. The center is protected and there are no bitmap writes.

The DOCK2 fill helper now reads cell records sequentially using HL rather than indexed IX loads. This removes late attribute writes seen in the first prototype. `verify_cycling_raster.py` checks every playfield pixel against the expected growing band pattern in all twelve colored frames across three pulses, plus unchanged Sinistar and exact restoration. These checks use actual TSRun raster output. The RAM-level effect test additionally verifies clipping, shifted positions, skipped events, exact restoration and continuing AY writes.

Complete synchronous effect time is 97.9-175.2 ms in the dedicated fixtures, including preparation and restoration. The displayed animation remains four refreshes (~66.5 ms); scene updates wait through preparation. The preexisting fast-mode two-rock limit and native notices remain unchanged.

DOCK2 helper payload: 712 bytes. DOCK7 effect/mode payload: 1343 bytes. Thirteen verification reports match the cartridge. Archived performance profiles identify older cartridge hashes. Earlier revisions are unchanged.

Demo: `/port/build/cycling-halo-video/WATCH.html`.

---

# Expanding, artwork-centered halo v13

Cartridge `4a4c015f3d1a2bd97d95c4b79614e5dad549925414dcfec36561ca03ca0438c7`. The halo center shifts four pixels left: the complete Sinistar art bounds are x=0..48 and y=2..50, so its center is (24,26), not the padded seven-byte rectangle center (28,26). Horizontal cell selection uses symmetric half-open extents to avoid favoring one side of the center. Attribute-grid edge steps remain unavoidable.

Outer diameters expand 86, 90, 94, 98 pixels over gray, yellow, red and white refreshes, respectively. The radius-40 center stays clear and the screen restores on refresh five. Actual emulator raster pixels were checked against all four expanding masks, including every pixel in the unchanged Sinistar image. These are complete consecutive colored refreshes, not just RAM snapshots.

Three half-width tables in spare DOCK2 space precompute the expansion thresholds. Preparation builds four-byte records (attribute address, original attribute, first visible phase) in HOME B800..BFFF; later phases recolor and extend the halo without rebuilding geometry. No bitmap writes occur. DOCK7 effect code is 1375 bytes; DOCK2 helper payload is 665 bytes. Fast-mode behavior is unchanged.

The displayed effect lasts four refreshes (about 66.5 ms). Full synchronous execution, including cell classification, initial alignment and restoration, takes 97.9-175.2 ms in current fixtures (about 175 ms fully visible). This preparation delay is a performance limitation; speech interrupts continue but scene updates wait. Ordinary frame rendering does not incur this work between hit events.

Twelve regression reports match the saved cartridge. Performance profiles retained from earlier milestones identify their older cartridge hashes. New video: `/port/build/expanding-halo-video/WATCH.html`.

---

# Attribute halo v12

Cartridge `ff2b0a5b934b8e05ef8cd94a2a49d9de1e579364bcea665adb5d6bfae7967a4d` replaces the solid disc with a color-cycling halo. The outer radius stays 49 pixels; a radius-40 inner area is excluded, including every ECM cell intersecting it. Sinistar's complete sprite rectangle remains unchanged during all four colors, including shifted and clipped fixtures. The outer diameter remains approximately 1.75 times Sinistar's width. Horizontal edges follow the 8-pixel attribute grid.

Gray, yellow, red and white occupy four consecutive refreshes; restoration occurs on the fifth. Only halo attributes are written. Bitmap bytes and all center attributes remain unchanged, and original halo attributes restore exactly. Speech continues. The complete synchronous routine, including building split row spans and alignment, measures 84.0-123.1 ms in the current fixtures; scene animation waits during that time. This is longer setup than the filled disc, despite fewer attribute writes.

Fast mode still has its native temporary ON/OFF notice and maximum of two visible planetoids. Previous snapshots remain intact. Twelve regression reports match this cartridge; normal-game performance profiles retained in the archive are from v11 and identify that cartridge hash. The new raster demo verifies that the entire Sinistar image stays unchanged through all four halo frames.

The DOCK7 effect/mode payload is 1337 bytes. Up to two attribute spans per scanline use the existing DC80 descriptor buffer; B800 holds original halo attributes. No extra bitmap drawing or additional cartridge banks are needed.

Demo: `/port/build/halo-pulse-video/WATCH.html`.

---

# Filled attribute color cycle, fast-mode notice and cap v11

Cartridge: `4e9cc7c44910024fd087f08732d9c7c9fd3fc488d44a713e630bf2a407559c0f`. Previous revisions are preserved.

The outline is replaced with a solid circular attribute region, nominally 98 pixels in diameter (1.75 times the 56-pixel Sinistar sprite width). It is centered on Sinistar's original position even at clipped screen edges. The ECM grid rounds horizontal edges to 8-pixel cells. Four consecutive refreshes show gray, bright yellow, bright red, and bright white. Restoration occurs on the fifth refresh. The gray step is normal palette white/gray to distinguish it from final bright white. INK and PAPER are equal, so the entire region is filled and the bitmap is never written. Original attributes restore exactly; radar and playfield bounds are protected. Current raster video verifies every sampled disc pixel across all four colors and restoration.

Setup, saving attributes, refresh alignment, color passes and restoration take 83.6-110.3 ms in the visibility fixtures. The visible colored interval is four refreshes (about 66.5 ms). Scene updates wait during this synchronous effect; speech interrupts continue. Thus the four-frame visual does not imply four frames of total CPU occupation.

F toggles experimental fast mode, initially off. The native reserved status band briefly displays FAST MODE ON or FAST MODE OFF for 90 refresh ticks (about 1.5 seconds), then clears both pixels and attributes. The message does not overlap radar, playfield or end-screen prompts. It is rendered once and cleared once, not redrawn every frame.

When enabled, at most two planetoids are visible. The primary slot is retained first, then the earliest visible secondary slot. Excess visible rocks are temporarily retired; during the chase, offscreen rocks also retire and cannot reenter. Before the chase, hidden world rocks remain eligible to enter until the cap is reached. Retired objects do not draw, mine or collide; replenishment is suppressed while enabled. Turning mode off or ending the game restores saved masses. Since filtering follows projection, restored rocks appear on the following completed picture. The scrolling test checks this documented transition separately and resumes exact reference comparisons afterward. These are deliberate performance adaptations, not original arcade population rules.

Matched silent scrolling chase benchmark: normal 6.62 fps, fast 12.61 fps. The cap, notices, and impact effect are native cartridge code. Current effect/mode code and precomputed tables occupy 1148 bytes in DOCK7. HOME B800 stores original attributes (at most 1,035 for this disc), DC80 stores up to 99 three-byte row descriptors, 7BE8-7BEE holds effect scratch, and 5BB1-5BC9 holds mode state, saved masses and notification timer. Buffers are reused only after regular screen publication.

Twelve current cartridge regression reports cover attribute-only cycling/restoration and continuing audio, default-off/edge-triggered F, two-rock cap before and during pursuit, retirement/refill suppression/restoration, native notice expiry and black-background restoration, native scrolling with mode toggles, normal scrolling/radar/clipping, overlap/publication, population, pursuit, speech priority, border feedback and complete game win/loss/restart. Actual raster video is at `/port/build/disc-pulse-video/WATCH.html` (stationary fixture, injected hit events, real F key toggles). Hardware is not yet tested.

---

# Circular impact ring and optional fast chase v10

Cartridge SHA-256: `083e856154564b5b75aa49ec26f8ebf5af0b0d922228adb237864bc6d5bd5f74`. Earlier revisions remain unchanged.

Sinibomb hits draw a radius-30-pixel, one-pixel circular outline around the visible Sinistar bounds. Native refresh timing produces red, yellow, red, then off on four consecutive raster frames. The 168 circle points are precomputed in the cartridge; clipping protects the radar and playfield edges. Every affected bitmap byte and ECM attribute is restored exactly. The shared 8-by-1 INK cells can temporarily recolor nearby sprite pixels. Partially clipped Sinistar uses the center of its visible bounds. Offscreen hits, player deaths, and final destruction retain border feedback.

This is a synchronous effect between complete pictures: speech and refresh interrupts continue, while scene updates wait. Dedicated tests measured 81-87 ms including preparing saved cells, refresh alignment, the three colored refreshes, and restoration. The colored interval itself is about 50 ms. Actual emulator raster capture confirms all 168 outline pixels are red on frame 67, yellow on 68, red on 69, and absent on 70. The demonstration injects hit requests into a stationary native fixture; it is not a browser-drawn approximation.

Press **F** to toggle experimental fast chase mode. It starts off and can be armed before Sinistar awakens. During an active chase, existing visible planetoids remain until fully offscreen; offscreen planetoids are temporarily retired and replacements are suppressed. Retired objects do not draw, appear on radar, collide with shots, or get mined. Their mass is saved and their simulation pauses. Turning the mode off or ending the chase restores retired objects; a restart returns the setting to off. This deliberately changes population behavior to favor speed; it is not an arcade-accurate world rule. The viewer reports off, armed, or active status.

Matched native scrolling chase benchmark, continuous right input, invulnerability, no worker/shooting/audio, first 120 refreshes excluded: normal 6.62 fps versus fast 12.67 fps. In the last ten seconds, normal 7.34 versus fast 13.47 fps. All 18 planetoids had retired by refresh 446 in this fixture. Normal-mode scrolling benchmark remains 8.25 fps. This does not meet the 20 fps goal and gameplay scenes will vary.

Implementation: DOCK7 uses 877 bytes of previously free cartridge space, including circle data and mode filter. DOCK2 supplies a bridge which keeps itself mapped until control reaches DOCK7; HOME2 is then mapped for display/settings access. HOME 5BB1-5BC5 holds enabled/active/key latch plus 18 saved masses. HOME DC80-DFC7 holds up to 168 five-byte ring records after ordinary publication, with scratch 7BE8-7BED. No screen buffer or additional cartridge capacity is required. Refill checks add 18 bytes to the world bank (4730 of 4750 bytes).

Verification: default-off and held-key behavior; visible retention; offscreen retirement and no reentry; 384 ticks without refill; primary respawn suppression; mass restoration on toggle/chase end; six ring visibility/event cases with exact bitmap and attribute restoration and continuing AY writes. Regression checks passed scene publication, overlap transitions, scrolling/clipping/radar, incremental rendering, population, pursuit timing, speech priority, border effects, complete playable win/loss/restart, and end screens. Physical hardware has not been tested.

See `build/fast-mode-profile.json`, `build/fast-mode-verification.json`, and `build/attribute-flash-verification.json` for measurements. Demo video: `/port/build/ring-pulse-video/WATCH.html`.

---

# Localized BRIGHT pulse v9

Current cartridge: `1690d30b20a337104e4e429a64422e19d101ff6f8e3bf586161a933258e6e091`. This replaces v8's full-screen PAPER pulse; v7 and v8 remain preserved for comparison.

A hit brightens the last published, clipped Sinistar rectangle for one displayed refresh. At most 7 by 52 ECM cells (364 attributes) are involved. Already-bright cells are unchanged, INK/PAPER/FLASH bits and the bitmap are preserved, and the exact original attributes are restored. Actors overlapping the rectangle share its brief brightness change. Hidden Sinistar, zero-size rectangles and player deaths skip the local effect; the existing border feedback remains. On the final kill the removed Sinistar has no visible rectangle, so victory uses the border sequence.

Both passes begin following a refresh interrupt. Normal composition waits until restoration completes; IRQ speech continues. Measured complete pulses in the dedicated fixtures take about 25-37 ms including alignment, compared with v8's 123 ms. The full rectangle's apply/restore work is approximately 9/7.5 ms with the current loops and interrupt overhead. Thus this is a shorter bounded pause, not a zero-cost asynchronous overlay. Ordinary chase benchmarks are unchanged from v8.

HOME E000-E16B stores up to 364 original attributes after the publication records have been consumed. HOME 783E is the pending event; 783C marks active effect writes; 783D is a row counter; 783F remains the border timer. No extra cartridge bank or live bitmap buffer is used.

Ten regression reports match the current cartridge. The effect test includes full visibility, top/left and bottom/right clipping, offscreen rejection, player-death rejection, pre-existing BRIGHT, and exact full-screen restoration. AY writes continue during the pulse. Actual gameplay exercised four visible localized pulses and passed mining, victory, restart, protection, and loss checks. Physical hardware is not yet tested.

---

# Full-screen attribute pulse experiment v8

Current cartridge: `c33a3f457c58d7f26bcef636582db1aec6c60743786d04874346ff79b8ccf0d5`. v7 remains available as the border-only comparison.

Native Sinibomb hit and player-death events now request a red PAPER pulse; victory requests yellow. The existing border sequence remains. All 6,144 ECM attributes, including the radar/status area, are XORed with 0x10 (red) or 0x30 (yellow), held for three HALTs, then XORed again. Bitmap, INK, BRIGHT and FLASH bits are untouched; every original attribute is restored exactly. Nonblack PAPER colors change by XOR too, so this approximates the arcade palette-zero effect rather than reproducing its palette behavior exactly.

The pulse runs between complete pictures. Rendering/gameplay progression pauses during it; refresh interrupts, speech and border timing continue. No rendering occurs between the two passes, so no backup buffer is required and the compositor sees restored attributes before its next comparison. The normal 60 Hz physics catch-up follows afterward. Each measured pass takes about 41 ms; the entire pulse takes about 123 ms (433k T-states). This intentional effect can cause an animation pause on impact; ordinary movement has no full-screen pass overhead. It is not an instantaneous hardware palette switch.

HOME 783E is the pending event, 783C the active effect flag, and 783F the separate border timer. DOCK2 has the unrolled native XOR routine. The obsolete generated-instruction template initialization was removed; packed publication is unchanged.

The dedicated test verifies all 6,144 attributes in both states, exact restoration, unchanged bitmap and INK/BRIGHT/FLASH, and continuing AY writes during three pulses. Actual mining/bomb/death gameplay also exercises the effect. Intentional flash writes are distinguished from normal raster-safe scene publication. Ten test reports and two profiles accompany this revision.

---

# Border effects v7

Current cartridge: `217a1462ee0822a65c9923cf71082529c536352eca7c64de105dc6deec4d2ad1`. Earlier performance tables below refer to v6; current measurements are in build/one-planetoid-profile-current.json and build/scrolling-profile.json.

Sinibomb hits flash red for six refreshes (~100 ms), player deaths for nine (~150 ms), and victory alternates red/yellow over 36 (~600 ms). The border returns to black, including after win/loss. These are adapted timings, not a cycle-exact recreation of the arcade palette effect. The prior persistent blue/red/green status borders are replaced; respawn protection and native end messages remain intact.

HOME 783F holds the boot-cleared timer. Event hooks publish the timer even when speech is busy. The ISR skips the banked effect routine while idle (29 T-states for the idle check, about 0.05% of a refresh). Active ticks write port FE with values 0, 2 or 6 only; no beeper/tape bits, AY writes, bitmap writes or attribute writes. Full-screen attribute flashes are not implemented in this revision.

The dedicated native border test covers expiry, colors, bank/stack restoration, and forbidden display/audio writes. The existing eight regression suites are rerun. The gameplay test samples victory positions at frame completion, because mid-render coordinates are temporarily camera-relative.

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

# Incremental overlap restoration â€” revision bf381583

Open http://127.0.0.1:8768/port/revisions/playable-incremental-overlap-v5/mining-web/ .

Old rectangles are subtracted from the new opaque Sinistar rectangle once. At most four exposed strips are erased; overlapping cells are left for the current face to overwrite. Dirty bounds still include old actors so their previous images are repaired. No live-screen erase is introduced.

When Sinistar is stationary, fully visible, awake and shut-mouthed, its shadow image is retained. Only dirty overlap spans are copied from the current face atlas. Eye changes mark rows 12â€“25; the builder verifies that all differing cells across all eye pairs and all eight fine phases lie in that range. Moved faces, clipping, mouth transitions, assembly changes and transitions from the direct-screen path retain the complete-copy fallback. This is not yet arbitrary-displacement incremental rendering, nor elimination of every layered overlap write.

Compared with compiled-rocks v4, the controlled one-rock chase improves 11.371 to 11.952 fps and the three-rock chase 7.704 to 7.932 fps. The no-Sinistar scene remains 19.261 fps. Mixed scrolling measures 8.089 versus 8.146 fps: essentially unchanged, slightly slower in this trace. The 20 fps chase target remains unmet. Tests suppress combat/speech for controlled timing; no physical hardware verification was performed.

Verification: `verify_incremental.mjs` checks 600 rectangle pairs, 47,562 restored cells, 4,140 preserved overlap cells, zero duplicate restoration writes, ROM safety and bank/stack restoration. `verify_scrolling.mjs` now checks 400 clipping/overlap/animation fixtures, including 144 stationary-face cases, across 548 pictures; the incremental face path executes 136 times and restoration 1,962 times. It reports zero ROM or late-raster writes. The existing population, pursuit, playable, voice, end-screen and 216-transition/432-overlap regression suites also pass. Reports match SHA256 `bf3815835602f2f1bb7dcb5054e252a449b52f8ed86ff2db3903511afbcbdf55`.

The following describes the preceding milestones and unchanged world behavior.

# Playable scrolling world â€” compiled planetoids revision 93b7974f



Open the saved revision at http://127.0.0.1:8768/port/revisions/playable-compiled-rocks-v4/mining-web/ .



Fully visible planetoids now use 209 shared, position-independent Z80 row programs (7,341 bytes including phase tables) in DOCK2. Each instruction stream embeds masks, pixels and colors, skips transparent cells, and composes into HOME shadow planes. Overlapping sprites retain their original order. The ISR and stack stay mapped, and interrupts remain enabled. Clipped rocks retain the existing compositor, reading raw graphics cached at A000/C300/5900 instead of decompressing or mapping a source bank.



This replaces the specialized horizontal Sinistar transition templates; the general Sinistar transition path remains and passes all 216 transition cases plus 432 overlap fallbacks. The original 60 Hz demonstration is preserved separately. The former transition cache windows now hold raw rock phases. Offscreen secondary rocks are rejected before full projection when possible, and hidden slots avoid unnecessary rectangle copies. Physics, population, collision bounds, speech priority and radar cadence remain unchanged.



Measured before/after against composition/endings v3:



| Scene | v3 fps | Current fps |

| --- | ---: | ---: |

| One visible rock, no Sinistar | 14.446 | 19.261 |

| One visible rock, active Sinistar | 9.357 | 11.371 |

| Three visible rocks, active Sinistar | 6.147 | 7.704 |

| Mixed scrolling trace | 7.120 | 8.146 |



Controlled rock tests disable combat, worker activity and speech; the mixed trace follows native keyboard flight and includes clipping. These are emulator results, not physical hardware measurements. The 20 fps chase target is not met. Local overlap composition for Sinistar remains pending. Broad four-byte dirty blocks and separate star comparison were prototyped but rejected because they slowed these benchmarks; neither is present in this cartridge.



Native YOU WIN / GAME OVER text remains. Release fire, then press Space or joystick 1 fire to restart; R also works. Wave progression remains pending.



The following culling milestone discussion is historical background.



The culling revision skips sprite staging for fully hidden objects, skips invisible secondary rectangles within the banked iterator, and marks new planetoid rectangles without redundantly clearing them. Old rectangles are still erased in shadow, preserving overlaps and edge restoration. Radar refresh is limited to once per 16 physics ticks (about 3.8 Hz), with publication on the next picture. In the same keyboard-flight trace, performance improves from 5.805 to 6.891 rendered fps, about 19%. The trace sees 1â€“6 planetoids, averaging 2.77, not all 18 simultaneously. Sprite clipping is a small fraction of frame work; composition and changed-byte comparison dominate. Population and world dimensions are unchanged.



The native 64 KB cartridge now uses persistent 512Ã—512 world coordinates for the player, planetoids, worker, crystal, bullets, Sinistar, and Sinibombs. A dead-zone camera follows the ship. Graphics clip against the 256Ã—112 playfield instead of deleting an object when it reaches an edge. Movement, homing, mining, and contact calculations use wrapped world distances. The earlier standalone translation of the arcade's soft/hard camera is not yet used by this playable adaptation.



Ten stars move opposite the camera and wrap around the visible playfield. Their screen phase persists across the 511/0 world seam. The source's `SAM/IRQ.SRC` and `SAM/SAMEQUAT.SRC` use ten stars with a common camera displacement; this build does not invent separate parallax depths. It suppresses a star in an occupied bitmap byte. The arcade's additional randomized edge-star replacement is not implemented.



## Population and source fidelity



`FALS/N1ALL.SRC`, `InPop0`, specifies ten type-1 planetoids and two each of types 2â€“5: 18 total. This build maintains that first-wave population, rather than recycling a single visible rock. All 18 retain their positions offscreen, drift, appear on the scanner, can be shot, release crystals, and can shatter. Depleted slots replenish away from the player, gradually rather than every time the camera moves.



The surviving source's `AdjPop`/`PopFil` fills shortages at sector edges while avoiding the player. The port uses a smaller toroidal world, deterministic starting positions, and a simplified replacement schedule; it is not a full translation of that allocator, later waves, or random swarms. All five population types currently share the IPLAN1 image and initial mass. There remains one worker, one free crystal, one bullet, and one Sinibomb slot. The worker mines the primary rock and follows crystals across the world; choosing among all mines and multiple-worker AI remain pending.



The nine `SCIVELT` directions retain the existing display-scaled velocities: Â±108/256 horizontal and Â±28/256 vertical pixels per physics tick. Secondary planetoids use four interleaved groups, integrating four ticks of displacement once per four ticks. This preserves average speed and fractional motion while reducing CPU cost. Those display scaling factors and cadence are adaptations, not literal arcade pixel speeds.



## Scanner



The top scanner maps the entire 512Ã—512 world into 64Ã—16 pixels: horizontal scale 1/8, vertical scale 1/32. Both axes include the ninth coordinate bit. The previous vertical mapping aliased contacts separated by 256 world units; that is corrected.



The player stays at (32,8), bright white. Planetoids are cyan, the worker red, and Sinistar yellow. Blue corners follow the actual camera viewport. Attribute conflicts can shift another marker down one scanline; the player stays anchored. The short markers may be truncated at an 8-pixel cell boundary. Changed scanner bytes are prepared in RAM and published with the next picture. Its bounded publication list holds 117 records; the verified sequence peaked at 71.



## Drawing and performance



Eight precomputed phases remain available for the ship, planetoids, and shut-mouth Sinistar. Planetoid graphics are stored uncompressed for faster staging. Secondary rectangles are projected and clipped once per picture, then reused for clearing, drawing, and overlap decisions. The Sinistar transition path checks old/new object rectangles and star cells, including all secondary planetoids. Overlap, clipping, larger moves, and speech use composition. Partial assembly and opening-mouth images use a runtime shift fallback when the camera is not byte-aligned.



Only changed final bitmap/attribute bytes are published; there is no visible erase pass. The saved 60 Hz scripted demo remains unchanged. **This much busier playable scrolling scene renders about 8.15 fps in the measured keyboard-flight trace.** Physics advances at the native refresh cadence, catching up between renders. This is a functional scrolling milestone, not the final smooth port. Composition and dirty-span comparison are the main remaining costs. No physical TS2068 verification was performed.



## Verification



- `verify_end_screen.mjs`: both native messages and attributes, held-fire protection, release/repress keyboard and joystick restart, reset inventory/lives/status.

- All listed regression reports were refreshed for cartridge SHA256 `93b7974fbf7ce291e042351f2571916bd36df2673a618d92bc7d2066f7b5bfa0`. The playable test now accounts separately for expired bombs; victory still requires exactly 13 hits and ammunition must match every launch.



- `verify_scrolling.mjs`: independent full-playfield composition, 256 camera/edge/assembly/mouth cases, and exact scanner bitmap/color comparison against world coordinates. Includes native keyboard scrolling. No late playfield writes or ROM writes in this trace.

- `verify_population.mjs`: 2,448 coordinate checks over all nine source velocity directions, fractional motion and both wrap seams; all 17 secondary slots refill; a secondary rock can be hit across the seam.

- `verify_pursuit_timing.mjs`: 225 signed hit cases, 1,536 pursuit ticks across all eight decision phases, including world wrap and stun.

- `verify_playable.mjs`: ammunition from actual mining/pickup, autonomous 20-piece assembly, 13-hit victory, restart, contact damage, protection, and game over.

- `verify_voices.mjs`: full AY register-stream verification, death and bomb-hit triggers, speech interruption/restart.

- `verify_mining_scene.mjs 16000 --transitions`: preserves the fixed diagnostic and its 216 direct-transition cases plus overlap fallbacks, with no wrong/redundant/ROM/late-raster writes.



Reports and a native screen capture are saved under `build/`. Use their cartridge SHA-256 to distinguish current results from historical reports.



## v16 rendering and empty populations

Empty chase populations bypass projection, draw/clear/overlap scans and physics after the final old rectangle is erased. Pre-awakening refill remains active. Stars covered by awakened Sinistar's rectangle are culled by position, with old/new bounds checked for safe direct updates. Guarded eye-band updates and an optional fully-covered-player experiment are available. The saved game preserves player visibility. See FAST_MODE_PROFILE.md for same-cartridge policy comparisons, native test coverage and the remaining 20 fps gap.


## v17 clipped Sinistar cleanup

Reproduced stale bitmap bytes on native pursuit picture 21: the old clipped face rectangle was (6,64,7,45), the new rectangle (6,64,7,42). The old-rectangle skip compared x, y and width but not height, leaving rows 106-108 untouched. clear_four now compares all four rectangle fields before skipping restoration. The compact loop fits the existing ROM allocation.

Added 112 radar-boundary shrink/reentry cases (592 total clipping fixtures) and a deterministic 18,000-refresh native pursuit regression with complete bitmap/attribute comparison after every picture. The stress run uses real world physics and direction changes; synthetic clipping tests remain separate so injected fixtures do not contradict fast-mode retirement state.
