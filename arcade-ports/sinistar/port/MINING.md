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

# Native mining integration cartridge

**Current playable build:** see [SCROLLING.md](SCROLLING.md) for the persistent scrolling world, ten stars, 18 planetoids, corrected scanner, performance measurements, and remaining adaptations. Earlier milestones below are historical.

Open http://127.0.0.1:8768/port/mining-web/ using the project server.
The cartridge is `build/sinistar-mining.dck`, with a 64K physical image at
`build/sinistar-mining.bin`. It is separate from the preserved pursuit cartridge.

## What runs on the Z80

The automatic fixture fires at one planetoid, registers bullet hits, releases
one crystal, lets the worker deliver it, and destroys the over-mined rock. The deterministic
baseline records 16 hits, one release, one worker pickup/delivery, zero player collections, and one shatter. Restart
repeats the sequence. QAOP / joystick 1 take control; Space / joystick fire
launches a shot. Release directions to coast. D resumes rightward automatic
fire from the current position; Restart restores the original setup.

The original IPLAN1 (26x28) and ICRYSTA (2x4 including transparent padding)
pixels are extracted from SAM/IMAGE.SRC. Colors are quantized to legal TS2068
8x1 extended-color cells. The existing 32-heading player sprite set is reused.
The bullet is a simple 2x2 test sprite. Browser statistics read native cartridge
state; JavaScript does not run the mining or movement simulation.

FALS/N1ALL.SRC AddVib, TosCrys, and Vibrate supply the vibration increase,
release threshold/probability, mass reduction, damping and shatter rules.
The integrated cartridge's copies pass the same 197,120 assembled-Z80 rule cases.

## Explicit adapters and limits

This is an integration fixture, not the complete arcade population or scheduler.
There is one rock, one worker, one active bullet, and one crystal slot. The allocator cannot
release another crystal until the slot is free. Collision tests use rectangles.
The random sample provider increments a byte by 73, and the crystal receives a
fixed -127/256-pixel horizontal drift for repeatable pickup testing. Release is
checked every 12 physics ticks, standing in for the three-leg Task4 vibration
cycle. Visible shaking, fragments, sound, crystal lifetime, inventory capacity,
arcade scoring and the actual scanner/object scheduler are pending.

The fixture uses a bounded test arena, not camera scrolling. The existing
pursuit cartridge still supplies the scrolling/parallax demonstration. Workers,
warriors, multiple planetoids, Sinibomb launch/damage, and Sinistar construction
remain to be connected to the shared game. The next integration should replace
the fixed slots with object records and wire worker pickup/delivery to crystal
ownership, rather than duplicate this fixture's temporary allocation scheme.

## Rendering and memory contract

Sprites compose into HOME bitmap $A000–B7FF and attributes $C000–D7FF. Old/new
rectangles mark dirty rows. The stationary rock is not cleared or fully compared
unless it changes position or visibility; recomposing it in shadow restores areas
covered by moving sprites. Publication uses XOR comparisons and generated final
stores, so the display is never erased then redrawn. Background is black in this
fixture. There is no emulator speed multiplier.

| Chunk | DOCK contents | Runtime HOME dependencies |
|---|---|---|
| 0, 1 | Sprite data | System ROM normally selected |
| 2 | Sprite data | Bitmap $4000–57FF; temporarily overlaid only for reads |
| 3 | Not supplied | Attributes $6000–77FF, state/IM2/stack $7800–7FFF |
| 4 | Resident code and pointer tables | DOCK always selected |
| 5 | Sprite data | Bitmap shadow, staging $B800; staging uses $D800 when overlaid |
| 6 | Unused ROM fill | Attribute shadow and temporary staging $D800 |
| 7 | Unused ROM fill | Generated publication code $E000–FFFF |

HSR=$10 normally; sprite fetch adds its source bank bit, then restores $10.
DECR=$02 selects extended color. AY register 7=$3F keeps port A input and sound
channels disabled. ISR saves AF; stack remains HOME at $7FFF, IM2 at $7A00.
Dirty row minima/maxima are $7900/$7D00. Five current rectangles occupy
$7840–7853, old rectangles $7860–7873. See symbols for object-state addresses.

All sprite rows stay within y=64..175. The five old/new bounding rectangles
contain at most 448 cells, or 896 final plane-byte writes. The generated program
is bounded by 4,481 bytes and publication by roughly 17,920 T-states plus call
and ISR overhead, before the first affected raster row. Measured publication
was much shorter; the independent raster verifier remains the acceptance check.

## Verification

- Baseline: 3,600 refreshes, 3,298 completed pictures, expected hit/release/pickup/
  shatter events, no wrong or unchanged display writes, ROM writes, or raster mismatches.
- Manual/relocation stress: 12,000 refreshes, 6,242 pictures, 46 rock relocations
  exercising all horizontal pixel phases; the same zero-error checks pass.
- Maximum observed generated program: 621 bytes; publication: 2,507 T-states.
- Native Fuse: 1,023 completed intervals over 1,447 refreshes, SP=$7FFF at both
  checkpoints. This mixes active mining and an empty scene after shattering;
  it is not an FPS claim for a populated game. Hardware remains untested.

Reproduce with Python and the configured modern Node runtime:

```text
python port/scripts/build_mining.py
node port/scripts/verify_mining.mjs --integrated
node port/scripts/verify_mining_scene.mjs 3600
node port/scripts/verify_mining_scene.mjs 12000 --controls
python port/scripts/verify_fuse.py --mining
```

Accepted snapshot: `revisions/mining-integration-v1`, including source, artifacts,
verification reports, browser files, and SHA256SUMS.json.

## Browser input fix

Restart now returns focus to the emulator canvas. The containing page intercepts
QAOP, D and Space keydown/keyup and forwards them to the emulator, preventing
Space from activating a focused Restart button. Ctrl/Alt/Meta shortcuts are
left to the browser. The native cartridge is unchanged. Verified in-browser:
Restart focuses the display, and Space directed at the Restart button preserves
manual mode and the existing hit/collection counters.

