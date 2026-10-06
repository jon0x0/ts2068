# Sinistar TS2068 port - scrolling flight

## Graphics work and gameplay audit, 6 October 2026

The v20 graphics work caches all eight assembly-mask phases using shared adjacent-byte patterns, retains the selected lookup, and intersects assembly composition with each row's actual dirty cells. Background transparency and fully covered-object suppression remain enabled. See ASSEMBLY_CACHE.md for measurements and memory constraints.

The following requested arcade features remain gameplay work; the graphics revision does not implement them:

- **Shootable workers and fragments:** WITT/COLLISIO.SRC, `COLLIDE WORKER,PLSHOT` / `WORKCR,PLSHOT`, invokes `QBang`, kills the worker and shot, and awards 150 points. A carrying worker leaves its crystal. Our bullet collision path currently tests planetoids, not workers. Implement worker death, a small fragment animation, crystal release, and respawn as one feature so killing the sole adapted worker cannot prevent construction permanently.
- **Explosion sound:** VSNDRM9.ASM maps `QBANG` to `CANNON`/`FNOISE`, not the existing `BBSV` bomb-launch effect. Generate this source-derived sound through speech2ay and preserve speech priority. The current port has firing, pickup, assembly, bomb-launch effects, and a Sinistar hit scream; that is not a complete explosion-sound implementation.
- **Planetoid bounce:** SAM/BOUNCE.SRC reverses velocities relative to the mass-weighted center of momentum. WITT/COLLISIO.SRC routes player/planetoid contact through `PreBou`, `Bounce`, `PosBou`. Use wrapped world coordinates and an object-bound broad phase, then retain a contact/separation guard. Do not implement a repeated inversion every frame inside a bounding box.
- **Player speed and acceleration:** SAM/EXECJNK.SRC scales the long-axis unit vector by four and the short axis by eight, then accelerates toward the target. The playable adapter currently assigns twice the signed unit vector directly (about one TS pixel per physics tick). Restore acceleration and explicitly account for the port's axis/display scaling; higher display fps alone does not correct movement speed.
- **Scanner outline:** SAM/SCANNER.SRC `SCANVEL` positions the small screen border relative to the player and camera. The current 64x16 adaptation already centers the player and projects the viewport, but draws corner markers rather than a complete outline. Extend that outline without increasing scanner update frequency, preserve per-line color staggering, and test wraparound/dead-zone scrolling.
- **Additional Run taunts:** WITT/ANISINI.SRC documents `Run, Coward!` and `Run! Run! Run!`; the sound source has the latter at command 29. The standalone `Run!` observation still needs sample/sequence verification. Do not label a cut-off `Run Coward` recording as a verified independent arcade phrase. These taunts are not in the current playable three-clip speech table.
- **Visible Sinistar damage:** SAM/ADDPIEC.SRC `SUBPIEC` removes a body piece and queues fragments; WITT/SUBPART.SRC requests the scream, slows Sinistar, and flashes the screen. The port already counts thirteen bomb hits, slows/stuns Sinistar, plays the scream, and shows the halo, but continues drawing the complete body until the final hit. Remove the actual outer pieces in source order, retain the head until the last hit, and reuse precomputed masks so damaged pursuit does not require runtime shifting.

Acceptance checks should cover worker death while carrying a crystal, rebuilding after worker respawn, seam-crossing bounces, held-thrust separation, camera-relative scanner outlines, speech/SFX arbitration, and a visibly different body after every successful Sinibomb hit. Keep fast-mode performance profiles separate for building, awakening, damaged pursuit, and hit effects.

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

8×1 cells inherit the sprite palette. This remains an ECM approximation.

TSRun verified 2,261 updates, all 32 headings, all eight pixel phases, and 2,260

consecutive one-refresh intervals. Full-frame and actual raster checks found zero

mismatches, intermediate writes, unchanged writes, or ROM writes. Maximum measured

work is 43,104 T-states of 58,688 per refresh; the publishing pass uses at most

15,965. Native Fuse independently verified 1,023 consecutive refresh intervals.

These guarantees cover this scene: y is restricted to 48–143 so the publishing

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

| `WITT/VELOCITY.SRC`, `updscreen` arithmetic; `SAM/FUNCTION.SRC`, `asrdN` | `smooth_velocity` | Every 16-bit difference at shifts 0–7 tested |

| `SAM/EXECJNK.SRC`, rotation block from `SUBB PLYRANG` to `STA PLYRANG` | `player_turn` | Every signed angular difference and radius tested |

| `SAM/FUNCTION.SRC`, `SINCOS`; `SAM/SAMTABLE.SRC`, `SINETBL`/`QUADTBL` | `src/player.asm`, `player_sincos` | All 256 angles, original XOR sign convention |

| `SAM/EXECJNK.SRC`, both player acceleration blocks | `player_accelerate` | Every 16-bit difference at nine boundary/representative radii |

| `SAM/EXECJNK.SRC`, `SCROLL` | `src/camera.asm`, `camera_axis` | 100,000 cases covering signed arithmetic and both edge limits |

| `SAM/EXECJNK.SRC`, 24-bit screen integration | `camera_integrate` | 100,000 carry/borrow/wrap cases |

| `SAM/IRQ.SRC`, star camera deltas | `src/stars.asm` | Full-scene comparison including 400 star wraps and 68 ship overlaps |

The scene also preserves the original ±32 angular acceleration gate and

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

on the TS2068's 256×192 display. Those are explicit display adaptations, not

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

