## v41: standalone initials, black victory text, repeat fire

Initials entry now clears to its own black screen, with a centered heading, double-size initials at y88, and keyboard instructions below. O/P or joystick up/down select; Enter/Space/fire confirms. Each new slot inherits the last confirmed letter. Both score tables retain the completed initials. Native tests verify BCC carry-forward, table ordering, session retention and controls. Captured entry screen contains no unrelated text; entry and victory text have normal-black paper with BRIGHT off.

Held-fire gap: the single projectile slot previously remained occupied for 60 physics ticks, including while offscreen. Lifetime is now 24 ticks, allowing ~2.5 shots/sec when uninterrupted versus ~1/sec. This also reduces unobstructed range from about 238 to 95 pixels at full cardinal bullet speed. One active player projectile remains a limitation; a true independent multi-shot pool is not implemented. Native held-Space test verifies 13 evenly spaced launches over 300 ticks; speech priority unchanged. Full mining/earned-bombs/win/restart/life-loss regression passes.

Original player death audio checked: source QPLDIE requests GUNSHOT then C4NNON (a longer FNOISE variant). No additional original audio stream was fitted. Effects bank remains full, title block has 39 bytes left, world block 19 bytes, resident block 15 bytes; these small non-contiguous gaps are insufficient for another stream plus its scheduling path without repacking. Existing reused explosion audio remains.

## v40: protected instruction layout

Attract instruction lines now start at y28,37,46; B-launch prompt starts at y56 and ends at y61, above the y63 divider and y64 playfield. Instruction transitions clear only y24..62. Original wording and normal-black attributes retained. Native attract test verifies bitmap and attributes remain identical across 359 published pictures, phase by phase. No per-frame text redraw introduced.

## v39: instruction background black

Removed BRIGHT from yellow/red attract instruction attributes and the white B-launch prompt. ECM shares BRIGHT between ink and paper; normal ink keeps the instruction paper consistent with surrounding black. Native frontend tests pass; all three captured instruction pages verified for black PAPER and BRIGHT off.

## v38: parallel radar upper fins

Adjusted only the static cap bitmap: its diagonal edges now advance four pixels per scanline, matching the side fins and meeting the radar top corners. Filled area above remains. No code-size or runtime-cost change. Native frontend test passes; rendered screen visually checked.

## v37: native Sinibomb inventory

White B and two digits below the live score (y10..14). Reads actual bombs inventory every 16 physics ticks and redraws only on change. Tests cover 3, 2, 0, 9, 10, and 24, plus no writes when unchanged. HOME 7BFE caches the count; 7BFF is reserved initialization padding. Reuses the HUD digit renderer; compresses repeated chevron rows and removes the obsolete standalone-help wrapper to fit the 64KB cartridge. Current attract instructions are unchanged. Effects bank now occupies all 8192 bytes.

## v36: reference-style radar surround

Four blue diagonal fins flank the scanner, with a filled tapered cap above. Native scanner content moves from y0..15 to y8..23; its world projection is unchanged. The trim occupies x80..175, y0..23 and is drawn once. Score and y63 divider remain unchanged. No ongoing drawing cost for the surround. Native HUD and frontend tests pass; rendered output visually checked.

## v35: worker harassment and destruction sequences

See [WORKERS_DEATHS.md](WORKERS_DEATHS.md) for behavior, memory, tests, and remaining adaptations. Single worker retained in normal and fast modes.

## v34: arcade victory message

Original MICA/STATUS.SRC wording, centered white in the reserved band. Drawn once on victory; existing three-second score-entry/title transition retained. Native frontend tests cover victory, loss, score insertion, audio, and attract; zero ROM writes. Effects bank 8097/8192 bytes.

## v33: native radar trim and live score

Adds mirrored blue ribbed wedges beside the 64x16 radar and a blue divider at y63, above the y64..175 playfield. This is a compact TS2068 adaptation of the arcade frame, not pixel-identical arcade artwork. Static trim is initialized once; attract instruction transitions restore the divider.

The six-digit white score at the upper left shares the high-score calculation: worker 150, collected crystal 200, outer piece 500, face 15000. Existing omission: five-point mining awards are not yet accumulated. Poll every 16 physics ticks; write only changed scores (60 bitmap/attribute bytes). No playfield compose work is added. HOME 7BF9..7BFA stores the cached score. Effects ROM uses 8002/8192 bytes.

Measured native HUD cost: 65 T on skipped ticks, 330 T for an unchanged zero score, 4684 T for the 2050-point update. Typical idle overhead is 0.14% CPU; even the 76000-point unchanged fixture costs about 0.94% averaged over its 16-tick polling interval. Initial trim/score costs 12660 T once. Full fast-mode stress: 3627 pictures/18000 refreshes, no late raster writes or ROM writes (v32: 3621 pictures; cadence varies, not a claimed speedup).

Original worker behavior: WITT/WORKER.SRC intercepts targets to collect crystals or ram the player; its EVADE routine targets the player when it has nothing else to do. The current serialized one-worker adaptation and speed are preserved. Multi-worker harassment is not added in v33.

# Current: attract audio and sound control v32

Attract audio now follows the arcade silent-demo rule. Workers approach from four sides with the delivery delay. **S** toggles native sound; the browser has a matching ON/OFF button. See [ATTRACT.md](ATTRACT.md) for source evidence, memory details and tests.

---

# Current: arcade attract and scores v31

The attract player now mines, collects, watches worker assembly and bombs Sinistar. The original instructions appear over gameplay, including an explicit B Sinibomb reminder. Both 30-entry arcade score tables are seeded and editable in RAM. Original title and edited roar are preserved. See [ATTRACT.md](ATTRACT.md) for sources, adaptations, memory changes and current verification.

The sections below record earlier revisions.

---

# Sinistar TS2068 port - scrolling flight

## Attract mode and session high scores — v30

The existing title bitmap is unchanged. Native Z80 code cycles title (about 8 seconds), three-score table (8 seconds), three instruction pages (about 10 seconds each), then 30 seconds of automated gameplay. Fire/Space/Enter starts a fresh real game from the idle screens or demo. Demonstration play is invulnerable and excluded from scoring. This is a scripted port demo, not the complete arcade attract AI. The original sequence audit is below.

Instruction wording comes directly from MICA/ATTMSGS.SRC, reflowed onto the smaller display. Yellow instructions and red SINISTAR/RUN emphasis match the source intent; the glyphs come from SAM/MESSAGE.SRC. Separate white lines describe the port controls. The original title pixels remain exact.