## Worker integration v1

The first IWORKER pose (10x12) is decoded from SAM/IMAGE.SRC with eight pixel
phases. HOME $78B0/B1 stores its pixel position, $78B2 its mission (0 waiting,
4 intercept, 6 carrying), $78B3 existence, $78B4/B5 pickup/delivery counters, and
$78B6 the caller identity. The sole crystal is assigned identity 1. A value of
2 in crystal_alive marks worker ownership; player pickup/drift no longer acts
on that crystal. It follows the carrying sprite until delivery.

Ownership and consume-on-delivery behavior follow WITT/COLLISIO.SRC,
FALS/N1ALL.SRC GivCrys, and WITT/WORKER.SRC mission 140. The prototype assigns
its sole free crystal directly; it does not implement caller arbitration.
Travel is a one-pixel-per-axis-per-tick fixture, not the original velocity
or scanner algorithm. The destination is (208,80). Delivery consumes worker
and crystal and emits a counter event; AddPart and visible Sinistar assembly
are not implemented. Original worker heading animation, drift/tail/evade,
orbit/dying-Sinistar gates, and worker shooting/death remain pending.

The automated sequence now demonstrates the worker winning the crystal.
The --player verifier disables the worker to retain the prior player pickup
regression. Every rendered frame asserts exclusive crystal ownership, attachment
to its carrier, and pickups = deliveries + current carried crystal. Native
scene/raster and Fuse reports in build/ are authoritative for this checkpoint;
the earlier measurement list above describes mining-integration-v1.
Saved checkpoint: revisions/worker-integration-v1.

Worker checkpoint results: 3,600 refreshes / 3,257 pictures in the default run;
12,000 refreshes / 6,217 pictures with manual input and 45 relocations. Both
runs have zero incorrect/unchanged display writes, ROM writes, or raster
mismatches. Maximum publication is 2,567 T-states. The player-only regression
still collects one crystal. Fuse completes 1,023 intervals over 2,141 refreshes
with SP=$7FFF at both checkpoints. These are fixture measurements, not a claim
about a populated arcade scene's frame rate.


## First assembly piece (2026-10-04)

Worker delivery now installs S1L, the first PIECETB entry ($270B), then consumes carrier and crystal. Original 15x14 artwork is decoded from S11 through S12; its final transparent row is outside the 52-row body canvas. Body origin (197,80) places the flipped 15x13 piece at (208,80). This is one AddPart transition, not the complete assembly dispatcher.

Assembly count is HOME $78b7. Sixth rectangle occupies $7854-$7857, previous rectangle $7874-$7877. Cartridge mapping and stack remain unchanged. Piece assets have eight horizontal phases. Stationary piece clearing occurs only on visibility changes; shadow redraw occurs only when dirty spans intersect it. Final display publication still uses XOR comparison and changed-byte stores. Six-object store capacity bound is 5261 bytes / 1052 stores.

Build SHA256: 521920402550bf85ecd8714c2f7ba650978ebbac7d6e262935f93fb94fa1cde0. Baseline: 2827 completed pictures over 3600 refreshes, 3462 physics ticks, one delivery and one piece. This does not achieve sustained 60 pictures/sec. Controls: 6050 pictures over 12000 refreshes, 45 relocation/overlap probes across eight sub-byte positions; no incorrect, redundant, ROM, or raster writes detected. Peak publication 2747 T-states. Player-only collection and 197120 integrated mining rule cases pass. Native Fuse completed 1023 frame intervals with SP=$7fff.

Saved revision: revisions/assembly-first-piece-v1. Remaining work includes the other eleven pieces, repeatable worker supply, full arcade worker AI, warriors, and Sinibombs.


## Twelve outer assembly pieces (2026-10-04)

Supersedes the first-piece fixture above. The pinned SAM/SAMTABLE.SRC PIECETB supplies twelve outer entries before ALIVE. Eight additional face entries follow ALIVE before PIECEND: twelve outer pieces are not a living Sinistar. Native deliveries now advance once through all twelve outer entries and stop at twelve. Targets use their body-relative offsets, with body origin (192,80). Right-hand artwork is read backwards by column as MODSINI does.

The first crystal is mined. After each delivery a 60-physics-tick test delay supplies a new worker and loose crystal until twelve pieces are installed. This deterministic supply is not the original worker spawning/resource economy. Taking the initial crystal yourself prevents assembly in the player-only test. Full scanner AI, internal face assembly, awakening/chase, warriors and Sinibombs remain pending.

Twelve cumulative 49x52 ECM images occupy 13104 cartridge bytes, retaining original pixel coordinates with ECM palette conversion. HOME D800-DC43 caches the current image; DC80-DE23 is temporary staging for bank-5 sprites (maximum 420 bytes). B800-BC43 holds staged images. DOCK chunk 4 remains resident; chunks 0/1/2/5/6/7 hold artwork; chunk 3 remains HOME for display, stack and IM2. The stack is still 7fff. Assembly count/previous stage/delay/target X/Y occupy 78b7-78bb; 78ee selects dirty-row-only background restoration. Changes to the count invalidate the whole body; otherwise only dirty intersecting rows are restored from cached artwork. Both display planes still receive only final changed bytes after XOR comparison.

Build SHA256: 9eea8c1c607c4d44870c4d13d90bc85f0e767fa067d9f00e5a37ccf42b38b278. Baseline sees every stage 0 through 12, with 12 pickups and deliveries: 2705 pictures in 6000 refreshes and 5862 physics ticks. Cached-row restoration improves this from 2328 pictures in the initial full-image implementation, but sustained 60 pictures/sec remains unmet. Player-only test: collection=1, assembly=0. All 197120 integrated mining rule cases pass. Native Fuse: 1023 frame intervals in 2807 refreshes, SP=7fff. Full controls/overlap and raster evidence is in mining-controls-verification.json. No real hardware test.

