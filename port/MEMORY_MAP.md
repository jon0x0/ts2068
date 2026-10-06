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

# Current v6 additions

- HOME 5B00–5B98: previous nine-byte projections for 17 secondary planetoids. 5BA0–5BB0: changed flags. Used only with HOME2 visible by world/render dispatch; compiled rock code receives its flag in 78E4 before DOCK2 is mapped.
- HOME 7BB0/2/4: saved compiler SP, packed-list start, saved publisher SP. 7BBC–7BBE: RAM jump thunk for fixed-width comparisons. 7BC0–7BC7: compiler row/span state. 7BD0/1: pending left span for direct-face exclusion.
- HOME 7BE0–7BE2: width-selected clear-kernel jump. 7BE3–7BE5: normal/dirty-row planetoid jump. IM2 trampoline 7B7B is unaffected.
- HOME E000–FFFD: descending four-byte publication records (flags, value, destination low/high), initially SP=FFFE. Compiler and publisher restore the ordinary stack; IRQs use free/consumed record space. The regression trace peaks at 2,600 record bytes and asserts at least 512 bytes of lower headroom. 78F0 now encodes E000 + seven timing-budget units per record, not an executable code end pointer.
- The legacy boot template fill is harmless but no longer used for publication. The failed gap-tracking experiments are absent from this cartridge.
- DOCK2 also holds the 16-byte compiled-rock phase pointer table. No cartridge chunk is written at runtime.

Historical contracts below describe earlier milestones.

# Initial port memory contract



Milestone 0 is a native Z80 movement-kernel diagnostic, not the finished game.



No original 6809 code is executed; reviewed routines are translated to Z80.



| Chunk | Address | DOCK contents | CPU visibility / writable HOME use |



|---|---|---|---|



| 0 | 0000–1FFF | absent | HOME ROM; untouched |



| 1 | 2000–3FFF | absent | HOME ROM; untouched |



| 2 | 4000–5FFF | absent | HOME RAM bitmap |



| 3 | 6000–7FFF | absent | HOME ECM attributes; state 7800–781F; IM2 7A00–7B00, trampoline 7B7B; stack below 7FFF |



| 4 | 8000–9FFF | resident header/code/tables, read-only | DOCK throughout execution |



| 5 | A000–BFFF | absent | HOME RAM, reserved for future object storage |



| 6 | C000–DFFF | absent | HOME RAM, reserved |



| 7 | E000–FFFF | absent | HOME RAM, reserved |



HSR=$10, DECR=$02 throughout runtime, with software shadows at $7804/$7805.



Startup writes both ports under DI; no later bank transitions or ROM calls.



IM2 ISR and routines execute in DOCK4, vector and stack always HOME.



A sparse ROM-only DCK and a padded 64 KiB physical image are built separately.



No physical hardware validation yet. Boot diagnostic results live at $7800



(status $A5=passed, $EE=failed), $7801 (stage), $7802 (16-bit IRQ count).



## Flight scene milestone



`flight.asm` uses the same DOCK4 resident code and HOME3 state/stack/IM2.



DOCK0/1/5/6 store pre-shifted player sprites. A selected 108-byte sprite is



copied to HOME $7C00 with HSR $11/$12/$30/$50, then HSR returns to $10



before composition. ISR executes only EI/RETI from resident DOCK4, changes no general registers,



and never accesses a mapped data chunk. Software mapping shadow is $7804.



HOME5 $A000–B7FF = composed bitmap; HOME6 $C000–D7FF = composed attributes;



HOME7 $E000–F7FF = static star bitmap. All three use display scanline layout.



The background and final sprite are composed before either old/new rectangle



is committed. No visible erase pass. Only nonzero XOR differences are written.



State $7820–783F holds position/velocity/angle, old and new rectangle, frame



counter. Screen-space wrapping is an explicit bring-up adapter, not arcade SCROLL.



## Camera/star milestone



Player state moves to two eight-byte records at $7860 (long) and $7870



(short): position16, velocity16, camera velocity16, unit8, axis8. Original



arcade coordinates are retained. Display x=short.high, y=152-long.high.



Camera positions are 24-bit little-endian at $7880/$7883. Star rounded previous



camera bytes are $7886/$7887; current deltas $7888/$7889. Ten five-byte star



records (x,y,bitmap offset16,mask) occupy $7D00–7D31. Twenty dirty bitmap



addresses occupy $7D80–7DA7. HOME7 bitmap becomes dynamic background.



The source-derived common-camera star movement replaces the static backdrop.



No star DMA/PIA code is reused: Z80 builds final dirty cells before publication.



## Optimized pursuit renderer



DOCK4 holds resident code. Executable Sinistar phase blitters occupy DOCK0/1/2;

DOCK7 includes the 1,024-byte pursuit lookup, indexing resident velocity tuples.

