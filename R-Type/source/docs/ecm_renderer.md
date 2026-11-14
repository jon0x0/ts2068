Current first-screen fix and measured scan optimizations: [r14](r14_initial_terrain_speed.md).

r13 terrain motion correction: [coherent palette contract](r13_terrain_motion.md).

Current r12 changes and validation supersede historical details below; see [r12 graphics](r12_graphics.md).

## r8 optimized builds (2026-11-01)

Use build/ecm_native/RType_level1_ECM_TSPico_RAM_r8.dck for live ECM on writable
TSPico SRAM. Stock64KB ROM output: build/optimized/RType_TS2068_64K_PicoROM_r3.rom
(and RType_level1_native_ROM_optimized_r3.dck). All original-colour ROM bytes fit
65536; ECM is still not ROM-only. Original r2/r7 preserved.

Implemented shared unrolled mirror copies;97 deduplicated sprite-colour rows
(776bytes); retained128-cell HUD history;160 prepared scroll-row pointers with
unrolled copies. Existing art, original title/menu and collision semantics retained.
All9872 cached-cell CPU cases pass. Natural-window updates:ECM113->122(~8%),
classic151->152(~0.7%); not universal FPS. See docs/performance_optimizations.md
for memory ownership, scripts, hashes, exact tests and timing limits.

Expanded512KB asset compiler is implemented:480 terrain phase variants,168920
bytes after row deduplication,all8 original level payloads. Full bundle at
build/expanded_cache/RType_level1_assets.ram512,with184884 bytes free. STAGING ONLY:
current game does not read the extra banks; native banked scrolling consumer and
loader remain outstanding. Do not deploy it as a PicoROM/DCK or claim a512KB
runtime speedup. No firmware was changed and no physical test performed.

## r7: rejected colour treatment removed; stable original menu (2026-11-01)

Use `build/ecm_native/RType_level1_ECM_TSPico_RAM_r7.dck` and matching initial
SRAM `.bin`. User rejected both r6 title treatments and reported flicker after
movement/recolouring. r6 is superseded and must not be described as accepted art.

The r6 menu wrapper republished all768 legacy cells, then overpainted chrome
attributes, on every input poll. Live display fetches could see both palettes.
It also sampled colours from arcade geometry onto different Spectrum geometry;
this did not provide a faithful chrome conversion. r7 removes that path and
retains the original title bitmap/movement and original8x8 menu colours. No title
asset is installed, no live menu-plane repaint, and menu stays mode0. Enhanced
actor/explosion ECM remains in gameplay. Scene material ramps are removed too:
level tiles and entering columns use their original source attribute, replicated
over8 scanlines. Correct retained-plane scrolling and dirty colour repair remain.
This is a stability/art rollback, not a completed replacement multicolour title.
Future title enhancement must use matching bitmap/palette geometry and publish
without repeatedly overwriting a visible title with a different palette.

verify_title_flicker.py reproduces three r6 palette oscillations at69AA:47->45
(hex) per poll. In200 displayframes, r7 services6842 native input calls with zero
menu-plane repaint calls and mode0. This proves removal of that oscillation;
original bitmap motion is intentionally retained. Tests also pass:8 full-shadow/
entering-column cases including live attrs and both IFF states;8 repair-path
comparisons;272 actor tile cases; key selection/start; controlled up/down route
92 displayframes,zero trails/IDs/deaths. At8000 frames returns to mode0 menu.
Actual captures: probe3000_r7.*,probe1400_joy_r7.*(coherent publication),
probe8000_joy_r7.* under build/ecm_native. No physical hardware claim.

BIN SHA256 5b553e6534e1205d493163ad99fa05947450d0c14a87a21fa8a895486c0e0be8
DCK SHA256 301da36ce0a74bec403aca0cd23e7c250927b23bf5f13b7db864bf4a318840f5
Still writable DOCK1+2+3, not ROM-only PicoROM; native first level only.