Saved revision: revisions/assembly-outer-v1, including source, generated targets, cartridge and verification reports.


## Complete twenty-piece structure (2026-10-04)

The fixture now follows PIECETB through PIECEND: twelve border pieces and eight face pieces. The source parser handles descriptor-local labels (CHIN/NEZ) and backwards right-hand columns. After delivery twenty, HOME 78bc becomes 1 and scripted worker/crystal supply stops. This marks structural completion only: original animation-pointer/FINISH retargeting, speech, awakening and pursuit integration are not implemented here. Existing pursuit/speech demos remain separate.

To fit twenty states, the cartridge stores cell patches rather than full snapshots: little-endian byte offset within the 1092-byte cache, followed by mask/bitmap/attribute, terminated by ffff. The first patch initializes every cell; native code zeros the cache first. Later patches update only changed cells. Total assembly payload is 4100 bytes (versus 21840 uncompressed). Metadata retains full independently composited states for verification. Cache remains D800-DC43; staging remains B800-BFFF. Bank-5 staging at DC80 is used only for small records that fit its remaining cartridge space. Bank 6 stores the larger assembly records; code, HOME stack and interrupts remain mapped as before.

Final DCK SHA256: e089adcba72e1d1d7660231a8a5a4bd0126f05e98eba09da9f8a569bd78a0ade. Baseline: every stage 0..20 observed, 20 pickups/deliveries, 4058 pictures over 9000 refreshes. Controls: 6816 pictures over 15000 refreshes, 30 overlap/relocation probes, no incorrect or redundant display writes, ROM writes, or raster mismatches; peak publication 2787 T-states. Completed-build flag is asserted against count==20 on every publication. Player-only collection remains assembly=0; 197120 mining rule cases pass. Fuse checks 1023 intervals over 2804 refreshes with SP=7fff. This is emulator evidence, not hardware validation; sustained 60 pictures/sec remains unmet.

Saved as revisions/assembly-complete-v1. Next: source-driven awakening/animation, then integration with pursuit; worker supply remains a test adapter.


## Awakening mouth animation (2026-10-04)

After delivery twenty, the native interpreter runs WITT/ANISINI.SRC AniSC2 (Beware! I Live!) once. AMOUT1/3/2 supply shut/half/wide artwork mirrored about the source center, replacing the source mouth region at offset 060C. Three 1092-byte ECM snapshots restore exact pose changes, including cleared pixels, into the D800 cache. This is a silent mouth-animation integration; no AY speech, eyebrow cycling, off-sector/death gate, or pursuit transition is claimed. The completed structure stays stationary with its mouth shut after the sequence.

Native state: mouth 78bd, remaining ticks 78be, published pose 78bf, sequence byte index 78c0, completed flag 78c1. The original duration data are converted from source decimal-suffixed/hex literals by the build script. Durations advance on physics ticks rather than render completion; a one-tick pose can be skipped visually when rendering spans several ticks. Dirty flags include pose changes, and publication continues to write only final changed display bytes. The existing bank/cache/staging/stack layout is unchanged.

Final SHA256: c4f75f9e92f2509ed2926e5fcc51c639bd88a20497cafdac00cffe2c24d8bbd1. The independent per-tick interpreter model matches all mouth/timer/index/completion state, 108 active ticks including the end marker, and all three displayed poses. Baseline: 4027 pictures in 9000 refreshes. Controls/overlap: 6783 pictures in 15000 refreshes, 31 probes, max publication 2707 T-states; zero wrong/redundant/ROM writes or raster mismatches. Player-only collection never starts awakening. Integrated mining rules: 197120 cases pass. Fuse confirms 1023 intervals and stable 7fff stack; those early checkpoints precede awakening, which is checked end-to-end in TSRun. No hardware validation; sustained 60 fps remains unmet.

Saved revision: revisions/awakening-mouth-v1.


## Independent eyebrow animation (2026-10-04)

AEYE1/2/3 now cycle independently of the one-shot AniSC2 mouth sequence. Original mirrored artwork at 1A0C and palette slot 0e intensities 7,3,0 are converted to legal ECM cells. Nine precomputed eye/mouth combinations prevent one animation from erasing the other. The fixture advances eyebrows every 16 physics ticks as a Task16 cadence adapter; the original Think/task scheduler is not integrated, so exact arcade wall-clock cadence is not claimed. Eye state persists after the mouth sequence ends.

State: phase 78c2, tick counter 78c3, published phase 78c4. Cached image index is eye*3+mouth. Dirty publication includes changes to either pose; memory banking/cache/stack rules remain unchanged. All animation remains native Z80; browser displays the native screen.

SHA256: 61f0e429e8ab4343ce39b245c1f3618a0210b0687002c3bc621d217f235cf403. Independent tick models verify eyebrow phase/counter and mouth timing; all three poses of both animations are observed. See current mining-scene/controls/player-verification JSON reports for full-display and raster results. All 197120 mining rule cases pass. Fuse early execution/stack checks pass (1023 intervals), while TSRun covers completed assembly and animation. No physical hardware test. Speech and pursuit remain pending; sustained 60 fps remains unmet.

Saved as revisions/awakening-eyebrows-v1.


## Assembly-to-pursuit integration (2026-10-04)

When the awakening mouth sequence ends, the assembled Sinistar starts direct pursuit. mining-pursuit.asm reuses new_velocity, chase_velocity and smooth_velocity, including the long-axis distance scaling and short-axis speed doubling from pursuit.asm. This scene uses screen-coordinate centers, player velocity and explicit fully-visible clamps (x=0..200, y=64..124); scanner wrapping, orbit, stop states, camera displacement and contact damage are not integrated. Worker/crystal supply remains scripted after the initial mined crystal.