Player phase data uses remaining ROM space in DOCK0/1/2/5/6/7; this build has no

DOCK3 player spill. DOCK3 stores compressed relative transition data, copied at

startup into HOME $E000–EAFF, $B940–BFFF, and $D800–DFFF. These caches do not

overlap the shadows, old stars, player staging, or generated publication lists.

DOCK3 is not mapped during animation. The generated erase routine is banked ROM,

called through the same HOME stub as the phase blitters.



HOME $A000–B7FF and $C000–D7FF hold final bitmap/attribute planes.

Player sprites stage at $B800; DOCK5 sources first pass through $7C00.

The previous ten star records are copied to $B900–B931 before updating $7E00–7E31.



HOME $EB00–EFFF holds threaded publication records: handler word, display address,

and shadow address, followed by the normal-stack restoration handler. There can

be at most 192 sprite rows plus 20 star cells: 1,274 bytes including the terminator,

which fits before $F000. The measured maximum is 464 bytes. During publication SP

walks this list; ISR pushes and row subroutine calls reuse already-consumed words.

The usual HOME3 stack pointer is saved at $78B6 and restored before frame_done.



HOME $F000–FFFF holds fallback final-byte store code (five bytes per write plus

RET). Its row capacity check stops before starting a row at or above $FE00,

leaving room for 320 bytes. The measured maximum is 2,156 bytes. The code and

threaded records execute only with HSR=$10; no cartridge ROM is modified.



Dirty row bounds ($7900–79BF and $7D00–7DBF) are used for separated rectangles and

the fallback compiler. Scalar bitmap/color bounds and budget scratch use

$78C0–78D5. Pursuit state and rectangles remain at $7890–78AF. RAM jump stubs at

$7B80 (unrolled row loop), $7B83 (next Sinistar row), and $7B86 (ROM blitter) are

initialized under DI. IM2 remains in HOME3. The ISR preserves AF and leaves the

main/alternate general registers untouched.



## Separated-sprite fast path



$78D6 selects the independent sprite path. $78DA/$78DC hold its publication

budget and current row cost. $78E0–E3 and $78E4–E7 hold the two swept byte-cell

rectangles (min x, max x exclusive, min y, max y exclusive). Each is limited to

10 bytes by 64 rows for this path; larger or intersecting envelopes retain the

shared renderer. Its list has at most 148 records (20 stars plus two 64-row

rectangles), fitting below $F000. Actual masks/attributes are still composed in

HOME before publication. Its sparse attribute-only program occupies $F000 and

runs before the independent bitmap list; a build assertion bounds the maximum

number of non-default old/new sprite attributes so that this program fits.



## Relative transition cache



$78ED marks a valid relative transition, $78EE holds the previous face pixel

phase. $78F0/$78F2 hold relocated color/bitmap stream pointers, $78F4 the bitmap

base byte x, $78F5 the current bitmap y, and $78F6 the run length.

The 72 resident pointer pairs select old-phase × dy × dx entries for -1..1 moves.

Colors encode row offsets and eight-bit cell masks relative to the old origin;

bitmaps encode run lengths and packed start/width spans. Final values always

come from the completed shadow image. Color streams omit unchanged cells;

bitmap handlers compare before writing. All unused movement cases use the

existing renderer. See relative-verification.json for relocated execution tests.



## Sinistar stop states



HOME $78A0 holds InStun, $78A1 the dying flag, $78A2 the attract flag, and

$78A3 the adapter's current screen-presence flag. Startup clears these with the

existing state block. Stop-state code is resident DOCK4 and introduces no bank

switches. Both 16-bit pursuit velocities are cleared on stop; camera displacement

still applies. The demo event sets only InStun; other flags are covered by the

assembled-code verifier. No new chunk, display, stack, or interrupt mapping.



## Input and mining kernels



For the current playable scrolling cartridge, additional HOME state is at

5884–588B (camera/current-previous), 5891–5896 (world counters), 58B4–58BD

(one secondary planetoid), 58C0–58E7 (current/previous stars), 58ED–58F4

(scanner/population scratch), 7C84–7C8D (saved primary clipping state),

7C90–7CBD (world high bits, saved and projected coordinates), 7CD0–7CEB

(sprite clipping), 7CEC–7CEF (last secondary rectangle), 79B0–79FF and

7DB0–7DFF (sixteen planetoid records), and 7D00–7D3F (previous rectangles).

The BC80–BD18 picture cache follows the B800–BC43 assembly staging area and

precedes the BE00 compressed bank-transfer scratch. The scanner now runs

from the DOCK6 extension, preserving DOCK7 space for graphics. See

SCROLLING.md; the older flight/pursuit assignments below remain historical.



HOME $78A4 is the sticky manual-control mode; $78A5 is thrust demand (0/127).