The three highest completed-game scores retain three initials in RAM. O/P selects backward/forward with A/Z wrap; Enter, Space, or joystick fire confirms each letter. Native TS2068 joystick 1 also supplies up/down selection, gameplay direction/fire, and start. B remains the Sinibomb key on the single-fire-button interface. There is no localStorage, browser score file, or cartridge nonvolatile save. Reload/power-off loses the session table; a new game preserves it.

Current scoring covers implemented worker kills (150), collected crystals (200), twelve outer pieces (500 each), and final destruction (15000), derived at game completion. The viewer displays the same current total; a native in-game score HUD, the arcade's planetoid 5-point awards, larger tables, initials timeout/repeat, warriors, and wave progression remain pending. Instructions and demo run only outside real play; the live per-tick addition is a small mode/result gate. Names advance once per press.

Native tests cover exact title preservation; all instruction pages; a complete demo-to-title cycle; starting with joystick fire; gameplay joystick direction/fire; O/P wrap, Enter, Space and joystick initials; descending insertion and name/score pairing; RAM retention; no ROM writes. Previous versions are preserved. See build/frontend-verification.json for this cartridge's results.



## Saved editor roar — v29

The current `sinistar-roar-edited.json` and matching register export are now the game roar. All saved download copies matched. JSON compilation reproduces the 2,380 exported bytes exactly (SHA-256 `f1ceb6f33b83fffd759be5b88cbff47c3cf21a4930f3480c849967910185612d`). No new optimizer pass or pitch changes were applied.

All 170 frames, including R13 envelope restart/skip values, are stored losslessly and play at the native refresh rate (about 2.83 seconds). Repeated hits do not restart the roar. The existing 12-refresh bomb burst temporarily takes channel C and the shared noise period; A/B routing is preserved. Outside that brief mix, playback matches the export exactly. Shooting remains subordinate to speech.

The cartridge remains 64 KB. Roar frame deltas take 1,284 bytes. A boot-only dictionary reduces the eight planetoid caches from 3,360 to 1,750 bytes and restores exactly the same graphics before gameplay. No runtime graphics decompression was added.

Validation: all 951 speech frames and envelope writes pass; native repeated bomb hits complete two 170-frame roars; all eight boot graphics caches match; 18,000-refresh fast-mode stress has zero ROM writes or late raster writes; mining, win, restart, contact damage and loss pass. Worst measured speech tick is 3,591 T-states (about 1.02 ms) with the impact mix. Physical hardware has not been tested.

## Sinistar loses pieces — v27

Sinibombs now remove the twelve outer pieces in the arcade source's reverse construction order, leaving the animated face for the thirteenth hit. Original impact explosions and roars remain active. See [DAMAGE.md](DAMAGE.md) for the captured sequence, rendering cost, tests and remaining collision/fragment adaptations.


## Original explosions and visible bombs — v26

Original IEXPLO artwork now animates for worker deaths and bomb impacts. The blocking Sinistar halo is removed; bomb impacts animate independently in the buffered renderer. Bombs use brighter colors and survive until at least one picture is published. Pending/active SFX now excludes the fast renderer's temporary bank-sensitive stack, fixing a reproduced bomb-flight freeze. C and F retain their toggle behavior. See [EXPLOSIONS.md](EXPLOSIONS.md) for before/after results and the remaining single-live-bomb limitation.


## Arcade taunts — v25

All eight complete voice recordings now play through AY speech2ay, with original Task64 chance checks, weighted selection, speech priority and mouth sequences. “Run, coward!” and “Run! Run! Run!” are both enabled. C still toggles bounce; F toggles fast mode. See [TAUNTS.md](TAUNTS.md) for source rules, validation, memory changes, performance and the remaining single-sector world adaptation.


## Bounce toggle - v24

Press **C** to turn planetoid bounce off or on. It starts on and resets to on when restarting. A native BOUNCE OFF / BOUNCE ON notice appears for about 1.5 seconds. The key is edge-triggered: holding it does not toggle repeatedly. Disabling bounce also clears the short rebound steering lockout. Both primary and secondary planetoids honor the setting; Sinistar contact damage is unchanged.

The check runs before mapping the collision-helper bank, so disabled bounce skips the contact calculation. Native tests verify press/hold/release behavior, both planetoid paths, restored reflection, notice pixels and attributes, expiry, and existing fast-mode notices. Keyboard forwarding includes C.

## Firing audio response - v23

The worker/planetoid explosion previously blocked shot effects throughout its 189-refresh tail. Shooting may now interrupt that tail after the first ten refreshes (about 0.17 seconds). A pending explosion still starts, other event effects keep their priority, and pending/active Sinistar speech still suppresses shooting unconditionally. The improved v22 noise-based explosion remains intact when uninterrupted.

This fixes missing firing sounds, not projectile density: native execution of both v21 and this version launches shots at ticks 0, 60, 120, 180 and 240 when no shot hits anything. The port still has one live projectile; a hit permits the next shot immediately. Multiple concurrent shots remain needed for an arcade-style stream in open space. The original SAM/PLSHOOT.SRC allocates a new shot object independently; this port does not yet implement that pool.

`verify_firing.mjs` compares the saved v21 cartridge with the current cartridge, checks the sound suppression interval falls from 190 to 10 refreshes, and verifies all three speech gates, other event priorities and explosion-to-shot timing. Native AY register playback and the full fast-mode game lifecycle also pass. Graphics and projectile motion are unchanged.

## Explosion audio revision - v22

Worker/planetoid QBANG playback now uses a noise-aware speech2ay/Ayumi fit. The v21 speech-oriented conversion selected a pitched tone in 188 of 189 frames; the new fit keeps AY noise enabled and selects noise period, volume and optional tone gating against the reconstructed source spectrum. It fits three-refresh blocks directly, matching the actual playback cadence.

This remains a source-derived approximation, not a recording of the arcade sound board. The source WAV is unchanged. Comparison previews use the same gain and modeled AY output filter; listen to audio/index.html in the saved v22 revision. Objective fitting scores are not a substitute for listening.

Only 183 ROM data bytes change from v21. Executable code, three-byte register format, 552-byte effects cache and playback cadence are unchanged. Other effects and speech remain byte-identical. Audio/register tests (including the high-RAM interrupt stack and speech priority) and the full playable lifecycle pass.