Face Q8.8 position X/Y is at 78c6/78c8; velocity X/Y 78ca/78cc; last drawn integer X/Y 78ce/78cf. A 2048-byte resident rotated-byte lookup shifts the current mask/bitmap cache at all eight horizontal phases, in one pass, into B800. HOME 78d4 is the row counter. ECM attributes remain on destination byte cells: geometry shifts by pixels, but colors near cell boundaries are approximate. Existing D800 cache, temporary bank-5 staging, HOME stack and IM2 remain unchanged. Movement invalidates old/new rectangles, and the full composition is published with changed-byte stores only.

Final SHA256: 0f7c49a413995042e91109a12a4cfb47731e8125be74eb2c18f836db304a24a5. Baseline: 2379 pictures in 9000 refreshes, 16 distinct chase positions; controls: 3288 pictures in 15000 refreshes, 297 chase positions, max publication 11767 T-states. Every full bitmap/attribute plane and raster comparison passes, including independently calculated horizontal shifts. No wrong/redundant/ROM writes. Bounds and all assembly/mouth/eyebrow state checks pass. Player-only collection still prevents assembly/pursuit. 197120 mining rule cases and early Fuse stack/execution checks pass; end-to-end pursuit evidence is TSRun.

The lookup improves on the initial repeated-bit-pass shifter (2277 baseline pictures), but continuous moving-face composition remains much slower than the target. This is a functional integration milestone, not a 60-fps result. Next work should optimize moving-face restoration/publication and add missing gameplay/audio.

Saved as revisions/assembly-pursuit-v1; prior fixtures and the older fast pursuit demo remain preserved.


## Pursuit cache optimization (2026-10-04)

Image identity (assembly/mouth/eye) is now separate from screen position. Movement no longer reloads the identical image from cartridge. HOME 5800-5c43 caches the shifted 1092-byte sprite; this is unused normal-mode attribute/storage RAM in ECM, outside bitmap 4000-57ff and attributes 6000-77ff. Cartridge overlays of chunk 2 do not change the HOME cache. The cache is invalidated by pose or horizontal phase changes, not Y or whole-byte X changes. Original unshifted D800 cache, B800 staging, resident code, stack and IM2 remain unchanged. New state: 78d5 image-dirty, 78d6 cached phase, 78d7 cache-valid, 78d8 old/new clearing pass.

When old/new face rectangles match, only the new rectangle is cleared. This retains masked composition and correct restoration of overlapping objects. A direct background-write experiment was slower and was removed.

SHA256: 98f35c7dab1f1c2283f75fb5d276fee37ce77a0a3a5913c5baee33148f8a9dea. Baseline: 2494 pictures per 9000 refreshes (previous 2379, +4.8%). Controls: 3389 per 15000 (previous 3288, +3.1%), 314 chase positions, peak publication 11547 T-states. Full image/raster and state checks pass with zero wrong/redundant/ROM writes; player-only test and 197120 integrated mining rules pass. Fuse early execution/stack checks pass. This modest gain does not meet 60 fps; sustained moving-face composition remains the primary bottleneck.

Saved revision: revisions/pursuit-cache-v1.


## Assembly speech and Sinibombs (2026-10-04)

Assembly now announces the correct phrase, Beware! I Live!, using the complete archived recording from https://seanriddle.com/bewareil.wav (archive page: https://seanriddle.com/willy2.html). prepare_assembly_speech.py converts it with local speech2ay harmonic3: 125 fourteen-register frames, 1750 bytes, about 2.08 seconds. This is AY resynthesis, not PCM playback. The original AniSC2 mouth sequence is restored (108 physics ticks); its timing is source-derived, not a fresh waveform alignment to this recording. An emulated capture is mining-assembly-speech.wav. The earlier I hunger substitution was discarded.

ISR preserves AF/BC/DE/HL, selects the speech ROM bank only while sending AY frames, then restores HSR from 78df. Main sprite staging updates that shadow before changing banks. R14/15 remain untouched for joystick input. Native speech state at 78f8/78fa/78fc tracks remaining frames, source pointer and one-shot start. This streams directly from ROM; no new HOME audio buffer is used.

B launches one Sinibomb while inventory is nonzero, with one projectile slot. The fixture grants twelve test bombs upon full assembly. Crystal collection also increments inventory. Original ISBOMB artwork is decoded at eight pixel phases. Original STBLSBOM speeds/acceleration are passed through the existing new_velocity/smooth_velocity core. Screen-coordinate adapters use a finite 180-tick flight lifetime and a small center collision box. Bombs without a live target expire; offscreen bombs are culled. Twelve hits hide Sinistar and stop pursuit. Damage is counted; individual SUBPIEC destruction/debris and original scanner/fuel/coasting logic remain unported. Player contact remains harmless.

Bomb state 78a8-78ae: active, X, Y, fuel, hits, launches, expired. Q8.8 position/velocity at 7830-7837. Seventh object rectangles extend through 785b/787b. Shifted-face cache 5800-5c43 and unshifted D800 cache remain unchanged. Background restores use final changed-byte publication, including target disappearance.

Final DCK SHA256: 82d3e0451a4c1187653d9cf7fe3dd2cf8c4ecc7f51f0eb20a2ec2a593cb2e76c. Speech/bomb test verifies all 125 frames and 1625 actual AY register writes against the encoded stream under live banking. Twelve launches consume twelve inventory units and produce twelve hits; full display, attribute and raster comparisons pass with zero wrong/redundant/ROM writes. Peak publication 10027 T-states. Controls run: 3366 pictures / 15000 refreshes, peak publication 11567 T-states, all display checks pass. Player-only collection and 197120 mining rule cases pass. Native Fuse confirms early boot/stack execution; completed assembly, speech and bombs are checked in TSRun, not physical hardware.

Saved revision: revisions/speech-sinibombs-v1. Sustained 60 fps, individual piece destruction, full worker AI, warriors, camera/scanner integration and additional speech remain pending.

## Playable fixed-arena prototype (2026-10-04)