## r6 scenery colour synchronization and multicolour title (2026-11-01)

Current playable ECM image: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r6.dck`.
Matching `.bin` remains an initial writable-SRAM image, not PicoROM-only output.
Palette-preserving title alternative: `RType_level1_ECM_TSPico_RAM_r6_title_preserve.dck`.

The previous scenery colour changes were not authored palette animation. The
original $8CD8 engine moves legacy attributes and IDs one character left, but the
retained ECM shadow did not follow. Its entering-column writer $89CF also bypassed
paint_tile, leaving absent/stale ECM colours at the edge. r6 hooks $8CDD after the
original scroll guard, shifting the shadow's columns2..31 to1..30 over160 gameplay
scanlines; borders and HUD remain untouched. $89FB initializes eight live/shadow
colour bytes for the entering column, using the same level shading palette as
the fallback tile painter. Actor palette/bitmap/collision semantics remain.

Compared actual arcade frame0540 title and frame1560 scenery. Arcade chrome has
white highlights, cyan/blue shadows and subtle pink fringes; scenery uses cream/
bronze surfaces, unlike our still stylized Spectrum art. The new title keeps the
Spectrum logo bitmap and applies arcade-derived per-8x1 chrome colours, black
paper and no FLASH. Primary colours use2.5x chroma; preserve-palette comparison is
also built. This is a static chrome treatment, not an arcade animation recreation
or full replacement scenery art. Actual screenshots and source comparison:
`build/ecm_native/title_r6_comparison.png`. Both menu styles use ECM; menu-only
publication is separate from gameplay input. ROM0 asset1B20,1130 bytes; all8 dummy
opacity bytes1B18-1B1F are reserved FF and builder-asserted.

8 whole-shadow scroll/column CPU cases (both IFF states, blank/ink/paper columns)
pass, including live column output, borders, HUD, registers and stack.272 renderer
cases,8 repair-path comparisons,4 repair-core cases,8128-byte metadata, key
selection/start and zero-trail/death retrace pass. Controlled route89 displayframes
versus r5's87. Natural600-frame window106 game updates versus r5's116 (~10.62 vs
11.62/sec at nominal60.1145Hz); includes death/restart and divergent simulation,
not matched-scene or hardware FPS. Colour-copy cost remains to optimize.
Frame8000 reaches the ECM menu normally. Original r5 and r2 are retained.
BIN SHA256 b42db62f1025b2274ca69adeb15de37a52e96e65718bfbe0cc649b4f20fd3d06
DCK SHA256 acaeafe9512da8ce1749c8e4998d111bb17f081ab3d48e3415eb5f5c56999630

## r5 frame-update repair (2026-11-01)

Use `build/ecm_native/RType_level1_ECM_TSPico_RAM_r5.dck` (and matching initial
SRAM `.bin`). r4's colour repair was called for every scanned cell, including
clean sky: about530 calls per game update. r5 leaves original $8883 branch intact
and hooks only actual nonempty copies at $8886 and dirty-sky clears at $88BC.
Clean cells incur no added CALL, bank switch or interrupt masking. Colours and
collision bookkeeping remain intact; writable DOCK1+2+3 are still required.

Measured Fuse TS2068 frame1400-1999 natural trace: r4 completes64 game updates,
r5 completes116, classic151. Nominal60.1145-Hz normalization gives6.41 /11.62 /
15.13 updates/sec. These are game-loop entries, not whole-picture/raster timing
or physical-hardware FPS. Natural runs diverge in simulation state; r5 includes
a116-display-frame death/restart gap. Controlled identical up/down sky route
improves164 displayframes(r4) to87(r5), with zero trails/IDs/deaths in both.
Further tile-shader/publication optimization remains; ECM is still slower than
classic. See scripts/measure_frame_rate.py and build/diagnostics/performance.

8 original-versus-patched repair cases verify exact bitmap, dirty marker, CPU
registers/flags/stack and IFF, including clean-cell no-write. 4 repair-core cases,
272 tile-hook cases, held-Enter key selection/start, and frame8000 run pass.
The latter reaches mode0 attract after natural play; no continuous-live-ship claim.


# r4 correction: retained background colours

The r3 description below is historical where it conflicts with this section.
r4 fixes a missed self-modified operand at8EBF and incomplete dirty-cell colour
restoration. Source bitmap base40 means live HOME4000;60 means retained game
buffer DOCK3:6000. Shader now returns that exact base/flags to the original pixel
writer. Attribute destinations are HOME6000 for direct draw and DOCK2:4000 for
retained draw. Writable DOCK2 is reusable only after its original bootstrap
payload has been copied to HOME4. Initial mirror fills both colour planes.

Dirty code8842 restores pixels outside the tile painter. The gate at8883 replays
its conditional JP semantics: nonzero background ID restores all8 attr rows from
DOCK2; zero ID removes old paper/FLASH using original legacy ink/BRIGHT. It does
not copy stale actor colour into an empty sky cell. Both branch paths preserve
original PUSH HL/caller stack, flags, registers, IFF and collision ID. Mask07
makes DOCK0 code/DOCK1 mode shadow/DOCK2 source and HOME3 destination visible;
DI protects this mapping and normal09 is restored before return.

r4 descriptors:2,3,3,3,2,2,2,2. It requires writable DOCK1+2+3. Metadata and asset
requirements otherwise remain. The initial64KB SRAM image is not a ROM image.

Tests:136 CPU cases per draw base40/60 (272 total); empty and retained restoration
under IFF0/1 (4 cases), including FLASH removal;8128 metadata bytes;4096 native
input cases; repaired key-selection/start; natural explosion and8000-frame run.
The 8-cell up/down route has zero strips, dense leftover bits, stale collision
IDs or deaths after deferred publication. Original r3 fails visible-strip check,
but also had no death/stale collision ID on that tested route. Do not equate a
coloured-paper artifact with a proved collision object. Normal hit detection
remains enabled. Physical tests and full-game validation remain outstanding.

Current tile-hook CPU samples: direct1674-1806 T-states, retained1676-1812;
not full-game FPS. Added RAM changes boot timing; probe_ecm.py starts afterframe800
and key-selection tests shift their input windows400 frames for the ECM model.
State-driven movement regression does not assume an active ship at a fixed frame.

# Live ECM gameplay r3: writable DOCK prototype

This is a first-level TS2068 ECM gameplay prototype, tested in Fuse. It shades
original Spectrum sprite geometry; genuine arcade graphics replacement and full
RGB cell composition remain separate work. Both art directions remain in the
arcade asset pipeline; this gameplay test leads with saturated authored shading.

## Memory contract

| DOCK chunk | Initial contents | Runtime use |
|---|---|---|
|0 ROM|Palette families, paired-paper maps, shader1400, native input1A00, key completion1B00|Resident|
|1 RAM|Snapshot6000-7FFF|Source metadata2000-3FBF after payload copied; bootstrap stack/mode shadow3FC0-3FFF|
|2 ROM|Snapshot8000-9FFF|Boot transfer|
|3 RAM|SnapshotA000-BFFF|After copying HOME5, replaced with logical6000-7FFF game workspace|
|4 ROM|AROS bootstrap|Boot only|
|5 ROM|SnapshotC000-DFFF|Boot transfer|
|6 ROM|SnapshotE000-FFFF|Boot transfer|
|7 ROM|Snapshot4000-5FFF|Boot transfer|

DCK descriptors are2,3,2,3,2,2,2,2. Flat64KB image is an initialization image
for writable SRAM, not a physical ROM cartridge. TSPico is already known to
provide512KB; this prototype occupies a selected64KB region and does not yet use
the other regions or define their storage allocation. Firmware-specific physical
loading/MEMDOCK priming and deployment remain untested here. No SD command or
firmware replacement is introduced by this renderer.

Runtime HSR09 exposes resident DOCK0 plus writable game DOCK3. Game logical
6000-7FFF remains writable as before while HOME6000-77FF holds ECM attributes.
HSR0B additionally exposes DOCK1 metadata. HSR03 exposes ROM0 and metadata while
unmapping game DOCK3 so shader writes reach HOME attributes. Stack is HOME upper
RAM and shader code remains in DOCK0. No code executes from the switched window.
The original full IM2 vector and ISR remain visible in HOME4/HOME5.

## Source metadata and texture

Boot walks111 original generic descriptors atBC67 (786 headers,617 nonempty
cells). Header metadata encodes local source scanline and horizontal variant.
Per-pixel-byte metadata marks original FF strips. For black-paper source cells,
those FF bytes become fixed55/AA texture in writable HOME sprite assets. They
get two nonblack foreground colours sharing BRIGHT, so all eight original
occupied pixels remain occupied. Non-FF edge bytes remain unchanged and retain
black paper. Transparent36 cells remain skipped. Original archives are unchanged.
Metadata is built in DOCK1 only after its original payload is copied; tail64
bytes are owned bootstrap stack/mode shadow, not guessed free game workspace.

The ROM0 hook replaces original8EA2 entry, reproduces ID/attribute writes,
original override8EB1, pointer advance and result flags, then publishes eight
ECM attribute bytes. Vertical mirror callers8DFD/8E57 reverse those rows;
horizontal variants preserve source-relative texture with the existing bitmap
flip. It preserves BC/DE/HL/IX/IY, AF result and IFF state.

To avoid the LD A,I P/V race, the hook first inhibits the periodic source using
owned DECR shadow OR40, then samples IFF2 and DI. It restores DECR mode and HSR09
before restoring the caller interrupt state. Both game0/2 video modes are shadowed
at DOCK1:3FF0. Mainline input gateways are explicitly enabled-IRQ callers; they
DI around the existing native reader then EI, without racy IFF sampling.

Hooks8640 and8689 wrap original initialization86C3 and end-stageC2D6. Initialization
mirrors the original attributes once; end-stage mirrors HUD rows20-23 only. It does
not scan/recolour the whole screen each frame. Menu7796 restores mode0. Native
keyboard and both joystick ports remain active; r2 held-Enter repair remains.

## Evidence and practical limits

- verify_ecm_phases.py:8128 metadata bytes exactly match independent Python walk.
- verify_ecm_renderer.py:136 real-Z80 cases cover four mirrors, IFF0/1, original
  forced-attribute path, registers/flags/stack, logical ID/attribute writes and
  exact eight output attributes, including paired foreground cells.
- IRQ-off tile samples:1565-1700 T-states, mean1617.8. This includes the hook,
  not just8 writes. It is not a whole-game FPS measurement or hardware benchmark.
- verify_native_input.py --ecm:4096 input cases pass.
- verify_key_selection.py --ecm --label fixed:one entry, six bindings retained,
  fire starts and player-update checkpoint reached.
- Live frame800:port1 right X4->6,port2 left X4->2,Y10,pose3.
- Live developed explosion:source54,frame984, five nonblack colours, two8x1 strips
  contain two nonblack colours. 512 source-cell pixels match original occupancy.
  First pose4B atframe964 has eight paired strips. Transparent/background cells
  are excluded from source-occupancy comparison, not invented as known artwork.
- Frame8000 returns to attract with video shadow0. Captures explicitly unmap
  game DOCK3 before dumping HOME display; logical player state is read separately.

Full arcade sprite shapes, per-asset palette refinement, background/sprite cell
clash resolution, performance optimization, stock-ROM RAM relocation, complete
level packing/loading, enhanced audio, full512KB game banking and hardware tests
remain. Existing renderer layer order/repair is reused; this is not a claim of
unrestricted multi-colour pixels, completed arcade restoration, or tear-free output.