Both are cleared by the existing startup state reset. Input code is resident

DOCK4, reads keyboard port $FE and joystick 1 via AY register 14, and changes

no memory banks. AY register 7 is initialized to $3F. Future speech must preserve

port A's input direction and account for the register latch changed by input.

Mining kernels are register-only routines in the separate diagnostic cartridge;

they allocate no object RAM and are not linked into the pursuit renderer yet.

# Composition/endings revision addition



HOME `$5897` is the native end-screen latch: 0 undrawn, 1 waiting for fire release, 2 ready for a fresh press. World vector `world_extension+96` draws the result once in live bitmap/ECM rows 24–46 and handles restart. It does not write the shadow-cache area beneath that reserved band.



## Compiled planetoid revision 93b7974f



DOCK2 contains 7,341 bytes of row programs and phase pointers. HSR 14 maps this source/code bank during shadow composition; DOCK4, HOME stack and both shadow planes remain visible. Live bitmap reads are deferred until HSR returns to 10. Raw clipped-rock phases occupy HOME A000–A68F (phases 0–3), C300–C7EB (4–6), and 5900–5AA3 (7), copied at boot from DOCK3. These replace the horizontal transition caches; no remaining runtime path reads those old templates. SFX at 5C40 and dictionary at C000 remain separate. Resident end_code is 9F47; world code is 4,630 of 4,750 bytes.


## Incremental overlap revision bf381583

DOCK2 5CAD reserves 768 bytes for the incremental renderer, assembled from incremental.asm. It maps alongside resident DOCK4 (and atlas banks 0/1/7 when needed). Scratch HOME 7BA0–7BAB stays visible: restoration flag, retained-face flag, temporary strip rectangle, copy width and intersection bounds. HOME 58xx is deliberately not used by this helper because DOCK2 hides it. The helper restores the previous mapping and leaves interrupts enabled. IM2 ends at 7B00, with its trampoline at 7B7B; scratch does not overlap either.


## v16 HOME helpers and visibility state

Boot copies home-render.bin from the checked tail of DOCK3 to HOME A690–A7FF, after raw rock cache A000–A68F and before playfield shadow A800. The builder asserts that both the HOME allocation and boot-bank gap fit. Helpers execute with the caller's bank mapping; population preparation calls world-bank routines only with DOCK6 visible. Clear/draw wrappers use the existing world_call trampoline.

HOME 5BCA: current-or-previous secondary visibility; 5BCB: diagnostic rendering bits (bit 0 omit fully covered player, bit 1 hide covered stars; default 2); 5BCC: changed-eye flag; 5BCD: previous projected population visibility; 5BCE: any remaining secondary mass, including offscreen. These extend mode state, before SFX cache 5C40. Reinitialization clears all flags before setting default policy 2.


## v18 assembly cache

HOME 8000-9FFF holds two 4096-byte phase sets under resident DOCK4. Each of eight 512-byte slots contains 364 bitmap bytes and 137 packed color bytes. HOME 5BD0-5BEF holds cache state, BF80-BF94 a raw row, and DE00-DF6B the decoded current palette. DOCK3 6D20 reserves 1792 bytes for banked cache code. Raw rock boot data is packed into 3360 bytes without changing its HOME destinations. Builder assertions protect cache code, palette scratch and bank capacities. DI banked calls restore both stack and bank mapping. HOME 7BAC records an oversized-publication retry, preserving its original dirty spans. See ASSEMBLY_CACHE.md.


## v19 assembly transparency

Each HOME 8000/9000 cache set now uses 4056 bytes: bitmaps +0 (2912 bytes), base masks +2912, normalized colors +3276, selected-phase masks +3640, row-overlap flags +4004. Each latter plane is 364 bytes except the 52 flags. HOME DE00-DF6B colors remain; DF70-DFFE adds boot-copied preparation/draw/clipped-player helpers. BE00-BE33 and BE40-BE73 temporarily snapshot dirty limits after object drawing. Low state extends through 5C23, including star visibility at 5C00/02/.../12; SFX begins 5C40. BF80 row scratch and BFC0 rotate stub are used only during preparation, before subsequent sprite staging. See ASSEMBLY_CACHE.md for lifecycle and banking.


## v20 mask cache override

The earlier assembly-cache layout is superseded by ASSEMBLY_CACHE.md. Each HOME 4 KB set contains 2856 bitmap bytes, 52 overlap flags, 364 mask-pattern indices, and 800 pattern bytes. DE00–DF6B stores front colors; BF00–BF63 retains the current phase lookup until source staging invalidates it; BF80–BF86 is row scratch. Pattern interning uses 5C14–5C23. The renderer extension reserves 1024 bytes. Shared compiled-rock tails save 1167 ROM bytes.