The default cartridge now starts under player control. QAOP or joystick 1 steers; Space/joystick fire shoots; B launches Sinibombs; R starts a fresh game from any state. Start with three lives and three bombs. Collecting a crystal grants three bombs, capped at 24. Destroyed planetoids respawn after 90 physics ticks. Assembly no longer grants free ammunition in playable mode. Replacement worker supply waits for an existing crystal to clear rather than overwriting it.

Twelve bomb hits win and freeze gameplay. Contact with an awakened Sinistar costs a life. Surviving players respawn at (8,152) with 180 ticks of protection, preserving ammo and damage to Sinistar. Zero lives ends the game. Native border feedback is blue for protection, green for victory, red for game over. The browser HUD reads native counters and displays instructions and restart status; it does not implement gameplay.

gameplay.asm adds mode/status at 782e/782f and lives/protection/rock-respawn/crystal-count at 7838-783b. The source-derived motion, mining, assembly and Sinibomb primitives remain; the lives, economy, contact boxes, respawn and victory rules are prototype adapters. Setting game_mode=0 in the diagnostic harness restores the old automatic fixture and its test-ammunition grant. Shared controls retain compatibility with the separate scene cartridge.

Final DCK SHA256: 3e2ffb8f1800b9c2c721f1f97c98024f11e5d9ba16543388e247ea2a3dc57234. Build ends at 9c00 within resident DOCK4. verify_playable.mjs checks default manual boot, movement/fire, mined crystal collection up to 24 bombs, no assembly grant, twelve-hit victory, frozen win state, native R restart, contact damage, protection and three-life loss. It uses controlled position/state setup for mining and encounters, then actual emulated keyboard input; this is not an unassisted human playthrough.

All regression reports match that cartridge hash: 197120 integrated mining-rule cases; baseline assembly 0..20 and full image/raster checks; control/overlap checks; player collection; twelve-hit destruction and post-target expiry; all 125 speech frames and 1625 AY register writes. Wrong/redundant display writes, ROM writes and raster mismatches are zero. Controls benchmark: 3293 published pictures across 15000 refreshes, peak publication 11387 T-states. Fuse checks 1023 render intervals over 3069 refreshes with SP=7fff. Browser boot and native lives/ammo HUD inspected. No physical hardware validation.

Saved as revisions/playable-v1, including cartridge, source, viewer, checks and speech assets. The fixed arena still has one worker/rock/projectile slot, scripted worker resupply, no warriors, camera/parallax, full worker AI, individual piece destruction or wave progression. Rendering remains below arcade speed. This is the first playable prototype of the integration scene, not a completed arcade port.

## Precomputed active-face renderer (2026-10-04)

Active Sinistar now uses a ROM atlas instead of runtime mask/bitmap shifts and sprite-buffer copies. There are thirty 728-byte poses: nine mouth/eye combinations at phase zero plus seven other X phases for each of the three shut-mouth eyebrow poses. Each row stores seven bitmap bytes followed by seven ECM attribute bytes. The independently composed result matches the previous geometry and palette approximation. Atlas banks 0, 1 and 7 leave resident code, stack, IM2 and both HOME shadow planes visible. Native code maps the selected bank, blits the prepared rows into shadow RAM with unrolled LDI, then restores mapping. The speech ISR restores the renderer's bank shadow as before.

This requires 21840 bytes of atlas. To fit the same seven-bank cartridge, player sprites now store five occupancy bytes and only their nontransparent triples (14168 bytes total versus 27648). Native code expands the selected sprite directly into the always-visible HOME 7c00-7c6b cache and reuses it until heading or fine-X phase changes. Assembly patches remain in D800 and generic staging remains B800 / DC80; the old 5800 shifted-face cache and resident 2048-byte rotate table are no longer used. Resident code ends at 9435.

Full face composition still precedes the rock, worker, crystal, shot, player and bomb, preserving overlap order. New full-face rectangles are marked dirty without being erased first; old rectangles are restored in shadow RAM. Clear loops update bitmap/attributes through separate pointers. The changed-byte compiler scans bitmap and attributes separately and emits through alternate HL instead of repeated IX stores. The ISR does not touch alternate registers. Screen publication still writes final changed bytes only, after interrupt synchronization. A more complex old-rectangle strip clear was measured and discarded because it did not improve the benchmark.

Final SHA256: 0d5f98ecf53ce814e810c23c7a8b694a7e2f688fa51a6d08d72536c23a3832b4.
profile_mining.mjs compares 500 active-face publications with the same programmed positions/phases against revisions/playable-v1/build. These are emulated CPU-time measurements, not browser wall-clock estimates:
- Before: 509240.60 T-states/picture, 6.928 pictures/sec.
- After: 239087.62 T-states/picture, 14.756 pictures/sec (2.13x).
The scripted benchmark overrides face position after awakening and exercises all horizontal phases; it is not a claim that every game situation has this rate. Changed-byte compilation and synchronization remain major costs. The 50-60 fps target is unmet.

Final regression reports all match the hash above. Controls: 4771 pictures / 15000 refreshes, 503 pursuit positions, 16 relocation probes, peak publication 9847 T-states. Baseline: 3367 / 9000. Player-only: 3299 / 3600. Full bitmap/attribute and raster comparisons pass with zero incorrect/redundant/ROM writes. All assembly stages, mouth/eye poses, 125 speech frames and 1625 AY writes pass. Twelve-hit destruction and post-destruction bomb expiry pass. All 197120 integrated mining-rule cases and playable win/loss/restart tests pass. Fuse confirms 1023 early execution intervals with SP=7fff; active rendering is tested end-to-end in TSRun, not physical hardware.

Saved as revisions/playable-fast-v1. Prior playable-v1 remains unchanged.

## Generated rendering kernels and publication templates (2026-10-04)

Build-generated width-specific comparison/emission kernels now cover spans of 1..32 bytes. Fall-through unrolled code removes the runtime per-cell loop and emitter call. Two aligned 256-byte tables supply the nonlinear scanline address bytes. Sprite art and the existing 30-pose shifted face atlas remain identical.

