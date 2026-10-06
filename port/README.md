# Sinistar TS2068 port - scrolling flight

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

- **Visible Sinistar damage:** remove the twelve outer pieces in original source order, with the head remaining until the final hit. The existing thirteen-hit counter, scream, slowdown and halo do not yet remove individual visible pieces. Precomputed damaged poses/masks need a storage pass before adding this without regressing pursuit speed.
- **Additional taunts:** the source documents “Run, Coward!” and “Run! Run! Run!”; the playable speech table still contains assembly, identity and roar. A standalone “Run!” recording/sequence remains unverified.
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

