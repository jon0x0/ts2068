# Sinistar pursuit experiment

Open <http://127.0.0.1:8768/port/pursuit-web/> using the project server.
`build/sinistar-pursuit.dck` adds a camera-relative Sinistar object, its original
49x52 closed-mouth image, and correct overlap with the player and stars.
The existing 60 Hz flight cartridge remains available separately.

## Logic

`src/chase.asm` translates `WITT/CHASE.SRC`, preserving signed comparisons,
16-bit overflow, same-direction target compensation, and speed limits.
It passes 200,000 additional arithmetic cases (1,645,439 total kernel cases).
`src/pursuit.asm` connects the direct branch of `WITT/SINI.SRC` to NEWVELOCITY
and UPDSCREEN. Long distance is doubled as in `WITT/DISTANCE.SRC`; short desired
speed is doubled as in `WITT/VELOCITY.SRC`. Camera movement is added to the object.

This adapter supplies actual player velocity to CHASE; original scanner
workspace conversions and scheduler wrappers are pending. Orbit, mouth-offset
retargeting, construction, collisions, off-screen
scanner objects, and speech are not implemented. Keyboard and joystick movement are available; firing and bombing are pending.

## Stop-state milestone

`src/sini-stop.asm` translates the InStun countdown and SiStopChk branches in
`WITT/SINI.SRC`. A nonzero remaining stun clears both pursuit velocities. Dying
and attract flags also stop movement when the screen-workspace presence flag is
set, but permit off-screen pursuit. Timer 1 expires before the check, matching
the source ordering. This ports the movement gates, not the death animation or
collision system.

The adapter applies camera movement first, even when pursuit stops. Until the
scanner workspace system is implemented, screen presence means the entire face
fits the existing renderer's visible rectangle. The countdown runs on this
adapter's 60 Hz physics tick; the original Think/Task16 scheduling is still pending.

A separate scripted stimulus loads stun=61 at tick 512 and every 1,024 ticks
afterward. This produces a 60-tick pause, then normal recovery, without controls
or a simulated collision. The first pause occurs about 8.5 seconds into motion.
`verify_scene_stop.mjs` exercises 9,216 combinations of timer, dying, attract,
and screen-presence inputs against the assembled code.


## Renderer and measurements

The renderer composes the final picture in protected HOME RAM. Precompiled
Sinistar erase/draw routines touch its covered cells, and default white
attributes are implicit. Stars use separate dirty cells, avoiding wide empty
spans between a star and a sprite.

Most updates use a compact six-byte record per row: a ROM routine address,
display pointer, and shadow pointer. The Z80 consumes these records using its
stack, compares final bytes, and writes only differences. The normal stack is
restored before returning. The ISR preserves the registers used by the renderer;
its temporary pushes occupy already-consumed record space.

Publication starts just after the frame interrupt. A conservative cycle bound
checks the rectangle against the raster deadline. Wider or higher updates use
an XOR comparison pass to compile only changed-byte stores at $F000, then publish
that short list. This fallback costs extra preparation time and causes occasional
slower updates. There is no emulator speed multiplier or precomputed trajectory.

When the old/new **byte-cell envelopes** of the two sprites do not overlap, a
separate path reuses the saved 60 Hz demo's fixed-width-copy strategy. It emits
independent bitmap rectangles, ordered from top to bottom, and compiles sparse
attribute changes from the completed shadow image. The current and previous
positions both participate in the test: crossing paths or sharing an 8x1 color
cell retains the overlap-safe compositor. Stars and transparent sprite holes
keep the same compositing semantics. A per-rectangle raster budget can still
select the conservative fallback.

The separated path now reuses **relative precomputed transitions** for all eight
pixel phases and moves of -1, 0, or +1 pixel on either axis. It relocates sparse
color-cell masks and run-length encoded bitmap spans using the old screen origin.
This works at arbitrary eligible positions, including byte and screen-address
boundaries. The 72 cases share 5,007 bytes of compressed data. Larger moves,
appearance/disappearance, or overlapping old/new envelopes retain the general
renderer. Stars keep their own publication records, including background holes.
The actual pursuit positions are still calculated by the running port.

The assembled-Z80 relocation test covers all 72 transitions at 1,615 valid
positions. Preparation plus publication of the face averaged 42,627 T-states
versus 48,601 for the previous separated rectangle path: **12.3% less CPU time**.
This is an aggregate microbenchmark, not a uniform improvement: the maximum
new-path cost was 57,711 versus 54,484 T-states. The publication budget still
checks safety and can select the conservative fallback.