The build also supplies a five-byte publication instruction template (LD HL,address; LD (HL),value). Boot/restart expands it through E000..FFFD once. Each frame restores the preceding terminator opcode, fills only address/value operands, then inserts its new RET. Both fixed opcode bytes survive between frames. Overlap still resolves completely in HOME before changed-byte-only publication; no CPU clock increase or browser interpolation. Resident code ends at 99b4. Existing stack, banking and sprite memory allocation are retained.

Cartridge SHA256: 1870bf69b214f46809de00d6b13ffbe7331a74ba3f0ed7ed39a47bbffad30a41.
Same 500-picture active-face profile: 207332.87 T-states/picture, 17.016 pictures/sec versus 239087.62 / 14.756 before (15.3% faster). Frame gaps are 236 at three refreshes, 260 at four, and three at five. Compilation falls from 98742 to 87453 T-states on average. This remains uneven and below the requested arcade rate, not a completed smoothness fix.

Full-plane and raster regressions pass: baseline 3457 pictures/9000 refreshes; controls 4952/15000 with 539 pursuit positions and 17 relocation probes; player 3297/3600; bombs 7246/10000; expiry 7157/10000. Zero incorrect, redundant, ROM or raster writes. All 125 speech frames / 1625 AY writes pass, as do 197120 integrated mining cases and playable win/loss/restart tests. Peak tested publication is 9827 T-states. Fuse confirms 1023 early intervals over 3069 refreshes with SP=7fff. Physical hardware remains untested.

Saved as revisions/playable-precomputed-v2; previous saved revisions are unchanged.

## Native relative-transition fast path (2026-10-04)

Cartridge SHA256 c00d7e8bb4a7344401055548f7608455e8a5dc116702ff52ee830af7ae2b39b4. All eight 8 KB DOCK banks now carry ROM. DOCK3 is mapped only during interrupt-disabled startup, without stack or state access, to copy immutable transition chunks to HOME A000-A7FF, C300-C7FF, and 5900-5FFF. These lie outside the supported y=64..175 composition area. The common ship-triple dictionary occupies HOME C000-C2FC; 255 indices plus literal escapes reduce ship storage. The selected ship still expands into 7C00. Generic stage buffers remain B800 and DC80. Resident code ends at 9db4.

216 offline transitions cover three shut-mouth eyebrow poses, eight old X phases and dx/dy=-1..1. Old and new face ECM envelopes must be disjoint from every old/new other-object rectangle; speech must be finished and pose unchanged. Precomputed masks identify exactly which bitmap and attribute bytes change. Generated ROM kernels read the new prepared graphics and write only those cells, with no face screen comparisons. Forty-eight horizontal cases additionally use prepared five-byte records in shared four-row chunks. One direction reads boot-cached HOME chunks; the other reads DOCK5. Shared padded atlas rows reduce duplicate face data.

During a fast run, the face is omitted from shadow composition. The first fast frame removes the preceding shadow face; subsequent frames retain background there. All other objects remain composed. The ordinary changed-byte compiler excludes the direct-face envelope in both planes. A return to overlap, a larger displacement, a pose change, or speech restores normal composition. This is a bounded movement fast path, not a promise that every separated situation is currently accelerated.

Prepared publication records descend from HOME DB00, below DC80 staging. The normal stack is restored after preparation. Preparation is gated until speech has ended because the speech ISR maps DOCK6 over the temporary stack. Actual record playback disables interrupts for its bounded duration and restores SP, mapping and interrupts. An offline cost bound plus current sparse-publication size ensures completion before even the earliest face row is scanned; oversized work retries the composed path. No browser interpolation or CPU overclocking.

Same 500-picture mixed benchmark: 17.016 -> 17.574 fps; 200746 T-states/picture, gaps 2:51, 3:190, 4:255, 5:3. Separated-object sweep: 18.645 -> 22.987 fps; 153478 T-states/picture, 405 fast frames, gaps 2:272, 3:156, 4:62, 5:9. These are controlled emulator workloads, not guaranteed whole-game rates. Original 60 Hz target remains unmet.

Validation: all 216 transitions explicitly selected across X phases, eye poses, both directions and nonlinear Y boundaries; 432 entering/leaving overlap checks. Full bitmap/attributes, individual writes, ROM immutability and raster comparisons pass with zero errors. Transition suite peak publication 18921 T-states. Standard controls: 5051 pictures/15000 refreshes with 566 pursuit positions and 18 relocation probes. Baseline 3494/9000; player 3299/3600; bombs 7277/10000; expiry 7190/10000. Speech 125 frames/1625 AY writes, all 197120 mining cases, playable win/loss/restart and Fuse early execution checks pass. Physical hardware remains untested.

Saved as revisions/playable-transitions-v1 before adding further speech.


## Player-death speech and Sinibomb scream (2026-10-04)

Build 983a1c6d adds full archived I-am-Sinistar (135 AY frames) and AARGH (170 frames), converted with speech2ay harmonic3. Source URLs and hashes are in assets/i-am-sinistar.json and assets/sinistar-roar.json. All three streams use 6020 bytes of DOCK6; total ROM payload remains 64 KB.

Original WITT/SUBPART.SRC line 57 requests SPEAK 8 on every hit; WITT/DEATH.SRC line 60 requests SPEAK 1 after player death. The fixed-arena adapter now screams on actual Sinibomb collisions and requests I-am-Sinistar on contact death if speech is idle. New hits restart the scream, interrupting existing speech as permitted by WITT/ANISINI.SRC. The last audio frame is held until the next interrupt before silencing. The final hit uses the same scream recording. Individual piece removal, separate death-mouth behavior, and mouth animation for these two new clips remain pending.

Foreground publishes a single-byte request; ISR owns stream pointers. Both pending and active speech exclude the fast renderer's temporary D800 stack, which DOCK6 audio mapping would hide. Rendering continues using the composed path during speech.