Offline regeneration: python port/scripts/prepare_explosion_sfx.py now runs fit_explosion_noise.py, using the installed speech2ay toolkit, Ayumi sources and GCC. Rebuild with python port/scripts/build_mining.py. The preserved v21 revision retains the prior sound for comparison.


## Worker combat and movement checkpoint — v21

V20 is checked in locally as commit `9c52e75`, tag `playable-mask-cache-v20`. Its saved viewer and cartridge are unchanged. V21 retains the assembly mask cache and adds:

- Player shots destroy workers, release carried crystals, award 150 points to the internal worker-score counter, and produce an expanding eight-fragment explosion. The adapted replacement worker respawns after three seconds, including before the first construction delivery. Score display is not yet implemented.
- Worker destruction and planetoid destruction request a QBANG-style explosion reconstructed from the original CANNON/FNOISE arithmetic and converted through speech2ay. The reconstruction uses approximate sound-CPU timing; it is not a bit-exact sound-board emulation. Sinistar speech always wins.
- Player motion uses the translated arcade acceleration arithmetic instead of immediately assigning velocity. A screen-adapted target of twice the former speed reaches about 1.94–1.95 pixels per physics tick; release directions to coast. The full-power multiply uses a shift/subtract fast path. This is a tuned TS2068 adaptation, not a claim of identical arcade axis scaling.
- Contact with primary and secondary planetoids reflects approaching player velocity in the moving rock's reference frame. Wrapped coordinates and an eight-tick recovery guard prevent repeated inversions under held thrust. Planetoids are treated as heavy obstacles; the arcade's exact mass exchange and altered planetoid trajectory remain unported. Secondary checks share the existing four interleaved population groups.
- Radar now draws the complete small viewport outline around the centered player, positioned from camera/world coordinates. Contact colors and 8x1 attribute conflict staggering remain intact. Update frequency stays at one preparation per 24 physics ticks.

The explosion is a compact port-specific fragment effect rather than pixel-identical arcade fragments. No graphics work is added for hidden explosions beyond existing object culling.

### Storage and interrupt constraints

All five effects use a three-byte register format; the four previous effects decode to identical AY register frames. Explosion register updates hold for three refreshes (about 20 Hz) over the full reconstructed sample. The total HOME SFX cache is 552 bytes at 5C40–5E67, below the radar queue at 5EA0. Speech is unchanged.

The decoder lives in DOCK6 because interrupts can arrive while the renderer's comparison-stream stack is in HOME E000–FFFF. Mapping DOCK7 in that interrupt path would hide the stack. Tests exercise both normal and high-RAM stack locations. The world extension reserves 5140 bytes and uses 5103; the cartridge remains 64 KB.

### Still outstanding from the arcade audit

- Exact mass-based bounce, original fragment artwork, and a score HUD remain adaptations to finish.

Source references: WITT/COLLISIO.SRC (worker hits/QBang), SAM/BOUNCE.SRC (arcade mass exchange), SAM/EXECJNK.SRC (acceleration), SAM/SCANNER.SRC (viewport position), SAM/ADDPIEC.SRC and WITT/SUBPART.SRC (piece removal), WITT/ANISINI.SRC and VSNDRM9.ASM (speech and sound). The original source checkout is pinned as a Git submodule.

Verification: `verify_gameplay_features.mjs` covers seam-crossing worker hits and bounces, crystal release, replacement before assembly, acceleration/coasting, all four explosion stages at eight shifts, scanner outline, exact packed AY frames, speech priority, and both ISR stack locations. `verify_scrolling.mjs --fast --assembly` includes 1078 scenarios, including explosions clipped at either edge and overlapping assembly. Full playable lifecycle and 18000-refresh rendering stress are also exercised. See FAST_MODE_PROFILE.md for current performance; older sections describe their named builds.

**Current playable milestone:** [Scrolling world](SCROLLING.md), including stars, 18 persistent planetoids and world-relative radar. The following flight/pursuit notes describe earlier separate builds.

**New:** [Sinistar pursuit experiment](PURSUIT.md) adds the large sprite and direct pursuit. It now renders at about 28.5 visible fps in TSRun and 20 fps in native Fuse after renderer optimization; the 60 Hz flight build remains unchanged. Open <http://127.0.0.1:8768/port/pursuit-web/>.

The actual port begins here, separately from the accepted scripted demonstration.

Open <http://127.0.0.1:8768/port/web/> using the main project server. The new

`build/sinistar-flight.dck` draws the original ship with all 32 headings and eight

pixel phases. Automatic joystick direction feeds translated turning, SINCOS,

and acceleration routines; position and velocity are calculated on the Z80.

This is a flight milestone, not a playable game. The player is followed by the

original soft/hard camera rules, with ten camera-driven stars. There are no

controls, enemies, weapons, or speech yet; input remains automatic.

The earlier `sinistar-port-kernel.dck` remains a separate green/red-border diagnostic.

The renderer restores the old rectangle in HOME buffers, composes the next sprite,

waits for refresh, and publishes only final changed bytes in the old/new rectangles.

Bitmap and ECM attribute comparisons use XOR to skip unchanged bytes. There is no

visible erase pass. This handles overlapping consecutive player rectangles and

moving stars; it does not yet compose overlapping multiple game objects. All

old stars are removed from protected RAM before any new stars are added. Dirty

star cells are published first, then the two ship rectangles.

Color pairs come from the existing demo assets; background stars sharing covered

8Ã—1 cells inherit the sprite palette. This remains an ECM approximation.

TSRun verified 2,261 updates, all 32 headings, all eight pixel phases, and 2,260

consecutive one-refresh intervals. Full-frame and actual raster checks found zero

mismatches, intermediate writes, unchanged writes, or ROM writes. Maximum measured

work is 43,104 T-states of 58,688 per refresh; the publishing pass uses at most

15,965. Native Fuse independently verified 1,023 consecutive refresh intervals.

These guarantees cover this scene: y is restricted to 48â€“143 so the publishing

pass finishes ahead of the affected raster. General screen coverage needs a new

timing strategy before removing that constraint. No physical hardware test yet.

## Original source baseline

Preserved 6809 assembly is checked out in `reference/original` from