The current scripted-stun sequence completes 5,930 images over 12,000 TSRun
refreshes, averaging **30.06 visible fps**. It includes 720 stopped physics ticks.
This is a different motion workload from the previous 28.58 fps continuous chase,
not evidence of another renderer speedup: Sinistar spends more time off screen.
The stress sequence injects 46 relocations, executes 4 relative transitions,
and completes 5,524 images at 28.00 fps. Both runs have zero wrong or unchanged
display writes, ROM writes, and raster mismatches. All 32 headings and eight
player pixel phases are covered. The 132,096 arithmetic cases and 1,615 relocated
renderer cases continue to pass.

Native Fuse completes 1,023 intervals over 2,715 refreshes, approximately
**22.6 fps**, with SP=$7FFF at both checkpoints. Emulator timing differs;
hardware speed and raster behavior remain untested.

The stop-state milestone is preserved in `revisions/stop-state-v1`. The precomputed
renderer baseline remains in `revisions/renderer-v4-relative`, and the preceding
independent-rectangle version remains in `revisions/renderer-v3-separated`.

The previous 12 fps renderer is preserved in `profiles/pursuit-12fps`; the original
7 fps experiment remains in `profiles/pursuit-before-optimization`.

Sinistar is drawn only when its entire rectangle fits at top-left x=0-199,
y=40-132. Partial-edge clipping and broader raster coverage are pending. The
existing ECM quantization remains; frontmost covered cells select the palette.
Stars remain white with deterministic wrapping. The mouth stays closed until
speech synchronization is connected.

## Reproduce

From the main workspace:

```powershell
python port/scripts/build_scene.py
& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify.mjs
& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify_scene.mjs 12000
& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify_scene.mjs 12000 --stress
& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify_scene_math.mjs
& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify_relative.mjs
& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' port/scripts/verify_scene_stop.mjs
python port/scripts/verify_fuse.py --scene
```

`scene-manifest.json`, `scene-verification.json`, and `scene-fuse-report.json`
identify the tested cartridge. See `MEMORY_MAP.md` for RAM and banking details.

## Input and mining-kernel checkpoint

Click the emulator, then use Q/A/O/P for up/down/left/right, including diagonals.
The first direction takes over from autopilot. Release directions to coast; D
resumes the scripted demo. Native TS2068 joystick 1 supplies the same eight
directions through AY register 14 and port $01F6. The adapter initializes AY
register 7 to $3F (silent channels, port A input). Gamepads use TSRun's existing
joystick adapter. Fire/mining and bomb-launch buttons are not connected yet.

`src/controls.asm` maps digital directions to the existing source-derived turn
and acceleration routines. It does not emulate the arcade's 49-position stick.
The automated input test alternates keyboard and joystick contacts, tests
coasting and D, and checks both display planes and raster output. In 12,000
refreshes it renders 6,090 images, all 32 headings and eight pixel phases, with
zero incorrect/unchanged display writes, ROM writes, or raster mismatches.
Native Fuse boot/long-run checks pass; physical joystick testing is pending.

`src/mining.asm`, included in the diagnostic kernel cartridge, ports numerical
rules from FALS/N1ALL.SRC AddVib, TosCrys, and Vibrate using FALS/N1SYM.EQU:
- A hit increases vibration by inverse pseudo-mass / 4, unless already at the
  signed maximum. It preserves the source's overshoot behavior.
- Crystal release requires Richter > $10 and random <= Richter-$10; Sinistar
  cannot release a crystal. A release removes eight mass units (floor zero)
  and halves vibration.
- Damping subtracts two; negative vibration stops, and excessive on-screen
  vibration shatters a rock. Off-screen damping does not shatter it.

These pure routines accept RNG samples and return release/shatter events. The
197,120-case assembled-Z80 verifier covers all Richter/mass and Richter/random
combinations plus damping boundaries. Existing kernel tests also pass all
1,645,439 cases. Planetoid sprites, object allocation, vibration displacement,
crystal launch velocities, pickup, worker delivery, warriors, Sinibombs, and
Sinistar assembly remain to be integrated. This is not yet a mining game.

Saved checkpoint: `revisions/input-mining-v1`. Reproduce the new checks with
`node port/scripts/verify_mining.mjs` and
`node port/scripts/verify_scene.mjs 12000 --controls` using the configured Node runtime.

## Mining integration follow-up

The independent native mining cartridge now connects visible planetoid and
crystal sprites, firing, hits, release, pickup, and shattering. Open
http://127.0.0.1:8768/port/mining-web/ and see MINING.md for its deliberately
limited object pool, test adapters, memory map, and verification results.
This pursuit cartridge is preserved; the two scenes are not yet merged.