Validation: verify_voices.mjs checks actual contact/bomb triggers and 5798 AY writes for full assembly/death clips and an interrupted/restarted scream (125,135,16,170 frames). The 16000-refresh transition regression passes 216 fast cases and 432 overlap fallbacks with zero incorrect, redundant, ROM or raster writes. The 10000-refresh bomb regression verifies 12 hits with speech and no rendering errors. Playable win/loss/restart/protection checks pass. This is emulator validation; physical hardware and subjective audio quality are unverified.

Saved as revisions/playable-voices-v1. Prior revisions remain unchanged.


## Effects, speech priority and arena gameplay (28f41d9b)

Four new effects are generated by scripts/prepare_sfx.py through speech2ay harmonic1: player shot, crystal pickup, assembly clang, Sinibomb launch. The source WAVs reconstruct GWAVE tables from SynaMax's VSNDRM9.ASM using the 894.886 kHz sound CPU clock documented by MAME. Waveform/pitch/decay data follow that source, but boundary timing is approximate and the assembly cue is shortened to 0.20 seconds. These are source-derived AY approximations, not exact arcade recordings. Explosion, player-death explosion, warrior and other effects remain pending.

Five audible registers per effect frame are cached in HOME 5C40..5E9C (605 bytes) from boot-only DOCK3. Muted B/C tone registers and unused envelope registers are omitted; B/C volumes are explicitly muted on SFX start. ISR playback uses no additional bank mapping, so SFX do not disable fast graphics. Speech preempts SFX and discards shooting requests while speech is pending/active. No delayed shot queue. Speech retains all three channels.

Playable mode now has horizontal planetoid drift (64..176), and a worker that approaches the planetoid, increases its vibration using the original numerical mining kernel, collects actual released crystals, delivers a piece, then respawns after a delay. No scripted crystal supply in playable mode. Diagnostic mode retains the old deterministic supply for graphics regression. Worker movement remains a simple one-pixel step; this is not yet the original multi-worker world AI.

A 64x16 arena scanner at the bottom of the screen shows player/rock/worker/Sinistar positions, updated every eight displayed pictures. A HOME 7E00..7E7F scratch buffer OR-composes markers (including overlaps) and publishes only changed bitmap bytes. The arena remains fixed, with one planetoid and worker. Scrolling-world radar, warriors, original world population and wave progression remain pending.

Corrected destruction threshold to 13 hits in rules, bomb tracking, pursuit, graphics and UI; 20 assembly pieces unchanged. Individual pieces still do not disappear per hit.

Validation: verify_world.mjs verified autonomous 20-piece assembly without supplied crystals, 113 planetoid positions, 501 scanner checks, 4012 independently composed arena pictures, 14520 SFX register writes, and seven actual shot events during speech without interference. verify_voices.mjs retained full exact speech stream checks. Native win/loss/restart/protection checks pass, including 13-hit victory. Both 216 fast movement transitions/432 overlap fallbacks and a 13-hit bomb scenario pass with zero bitmap/attribute/raster/ROM write errors. Physical hardware and subjective sound fidelity remain unverified.

Saved as revisions/playable-world-sfx-v1; previous revisions are unchanged. Cartridge SHA256: 28f41d9b47445e63fd40e7ef7da044b27455af76e6548ca044f4903cd47ca33a.


## Top scanner and scaled arcade planetoid velocities (a13f745f)

Scanner moved to the top center (x=96..159, y=0..15). Player is fixed at local (32,8); other positions are player-relative at 1/8 horizontal and 1/16 vertical scale. Four blue corners mark the current fixed playfield. Marker attributes: player bright white (cream approximation), worker red (burgundy approximation), planetoid cyan (distinct substitute for dark grey), Sinistar bright yellow. Shapes are 1/2/3 bits; masks are clipped within their byte. On an attribute collision, a non-player marker moves down one scanline; crowded overlaps may still share a color. This is a deliberate ECM adaptation, not pixel-identical arcade radar.

335-ish bytes of scanner code occupy the previously unused ROM7 tail at FE00. The resident wrapper maintains the ISR bank shadow and restores DOCK4-only mapping. HOME 7E00..7EFF holds bitmap/attributes. Scanner preparation runs at most once per eight display ticks, compares the buffer against the screen, and emits address/value records at 5EA0, after the sound cache. At the next main publication the short list is written before the top scanlines are fetched. No scanner wait loop, full-screen redraw or runtime graphic shifting. Fast-path timing reserves another 2500 T-states for this publication. Test maximum is 24 changed bytes; preparation maximum 27407 T-states, publication is bounded separately by the record count. The separated-object diagnostic remains 22.95 pictures/sec (scanner disabled in this diagnostic); this is not a whole-game or 60fps claim.

SCIVELT is now read from original SAM/SAMTABLE.SRC at build time. SAM/SCANNER.SRC FINON converts velocities to S/2 and L/4 pixels/tick. Our explicit arena adaptation scales horizontal by 256/304 and vertical by 112/256, giving signed increments 108/256 X and 28/256 Y per physics tick (vertical sign reversed for top-down coordinates). All nine directions, including stationary, are retained; a regenerated planetoid advances through the table. Arena-edge wrapping substitutes for original off-screen world travel. Fractional positions are retained. Rendering dirtiness now includes Y movement, and gameplay tests aim relative to the moving planetoid.

Validation: all nine choices and 6154 movement steps matched an independent source-table model; 915 scanner snapshots and 1128 changed writes matched bitmap and attributes, all publications before the scanner raster. 2978 arena pictures matched independent composition. Autonomous 20-piece assembly, speech priority, native win/loss/restart/protection and 216 fast transitions/432 overlap fallbacks passed. Physical hardware remains untested. Saved as revisions/playable-top-scanner-v1; prior revisions unchanged.

SHA256 a13f745f345b7f290910c4b55653ff8f7e98b00e85ad6738e2147b406bc13de4


## Native title and persistent planetoid edge clipping (866433c4)