[historicalsource/sinistar](https://github.com/historicalsource/sinistar/tree/dc00bce37e5c5c7947369cf5040c10e4799f4a06),

commit `dc00bce37e5c5c7947369cf5040c10e4799f4a06`.

Using surviving source retains labels and comments that a ROM disassembly loses.

The original library describes V17 programmer directories and overlay builds.

This checkout has **not been assembled and matched against a shipped arcade ROM**.

Its later patches must be reconciled before claiming retail-revision fidelity.

Original material remains attributed to its authors; this import grants no new license.

| Original code | Z80 translation | Status |

|---|---|---|

| `WITT/VELOCITY.SRC`, `newvelocity` | `src/motion.asm`, `new_velocity` | Sinistar table; every valid signed distance tested |

| `WITT/STBLSINI.SRC` | generated little-endian ROM table | Parsed directly from pinned original expressions |

| `WITT/VELOCITY.SRC`, `updscreen` arithmetic; `SAM/FUNCTION.SRC`, `asrdN` | `smooth_velocity` | Every 16-bit difference at shifts 0â€“7 tested |

| `SAM/EXECJNK.SRC`, rotation block from `SUBB PLYRANG` to `STA PLYRANG` | `player_turn` | Every signed angular difference and radius tested |

| `SAM/FUNCTION.SRC`, `SINCOS`; `SAM/SAMTABLE.SRC`, `SINETBL`/`QUADTBL` | `src/player.asm`, `player_sincos` | All 256 angles, original XOR sign convention |

| `SAM/EXECJNK.SRC`, both player acceleration blocks | `player_accelerate` | Every 16-bit difference at nine boundary/representative radii |

| `SAM/EXECJNK.SRC`, `SCROLL` | `src/camera.asm`, `camera_axis` | 100,000 cases covering signed arithmetic and both edge limits |

| `SAM/EXECJNK.SRC`, 24-bit screen integration | `camera_integrate` | 100,000 carry/borrow/wrap cases |

| `SAM/IRQ.SRC`, star camera deltas | `src/stars.asm` | Full-scene comparison including 400 star wraps and 68 ship overlaps |

The scene also preserves the original Â±32 angular acceleration gate and

`(angle+4)&$F8` image selection. Its screen adapter reverses the long-axis sign

because TS2068 scanlines grow downward. Camera integration now retains the

original 24-bit wrap and rounding. The automatic input advances one angle unit

every two refreshes with radius 127; the original game scheduler is not ported.

ABI details are above each routine. These are arithmetic cores; original object

workspace addressing and scheduler wrappers are not yet translated. The speed

selection deliberately retains the second search by speed, even though table

speeds are nonmonotonic. Acceleration retains `ORB #1`, including its asymmetric

effect on negative values. Turning retains signed delta and +128 rounding.

Distance -32768 is excluded: its absolute value cannot be represented in the

original signed range search. The eventual world-distance adapter must enforce

that precondition. No floating-point substitute or precomputed flight path is used.

## Build and verify

From the main project directory:

```powershell

python port/scripts/build.py

& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify.mjs

python port/scripts/verify_fuse.py

python port/scripts/build_flight.py

& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify_flight.mjs

python port/scripts/verify_fuse.py --flight

```

Dependencies: existing SjASMPlus under the main `tools/`, local sibling TSRun

checkout and its TS2068 ROMs, Git, Python, and native Fuse. Build refuses changed

original sources or a different source commit. Outputs stay under `port/build`.

`sinistar-port-kernel.dck` is a sparse 8,201-byte ROM cartridge;

`sinistar-port-kernel.bin` is the corresponding padded 64 KiB physical image.

`manifest.json` records original-source hashes and the cartridge hash.

`verification.json` records 1,645,439 Z80 cases compared against independent

integer models, followed by genuine ROM boot and 1,068 consecutive TSRun refresh

interrupts. This is model-based arithmetic equivalence, not differential execution

of a rebuilt 6809 game. Native Fuse results are in `fuse-report.json`.

See `MEMORY_MAP.md` for the complete chunk/interrupt contract. Hardware untested.

The flight build has separate `flight-manifest.json`, `flight-verification.json`,

and `flight-fuse-report.json`; each report identifies its tested cartridge hash.

## Starfield fidelity

`SAM/IRQ.SRC` moves every star by the same rounded screen-coordinate delta;

`SAM/SAMEQUAT.SRC` sets NSTARS to $0A. The port follows those mechanics rather

than the saved demo's three artificial depth speeds. Its world-relative motion

is therefore shared-camera scrolling, not a new multilayer parallax effect.

The original routine also alternates packed-pixel nibbles, uses five repeated

colors, and randomizes one coordinate on the first wrap in an interrupt. This

milestone uses white 1-bit stars, fixed repeatable seeds, and toroidal wrapping

on the TS2068's 256Ã—192 display. Those are explicit display adaptations, not

claims of exact original star placement/color. Source camera arithmetic remains

in arcade units; displayed y=152-long.high is the current vertical adapter.

## Next implementation stages

1. Reconcile the source overlays and patches (`MAKE.COM`, `SAMFIXES.SRC`,

   `RICHFIXE.SRC`, related include chains); select and document an arcade revision.

2. Connect the camera coordinates to object/scanner world coordinates. Translate

   joystick conversion when controls are requested; keep automatic input for now.

   Player acceleration, camera damping, and camera-driven stars are implemented.

3. Extend the dynamic ECM compositor to multiple overlapping objects and the

   full screen. The saved demo's precomputed deltas are not used by this renderer.

4. Port object workspaces/scheduler, `CHASE` and velocity wrappers, Sinistar state

   transitions, workers, warriors, planetoids, crystals, weapons, collisions, and HUD.

5. Connect AY speech/mouth events and measure the complete worst-case frame budget.

## Saved demo

The accepted 60 Hz audiovisual demo is frozen at `../revisions/v3-60hz/`.

Open `WATCH.html` there for offline playback, or use its `web/` route through

the main project's server. Its files and validation reports are independent

of this port and are covered by `SHA256SUMS.json`.



### v28 roar and impact mix

Bomb hits no longer restart an ongoing roar. Its full duration is preserved while a short channel-C noise impact plays alongside channels A/B. The full roar recording has a new noise-aware speech2ay fit to address the tonal tail. Other voices and speech priority over firing are preserved. See TAUNTS.md and the saved revision's audio/index.html for details and listening comparisons.


### Original attract sequence audit

MICA/ZZAMSINI.SRC is an event-driven controller: collect at least four bombs or exhaust the initial timer; force the player into OMWaBomb with Sinistar as its target; bring Sinistar to the sector edge if necessary; launch up to sixteen crystal-carrying workers on TASK8; when bombs run out, wait roughly three seconds and end the demo. MICA/BOBFIXES.SRC reapplies the bomb mission so other AI cannot displace it. WITT/WARRIOR.SRC uses the outer-orbit distance/velocity tables and occasional random bomb launches only while Sinistar is onscreen. FALS/N1ALL.SRC's InPopD specifies two workers and twenty-one planetoids.

The new frontend uses the original ATTMSGS.SRC wording and color intent, but its gameplay demonstration currently uses a timed native steering/shooting loop. The source AI, phase controller, extra worker capacity and original demo population are not implemented by this change. A faithful gameplay attract sequence remains a separate gameplay-port step; it is not a fixed prerecorded joystick sequence that can simply be replayed.


### v42 - player death attack

Adds a source-derived GUNSHOT attack converted with speech2ay harmonic1: 12 AY frames, 36 packed bytes in resident DOCK4. The existing explosion starts exactly twelve audio refreshes later (~0.200 seconds), independent of graphics/physics catch-up. The first visual burst does not restart it. Later death bursts retain their existing sounds; speech always takes priority. The second part reuses the current blast, not the full original C4NNON sound.

Excluded obsolete bullet/crystal diagnostic branches from PLAYABLE_GAME; production world-bank handlers and shared kill routines are unchanged. Scanline tables remain at 9300; resident end is 9FF5. The cartridge stays 64 KB, with no extra RAM allocation or graphics work.

Verified exact AY registers, twelve-refresh chaining, speech priority, no ROM writes, player/Sinistar death sequences, firing cadence, and playable win/restart/loss. See build/player-impact-verification.json.


### v43 - recorded gunshot attack

Player death now starts with the selected half-second real-gunshot AY noise fit, followed by the existing explosion. It uses 90 bytes in existing resident padding; no cartridge growth. See [RECORDED_IMPACT.md](RECORDED_IMPACT.md) for timing, source attribution, and validation.


### v44 - game-over text and radar cost

GAME OVER and FIRE TO RESTART now use attribute 7 instead of 71, matching normal black. Native verification checks all 168 attribute writes. Radar interval remains 24 display refreshes. A populated-world native Z80 benchmark of 128 moving positions measures about 75,052 T-states (21.27 ms) per preparation/publication; 73,329 are preparation. Nominal average CPU at intervals 24/12/8/6 is 5.33/10.66/15.99/21.31 percent. These are isolated instruction-cycle estimates, excluding interrupts/contention; actual update rate is limited by main-render completion. Fast mode still scans the world population, so its radar cost is similar. See build/radar-cost-verification.json.


### v45 - faster radar preparation

Replace 64 general-purpose horizontal viewport dot calls with masked byte-span writes. Vertical outline and object markers retain their original layering and conflict handling. Replace repeated 16-bit coordinate shifts with carry/rotate extraction of the wrapped 9-bit positions; simplify camera setup. Remove unused legacy YOU WIN string to fit bank 6.

Against v44, 1,024 scenes exercise all 64x16 radar origins, randomized 9-bit positions and varying populations. Staging pixels/attributes, publication queues, and resulting screen bytes match exactly. No ROM writes.

Matched populated-world cycle estimate: preparation 73,329 -> 47,471 T-states (35.3% reduction), total preparation/publication 75,052 -> 49,194 (21.27 -> 13.94 ms). Current 2.5 Hz estimated CPU share 5.33 -> 3.49%; 5 Hz would be 6.99%. These are isolated instruction-cycle measurements excluding interrupts/contention and main-render scheduling delays, not a measured whole-game FPS gain. Radar cadence remains 24 refreshes. See radar-cost-verification.json and radar-equivalence-verification.json in build.


### v46 - responsive player death

Decouples visual death start from the 30-refresh gunshot. Start the first explosion immediately and keep the existing 96-tick sequence instead of 126 ticks. The full gunshot still finishes before the explosion sound; visual waves cannot interrupt it. Player bursts alternate left/right, using one explosion sprite per wave rather than two concurrent slots. Sinistar destruction retains paired bursts. Skip radar preparation while world physics is paused for either death sequence.

Native encounter fixture: v45 first explosion 615.60 ms, total 2.197 s, 9.63 mean picture fps including the static lead-in. v46 first explosion 136.02 ms, total 1.630 s, 10.71 fps. Immediate-start with two simultaneous slots measured 7.85 fps in the intermediate experiment; alternating one slot measured 10.71. These are controlled fixtures, not a general frame-rate guarantee. Sinistar/world movement still pauses during player death by design. Validate full audio stream, speech priority, all six waves, respawn protection and victory/game-over completion.


### v47 - faster explosion shifts

Explosion unpack now uses Z80 RRD to shift mask/bitmap nibbles by four pixels in one pass, then runs only the remaining zero-to-three bit shifts. Phases 4..7 save about 13,980 T-states per sprite (20..26% of total unpack/shift/color time). Phases 1..3 add 46 T-states (<0.14%); phase zero is unchanged. 256 deterministic random dictionary/index tests compare every decoded output byte with v46, across all phases including masks, spills and palette propagation.

Player-death encounter mean picture rate improves 10.713 -> 11.253 fps (5.0%). Native non-explosion one-rock mining / one-rock pursuit / three-rock pursuit remain 19.282 / 11.741 / 9.772 fps in matched controlled fixtures. Main remaining costs are composition and dirty-byte comparison, followed by physics. No global speedup or 20-fps claim.

Removed unreachable diagnostic assembly-drawing code from PLAYABLE_GAME only (retained behind IFNDEF), making room for the nibble helper before aligned scanline tables. These remain at 9300; resident ends 9FFF. No extra RAM, same 64-KB cartridge. Gameplay win/restart/loss and 18,000-refresh fast render stress pass. See explosion-speed-verification.json, worker-death-verification.json and stress-fast-verification.json.


### v48 - cheaper normal rendering

Erase only the ten previous star cells, rather than both previous and new positions. New stars mark their cells dirty only after passing occlusion and blank-pixel checks. This avoids clearing retained sprites unnecessarily; star motion, overlap order and colors are preserved. Use a sequential star pointer instead of indexed accesses. The shared changed-byte compiler skips setup on empty rows and reconstructs attribute pointers from the completed bitmap span, eliminating two pointer saves/reloads per span.

Matched v47/v48 native controlled scenes (18 simulated rocks, continuous right input, no combat/speech):

| Scene | v47 fps | v48 fps |
|---|---:|---:|
| One visible rock, no Sinistar | 19.282 | 19.282 |
| One visible rock, pursuing Sinistar | 11.741 | 12.358 |
| Three visible rocks, pursuing Sinistar | 9.772 | 9.842 |

These scenes control visible counts; they are not a complete fast-mode gameplay average. The 18,000-refresh fast stress fixture completes 3,988 pictures versus v47's 3,737 (+6.7%), with exact reference-compositor bitmap/attribute checks, zero ROM writes and zero late display writes. Its changing positions and scripted state transitions make it a broad regression/workload sample, not a matched-pose microbenchmark. Quiet mining now spends more time waiting for the next refresh rather than increasing its picture rate.

The compiler independently matches expected output and v47 across 128 randomized dirty-region cases, including empty rows, column-zero underflow, full widths and split fast-face exclusions (15,478 changed-byte records). Average isolated comparison cost drops 3.44% in that test. Fast gameplay mining/assembly/bomb victory/restart/contact/loss checks pass. No changes to physics cadence, visible population limits, speech or cartridge size. Resident ends 9FF6, with 10 bytes remaining; bank 6 uses 5,999/6,000 extension bytes. Further large gains still require reducing composition/comparison work, especially with multiple visible rocks; this is not a 20-fps pursuit claim.


### v49 - compiled rendering for vertically clipped planetoids

Rocks with all five byte columns visible now use compiled row programs even when clipped above or below the playfield. Skip source row pointers for the hidden top rows and draw only the visible height. Previously any height other than 28 triggered staging/unpacking the sprite and the general clipped compositor. Side-clipped rocks retain that fallback. Masks, attribute writes, object layering, dirty-row repair, populations and physics are unchanged.

Matched native v48/v49 benchmark, 18 simulated rocks, continuous right movement, no combat/speech; three visible rocks with secondary rocks at screen Y=52 and 164:

| Scene | v48 fps | v49 fps | Gain |
|---|---:|---:|---:|
| Three rocks, mining | 13.737 | 19.282 | 40.4% |
| Three rocks, pursuing Sinistar | 8.544 | 9.985 | 16.9% |

These gains apply to top/bottom clipping; fully visible controlled scenes are unchanged (three-rock mining 18.765 fps, pursuit 9.842 fps). The mixed 18,000-refresh fast stress workload remains effectively unchanged at 3,986 pictures vs 3,988, while validating exact bitmap/attribute output, zero late writes and zero ROM writes. It is not a general 40% speedup.

448 independent native renderer cases cover all eight fine X phases, heights 1..28, top/bottom clipping, randomized background bitmap/attributes and placement through the rightmost full-width column. Output exactly matches masked reference composition. Cartridge resident ends 9FF8, leaving eight bytes; no extra graphics tables or RAM. See vertical-rock-verification.json and the before/after-v49 controlled profile reports. The profiling script now accepts an optional build directory and --edge-rocks to reproduce this comparison.


### v50 - reject distant planetoid collisions before banking

Before calling the banked player/rock bounce routine, reject low-byte X differences outside the necessary contact interval. Candidates still undergo the original wrapped 9-bit X/Y and approaching-velocity tests; the coarse check cannot discard a real collision. Preserve the direction in C while testing the bounce toggle; remove redundant IX saves (the effects routine and signed_word do not touch IX). Reclaim two bytes from an unreachable RET and equivalent projection shifts to fit the bank.

8,192 native comparisons against v49 cover every wrapped X difference, varied Y offsets, both world seams, all nine rock directions, varied player velocities, bounce disabled and recovery cooldown. Player velocity, cooldown, bank state and IX match exactly. The isolated check averages 357.82 -> 102.98 T-states across this sample (71.2% lower); far rejection averages 338.13 -> 46. This is collision-check savings, not overall FPS gain.

Matched controlled profile, 18 simulated rocks, continuous right input, no combat or speech:

| Scene | v49 fps | v50 fps |
|---|---:|---:|
| One visible rock, mining | 19.282 | 19.276 |
| One visible rock, pursuit | 12.358 | 12.334 |
| Three visible rocks, mining | 18.765 | 19.276 |
| Three visible rocks, pursuit | 9.842 | 10.196 |

The three-rock improvements are 2.7% and 3.6%. Single-rock rates remain approximately unchanged, slightly lower in these runs due to picture/refresh scheduling and evolving pursuit positions; no universal frame-rate improvement claimed. Physics tick rate, world population, bounce behavior and graphics are preserved. Savings decrease after fast pursuit retires secondary rocks or when bounce is disabled. No additional RAM or cartridge capacity: world extension remains 5,999/6,000 bytes, resident end 9FF8. See bounce-broadphase-verification.json and one-planetoid-profile-after-v50.json.


### v51 - frame-wide compiler and sprite overhead

The changed-byte compiler keeps its scanline in IYL, span width in IXL and optional split width in IYH instead of repeatedly accessing RAM. Bit 6 of the shadow address distinguishes bitmap from attribute passes, eliminating the per-row plane flag. Kernels/offset and the audio/border ISR leave these index registers intact. Remove the diagnostic stationary-face dirty-row branch from the playable generic sprite loop; it remains available under IFNDEF PLAYABLE_GAME for diagnostic builds. No reduction in update cadence, graphics quality, population or game logic.

Matched compiler testing against v50 covers 128 randomized dirty-region cases and 15,478 changed-byte records, including column-zero wrap, both planes, empty rows, full widths and fast-face split exclusions. Exact output, 157,209.84 -> 148,001.23 average T-states (5.86% less compiler time).

| Controlled scene | v50 fps | v51 fps |
|---|---:|---:|
| One visible rock, mining | 19.276 | 19.276 |
| One visible rock, pursuit | 12.334 | 12.362 |
| Three visible rocks, mining | 19.276 | 19.276 |
| Three visible rocks, pursuit | 10.196 | 10.497 |

Controlled scenes have 18 simulated rocks, continuous right input, no combat/speech, 120 measured pictures. Quiet mining stays refresh-wait limited at this workload. The broader 18,000-refresh stress run completes 4,114 pictures versus v50's 3,965 (+3.76%); it verifies exact reference bitmap/attributes, radar output, no ROM writes and no late screen writes. As simulation/picture timing changes, scene positions vary, so this is a workload result rather than a universal FPS guarantee. Mining/assembly/bomb victory/restart/contact/loss and speech checks pass.

No extra RAM or cartridge capacity; resident ends 9FDE (34 bytes free), world bank unchanged. See dirty-stream-verification.json, one-planetoid-profile-final-v51.json, stress-fast-verification.json and voices-verification.json.


### v52 - reuse population preparation and shared star wrapping

Population preparation sets the erase/repair flag once per record. Hidden projections invalidate their width and finish immediately instead of looking up and testing the cache again. Visible projections reuse the pointer left by the copy instead of a second lookup. Prior-visible disappearance erasure and retained-object repair are unchanged. Native comparison against v51 matches cached projections, identity copies, dirty flags, visibility aggregates and restored primary rectangle/clip state across 256 randomized worlds; average preparation 18,096 -> 15,312 T-states (15.4% lower).

Star motion reduces the signed camera Y displacement modulo 112 once per picture, then updates ten stars with byte arithmetic and a single possible subtraction each. Sequential HL accesses replace indexed loads/stores. Native comparison matches all 512 wrapped Y displacements, every star row, varied X scrolling and initialization across 6,144 cases. Small-scroll update cost averages 2,641 -> 1,631 T-states (38.2% lower). Stars and scrolling remain visually identical.

| Controlled scene | v51 fps | v52 fps |
|---|---:|---:|
| One visible rock, mining | 19.276 | 28.098 |
| One visible rock, pursuit | 12.362 | 12.489 |
| Three visible rocks, mining | 19.276 | 19.265 |
| Three visible rocks, pursuit | 10.497 | 10.771 |

Same 18 simulated rocks, continuous right input, no combat/speech, 120 measured pictures. The large one-rock jump is a refresh-deadline threshold, not a 46% reduction in CPU work. Three-rock mining remains approximately unchanged. The mixed 18,000-refresh stress fixture produces 4,129 pictures versus 4,114 (+0.36%), with exact bitmap/attribute/radar checks, zero ROM writes and zero late writes. This workload is still dominated by chasing/overlap costs, so no large whole-game-average gain is claimed. Mining/assembly/bomb victory/restart/contact/loss checks pass.

No new RAM, tables, physics or population changes. World extension is now 5,985/6,000 bytes; HOME render helper is 353/368 bytes, freeing ten boot-source bytes as well. Resident still ends 9FDE. Reports: star-update-verification.json, population-cache-verification.json, one-planetoid-profile-final-v52.json and stress-fast-verification.json.


### v53 - leaner rock drawing and rectangle clearing

clear_plain keeps height/end-column in index registers (preserving caller IX) and avoids BC save/restore around kernels that do not modify BC. Native randomized rectangles match v52 and a reference fill across 512 cases; average clearing cost drops 9,935 -> 8,865 T-states (10.8%). Compiled rock programs reuse an already-loaded attribute when opaque pixel stores preserve A. Direct stack dispatch removes the intermediate IX transfer for each row. 448 masked-composition tests across all shifts, top/bottom clipping and background pixels pass. Compiled rock code/tables shrink 5,087 -> 4,907 bytes, recovering 180 cartridge bytes.

The existing controlled fixture pins rocks at fixed screen positions; it does not exercise continuously moving rock images. A new --moving-rocks fixture keeps the requested visible count while applying a deterministic 0..16-pixel horizontal triangle displacement over 64 refreshes to those rocks. Native player/pursuit physics and 18 simulated planetoids remain active. No combat or speech; 120 measured pictures after warmup.

| Moving-rock scene | v52 fps | v53 fps |
|---|---:|---:|
| Two rocks, mining | 11.675 | 11.763 |
| Two rocks, pursuit | 8.192 | 8.268 |
| Three rocks, mining | 9.870 | 9.855 |
| Three rocks, pursuit | 6.619 | 6.774 |

These are modest gains, with three-rock mining approximately unchanged/slightly lower. Fixed-position two-rock pursuit is likewise approximately unchanged (11.893 -> 11.888), as is three-rock pursuit (10.771). The mixed stress run draws 4,151 vs 4,129 pictures in 18,000 refreshes (+0.53%), with exact bitmap/attribute/radar checks, zero ROM writes and zero late display writes. Gameplay win/restart/contact/respawn/loss passes. This does not meet a 20-fps multi-rock target. Larger gains require reducing the amount of changing sprite/dirty-region work rather than only making its loops cheaper.

Reports: clear-regions-verification.json, vertical-rock-verification.json, one-planetoid-profile-rocks-v53.json, one-planetoid-profile-moving-after-v53.json and stress-fast-verification.json. Reproduce baselines using the profiler's optional build-directory argument with v52. No sprite, timing, physics or population reduction.


### v54 - skip invisible awake Sinistar preparation

Check the clipped Sinistar rectangle before selecting/decompressing/shifting an awake face. Previously a nonzero fine-X speaking pose unpacked all 52 rows, reconstructed the shifted body and shifted mouth data before scene_sprite rejected the zero-width rectangle. Offscreen closed poses also performed needless atlas selection/bank dispatch. Old-screen cleanup still occurs earlier, and assembly image/cache building remains active as needed. Audio, animation state and pursuit continue normally; visible poses use the unchanged renderer.

Native path test covers 72 combinations of mouth/eye/fine-X, confirming unchanged animation state/bank and no screen writes. Previously shifted hidden speaking poses averaged 151,919 T-states (43.06 ms) in isolated preparation; now they exit in 27 T-states. This is preparation cost, excluding physics, other objects and audio interrupts.

Controlled forced-hidden-speaking benchmark (18 simulated rocks, pinned rock positions, Sinistar kept offscreen with open mouth before each picture; native pursuit runs, no audio stream injected):

| Visible rocks | v53 fps | v54 fps |
|---|---:|---:|
| One | 10.460 | 19.285 |
| Two | 9.639 | 19.285 |
| Three | 9.639 | 19.269 |

This measures the invisible speaking graphics case, not normal gameplay average or end-to-end speech CPU cost. The broad 18,000-refresh stress workload is effectively unchanged (4,153 vs 4,151 pictures), with exact pixel/attribute/radar reference checks and no late writes or ROM writes. Gameplay victory/restart/loss and full speech/roar/hybrid audio tests pass. Resident ends 9FDB (37 bytes remaining), same 64-KB cartridge.

Reports: hidden-face-verification.json, one-planetoid-profile-hidden-after-v54.json, stress-fast-verification.json, fast-playable-verification.json and voices-verification.json. The profiler accepts --hidden-speaking-face for reproduction.


### v55 - normal-black text and fewer text attribute writes

Game-over/restart already use attribute 7 (verified again: 168 attribute writes, all normal black). Remove remaining BRIGHT flags from high-score headings/rows/hero fields (66/70/71 -> 2/6/7), live HUD score/ammo (71 -> 7), and FAST MODE / BOUNCE notices (71 -> 7). Captured high-score screen attributes are exactly {2,6,7}; initials screen {7}. Instructions, congratulations and initials were already normal-black. Decorative radar trim/title artwork is not text and is unchanged.

front_char formerly selected banks and rewrote the attribute for all five pixels of each glyph row. It now writes the attribute only when entering an 8x1 cell, including a glyph crossing the byte boundary. Native comparison against v54 covers all 37 glyphs, eight horizontal phases and red/yellow/white ink: 888 exact bitmap/attribute cases. Average character rendering 7,744 -> 6,241 T-states (19.4% faster). This improves text screens/instruction transitions, not the gameplay sprite frame rate. Removing the now-redundant notice-brightness branch provides the needed code space.

Frontend cycle/attract/instructions/native initials/keyboard/joystick tests pass, as do HUD changed-only updates, bounce notices, gameplay features and the game-over normal-black check. See text-cell-verification.json, frontend-verification.json, frontend-hud-verification.json, gameplay-features-verification.json and radar-cost-verification.json. Same cartridge capacity, no additional RAM.


### v56 - longer shots and cheaper coordinate access

Player shots use a 12x rather than 8x signed unit vector: 50% faster, about 137 instead of 91 world pixels of cardinal travel before expiration. Keep the 24-tick lifetime and single projectile slot, preserving held-fire launches every 24 ticks; impacts can release the slot sooner. Range relative to a ship flying in the same direction increases more than 50%. This avoids slowing repeat fire or adding projectile rendering work. Validate all 256 headings at exactly 1.5x velocity, a worker beyond the former range, and a distant secondary planetoid across all four interleaved population phases. Speech/SFX priority and firing cadence checks pass.

All 16 primary-object integer coordinate bytes reside in page 78. Compress the coordinate pointer table to offsets and retain the constant page across projection/restoration. wb_get, used by movement and AI, likewise avoids reading the redundant high byte. Assembly assertions enforce the layout. Against v55, 512 randomized projection/restore cases and 8,192 coordinate reads are exact; projection+restore costs 5,804 -> 4,890 T-states (15.7% less in that routine). No new RAM.

Moving-rock controlled scene rates v55/v56: one-rock mining 16.058/16.300; one-rock pursuit 10.131/10.141; two-rock mining 11.763/11.763, pursuit 8.268/8.259; three-rock mining 9.855/9.855, pursuit 6.774/6.763. Thus little overall rate change; no broad major speedup claimed. These fixtures disable firing. The 18,000-refresh stress run draws 4,171 pictures and passes exact graphics/radar checks with no late writes or ROM writes; full playable win/restart/loss also passes. Shot speed is an intentional gameplay change; physics timing/population and speech priority remain unchanged.

Reports: coordinate-page-verification.json, shot-range-verification.json, firing-verification.json, one-planetoid-profile-final-v56.json and stress-fast-verification.json. Same 64-KB cartridge.

## v57: faster speaking-pose preparation

Visible speaking Sinistar now unpacks bitmap and palette planes sequentially. Mouth shifts of four or more pixels use one four-bit RRD pass followed by at most three one-bit passes. The output is identical, including transparency masks and attributes. The cartridge retains the longer shots from v56.

Controlled moving-rock benchmark: continuous right input, 18 simulated planetoids, 120 measured pictures after 360 refreshes. The encounter fixture forces the open mouth; no speech audio IRQ load, workers, firing, or damage is injected. These are stress cases, not averages for normal play.

| Visible rocks | Sinistar | v56 fps | v57 fps |
|---|---|---:|---:|
| 1 | Absent | 16.30 | 16.30 |
| 1 | Speaking | 5.96 | 6.28 |
| 2 | Absent | 11.76 | 11.76 |
| 2 | Speaking | 5.09 | 5.61 |
| 3 | Absent | 9.86 | 9.86 |
| 3 | Speaking | 4.71 | 4.93 |

Preparation saves 5,701–34,813 T-states per nonzero-phase speaking pose (about 1.6–9.9 ms at 3.528 MHz). Mining speed is unchanged. Speaking scenes remain below 10 fps; this does not meet a 20 fps target.

Validation: 256 randomized shift cases and 63 actual eye/mouth/shift combinations match v56 exactly; full gameplay and speech checks pass. Fast-mode rendering stress: 4,171 pictures over 18,000 refreshes, no late raster writes or ROM writes. Cartridge is 64 KiB payload plus nine-byte DCK header; world code 5,993/6,000 bytes, incremental helper 1,032/1,056 bytes.

## v58: dedicated shifted Sinistar compositor

Shifted speaking/awakening poses have one masked left cell per row and opaque remaining cells. The dedicated compositor retains the left-edge mask, writes the remaining bitmap cells directly, and uses alternate HL for the attribute plane. Other object compositors and drawing order remain unchanged. It does not add an opaque rectangle or remove existing overlap composition.

The loop measures about 30% cheaper in isolation; including clipping and banking, 1,323 equivalence cases take 42,673,995 versus 34,440,525 T-states (19.3% reduction). All three eye poses, three mouth poses, seven nonzero shifts, seven horizontal crops and three vertical crops match v57 over randomized backgrounds, including attributes. This test invokes the actual scene entry wrappers.

Controlled full-scene benchmark: 18 simulated rocks, moving camera and visible rocks, forced open mouth, no speech IRQ load, workers, firing or damage; 360-refresh warmup and 120 measured pictures. These are demanding controlled encounters, not typical gameplay averages.

| Visible rocks | Sinistar | v57 fps | v58 fps |
|---|---|---:|---:|
| 1 | Absent | 16.30 | 16.30 |
| 1 | Speaking | 6.28 | 6.70 |
| 2 | Absent | 11.76 | 11.76 |
| 2 | Speaking | 5.61 | 5.75 |
| 3 | Absent | 9.86 | 9.86 |
| 3 | Speaking | 4.93 | 5.08 |

The final full-scene benefit is 2–7%; mining is unchanged. An early integration bug involving the bank wrapper overwriting A was fixed by reading the clipped height directly, and the full benchmark was rerun. Earlier provisional 9–15% figures do not apply to the final build.

Build fits the existing 64 KiB cartridge payload. Fast-mode rendering stress passes 18,000 refreshes with no ROM writes or late raster writes; gameplay and voice verification pass. The earlier long shot range and edited roar are retained.