The native title decodes MARKEY from original MICA/MARQUEE.SRC and the
variable-width small glyphs from SAM/MESSAGE.SRC. The red logo retains its
171 original columns and original odd-run padding rule. Layout is adapted to
256x192, with copyright wording and a cartridge-specific fire prompt.
Space or joystick fire begins play; R still restarts gameplay directly. This is
a title screen, not the complete arcade coin/high-score/attract sequence.

Startup-only initialization now loads from DOCK3 into HOME B800 before gameplay.
That area becomes sprite staging afterward. The native title is compressed;
neither title decoding nor startup relocation adds per-frame work.

Removed planetoid teleports at X=8/208 and Y=72/136. Fractional coordinates now
persist modulo a 512x512 domain (high bits 586E/586F). Rendering clips pre-shifted
cells at x=0..255 and y=64..175; partially visible rows/columns are packed only
on the edge path. Full-sprite drawing and the Sinistar transition atlas remain.
Offscreen objects retain mass and identity. The scanner includes the ninth X bit;
its current vertical scale wraps that extra Y bit naturally.

**Not yet a scrolling-world conversion:** the player and Sinistar remain in the
fixed viewport, and the worker/vibration adapter pauses when the planetoid leaves
its supported mining bounds. Camera-relative coordinates for all actors and
continuous offscreen worker simulation remain necessary. Previous adapted
planetoid speeds (108/256 X, 28/256 Y per tick) are unchanged, not newly verified
as arcade pixel speeds. Source FINON coordinates also require care about packed
vertical pixels when establishing final world-to-screen scale.

Original SAM/IRQ.SRC scrolls STARRY using camera position differences from SSPOS
and SLPOS, suppresses stars over occupied pixels and wraps stars at display
edges. It applies one common displacement to the stars; this reading does not
establish multiple independent parallax-depth layers. Gameplay still needs that
camera-driven starfield; the saved scripted demo has its own background.

Sinistar speed is **not certified arcade-correct**. STBLSINI/VELOCITY/CHASE
numerical kernels are present, but mining-pursuit.asm rescales distances,
doubles X speed, clamps to the viewport and omits SINI.SRC orbit, stop/stun and
sector behavior. A 60 Hz physics schedule does not mean 60 rendered pictures/s.
No arbitrary multiplier has been applied as a substitute for that port work.

Validation: native title and keyboard start; 238 independently composed clipped
positions; 216 fast transitions and 432 overlap fallbacks without incorrect,
redundant, ROM or raster writes; complete speech and interrupted/restarted roar;
earned-ammo 13-hit victory, loss, protection and restart. The separated-object
500-picture diagnostic measures 22.15 pictures/s (scanner disabled); it is not
a whole-game benchmark or a 60fps claim. Physical hardware remains untested.

Cartridge SHA256: 866433c4813868627912a04b3ef10597c9eeabb8d76bae97d0e0b5f4bcd61daf


## Banked world code, lossless speech and Sinistar timing (6a22a273)

Speech storage is reduced from 6020 to 3010 bytes without resynthesis or sample
truncation. Each frame packs period low bytes R0/R2/R4, paired nibbles
R1/R3, R5/R8, R9/R10, and mixer R7. Constants R6=5, R11=1, R12=0 and
R13=255 are checked for every input frame at build time. Native code reconstructs
R0..R12 at HOME 5874..5880 and emits all thirteen original values each tick.
R13 remains unwritten, exactly as the original streams request.

DOCK6 now reserves 2048 bytes for world code; 582 are used by planetoid motion,
worker approach, visibility checks, speech unpacking, Sinistar pursuit and its
bomb-hit response. Resident calls maintain the bank shadow used by the ISR and
restore DOCK4-only mapping before returning. This frees the main code bank to
215 bytes of headroom and leaves 1466 bytes in the world-code reservation. No
runtime code writes to ROM and no new cartridge banks beyond the existing 64K.

Source FALS/N1ALL.SRC SiniPa schedules Sini on Task8. WITT/THINK.SRC explicitly
allows thinking every scheduled invocation when on screen (the older Task16
comment in SINI.SRC does not describe this on-screen case). Playable mode now
updates chase velocities once per eight physics ticks and integrates the held
velocity every tick. Diagnostic mode retains its existing per-tick fixture.

WITT/SUBPART.SRC halves signed screen velocities on a damaging bomb hit;
WITT/COLLISIO.SRC SBOMB,SINI adds two to InStun. SINI.SRC decrements that byte on
a decision tick, then SiStopChk zeros velocities if stun remains nonzero. These
rules, including byte wrap and arithmetic negative shifts, are now ported. Player
contact clears stun and velocities as in the eating sequence, though the full
arcade eating animation is still unported. R restarts with clear phase/stun state.

The new test verifies 225 signed hit cases, all eight initial decision phases,
1536 physics ticks and repeated-hit recovery against an independent integer
model. Bank mapping and stack balance are checked after each native call. Full
speech tests verify all original register values through complete clips and
interrupted/restarted roars. Native title, 238 edge positions, 216 fast
transitions, 432 overlap fallbacks, earned-ammo victory, loss and restart pass.
Separated-object rendering measures 22.11 pictures/s versus 22.15 in the prior
revision; this diagnostic disables the scanner and is not a whole-game rate.

Camera scrolling, world-space actor interactions, continuous offscreen workers,
the camera-driven starfield and Sinistar orbit/sector behavior remain pending.
This iteration resolves a code-space constraint and an original pursuit timing
mismatch; it does not enable camera scrolling or establish complete arcade
speed fidelity. WITT/VELOCITY.SRC confirms that doubling the short-axis desired
velocity is intentional in the original, not itself evidence of a port bug.

SHA256: 6a22a2739f0f8f4786f53cdf973c64cde3fd83e7cf5c2fae64991cb242165b4b

Long-run validation also passes autonomous 20-piece assembly, 39041 movement
checks, 16974 independent composed pictures, 4535 scanner snapshots and speech
priority under shooting. Saved as revisions/playable-banked-world-v1.
