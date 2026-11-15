# R-Type test history

## 001 - source inventory, 2026-11-01

Original archives retained. Arcade ZIPs identical, SHA-256:
F995DD172E83C1B6ADAAE72CAC4A9BFF62ACD4A2E9A6BD10415A8C546CE32EEB.
Standard TAP has eight level payloads [13228,12856,13074,12998,8904,8849,12997,11980],
total 94886 bytes. All eight match +D-wrapper payloads. Standard TAP itself is
132823 bytes; 128K Torasoft TZX is 95309 bytes and BASIC states 128K REMIX BY
TORASOFT '93, with trainer menu. Code Monsters pair are separate disk-style
members, not assumed to be equivalent tape baselines. Full hashes/CRCs/names:
`build/source_inventory.json`. No claim of native game execution yet.

## 002 - reference reuse and arcade captures

Read graphics skill plus graphics, buffering, precomputed and optimization
guidance; examined Sinistar asset preparation and retained/damage renderer.
Reuse mask/phase/data contracts, not its game-specific addresses. Read speech2ay
integration contracts and TSVideoCodec intro/dithering guidance. User confirms
512KB TSPico use is already demonstrated; do not treat capacity as unproven.

MAME 0.289 initial verification found the supplied 20 functional ROMs valid,
but five archival PROM/PLD dumps missing. m72.cpp/m72_v.cpp/m72.h show these
regions are not palette sources/consumers in the emulated device configuration.
Capture tool creates labelled diagnostic stand-ins only for archival regions;
it rejects missing functional ROMs. Checksum warnings remain in mame.log.
Do not label stand-ins authentic ROMs or use them for hardware programming.

First captures at frames420,540,660,900 inserted coin/start before boot completed;
they showed title and attract/game-over content. Retimed electrical inputs:
coin720..729, start780..789. Accepted captures at 420,540,660,900,1080,1320,1560,
1800 cover title and actual gameplay/death. Initial capture files were replaced
by this deterministic run. Source screenshot and palette data are originals.

Artifacts: `build/arcade_capture/frameNNNN.png` and matching `_palette_sprite.bin`,
`_palette_tile.bin`, `_sprites.bin`, `_tiles0.bin`, `_tiles1.bin` (48 files total),
`capture.lua`, `mame.log`, `rom_audit.json`. Repeated with zero rather than FF
archival fill under `build/arcade_capture_zero/`: all 48 outputs byte-identical.
Result recorded in `build/arcade_standin_validation.json`. No functional ROM or
palette data was fabricated. This validates these captures, not physical hardware.

## 003 - arcade decode and finite masked phases

Decoded 4096 sprite tiles (16x16, four bitplanes) and two 4096-tile banks (8x8).
Mirrored sprite ROM tails are preserved. Extracted ship code34/colour0 at frame
1320, assembled code+8*x+y, matches screenshot opaque pixels 100% at x123,y102.
Enemy sample uses code54/colour5. Palette comes from game-populated 5-bit-channel
RAM, not a guessed RGB list. Source indices and palette are in decoded_indexed.npz.

Generated eight finite 0..7 phases with transparent spill margins and preserve
mask=1 semantics. Quantize once per row, shift bitmap/coverage together. Black-
paper palette policy is explicit; arbitrary coloured backgrounds require
composite-cell palette resolution later. No runtime sprite-engine claim.

Artifacts under build/graphics: ship_arcade.png, ship_arcade_large.png,
enemy_arcade.png, enemy_arcade_large.png; ship_phase0..7.bin, enemy_phase0..7.bin;
ship_rigid_phases.gif and enemy_rigid_phases.gif. Each 32x16 pose costs 912 bytes
for candidate even phases or 1872 for all eight. Four-phase use requires proven
two-pixel motion/fixed parity; not yet selected for the real game.

## 004 - ECM conversion comparisons

Initial scene1320 comparison was replaced with busier scene1560. Uniform scaling
384x256 -> 256x171, letterboxed in 256x192, preserves proportions. The baseline
8x8 panel is an arcade-image conversion under Spectrum colour constraints, not
the original Spectrum game screenshot. Both display planes use nonlinear offsets.

Final scene1560 results (RGB MSE is one metric, not subjective acceptance):
- 8x8 baseline: MSE843.092, 9 distinct RGB colours, 10 attribute pairs.
- 8x1 Sierra Lite: MSE650.287, 14 colours, 25 pairs.
- 8x1 ordered: MSE797.223, 14 colours, 25 pairs.
- Full-row coherent: MSE883.016, 9 colours, 9 pairs.
- Explicit 2.5x chroma-emphasis artistic source: 15 colours, 31 pairs.
The colour-emphasized option is deliberately labelled, not called original RGB.
No inference about temporal quality, streaming speed or final compression.

Artifacts: arcade_reference.png; spectrum_8x8.png/.pix/.atr; ecm_sierra.png/.pix/.atr;
ecm_ordered.png/.pix/.atr; ecm_row_coherent.png/.pix/.atr;
chroma_emphasis_source.png; ecm_colour_emphasis.png/.pix/.atr;
comparison.png, colour_comparison.png, dither_comparison.png.
Title artifacts: arcade_title_reference.png, title_spectrum_8x8.png/.pix/.atr,
title_ecm_sierra.png/.pix/.atr, title_comparison.png. Detailed hashes/metadata:
graphics_report.json. All previews decoded/round-tripped from legal pairs;
FLASH off. The ship Sierra bitmap and attributes exactly match the existing
graphics skill's scalar reference (serpentine 1/2,1/4,1/4 diffusion).

## 005 - native 64KB graphics proof

Early viewer cycled four frames. Accepted viewer cycles five: colour-emphasis
ECM, palette-preserving ECM, 8x8 baseline, ordered ECM and ECM arcade title.
Five raw images consume 61440 bytes. Resident code/descriptors use 1830 bytes
below $8800 in DOCK4; data uses seven full chunks plus DOCK4 tail from $8800.
Output BIN65536 bytes; DCK65545 bytes, DOCK bank0, eight ROM descriptors.

AROS EF lower-chunk specification, entry8008; HSR10 baseline, DECR02, SP7FFF,
DI throughout. Source transfer maps source+DOCK4, uses a visible HOME bounce
buffer (7B00 for source2, 5B00 otherwise), then restores HSR10 before display
writes or stack access. No ROM writes or unverified ROM services. This viewer
does not establish a flicker-free game renderer, frame rate or audio coexistence.

All five pages captured in Fuse1.7.0 TS2068: every bitmap/attribute byte matches
the generated 6144-byte planes. SP7FFF at every checkpoint. Previews match the
decoded live RAM. Verifies transitions including source2 display overlay, source3
stack overlay and the resident-bank data tail. Twelve restarted 1024-byte chunks
per frame; no debugger state injection. Human-readable src/graphics_proof.asm
assembled with SjASMPlus1.20.3: zero errors/warnings, byte-for-byte identical to
the emitter. A metadata-only rebuild retained the same accepted cartridge hashes.

Artifacts: RType_ECM_graphics_proof.bin/.dck, proof_manifest.json,
proof_descriptors.bin, proof_resident.bin, proof_resident_assembled.bin;
fuse_ecm_colour_emphasis.png, fuse_ecm_sierra.png, fuse_spectrum_8x8.png,
fuse_ecm_ordered.png, fuse_title_ecm_sierra.png; each with `_4000.bin` and
`_6000.bin`; fuse_validation.log/json. These are static graphics pages, not
playable R-Type screenshots. Physical confirmation remains pending.

BIN SHA-256: A6BA5C4B20CFEBB1465CDA418E748F87D0E2A1A5A3F9B8B21BEE1B4010DDB81A.
DCK SHA-256: B4B561EAB1399ACAF617B422784716FF745E47D27FFA62DC1AAF3DA7E0B9B0E7.

## 006 - regression tests and current limits

tests/test_graphics.py covers independent known row addresses, decoded ROM
shape/range/mirroring and exact arcade pixel match, every finite sprite mask/
phase with rigid dither, and exact Sierra reference output on the ship.
Run results are retained in build/unit_tests.log.

Not implemented: native gameplay port, scrolling compositor, runtime mixed-cell
palette resolution, full-game cartridge packing, TSPico game integration,
speech2ay effects, TSVideoCodec opening animation. These are next work, not
features inferred from the graphics proof. Ordered TSPico streaming remains an
explicit performance comparison; no blanket quality/performance claim is made.


## 007 â€” original Spectrum execution and checkpoint

scripts/capture_spectrum.py captured original standard TAP on Fuse48 at frame8000
(REWIND SIDE 2 prompt) and frame14000 with first scripted Space (STOP TAPE
prompt). Images, SCR files, CPU JSON and debugger logs are retained under
build/spectrum_baseline/spectrum48_frame8000.* and
spectrum48_frame14000_started.*. These are original Spectrum diagnostics.

scripts/capture_checkpoint.py applies electrical Space input at the keyboard
scanner after frame8100 and frame14500. It reaches original $8634 immediately
after the level-loader returns at frame14500. Saved all 49152 bytes of RAM and
CPU state before freezing interrupts; the three bytes used for the capture loop
are restored in the saved image. SP=$FFFE, I=$84, IM2, IFF1=IFF2=1.
RAM SHA256: 6cfc8fddab6749c3d7e869a57dda9a73e01b095228cc6369afbe99e1978ad7af.
Artifacts: postload_4000_FFFF.bin, postload_checkpoint.json/.log/.commands.
No native gameplay or hardware claim follows from this Spectrum checkpoint.

## 008 â€” art direction confirmed

User selected keeping both palette-preserving and colour-emphasized ECM styles
for comparison. Both already exist in the five-page native proof. Ordered
dithering remains a comparison for the existing TSPico streaming approach;
Sierra Lite remains a preconversion option. No additional runtime measurement
was performed for this preference update.


## 009 - native level-one bootstrap and input (2026-11-01)

Built native copy-and-run DCK65545/BIN65536 using original postload checkpoint.
First unpatched baseline hash AEE1CEF56D1103CEFD64987ED18E76627CE2F7ADDCCF4546327D14C864123391.
At handoff all49152 bytes matched the original saved state. Initial original-input
captures: probe_300, probe_1200 (attract/title/highscores), probe_900_started and
probe_2000_started (scrolling gameplay). Each diagnostic has .bin/.png/.json,
.commands and .log under build/native. These initial diagnostics predate input patches.

Rejected RAM-input prototype hash837259D82BE36A0EFCB99738026BE2112A7DA202855B811B56F9E181A7EECA42:
$8540 appeared empty but is cleared during game initialization. Assertions caught
its removal at frame900 and later probes. This version is superseded; no RAM
reservation remains in final code. Failed prototype raw captures were replaced by
the corrected ROM-input captures with the same _joy diagnostic names.

Accepted ROM-input build hash511564E509CD60FE89FAE201E12D87CBA306B15D28213CE815B0DACC5783B757.
DCK hashF64EA0D3B9C68719042417567F53A54F0E929C11AC81EB525420DE2892AAB181.
Native input moved to persistent DOCK0 $1A00; source of HOME2 moved to DOCK7.
probe_0: all49152 RAM bytes match patched snapshot, SPFFFE, I84, IM2, IFF1/2=1.
A=1 selects final HSR; first original routine overwrites A before reading it.
All other general registers/flags match saved checkpoint. R/frame phase not restored.
Rebuild after source cleanup retained the exact accepted BIN hash. Assembly has
zero errors/warnings. No ROM descriptor is writable and BIN has no DCK header.

Corrected native-fire captures probe_900_joy, probe_2000_joy, probe_8000_joy show
continued execution through original gameplay/death/attract paths. They are not
complete-level validations. Live electrical fire is injected at port1 IN result
frames400-429. No player/game state is forced in gameplay probes.

Initial movement tests at frame520 failed to move: ship was in its initial
collision/death interval (pose0). Recorded probe_520_joy and both
probe_520_joy_move8_port1 / move4_port2 diagnostics. Repeated in live pose3:
probe_1820_joy X8,Y10; move8_port1 X12,Y10; move4_port2 X4,Y10.
Directions injected only at native IN results during frames1800-1809.
All three have RAM, PNG, CPU metadata, commands/log; gameplay_input_validation.json
retains the coordinate comparison. This verifies both native ports affect game motion.

First natural-game exhaustive-input harness timed out after55s; replaced with
isolated real-ROM CPU contract harness (explicit state setup, not gameplay).
verify_native_input.py:4096 cases pass (1024 two-port combinations x two keyboard
states x two interrupt states). Checks A/Z result, interrupt preservation, DE/HL
and stack balance. input_cpu.commands/.log/.json retained. All four existing
asset regression tests pass. No claim of physical joystick or audio testing.

## 010 - compatibility and ECM relocation audit

audit_native.py traverses5469 instructions from explicit entry/input/IRQ/loader
seeds, emitting compatibility_audit.json and reachable_disassembly.txt.
$8F2A CALL $0562 remains unconverted tape dependency. $9460/$FF52 CALL0000 are
self-modified dispatches with operand writes $9455/$FF48; do not patch as ROM calls.
135 candidate references into $6000-$77FF demonstrate ECM-plane ownership must
be resolved before enabling mode2. Static coverage remains partial due to indirect
branches, self modification, inline data and later-level overlays. No additional
ECM gameplay, speech2ay or TSPico integration is implied by native baseline.

Independent skill inspect_dck.py confirms all eight ROM descriptors, AROS8008/EF,
safe lower HOME chunks and exact expanded BIN equality (65536 bytes). Reports
build/native/dck_inspection.json and expanded_verified.bin retained.


## 011 - r2 key-selection loop repair (2026-11-01)

Reproduced user report on accepted r1 hash511564...: open with Enter, select
O/P/Q/A/Space/Enter and hold final Enter until frame710. At frame850 the original
routine had entered twice, stored six keys, then cleared the whole table on
re-entry. keys_before.commands/.log/.json preserve this reproduction.

Patch $BFD0 CALL $C2C5 -> CALL $1B00. ROM wrapper calls the original completion
routine, saves AF/BC/DE/HL, polls original keyboard scanner $BF55 until D=$FF
(all released), restores registers and returns. No game RAM code cave, key table
layout, joystick path, interrupt scheme or graphics change.

verify_key_selection.py --label fixed: at frame1200 entries1, stores6,
control_type2, bindings DF02 DF01 FB01 FD01 7F01 BF01 retained. Chosen Space
fire starts game; $863D start and $94F1 live player-update checkpoints both reached.
An initial extended diagnostic wired the added two breakpoint command numbers
incorrectly; corrected numbering passes both checks. The earlier six-key/r2
selection-and-start check also passed independently before this extension.

4096 real-CPU native input cases and all49152 handoff bytes pass after patch.
probe_2000_joy confirms continued gameplay with native fire. Relevant existing
probe_0 and probe_2000_joy artifacts now carry r2 cartridge hash. Other earlier
probes retain their original diagnostic provenance from history009.
Skill inspect_dck.py confirms all ROM descriptors, valid AROS and exact 65536-byte
expanded image equality. dck_inspection_r2.json and expanded_verified_r2.bin saved.

r2 BIN SHA256 EF2B9E08DF9D21244C565EAE3E8A42BDEA95B35E279CEBE3AB2F0F743B9DA871.
r2 DCK SHA256 F3FE5A76FE4C97626A9DA725DC21E650AB9E8DB710BDA1A975FDBAF067EB0B91.
Both versioned _r2 files and unversioned aliases contain the accepted build.
Physical confirmation of this fix remains pending. Other native baseline limits
(ECM gameplay, later levels, enhanced audio, TSPico game banking) still apply.


## 012 - live ECM writable-DOCK bring-up and rejected passes (2026-11-01)

User correctly identified that the playable r2 build still used Spectrum8x8
colour and monochrome explosions. r3 is a separate TSPico SRAM branch, keeping
stock r2 byte-identical. DOCK3 becomes writable game6000-7FFF, freeing HOME3 for
ECM. DOCK1 becomes writable metadata only after copying its original payload.
No physical SRAM deployment or extra-region512KB game allocation is claimed.

Initial whole-cache colour pass hash564210F109ACC86C8EA25DE8FCFF9AF4242FA5F20FD4123EC7F87CA128428C56:
probe900/1820/4200 showed added colour but later1820/4200 RAM was identical at
868C with IFF0 (stall). interrupt_trace.log showed LD A,I interrupt-state sampling
race in the long mainline critical section. Fixed mainline input/publisher
contracts without inferring a safe RAM code cave. Rejected full pass also cost
roughly8-11 emulated frame intervals per publication in that trace.

Optimized cache scan hash1BA0772D9399E761F16928D4469044AFAD4B34BA0032E2D05B29C04BAE735370
continued gameplay, but publishing before object draw read stale/cleared collision
IDs and recoloured explosions incorrectly. Moving hook into868C wait loop
(hashDDFCD9CE8F065612C197FB0291D7A7A9895DBC8D6C05812F244629A91E64732F)
caused redundant publications while waiting for frame counter. Superseded by
end-stage8689 hook (hashCFBB21351CD77040F2E3A6EC91D1418731C6D2E38C22A5930CD15F7A7FBBD02F).
That pass demonstrated five live fire colours but retained expensive frame scans.

Prototype diagnostics: build/ecm_native/probe_900_joy.*, probe_1820_joy.*,
probe_4200_joy.* and explosion_joy.* (.commands/.log/.bin/.json/.png). Several were
regenerated under later builds; their saved JSON cartridge hashes identify the
actual retained version. Earlier failed capture triggered repeatedly because its
time condition lacked armed==1; corrected before accepting the dump. A later
capture requested4E-51 but the natural first collision uses sequence57-52/4B,
so that request reached its bounded deadline. No game state was forced to create
an explosion. Developed54 and first4B were subsequently captured successfully.

## 013 - per-tile ECM publication and source-relative shading

Replaced full-screen scanning with original tile-helper8EA2 -> ROM0. The helper
replays original ID/attribute writes, override8EB1, pointer/flags, then publishes
8 attribute rows with local sprite Y/X metadata and mirror handling. Initial
per-tile hashD0005F65B4F4F9978E07D22F16C6A876E2282FC30A6B1FCABC6D8C5652F59F5B
passed68 normal/vertical mirror CPU cases, all4096 native input cases, key-selection
regression and continued gameplay/return to attract at8000. Ship and explosion
art now use actual ECM planes during gameplay, not just the graphics viewer.

The first isolated renderer harness waited for an unpressed menu start, then a
terminal entry breakpoint was skipped after PC reassignment; bounded
 tile_cpu_diagnostic.log identified all cases had executed. Terminal NOP checkpoint
fixed the harness. Conditional same-address last-case breakpoints were also
replaced so final cases actually execute. Current test has one terminal instruction
checkpoint, rather than accepting an unexecuted final setup as a pass.

Source-phase walker independently verifies all8128 nonreserved DOCK1 bytes,
786 headers and617 nonempty cells. Phase table tail64 bytes explicitly owns boot
stack and DECR shadow. Native branch bitmaps/code remain outside the HOME ECM
plane. HUD rows20-23 mirror original attrs; mode0 restored on attract/menu.

## 014 - r3 paired foreground colour, final accepted RAM prototype

Final BIN/SRAM initialization SHA256:
368FDF50E000D03FC510B3ADDE189EEEA5224415F0F3E137E69D0AB25C509780.
DCK SHA256 DAD528A788C24414384781C2F4EBE0CE0A2AE14B4328FABE453994DB5E4B081B.
Files RType_level1_ECM_TSPico_RAM_r3.bin/.dck; unversioned aliases match.
Build reproduces classic r2 first; its BIN remains accepted EF2B9E08... unchanged.

Only original FF pixel rows of black-paper generic sprite cells become fixed
55/AA textures. Metadata marks those original full strips; shader supplies two
nonblack foreground colours sharing BRIGHT there. Partial edge bytes and skipped
transparent cells remain unchanged. This permits intra-8x1 colour detail without
painting coloured bounding rectangles. Original archives and raw stored source
assets remain unchanged; transformation occurs after copying into writable HOME.

Final verify_ecm_renderer.py:136 real-Z80 cases, four mirror return paths,
both IFF states, default/forced original attributes, exact original AF/BC/DE/HL/
IX/IY/SP, legacy ID/attribute writes and eight expected ECM attrs. Paired ink/paper
output included. IRQ-off tile-hook samples1565-1700 T-states, mean1617.8 over66
samples that did not cross frame boundary. This is not whole-game FPS/hardware
performance. Renderer code416 bytes plus separate palettes and existing input.

verify_ecm_phases.py checks8128 bytes including full-strip metadata exactly.
verify_native_input.py --ecm:4096 cases pass.
verify_key_selection.py --ecm --label fixed:one entry, six bindings retained,
start and player update reached. Original held-Enter fix remains.
All four asset regression tests pass. Skill inspect_dck.py recognizes valid AROS,
descriptors2,3,2,3,2,2,2,2; dck_inspection_r3.json retained. This is initialized
RAM, not a ROM-only PicoROM image. Flat .bin size65536 is not proof of ROM compatibility.

Actual HOME RAM captures in build/ecm_native:
- explosion_joy: source54, eventframe980, captureframe984 at next8B06 after end-stage
  publication. Five nonblack hues, two8x1 strips contain two actual nonblack hues.
  512 original-source pixels in nontransparent cells match occupied silhouette,
  mismatches0. explosion_colour_validation.json and explosion_silhouette_validation.json.
- explosion_4b_joy: eventframe959,capture964; eight paired foreground8x1 strips.
  Retained explosion_4b_joy_paired_cells.json. Empty/background source cells are
  not counted as recovered geometry.
- probe_800_joy: X4,Y10,pose3,mode2; hull cell40,84 contains cyan+white simultaneously.
  ship_detail.png / ship_colour_validation.json show this actual capture.
- probe_800_joy_move8_port1: X6; move4_port2:X2,Y10. Inputs only at electrical native
  IN results during780-789. gameplay_input_validation.json retains comparison.
- probe_4200_joy: gameplay/death progression,mode2.
- probe_8000_joy: attract return,mode shadow0. Capture decoder switches to legacy
  attributes when mode0; does not mislabel old ECM plane as live display.

Earlier1820 movement probes did not move because pose0 was a death interval;
retained probe_1820_joy and _move8_port1/_move4_port2 correspond to prior per-tile
build hashes. Final movement assertion is at800, not1820.

Captures carry full .bin RAM, .png, CPU/mode/player metadata JSON, commands/log.
HOME plane capture explicitly clears DOCK3 after freezing; logical player info
is read beforehand. Probe diagnostics set only electrical input before freeze;
isolated CPU tests deliberately set registers/state and are labelled as such.

make_ecm_comparison.py reproduces explosion_comparison.png and explosion_detail.png
from live HOME RAM. The white reference is the same occupied silhouette, not an
independent old-game screenshot. The true ECM panel includes paired-color texture.
No moving-image frame rate, tear-free rendering or physical hardware test claimed.
Existing sprite shapes remain Spectrum-derived, not full converted arcade artwork.
Further palette refinement, full RGB shared-cell composition, stock-ROM memory
relocation, complete multilevel packing/loading,512KB game allocation and enhanced
audio remain. Graphics requirement is progressed by an actual live ECM renderer;
original r2 is deliberately not relabelled as enhanced.


## 015 - r4 moving-ship 8x1 trail reproduction and fix (2026-11-01)

User screenshot shows cyan strips below a moving ship and reports collision/
explosion. Scripted upward input on r3 reproduced empty pixel bytes with paper
47decimal at(40,76)/(40,84). before_up .commands/.log/.bin/.json/.png and exact r3
DCK/BIN copies preserved in build/diagnostics/r4_trails; original user PNG remains
C:/Users/Jon/AppData/Local/Temp/codex-clipboard-d7e0fe73-459e-47e3-aa6f-4f0ea47c6edf.png.

Code audit found two bugs in r3: shim hardcoded ADD60 instead of reading original
self-modified8EBF(40/direct or60/background), and dirty restoration8842 never
restored ECM attrs after copying/zeroing pixels. r3 tests checked only base60;
claims of exact original helper semantics were incomplete. r4 keeps both modes,
uses writable DOCK2 as retained background colour, and patches8883 to a colour
restore gate preserving original NZ/fallthrough or Z/jump88B3 and PUSH HL stack.
Empty background IDs clear paper and FLASH; nonempty IDs restore retained colours.
No collision-death jump or immunity setting is patched.

First r4 draftD0080A49823C3DECA4D374C5B71C0CDC67406EF7EFE6D24D983F835CAF31D405
copied stale retained actor paper even for empty ID0. Expanded fixture detected
one remaining strip. Empty branch fixed. Early probes at800 missed menu start:
added writable DOCK2 changes boot/menu readiness toframe615; input400 was too early.
r4_start_trace.log confirmed no game start, not a crash. Probe start default800;
ECM key-selection electrical input windows offset400. Manual key handling is not
changed. probe_1200_joy_move1_port1.* retained from early draft/fly-in pose0.

Roundtrip fixture was initially captured at frame-end before original deferred
bitmap publication, detecting the legitimate immediately previous ship image.
Moved capture to next8B06, after original frame publication and dirty repair.
Pre-update input transition boundaries also adjusted to avoid overshooting targets.
These changes do not set game coordinates: only native post-IN values are injected.

verify_ecm_trails.py now waits for an active ship, moves up Y10->2, then down2->10.
Checks empty prior-route cells for coloured paper and dense residual bits and
reads27 collision-ID cells over rows2-10. Fixed r4: X4,Y10,pose2,frames1401-1565,
zero trails,zero IDs,zero deaths. Preserved r3:frames1118-1203 retains two strips
(40,20),(40,28), so expected test assertion fails. Its IDs and deaths were also0:
user-reported death was not proved to be caused by the visual strips in this
reproduction. No invulnerability workaround used. r3_roundtrip.* and r4.* retain
RAM/PNG/JSON/log/commands; before_after.png and *_path.png are actual image crops.

verify_ecm_restore.py:4 CPU cases verify empty/retained background IDs,IFF0/1,
legacyFLASH clearing, exact A/flags/BC/DE/HL/IX/IY, original stacked HL/SP and
untouched collision ID. verify_ecm_renderer.py:136 cases for each bitmap base40
and60 (272 total), all four mirrors,IFF0/1,original forced attrs. Checks exact
returned A/flags4010 or6034, original metadata and proper live/retained colour
planes. Saved tile_cpu_40 and tile_cpu_60 .commands/.log/.json. IRQ-off measured
ranges1674-1806/1676-1812 T-states; not an FPS or physical timing result.

Metadata8128 bytes passes; native input4096 cases passes; six-key selection retains
all six and reaches start/player update; natural source54 explosion event1871,
coherentcapture1879 has five colours,two paired foreground strips and512 matching
source silhouette pixels. make_ecm_comparison.py regenerated colour/silhouette
JSON and explosion comparison/detail PNGs. probe_8000_joy continues with active
ship X8,Y10,pose3,mode2; not the older r3 attract-return checkpoint. These shared
artifact paths now contain r4 hashes; history014 describes earlier r3 captures.
Skill inspect_dck.py validates descriptors2,3,3,3,2,2,2,2 and valid AROS;
dck_inspection_r4.json retained. Stock r2 hashEF2B9E08... remains unchanged.

Final r4 BIN/SRAM SHA256:
32832d91ae27f7b08b5a3ec8f674f8e5c5997b5e7e6f3f45422a7179e77e96cf
DCK SHA256:
298bbdcc565ebeb07ec280098462d7e73bd54db2a2fa4072d3f63259ff765258
RType_level1_ECM_TSPico_RAM_r4.bin/.dck and unversioned aliases are identical.
Physical TSPico validation, stock-ROM ECM relocation, full arcade art and full
multilevel support remain outstanding. This image requires writable SRAM1,2,3.

## 016 - Goodboy/Tiboh 2019 audio source verification (2026-11-01)

Primary VTRD release note confirms CPC/MSX alternatives and mouse support.
RTYPE_GT.zip SHA256 e6d307a87721fd190499c2a257a7c5d33c385acea58da73e274e18d87c529b86;
sole SCL member101161 bytes, directory/checksum checked. source.json, inventory,
file00/file01 and reference firmware provenance retained in
build/research/goodboy2019. Old release-page link unavailable; author forum403;
actual primary archive download succeeded.

Early missing-ROM and relative-ROM-path launches timed out; absolute matched
Pentagon/TRDOS reference ROM paths fixed startup. Forced PC3D00 skipped normal
128K initialization and did not yield working scripted input; discarded that
method. Normal menu electrical cursor/Enter, RUN/Enter and intro-key injection
boots correctly. Earlier unguarded dump-loop condition corrected to armed-only.
No user Fuse instance operated; only isolated child instances used.

pentagon_1200.*: disk-load blank screen, not a completed menu boot.
pentagon_3000.*: original R-Type title/loading screen.
pentagon_4000.*: actual 2019 menu, visible MSX/CPC sound selector.
All commands/logs/SCR/PNG/CPU JSON retained; research_goodboy_audio.py reproduces.
intro_entry.commands/log and intro_6000.bin capture loader at6000.
research_goodboy_banks.py captures bank3 at6008 and bank7 at85FD after normal
menu start; both exit successfully with8200 parsed words/header fields and16KB
output. player_bank3/7.commands/log/bin retained. Static disassembly verifies
intro init/tick/stop C000/C005/C008; game bank7 C000 writes FFFD/BFFD, C220
dispatches effects, C253 selects tune table, C684 initialises. Alternate game
hooks capture sound IDs at8F1F and call bank7. Full findings recorded in
docs/goodboy_tiboh_audio.md. No sound listening or complete-level audio coverage
claimed: Fuse ran --no-sound. No native game or cartridge images changed.

## 017 - frame-update regression profile and r5 repair (2026-11-01)

User reports infrequent frame updates. Read graphics skill optimization reference;
measure completed work separately from IRQ counts. New measure_frame_rate.py uses
isolated Fuse TS2068, --speed5000 (only host acceleration), electrical joystick
fire800-829, 600-display-frame window1400-1999; logs/commands/JSON under
build/diagnostics/performance. Counts loop8649, tile8EA2, scanned-cell8883, IRQBE23.
Classic151 updates/598IRQs; r4 64updates/296IRQs,33925 scanned cells. r4 masks IRQ
and maps banks for every scanned cell, including already-clean sky (~530/update).

First optimization retained gate and checked zero dirty marker:91updates/505IRQs;
4 core tests and retrace passed, but still extra CALL overhead per clean cell.
Superseded by actual-write hooks: original8883 JP Z88B3 retained.8886 CALL restores
nonempty ECM and emulates displaced LD A,H / ADD20;88BC CALL restores dirty empty
ECM and emulates XOR A / LD(HL),A / INC H. No clean-cell hook. Final r5 renderer603
bytes. Current benchmark JSON replaces intermediate r5 result. Final116updates,
495IRQs,1829 tile calls,61238 scanned cells. Classic/r4 retained outputs untouched.
Nominal60.1145 normalization:classic15.1288,r4 6.4122,r5 11.6221 game updates/sec.
Natural traces diverge after speed changes; r5 interval116 frames is a death/
restart gap, not a 116-frame single render. Counts are loop entries rather than
completed-picture publication/FPS or hardware performance measurements.

verify_ecm_trails.py --label r5: controlled routeY10->2->10,begin1129/end1216,
87 displayframes vs r4's164. Zero trails,27 zero IDs,zero deaths; actual RAM/PNG/
JSON/log/commands at build/diagnostics/r4_trails/r5.*. Original screenshot remains
in history015. verify_ecm_repair_hooks.py:8 original-versus-r5 cases (ID0/1,
dirty0/1,IFF0/1),16 Fuse runs compare exact CPU/bitmap/dirty-marker outputs and
expected ECM colours. Clean cells untouched. hook_*.commands/log and validation
JSON saved in performance. Existing repair fixture initially failed because it
stopped before new hook8886; updated to explicitly install conditional gate for
its isolated core-contract check, then4 cases pass. New actual-path comparison
covers the production hooks independently.272 tile cases pass, unchanged costs.
Key-selection6 keys/one entry/start/play passes. probe_8000_joy.* now r5,mode0
attract after natural play, not r4's frame8000 live ship. No freeze detected.

BIN SHA256 d57ea2d01cb6e5fa5e70265454f2de5f4484a92865e4c1eb6e8d3207d4a02f7a
DCK SHA256 44d106c6c5f5f1909e7e2dada2958e4c3d4c15918ba0ebb640bde661a4527c35
Versioned r5 and unversioned aliases match. r4 versioned image retained.
Stock r2 rebuilt byte-identical EF2B9E08... . Writable SRAM1/2/3 still required.
ECM remains slower than classic; physical validation and further optimization
remain outstanding. No audio changes included.

## 018 - scenery scroll colours and arcade chrome title (2026-11-01)

User reports bottom scenery changing colours and requests arcade-informed titles.
Read state/history and graphics optimization reference. Viewed actual arcade
frame0540 title (arcade_title_reference.png) and frame1560 gameplay; no downloaded
replacement images. Found missing ECM counterparts for8CD8 legacy/ID shift and
89CF entering-column writer. r6 hooks8CDD and89FB; full details in current state.

Build_title_attributes.py reproducibly quantizes existing arcade title with black
paper pairs. Preserve and2.5x-chroma assets1112/1130 bytes atROM1B20; original
Spectrum logo bitmap retained, per-8x1 chrome only. Actual title captures:
probe_3000.png(chroma),probe_3000_preserve.png; title_preserve_source.png and
 title_chroma_source.png are converted arcade-source previews, not game captures.
make_title_comparison.py uses current native bitmap+legacy5800 attrs for original
reference; title_legacy_reference.png and title_r6_comparison.png retained. An
initial comparison used r5 frame3000, which was the high-score attract screen;
corrected to exact original legacy colours rather than presenting it as logo.
probe_3000_r5.* retains actual high-score diagnostic, not title proof.

Initial r6 accidentally used the title wrapper on game input8B06, restoring title
attributes during play and reducing updates to62/600frames. Split menu-only entry
and input entry. Then the C011 patch was not propagated into ROM bank5; copy fixed.
Early probe700/1000/1300/3000(older) mode0 title tests were incomplete and shared
probe3000 overwritten by final capture. Early probe1700_joy.* has superseded hash
B72E1C64... and visible erroneous strips; retain as failed diagnostic, not final.
New title asset overlapped seven of eight fallback opacity-marker reads at1B1F,
creating false paired foreground colours in level tiles. Coherent probe1400 caught
it; moved all8 dummy bytes to1B18-1B1F and added build assertions. Superseded
probe1400 data overwritten with final B42D...; current image is clean. Current
probe1400_joy.* captures completed publication at8B06, frame1404, not arbitrary
half-render. probe_ecm now supports --coherent, --dck, --label and hashes that image.

verify_ecm_scrolling.py initially exceeded Windows command-line length while
setting6144 bytes individually. Compact injected Z80 initializer propagates a
256-byte fixture pattern instead.8 cases pass with complete6144-byte shadow
comparison and live new-column8-byte checks; synthetic20 rows, untouched borders
and HUD, AF/register/stack/IFF assertions. commands/logs/validation under
build/diagnostics/r6_scrolling. This validates exact byte correspondence, not
subjective full-level visual stability. r5 same-frame1400 comparison retained as
probe1400_joy_r5.*; natural timelines differ because speed changes.

Final272 tile cases (both bitmap bases/four mirrors/IFF/override) pass unchanged
costs.8 repair comparisons updated to current image pass; legacy printed label r5
names the hook design, not the tested image revision.4 repair-core,8128 metadata
bytes, key definition6keys/one entry/start/play pass. r6 retrace begin1163/end1252,
89displayframes,zero trails/IDs/deaths: build/diagnostics/r4_trails/r6.*. Final
probe8000_joy.* returns to ECM menu (mode2), not live ship or old mode0 expectation.
Final natural benchmark r6:106updates,1621tiles,56060scanned cells,449IRQs/600frames;
r5:116updates. Normalized nominal10.6202 vs11.6221 updates/sec; includes natural
restart gap. Correct palette copying has a measured cost; do not claim unchanged
speed. measure_frame_rate.py reproduces; performance/r6.* retained.

Finalr6 BIN B42DB62F1025B2274CA69ADEB15DE37A52E96E65718BFBE0CC649B4F20FD3D06
DCK ACAEAFE9512DA8CE1749C8E4998D111BB17F081AB3D48E3415EB5F5C56999630
Preserving-title alternative BIN E4B49E5DA2EE4D5286870B13475B6EC1519D642C4375040C12F95438A8BAE9FE
Unversioned aliases match mainr6; versionedr5 retained. r2 ROM unchanged EF2B9E08.
Still first-level/writable DOCK1+2+3; full arcade scenery/art, animation/audio,
ROM-only ECM, physical tests and further performance work remain outstanding.

## 019 - rejected r6 title flicker and r7 stability rollback (2026-11-01)

User explicitly rejects both new colourings and reports flicker after title moves
and recolours. Prior r6 screenshot/static contracts did not validate temporal
palette stability. Found full legacy-plane mirror followed by title recolour on
every menu poll. Removed entire title publisher/asset build from active r7.
Original menu mode0, bitmap and movement restored; no new artwork claimed.
Rejected palette-preserve/chroma artifacts and r6 images retained as history.
Level fallback and new entering columns now flat original source attributes;
actor/explosion shading retained; retained-shadow scroll still correct.

verify_title_flicker.py extracts actual r6 CALL targets from its frozen binary,
traces selected69AA attribute before/after title overlay. First assertion assumed
capture began at the start of a poll; debugger window began at overlay entry,
so added explicit stage tags. Actual three pairs47->45 each poll confirm palette
oscillation. r7 frames2800-2999:6842 input entries,zero mirror calls,mode0. Saved
r6/r7.commands/log and validation.json under build/diagnostics/r7_title. This
proves removal of repeated recolouring, not absence of original logo animation.

verify_ecm_scrolling.py updated for active r7 and original column attributes;
8 cases pass including whole6144-byte shadow, untouched borders/HUD,live entering
column,registers/stack/IFF. Logs/commands/JSON at diagnostics/r7_scrolling.
8 repair comparisons pass on currentimage; printed r5 refers to hook design.
272 actor renderer CPU cases pass both bases/all mirrors/IFF/override,unchanged
sampled shader costs. Original key redefinition stores6 keys,one entry,start/play.
r7 retrace begin1138/end1230 (92displayframes),zero trails,zero27 IDs,zero deaths;
RAM/PNG/log/commands/JSON under diagnostics/r4_trails/r7.*.
probe3000_r7.* mode0 original menu/attract (not necessarily logo at every instant).
probe1400_joy_r7.* coherent8B06 frame1401 active ship and original scenery colours.
probe8000_joy_r7.* mode0 menu after natural play. These images remain actual RAM
captures; no new title-preview comparison presented as an accepted enhancement.

Finalr7 renderer761 bytes. BIN5B553E6534E1205D493163AD99FA05947450D0C14A87A21FA8A895486C0E0BE8
DCK301DA36CE0A74BEC403ACA0CD23E7C250927B23BF5F13B7DB864BF4A318840F5
Unversioned aliases match r7; r6/r5 retained. Stockr2 remains EF2B9E08... . No new
whole-game performance/hardware timing claim. Title design remains unfinished;
a future alternative needs matching bitmap/colour geometry and temporal checks.

## 020 - stock-ROM and ECM memory optimizations; expanded cache compiler (2026-11-01)

User requests Sinistar/Beast-style memory optimizations for different targets.
Read state/history, graphics precomputed/parallax/optimization refs, actual
Sinistar SCROLLING/ASSEMBLY_CACHE and Beast Horizons MEMORYrev14, TSPico skill and
expanded-memory/protocol refs. Reference files unchanged. No agents/hardware used.
Shared84-byte ROM kernels,776-byte/97-row colour cache,128-cell HUD history and
320-byte scroll plan implemented; memory contracts in docs/performance_optimizations.
Colour metadata786 IDs in bootstrap padding,existing8128-byte DOCK1 indexed layout.
Boot still transforms originalFF pixels to55/AA; shading output unchanged.

Initial cached-renderer assembly failed on out-of-range JR branches; changed toJP.
Some subsequent commands in that diagnostic batch exercised preserved r7 because
the build had failed; those passes were not r8 evidence. After successful assembly
r8 hash5F62BFE7... produced136 direct and136 retained passes,means1123.2/1129.0T
vs1723/1726 previous. Final HUD/scroll plan addition yields1A9462F2... below.
Initial kernel oracle timed out after its16 completed cases because its finalPC
landed directly on a breakpoint and continue skipped it. Frame watchdog exposed
case16; corrected final NOP landing4000->stop4001.32 cases per original/r3/r8 image
then match entire register/flag/bitmap/IFF state; IRQ-off mean347T->249T(stock),
254.7T(ECM). Tables/logs/commands and kernel_validation.json under build/optimized.

HUD fixtures verify all-changed,unchanged,one-cellFLASH cases over complete6144-byte
plane with exact CPU registers and IY/stack; saved hud.commands/log/validation.
Current measured31508/12233/10627T includes phase/IRQ effects. Scroll oracle8 cases
passes after replacing loop with immutable row-pointer SP stream; diagnostics now
r8_scrolling. SP saved3FE0, restored before unmaskingIRQ; original IDs untouched.
8 repair comparisons pass. Retrace r8 begin1123/end1208=85displayframes,zero
trails/27IDs/deaths. r8 key6bindings/one entry/start/play passes. Stock ROMr3 also
passes key/start via new --dck verifier option. probe8000_joy_r8.* returns mode0
menu; actual RAM/PNG/log/commands/JSON retained. Title verifier updated to actual
r8:6842 input calls,zero menu-plane repaints,mode0; preservedr6 palette oscillation
still demonstrated. No new colour treatment or logo change.

All-cell oracle first still iterated only original4 representative descriptors;
empty chunk assertion caught this after2 chunks. Expanded to all111 descriptors.
Then78 independent batches verify617 nonempty cells x4 mirrors x2IFF x2destinations
=9872 CPU cases. tile_cpu_40/60_all_NNN .commands/log/json retained; aggregate
build/optimized/all_cached_cells.json. Independent original palette/source flags
oracle covers forced attributes too. Boot metadata8128 bytes matches expected IDs.

Frame-period diagnostic first used $f, parsed as hexF, then an underscore variable
unsupported by debugger grammar; both failed and are not timing evidence. Changed
to $startframe and an uncontendedC00010T JP loop with IRQoff. Actual current
Fuse1.7 TS2068 measured58688T/frame,60.1145038Hz at3.528MHz. Corrects the idea of
borrowing older skill evidence59736 from another Fuse build. frame_period commands/
log/JSON retained. HUD elapsed calculation uses measured period. Natural benchmark
fixed600refresh window1400-1999:classic151,ROMr3 152,r7 113,r8 122 update entries.
Simulation states diverge and restart gaps remain; not complete-raster/hardwareFPS.
Measurements/scripts under performance. Shared helper gains don't imply equal
whole-game gains. ROM improvement~0.7%,ECM~8%,controlled retrace92->85.

Expanded cache compiler:actual first-level map535 bytes,60 orientation codes,
max tileID21.480 finite phases(8each),15360rows of25 bytes,5528 unique;168920bytes
pool+indices vs384000raw. Independently decoded all source colour indices and
coverage/spill. This is four palette-index planes plus coverage,not finalECMattrs.
512KB image exactr8 region0 plus all8 unmodifiedTAP levels94886bytes andatlas;
used339404,free184884.64 page hashes,8 even-slot region files,chunk-bounded asset
spans verified by reassembly; build/expanded_cache/manifest.json. Expanded data
is NOT consumed by game yet; no native bank gateway/loader or512KB runtime gain
claimed. This is implemented compiler/staging work,unfinished runtime integration.

Cartridge skill inspector validates stock[2]*8 andECM[2,3,3,3,2,2,2,2],validAROS.
DCK reports optimized/dck_inspection.json andecm_native/dck_inspection_r8.json.
Deterministic rebuilds of ROM/ECM/expanded bundle match prior hashes. Originalr2
remainsEF2B9E08...,r7 preserved. No source archives modified. Newoutputs:
ROMr3 BIN/ROM023746F741D1E8180079BA5F4FEE00DB425CB67B5B189F55F453309210373AA9
DCK C0F3AB4B82BCF5C1DFEA66A90C46041306E0650986DFE59A0398965AA153CB05
ECMr8 BIN1A9462F21A37E403D45196822106B59DAF6D246763F8D80286385CE7CAEEA7BC
DCK B94289B0B51BC6AAA779A3C100A027E7B6D0354BDCFC1C42744A96A0D87567BA
Both remain first-level. Full512KB banked game renderer and ROM-onlyECM unfinished.


## 021 - r9 terrain publication repair (2026-11-01)

User reported terrain colours standing still in ECM r8. A natural live capture
at frame1400 found40 mismatches among72 bottom terrain cells. Source tracing
showed8842 copies legacy attributes,88E6 handles the bitmap terrain spans, and
8981 conditionally calls8CD8 to shift the IDs. Cached actor repair did not publish
the live terrain plane. The first r9 draft repaired spans every frame but left
seven phase0 mismatches. Final r9 publishes at7A82 phase0 and repeats after the
coarse ID shift. All nonempty cells in the22 first-level terrain tiles have their
solid flag set, confirming the terrain-ID oracle covers visible source terrain.

scripts/verify_terrain_motion.py retains phase commands/logs/RAM/PNG and animated
terrain strips in build/diagnostics/terrain_motion; probe images live under
build/ecm_native. r8 phase1200 mismatches44,44,44,44,44,44,45,45; final r9 all eight
zero at1200 and1600. The1200 comparison was initially retained as validation.json;
1600 is validation_1600_r9.json. Earlier draft captures sharing names were replaced
by final captures; only the stated failed counts describe that draft.

verify_terrain_spans.mjs:240 CPU vectors across SRAM r9 and read-only renderer,
20 rows, three spans and IFF0/1, full6144-byte colour plane, borders/actors,
registers, stack and mapping. span_cpu_validation.json retained. Existing repair
hook8 cases, keyboard six-key held-Enter setup, and ship retrace pass on r9.
Retrace1142->1227 (85 refreshes), zero trails, invalid IDs or deaths.
SRAM BIN A842744303506283201A6DEF665F35C34D243A11EEFCB72CDE58C50C9007DCFA
DCK 7B5E4AB0BF66ACB44EE0902E098A17C1AFCA8FAC6A9D6CFC9FA6E9A54427E603
This remains writable DOCK1/2/3, not the PicoROM target.

## 022 - genuine ROM-only ECM memory conversion (2026-11-01)

User explicitly confirmed cartridges must be read-only. Implemented a separate
all-ROM ECM renderer and bootstrap, not a renamed SRAM binary. Workspace6000-77FF
moves into HOMEA600-BDFF; immutable graphics move to ROM1. Runtime maps ROM0/1,
HOME for mutable game state. Sprite ROM headers embed colour-cache indexes;
level graphics retain their original raw header format. Existing7800 palette
buffer and8100 dirty-grid high bits encode deferred background colours. MODE
moves to HOME BE00. Native key table/control state move with the original code.
133 typed instruction relocations plus startup/IRQ/sound pointer tables applied.
Original title/menu colouring remains; source archives/reference projects unchanged.

trace_readonly_layout.mjs saved8000-refresh r9 execution/dirty-access trace under
build/readonly_ecm/runtime_layout_trace.json. This disproved an early proposal to
borrow HOME5B00: sound routines F91D/F920/F923 actively alter that buffer. No sound
workspace is borrowed by the implemented renderer. First bootstrap draft used
labels spanning DISP and therefore copied an incorrect helper length; corrected
by separating image/relocated labels before successful handoff. Initial firmware
probe was incorrectly treated as a game ROM write; firmware attempts8192 writes
before entry as RAM detection. Guard now counts those separately and fails on
any game-origin ROM write. No failed draft was published as a PicoROM output.

Fuse diagnostic images/RAM/logs/commands are under build/readonly_ecm:
probe_0_rom_handoff, probe_1200_joy_rom_play, probe_3000_rom_menu and all
probe_1200_joy_phaseN_rom_terrain captures. Menu3000 is an intermediate original
moving-letter frame, not proof of the full title composition. Gameplay1200 was
visually inspected; ship source bitmap matched original pose3. Every phase1200
has zero terrain mismatches. Later1600 phase4 reached a death/restart gap with
zero terrain cells; oracle correctly rejected that capture, not a visual pass.
Its earlier phase0..3 diagnostic PNG/RAM/logs remain; final gate uses active1200.

Initial ROM retrace exposed two stale cyan strips: empty restore called the
colour helper with A=dirty1. Explicit XOR A fixes the erase path. Retest passed
begin1186/end1283, zero trails, invalid IDs and deaths. Background fixture initially
used initial_home.bin saved before hook patching; it is now emitted after hooks,
matching the actual boot image. This was a test-fixture bug, not a game execution
change. Keyboard redefinition on relocated BD80 passes six keys, one setup entry,
held final Enter, and entry into play.

Independent CPU bitmap/colour oracles: verify_rom_sprites.mjs passes2160 cases
(all90 nonzero common poses, four mirrors, three clipping positions, both IFFs),
zero ROM writes. verify_rom_background.mjs passes720 background draws,4936
restores and4936 empty erasures, full planes, dirty bits and IFF. Reports retain
exact final-binary hash. These cover617 nonempty common sprite cells; they do not
claim an exhaustive test of every level-specific enemy or all gameplay states.

The first4000-refresh ROM runtime passed575 updates, but extending to8000 caught
an unrelocated sound-data pointer: FC4F held72E8, indexed by F9D8 and read byF91D.
The35-entry sound pointer table FC0B-FC50 is now explicitly relocated (last entry
B8E8). The failure and sound-pointer history remain in runtime_failure.json.
An automatic approval-review timeout prevented one local runtime invocation;
retry executed successfully and found this substantive bug. Final reports below
supersede preliminary4000-refresh evidence. Physical hardware is untested and
subsequent-level native loading remains unfinished.


Final ROM r9 hash3E61CC47634DF10C9A0F03AA48C1513C23A5B639328FF19E67E3F0A3C8B33B1B.
DCK5A5960B9BCD5CC1C74C354A9F8ABD87617A7CFC10D4E391ECC1AD4E0A576A256.
Final8000 refreshes:792 update entries, five starts, three menu entries, mode0 at
end after return to menu. Zero game-origin ROM writes;8192 firmware detection
attempts before entry; every ROM bank byte unchanged; no original-game access to
old6000-77FF workspace. runtime_validation.json saves exact hash and4426 executed
PCs. Sprite2160/background720/restore4936/erase4936 reports repeat on this hash.
Fuse all eight active-play terrain phases1200 match; relocated keyboard passes;
retrace1186->1283 has zero trails/IDs/deaths. publish_rom_ecm.py verified matching
binary hashes on runtime, sprite, background and all phase probes before emitting
RType_level1_ECM_64K_PicoROM_r9.rom/.bin/.dck. Raw ROM exactly65536 bytes; DCK65545.
Cartridge-skill inspect_dck validates all descriptors2 and AROS entry; flattened
DCK is byte-identical to raw ROM. SRAM r9 separately validates mixed descriptors.
Inspector JSON and inspected_flat.rom retained in build/readonly_ecm. This is an
emulator-validated first-level ROM build, not a physical-hardware or full-game pass.


## 023 - actual spill-cell / fine-scroll ownership repair (2026-11-01)

User screenshot showed wrong white left edges and repeated palette shifting in
r9 buildings. Previous r9 test compared only original legacy8x8 terrain attrs;
that oracle did not cover actual shifted pixel ownership. Original RL loop88E6-
8974 shifts one extra non-terrain cell on the left. r9 excluded that cell and
published before pixels moved. Replaced it with shared terrain_live_colour.inc,
hooked after RL at8974. It uses the original DE/BC bounds rather than rescanning
IDs. This eliminated redundant hot-path work. Global register/IFF/mapping contracts
are preserved; the cartridge version writes only HOME RAM.

The first r10 draft corrected coverage but reused stale sky attrs for existing
pixels in the spill cell. Natural ROM phase capture caught this at row19,col24:
cyan5 switched to white47. Spill cells now always inherit the entering terrain
palette, while actual terrain mixed cells use shifted-pixel coverage. At phase0
the original game has already coarsened IDs, so a newly inferred left neighbour
is outside the preceding RL span; the whole-frame oracle excludes that false
classification. The instruction-level live oracle independently checks exact
original span bounds at every hook return, including actual spill cells.

verify_terrain_spans.mjs passes1920 full-plane CPU cases:20 rows, three spans,
eight phases, both IFFs, both targets. Borders, spill cells, complete6144-byte
plane, all registers, stack and mapping verified. Homogeneous phase7 emits the
right source palette unconditionally; fixture expectations were updated for
that legitimate write rather than assuming untouched synthetic attributes.
verify_scroll_integration.mjs checks8000 refreshes each target,8522 SRAM spans
and1814 ROM spans, across all eight phases. It includes5694/1814 spill spans.
Reports: terrain_motion/edge_cpu_validation_r10.json andscroll_integration_r10.json.

Fuse verify_terrain_edges.py passes all eight phases for both at1200, including
occupied left spill cells and pixel-derived palette selection. Commands, logs,
RAM and PNGs use probe_1200_joy_phaseN_r10_terrain and
probe_1200_joy_phaseN_rom_r10_terrain in each target folder. Phase GIFs and JSON
live in build/diagnostics/terrain_motion. Early drafts reused these names; only
final hash-matching reports are validation evidence. probe_1200_joy_r10_edges.png
is an earlier draft visual diagnostic, not the final-binary fixture. Original
terrain tile contact sheet retained at sibling Elite/tmp/rtype_terrain_original.png.

## 024 - boss and small-enemy flat-colour fallback removed (2026-11-01)

User reported cyan boss and approximately16x16 height-tracking sprite. Traced raw
level sprites being deliberately excluded from common-sprite colour caching.
Descriptor8 is14x18 cells atC571-CB4C,156 nonempty cells; all70 descriptor slots
were inspected,55 have nonzero dimensions. Small raw frames now use four cached
material ramps. The large boss has nine authored row variants for warm head,
blue armour, vent cores and lower jaw. All13 rows are immutable ROM data. Common
actor ramps are preserved. Bitmaps, source pointer layout and collisions unchanged.
The exact user's height-tracking object was not independently identified; all
nonempty raw level frames, including all16x16 candidates, are covered by the fix.

Boss/source diagnostic Elite/tmp/rtype_boss_source.png uses monochrome reference
geometry, not new arcade artwork. Actual CPU previews in diagnostics/r10_boss_cpu.png
and r10_small_enemies_cpu.png show authored Spectrum shapes. Individual raw16x16
CPU captures live in ecm_native/level_spriteN_cpu.bin. Preview generator was run
before final terrain-only bounds optimization; sprite results are unchanged and
unit reports were rerun against the exact final binaries.

Expanded test fixture initially placed stack atD000, inside later level graphics
(descriptor33 CFBC crosses it), corrupting the diagnostic's source. Moved stack
toFFE0. SRAM fixture also initially failed to initialize mapped DOCK3 workspace
and incorrectly called legal SRAM ID writes ROM writes; it now models bootstrap
workspace and tests actual bank writability. These were fixture defects, not game
crashes. Final tests:1320 SRAM level-sprite cases;3480 ROM common+level cases;
1160 background draws with8996 restores and8996 empty erasures. Complete planes,
clipping/mirrors/IFF and no illegal ROM writes verified. Reports include binary
hashes. Level pixel data is compared independently to original source.

Final8000-refresh ROM safety run:792 update entries, five starts, three menu
entries, return to mode0. Zero game-origin ROM writes, unchanged banks, no old
workspace access;8192 firmware probe attempts counted separately before entry.
Both Fuse trail tests pass:SRAM1151->1247 (96 refreshes),ROM1187->1284 (97), zero
trails/IDs/deaths. Relocated six-key held-Enter setup passes one entry and play.
Natural performance600 refreshes1400..1999:r9=116 updates,r10SRAM=104,r10ROM=99.
This has a colour-rendering cost; no speed gain claimed. Reusing bounds improved
the provisional SRAM100-update result to104, but scenes/restart timings diverge.
publish_rom_ecm.py gates exact hashes for runtime/sprites/background, phase probes
and live scroll integration before publishing true read-only r10 files. Skill
inspector validates all ROM descriptors2; flattened ROM is byte-identical.

## 025 - original arcade boss graphics comparison (2026-11-01)

User reminded that original arcade graphics must be the starting point for
comparison. Added capture_arcade_boss.py, reaching the actual original boss with
MAME's diagnostic Invulnerability DIP. First attempt used digital set_value(0),
which did not change DIP selection and returned to game-over/attract scenes.
Those15 PNGs/palettes/sprite/tile dumps at2400..10800 step600 remain in
build/arcade_boss_capture as failed boss progression evidence (later attract
scenes are stage2). Corrected using documented field.user_value=0:
https://docs.mamedev.org/luascript/ref-input.html . Second15 capture sets in
build/arcade_boss_capture_invuln include actual boss at9600/10200/10800, with
genuine runtime colours and original functional graphics ROMs. Capture audits
verify20 functional ROMs; five missing archival PROM/PLD stand-ins remain explicitly
labelled diagnostics only. Existing source ZIPs were unchanged.

compare_arcade_boss.py converts frame9600 crop176,16,384,224, resized112x112 and
letterboxed112x144 preserving aspect. This includes attached boss objects/overlaps;
it is not an isolated animation atlas. Both palette-preserving and2.5x chroma
Sierra Lite versions retained, alongside authored Spectrum r10. Per8x1 pairs
require black only where the source touches black/transparent edges; opaque
interior strips may use two coloured endpoints. Original all-black-paper draft
was retained only as a diagnostic observation and replaced by the better final
conversion. Black-pixel masks are a crop heuristic, not authentic decoded alpha.

All files under graphics/arcade_boss_compare: boss_arcade_original_crop.png,
boss_arcade_scaled.png, boss_preserve/chroma_sprite.png, boss_comparison.png,
small_enemy_arcade_original.png, enemy_16_ECM.png and enemy_32_ECM.png; five full-page PNG/planes
boss_preserve,boss_chroma,spectrum_recolour,arcade_scene,small_enemies; matching
fuse_*.png/RAM planes and validation logs. Two boss sprite asset sets each2016
pixels+2016 colours+2016 preserve mask bytes. Small enemy uses decoded arcade
sprite54/palette5, not a claimed identification of the reported tracker. Separate
64KB ROM-only graphics viewer has five pages; verify_graphics.py --output checks
both6144-byte live planes and stack7FFF for every page in Fuse. This is comparison
art/viewer only; original arcade geometry is NOT yet integrated into playable r10.
Both art styles are retained. No full-game/physical cartridge validation claimed.

Final artifact hashes:
build/ecm_native/RType_level1_ECM_TSPico_RAM_r10.bin afc87217c9917d2330046b01c03433a28a909f4aa6a9f6fd976e17701d4fe678
build/ecm_native/RType_level1_ECM_TSPico_RAM_r10.dck 0c103a6f5c343822d4f22b9b90ed60b038d5c47bc881f6e01e943cd29f93b374
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r10.rom 7b65726ad7a0649ef88238f7e12b744c01c2ed43e1c6e0c9d3a9c02c2f795d7b
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r10.dck e6497938c4b97024f948a48bf2b0f90e8f4ee2a8dbcedfd816818f0497fea50c
build/graphics/arcade_boss_compare/RType_ECM_graphics_proof.bin 6b4b1ffad31508044a11160acacc4c3a50aed398075d8963c8bb3ce55d28ffd9
build/graphics/arcade_boss_compare/RType_ECM_graphics_proof.dck ecb204d014a124cc9c973b3f91ccd6f79b405543cfc1820406a851e1a04072d2


## 026 - remove rainbow stripes on smaller level enemies (2026-11-01)

User found r10 small bosses unnatural because their colour was just stripes.
Replaced four repeating ramps with per-header material selection in pose-local
coordinates. Seven restrained small-enemy rows now describe upper shell, lower
shell, warm core, green body, red body, pale highlight and blue body. Selected
core/highlight cells vary spatially; animation aliases retain deterministic
pointer-owned material tags. Existing nine large-boss material rows unchanged.
There are16 rows total. Bitmaps, cell encoding, collisions and terrain remain
unchanged. This is still authored Spectrum-shape colouring; actual arcade-geometry
comparison assets from025 remain separate.

Packed4-bit source-header tags cover C400-D7FF using2560 ROM bytes at0200-0BFF;
only valid enemy rangeC4CE-D7F8 is accepted. Palette moves to0C00-0C7F. Both
foreground and deferred read-only background token decoding use the new base.
Readonly tokens97-112 remain below128. Original level descriptors/source bytes
are untouched; no extra RAM, per-frame quantization or ROM writes introduced.

verify_boss_sram.mjs:1320 complete level-sprite/mirror/clipping/IFF cases pass;
verify_rom_sprites.mjs:3480 common+level cases pass; verify_rom_background.mjs:
1160 draws,8996 restores,8996 empty erasures pass. Independent original bitmap
and expected palette checks cover all55 nonzero raw level frames. CPU captures
level_spriteN_cpu.bin regenerated; r11_small_enemies_cpu.png and
r11_small_enemies_comparison.png are actual CPU-rendered contact sheets. Earlier
r10 sheet retained. scripts/boss_colours.py is reproducible material compiler.

8000-refresh live scroll integration:8522 SRAM/1814 ROM spans; all8 phases and
spill cells match. ROM runtime8000refresh:792 updates, five starts, three menus,
zero game-origin ROM writes, unchanged cartridge banks, no unrelocated workspace
access.8192 pre-entry firmware probe writes counted separately. Fuse readonly
phase1200 passes all8, logs/RAM/PNG probe_1200_joy_phaseN_rom_r11_terrain; GIF/JSON
under terrain_motion. Readonly retrace1184->1283 passes with no trails/IDs/deaths.
Publication gate checks exact hashes. Final DCK inspected with cartridge skill:
all8 descriptors2, valid AROS,65545 bytes; rawROM65536. Physical hardware untested.
No new speed benchmark claimed for r11.

## 027 - enlarge/align R-TYPE title to isolate blue terminals (2026-11-01)

User proposed enlarging letters so blue terminal shading falls in separate8x1
cells. Inspected prior r6 failed recolour and actual original menu/arcade title.
The issue is horizontal two-colour sharing: black+white+blue cannot all occupy
one strip. Previous r6 applied differently sized arcade attributes to Spectrum
pixels and alternated palettes. r11 leaves the original moving title untouched.

compare_title_alignment.py searches sizes232..248 and central pixel offsets,
using original arcade RGB geometry and counting mixed cool/neutral material
pixels per8x1. Best weighted candidate239x39 atx4,y101:176 mixed cells/301
conflicting source pixels, score0.089397.248x40 atx4,y101:199 mixed/344 conflicting,
score0.092747. A neutral-stroke protection rule keeps conflicting cells neutral
and gives isolated terminal cells cyan/blue. This sacrifices incompatible blue
fragments, not a claim that scaling eliminates every conflict. Source comes from
arcade_title_reference.png and actual title_legacy_reference.png. No AI artwork.

All artifacts in graphics/title_alignment: original_menu,arcade_default,
aligned_best,aligned_248,alignment_grid PNG and .pix/.atr; aligned_best_grid.png,
title_alignment_comparison.png; alignment_manifest.json with all candidates;
separate five-page ROM-only RType_ECM_graphics_proof.dck/.bin. Fuse verifies both
6144-byte live planes and stack7FFF per page; fuse_*.png and RAM/logs/JSON retained.
This static comparison does not prove animation timing or flicker-free live
integration. A future animated integration must own bitmap/palette publication
together; do not restore r6's per-input full-plane mirror/recolour loop.

build/ecm_native/RType_level1_ECM_TSPico_RAM_r11.bin 356907a0091e134c88fe29053927549f048161c7768672964d4f1e6b5b9e90ee
build/ecm_native/RType_level1_ECM_TSPico_RAM_r11.dck 5107286da43c790ca7b188e2ffee2b0d535745d4db3b9b068dd6909f7956b1e7
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r11.rom 9087c6c6802d832518f0ee8e177ef8866cc85b2d91d458d910c628a2f63ba90b
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r11.dck 75614de60f32a03dbbb116f5d47296f91b8b7c3e45d82ef4639bd252cf9c4b3a

## 028 - internal gap diagnosis and correction (2026-11-01)

User arrow at an internal terrain gap, not screen border. trace_terrain_gap.mjs
checks actual visible RGB as well as bitmap. r11 first hits SRAM1150/ROM1186,
update3,row18,col30,phase0: pixels present, palette0, front attrs71,71,0 versus
back71,71,71. Stock native r2 has no hits. Earlier bitmap-only and broad x24..30
scans were insufficient. Saved trace_r11.json and *_gap_home.bin under
diagnostics/terrain_gap. r12 runs8000refreshes per target with zero root-pattern
hits. Uses actual incoming back31 palette, clips publication at30, restores the
front sentinel and clears live staging31; original scrolling/collision layout retained.

## 029 - live enlarged title (2026-11-01)

Selected239x39 logo integrated, replacing settled title after original intro.
verify_title_publication: three publications/target, exact3072-byte assets,
3072 polls and zero changed title writes. Score transition restores mode0.
Evidence: art_assets/title_validation.json, */title_live_home.bin,
probe_500_live_title_r12.* and probe_500_final_title_r12.*; diagnostics/r12_title.png.
Static title alignment study remains. Firmware ROM probes caused a strict fixture
false positive before cartridge entry; natural runtime guard counts them separately.

## 030 - actual per8x1 terrain art (2026-11-01)

build_live_art.py transfers original arcade platform/pillar material crops into
22 native tiles, preserving outer profile/edge bits and solid-cell flags. Interior
texture changes intentionally. Both preserve and chroma factor5 variants retained:
art_assets/terrain_* (.json,.patches,.palette,_atlas.png), terrain_arcade_material*.png.
Raw tagged headers need FF81 RES7 removed; otherwise startup stripped tags and
created rainbow index colours. Added bank-safe palette decoders and readonly
terrain category bit6. First SRAM prototype read IX8080 after mapping ROM4 and
crashed PC0110; source target now read before mapping. A partial helper build
jumped to old authoring data at0100; assembly installed for both targets before
retesting. An accidental restore_uniform zero was removed; sky restore checks pass.
SRAM painter now preserves background tags and vertical palette orientation.

verify_terrain_art:1408 oriented decodes,2112 draw/clip/IFF cases,11264 restores;
exact full planes, both targets. Fixture ownerDD triggered native solid-cell skips;
owner1, cleared ID grid and stackFFE0 correct the fixture. Buffer/Uint8Array
comparison normalized. All final art hashes match cartridges. Evidence:
diagnostics/terrain_art/validation.json; */probe_1400_joy_arcade_terrain_r12.*,
*/probe_1400_joy_final_r12.*, diagnostics/r12_gameplay.png. Failed prototypes
were never published. Source exploration sheets: sibling elite/tmp/
rtype_terrain_original.png, rtype_pose_identification.png,rtype_arcade_fireball.png.

## 031 - arcade orb and enemy material cleanup (2026-11-01)

Original arcade cels175/176/177 replace descriptor57, with authored pulse0,1,2,1.
verify_orb_animation:32 copy/IFF cases,144 complete frame/mirror/clip cases, noROMwrites.
art_assets/fireball_frames.bin,fireball_colours.bin,arcade_orb_frame0.png,
arcade_orb_pulse.gif,orb_validation.json and manifest retain provenance. GIF is an
asset preview, not gameplay capture. Common families2..7 use stable materials;
ship/explosion family unchanged. Small raw material rows9..15 now constant per
material; shell/core spatial selection remains. Common30..37 identified as force/
powerup, not replaced blindly. Arcade2805/6 rejected as unsuitable tiny bullets.
All3480 SRAM and3480 ROM complete sprite/mirror/clip/IFF cases pass. Common cache
96rows/768bytes; saved authoring_palette.bin is test/reference data, runtime0100
holds the fast palette helper instead. ROM1160 background draws,8996 restores
and8996 empty erasures pass.

## 032 - final r12 validation and timing (2026-11-01)

3840 exact full-plane terrain-span CPU vectors pass all phases, IFF, mappings,
borders and sentinel preservation.8000-refresh live scroll each target:1814spans,
11945 mixed boundaries, all8 phases. ROM runtime8000refresh:792 updates,5starts,
2menus,zero game ROM writes, immutable banks;8192 firmware probe writes before
entry counted separately; no old6000-77FF workspace access.
Fuse terrain-phase test first incorrectly compared phase0 with next staging31;
coherent capture occurs after coarse shift, so back30 is the correct reference.
SRAM dump also originally read underlying HOME attrs, not DOCK3: added explicit
banked back-attribute capture. Those failures were reference defects; CPU hooks
already matched exact live colours. Final phase reports retained under terrain_motion.
Fuse keyboard selection both: one entry,six stores,starts/plays. Movement tests
r12/readonly_ecm_r12: no trails,stale IDs or deaths. Logs/RAM/PNGs retained under
ecm_native and readonly_ecm; terrain_motion GIFs are eight phase captures.

measure_r12_frame_rate natural600refresh window1400..1999: r11 SRAM108updates
(10.82/sec),r12 SRAM114(11.42/sec),r12 ROM80(8.02/sec). TS2068 Fuse frame58688T,
60.1145Hz. Includes long restart pauses; evolving scenes differ, not universal FPS
or controlled speedup. Full timing JSON/commands/logs in diagnostics/performance.
Read-only remains slower.512KB optimizations are still staging-only. Level one
and emulator validation only; physical hardware and subsequent level loading pending.

Final Fuse coherent terrain captures: zero mismatches in all eight phases on
both SRAM and ROM, using bank-correct back_attrs.bin sidecars. All gates pass.
Cartridge skill inspect_dck: all eight descriptors2, valid AROS machine header;
65545-byte DCK flattens byte-identically to the65536-byte published raw ROM.
build/ecm_native/RType_level1_ECM_TSPico_RAM_r12.bin c79f516e4ebf5cfbb22deb08904bd67a0b252c6a746562f0523d8d18d890db4e
build/ecm_native/RType_level1_ECM_TSPico_RAM_r12.dck e41da1c5df64d2360b671f23d7f5e1d9cee0566173c76006224ba2fd9b3cecc4
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r12.rom b1548045c82e5862a50e174d02f6ddcc1b3d918d1580e349b21cd34b70eabfb2
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r12.dck 40aa075b075464b0d835f3594ab9afdbf98e35c7fd0e2663a3ff668b7618c870

## 033 - r12 terrain moves but colours do not (2026-11-01)

User marked building tops and ground in codex-clipboard-e1236833-5125-4cf5-87a2-fd69235fd477.png.
Read graphics-animation skill and precomputed-graphics reference. Earlier exact
palette-copy assertions did not establish actual colour motion. New deterministic
trace compares successive pixel positions and associated foreground colours.
Normal2600refresh r11:113296 bytes,0bitmap/135colour errors (old incoming black
sentinel); r12 SRAM/ROM:18016 bytes,0bitmap/5587colour errors. Clearly reproduces
palette incompatibility independent of bitmap shift correctness.

First r13 used per-material32-pixel row fits; normal opening scene passed, but
extended later terrain found4704 SRAM/2398 ROM changes at material joins around
update764. Saved first_r13_terrain_palette.bin and first_r13_terrain_chroma_atlas.png.
Final compiler fits across both material references and their vertical mirrors;
asserts symmetry. Source texture remains fixed, original terrain envelope and
solid-cell flags remain, no native scroller or runtime code edits. Per-cell
horizontal hue freedom is traded for stable compatible8x1 rows. Both preserve/
chroma styles retained. r12 source patches/palette/atlases copied to diagnostic
r12_* files before regeneration. Earlier r12 artwork is not the current release.

## 034 - r13 motion validation and publication (2026-11-01)

Final normal2600refresh: SRAM217updates/18304checked bytes; ROM180/18016;
both zero bitmap or foreground-colour motion mismatches. Extended8000refresh
diagnostic bypasses death via test-only HOME91F2 RET, never written to outputs:
SRAM1034updates/540240bytes, ROM878/436456; zero bitmap or colour mismatches.
Failing r12 control:958updates/493856bytes,171245colour changes. New gate enforces
exact hash match and >400000 checks. It excludes actors, changed ownership, sky,
staging and out-of-region cells; not proof of every enemy/raster/hardware case.
Unmodified ROM runtime separately runs8000refreshes:792updates,5starts,2menus,
zero game ROM writes, immutable banks,8192 pre-entry firmware probes, no old
workspace access. Thus diagnostic invulnerability cannot conceal cartridge writes.

Both final builds:1408 terrain decodes,2112 draw/clip/IFF cases,11264 restores;
8000refresh live-scroll1814spans/224mixed boundaries/all8phases each. ROM3480
sprite cases,1160 background draws,8996 restores and8996 erasures. Title each:
3publications,3072polls,zero changed title writes. Orb32copy/144draw cases.
Fuse1200 coherent captures:all8phases zero mismatches for both targets. Existing
controls and renderer code unchanged; no new audio or hardware claim.

Artifacts: diagnostics/terrain_motion_r13/trace.json,trace_extended.json (first
candidate),trace_extended_detail.json(final), r11_30..61.bin,r12_30..61.bin,
rom_r12_30..61.bin,r13_30..61.bin,rom_r13_30..61.bin; r12_actual_motion.gif and
r13_actual_motion.gif are actual consecutive CPU game updates with authored120ms
playback, not measured rate. r13_gameplay.png from final Fuse capture; intermediate
ecm_native/probe_{1200,1400}_joy_row_coherent_r13.*; final */probe_1400_joy_final_r13.*;
both targets */probe_1200_joy_phaseN_{r13,rom_r13}_terrain.* including PNGs and
banked .back_attrs.bin; terrain_motion/r13_1200_terrain_phases.gif and ROM equivalent.
Regenerated art_assets/terrain_{preserve,chroma}_atlas.png and arcade material
reference crops retain source comparison; orb GIF remains asset-only preview.
All validation reports retain exact hashes. No physical machine test; level one.

Final r13 publication gates pass; all eight DCK descriptors are2 and valid AROS.
Inspected flat image matches the65536-byte PicoROM byte-for-byte.
build/ecm_native/RType_level1_ECM_TSPico_RAM_r13.dck 8280e8fe35ca55a2a02cf1f09b81fdfffbf4dbd98b6f78528f809aa2a0992da1
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r13.rom 2b72408dd58eb9c0d8ddec72d322ab29467e2abdd630365aefc07b4235ef85b6
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r13.dck 944b8331f9be276f902451c04b3b2070438ba2a5fa22a2ec3e477de14d2ef0ed

## 035 - first-screen buildings still broken in r13 (2026-11-01)

User clarified later similar building scrolls. Investigated full initial geometry,
not only cells already ID>=DC. Initial direct owner0 paint suppressed native attrs
under mode2 overlay protection. FF7A therefore saw no bit7 and left owner0, so8842
skipped initial buildings/ground. Streamed columns installed tags correctly. r13
zero-error claims excluded this broken geometry and were insufficient.
New verify_initial_terrain records coverage from actual source headers before IDs.
r13 SRAM:291/291 missing cells across3initializations,64257motion errors/152968checks.
r13 ROM likewise fails. Final r14 SRAM291/0missing/136160motion checks/0errors,
ROM194/0missing/124200checks/0errors; category0errors each. Owner0 attrs and vertical
orientation now retained. RO helper1160 initially omitted categorybit6; extended
test caught1171 colour errors, Fusephase0 failed67cells. Set category alongside
initial token. Final extended8000refresh: SRAM1060updates/593184bytes, ROM950/
531072bytes, zero bitmap/colour motion mismatches. Diagnostic death bypass is
test-only. Separate final true-ROM run unmodified:8000refresh,792updates,5starts,
2menus,zero cartridge writes,unchanged banks,8192pre-entry firmware probes.

Diagnostic files: terrain_boundary_r14/trace.json and *_30..61.bin (unfiltered
exploration includes actors/stars, not itself a pass/fail geometry oracle);
initial_terrain_r14/validation.json,*_initial_home.bin,*_initial_coverage.bin,
sram_r13/rom_r13/sram_r14/rom_r14_30..61.bin; first_screen_comparison.png and
first_screen_comparison.gif actual consecutive CPU updates with120ms authored
playback; r14_gameplay.png from final Fuse capture. Intermediate timing changes
alter actor placement; compare terrain motion, not screenshot frame identity.
Final */probe_1400_joy_final_r14.*; */probe_1200_joy_phaseN_{r14,rom_r14}_terrain.*,
terrain_motion/*r14_1200_terrain_phases.gif. Final all8phases both zero mismatches.
terrain_motion_r14/trace_extended_detail.json and *_result.json retain exact hashes.

## 036 - measured actor-rate optimizations (2026-11-01)

Profiled80active game updates20..100, diagnostic death bypass. Empty clean grid
scanning and RO per-cell category lookup consumed substantial CPU. Added ROM0:1F70
clean owner0 dispatch, preserving native handling of all nonzero/dirty IDs. SRAM
uses any-nonzero dirty test; ROM dirtybit0 respectsC0metadata. ROM front attribute
copy checks bit7 first, skipping category lookup for flat cells. Renderer1508/
1530bytes; no physics, frame cap, sound timing or cartridge write assumptions changed.
verify_clean_scan768cases compares native vs fast pixels/colours/IDs/dirty/registers/
SP/IFF/mapping; passes,1536aggregate T saved on its clean subcases.

Fair baseline generated from final corrected cartridges with only optimized scan
branch and RO token-copy body reverted; old pre-category benchmark saved separately.
Profile script initially omitted function-name matches due regex typo; raw PC/timing
was intact, corrected regex and added binary hashes. Both final80update runs have
identical1778paints,2552repairs,774spans,200columns,10coarse scrolls,80inputcalls.
SRAM26390568->24911664T (10.6947->11.3296updates/sec,+5.94%); ROM32528546->
29197012T (8.6767->9.6667,+11.41%). Earlier13%ROM estimate preceded category fix;
final fair comparison supersedes it. This is not universal FPS or high-rate motion.
Remaining beeper busy loops, grid scanning and blit cost are documented; no new
512KB consumer or nonblocking AY conversion is claimed.
Artifacts actor_rate/*_r14{,_baseline}.json/.dck,slow_front_copy.asm/.bin,
*_before_category_fix.dck,scan_validation.json. Baseline DCKs are diagnostics only.

## 037 - final r14 emulator checks (2026-11-01)

3480complete sprite cases each SRAM/ROM; ROM1160 background draws/8996restores/
8996erases. Terrain1408decodes/2112draws/11264restores. Live scroll8000refresh
each:8522spans/6852mixed boundaries/5694spillspans/all8phases, exact colours.
Title3publications/3072polls/0changed title writes each. Orb32copy/144draw cases.
Fuse retrace r14 and readonly_ecm_r14: zero trails/IDs/deaths; keyboard selection:
oneentry/sixstores/started/played. Retained logs,RAM,JSON,PNG under existing
diagnostic folders. These SRAM/control checks precede the final ROM-only category
metadata fix; that fix is exercised by complete final motion/art/runtime/phase gates.
Level one; physical hardware untested. Original archives and reference code unchanged.

Final ROM-only category fix also passes rerun readonly_ecm_r14 retrace and key
selection at final hash. Publication inspection: eight ROM descriptors2, valid
AROS header,65536-byte flat image matches published PicoROM byte-for-byte.
build/ecm_native/RType_level1_ECM_TSPico_RAM_r14.dck 268b86dff420762792677dd2d06864fed6d172c0136c0e56ca896ef0b1ef4c60
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r14.rom 31dca3f761e8781edd472129603a12a5664f22963c07f44f67d8ee950c14cfe3
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r14.dck 4636fe70d07e72c8a435ae94ce898fe5173790c47deb7b38281d66d2a9a38687

## 038 - r15 audio and renderer development (2026-11-01)

Applied the TS2068 native AY skill. Extracted21 finite original2019 bank7
effect scripts (2259bytes) and260tone-table bytes, including effect5's1242ticks.
An earlier600tick cap incorrectly classified that effect as unbounded; corrected.
Both native interpreters exactly match4452ticks/9420ordered writes. R14/R15
remain joystick-only. Effect provenance/selector limits in r15_audio_rendering.md.
Generated build/audio/* reference,packed,validation JSON and source-stream WAV.

Dense640byte level-cell lookup frees1920ROM bytes. Whole-row and clean-run
skips replace repeated empty-cell repair. A DEC L flag clobber initially skipped
dirty rows; corrected and checked by240whole-row native comparisons.
An initial direct-only compiled cache had zero live hits; replaced with retained
plane support. Final SRAM cache500bytes, tenhot cells,136674liveinstruction fetches
in4000refresh diagnostic. HOME/DOCK2 identical copies; no ROM-target livecache.
Earlier header-marker experiments removed. Cache-space audit records0prior accesses.

## 039 - direct versus buffered and IRQ timing (2026-11-01)

compare_draw_methods.mjs includes erase/draw/publish and exact plane/metadata
comparison. SRAM ship6239vs7078T; enemy17169vs18685T. ROM ship5771vs8249T;
enemy15566vs22584T. Uniformsky only, sixraster starts; no live direct switch.
Artifact build/diagnostics/r15/draw_method_comparison.json.

Initial AY integration missed many displayIRQs during masked graphics work
(802/1200SRAM,1013/1200ROM). Resident128byte terrain palette and exact-HSR IRQ
gateway allow preemptible drawing/restoration/columns. Coarsecopy now IX rather
than redirectedSP. Final live_validation.json records recovered cadence near50Hz.
Gateway preserves primary/alternate registers,SP andmapping in7cases. Primary
Timex manual confirmsF4readback; Fuse readback3 also verified independently.

## 040 - title reveal and Fuse input regression (2026-11-01)

All32partial column states compare exactly against final title bitmap+ECM
source. Threepublications and3072polls each target:0changed settled-title writes.
RAM captures title_reveal_r15/{sram,rom}_column0..31.bin, validation.json,
title_reveal.gif and title_reveal_last_partial.png. LastPNG deliberately partial.

Fuse terrain probes initially failed to reach gameplay (DEAD/FDEB halteddelay).
CPU still polledmenus; F4readback correct. Native LD A,I interrupt-state sampling
race leftIFF disabled. MaskFF periodic source before sampling, restoreoriginalFF
andIFF; fix validated with Fuse on both targets. Injection offsets shifted7bytes;
diagnostics now derive them from opcode signatures. Diagnostic helper underTemp.
Failed logs *_r15_inputfix.log overwritten by successful rerun, original failures
remain phase probe logs if not overwritten; failure facts preserved here.

Full sprite/span fixture failures after runtime relocation were fixture-only:
SRAM fixture omitted patched C000/E000 banks; spanfixture omittedresidentpalette.
Fixed initialization, then3480SRAMsprites and3840spanvectors pass independently.
No production changes made for those fixture failures.

## 041 - final r15 validation and publication (2026-11-01)

Final complete sprite tests3480cases pertarget; ROM1160background draws and
8996restores/erases. Terrain1408decodes/2112draws/11264restores;3840spanvectors.
Live scroll8522spans/6852boundaries/5694spillspans, all8phases eachtarget.
8000refresh motion: SRAM620976/ROM558096checked bytes,0bitmap orcolourmotion
mismatches. First-screen291solidcells,0missing tags/categoryerrors,212384SRAM/
153776ROMmotionchecks with0mismatches. r13controls fail as expected.
ROM8000refresh run:792updates,5starts,3menus,0gameROMwrites,all8banks immutable;
8192firmwareprobe writes accounted separately. Orb32copy/144drawcases.
Fuse bothtargets8terrainphases:0mismatches. Retrace:0trails,0logical IDs,0deaths.
Keyredefinition:1entry,6stores,startedandplayed onbothtargets.

AYexact21effects4452ticks9420writes; scheduler2205IRQ->1834ticks. Live4000refresh
simultaneousjoystick/all20shiprows:1195/1200IRQs and994ticksSRAM,1199/1200IRQs
and997ticksROM (about49.8/49.9Hz). R14/R15 untouchedbyaudio. Nativeinputracefix
validated inFuse; opcode-derived injection retested successfully.
512compiledcases,240native-rowcomparisons and7IRQcontracts pass.
Title32partialstateseach,3publications/3072polls with0changed title writes each.
AllJSONhashes match finaloutputs. Testfixture failures and their fixes above.

Final measured380update window (diagnostic deathbypass absentfromproduction):
sram: 11.6946 -> 14.0538updates/sec (20.17%); 114637451 -> 95393504T.
rom: 9.8584 -> 10.4107updates/sec (5.60%); 135989530 -> 128774587T.

Outputs:
build/ecm_native/RType_level1_ECM_TSPico_RAM_r15.bin 34594f001b94b7a597ce87678c53b8fd0e58084f24d2835226a67c5430407fcb
build/ecm_native/RType_level1_ECM_TSPico_RAM_r15.dck a991e5cf59ec9694a45683b91041b110024857f8ebf980c9e1d327f462c6fb08
build/readonly_ecm/RType_ECM_ROM_candidate.bin d669bb8987c6eca8f044e2da0b53a83d4175b19e1a7b0b205ed78cf0bd6f24db
build/readonly_ecm/RType_ECM_ROM_candidate.dck ec7c86f8115176337b52010d761a83bab445aa421376ff94811eab747234dcc4

Physical hardware untested; levelone only;512KB remains staging-only. Production
renderer buffered; directdrawing comparison only. Source-stream WAVpreview and
captured-RAMtitleGIF are diagnostics, not hardware recordings.

## 042 - replacement coloured logo motion (2026-11-02)

User correctly identified r15 as original movement plus an added reveal. Replaced
8A4D's old title-sprite animation with new-art six-glyph left sweep then spread.
Adapted final cells0,6,9,15,21,26 to accepted wider artwork. Thirty states each
target exactly match independent bitmap+8x1-colour compositor; final title3menu
publications each, zero changed settled-title writes. Glyphs are byte aligned.

Initial helper exceededFD20 by5bytes: assembler negativeDS warning let it shift
IRQ entry. Fixed with tighter FD20 assertion and shorter helper. An early main
routine selectedROM4 while still executing HOME8Axx; moved bank switch into
persistent ROM0 gateway. Initial direct clear/draw replaced with offscreen
A600–B1FF composition and paired-row publication. SRAM stashes/restores source
graphics viaDOCK2; read-only target uses idle workspace. Exact source restore
is checked. Captures title_motion_r16/{sram,rom}_frame0..29.bin, validation.json,
new_logo_motion.gif,settled_title.png; title_live_home.bin on both targets.
These are captured CPU RAM previews, not physical raster/tearing evidence.

## 043 - original level-one AY music and mixing (2026-11-02)

Read native AY and animation skills. Web sources/release provenance in
docs/r16_logo_music_arcade_sfx.md. Exercised16local2019tunes; entry0 level mapping
proved by intro6258 subtractingASCII31 from level text719C before C253.
Full driver-bank state repeats at2305ticks;46.1sec. Source/init registers preserved
in music_probe_0.json; complete sourcebank hash retained. RePair grammar over
174delta frames /99pairs /385root tokens. No note/frame loss; redundant writes
removed. State matches4611init/tick frames through2loops pertarget. Original
level tune uses only tone/volume andB8mixer; no noise/envelope orR13 retriggers.
Source MSX/CPC selector attribution remains unproven; credit2019 AY arrangement.

An attempted5E00state reservation corrupted native terrain buffers. Baseline
read/write audit confirmed active5E00usage; moved all state into obsolete beeper
tables FD50–FD92. Title scratchFC50–FC7F. Bit-reversal table ROM7FD00–FDFF must
remain intact; an early allocation there was removed. Native IRQ primary/alternate
registers,SP,HSR preserved. Grammar stack max44bytes in48byte reservation.
Music usesA/B/C idle; effect borrowsA, B/C continue andA resumes current note.
Native50Hz cadence tied to displayIRQphase, not actor updates. R14/R15 untouched.
ROM0 helpers restore bank before stack use. Moving grammar pairs to freedROM0
and simplifying word reads cut worst music tick23051->15523T in the test model.

## 044 - rejected effects replaced with arcade speech2ay (2026-11-02)

User explicitly rejected current effects during work; comparison-only approach
superseded. r16 defaults replace all21slots using8original arcade-derived sounds.
Real gameplay I/O0 write-tap confirms repeated playerfire48, enemyshot80,
death/music-stop sequence53 and coin99. Other43/49/50/52 assignments provisional.
MAME source documents YM2151, so AY conversions approximate original FM effects.
Captured commands and WAVs under build/audio/arcade, original ROMs untouched.
Existing documented unused PROM/PLD diagnostic stand-ins still produce MAME warnings.

Initial MAME suspend API unavailable; replaced with mainCPU diagnostic loop and
PSW IRQ masking for isolated capture. Natural gameplay captured separately.
Command38 was silent in isolation; excluded in favour of confirmed coin99.
An exploratory converter parse incorrectly assumed17bytes/frame. Actual format
is11registers+2envelope period bytes+255skip sentinel =14bytes. Caught by invalid
volumes/length checks, corrected and reconverted before publication. Earlier
comparison WAVs regenerated; no malformed curves ship. Tool/source hashes retained.

One-channel harmonic curves sampled60.1145Hz, resampled50Hz for IRQ player; delta
and run-length compressed.1238stream bytes+66directory. Death11 priority prevents
shot requests interrupting death sound. All21slots on bothtargets match2428total
converted source frames; effects never touch B/Ctone/volume orjoystickregisters.
Reclaimed old effect-data space holds music tables. Early one-byte old-script
terminal collision in8726 was fixed; final old engine is completely replaced.
Old2019effect11 kept only as explicitly rejected A/B WAV baseline.

Artifacts: speech2ay_candidates/{manifest.json,compare.html,arcade_command*.wav,
normalized_arcade_command*.wav,command*_harmonic*.bin/.wav,death_comparison.wav,
death_comparison_timeline.json}. Two-channel alternatives remain comparisons;
one-channel replacements are the default. Native mixed20sec preview
music_and_effects_r16.wav; mixing test verifies B/C throughoutA borrowing and
subsequent recovery. Modeled/synthesized previews, not hardware recordings.

## 045 - final r16 checks and publication (2026-11-02)

All final node checks logged individually under r16_final_checks; all pass.
build/audio/music_validation_r16.json
{"target": "sram", "frames": 4611, "loop_ticks": 2305, "max_music_tstates": 15523, "max_grammar_stack_bytes": 44, "passed": true}
{"target": "rom", "frames": 4611, "loop_ticks": 2305, "max_music_tstates": 15523, "max_grammar_stack_bytes": 44, "passed": true}
build/audio/live_validation.json
{"target": "sram", "frames": 4000, "windowIrqs": 1193, "windowTicks": 992, "window_refreshes": 1200, "passed": true}
{"target": "rom", "frames": 4000, "windowIrqs": 1198, "windowTicks": 997, "window_refreshes": 1200, "passed": true}
build/diagnostics/terrain_motion_r16/trace_extended_detail.json
{"target": "r16", "frames": 8000, "checked": 604112, "bitmap_mismatches": 0, "colour_motion_mismatches": 0}
{"target": "rom_r16", "frames": 8000, "checked": 534672, "bitmap_mismatches": 0, "colour_motion_mismatches": 0}
build/diagnostics/initial_terrain_r16/validation.json
{"target": "sram_r16", "solid": 291, "missing": 0, "categoryErrors": 0, "checked": 202288, "bitmap_mismatches": 0}
{"target": "rom_r16", "solid": 291, "missing": 0, "categoryErrors": 0, "checked": 143352, "bitmap_mismatches": 0}

3480complete spritecases each; ROM1160background sprites/8996restores/8996erases.
Terrain1408decodes/2112draws/11264restores;3840spanvectors; live8522spans and
6852boundaries/all8phases each. Orb32copy/144drawcases.512compiledcellcases,
240native-row comparisons,7IRQcontracts. ROM8000refreshes/792updates/5starts/
3menus/0gameROMwrites/all8banks immutable. Firmware8192probe writes separate.
Fuse8terrainphases eachtarget0mismatches; retrace0trails/0logicalIDs/0deaths.
Keyselect1entry/6stores/started/played onboth. No immunity inproduction outputs.

Final380-update diagnostic window with music+new effects (not universalFPS):
sram: r15 14.0538 -> r16 13.3269updates/sec (-5.17%).
rom: r15 10.4107 -> r16 9.8521updates/sec (-5.37%).

Byte-identical rebuild from regenerated grammar and build scripts verified.
Eight read-only descriptors, validAROS header,65536flat bytes inspected.
build/ecm_native/RType_level1_ECM_TSPico_RAM_r16.bin ed1689a95c284f7862a7e8b7fdcfd00e3c8a223cd6a6f4bfead1d214ac0e1bf9
build/ecm_native/RType_level1_ECM_TSPico_RAM_r16.dck 9c08f7678b3f8076675aa82a70382292d00ac441b3d50ce362f3dc7b509582df
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r16.rom 8b847d05a8f1b8aece8239f40a4f2c65f9036f2dda4a6090a3233a554ebc9585
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r16.dck 7f05ab46eddc84b764e5f6b39907b8709639f6e1267e219ff4e2cf4730ac2563

Levelone only; physicalhardware untested; no new512KBconsumer.

## 046 - title corruption feedback and coherent cluster (2026-11-02)

r16's exact OR-composite tests passed but did not establish acceptable appearance.
User reported corrupt-looking palettes during overlap and requested a vertical
colour divide, smoother movement and recovery as letters spread. Applied graphics
skill constraints:8x1attributes, source quantization once, offscreen composition.
Precompute0/4pixel phases of the merged silhouette (624bytes); four-pixel sweep
replaces16pixel steps. Spread uses8pixel steps, oneHALT rather thanthree perstep.
Shared white/cyan boundary is cell aligned. Each settled letter restores source
colours after the moving group clears its right edge; finalE restores atx208.
Ninety states pertarget match independent per-pixel source reconstruction and
palette ownership; SRAM A600–B1FF source restored exactly. Stable title2menu
publications/2048polls each,0changed writes. No physical raster-tearing claim.

Atlas regenerated by scripts/build_title_sweep.py; title_motion_r17 captures
{sram,rom}_frame0..89.bin plusvalidation.json. coherent_title_motion.gif preserves
observed CPU-frame timing; settled_logo.png andmotion_comparison.png inspected.
Montage shows white/cyan swept cluster, progressively coloured settled glyphs,
and exact final source logo. No random per-letter attribute fights remain.

## 047 - death53 noise and temporary musicB borrowing (2026-11-02)

User likes coin, finds43 reasonable, rejects tonal death53 and requests more
noise / another channel; considers2019deathhook. Confirmed nativeevent11at9201
maps toarcade53; old2019effect11 is another waveform for the sameevent.
Fitted originalarcade53PCM with speech2ay's stateful Ayumi worker: first noise
period/volume, then shared-noise B with optional low tone gate. Objective spectrum
+3*periodicity+.05roughness,2tick blocks at50Hz. Constrained bothvoices active
for non-silent blocks; no independent second AY noise generator is claimed.
Final56frames/1.12sec allnoiseA,42gatedB. Mean selectedobjective0.4512 does not
prove subjective quality. Initial exploratory pure-A choices superseded by the
explicit two-active-voice constraint. Final waveform rerendered from exact frames.

Death alone borrowsA+B; musicCtone/volume and progression maintained. Ordinary
effects stillborrowA; B resumescurrent musicstate afterdeath. Death outranksshots.
Native deltaformat extends to Bperiod/Bvolume only fordeath. Exact2428total
sourceframes across21slots/bothtargets; death reference now8register fields.
Noise fit costs141streambytes versus215previous. Coin99,43 and all7nondeath
sourcecurves compare identically to r16 (unchanged_effects_r17.json).

Native mixing1000ticks/20sec:56deathticks onA/B withC maintained; ordinary B/C
maintained and normalmusic recovered. R14/R15 untouched. Music registerstates
match4611frames/two full2305tick loops eachtarget; worsttick16099T in testmodel.
build/audio/death_noise_r17/{frames.json,r16_before.wav,noise_fit.wav,
death_comparison_r17.wav,comparison_timeline.json} andmusic_and_effects_r17.wav.
Comparison order: arcade53, r16single-channel,2019effect11, r17noiseA/B. Perclip
peak normalized; previews modeled, not hardware listening. Existing compare.html
updated with newdeath and unchanged coin/43 players; oldeffect11 labelledreference.

## 048 - final r17 verification and publication (2026-11-02)

All final node checks logged individually inbuild/diagnostics/r17_final_checks.
3480fullsprite cases eachtarget;1160ROMbackground sprites/8996restores/8996erases.
Terrain1408decodes/2112draws/11264restores,3840spanvectors, all8live phases with
8522spans/6852boundarycells/5694spills pertarget. Initial291solidcells,0missing
tags/categoryerrors and0bitmap motionmismatches. Extended8000refresh terrain
motion checks0pixel/colour mismatches. Orb32copy/144drawcases;512compiledcases;
240rowcomparisons;7nativeIRQregister/stack/banking contracts. ROM8000refresh,
792updates,5starts,3menus,0gameROMwrites;8banks immutable;8192firmwareprobes separate.
Fuse all8terrainphases eachtarget0mismatches; retrace0trails/0logicalIDs/0deaths.
Keyselection1entry/6stores/started/played onboth. No immunity inproduction.
Byte-identical rebuild verified after adding atlas regeneration and metadata fix.
Flat64KB output/header/descriptors inspected. Physicalhardware remains untested;
levelone only; no new512KBconsumer. Full evidence paths and outputhashes below.
build/ecm_native/RType_level1_ECM_TSPico_RAM_r17.bin 29d66a5941b7917917c744329c2c36daf05f8c4638bae7a7c417726f48a5ee88
build/ecm_native/RType_level1_ECM_TSPico_RAM_r17.dck 743bba4694596ca04011ab62940ca11938db275ab7f9a1f64feeb852d59414d5
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r17.rom f96d212a89fbffc9873ae33f17d9189f70bff263ac2e483762a8a68065db700c
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r17.dck 185b144e6c6aa387ad0470df28feb377bd72447bd09babbf85d48db7eb8c893a

## 049 - twenty death-effect audition alternatives (2026-11-02)

User rejects r17death and requests20different choices including importedAY,
arcade, hybrids and explosion+tone. Generated20numbered50Hzregister sequences:
1–4imported2019effect11,5–8arcade-derived,9–12designed explosions,13–16hybrids,
17–20noise+tone. Every register stream has a distinct SHA256. MaximumA/B effects,
Creserved; one-channel choices retainB/Cmusic. Imported original and currentr17
fit are included as baselines. Other choices vary noise colour, attack/decay,
pitch, tone gating, double detonation and shrapnel texture, not just loudness.

Scripts build_death_20.py/render_death_20.mjs. Initial Windowsdefaultencoding
produced cp1252source with non-UTF8 punctuation; savedgeneratorUTF8 and reran.
All20solo and20music WAVs rendered through sameTSRun AYmodel, summedA/B/C,
22050HzPCM, peak-normalized perclip.20unique nonzero solo PCMhashes; all register
values valid, noCvolume/period overwrite byFX, musicB retained for1channel effects.
Music excerpt identical acrosschoices, effect begins0.3sec, restoresborrowedvoices.

Artifacts build/audio/death_20/{01..20.json,01..20_solo.wav,01..20_music.wav,
manifest.json,validation.json,index.html,all20_solo.wav,all20_timeline.json}.
Page has20numbered players, solo/music mode, playall/stop, temporary shortlist;
existing speech2ay_candidates/compare.html hasprominentlink. Alllocalaudioassets
checked. No diagnostic images generated. Sources/provenance inmanifest and
docs/death_20_audition.md. Preview/model only, no physical quality claim.
No cartridge bytes changed; r17hashes rechecked. Coin99,43,title/game unchanged.

## 050 - full-screen ECM corruption reproduced and fixed (2026-11-02)

User screenshot codex-clipboard-726e8368-2b08-411e-b910-1a3706fdc333.png shows
ghost title text/colourstripes around the swept conglomerate. Reproduced from
r17sram_frame25.bin:0off-logo setbitmap bytes,4604off-logo non47colour bytes,
207palette values. Thus stale workspace became PAPER colour patterns when ECM
was enabled. Prior exact logo-band tests and cropped previews missed this.
r17control PNG/JSON retained underdiagnostics/title_screen_r18.

New ROM0F20initializer masks interrupts/selectsmode0, exposes HOME4000/6000,
clears6144bitmapbytes and sets6144colourbytes to47 before first mode2frame.
Only runs at title entry; loading art before title unchanged. During first Fuse
capture SRAM mode shadow read0 despite actualECM2: per-step store3FF0withmap9
targeted HOME ROM. Removed ignored stores; initialize shadow underproperbank3
(DOCK1 forSRAM, HOME BE00forROM). Final captures show2onboth.

90completeanimation states each check exact logo plus every off-logo pixel=0
andattribute47, actualECMmode andmode shadow. SRAMsourcegraphicsrestored. Title
publication stable onrepeatedmenus. Full-screenFusemid-sweep x148 onboth:
0straybitmapbytes,0badcolourbytes,mode2. Files fuse_{sram,rom}_mid_sweep.png,
fuse_validation.json,full_screen_motion.gif; raw probe_1_title_screen_r18
commands/log/RAM/JSON/PNG retained ineachbuildfolder. Full90RAMstates saved in
title_motion_r18. Full PNG inspected. No physical raster/hardware claim.

Final checks inr18_final_checks:3480sprites pertarget;1160ROMbackgroundsprites/
8996restores/erasures;terrain1408decodes/2112draws/11264restores;3840spanvectors;
liveall8phases/8522spans/6852boundaries/5694spills;initial291solidtags/0missing/
0categoryerrors; extended8000refreshmotion0pixel/colourmismatches. Music2loops,
all21effects,IRQcontracts,compiledcache andnativejoysticks pass. ROM8000refresh
0gameROMwrites/all8immutablebanks. Fuse8phases0mismatches, retrace0trails/IDs/
deaths;keys1entry/6stores/started/played onboth atfinalhash.

Audio data/code ranges compare byte-identically with r17; no new audition
selected. Coin43/99 and20audition files untouched. First publication attempt
correctly rejected stale extended-motion hash while final rerun was still active;
publication waits for final-hash checks. Whole-screen gates added topublisher.
See docs/r18_full_title_screen.md forrepro/evidence. Levelone; hardwareuntested.

Final r18 outputs:
build/ecm_native/RType_level1_ECM_TSPico_RAM_r18.dck fec4b6f76d7d199c3fbce431ba7953568b832c9809d812f97108a375068f7c67
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r18.rom 8c3c945b276bc4ee436ca9e2cde5ca8e4f20ea5e2184ca9f9393702d0986e8fb
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r18.dck 06ab8158ad09ac06b3c91b34b7f44253589c5a4304b6bebb9f8c8f7893a007c2

## 051 - twenty derivatives of preferred14 (2026-11-02)

User selected14as basis and requested20more focused on originalarcade explosive
attack/tone shifts/noise. Original14JSONhashed andpreserved; options21–40areall
new and distinctfromboth eachother andfirst20registerstreams. Fourattack variants,
fourarcade-tone blends, fourtone-stage variants, fournoise-evolution variants,
fourbalanced hybrids. All retain14foundation; A/B only, Creservedformusic.

50mswindows/50Hzanalysis oforiginalarcade53PCM: RMS,continuouslow spectralpeak,
upperpeak,centroid,flatness. Used asspectralguides, notassertedFMtranscription.
Strongburst/doublecrack, original14body, lowgates, noise sweeps/cascades,tails,
toneblend25/50/75%, high-to-low attack shifts andnoise/shrapnel combinations.
No automaticquality ranking orcartridge integration. Userwillchoosebynumber.

build/audio/death_14_variants/{21..40.json,21..40_solo.wav,21..40_music.wav,
arcade_features.json,manifest.json,validation.json,index.html,all20_solo.wav,
all20_timeline.json}. SameAYmodel/all3outputssummed/22050HzPCM/50Hzregisters,
perclippeaknormalization.20unique nonzero soloPCMhashes,40WAVs valid, musicC
unchanged duringeffects, allsource/localassetlinkschecked. Page includesoriginal14
solo/music references,arcade53,playall/stop/mode/shortlist; oldpageslinknewset.
No diagnosticimages generated. Existing14/firstset andr18cartridgeshashesunchanged.
Scripts build_death_14_variants.py/render_death_14_variants.mjs reproduce data/page.
docs/death_14_variants.md records methods andlimits. Modelpreview, hardwareuntested.

## 052 - arcade up/down pitch,33/37basis and real optimization (2026-11-02)

User requests20more based on33noise and37noise/loudness, matching originalarcade
pitch movement; requests speech2ay optimization. Created41–52source-guided and
53–60actualoptimizer fits.64ms/50Hzwhitened harmonic spectral ridge,75–1800Hz
loggrid, dynamicprogramming continuity allowingup/down.10rises/29falls above
.02octave in56activeframes. Not claimed as recoveredFMnotes. SomeclearAtone/
Bnoise choices, somegatedA variants, allkeepnoise33/envelope37basis. No fabricated
monotonic fall. Analysis/sourcehashes andparameters retained.

Actual maintained speech2ay stateful Ayumi search:8runs,66frames each;882samples
perframe.53–56pitchlocked,57–60periodwithin2%plusquantization. Noise,volumes,Bgate
optimized fromsameanchorstate, committedselectedstate. All8meanselectedcosts
improve overseedinsamehistory; objective evidence notperceptualqualityclaim.
No sharedtoolkitcode modified. OneWindowsencoding issue inlabels corrected to
UTF8; curvesunaffected. All20PCM andregisterhashes unique anddifferentfromprior40.

Artifacts build/audio/death_pitch_variants/{41..60.json,41..60_solo.wav,
41..60_music.wav,arcade_pitch_analysis.json,optimization.json,manifest.json,
validation.json,index.html,all20_solo.wav,all20_timeline.json,ay-worker.exe}.
Scripts build_death_pitch_variants.py/optimize_death_pitch_variants.py/
render_death_pitch_variants.mjs.20cards+source33/37/arcadereferences, solo/music,
playall/stop/shortlist, source/optimizerdata links. Existingpages linknewset.
40WAVs nonzero,20uniquesolostreams, allassetsvalid, Cmusicownership preserved.
No diagnosticimages generated. NativeJSsyntax checked. No cartridge/accepted
soundchanges; parent33/37andr18outputhashesrechecked. docs/death_pitch_variants.md.

## 053 - triangle experiments after preferences50and59 (2026-11-02)

User suggests triangle tones. Verified GIAYdatasheet and localTSRun/Ayumi envelope
implementations. Envelope-only repeatingtriangle14possible withtone/noisedisabled,
but waveformstepped/logarithmic ratherthanidealtriangle. Created61/62software
lineartriangle references,63/64pureAYenvelope,65/66noise-gatedenvelope,67/68lower
octaveAYenvelope. Sixnativefeasible; twosoftware-onlyclearlylabelled. NativeApeak
fixedinenvmode: originaldynamicvolumecontour cannotbeindependentlypreserved.
Bnoise/Cmusicreserved. R13firsttriggeronly; skip255 thereafter. Parent50/59unchanged.
Bothmodels period16probe215Hz against215.33/215.42expected; reportandprobeWAVsaved.
Eightunique nonzerosolos/eightcontextWAVs validated; Cfixedamplitude ownership
checked. Page linksfrompriorpitchchoices. No cartridge integration/newdefault.
Artifacts build/audio/death_triangle_trials/{61..68.json,*_solo.wav,*_music.wav,
manifest.json,validation.json,envelope_frequency_validation.json,
envelope_period16_probe.wav,index.html,all20_solo.wav,timeline.json}.
Scriptssaved; method/caveats/sourceindocs/death_triangle_trials.md. Noimagesgenerated.

## 054 - arcade-guided colour in terrain/buildings (2026-11-02)

User requests moreterrain/buildingcolour guided byarcadeimages. Current source
templates are arcadeframe2400platform/pillarcrops. Existingblack-paper rowfit
yielded nearlyallwhite with twoyellowrows. Addedarcadeprofile: moderatechroma3,
robustnonblack surfacecolour andverticalchromaerror diffusion acrosswarm/neutral
inks. Silver/gold/copperapproximation; no nativebrown. Kept32rowsymmetricshared
pairs acrossmaterials/columns;4forward+4reverse rows inexisting128bytecache.
Rendererbytes andRAMallocationunchanged; originalsolidflags/envelopesretained.
Preserve/chroma outputs retained; arcadeprofiledefault, envcanselectpriorstyles.
An earlypalettepreview includedbrightred; restrictedtowarm/neutral standardred
toavoid harsh primary-red dominance. Finalprofile atlasinspected withactualFuse
before/after andoriginalarcade strip. Materialsourceimagesretained. This doesnot
claim arbitraryhorizontalcellcolour underfine scroll.

Diagnostics terrain_colour_r19/{arcade_before_after.png,colour_coverage.json};
art_assets/terrain_arcade{_atlas.png,.palette,.patches,.json},terrain_active.json.
Fulltitle90RAMframes andwholescreenFusechecks in title_motion_r19/title_screen_r19.
Firstartifactcopy neededdestinationdirectorycreation; reran successfully.
Allnodegates inr19_final_checks:3480sprites each,1160ROMbackgroundsprites/
8996restores/erasures,1408terrain decodes/2112draws/11264restores,3840spanvectors,
all8livephases/8522spans/6852boundaries/5694spills,initial291solidcells/0missing/
0categoryerrors. Extended8000refresh601040SRAM/529632ROMbytes0pixel/colourerrors.
ROM8000refresh792updates/5starts/3menus/0gameROMwrites/allbanksimmutable;
8192firmwareprobes separate. Music2loops,21effects,joysticks,IRQcontracts,
row/cache/orbchecks pass. Fuse8phases0mismatches, retrace0trails/IDs/deaths,
keys1entry/6stores/started/played onboth. Entiretitleinitializedmode2/shadow2,
outsidebitmap0/attrs47. Byteidenticalrebuildverified; no newaudioselection.
Triangle61–68areauditiononly; sixAYenvelope/twoidealsoftware references (history053).
Primarydatasheet/2modelenvelopefrequency evidence indocs/death_triangle_trials.md.

Finalassetsaturationmetrics (nonblackatlaspixels, diagnostic only):
{
  "chroma": {
    "nonblack_pixels": 100208,
    "chromatic_pixels": 5728,
    "chromatic_fraction": 0.05716110490180425,
    "rgb_colours": [
      [
        255,
        255,
        0
      ],
      [
        255,
        255,
        255
      ]
    ]
  },
  "arcade": {
    "nonblack_pixels": 122864,
    "chromatic_pixels": 47616,
    "chromatic_fraction": 0.38755046229977863,
    "rgb_colours": [
      [
        205,
        0,
        0
      ],
      [
        205,
        205,
        0
      ],
      [
        205,
        205,
        205
      ]
    ]
  }
}
Finalr19outputs:
build/ecm_native/RType_level1_ECM_TSPico_RAM_r19.dck 857e0e9b8b837473943a7c77a53c9b33e959ba8a63ce6429142f9a4a08201304
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r19.rom 340e68a8174bff6f1ecf59f0bab059a790d105007f0231887a9dbda4f9cc2684
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r19.dck a5e162797aad3e53d026ca94df1a3b11e6f6261414c5479239f7a8a3354e87e5

Leveloneonly; physicalhardwareuntested; no new512KBconsumer.


## 055 — r20: selected65, faster title and terrain colour islands (2026-11-02)


The SRAM and read-only64KB cartridges both use selected audition65 from
`build/audio/death_triangle_trials/65.json`. The death event remains11 (arcade53).
The packed death records retain the existing eight fields and add three envelope
bytes. A ROM0 helper at0BC0 writes R11/R12 and writes R13 only for a real shape;
255 means skip. Shape14 is written exactly once per death. A/B supply the triangle
and explosion noise; C continues music. The current music does not use the shared
envelope. Future envelope-based music must respect this shared resource.
Silent trailing audition frames are trimmed as before;56 active playback ticks.
The allocator reserves0BC0–0BFF before placing music and effect data.

Title: sweep248→0 now steps8 pixels; spread0→208 steps16. This reduces90 states
to46, preserves the final logo and coherent overlap colours, and keeps the full
screen initialization fromr18. Measured on both targets at3.528MHz: sweep4.303→
2.240sec; spread4.315→2.152sec between publication timestamps. These are timing
measurements, not an increase in gameplay frame rate. Larger motion steps trade
some intermediate positions for a shorter animation. Preview:
`build/diagnostics/title_screen_r20/full_screen_motion.gif`.

Terrain: `scripts/terrain_islands.py` analyses the native map stream offline,
including H/V mirrors and the final arcade-derived bitmap interiors. Source cells
are connected if consecutive foreground pixels have at most8 black pixels between
them on any scanline. Reused source cells conservatively connect their instances;
unchanged native cells anchor their components to the original arrangement.
Six independent populated components remain. Selected components use a second
warm-metal vertical arrangement (three-scanline shift, with symmetric mirrors).
Bit3 selects the second palette bank; the existing128-byte resident cache already
has room for both arrangements and their reversed rows. No game RAM or frame-time
work is added. This conservatively reuses styles rather than assigning a unique
palette to every building instance. Black paper, bitmap geometry and collision
flags remain intact. Preserve/chroma alternatives remain available.

Validation: all46 whole-screen title states match independent expected pixels and
colours on both targets; mid-sweep Fuse captures contain no stray screen data.
All21 sound slots match packed reference curves; dedicated65 tests confirm exactly
one shape14 write and no writes to music C or joystick R14/R15. Two music loops,
live joystick/audio, IRQ register/banking contracts and music/effect mixing pass.
The map-level proof checks738812 occupied8×1 cells across8 phases with0 introduced
foreground colour conflicts. Fuse also passes all8 actual scrolling phases.
Extended8k-refresh traces:599312 SRAM/528192 ROM bytes,0 bitmap or colour motion
errors. Initial-world ownership, complete sprites, restoration, orb animation,
compiled ship cache and keyboard selection pass. The8k-refresh read-only run has
0 game ROM writes; all eight cartridge banks are immutable. Legacy r12/r13 failure
controls still detect their historical defects; these expected failures are kept.

Diagnostics: `build/diagnostics/terrain_islands_r20/terrain_atlas.png`,
`build/diagnostics/terrain_motion_r20/trace_extended_detail.json`,
`build/audio/selected65_validation_r20.json` and versioned title/audio reports.
Build: `python scripts/build_ecm_native.py`, `python scripts/build_rom_ecm.py`;
publication: `python scripts/publish_rom_ecm_r20.py` requires matching checks.
Versioned r20 verification scripts sit beside their r19 controls. Scope remains
level one, physical hardware untested,512KB assets still staging-only.

Deterministic final rebuild and gated publication passed; flat ROM65536 bytes,
read-only DCK descriptors2 in everybank, AROS header verified. Final hashes:
build/ecm_native/RType_level1_ECM_TSPico_RAM_r20.dck 166e47a4b604427ded5ef93e1311240396fc5a3379167210c2d8446fcab77b6e
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r20.rom 67709aa16346432a8dd9b41b3f76e65a7f931cb6817d5e86a01ae4bb6b2da69b
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r20.dck f828609b3e3c6be7e1d909a4b0f2c7a95197fe912a92e3f6899a2ef1a34f4cf5


## 056 — r21 per-instance terrain group palettes (2026-11-02)


The user correctly observed that r20 did not visibly give separated groups
different palettes. Its graph merged all occurrences of each source tile cell.
It also used C4BE as map end, scanning539 apparent columns including enemy data.
The actual map is E571–E788 (C4BC to C4B4),535 bytes/107 columns, as already
documented by the expanded-cache builder. r21 uses these verified bounds.

The new graph contains level instances rather than source tile identities.
Within each8-row band, foreground cells separated by at most8 black pixels on any
scanline stay connected, preserving colour compatibility for every fine scroll
phase. Larger gaps allow independent arrangements. Alternating independent groups
use warm copper/gold/red or cool cyan/blue machinery, with different vertical
arrangements. Contiguous areas retain compatible colours; row bands can have
different group boundaries because ECM works at8×1 resolution. Shared source
art no longer forces disconnected occurrences into the same palette.

The actual map yields196 populated band groups. Their20-bit column masks compress
to87 five-byte records including a terminating zero mask (435 bytes). ROM0
08C0–0BBF contains the table and helpers, separately reserved from death65 at0BC0.
The selected mask is cached in three bytes of idle title scratch FC50–FC52 once
per incoming8-pixel column. Initial drawing looks up its world position directly.
Only staged RAM tokens are modified; cartridge memory remains read-only.
Terrain repaint/repair reads the retained instance style rather than the source
tile's style. Collision flags and geometry are preserved.

To fit both64KB builds, the unused fine4 title atlas at9EA0–9FEF is reclaimed
for music data. r20's sweep already steps8 pixels; all46 states remain unchanged.
A build assertion rejects a return to a4-pixel sweep without restoring its atlas.
Selected death65 and its music-channel ownership remain unchanged.

Validation:
- Whole-level native helper test:1831 converted instance cells per target;
  181 source cells demonstrably receive different styles in different instances.
- Natural boot checks validate initial cells and actual incoming streamed tokens
  against world positions. Both targets show warm buildings beside cool ground.
- Independent535-byte map composition checks99997 occupied8×1 cells across all8
  fine phases:0 introduced foreground-colour conflicts.
- All8 real Fuse scrolling phases pass on SRAM and read-only ROM.
- Extended8k-refresh traces check596816 SRAM/524592 ROM bytes:0 bitmap or
  foreground-colour motion errors. Historical r12 failure control still fails.
- Initial-world ownership, all3480 sprite cases per target,1160 background sprites,
  8996 restores and erasures,3840 spans, compiled cache, orb animation and IRQ
  contracts pass. Live joystick/audio, two music loops and death65 checks pass.
-46 title states, whole-screen Fuse captures and stable publication pass.
  Fuse flight retraces show no trails or path deaths.
- Read-only8k-refresh run:0 game ROM writes, all eight banks immutable.

Diagnostics: `build/diagnostics/terrain_groups_r21/fuse_terrain.png` is an actual
Fuse capture crop. `whole_level.png` and `group_comparison.png` are offline palette
previews. `instance_groups_r21.json` and `all_group_instances_r21.json` prove native
application, not merely authored palette tables. Versioned traces retain controls.

An initial implementation had a row-mask rotate off by one. The independent
world-position test caught it before publication; corrected and all checks rerun.
The observation script also needed the emulator's XL field and the ROM helper's
actual return point; these test-harness corrections are recorded here.

Rebuild: `python scripts/build_ecm_native.py`, `python scripts/build_rom_ecm.py`.
Publish only after checks: `python scripts/publish_rom_ecm_r21.py`.
Level one only; physical hardware untested;512KB cache remains staging-only.

Deterministic rebuild matched all gated hashes. Final65536-byte PicoROM,
AROS header and eight read-only DCK descriptors verified. Final artifacts:
build/ecm_native/RType_level1_ECM_TSPico_RAM_r21.dck f482e1f6358caba09876e278b324a1c70026fae68d45e2cd5797386a864a43eb
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r21.rom b2d3bf703d7ce628b42ce724016de5cf2bbf939f56378ba70d89cce4e2301c9b
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r21.dck e13fa7b4cea096ef455a87cc3b3b512bb66c1e295e3281a2c8059c70e9c697d7


## 057 — explicit level themes with within-level variation (2026-11-02)

Added assets/terrain_themes.json and scripts/terrain_themes.py. All eight levels
have an authored coherent theme family with two complementary group arrangements.
Level1 keeps its accepted copper/gold and cyan/blue appearance and r21 group rules.
The build now emits eight128-byte palette tables, a status manifest, and the
comparison image build/art_assets/level_themes/theme_families.png. Level1 is selected
explicitly by the playable build. Levels2–8 are prepared assets, not playable ports
or automatic runtime level switching, and still need arcade-reference refinement.

Validation: eight distinct table hashes; black paper/no flash, valid ink indices,
and forward/reverse row compatibility asserted for every family. Both full
cartridge rebuilds match their accepted r21 hashes exactly; gated read-only
publication passed. No gameplay bytes or memory costs changed. No new hardware test.


## 058 — M music toggle and audited implementation coverage (2026-11-02)


Press M to switch music off/on. Music starts enabled. One transition is accepted
per press; holding M does not repeat. Song decoding continues while muted, so
unmuting resumes at the current position rather than restarting. Fire and death
effects remain enabled, including the selected65 triangle/noise death effect.
The preference survives menus and life restarts during the same running session.

| Area | Implemented | Remaining |
| --- | --- | --- |
| Levels | Level1 gameplay in SRAM and read-only64KB builds | Levels2–8 loading, native compatibility, rendering, progression and validation |
| Music | One looping first-level2019 AY arrangement,2305 ticks/46.1sec; M control | Other level/boss/title music selection and resident/banked playback |
| Boss graphics | ECM material shading on the Spectrum-derived level1 boss/enemy shapes | Full arcade-derived geometry/animation conversion for the bosses |
| Arcade graphics | Terrain interiors and three orb animation cels integrated | Remaining enemies/bosses and later-level art |
| Themes | Level1 complementary group palettes; eight authored theme families generated | Apply/refine later themes when their gameplay is converted |
| Expanded RAM |512KB staging/cache assets | Live gameplay consumer and full-game deployment |

Native music comes from the local2019 AY arrangement capture, entry0, not a claim
that all original arcade music is converted. Existing source notes in
docs/r16_logo_music_arcade_sfx.md retain the uncertain MSX/CPC attribution.
All70 level1 enemy descriptors have colour lookup coverage, which is not the
same as converting all arcade boss graphics. Boss geometry is still primarily
Spectrum-derived. Prepared source payloads/theme assets are not playable levels.

Implementation: music_tick polls keyboard row7FFE bit2 at50Hz through ROM0:11D0.
FD93 is the mute preference; FD94 debounces the held key. Both are initialized
once by the AY IRQ startup. These bytes sit beyond the music state FD92 and before
native game code FDA5. The music-owned-volume helper at0ED4 emits zero for R8–10
when muted, after the existing SFX channel-ownership filter. It never silences
an effect-owned channel or writes joystick R14/R15. ROM0:11D0–11EF is separate
from initial_terrain, which ends11C2. Native banking/IFF contracts remain intact.

Validation: both targets pass160 ticks with four held/released press sequences,
140 muted-volume checks and122 SFX-owned-volume checks. Music shadow states match
an unmuted control throughout; boot defaults enabled. Real Fuse native keyboard
port-result injection confirms a held first press mutes and a second press unmutes.
Logs/commands: build/diagnostics/music_toggle_r22; CPU report:
build/audio/music_toggle_validation_r22.json. Standard music loops, selected65,
IRQ contracts, live joystick/music, sprites/restoration, instance palettes, all8
Fuse scroll phases, full title states and read-only execution are revalidated.
Extended scrolling controls remain under build/diagnostics/terrain_motion_r22.

Build with scripts/build_ecm_native.py and scripts/build_rom_ecm.py; the versioned
publisher now also requires matching CPU and Fuse music-toggle reports.
Level1 only; physical hardware untested.

Final deterministic rebuild and publication gates passed. Flat65536-byte ROM,
AROS header and read-only DCK descriptors verified.
build/ecm_native/RType_level1_ECM_TSPico_RAM_r22.dck 55252403b389475530f7d2f77636f80f3c5bd03aa286d2fc49525d68c8e77b05
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r22.rom 8b52535fd38b5f18bf38c3e9bd43236401458f5912f9523ede12b5e33498cc84
build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r22.dck b4c53089ef840f7b675de4ef6deee85a3b286f8dd7421d59f0213fac97cc5acb
Extended motion: [{"target": "r22", "checked": 594784, "bitmap_mismatches": 0, "colour_motion_mismatches": 0}, {"target": "rom_r22", "checked": 522432, "bitmap_mismatches": 0, "colour_motion_mismatches": 0}]


## 059 — Eight-level ECM/AY full-game TSPico512 candidate (2026-11-02)

User authorized completing the remaining level/music/boss conversions. Applied the local TS2068 cartridge, TSPico, graphics/animation and audio skills; consulted the hardware-tested512KB video source and official MAME M72 sprite rendering source. Reference projects and source archives were not changed.

Published `build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r23.zip` and `RType_TS2068_ECM_fullgame_TSPico512_r23.ram512`. SD ZIP SHA256 `2ef1db9d7f7fb835c5ff253fabe5c9e12bf68e1653410861a6a00589c1c8dfde`; memory-image SHA256 `a2133a307bfdff576dc7590403d6dda322d29d75a4c38efe9936772fe7d0db02`. See `docs/fullgame_r23.md` for run instructions and limits. The ZIP contains RTYPE/RTFULL.TAP plus16 RTFGxx.TAP volumes, and validation reports. This is an emulator/controller-model candidate, not a physical hardware pass.

All eight original level payloads were extracted independently; bounds/descriptor diagnostics are in foundation/manifest.json, enemy_boss_contacts.png, world_end_contacts.png, levelNN_world.png and foundation/levelNN*. Native foundation tests passed before ECM integration. Full ECM uses correct per-level terrain bounds/maps/descriptors and compact typed group tables (largest579bytes). Each region contains its own live workspace, palette dictionary and level music. The accepted level-one arcade-derived terrain is retained through assets/terrain_level01_arcade.bin. Regions actively switch through stock legacy MEMDOCK even SRAM slots0..14; this is no longer a staging-only512KB asset bundle.

Arcade diagnostic capture reached all eight stages and loop2 with invulnerability/lives diagnostics. Provenance,327 frame captures, palette dumps, sprite RAM/state dumps, contact sheets, and MAME logs are under arcade_reference/. The primary FBNeo cheat reference is stored under research/rtype_cheat_reference.txt; two attempts to access the Pugsy site returned403. Sprite decoder coordinates were initially wrong; calibrated visible origin64,0 against actual screenshots. Source composites are under arcade_objects/; giant_ship_panorama.png and giant_ship_stitch.json record a multi-capture hull reconstruction. Both preserve/chroma boss styles, source crops, encoded assets and galleries are under converted/. Chroma is active. Converted Gomander terrain tiles19..31 separately; gomander_arcade.png/gomander_ecm.png show the source/result. Its conservative32-row palette still warrants visual refinement. Actual arcade art is fitted to native cell envelopes; native AI and all arcade animation frames are not replaced.

Initial boss palette fitting produced poor white/yellow results and cargo clipping. Revised to independent per-cell8x1 colour pairs and checked free payload pools for selected small frames. Level8's6x6/6x5 expansions exceeded free space; kept6x4. Palette IDs reserve54 as the native transparent sentinel;1024-byte dictionaries are copied from immutable region7:E000 to live DOCK1:2000 at boot. Selected descriptor updates stay below resident AY F87C. All native descriptor pointers, clips, four flips and damage flashes pass 10416 actual-Z80 bitmap/colour comparisons, including original non-boss enemies. Initial test reuse failed because native blitter code self-modifies; reset its state per independent case, then all comparisons passed. Results: boss_validation.json/log.

Extracted all16 local Goodboy/Tiboh2019 AY entries. Entries0..7 are integrated level songs; eight additional entries are prepared but not selected as event music. No established MSX/CPC attribution claim. Unbounded compression grammar initially overflowed48-byte pending storage on level3/7, corrupting music state and eventually stalling gameplay. Bounded grammar depth22 fixes this; late-window update assertions now prevent a startup-only false pass. Each level song passes two exact source-register loops; maximum pending usage 42 bytes. Reports and source traces: audio/native_validation.json/log, grammar_inventory.json, music_probe_N.json, music_grammar_N.json. M toggles four times across160 ticks in each level; held-key debouncing, continuing song position, mute-owned volumes and retained SFX ownership all pass controls_validation.json/log. Effect65 remains selected.

All eight levels pass8000 refreshes of sustained ECM play, with updates [1059, 1003, 770, 898, 767, 984, 839, 1109] and late-window counts [138, 172, 124, 204, 140, 224, 152, 180]. Reports/captures: foundation/ecm_validation.json, foundation/levelNN_ecm_live.bin, final_runtime.log and level01/final_runtime.log. Tests bypass player death and inject boss victory counters for progression; they are not normal unassisted playthroughs. Controller fixture guards code/ROM writes after handoff, enforces paced TX, delayed selectors and plain/verbose replies.

Gateway design initially used HOME8100 permanently, but the native startup clear list wipes8100..837F. Replaced it with a temporary HOMEA000 overlay saved/restored via8100, with restore tail at5E00 after the workspace bounce. Initial tail-copy ordering was corrected so the bounce cannot overwrite it. All eight bank transitions preserve score, mute preference, new payload/palette and compiled ship cache (gateway_validation.json/log). Native progression reaches all eight levels (progression_validation.json/log). The real final-level ending runs and returns to level-one play (ending_validation.json/log); a first assertion stopped too early at selector change, corrected to await resumed gameplay. Those progression/ending paths use native C25E/C2A3 with the actual stack and execute real Z80 MEMDOCK code.

SD preloader uses the unmodified legacy transport from the already-tested VU3D512KB demo, with explicit bank-safe copy trampolines and eight read-only priming reads. Actual Z80 loader/model loads and compares524288 bytes,16 mounts,128 CODE blocks,136 priming reads,110.198 emulated seconds. Two running checksums plus TAP XOR and a full second readback sweep reject a deliberate region4/0 alias with E2. Reports: preloader_validation.json/log, package_manifest.json; preloader_screen.bin/png are diagnostic screenshots (earlier PNG showed clipped font, font corrected in assets/fullgame_preloader_font.bin). No new firmware was installed or modified. Loader hash is bound in the report.

Reproduce with scripts/build_fullgame.py from the audited local capture/source assets. It prepares both art styles, bounded music grammars, eight ECM levels, initialized runtime banks, full image, SD volumes, all native tests and hash-gated publication. Outputs are versioned separately. Normal level-one defaults were restored afterward and rebuilt exactly: SRAM BIN a7e0e09c0d935842279a98876f14f3b728d3de3ae1ca83319580ca3b6b7ad90f, DCK55252403b389475530f7d2f77636f80f3c5bd03aa286d2fc49525d68c8e77b05. Read-only PicoROM remains8b52535fd38b5f18bf38c3e9bd43236401458f5912f9523ede12b5e33498cc84. Logs: restore_r22.log. Existing64KB cartridge is read-only and level-one only; this work does not claim all eight full-colour levels/music fit a standalone64KB cartridge. Physical hardware verification and further visual/boss-balance refinement remain outstanding.


## 060 — Protected title text and narrow raster delta animation, r24 (2026-11-02)

User reported moving stars deleting the tops of BLAST OFF AND STRIKE and related lines, and requested TSCodec-style motion deltas. Read the graphics/animation and cartridge skills, including buffering/optimization/validation references; inspected the actual TSVideoCodec paired raster replacement decoder. Reference projects remain unchanged.

Root cause: title_publish protected only six logo rows in the native dirty grid, leaving the upper text unprotected. Added text rows2..11, cols9..31. The footer cannot be protected by extending that grid because IRQ code lives at8383; a small ROM0 star-entry guard suppresses menu stars in its band and preserves original gameplay entry behavior. Actual scripted Fuse refresh600 captures show intact text in SRAM and true-ROM targets: build/ecm_native/probe_600_r24_text.* and build/readonly_ecm/probe_600_r24_text.*.

Replaced full3072-byte staging clear, glyph-by-glyph composition and full-rectangle publication with reusable OR-suffix phase assets and narrow old/new replacement windows. This follows TSCodec retained raster concepts but is a geometry-driven title decoder, not a full-frame video file or the stock TSCodec wire format. Atlas5376bytes, phase cache1344bytes, max dirty span8byte columns per row; fixed letters stay untouched outside that span. Shared white/cyan vertical colours are used during overlap, then final artwork colours settle on released columns. Quantized source pixels/dither are shifted once rather than refitted each phase.

Two-pixel trial:178 exact states but5.7246seconds total; selected four-pixel sweep/spread:116 states,3.76165seconds versus previous46/4.39254seconds, approximately31 vs10 completed pictures/s in TSRun. Mean decoder87257.7T, max119573T; not a physical timing or zero-tearing claim. Actual-frame preview: build/diagnostics/title_delta_r24/title_delta.gif, assembled from116 native CPU captures at measured intervals. All sram/rom/full_stateN.bin are actual HOME dumps; initial menu captures are *_menu_initial.bin.

Diagnostic corrections: initial HALT stalled because display initialization left interrupts inhibited; explicitly select mode2 before waiting. Initial SRAM palette test found mask19 mapped away HOME attributes; restored mask13 for visible publication and93 only around stack-free atlas LDIR. An initial ROM build exceeded the1536-byte renderer by4bytes; moved footer selection to native menu/game state and removed redundant flag writes. An early test accepted a stale ROM while checking only a picture count; build runners now fail on subprocess errors and title validation requires the true final x208/spread state. Final source cleanup replaced magic patch offsets with assembler symbols and reproduced exact validated bytes.

Validation:116 complete bitmap/ECM states each for SRAM, read-only and full-game;1024 star updates and900240 text-byte checks per target, including top lines and copyright. Reports: build/diagnostics/title_delta_r24/validation.json and validation_full.json. Both level-one targets pass3480 complete sprite/clip/flip/IFF cases each; source-exact music loops, four M toggles with retained SFX, live AY/joystick and7 full IRQ mapping/register cases. True-ROM runtime:8000 refreshes, zero ROM writes, immutable banks, sustained gameplay. Reports: build/audio/*r24*.json/log, build/readonly_ecm/runtime_validation.json, sprite_validation.json, build/ecm_native/all_sram_validation.json. No new change to gameplay renderers, music data or enemy assets beyond title protection.

All eight r24 full-game levels pass sustained gameplay again; all10416 enemy cases, eight level songs, M/SFX controls, eight MEMDOCK transitions, ending/restart, full512KB byte-exact preloader and negative alias control pass. Native full title state hash is bound to level01/game_progression.bin by the publisher. Logs: build/fullgame/r24_*.log; reports retain explicit diagnostic victories/death-bypass and controller-model scope.

Published SRAM level-one r24 BIN/DCK: d0fde5028b9100e9e20b96b623cf8d3ca11718c295c34afc8f0f744c9eda7549. True64KB read-only RType_level1_ECM_64K_PicoROM_r24.rom BIN hash 0ac6250db0d99276456a558b2c36afb987f3709eea6551c260a9e8ccf6cea041, with matching .bin/.dck under build/readonly_ecm. Full TSPico512 image hash a3a23d3067c5da8d434c46c8874396c3e067906855890acdd8342a49938a174b; ZIP RType_TS2068_ECM_fullgame_TSPico512_r24.zip hash f1834cd9d508627e7ae0d9ee9cb6d276015c5ef38f962f1b420959bb5d96e291. See docs/title_delta_r24.md and docs/fullgame_r24.md. Full game still requires512KB; read-only64KB remains level-one only. Hardware untested. r22 was rebuilt and restored exactly to a7e0e09c0d935842279a98876f14f3b728d3de3ae1ca83319580ca3b6b7ad90f; r23 versioned releases were preserved.


## 061 — Title number keys select the starting level, r25 (2026-11-02)

User requested a way to choose a different starting level before starting. Full TSPico512 r25 now accepts1..8 on the title/start pages, displays "1-8 LEVEL n", and applies the choice when Fire is pressed. The number key itself never starts a game. Default1; the preference persists for the session. Original keyboard0 and built-in joystick Fire still start. The indicator is drawn only in ECM title mode, leaving the cycling legacy high-score page untouched. A small dash stroke supplements the original font's missing hyphen. Image: build/fullgame/select_level8_menu.png, rendered from actual select_level8_menu.bin; all select_levelN_menu.bin captures are from native execution before Fire.

Implementation is isolated in src/fullgame_level_select.asm and installed by scripts/build_fullgame_image.py only when RTYPE_LEVEL_SELECT=1. It uses the full build's unused legacy ROM0:0C00..0CFF palette slot; full enemy palettes already use the1024-byte DOCK1 dictionary. The first free-slot assertion incorrectly expectedFF fill, but that slot retained obsolete authoring ramps; changed to the explicit full-build empty boss_colours contract and verified all10416 enemy cases against the selector-patched images. Resident HOME FD95 stores the chosen1..8, FD96 caches the shown value, FD97..FDA1 is the terminated11-character indicator, FDA2 is the current numeric-key flag, and FDA3 is a one-shot new-game flag. These remain above music state FD94 and below native code FDA5. Original input registers/flags and native control-type selection are preserved.

Title dispatch scans real F7FE/EFFE rows and consumes numeric presses. Initial tests found the original Sinclair1 fallback treating key5 as Fire. Consuming only the first sample still allowed a key arriving between polls to trigger the fallback, exposed after adding the high-score display guard. The menu-only C01C fallback is now skipped because1..8 are reserved for selection; gameplay controls remain unchanged. The new-game hook originally shared863D with ordinary stage changes and reset level2 to the selected1; an explicit one-shot arm at the original C042 Fire path now restricts selected-level loading to new games. Normal transitions, respawns and ending loops retain their original stage behavior. Loading uses the existing paced, primed MEMDOCK gateway, preserves the workspace/music preference and initializes the chosen level's native checkpoint pointers.

Tests: verify_level_select.mjs selects every1..8 via actual keyboard rows, holds/releases the key, verifies no bank switch before Fire, ignores9, then starts through joystick Fire and runs140 actual gameplay updates. Correct region/slot, native header, level character and terrain palette pass for all eight. Keyboard0 additionally starts selected levels2 and8 (verify_level_select_keyboard.mjs). verify_selector_pages.mjs confirms choosing a level in legacy mode leaves both screen planes unchanged and updates the indicator on return to ECM. All10416 enemy draw/flip/clip/flash cases pass against game_progression.bin images (verify_selector_bosses.mjs). Reports: level_select_validation.json/log, level_select_keyboard_validation.json, level_select_page_validation.json, boss_selector_validation.json under build/fullgame.

Full regression gates pass again: eight MEMDOCK transitions, all-level native progression, original final ending and resumed level1, byte-exact512KB preload and negative alias control, and116 exact title states plus repeated star/text checks. Original r24 per-level game/art/music bytes remain unchanged; selector patches are applied only to the combined full-game image. Title verification now derives the motion hook from the actual DCK bytes rather than stale generated title_motion_sram.bin after the r22 defaults were restored. An initial report path typo overwrote the base boss report with patched hashes; fixed to separate boss_selector_validation.json and reran both suites before publication. All build runners stop on nonzero exit. Final pipeline/logs: scripts/validate_level_select.py; build/fullgame/r25_*.log. Publish gates bind selector/page/enemy reports and title coverage to the exact image. Physical hardware untested; tests use the established controller model and diagnostic player-death bypass.

Published build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r25.zip, SHA256 e0d834b0ac9905a2bdc00eda81dc8a0127503fc9a22299dd04d519ee45f3f301. Raw image RType_TS2068_ECM_fullgame_TSPico512_r25.ram512 SHA256 885566b16ffa128b50b3c37afe1040d50d3c0d740bcf16245ff7b02dae2593c7. ZIP includes RTYPE SD loader/volumes plus Fuse-level-previews/Level_1.dck..Level_8.dck for direct single-stage testing without the SD loader. Preview files are the already-validated r24 per-level ECM candidates, not full progression images; they cannot load the following stage after victory and do not offer the512KB number selector. Instructions: docs/fullgame_r25.md. Reproduce with RTYPE_TITLE_DELTA=1 and RTYPE_LEVEL_SELECT=1 using scripts/build_fullgame.py, or validate_level_select.py from prepared r24 level assets. The64KB read-only cartridge remains r24 level-one only; prior versioned releases are preserved.


## 062 — L2 blue zones: screen-memory/raster diagnosis and clean-redraw candidate (2026-11-02)

User reports static blue zones near the bottom in Fuse Level_2.dck; screenshot also contains faint title/prompts behind the playfield. User confirmed the emulator/file via clarification. Reproduced the preview and full selected-level2 paths in TSRun, captured early handover frames800..930 in5-refresh steps and later1000/1300/1600/2000/2400 RAM/DOCK views, then repeated with firing and actual raster pixel buffers. Artifacts and render scripts are under build/diagnostics/l2_blue and scripts/probe_l2*. Large blue rectangles/title ghosts are absent from these captures; scattered blue ink inside scrolling texture is distinct. No scenery/collision change was justified by those observations.

Scripted Fuse captures in1.7.0 (C:/Program Files (x86)/Fuse/fuse.exe) and the user's installed1.10.0 (C:/apps/emulation/Fuse/fuse.exe) yield identical CPU state and HOME-memory SHA256 ecb8a7d5955d0eeec931670453977ad3f8b8089ea34e134a581af16942be62e6 at the same controlled completed frame. Source cartridge BIN hash ce42894393dbe8963045d1cb73eaacb7449ccec548aa03c30e5d3fe2beb5802a. Captures: build/ecm_native/probe_1000_joy_l2_blue.*, probe_1150_joy_l2_blue.*, probe_1000_joy_l2_fuse110.*. Scripts probe_ecm.py and probe_fuse110.py.

Used computer-use skill to inspect the actual Fuse window. The app/window inventory returned the user's1.10 process, but two screenshot attempts timed out even after activation; no game input, file menu operations, settings or emulator installation changes were made. Read local release notes and obtained a separate upstream source copy under build/research/fuse_upstream from https://git.code.sf.net/p/fuse-emulator/fuse (HEAD67d72235610a9821c780499a0c10d89512656127). Reviewed scld.c, display/render/Win32 dirty-region code and FMF format. Recent refresh/scaler changes are context, not proof of a particular emulator bug. Browser raw-source requests failed; git source access succeeded. The GUI/scaler path remains a hypothesis because the visible artifact could not be captured directly.

Recorded the user's Fuse version with its own FMF logging to capture displayed raster records rather than only RAM: probe_1000_joy_l2_movie.fmf and decoded .frameN.png files under build/ecm_native. Actual FMF frames also show clean scenery/black sky, without the reported static rectangles/title ghosts. scripts/read_fmf_frames.py implements the documented upstream run-length/plane records. Debugger exit omits the final zlib trailer, so the decoder uses a streaming decompressor; all1006 recorded frames decode. This evidence narrows the suspect path to displayed/scaled/cache handling but does not establish the exact source of the user's screenshot artifact.

Created a minimal diagnostic workaround in src/clean_game_handover.asm and scripts/build_clean_preview.py: after ordinary game initialization, preserve AF, select standard video with a black bitmap, wait for two interrupts (one complete display refresh), then restore ECM and AF. The16-byte wrapper uses the full preview's unused ROM0 CF0..CFF slot and replaces only the8640 initialization CALL. Terrain/sprite/collision payload bytes A4AE..D87B are asserted unchanged. No full-game or64KB read-only release was overwritten.

Candidate: build/fullgame/previews_r26/Level_2_clean_redraw_r26.dck (+.bin/.json/README.txt); BIN SHA256 f2722a6c92954e2881225f4567b8001ebf9bdd0943b251868e57c3b91f00422a. verify_clean_preview.mjs confirms AF/mapping/ECM return and112563T between refresh entry/exit,8000refreshes, 998 actual gameplay updates and 172 late-window updates. Initial test falsely trapped factory-ROM PC0CFF before cartridge entry; tightened it to the actual DOCK runtime mapping/entry. Final tests pass. Scripted Fuse1.10 capture/movie: probe_1000_joy_l2_clean_r26.*; screen remains clean and scenery scrolls. The visible blue-block fix is NOT confirmed; deliver this diagnostic for the user's same display setup. Hardware untested. r25 remains the current verified full-game release.


## 063 — Actual L2/L4 blue-rectangle cause: retained palette IDs, r27 (2026-11-02)

User supplied L4 green-chain screenshot with blue rectangles, then confirmed L2 clean-redraw still showed a blue rectangle. Reproduced L4 immediately in TSRun screen RAM; the artifacts were not limited to the GUI. Prior062 display/cache hypothesis was incomplete and the redraw-only r26 did not fix the actual palette mechanism. Preserve its diagnostic history, but supersede that workaround with r27.

Root cause: converted source attributes carry enemy dictionary IDs. Direct actor drawing decoded them, but background legacy-colour storage/restore copied ID12 as native0C (green ink/blue paper), filling empty portions blue. Live write tracing located the flat native copy at0E7E, fed from legacy cells around58DD. Source/direct-sprite tests passed because they did not exercise retained restoration; added exhaustive retained and actual-scene tests rather than relaxing existing expectations.

Implemented src/terrain_palette_full.asm, accurate enemy/pool predicates and retained encoding in full_boss_colour_lookup.inc, FULL-specific fast-row pointer lookup, and retained publication/group guards in the full terrain-group compiler. Constant16 enemy rows store actual native colours; other rows use dedicated90..FF/10..1F tags. Terrain alone uses80..8F. Fast fill/palette loops are unrolled/four-row batched to limit extra decode cost. Common sprite and non-solid terrain token reservations are asserted. No source geometry/sprite bitmap or native collision routine edits. Default/stock-ROM targets keep the original separate colour format.

Expanded-pool regression: first accurate source-range predicate used IFDEF on EQU labels, so sjasmplus omitted the pool branch and level5 boss8 fell back to native colours. All-enemy tests caught it. Changed to numeric IF ENEMY_POOL_END and define zero for no pool; added positive pool-address cases to the encoder tests. All10416 direct/flip/clip/flash cases now pass, including expanded level5..8 frames. Terrain/map/descriptor addresses between graphics and pools are explicitly excluded, fixing the former overly broad range as well.

Validation: 23800 retained cases across8 levels cover all256 byte tokens, all128 dictionary IDs with both source flags, native/terrain rows, mixed fast paths, native-colour copies, reverse-marker classification and positive/negative pools. Report: retained_palette_validation.json/log; final run logs r27_verify_retained_palette.mjs.log. All eight8000-refresh gameplay runs pass; updates [1004, 929, 730, 790, 700, 873, 767, 1046], late counts [132, 164, 120, 180, 129, 188, 141, 168]. Native source data, every enemy image, all songs/M/SFX controls, number selection/keyboard0, page safety, eight bank transitions, original ending/restart, full512KB preloader/alias rejection and exact116-state title all pass again under r27_*.log.

Visual/negative controls: old L4 preview retained424 green-on-blue attribute bytes in a real Fuse1.10 capture; corrected L4 has0, corrected L2 capture has0. Files build/ecm_native/probe_1300_joy_l4_before.*, *_l4_palette_r27.*, *_l2_palette_r27.*; scene_palette_validation.json binds source hashes. Native gallery before/after: build/diagnostics/l4_boxes/before_1300.png and preview_1300.home.png; the green circular chain now sits on black. scripts/compare_l2_retained.mjs stress test: old redraw-only r26 records 110 incorrect copies and corrected build 0; old/new updates 1240/1129. Natural timing/random states diverge, so these are not a controlled speed benchmark. The actual palette-path fix addresses the renewed L2 report; no emulator install/settings changes were made.

Release: build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r27.zip SHA256 8b25d331c4ee16169d6401830ac6a127aa953c484fb48e9da532e6b55242b225; image SHA256 741ad3721c27166265d4c260235f10b8919f9f36e9ee5951702c35135ddc87a1. Includes updated Fuse-level-previews for all8 stages. Also publish direct previews_r27/Level_N_palette_fix_r27.dck, bound by previews_r27/manifest.json. L2 BIN 276ec7be09b218845648dc2d9ed33bc5667015644f1bce24f4e270f9b00c4499; L4 BIN c544447705c5a350ac20534a8bd9b4e8de1dde0ce541c1945c5e48f7bec0f565. Docs: docs/retained_palette_r27.md and docs/fullgame_r27.md. Single-stage previews still do not load a following stage after victory; full game requires512KB TSPico. Physical hardware remains untested. Normal r22 output rebuilt to a7e0e09c0d935842279a98876f14f3b728d3de3ae1ca83319580ca3b6b7ad90f after final publication; r24 read-only/r25 full releases remain preserved.


## 064 — L7 blue/magenta report: compare old preview and r27 (2026-11-02)

User supplied L7 screenshot with blue and magenta rectangles. Asked whether the file is older Level_7.dck or Level_7_palette_fix_r27.dck; version was not yet confirmed at time of this record. Independently compared the archived r25 Fuse-level-previews/Level_7.dck with current r27 under identical startup inputs, with diagnostic death bypass. Reproduced blue rectangles in the older file; the sampled older scenes did not reproduce magenta rectangles. Current r27 is clean at all9 captures1000/1300/1600/2000/2400/3000/3500/4000/4500: zero zero-bitmap scanline bytes with blue paper and zero with magenta paper across the visible playfield. Blue ink that belongs to actual texture is excluded from that test; no broad colour deletion was applied.

Scripts: probe_l7_boxes.mjs, render_l7_boxes.py; old/fixed HOME/DOCK dumps and .home.png images under build/diagnostics/l7_boxes. Counters: build/fullgame/l7_rect_compare.json and l7_rectangle_comparison.log. Compared both files in the user's Fuse1.10 using native input injection and coherent refresh2000 captures: build/ecm_native/probe_2000_joy_l7_old.* and probe_2000_joy_l7_r27.*; logs under build/fullgame/l7_{old,r27}_fuse.log. Corrected image is clean; old shows rectangle patches. Native r27 L7 BIN SHA256 32bf6bf34aa14f092c93d79a9acf83e44c6e50fe87411aaf5350009291000097.

No additional engine patch was justified by these results; the existing r27 retained-palette fix already corrects this reproduced L7 case. Provide direct build/fullgame/previews_r27/Level_7_palette_fix_r27.dck to avoid accidentally continuing with the older single-level file. This comparison does not prove which file produced the user's screenshot or cover every future input path. If they confirm the exact r27 file still fails, continue from that input/version rather than assume the earlier diagnosis explains it. Prior releases and all source gameplay data were left unchanged.

## 065 — L8 scanline gap/palette planning (2026-11-02)

User marked curved upper/lower scenery gaps as opportunities for independently shaded groups. Read project state/history and R-Type AGENTS. Existing terrain_groups.py unions source cells across each eight-row band; L8 starts with long components spanning columns0..114 on rows0/1/18/19, hiding scanline-specific gaps. Testing the exact-gap threshold <=8 versus <=9 alone produces the same46 band groups, so that change was not applied.

Added scripts/l8_contour_palette.py, an OFFLINE ASSET PLANNER, not a runtime change. Reconstructs all184 world tile columns including native horizontal/vertical flips; joins source scanline colour variables wherever foreground pixels can share a byte at any fine-scroll alignment. Reused source instances are constrained together. Chooses stable gold/amethyst arrangements per source component, independent of screen position/frame. Exhaustive eight-phase checks across the entire160-line world yield zero planned colour conflicts. Candidate dictionary needs67 additional eight-byte rows after52 preserved enemy rows (119/128). Geometry in the preview is the original bitmap. This is a candidate recolouring of all foreground, including native edge pixels; integration must reconcile those edges with native flat attributes too.

Diagnostic outputs: build/diagnostics/l8_contours/level8_contour_plan.png (visually inspected, first256 pixels, scaled4x), level8_contour_world.npy, level8_contour_plan.json (explicit gaps and source-cell row IDs) and terrain_contour_dictionary.bin (candidate only). No DCK/BIN/gameplay source was patched. Current r27 remains unchanged. Remaining work: source-specific terrain dictionary decoding, vertical reversal, retained publication, native edge colours, scrolling/actor restoration tests, before claiming playable improvement. Low retained tags for IDs112+ cannot simply replace source solid attributes because bit7 carries geometry; rejected naive patch outputs and removed them.

Exploration: first analysis accidentally used default level-one native snapshot with L8 map bounds and failed tile-index assertion; corrected input is level08/snapshot.bin. Four material ramps exceeded dictionary capacity (85 added rows); two ramps fit67. Attempts to squeeze all tags below112 using flatter ramps needed100/64 rows and were rejected. A PowerShell quoting error prevented one edit, corrected through a literal helper script. These failed experiments produced no game release. Reproducible successful command: python scripts/l8_contour_palette.py.

## 066 — Higher-level enemy colour coverage audit (2026-11-02)

User reports sparse higher-level enemy colour. Audited every nonempty descriptor in converted level5..8 graphics, decoding the actual enemy dictionary and native/expanded descriptor pointers. Sparse diagnostic means at most two visible nonblack palette colours or one colour covers at least90% of visible pixels. Includes small projectiles/effects and animation frames, not unique enemy species: L5 9/37, L6 9/30, L7 17/45, L8 33/44. Descriptors without individual arcade-source conversion:18,14,39,39 respectively. Those fallback descriptors still use native flat cell rows; the existing boss conversion did not cover every regular enemy/effect. Thus prior all-boss coverage does not imply all-enemy high-colour coverage.

Added reproducible scripts/audit_enemy_colours.py. Data: build/diagnostics/enemy_colour_audit/audit.json; diagnostic higher_level_enemy_gallery.png visually inspected. Confirms white/cyan L7 ships and green/magenta L8 organisms remain largely flat. Gallery truncates IDs above45 for layout, audit JSON includes all descriptors. No playable assets modified. Art improvement requires mapping the remaining regular enemies/animation frames to genuine arcade references and rebuilding/testing, rather than arbitrary per-row stripe substitutions. Sparse count is a triage metric, not proof every small effect needs more colours.

## 067 — Cartridge/disk loading instructions, text overlay r28 (2026-11-02)

User requests replacement of rewind-side2 prompts and no device branding in instructions. Added reproducible scripts/build_loading_text.py, deriving from preserved r27 full image/ZIP and r24 read-only cartridge. Main prompt now LEVEL READY - PRESS ANY KEY; REWIND TAPE becomes PLEASE WAIT; STOP TAPE becomes DATA OK; START TAPE becomes READ DATA; SEARCHING FOR becomes SELECTING DATA. No device name appears in replacements or the new package README. Full game preloads every level, so prompt does not ask user to swap media. Every encoded string retains its original byte length and final high-bit terminator, with spaces for padding. Byte-difference assertions allow only those string intervals. Source originals remain unchanged.

Outputs under build/fullgame/loading_text_r28: RType_TS2068_fullgame_r28.zip, raw .ram512, eight Level_N.dck previews, RType_level1_cartridge_r28.rom and .dck, manifest.json with replacement offsets/hashes. Full image40 replacements; cartridge5. Cartridge still level1 only, full package512KB; single-level previews do not advance stages. No graphics upgrade is included. New disk blocks rebuilt and read back from final ZIP: all64 pages exactly match updated image and every block XOR validates. Initial DATA READY wording exceeded the9-byte field; length assertion caught it, shortened to DATA OK. One separate shell-quoted validation failed to parse; added literal Python readback directly to builder and reran successfully. No graphical diagnostic image created and no new emulator/hardware run claimed for this text-only change. Existing runtime code, pointers and gameplay geometry unchanged.

## 068 — Stop standalone previews entering the tape loader, r29 (2026-11-02)

User presses a key after the newly worded prompt and reaches ERROR IN LOADING. Acknowledged r28 only changed text and left standalone FE03 tape-loader execution intact. Added scripts/fix_preview_loader.py and verify_preview_end.mjs. All eight resident-level DCKs and the level-one read-only cartridge replace obsolete loader entry with a completion notice and IRQ-enabled wait. Uses native clear/text routines, selects standard video and fills attributes; prints PREVIEW COMPLETE and RESET TO REPLAY in two centered lines. No key requests a missing next cartridge. Full disk r28 untouched: all eight image regions statically verified with CALL0A08 transition gateway rather than CALLFE03 at offsetA2A3. Previously verified full progression behavior preserved; not rerun here.

Output build/fullgame/preview_end_r29/RType_standalone_previews_r29.zip, Level_N_preview_r29.dck and RType_level1_cartridge_r29.rom/.dck, manifest.json, verification.json. Deterministic runtime tests boot each image1200frames, force the resident loader entry with native transition mapping9, then run180frames and press keys80..99. All nine handlers reach completion wait and record zero calls to native cassette entry8F1F. This is targeted forced-entry testing, not nine natural level completions or hardware validation. completion_screen.home.bin and standard-mode completion_screen.png visually checked: both white lines centered, clean black background.

Failures resolved: initial message incorrectly assumed31-byte field (actual32); length assertion caught it. Read-only cartridge relocates clear routine73C2->B9C2 and text7280->B880; signature assertions caught that difference, separate relocation applied. Initial one-line ECM text clipped and retained colours; replaced with centered two-line standard-mode notice. Initial forced-entry test sampled arbitrary temporary mapping and stalled in text; corrected to actual transition mapping9. IRQ samples PC8383 are expected; wait-entry execution is tested rather than insisting every frame ends at HALT. Graphics source/palettes and full disk code unchanged. User must reset/reload standalone to replay; no software cartridge swapping promised.

## 069 — Physical disk loader ERROR03 before first page: deployment root, r30 (2026-11-02)

User reports physical loader title/loading512K then ERROR03, no PAGE or VERIFY line. Traced firmware reply03 to reviewed original CDIR directory-not-found path in TSPico/TS-Pico-Working_20261026/TS/tspico.py lines1037 onward. Its cd / explicitly selects /sd/TAP, not /sd. Our loader then cd RTYPE, while package README incorrectly instructed SD root/RTYPE. Therefore the documented layout cannot satisfy the loader's initial directory selection. Prior emulated controller only accepted cd commands without modelling real filesystem paths, so it missed this deployment mismatch. Physical installed firmware revision is not independently read here; user timing and reviewed source strongly support this diagnosis.

Read local hardware development SKILL.md plus protocol reference; no firmware changes. Added scripts/fix_disk_package_path.py. Output build/fullgame/disk_layout_r30/RType_TS2068_disk_r30.zip installs TAP/RTYPE/RTFULL.TAP and siblingRTFG00..0F.TAP by extracting at SD root. INSTALL.txt explains public root and relocation of an older root/RTYPE directory. All17 TAP files verified byte-identical to r28, preserving checksums/runtime image; only paths/readme changed. Corrected future instruction strings in build_fullgame_package.py and build_loading_text.py. r28 archive retained as historical, superseded for installation instructions. Device branding absent from new UI/instructions. Physical success pending; no new visual diagnostic created. User can alternatively move their existing complete RTYPE directory under TAP without downloading. No assertion that generic error03 always means path failure at later stages.

## 070 — Physical PAGE17 timeout and requested demand-loading architecture (2026-11-02)

User reaches PAGE17/3F then E0, requests level-at-a-time loading, Loading Level n between stages and idle-title prefetch interrupted by Start. Asked whether repeatable on same page (answer pending). E0 is local E_TIMEOUT. PAGE17 is hex23, last page of four-page volumeRTFG05.TAP; display changes only after next mount, so reported page may be stale during mountRTFG06. Cannot assign exact failing command from existing display. No unsupported claim of bad page data or a firmware defect.

Reviewed preloader, protocol transport and working firmware SEND_MSG. Need explicit operation/file/page diagnostics and timing-aware transport tests; existing model supplies instant FIFO responses and does not establish physical timing. Preserve failure evidence. New architecture requirements: resolve files relative to current launch directory; initially load only selected level; show Loading Level n during cache miss; cache fully verified regions; no partial region marked ready; idle title advances preload at bounded complete transaction boundaries; Fire/start wins before scheduling another block. Finish/drain an in-flight block before yielding, never abandon the FIFO mid-payload. Preserve AY ownership, game state/stack and native/retained rendering memory; title code must not run over a loading buffer or vice versa. Existing full64K runtime regions include live mutable caches, so a previously played region is not automatically a pristine reusable level. Design needs explicit invalidation/eviction and a resident loader memory allocation; merely stopping current preload after page7 would make transitions read uninitialized SRAM.

Concrete staging: added scripts/prepare_level_disk_assets.py. Generated build/fullgame/demand_loading/LEVEL01.TAP..LEVEL08.TAP and asset_manifest.json, each eight local-numbered CODE pages containing the exact r28 region. Parsed every resulting block, verified all XORs/header addresses and reconstructed each64KB region byte-for-byte. Status explicitly staged assets only, not a playable loader. No replacement RTFULL.TAP or release ZIP published; demand transitions and title prefetch remain unimplemented. Current r30 retained for baseline; no hardware timing fix claimed. No diagnostic image generated.

## 071 — PicoVideo bright-black trails: true-black candidate r31 (2026-11-02)

User supplied hardware photo12817.jpg under Elite .codex-remote-attachments/01a19855-5e8b-7c01-9834-206ac0fda11a/6aa459ae-dfd2-44a2-9ee2-fab14f491ac1/1-12817.jpg. Broad blue/grey sky and darker actor trails show that the two black intensities are distinct. Read graphics-animation SKILL.md and PicoVideo reference. Reviewed local PicoVideo4.2 macros.h/globals.c: native BLACK=00, BBLACK=25; tsColors keeps them distinct whereas speccyColors maps both to BLACK. Emulator build_graphics.PALETTE treats index0/8 alike, masking this issue. No video firmware or global display settings changed.

Implemented reproducible scripts/build_true_black.py overlay on preserved r28 image/r30 package, plus standalone r29 previews. Normalizes actual decoded attribute pairs containing black by clearing BRIGHT; preserves bright pairs whose two colours are nonblack. Normalizes enemy dictionary rows, common cached rows, terrain row cache, literal non-solid terrain cells, common native sprite attributes, compiled ship immediates and settled title attributes. Uses renderer symbols to restrict native publish-mask edits, never masks encoded enemy IDs. Corrects full_retained_attribute constant-row encoder which otherwise reintroduced bright-black. Added two small normal-native return helpers in previously unused E18/E20 space and retargets existing decoder/copy branches; fixed entry addresses and renderer size preserved. Native flat publication/HUD/mirror paths use normal intensity. Empty sky/title initialization no longer writes47/45. SharedBRIGHT means black-edged foreground loses bright intensity; enclosed nonblack pairs retain it. No bitmap/geometry changes.

Initial palette-only fixes were insufficient: live writer tracing showed bright literals restored atE60..E6E and terrain_line1876. Fixed central native publication as well. Initial broad-mask assertion detected extra AND7F instructions in boss-ID helpers; replaced with exact symbol-bounded colour writers so source IDs remain intact. No failed candidate was presented as fixed. Final verify_true_black.mjs runs4500refreshes per level with diagnostic death bypass, samples title200/700 and game1000/1300/2000/3000/4000. All56 samples have zero exposed bright-black scanline bytes; some bright enclosed nonblack pairs remain. Gameplay update counts625/474/437/386/364/439/400/614. Preboot temporary writes can still appear in writer histogram; published samples and static pair policy are the relevant evidence. This is not every possible gameplay input path or hardware verification.

verify_true_black_release.py reconstructs final ZIP pages and validates all64 pages/XORs against new image. Generates isolated true_black_fixture.mjs / verify_true_black_ending.mjs (original fixture/reports preserved), runs native progression across8 levels, ending/restart with diagnostic victories and death bypass; pass, image hash bound in ending_validation.json. Final live snapshot level1_live.home.bin rendered as level1_true_black.png and visually inspected (clean black sky, unchanged bitmap geometry). Reports under build/fullgame/true_black_r31. Publish candidate RType_TS2068_disk_r31.zip and direct Level_N_true_black_r31.dck, raw .ram512. Includes standalone completion notices fromr29 in preview DCKs; full disk keeps original full progression.

Important scope:64KB read-only r29 ROM is NOT updated by this overlay (different relocations/renderer); don't claim its hardware black issue fixed. Disk on-demand/title prefetch, arbitrary subdirectory loading and physicalE0 timing issue remain outstanding. r31 retains r30 installation layout and existing preloader. Physical display confirmation pending. Existing archives/artwork references untouched.

## 072 — Full disk game-over restart still calls tape loader: r32 (2026-11-02)

User played a level, died, restarted and saw LEVEL READY then error on full disk. Inspected every native direct CALLFE03: original8631 reinitialization,92B8 exhausted-credit/game-over path, andC2A3 normal stage progression. Full-image builder had patched onlyC2A3 (imageA2A3).92A4 native exhausted-credit branch resets credit/name state, compares level1, sets719C to0 when another level was resident, then callsFE03 at92B8. That bypassed the full bank gateway, exactly explaining the observed tape prompt/error after higher-level play.

scripts/build_restart_fix.py patches image offsets4631/52B8 in every region to CALL0A08, retaining existingA2A3 gateway call. Updated build_fullgame_image.py to reproduce both missing hooks on future builds. Static full-image scan finds no direct CALLFE03 remaining. Only48 code bytes changed fromr31 image, with normal-black palettes/graphics and native joystick/music unchanged. Output build/fullgame/restart_r32/RType_TS2068_disk_r32.zip and RType_TS2068_restart_r32.ram512, hash a7dc50116feff624421e236f06d288c2a05975ffaa0b103a05669184341244f7. Single-level previews in ZIP remainr31, as this fix is full-disk-only; no standalone progression promised.

verify_gameover_restart.mjs: actual number-key selection and Fire; run80 gameplay updates, force the native exhausted-credit branch92A4 with mapping9 (diagnostic bypass of death/continue animation), then run actual restart code and Fire. Oldr31 level2 negative control entersFE03 once. Newr32 all8 selected-level cases return through resident level1 reset and restart selected level with zero tape-loader entries, ECM mode2. Reports gameover_validation.json. New isolated restart_fixture.mjs and verify_restart_ending.mjs preserve older fixtures/reports. Native transitions through8 stages, ending and level1 restart pass again over21281refreshes, using diagnostic victory countdowns/death bypass. This is targeted control-flow validation, not eight natural deaths or hardware confirmation. Parsed final ZIP: all64 payload pages equal new image and all TAP block XORs validate. manifest records status/checks. No new diagnostic image needed.

Full disk r32 supersedesr31 for runtime restart; no firmware changes. The intermittent startupE0, current-directory loading, demand loading/title prefetch,64KB normal-black ROM and remaining arcade art upgrades remain outstanding. Physical confirmation pending.

## 073 — Reported level3 repeated-play corruption: investigation open (2026-11-02)

User reports screen corruption, a momentary freeze and glitches killing the player after a couple of level3 plays. Asked asynchronously whether full disk r32 on hardware and whether lives/continues versus new games; answer pending. Do not assume exact release/platform or mark fixed without reproduction. Used latest full disk r32 as baseline.

Added scripts/stress_level3.mjs: native keyboard number3 before Fire, no death bypass, periodic fire/directional movement and real collisions. Ran60000refreshes,5537 gameplay update entries,120 native ship-start entries8721,119 death-handler entries91F2, zero obsolete tape-loader entries. These are ship starts/respawns, not120 independent new games. Logged region switches,mode,PC/SP,min native stack and sampled music pointer each1000frames. No persistent stall in sampled progression or ROM-write exception; this does not exclude brief corruption between samples. CPU stack minimum65462, well above music workspace. Sampled gameplay music pointers stay in the allocated range; pre-song raw bytes at startup are not treated as active pointers. Report and HOME/DOCK dumps under build/diagnostics/level3_crash/stress.json, frame0/10000/20000/30000/40000/50000.*. frame20000.png rendered and visually inspected: clean native scene in that snapshot.

Added scripts/stress_level3_late.mjs:25000refreshes, temporary diagnostic death bypass through frame11999 to reach later waves; restore original death handler at12000, continue real collisions afterward.2255 gameplay updates,27 ship starts,898 death-handler entries (many are suppressed collision requests, not actual deaths),zero tape entries. Reached large giant-ship scene at frame10000; frame10000.png rendered and visually inspected. Snapshot has expected large arcade-derived ship/scenery, not a demonstrated crash. Native mode65/region0 at frame24000 is an in-progress bank transition, not by itself corruption. No new game patch or candidate published from this investigation. These scripted inputs do not reproduce the user's exact hardware/input history.

Both diagnostics retain runtime code/palettes unchanged except explicitly documented late-wave temporary death bypass. Earlier full-game tests mostly bypassed death or forced game-over branches; natural repeated lives are now covered for this deterministic path, but user-reported intermittent failure remains open. Need exact build/platform and trigger sequence before attributing it to memory, graphics, audio or display timing. No claim that hardware failure is disproved by emulator success.


## 074 — Implemented per-level disk loading, r33 (2026-11-02)

User explicitly requests implementation. Reviewed current state/history and local hardware-development skill. Added src/demand_loader_head.asm, scripts/build_demand_disk.py and validate_demand_disk.py; generated demand gateway/entry, runtime loader and launcher sources/binaries under build/fullgame/per_level_r33. Base gameplay is r32, including normal black and corrected restart callers. First load reads only RTBOOT.TAP, eight pages, not all512KB. LEVEL01..08 contain initialized64KB runtime regions loaded on selection/progression. Launcher and companion files may be in any current subdirectory: no cd / or fixed RTYPE command. LOADING LEVEL n / filename / PAGE00..07 shown; error includes operation step. Packaged RType_TS2068_per_level_r33.zip SHA256 5be5147a52bb2a20908e677f9994d82a0a26ec2266c145938e33b8d52d23e5f6.

Memory: active level physical region0, resident/backup region7. Loader2385bytes at HOME6000; entry gateway331bytes temporarily at A000 with original331 bytes saved in8100 scratch, restored before resident disk work. Save old native DOCK3 workspace through a bounce to reserved region7; preserve HOME8000..BFFF before usingA000/8000 for transfers. Copy helpers5E00/7800 handle mapped-bank conflicts; an8-byte F900 helper is preserved inD3E0 for bounce copies that overwrite5E00. Restore both common chunks, audio helper, stack, score/continuation metadata before native init. Every page gets TAP XOR, immediate RAM readback sums and final eight-page sweep. Do not execute partially loaded data. The existing level-one cold-boot image and warm initialized metadata are separate representations (RTBOOT versusLEVEL01).

Validation: demand_disk_fixture.mjs executes actual loader/gateway with legacy packet/file model, nested /sd/TAP/GAMES/SHOOTERS/RTYPE, delayed acknowledgements/replies, plain/verbose statuses and eight-cycle selector priming. verify_demand_disk.mjs: boot at frame1283 with only RTBOOT mounted/16 blocks; all eight stages, ending and level1 restart pass at frame33414. Mount order RTBOOT,LEVEL02..08,LEVEL01;144 total blocks read. Uses diagnostic victories/death bypass, not normal playthrough. Common-code/audio-helper/stack/native-metadata assertions execute on handoffs. verify_demand_selection.mjs: selected1/3/8 and native exhausted-credit branch/restart pass, zero FE03 entries; selected3/8 each load RTBOOT, selected level,LEVEL01, selected level. Three common/native-metadata checks per selected3/8. verify_demand_failures.mjs: corrupt payload ->E2/page1/step3; aliased RAM ->E2/page1/step6; missing header ACK ->E0/page2/step2; absentLEVEL02 ->03/page0/step1. Safe diagnostic halt, no partial-level launch. validate_demand_disk.py verifies all72 asset pages and CODE block XORs from final ZIP against manifest region hashes. Report files progress/selection_restart/failure_validation.json and manifest.json.

Visual diagnostics: loading_level3.home.bin/png and missing_file.home.bin/png rendered in correct standard video mode, visually checked: normal black, white level/file/error/step text. Initial source-capture comparison ran after native boot changed cache chunks, so it failed although bytes at cold launch were correct; moved byte comparison to prelaunch snapshot. Initial handoff failed because native metadata was not preserved and a bounce copy overwrote its own5E00 gateway; captured failed.home.bin/failed.store.bin and instruction traces, added distinct metadata backup and preserved F900 helper, then retested. A shell-quoted debug edit failed to parse; corrected with literal helper script. Earlier full-game test exited during the ending's next-file mount because level character changes before gameplay resumes, leaving one queued reply; moved counter reset immediately after observing a mount, so the final pass waits for actual resumed level1 updates and an empty FIFO. Reset PAGE_NO at every entry so missing-file diagnostics cannot show stale game data.

Limits: foreground demand loading only; idle-title prefetch/cache still outstanding. Each level is64KB, not a minimal/compressed asset subset. Regions1..6 remain unused by this implementation. Requires full512KB hardware addressing for reserved region7; no64KB cartridge update. Current-directory support requires navigating into the game directory before loading the launcher. Physical timing/loading confirmation pending; do not claim prior E0 or level3 hardware corruption fixed. User has since confirmed level3 issue was on real hardware after life-loss/continue; exact artifact remains unconfirmed. No speculative gameplay crash patch included. All earlier versioned packages preserved.


## 075 — Eight resident level banks, r34 (2026-11-02)

User requires each loaded level to remain in a separate RAM bank and revisits to avoid disk. Replaced r33 single active region plus dedicated spare with eight physical64KB level regions0..7. Cached code/art/music/dictionary chunks0/1/4/5/6/7 are retained; inactive mutable chunks2/3 hold resident loader, native metadata and common-code backups. Destination is excluded from scratch holder/backup choices. Rebuild rendering buffers and compiled ship code on activation so stale scratch is not reused. Cache flags mark successful verified loads only and remain through replays; cold launch initializes a new session. Cache hit holding the resident program relocates it through RAM; other hits use the native short bank handoff without file access. No level eviction, all512KB addressing used. Handoff helper restores original native code before using8100 staging, preserves IRQ/stack/music state, then invokes native game init.

Added src/cache_loader_head.asm, cache_gateway_head.asm, cache_transition_tail.asm; scripts/build_cached_disk.py, cached_disk_fixture.mjs, verify_cache_progression.mjs, verify_cache_restart.mjs, verify_cache_failures.mjs and validate_cached_disk.py. Persistent fields FD48..FD4A, initialized in BOOT source DD48 too. Readiness tag0D70, common polling helper0D80 and blank-transition helper0DA0 in compile-time palette space after executed orb code; cached-fast setup at0D40. Native fast tail194bytes in unused compiled paddingFBE0; actual ship code169bytes, so no live instructions displaced. Gateway390bytes and resident2615bytes. Short cache switches remove the fixed post-reply guard only by polling the target tag after priming, with bounded timeout before any target writes. This accounts for firmware MEMDOCK posting BANK changes after sending its reply. Slow resident-relocation branch keeps conservative guards; no claim every switch is literally instantaneous on hardware.

Final model validation: first circuit mounts RTBOOT,LEVEL02..08 once; second circuit revisits1..8 with no additional disk mounts or block reads.128 total header/data blocks, eight valid bitsFF, ending/restart included,41810refreshes. Delayed replies plus500000T delayed selectors; max101712 selector/low-code reads demonstrates readiness polling rather than assuming readiness after eight reads. Fifteen native-core/workspace checks pass. Selected3 and8 native game-over/restart tests mount only RTBOOT plus their selected file; three code/workspace checks each, zero tape entries. Four error controls (CRC E2, alias E2, timeout E0, missing file03) pass. Final ZIP reconstructs all72 distributed pages with correct TAP XORs and exact region hashes. Package build/fullgame/cached_levels_r34/RType_TS2068_cached_levels_r34.zip SHA256 1b6e92c0a5b553ca38f4f9dde436540e87e347318053eda97fcdc603b211c6af. Manifest and reports in same directory. Original r33 files unchanged.

Exploration failures caught before release: initial cache fieldsFD20..22 collided with executable IRQ entry; moved to genuinely freeFD48..4A and stamped cold-boot copy source. Initial backup reused a same-address4000 bounce while mapping destination chunk2, leaving the old resident program instead of common code; changed to direct HOME8000/A000 ->inactive4000/6000 copies and added byte-exact native-core assertions. PowerShell CRLF replacement initially did not apply; used literal Python source edits. No failed candidate published. Core checks and second complete cache circuit pass after corrections. Documentation docs/resident_cache_r34.md. Idle-title prefetch and physical confirmation remain pending; no64KB ROM update.

## 076 — L2 emergence investigation, still open (2026-11-02)

User describes reasonably large creature emerging/crawling out before the final boss, then moving up/down, sometimes spawning high. PicoVideo confirmed; original TS2068 video was inferred by user, not independently observed. Asked for the rendering output to distinguish native RAM from separate display capture. Do not assume a video-board defect or dismiss the reported corruption.

Added scripts/probe_l2_emergence.mjs on r33 baseline: actual selected level2 with diagnostic invulnerability,10000refreshes. Logged native wrapper source pointers/size/flip/coordinates. The first captured5x5 ground/high spawn uses native descriptor32/CBC7 and33/CC80 at y18 and signed y-3, with subsequent3x3 and other object sources. JSON id-111 is object-slot identity, NOT the graphic descriptor ID; pointer maps identify the actual frame. No shared source-cell overlap in converted boss descriptors3..6. Native ground families32..38 and41..44 were not individually arcade-converted; source artwork remains native. Catalogued those frames in build/diagnostics/l2_emergence/native_frame_catalogue.png.

Direct exact-clipping test verify_l2_emergence_clip.mjs checks those11 descriptors, four flips, three X positions and seven signed Y positions(-3,-2,-1,0,16,18,19):924 cases, zero bitmap/attribute mismatches. Added verify_l2_emergence_background.mjs using the observed prelaunch background mode8EBF=60 and collision return opcode8F10=D0, instead of the direct-mode40/D8 test:924 more cases, zero mismatches. This covers primitive drawing but does NOT prove real mixed terrain composition or PicoVideo capture. The source creature is not yet definitively matched to the user's corrupt pose.

Diagnostics: draw_sources.json, clipping_failures.json and background_clipping_failures.json (both empty), native_frame_catalogue.png and HOME captures under build/diagnostics/l2_emergence. id19_f4251_pcbc7.home.png and id19_f4264_pcc80.home.png rendered/inspected: partial ground-level poses within scenery, not a reproduced screen corruption. Catalogue rendered/inspected; local arcade frames12600/14400 and descriptor003 source visually inspected for comparison. Source descriptors32/33 have no overlapping storage; sprites3..6 also have none, ruling out the suspected overlapping-write explanation for those tested sets. One shell-quoted background-test generation command failed to parse; corrected using a literal helper script. No speculative emergence patch or new creature artwork applied. Need the actual corrupt pose/sequence to match these captures; keep issue open. Reviewed graphics skill's older-V4 versus4.2 F4 capture discussion and local4.2 bank filters; this is a diagnostic possibility, not established cause. r34 cache package does not claim to fix this or the level3 hardware respawn corruption.


## 077 � Matched and fixed L2 emergence corruption, r35 (2026-11-02)

User hardware photo 1-12823.jpg (attachment e79b737f-54ab-49d4-a5d9-fdc99169320b) shows the five-by-five native descriptor32 mirrored spawn, not the final boss. Compared with the actual r33 HOME capture: all256 bytes at HOME5D00 differed from the expected bit-reversal table; bytes contain high-score names/text. Native horizontal mirror routine8D65 loads B=5D and looks up every pixel byte there. Unmirrored/flying frames do not use that table, explaining temporary recovery after launch. Earlier1848 clipping tests injected a valid table and therefore masked this integration bug; those primitive passes were insufficient evidence about initialization.

Added scripts/build_spawn_fix.py and validate_spawn_fix.py, based on preserved r34 resident-cache build. New helper at ROM0DC0 calls displaced native86C3, saves AF/BC/DE/HL, regenerates all256 HOME5D00 reversal entries, restores registers and returns. Patch CALL at1485 to0DC0 in BOOT and all8 level regions, so native gameplay initialization repairs it after menus, loads and restarts. Helper ends before0E00 and does not enlarge gateway/tail or change cache layout. No speculative artwork patch or firmware change. r34 stays unchanged.

Negative control scripts/compare_l2_spawn_table.mjs uses the actual r33 captured bad table to draw sourceCBC7 with8D65 at an unclipped position. It reproduces the distinctive vertical-bar/scrambled block in the photo exactly; valid table restores intact head/body silhouette. Images build/diagnostics/l2_spawn_r35/old_pose.home.png, fixed_pose.home.png and table_comparison.png rendered and visually inspected. probe_l2_spawn_r35.mjs uses normal boot/selectedL2 gameplay without table injection,10000refreshes with diagnostic invulnerability, and captures actual native poses plus source pointers. Source family32/33 confirmed; timing shifted relative to r33 because of cached loader. Rendered captured frames for inspection. Earlier diagnostic files retained.

Final r35 gates: complete first8-stage traversal, ending/restart and second8-stage traversal without new disk reads;41853refreshes,128total tape blocks,15native core/workspace guards and3405 live reverse-table assertions. Selected3 and8 game-over/restart tests each pass160 additional live table assertions and3code/workspace checks, zero tape entries, no re-read. Four failure controls pass (checksumE2, aliasE2, timeoutE0, missing03). All72 packaged pages/TAP XORs/hashes pass. ZIP build/fullgame/spawn_fix_r35/RType_TS2068_spawn_fix_r35.zip SHA256 cef507e26ba61c833b604c1b363b267842dd0f8b487401656a99ba4231b558f8. Reproduce python scripts/validate_spawn_fix.py. Separate fixture spawn_disk_fixture.mjs asserts all256 table entries at every active8B06 update, not just after boot. Physical confirmation of correction pending. Separate level3 hardware freeze remains open; do not infer this resolves that crash. Older standalone previews and64KB ROM are not updated by this disk release.


## 078 - Hardware stuck-down report, r34 confirmed (2026-11-02)

User reports ship immediately moves down uncontrollably after a few games; clarifies artifact was r34, not r35. Controller/socket detail was not unambiguously supplied. Reviewed native_input.asm keyboard/native dual-stick merge, native keyboard mode dispatch74FB/74FC, AY register selection and audio writers. No proven new defect or patch. R34 stale HOME5D00 can also affect the original Sinclair decoder8B2D, but default redefine decoder8B14 does not use it; do not claim r35 fixes this reported motion without matching input mode/hardware evidence.

Added probe_repeated_input_r34.mjs and r35 equivalent, each40000refreshes of actual neutral keyboard/two neutral sticks with Fire pulses and natural collisions. At every1A6D input return, assert lowfour directional bits zero. R34 passes6997 input returns,35ship starts and1exhausted-credit restart; r35 passes6879returns,33starts and1exhausted-credit restart. Keyboard mode2/decoder8B14 and six bindings remain stable. Reports diagnostics/repeated_input_r34/result.json and r35 equivalent. These are fixed-length runs, not35/33complete games. No diagnostic images generated because no failure. Initial artificial repeated PC92A4 experiment hit fixture bookkeeping failure after five forced restarts onr34, and stalled after11onr35; stopped, replaced with natural collision paths. Neither is valid evidence of a hardware/game defect. Do not publish an input patch based on them.

R35 package unchanged. Ask user to test latest fullfolder replacement; stuck-down hardware issue remains open. Separate L3 hardware corruption also open.


## 079 - Hidden level/title transitions, r36 (2026-11-02)

User reports flashes after selected-level start before loading and after switches before title animation. Exact latest artifact not separately confirmed. Found concrete r34/r35 defect: gateway blanks HOME6000..7AFF and selects secondary standard displayFF41, but resident copy helper is installed at HOME7800, the first secondary attribute cell. Nonzero helper bytes reveal loader instructions in bitmap6000. Negative control verify_transition_negative.mjs with instrumented old_transition_fixture.mjs reproduces the first visible write7800 at PC6245. Saved post-write old_secondary.home.bin/png under diagnostics/transition_r36, rendered and visually checked: magenta/red scratch block at top left. This establishes a software source of the flash without relying on video-board assumptions.

scripts/build_transition_fix.py builds a separate r36 package from r35 logic. Relocates the resident loader copy helper/call sites to HOME7B00 (outside secondary bitmap/attributes), keeps7800..7AFF black during scratch work, hides restored metadata before cache_loaded copies, prepares primary loading bitmap/attributes before selecting primary mode0, and prepares title under blank secondary mode41 instead of exposing primary during clearing. New title initializer clears secondary attrs with temporary DE saved/restored; original fill routine ultimately returns DE7800. Cold BOOT display sourceE000..FAFF (HOME4000..5AFF) is zeroed, preserving compiled cacheFB00 and all executable/game data, so bootstrap copy doesn't expose stale screen bytes. All eight region title initializers patched; level cache layout, gateway390bytes and creature-table helper0DC0 unchanged. Resident2631bytes. Earlier packages untouched.

transition_disk_fixture.mjs asserts every switch into secondary mode1 has all768HOME attributes zero, and rejects any nonzero HOME7800..7AFF write while that screen is visible, excluding mapped DOCK writes. Final progression41898refreshes passes full8stages, ending/restart and second8-level circuit without new disk reads;128 tape blocks,15core/workspace guards,3404live reverse-table checks, delayed500000T selectors/max101712reads. Selected3/8 restarts pass160table checks and3workspace guards each, zero tape entries/re-reads. Four error controls pass.72 packaged pages/checksums/region hashes pass. Targeted verify_transition_init.mjs checks original DE7800 fill endpoint, F4=9, FF41, cleared primary bitmap and zero secondary attrs. capture_transition_r36.mjs final-byte normal selection run records3black secondary handoffs; new_secondary.home.png rendered and visually checked completely black. render_transition_r36.py reproduces standard-secondary diagnostic rendering. No hardware fix claimed until retest.

Exploration: first candidate completed all levels but stalled after ending/58second-circuit updates, at sampledIRQvector8383, active3 and intact guards; debug_transition_progression.mjs captured stalled HOME/DOCK1/2/3 in package build dir. Added PUSH/POP DE around newly inserted title scratch clear; final candidate completes bothcircuits/restarts. This does NOT prove DE was the stall's root cause: an initially added DE-preservation test incorrectly expected CAFE, but nativeFDF0 returns end address7800; corrected test to actual original contract. Keep failed-candidate evidence for future timing-sensitive/hardware investigations. No failed candidate published. Separate hardware stuck-down andlevel3freeze remain open; no claim r36 fixes them.

Final ZIP build/fullgame/transition_fix_r36/RType_TS2068_transition_fix_r36.zip SHA2561738946ed15322224b12c91b3cadeb031b31837523507cca34b7fdfcc9bc888e. Reproduce python scripts/validate_transition_fix.py (includes negativecontrol and init check). Replace completeRTYPE folder. Hardware confirmation pending; standalone previews/64KB ROM unchanged.


## 080 - L3 dotted rows/magenta corruption hardware photos, still open (2026-11-02)

User supplied 12824/12825 photos, attachment01e06027-1d6d-490f-8c76-973c9a9bdd4c. Repeated dotted rows cross sky at8-pixel intervals and a tall magenta block appears at left, near initial entrance of converted giant ship. User believes r35, music continues, movement not currently possible; version not certain. Treat as potential main-loop stall while interrupt audio continues, not proof of video-only capture fault. No new gameplay fix claimed. R36 prior transition fixes do not claim to resolve this.

Added probe_l3_photo.mjs normal selected3 via r36 fixture, diagnostic invulnerability,17000refreshes.26HOME+DOCK1/2/3 samples every500from4000..16500, matched the initial giant ship entrance around5500..6500 and later complete ship. render_l3_photo.py produces individual PNGs and contact.png; contact sheet and earlier r32 late-waveframe10000.png visually inspected. No photographed dotted rows or left magenta block reproduced. All native updates continued through1128 at16500. Audit source cell starts found zero sharing between converted and unconverted L3descriptors; this does not rule out all byte-level/script interactions.

verify_l3_photo_clip.mjs and background counterpart independently decode actual dictionary/pixels for nonzero descriptors40..106 across4flips,5X positions(0,1,15,30,31) and5signedY(-12,-1,0,8,19). Both pass with zero bitmap/8x1 attribute mismatches, including13-cell-high giant columns. Outputs clipping_failures.json and background_clipping_failures.json under diagnostics/l3_photo. First generated tests accidentally retained L2layout index despite L3payload, producing CPU loop errors; corrected .levels[2] before valid tests. These primitive tests explicitly initialize reversal table and do NOT by themselves prove complete runtime state.

verify_l3_background_scan.mjs compares optimized background-row/clean-run scanners against the original native instructions, retaining ECM restoration hooks, on all26 actual captured scenes. Exact bitmap, ECM attrs, DOCK1/2/3 equality in every case. background_scan_comparison.json records results. This rules out a difference for those scenes only.

probe_l3_replay_r35.mjs runs45000refreshes using original r35 disk fixture, keyboard Fire/directions with neutral native sticks. First12000 diagnostic invulnerability reaches giant ship, then restores native death opcode and permits natural collisions/respawns. Reports updates/starts/death entries, captures every5000, and first700-refresh gap snapshot. A gap near23933 recovered by25000 and later updates continued; not a persistent stall, can be continue/menu waits. Results diagnostics/l3_replay_r35/result.json, possible_stall HOME/DOCK files and HOME captures. This is not proof of successful physical gameplay and no replacement release is warranted from passing probes alone. Earlier source review covered compiled cache candidate full high-byte gate, IRQ banking/audio mappings, source overlap and clipping. Hardware stuck-down and L3corruption remain open.


## 081 - Interrupt-driven hardware debug chord, r37 (2026-11-02)

User requested a key to print diagnostic information when L3corrupts. Implemented Caps Shift+D as an IRQ-polled diagnostic takeover, so ordinary main-loop input polling need not work. New src/debug_irq_screen.asm, scripts/build_debug_key.py, debug_disk_fixture.mjs, verify_debug_key/live/progression/restart/failures.mjs, validate_debug_key.py and render_debug_key.py. Marker0D7F protects BOOT bootstrap: active on regular levels2-8, ignored on cached BOOT level1. No disk writes/commands or MEMDOCK transaction at capture. Diagnostic1112bytes in otherwise bootstrap-only DOCK4 8000..8457, below per-level music allocations84B4. Permanent ROM0 poll at0DE0..0DFF; owned IRQ entryFD20 gains CALL beforeBE26. Cold high-RAM sourceDD20 patched too. Uses current region, F4=19 then11, so stack remains HOME7 throughout. No resume attempt; game/audio intentionally freeze and require reset. Normal D, Caps, and no-key continue native IRQ.

Exact capture layout: IRQ pushes original AF/BC/DE, CALL return then diagnostic HL/IX/IY. HOME7C00..7C1F holds stack copy; saved original PC at7C0E and original SP at7C20. Snapshot native vars7C40..5F via temporary DOCK3 mapping, raw sticks7C60/61. PC/SP, six registers, F4, level/input/world/object, cache, player/game, music pointers, keyboard decoder, render control, sound/timer and four return-stack words displayed as28fields in2columns. Raw adjacent bytes may be unused; labels/interpretation in docs/debug_key_r37.md. Text is standard normal-black background with white ink; no dependency on the native game's font or drawing routines.

verify_debug_key synthetic IRQ test passes exact PC8D21, SPFFF2, AF1122/BC3344/DE5566/HL7788/IX99AA/IYBBCC, map9 and live native control word. Negative chord tests return atBE26 with correct stack/map/HL. First test incorrectly assigned emulator ix/iy properties (actual xh/xl/yh/yl); fixed test setup, not runtime. First live test allowed3frames and failed halted assertion while drawing was incomplete; allowed20, then passed. Real frame-IRQ test selects3, deliberately runs JP8400 with SPFFF0, keeps interrupts active, and confirms chord captures PC8400/SPFFF0 and reaches permanent halt. captured.home.bin/png and live_stall.home.bin/png rendered and visually inspected; all fields fit and readable.

Full final-byte normal progression:41850refreshes, all8 levels, ending and second8-level circuit without disk rereads;128 blocks,15core/workspace guards,3404reverse-table checks. Selected3 and8 game-over/restart pass160checks and3guards each, no tape entries or reread. Four failure controls pass.72packaged pages/checksums/hashes pass. Full reproduction validate_debug_key.py now includes synthetic/live checks. Earlier run interrupted before finalization to improve field layout; final checks all rerun. Physical testing pending; no L3crash/stuck-down fix claimed.

While allocating diagnostic source, found r36 BOOT zeroingE000..FB00 had overwritten ROM7 enemy dictionaryE000..E3FF and title delta atlasE400..F8FF, not merely disposable display memory. R37 removes that source zeroing entirely. Verified BOOT E000..F900 exactly equals r35. Other r36 hidden-screen helper/title/loader fixes retained. This source correction is separate from L3fault and does not prove it resolved. No original asset source files altered.

Final package build/fullgame/debug_key_r37/RType_TS2068_debug_key_r37.zip SHA2568465088b9ad18dc8bff3cb6c21aea602ec570fc50dca70a17d6f1ee7f7a29ddc. Replace whole RTYPE folder; select3; when fault occurs hold Caps Shift+D, photograph complete screen, reset afterward. Full diagnostic docs/debug_key_r37.md. Earlier releases preserved;64KB ROM/previews unchanged.


## 082 - R37 hardware capture interpreted; RAM replay diagnostic r38 (2026-11-02)

User photos12827/12828 in attachment326c7adb-87b8-49b6-b700-72ee05fa08a1 capture dots and R37 state. User explicitly says game was NOT frozen, correcting earlier inference. Output confirmed PicoVideo only, "latest firmware available" (no independently verified version number). No native-video observation. Enlarged PC crop saved Elite/debug_pc_crop.png: reads18DE. Initially misread160E then180E in commentary; corrected after enlargement. Correct instruction18DE is OR A in full_enemy_source, following PUSH HL/PUSH DE/LD DE,C4CE. RegistersDE=C4CE, HL=C993 and stack7A19/C993/18F4/0C54 are consistent with that call, not evidence of a stuck terrain loop. INPUT0200/JOYSFFFF neutral, MAP9/CACHE0200/VALIDlow05 consistent with currentL3/holder0 and levels1/3 loaded. Full transcription saved diagnostics/debug_ram_r38/hardware_r37_transcription.json. Corruption remains unresolved.

Found a diagnostic-only defect: R37 ATTR/DRAW words sampled8EB0/8EBE while DOCK4 debug code hid HOME8000..9FFF. Those two photo fields84C6/84FD are music/debug-bank bytes, NOT corrupt game selfmod code. R38 uses12-byte HOMEF910 helper to map9, read native word, restore19 before returning to DOCK4. Old F908/F922 obsolete callbacks remainRET; F910..F91B was FF padding, patched at cold sourceD910 too. Other captured fields were in unaffected chunks. Added assertions comparing captured7C4C/7C4E to actual HOME8EB0/8EBE; now003E and60C6 on the sampled scene.

src/debug_ram_screen.asm captures both6144-byte physical HOME display planes before clearing: bitmap4000->A000 and attributes6000->C000, F4=11. After photographing state, Space redraws both planes exactly and selectsFF42 (ECM with IRQ inhibited), then halts. No resumed gameplay/audio/region commands. Terminal scratch overwrites native code only after all fields are captured; no resume promised. Diagnostic1162bytes at8000, still below84B4. scripts/build_debug_ram.py, debug_ram_fixture.mjs, verify_ram_* and validate_debug_ram.py preserve r37 sources/releases. Render_debug_ram.py renders state and restored ECM image.

Final validation: exact synthetic registers/PC/SP, negative chord keys, correct native renderer words; actual frame-IRQ stuck-loop capture and byte-exact Space restoration of bitmap+ECM pass. Complete8-stage progression, ending/restart and second8-stage cached circuit41850refreshes/128blocks,15native guards/3404table checks; selected3/8 restarts160checks+3guards each, zero tape entries or re-read. Four disk failure controls and72packaged pages/checksums/hashes pass. captured/live_stall/ram_view PNGs rendered and visually inspected. Earlier r38 validation stopped before finalization to correct renderer-word sampling; all final checks rerun. User instructed to compare original glitch photo, state photo, and Space RAM redraw. No firmware diagnosis or gameplay fix claimed.

Package build/fullgame/debug_ram_r38/RType_TS2068_debug_ram_r38.zip SHA25601621b0c3dfcd1d912557d7da344642a54ad846fbf4fc485202ab28fc0991f02. Replace completeRTYPEfolder. Docs/debug_ram_r38.md. Hardware comparison pending.


## 083 - R38 artifacts survive RAM replay; completed-frame r39 (2026-11-03)

User photos12829/12830 under0ab966dc-7485-4377-8249-3f92a5c67fb4. User explicitly confirms second is Space RAM redraw. It shows thin blue top rows and dotted lower rows persisted in captured planes; cannot dismiss as merely live bank-capture contamination. PC8D43 is original normal-direction sprite LD(DE),A, sourceHL D6A7, destinationDE7539 in retained bitmap, INPUT0200 andJOYSFFFF neutral. ATTR003E/DRAW60C6 now agree with valid native source. No invalid-control/bank state established and no freeze reported. Transcription diagnostics/debug_frame_r39/hardware_r38_transcription.json. The snapshot is mid-draw, so still distinguish persistent damage from incomplete compositor publication. Reviewed terrain repaint/restore/scan and native renderer around capture; no speculative graphics patch applied.

Added src/debug_frame_screen.asm, scripts/build_debug_frame.py, debug_frame_fixture.mjs, verify_frame_capture/progression/restart/failures.mjs, validate_debug_frame.py, render_debug_frame.py. R39 IRQ poll latches F91C; native868C now CALLFCC8, a verified FF padding block throughFD20. Main hook returns displaced LD A,(7A8A) semantics when not armed. When armed, constructs the exact IRQ-style saved register frame and invokes diagnostic after the whole current update. PC868F is expected capture checkpoint. Hook copied from BOOT sourceDCC8 and468C; common main code persists across regions. Request flag initialized0 at sourceD91C. Does not change normal draw algorithms or graphics. Debug RAM replay unchanged. Unlike r38, cannot report a permanently stuck main loop; r38 preserved for that purpose. Levels2-8 supported.

verify_frame_capture observes actual helper entry then independently compares saved AF/BC/DE/HL/IX/IY/SP to pre-hook CPU registers and expectedPC868F; passes. Space restores both6144-byte planes exactly. captured.png/ram_view.png rendered; restored scene visually inspected, no sampled corruption reproduced. Full final package progression42104refreshes, all8stages/ending/second cached circuit without disk re-read;128blocks,15core/workspace guards,3406reverse-table checks. Selected3/8 restart tests160checks+3guards each and zero tape entries/re-reads. Four disk failure controls and72packaged page/header/XOR/hash checks pass. No hardware cause or corruption fix claimed.

Package build/fullgame/debug_frame_r39/RType_TS2068_debug_frame_r39.zip SHA25622e3cc89197a8076632ffd1f9d7bdf0e3165787d66260d42e1496cb1b6dfb030. Docs/debug_frame_r39.md. User instructed to request completed-frame capture, photo state and Space view, then reset. Hardware comparison pending.


## 084 - Retained-bitmap initialization correction candidate r40 (2026-11-03)

User rejects redundant completed-frame distinction: lines visibly remain after drawing, and redraw looked the same as gameplay. Treat that evidence as established; no further capture requested for this distinction. User says "So fix it." Reviewed retained compositor/init/native workspace. Found old init86C3 resets front bitmap, owner/dirty arrays, but conversion1485 initializes retained attributes without clearing retained pixels. Existing real L3capture DOCK3 begins ASCII loading-header bytes "R TYPE LEVEL1" and stale content in playfield. New correction explicitly initializes retained pixel area before native world draw. This is a concrete omission fixed; causal linkage to every photographed artifact remains hardware-unconfirmed, not asserted as proved.

scripts/build_retained_fix.py based onr38 (notr39 capture boundary) calls new HOMEFCC8 retained_clear after native86C3 via init wrapper0DC0, within0DE0 boundary. Helper saves AF/BC/DE/HL, clears5120bitmap bytes:6000..6FFF plus7000..707F through7700..777F. It preserves interleaved native data70xx..77xx low80..FF and7800..7FFF exactly. Whole-bank clearing would erase native state and is not used. Verified FCC8..FD20 wasFF in cold sourceDCC8. No per-frame scanning cost or star/actor heuristic added. R38 diagnostics and cache remain, source palette/title correction preserved.

verify_retained_init.mjs independently injects deterministic nonzero playfield pixels before init across8levels. Oldr38 leaves5102nonzero bytes; newinit clearsall0. Focused helper contract checks every8192DOCK3byte against expected pixel/workspace partition, unchanged front bitmap/ECM plane, AF/BC/DE/HL and F4. All8 pass. Full progression42130refreshes/128blocks,8levels/ending/secondcached circuit,15core guards/3406reverse checks pass. Selected3/8 restart and four error controls pass;72packaged page/header/XOR/hash checks pass. Reproduce validate_retained_fix.py.

Longer diagnostic: probe_retained_l3.mjs uses the prior artificial RET-at91F2 death bypass. It progresses through early giantship, then native execution goes off course around7500refreshes and update counts become invalid; late captures retained under diagnostics/retained_fix_r40. Do NOT claim that run is valid or a reproduced hardware fix. Existing invulnerability bypass can violate native collision bookkeeping; cause of this particular diagnostic divergence not established. No artificial death patch is in the release. probe_retained_natural.mjs removes the death bypass and uses actual keyboard input/collisions:30000refreshes,2435updates,52ship starts,51death entries, lastupdate29999; no persistent stall, a700-refresh gap recovered. Natural HOMEcaptures/result at diagnostics/retained_natural_r40. These checks do not prove a complete unassisted boss playthrough or physical correction.

Final package build/fullgame/retained_fix_r40/RType_TS2068_retained_fix_r40.zip SHA2560a95d313b82c386318c2b715b45109582dd754b16148972989a7f6eafb9c79a1. Docs/retained_fix_r40.md. Hardware symptom confirmation pending; no claim all outstanding crashes/stuck-down are fixed. Earlier releases preserved. User asked to play normally with correction, no additional diagnostic screen requested.


## 085 - Reproduced rocket ROM-write corruption; fix r41 (2026-11-03)

User12832/12833 photos under648b698e-5fa9-45eb-a5a4-fa860a9dc3f4: L3corruption recurs, coincides with beep slightly after rocket motor detaches. SnapshotPC88A4 is normal background bitmap copy, neutral0200/FFFF, DRAW60C6. Photo transcribed in diagnostics/rocket_fix_r41/hardware_latest.json. Audio/event timing led investigation to special rocket spawner, not another capture-boundary request.

Extended trace_l3_event.mjs/watch_l3_irq.mjs/watch_l3_renderer.mjs from the previously divergent r40long route. Found FD20 interrupt code overwritten by palette-like00/44/47 bytes. Watch firstoverwrite: PC1419 LDIR (bus reports141B) writingFD20 at7477. Its intended destination7800 had becomeFD00. Active DOCK0 comparison found renderer operand1415 modified, not an IRQ register-save issue. Earlier write watch catches native9C3E LD(BC),A atrefresh6757 withBC1415, A=B4, original1415=78. CPUstate/preceding call/return trace saved old_renderer_write.json, original bad HOME/DOCK0..3 under diagnostics/l3_event_trace. Later shots produceFD operand and catastrophic IRQ overwrite; lesser mutations cause graphics corruption while game/music continue. R40long-run divergence was NOT safely dismissible as diagnostic invulnerability; correction to earlier notes. An isolated native helper test reproduces the same bug without a death bypass.

Root: shared9C31 projectile record helper ends ADD A,20; LD(BC),A; RET. Ordinary9C2C callers setBC=7AF3/4/5 timer addresses. Special rocket9C40 path calls9C31 at9C88/9C90 with no timer pointer, soBC contains a coordinate below4000. On original Spectrum these are ignored ROM writes. Writable DOCK0 in expansion RAM accepted them, mutating renderer/palette code. Rocket path then queues sound at9C96, consistent with userbeep. A read-only DCK/physicalROM can hide this error; real writable banking must be tested.

scripts/build_rocket_fix.py bases onr40, patches cold common-code source5C3C (HOME9C3C) C62002 -> CDF8FC. New guardHOMEFCF8 in free padding, after44-byte retained clear endingFCF4 and before IRQFD20. Guard reproduces ADD, PUSHAF, comparesB40, restoresAF, skips storesbelow4000, retains legitimateRAM stores and originalRET. SourceDCF8 installed cold; common code preserved across cache changes. No music/SFX disabled. Earlier r40 initialization retained, but it did not address this rootcause.

verify_rocket_store.mjs reproduces old overwrite of1415, verifies all16384ROM destinations ignored, six RAM destinations retained, native four-byte rocket record preserved, and all256A values preserve exact original ADD result/flags. watch_rocket_l3.mjs traps any executable DOCK0write plus invalid control flow: exactformerly failing17000refresh route now passes,60bad stores blocked, complete DOCK0 byte-equal to original,1121updates by16500. Earlier same path mutatedcode6757 and crashed7478. Fixed captures rendered by render_rocket_l3.py; frame10000 and late ship scene visually inspected, no reproduced stripes. The route still uses diagnostic death bypass to reach late waves; isolated defect/regression do not depend on that bypass.

Full final validation42128refreshes all8levels/ending/secondcached traversal,128blocks,15nativecore guards,3406reverse-table checks; selected3/8 restarts160checks+3guards each, no tape entries/re-reads. Four failure controls and72packaged pages/TAP XOR/region hashes pass. Reproduce validate_rocket_fix.py including long route and focused tests. No additional broad test rerun after focused all-A flag assertions (test-only change); gameplay bytes unchanged.

ZIP build/fullgame/rocket_fix_r41/RType_TS2068_rocket_fix_r41.zip SHA256fbc28573b24214a9d1c0d8aa506a29dd580d615facceffca4d543c7729ccd33a. Replace entireRTYPE folder, normalplay. Hardwareconfirmation pending; code-level rootcause reproduced and fixed, not merely another diagnostic. No claim every unrelated hardware crash/input issue resolved. Docs/rocket_fix_r41.md.


## 086 - Follow-up write-assumption triage and regression lessons (2026-11-03)

User asks how rootcause was found and what further scans/lessons apply. Added audit_write_assumptions.py, write_audit_fixture.mjs, audit_writes_progression/restart.mjs and docs/write_assumption_audit.md. Initial partial static scan5483native instructions yields528write-like candidates. LD(BC),A only9C3Efixed andBF3Cstarattribute store; latter's destination is row metadata derived, remains a runtime-range audit target rather than a confirmedbug. Apparent direct LD(0000),HL atF8DD is obsolete originalbeeper/selfmod target setF8C4, not anotherconfirmed liveROMwrite.

All-level immutable DOCK0 audit compares8192bytes at each active input update. First test wrongly compared coldBOOT level1 marker withwarmLEVEL01; correctedbaseline toBOOT. Final42128refreshes first8stages/ending/restart/second8cached circuit pass3406executable-bank checks. Results write_audit_progression.json; normal forced-victory coverage stillnot fullweapon/AIcoverage. Tested fixture assertion integrated into rocket_fix_fixture.mjs and counts added to normalverify_rocket_progression/restart outputs forfuture gates. Production binary/ZIP unchanged. Existing longrocket first-writewatch remains complementary to boundary hashes.

Documented future bounded coverage: indirectstore/blockcopy destination/range traces, immutableIRQ/table/codemargins, explicitselfmod allowlists; allweapon states anddeath/restart/cachepaths across8levels; nativeindirect dispatch andROM/I/O contracts; bothreadonly andwritablecartridge models; preservefailedlongroute beforeassumingdiagnosticartifact; isolateunit setup versusrealbootinitialization. No second live defect confirmed in this follow-up. This is triage/runtime sample, not an exhaustive all-code safety claim. Hardwareconfirmation pending.

## 087 - Native-size Sierra Lite enemy alternatives (2026-11-04)

User requests substantial arcade enemy improvements, scale before conversion, high saturation/gamma, more animation and scroll-safe palette transitions without substantial slowdown. Added scripts/preview_enemy_sierra.py. Generated build/graphics/enemy_sierra_trials/index.html, eight per-level comparison sheets and 115 candidate bitmap/attribute pairs covering 23 representative existing arcade-derived descriptors. Columns source/current/A gamma1.8 saturation4.5/B gamma2.4 saturation4.5/C row-coherent B/D hue-preserving HSV saturation2 gamma1.8/E HSV saturation2 gamma2.4. These numerical settings are experimental, not verified equivalents of Retro Image Converter controls. Source resized first with Lanczos to actual current descriptor dimensions; native absent cells preserved; transparent pixels forced black; legal brightness/flash constraints asserted. Sierra Lite uses existing serpentine scalar coverage diffuser. Palette dictionary reduction is deliberately not applied yet; these are offline alternatives, not playable/released improvements, new enemy-family conversions or performance measurements. Visually inspected level01 and level05 sheets: Sierra restores some surface texture; high gamma can wash detail, hue-preserving treatment removes some spurious primary-colour blocks; global row coherence produces strong striping. Initial two reruns failed allocation under host memory pressure; OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1 completed all115. No existing release/reference project/source archives modified. Further work: user visual choice, ordinary enemy source matching, real arcade animation cels/walker frames, shared dictionary quantization, runtime clipping/scroll/throughput validation. Existing L8 contour plan is offline only; do not claim gap-aware recolouring already integrated across all terrain.

## 088 - User art selections and corrected component previews (2026-11-04)

Saved assets/enemy_art_selections.json exactly for reviewed descriptors: L1 8/9 D; L2 3/4 D; L3 40 D/60 A; L4 25/27 D; L8 42/43/44 A. Keep reviewed L5/L6/L7 current; provisionally read user L4#11 as L5#11 shown in gallery. Unlisted descriptors unchanged; sibling frame choices not inferred. No playable integration claimed yet. L1#16 source is entire horizontal tail assembly squeezed into24x24. L3#101 source contains several separate projectile objects squeezed into32x16. Added preview_enemy_geometry.py: connected-component isolation from existing original arcade RGBA, aspect-preserving scaling BEFORE Sierra Lite D conversion, four tail alternatives and five projectile alternatives including larger dimensions. Output build/graphics/enemy_geometry_trials/index.html, group0/group1.png and manifest. Visually inspected both sheets; isolated rockets are substantially more recognisable than formation compression. Larger sizes require clipping/collision/frame/runtime review. Component poses are not yet a temporally recovered animation sequence. Black transparency/legal attrs asserted by shared converter. Initial JSON write failed on NumPy int64 boxes, fixed explicit ints and reran successfully. Corrected fit helper to allow upscaling as well as shrinking. No original ZIP/reference project or release modified; current r41 remains latest playable.

## 089 - Double-B native boss preview r42 and modest size comparisons (2026-11-04)

User requests in-game boss shortcut, specifically two B presses, and clarifies sprite growth should be1.2/1.3/1.5 rather than doubling. Added src/boss_preview.asm and scripts/build_boss_preview.py, boss_preview_fixture.mjs, verify_boss_preview{,_progression,_restart,_failures}.mjs, render_boss_preview.py and finalize_boss_preview.py. Separate r42 derives from releasedr41 without modifying old releases. Main call865F routes to84-byte immutableDOCK0 helper1FA3..1FF6. B row7FFEbit4 uses edge-stateFD4B (outside cache metadataFD48..4A and musicstackFD50..); held first/second presses do not repeat. No IRQ work; normal released path107T added per gameplay update (static instruction count, not frame-rate benchmark). Per-regionD71..D74 stores native event pointer/checkpoint/priorcmd4setting. Full ECM init1485, native8721 and8BAE rebuild scene/spawn using native scripts; no production death bypass or boss-victory manipulation. Native checkpoint changes for current life; new-game8696 restores ordinary start. Entries L1=99,L2=63,L3=9,L4=74,L5=73,L6=8,L7=61,L8=32. L3giantship/L6movingmaze require early persistent setup; these restart at encounter entrance.

Important failed candidates retained in narrative: first checkpoint placed phase-zero event behind next tick, missing bosses despite ongoing updates. Fixed by beginning one world column before event, accounting forFEEB's8-column initial draw. Tests strengthened to require specific actual rendered boss IDs, not merely updates. L6late59candidate omitted persistent maze controller and advanced out of stage; moved to8 so original setup runs and descriptors18..33 appear. Final uses fullECM1485 initializer, not raw0DC0, to rebuild retained/front planes consistently. First end-state test wrongly read7A84 through transient end-frame mapping; fixed explicitDOCK3state access.700update tests initially had12000refresh cap, legitimately too short forL4; raised22000. One normal progression run aborted due host V8 zone OOM after second-circuitL1, not an emulated game fault; no pass claimed for that run. Final sequential run with128MB old-space cap passes.

Final exact-byte boss test: all8stages, each double-B exactlyonce, held first10updates and second10updates,700actual subsequent gameplay updates, expected boss IDs8/3/41/27/8/18/53/42 observed, same selectedlevel. Diagnostic death bypass used only in test to sustain viewing. Final normal progression41989refreshes all8stages/ending/secondcachedcircuit,128blocks,15core/workspaceguards,3407reverse and executable-bank checks; selected3/8restarts6671/6707refreshes160checks/3guards each, zero tapeentries. Four checksum/alias/timeout/missing-file controls pass.72packagedpages TAP XOR/region hashes pass. render_boss_preview contact.png and level1..8.png from actual emulation rendered and visually inspected. Stage5boss has moved offscreen in late700update picture but descriptor8 was observed earlier; do not imply each final still is a static boss viewer. This tests native scripts under diagnostic conditions, not normal unassisted boss completion or hardware.

Published build/fullgame/boss_preview_r42/RType_TS2068_boss_preview_r42.zip SHA25665b9ef8be91d0276dd00e5056fa11d2ebe4f9e054d9e4806551d216ef1e2c5f3. Replace completeRTYPEfolder. Uses same per-leveldisk/cache/rocketfix; graphics unchangedr41. User selectedSierraLite treatments not yet packed,64KBcart unchanged. Physical testing pending. docs/boss_preview_r42.md.

Added modest_scales.html/png/json to build/graphics/enemy_geometry_trials via preview_enemy_geometry.py. Corrected isolatedtail/projectile components compared1.0,1.2,1.3,1.5 with aspect fit BEFORE conversion and separate8pixelpadding. Tailfitboxes24/29/31/36 padded24/32/32/40 square; projectilefitboxes32x16/38x19/42x21/48x24 padded32x16/40x24/48x24/48x24. Visually inspected output; these are offline choices, not integrated collision changes or measured speedups. Clarified doubling was illustrative only. User scale preference applies to further enlargement work.

## 090 - Level-five material-colour alternatives (2026-11-04)

User requests more options after monochrome level5boss report. Added scripts/preview_level5_materials.py; generated build/graphics/level5_material_trials/index.html and four comparison sheets for descriptors8/9/10/11,72 individual bitmap/8x1attribute alternatives. Six options at1.0/1.3/1.5 content scales: source-hue saturation1.3 gamma1.0/1.35; authored green/red and turquoise/red material pairs at subdued/bright intensities, gamma1.15. Arcade RGBA resized with preserved aspect before conversion, padded to8pixels separately. Explicit red-node mask uses original RGB red dominance; body tints are authored arcade-inspired alternatives, not recovered original palette. Material pairs allow red/body interiors and black-paper transparent edges; SierraLite applied after pair selection; transparent pixels remain black and flashbit clear assertions pass. Visually inspected cel009 and cel008 sheets. Source-preserving automatic fits remain largely grey; material constraints restore colour but trade some local shading for consistent green/red or cyan/red. These are offline choices, not updated playable assets or dictionary-packed/runtime-validated larger sprites. No release/reference assets modified; r42 remains latest playable.

## 091 - Level5 rectangular overlap investigation (2026-11-04)

User confirms rectangles during actualr42level5boss animation, not browser. Reviewed native8D2D..8D4F whole-cell pixel copies and8EC2metadata owner gating; independent ECM palette publisher also operates whole8x1rows. Added verify_level5_overlap.mjs using actual level5game/runtime renderer and converted descriptors9/10 atoverlappingcellpositions. First hypothesis expected earlier pixels erased; negative test shows0erased. Corrected experiment renders second alone andcompares actualoverlap:37foregroundpixels missing because native cellpriority rejects cells already owned by firstcomponent. This reproduces concrete block-level occlusion but NOT the exact reported animated frame; do not claim fullrootcause/fix yet. Syntheticcall fixtures initialize reversal table explicitly; integration coverage limits apply. result.json and first/second_alone/overlap.home.bin under build/diagnostics/level5_overlap.

Added preview_level5_composition.py: native_overlap.png actualZ80 proof, plus group_composition.gif offline mask/group/thenECM-pairfit experiment. Alpha silhouettes from arcade source resized tonative24x24, pixel composition beforefinallegal8x1SierraLite quantization avoids independently assigning samecellmultiplepalettes. GIF positions newlyauthored for controlled overlap, not recoveredgameanimation. AllgeneratedattrsnoFLASH assertionpass. Nativeproof visuallyinspected, enlargedcrop addedforreadability. index.html explicitly separates actualZ80 evidence fromofflineproposal; performance not measured, no playable changes. A production approach should preserve native collision/ownership semantics separately from visual coverage, restore background once perdirtygroup, composecomponentswithmasks thenpublishonepaletteper8x1cell; cache/precomputelimitedoverlapcases ratherthanfullRGBfitinZ80loop. Native masksalone do notsolvepaletteconflicts. r42 remains latest playable, bugstillopenpending actualanimationtraceandproductioncompositor.

## 092 - Solid organic shading alternatives and symptom clarification (2026-11-04)

User clarifies white/grey animation showed black-edged rectangles; previous synthetic overlap experiment may not explain actual fault. Do not present091 as confirmed rootcause. Wants solid saturated organic shading and highlights rather than black dithering,1.3/1.5scales promising. Added preview_level5_solid.py,32options acrossdescriptors9/10/11/8,4themes x2scales. Source aspect-preserved beforeconversion; slight0.45pixel luminance smoothing; no error diffusion; green/yellow,green/cyan,cyan/white,yellow/white shades with rednodes. Black onlysourcealphaoutside; asserts zero black pixels inside silhouette, no blackpaper fullyopaque8x1cells, legal sharedbrightness. Native edge requiresblackpaper but visibleedgepixelsallsolid. Solid palettes may mergefinefeatures and make forms flatter; do not call conversion finished. Visually inspected cel009sheet. Outputs build/graphics/level5_solid_trials/index.html,PNG/BITS/ATTR/manifest. Previewonly, no r42change, collision/timing/dictionarynotvalidated. Actual white/greyblackrectangleanimationfault remains open; user'sclarification overrides earlier inferredattribution.

## 093 - Playable selected level5 core r43 artwork trial (2026-11-04)

User selects earlier source/gamma1.35 1.5x/96x96 option and asks playable changes, then asks smoother/1pixelmovement and shooting responsiveness. Added build_level5_selected.py: separate r43 basedonr42, level5descriptor8 enlarged8x8cells to12x12; exact earlier cel008_1.5_option2 bit/attribute trial packed, with established normal-black policy. Other art unchanged, including unapprovedsizechanges toorbcomponents. Original8pool leftunused; new1104byte cellstream EFA1..F3F0 belowF87C AYcode. Rebuild113-rowdictionary preservingconstantfirst16/reserved54 andallotherusedrows; remap existingcells to newindices. Both residentDOCK1 andcoldDOCK7 dictionaryupdated; nativeC000..FFFFsourceDOCK5/6patched; descriptorpointsEFA1,width/height12. ROM0full_enemy_source poolend updatedEFA1->F3F1 (onecheckedLD DE operand). DoubleB/rocketfix/caches preserved. No sourcearchive/referenceproject changed.

ActualZ80 verify_selected_art_draw.mjs checks888level5descriptor/flip/clip/normal/damage cases with byte-exact bitmap/palette, IFF/map preserved andsourcesbelowAYcode. Initial expectedflash71 failed because normalblackrenderer correctlypublishes7; correctedreferenceexpectation, notgamecode. core_draw.home.bin/png rendered andvisuallyinspected; A5backgroundtestpattern intransparentcells is intentionalprimitivefixture, notgame artifact. Actual selectedstage5doubleBtest700updates afterjump passes, descriptor8rendered, selectedstageunchanged13417refreshes. This is diagnostic death-bypass playback, notunassisted/hardware. Fullprogression41994refreshes8stages/ending/secondcachedcircuit,128blocks,15guards,3410reverse/codechecks; selected3/8restarts andfourerrorcontrols pass. Finalizer validates72TAPpages/regionhashes. Othersevenlevelregionsbyte-identicalr42.

Published build/fullgame/selected_art_r43/RType_TS2068_level5_art_trial_r43.zip SHA25683d582df68868ff05cdd0205dd3450e44429799798d389de472dec6edb807570. ReplacecompleteRTYPEfolder; title5,Fire,B/release/B. ARTWORKTRIAL, notperformanceupgrade: profile_level5_baseline.mjs oldcore159358T vsnew309200T normalunclipped isolateddraw,1.94xcorecost; notwholegameframebenchmark. Otherflips old157200/156711/163043,new305056/304103/316351T. Avoid claiming noslowdown. Enlargedcollision/visualfootprint andphysicalbalance needreview. White/greyblack-edgedrectanglefault unresolved; no compositorchange. 64KBROM unchanged. Existingr42preserved.

Movement/firing sourceaudit docs/movement_and_firing.md:94F1uses8pixelcellcoordinates and8x1metadataC0E4collision, so true1pixelrequiresfractionalphysics/shiftphases/restoration/collision/shotorigins. Main865Fpollsonceperupdate;868CwaitCP3notnecessarilybottleneck. Normal95A6/9A2Cfirechargesonhold and9A33emitsonrelease, soquickreleasebetweenpollscanbemissed;16slot9D96poolalso bounded. These aresourceexplanations, notcapturedspecificsymptom. No movement/firing changes shipped; stillopen. Nextimplementation: higherfrequencyboundedfireedgequeue preservingcharge/AY/joystick/IRQcontracts; fractionalshiprendering; compiledlargecorebitmappalettecache tocutmeasuredcost. Do notsubstituteautofireorvisual-onlyinterpolation andclaimcorrect1pixelphysics.

## 094 - Arcade equivalent identified and pixel-motion proof status (2026-11-04)

User photo12860 shows level5 repeatedroundcomponents, requests arcadeequivalent. Local frame044700.png and level05_objects.png inspected: originalBellmite orbmass surrounds separateyellowmechanicalcore. ExistingconverterextractsROMspritecodes2964/2966/2976 (0B94/0B96/0BA0),capturedspritepalettebank6, each32x32; cycles acrossnativelevel5descriptors9..26. Originalgreen/greyshadedbody withrednodes is indeedthematchingarcadeart. Earlier r43changesdescriptor8mechanicalcore only, nottheseorbs. Evidence build/diagnostics/level5_arcade_identity/orb_sources.png andidentity.json; sourceatlasvisuallychecked. Bellmitename independently corroborated ShmupsWiki R-Type/Strategy and R-TypeWiki Bellmite page. Do not inferfulloriginalanimation timing fromthreeselectedcels.

Priorongoingmovementwork: build_pixel_movement_trial.py exports3shipposesx8ECMhorizontalphases,2304bytebitmap/attrs/maskcache,768legalpairchecks. Interactivebrowserproof build/diagnostics/pixel_movement_trial/index.html uses1pixel/50Hzlogic,keyboardqueuedfireedgeswithcharge,matchingpixelshotorigins,sweptsilhouettecollisionagainstcapturedterrain,coarse8pixelcomparisonmode. verify_pixel_movement_trial.mjs headlessVMchecksX/Y1pixel,phase,quickfiretap,charge,leftbound,coarsecomparison,terraincollision/renderpass. ThisisNOTnativefullgame/cartridgepatchorhardwaretimingproof; existingr43unchanged. Nativefractionalphysics/rendering/shotintegrationstillpending. Userphotoandarcadeidentificationsteerartworkwork,donotclaimmovementrequestcompletedbynonnativedemo.

## 095 - Actual live sphere mapping corrected; r44 and native pixel-motion proof (2026-11-04)

User asks improve Bellmite and insists native1pixel/smootherfasterplay. Live8E85descriptortrace proves sphereanimation is30..33, NOT9..26 aspreviouslyinferred. Decodedoriginal30..33 exactlymatchphotomonochromespheres;34..39areotherenemies. Prior094andearlierclaims9..26werecorrectgamebindingweremistaken; originalsarcadecodesidentifiedcorrectly,butconvertermappedthemtoothernativecomponents. Negativefirst r44attempt changed9..26andactualbosstraceusedonly30..33pluscore8, exposingerrorbeforepublication. Oldsyntheticoverlap091uses9/10anddoesNOTestablishactualsphereanimationrootcause. Correctedsrcbuildertarget30..33andpreserves9..26.

build_bellmite_orbs.py derivesr44fromr43, keepsselected96pxcore andotherlevelart; replacesnative30..33with32x32originalarcadecels0B94/0B96/0BA0,mappedfoursteps0/1/2/1 (authoredmapping,notprovenrecoveredarcadetiming). Solidgreen/yellow/white withrednodes, noerrordiffusion,sourcealphatransparency.3deduplicated144byteassetsappendF3F1..F5A0,poolendF5A1belowF87CAYcode;full_enemy_sourceboundcheckedupdated. Initialexactpaletteoverflowed127rows; preservedallother113rows,filled14remainingwithmaterialconstantrowsandfrequentnewrows,thenRGB-fitnewcellsundertypedtransparency/noblackfullyopaqueconstraints. Allothersourcepixels/palettespreserved;finaldictionary127rows. BothDOCK1/7dictandcoldDOCK5/6payloadupdated. Colourimprovementisreal,butlimitedpairfitcanflattenfinetexture.

888Z80descriptor/flip/clip/normal/flashcasespass;stage5B/release/B700updateprobe renders30..33and8,samelevel14912refreshes. Fullprogression41994refreshes8stages/ending/secondcachedcircuit,3410code/reversechecks,15guards,128blocks;selected3/8restart160checks/3guards,and4errorcontrolspass.72packagedpages/hashes/XORpass. Actualcompleted-framecaptures sample40..400step20 under bellmite_orbs_r44,PNGforeach,native_animation.gif (200msper20-update sample,NOTreal-timeFPS) andboss_live.png(sample200) renderedandvisuallyinspected. Spheresnowgreen/redinactualgame,NOTwhite/grey. Blackhorizontal/cellcutsarestillvisible: nativecompositorunchanged, no claimrectanglesfixed. Larger32pxspherescanincreasecost;nodemonstratedfullgamespeedup. Fullmovement/firingstillunchanged.

Published build/fullgame/bellmite_orbs_r44/RType_TS2068_Bellmite_r44.zip SHA25633855699b23fbfb471e92ec00403b1d0a600bf0031f9bb89feec18214a0dfb7b. ReplaceRTYPEfolder,select5,start,BreleaseB. Hardwareconfirmationpending. No64KBcartupdate.

Added src/pixel_movement_demo.asm,build_native_pixel_demo.py,verify_native_pixel_demo.mjs. StandaloneTAPactuallyrunsZ80onTS2068model: ownIM2vectoratFE00pointFDFDjump,ECMmode2,HOMEbitmap/attrclear,centrepose8horizontalphasesfrom2304bytephasecacheat9000;recomputesnonlinearbitmap/attrsperpixelY,erasesolddirty4x8area,paintsnew4x8rows. Q/Wleft/right,O/Kup/downplusbothnativejoysticksmerged,1pixelpervideointerrupt,clampedX8..224/Y0..152. NoIRQworkexceptEI/RETI;allmotion/drawingmainloopHALT-paced. Actualemulator20consecutiverightframespositions41..60exactly,10joystickupframesY-10,andopposingkeyboard+secondstickcancel. ScreenHOME/PNGsavedandvisuallycheckedshipvisible. Publisheddiagnostic native_pixel_movement/Pixel_movement_TS2068.tap plusREADME. ThisisREALnativehardwarerender/controlproof,notfullRType1pixelintegration,noenemies/shooting/collision/stageloading. Physicaltestingpending. DoNOTclaimfull-game1pixel/fasterplayrequestcomplete;fractionalcollisionandweaponorigins/nativeintegrationremainopen. Priorbrowsertrialnotasubstitute.

## 096 - Native one-pixel differential renderer (2026-11-04)

Userhardwarefeedback: movement smooth butship flasheson/off;requestsXOR/differentialmotion. PreservedoldpixelTAP/source. Added src/pixel_movement_delta.asm,build_native_pixel_delta.py,verify_native_pixel_delta.mjs. Composeold-clear/new-imageinscratchRAMbitmapA000..B7FF/ECM C000..D7FF, nevervisibleerase. Publishunionofold/new4x8bytewindows(atmost5x9): comparevisiblewithdesired,computeXORdeltaandapplyonceonlyifnonzero;ECMwriteonlyifchanged. Thuscommonpixelsneverpassblank;stationaryvisiblewriteszero. Sharedscratchdirtyboundscliprightedgeatcolumn31andhandleSpectrumaddressrowcrossings. NoIRQdraw, sameHALT-per-refreshcontrols,onepixelX/Yandnativejoysticksmerged. InitialsourceaddresspatchSET7alonewouldmapC000ratherthanA000;correctedRES6/SET5beforetests.

ActualZ80verification:20consecutiverightrefreshes41..60,10nativejoystickupY-10,opposingkeyboard+secondstickcancel;825byte-exactbitmap/ECMframesacrosshorizontal/vertical/diagonalmotion,phases,byte/scanlineboundariesandclamps; instrumentedeverybitmapwriteprovescommonold/new1bitsnevercleared. Stationary10frameszerooutputwrites.12870totalvisiblewrites,max40/frame,versusoriginalfixed128bitmap+attrerase/redrawwrites. Thisiswritecountcomparison,notfullgameFPSbenchmark. screen.home.bin/pngrenderedforvisualQA. New build/diagnostics/native_pixel_delta/Pixel_movement_delta_TS2068.tap SHA256 recordedvalidation.json,READMEexplainscontrolsandstandaloneboundary. Hardwareflickerconfirmationpending;doesnotclaimbeam-synchronizedorfullgameintegration.

## 097 - Hardware Bellmite block cuts; actual-position detail feedback (2026-11-04)

Userphoto12861(de770273attachment)confirmsr44colourimprovedbutretainedblackrectanglesseverelycutspheres;requestsdetailandfeedback. Readcurrentstate/testhistory. Addedcapture_bellmite_composition.mjs:exactnativebossdrawcommandsat8CFD/8DD3/8D65/8E29withHLpointingF3F1/F481/F511spherecelsandEFA1core,BCpositions,dimensions,flipentry,8EBFmode. sample40..400step20completedframeHOMEandcommandsJSON. Actualsample200has24spheredrawsandcore;ALLmode60retained-backgrounddrawing,notjustdirectscreenpaint. Capturerepeats700updateprobeandpasses. Thisnarrowstheproductioncompositingpath,doesnotfixit.

preview_bellmite_detail.py generates build/graphics/bellmite_detail_feedback/index.html,sphere_A/B/C.png,composition_A/B/C.png,current.png,manifest. Usesactualsample200positionsandflips,firstdrawpriorityreplayedback-to-frontwithfullalpha(masks),thenfinallegal8x1pairselectionaftercomposition. Coreomittedexplicitlytofocusonspherelayer. Awarmergreen/yellow/white,Bdeepblue/green/cyan/white,Cgreen/cyan/white;sourceoriginalbrightnessguidesdetailandredmaskguidesnodes. Noerrordiffusion. Every8x1max2coloursandsharedbrightnessbyenumeratedpairs;transparentpixelsactualnormalblack;fullyopaqueareasnonblackpairs. Initialnearestedgefitlost55..57visiblepixelsintoblack;correctededgecandidatecostandforcesallvisibleedgepixelstooneink. Assertionsnowzero blackpixelsanywhereinsidecomposedsilhouette,alloutsideblack. Partialedgehuedetailnecessarilyreducedtoonevisibleink. No dictionary127rowreduction/runtimeimplementation/performanceclaim. Currentr44imageincludedandclearlylabelledasactualZ80;alternativesareOFFLINEfeedback,notfixedgameplay. VisuallyinspectedspheresA/B/CandcompositionB. Nativeblock-cutfix,fullgamepixelmotionandfasterplaystillopen;latestgameunchangedr44. UserfeedbackrequestedonA/B/Candroundoverlapreadability.

## 098 - Approved delta motion; QAOP controls corrected (2026-11-04)

User confirms latestnativepixeldeltatestprettysmooth,authorizesfull-gameimplementationandrequestsQAOP. Treatapprovalasnativeintegrationdirection,notcompletedfeature. Addedpixel_movement_qaop.asm/build_native_pixel_qaop.py/verify_native_pixel_qaop.mjs;newstandaloneTAPPixel_movement_QAOP_TS2068.tapunderdiagnostics/native_pixel_qaop. CorrectphysicalmatrixrowsQ=FBbit0,A=FDbit0,O=DFbit1,P=DFbit0. EarlierdemolabelQWwaswrongforrowFD(actualA/S);fixedQAOPsourcewithoutalteringolderartifacts. Testsnowexplicitlyassertallfouractualkeysonepixelcorrectaxis/sign,plus20consecutivepixelsteps/nativejoysticks/opposedinput and825byte-exactframes/commonbitsnevererased.26939visiblewrites,max59/framebecauseupdatedsweepsnowexerciseactualverticalmovement,notoldunmappedkeys;stationaryzero. Nativegamekeyboarddefaulttable7780stilloldinr44. Fullnativefractionalcollision/projectileorigins/backgroundintegrationNOTyetimplemented;doNOTclaimQAOPstandaloneisfullgamecompletion. Userapprovedmotionfeel,sonewprototypefeedbacknotrequired. Latestplayablegameunchangedr44;priorBellmitedetailfeedbackstillpending.

## 099 - Approved deep shadows, source-guided rim alternatives (2026-11-04)

UserprefersdetailB/deepshadows,askscloserarcaderesemblanceandorganicrimhighlights. Savedassets/bellmite_style.json:baseBapproved,30..33correctnativeframes,rimrefinementpending. Addedpreview_bellmite_rims.py andbuild/graphics/bellmite_rim_feedback/index.html. RetainsBuntouchedcomparison;Daddsonepixelwhiteupper/leftedgegatedbyoriginalarcadebrightness>.27andcyaninnerbandwhere>.42,Estrongercyanperimeter/whiteupperleft.Rednodesretained,alphaunchanged;loweredgekeepsshadowinD. Followscapturedactualpositions/flips/firstdrawpriority;finallegal8x1fittingaftercomposition. Reusedlegalassertionsfullytransparentblack/zerointeriorblack/max2coloursper8x1andsharedbrightnessenumeratedpairs. SphereB/D/EsheetsandgroupPNGsfor3sourcecels;visuallyinspectedspheres.pngshowssubtleDandstrongerErims. TheseareOFFLINEfeedback,notnative127-rowpacked/gameplaycompositorfix/performanceproof. Pageexplicitlylabelsstatus. RecommendDsubtlerim;usercancompareE. Fullnativepixelgameintegrationandblock-cutfixremainopen,r44gameunchanged.

## 100 - Dark-blue top/right rim, explicit scanline/cell planning (2026-11-04)

Userrequestsdarkblue1pixelrightedgeandthenalsotop,carefullyplannedseparatelinesifneeded. Addedpreview_bellmite_blue_rim.py. OfflineDbaseline,Fcontinuousblueforced,Gstrictlegalblueonly,Hplannedoutlinevariant;build/graphics/bellmite_blue_rim_feedback/index.html,spheres.png,D/F/G/Hsphere/groupPNGs,manifestwithcounts. SourceDkeepsapprovedBbodyandbrighterinnerhighlights. Per8x1candidateusesnormalblue205andsamebrightnessnormalizationforcell. Gacceptsblueonlyifnormalisedcell<=2colours;transparentblack+body+bluecannotcoexist,soacceptedrim19/18/13of51/50/52pixelsacross3cels. Fforcesblueandturnsentirevisibleedgecellbluewhereblackbackgroundoccupiesthirdcolour,exposingobviousspill. Hnudgesrightsilhouetteoutby1pixelonselectedrowsendingatxmod8=6,onlyifresultingbody+bluepairlegal. Hexpands13/10/10rowsonepixel,retains33/29/24blue-rimpixels. Showsmoredefinedrightbluewithoutwideblueblock;smallshapechangeexplicitlylabelled. Topcontourcomputedfirstopaquepixelpercolumn,rightcontourlastperrow. Assertionsmax2colorsper8x1,transparentblack/opaquevisiblecolourpass;generatedsharedbrightnesspairsource. Groupcompositionrecheckedthroughlegal()afteractualposition/flipslayering;noneofthisisnative127rowpacking/runtimefix. Visuallyinspectedspheres.pngbothbefore/afterH. RecommendHforrightedgeplanning,Gforunchangedsilhouette. Nativegameunchangedr44,fullpixelintegrationpending.

## 101 - Dark-blue edge preference confirmed (2026-11-04)

Userprefersdarkblueratherthanwhite. Updatedassets/bellmite_style.jsonapproved_edge_colourandtop/rightplacement;keepapprovedBbody/interiorhighlights. Extendedpreview_bellmite_blue_rim.pywithJ(darkblueedgesinplaceofresidualwhite),usingHplannedscanlinesthenre-fittinglegal8x1pairs. ExistingD/F/G/Hretained. JindividualsphereRGBAsall3checkedzero whiteedgepixelsafterfinalfit;groupJvisuallyinspected. Outputsblue_rim_feedbackupdatedindex/spheres/Jgroup/Jcels,legal/alphaassertionspass. Offlineonly,nativeintegrationstillpending,r44unchanged. Preferenceaccepted;noneedtoaskuserapproveblueagain.

## 102 - Planned edge approved; conservative contour touch-ups (2026-11-04)

UserselectsplannedHedgeoverclash/no-contrastvariants,asksfurtherlocalimprovement. Updatedassets/bellmite_style.jsonapprovalH;notanotherglobalpalettechange. Addedrefine_bellmite_planned_edge.py andbuild/graphics/bellmite_planned_edge_refined/index.html,comparison.png,H/Kcelsandgroups/manifest. Firststrictone-body-pixelcolourreplacementfound0legalimprovements;didnotclaimsuccess. RevisedKallowsonepixelinwardright-contourtrimonlywhenatxmod8=1,notred/yellownode,andexistingedgeisnotblue: turnsatwo-pixeltipwithblack+body+blueconflictintoonebluepixel+black. Affects0/1/4rowsacross3cels;Hfirstcelunchanged,one/fourblueedgeplacementsimprovedlatercels. Max2coloursper8x1andalpha-change-countassertionspass. Sourceoutlinechangeissmallandlabelled;nohallucinatedbroadshadingimprovement. Visuallyinspectedfinalcomparison. Offlineonly,notnativepalettepacking/compositing/gamebuild. Hremainsapprovedbaseline;Ksmallrefinementavailableforinspection. Fullgamepixelintegration/blockcutsstillopen,r44unchanged.

## 103 - Combined planned-edge spheres and selected mechanical core preview (2026-11-04)

Useraskstoseecombinedbossafterconfirmingcoreincluded. Addedpreview_bellmite_complete.py. Decodesactualr44native_level5descriptor8/dictionary96x96core,appliesoriginalarcadesourcealpharesizedwithsame96threshold;combinesapprovedHplanned-edgeRGBAcelsatcapturedsample200coordinates/flips/first-drawpriority. Finallegal8x1pairfitassertionspassviaexistinglegal(). Outputs build/graphics/bellmite_complete_preview/combined.png,cutaway.png,comparison.png,selected_core.png,index.html,manifest. Leftallcapturedsphereparts/core;rightintentionallyhidesselectedfrontspheresincentralwindowtoexposecore,explicitlyillustrative/notactualdamageframe. Visuallyinspectedcomparison:corelargelyoccludedinfullmass,clearlyvisibleincutaway. No nativebuild/runtimechange;previewonly,dictionarynotpacked.No claimcompositingfixorin-gamechangedanimation.


## 104 - Unreleased native Bellmite compositor and exact H art packing (2026-11-04)

Added src/bellmite_compositor.asm,build_bellmite_compositor.py,bellmite_compositor_fixture.mjs,verify_compositor_boss.mjs. Actual source classified coreEFA1 and spheresF3F1/F481/F511; owner prepass temporarily removes enemy cell-priority gate, pixel composition fills behind existing nonblack coverage and keeps first collision owner. Original fallback preserved. H legal32x32 source bitmaps packed exactly in cold payload;384 dedicated colour bytes inDOCK4 bypass127-row dictionary fitting; selected96core retained. Native metadata coverage cache192bytes inHOME5BC0, low lookup wrapper5BAA, activeflag5C80, highpaintwrapperFD08.

Failures caught, NOT released: BOOT-only cachewrapper patch didnotreachselectedlevel, fixedallregions; bank4mapping hidIM2vector causing ROMwrite09A9 at4A54, fixedDI/EI around helper; wrong retainedbitmap highbyte formula wrote workspace, fixedsubtract7E; flashread8EB1 whileDOCK4mapped producedwhitefilledrectangles, fixedprebankcapture5C81. Diagnostic build/fullgame/bellmite_compositor_r45/sample_200.home.png was regenerated/visually inspected for intermediatewhitefailure, correctedr44-colourmass and exactHcolours. FinalHnativeimage hasroundcoverage but inheritedfrontpalettescausebroadcolourbands; not exactofflinegroupquantization. Initial700countertestinvalidbecauseenginealsoexecuted8B06; changednativecounter/audit torequireF4bit4off. Correctedtestpasses700actualbossupdates/DOCK0immutability/reversetable,checkpoint93,43731refreshes. Replaced tileindexrepeateddivisionby57mod256multiply(exactfor9-bytecelloffsets/indices0..47), same700testpasses41089refreshes. Stillfar slowerthanr44's14912witholdart/compositor. NOnewplayableZIP, fullcrosslevel/hardwaregatesnotdone. Latestpublishedr44unchanged. Movementstillunimplementedinfullgame.

## 105 - TSVideoCodec and relocatable object delta measurements (2026-11-04)

User askswhethercodec/modifieddeltasatobjectpositionscanimprovespeed. ReadexistingTSVideoCodec docs/MEASUREMENTS.md andsrc/encoder/svd_stream.py plusnative decoder, referenceprojectunchanged. Addedcapture_delta_benchmark.mjs: captures61consecutivecompletedr44bossupdates150..210,actualcommandsandHOME,not20-update-skippedframes. build/diagnostics/delta_benchmark holdscapturefilesandmetrics. benchmark_delta_encoding.py importsrealTSVideoCodec encoder read-only, all60XORroundtripsand3hybridroundtripspass. Mean1628.87changedplane bytes,2706.42XORpayloadbytes,4890.6sparsebytes;25parts,4.93stablecommands,179.57dirty8x8cells.

AddedactualZ80src/delta_benchmark.asm/verify_delta_benchmark.mjs.240nativecases/60framepairsbothplanesexact. Meancyclesraw2LDIR258088,wholeplanescan801185.8,preencodedXOR151458.58,sparse117410.4. Meanscreenwrites12288/1628.87/1920.33/1628.87. Publicationonly; offlineencoding/composition/game/IRQ/bankcostsexcluded. Fullscreencomparisonisslowerdespitefewerwrites;thisdoesnotprovewholegamespeedup.

Added src/relocatable_delta.asm andverify_relocatable_delta.mjs: actualZ80localpairedXORpublisher takesrowY/leftbytecolumn/transitionstream,computes9nativeaddressrows,updatesonlychangedrecords. Initial4-bytecoordinate-recordversion6072testspass8968.26meancycles/24928templatebytes; refinedrow-groupformat3bytesperchangedcellpasses6072testsacross3poses/8phases/8directions/multiplerelocations,8/64rasterboundaries. Sharedold/newbitmap1bitsnevererased;bothplanesbyteexact,maximum61visiblewrites.192templates20280bytes,centrecardinal3120. Matched64centre-posecases7036.90625cycles versusbenchmark_existing_player_publish.mjs10461.90625(nativeexistingdirtywindowpublicationonly),32.74%fewercycles. Meanall6072cases7112.31,min5746,max8584includingnativerowtableconstruction. Blackbackgroundpublicationproofonly; cannotblindlyapplyspriteXORoveroverlappingobjectsorclaimfullgame1pixelintegration. docs/relocatable_deltas.md detailsscope/architecture/storage/reproduction. No newTAP/ZIPorhardwareperformanceclaim.


## 106 - Future relocatable-delta research and skill-update note (2026-11-04)

At user request, recorded a future expansion checklist in docs/relocatable_deltas.md and PROJECT_STATE.md. Covers reusable transitions, background/overlap correctness, legal ECM pairs, end-to-end timing, cartridge/RAM budgets, collision/weapon origins and hardware validation. Candidate for a future TS2068 AI skill update; no skill or runtime files changed. Documentation-only, no new execution tests required.


## 107 - Packaged native relocatable-delta movement trial (2026-11-04)

Added src/pixel_movement_relocatable.asm,build_native_relocatable.py,verify_native_relocatable.mjs. Standalone native TAP uses64 centre-pose phase/direction transitions6618bytes+128pointerbytes, relocatable row-group paired XOR publication; original scratch baseline retained. SameQAOP and both native joysticks.825 byte-exact frames,20consecutiveX41..60steps, diagonal/boundary/clamp sweeps, stationary0writes, commonbitsnevererased, max59visiblewrites pass. build/diagnostics/native_relocatable/Relocatable_delta_QAOP_TS2068.tap SHA256bd5c54b3469e05f215093a263efe7e6f6ed609d94e4925f4b65c50fea54f8fa0. A standalone comparison, not claimed as full-game integration. User clarified game asks for keys: no fixedQAOP assignment in gameplay; only trials useQAOP.

## 108 - Actual full-game one-pixel player/input integration (2026-11-04)

Added src/game_pixel_overlay.asm,game_pixel_gateway.asm,game_pixel_irq.asm,build_pixel_game.py and actual-game fixture/verification scripts. R47 uses existing512KB per-level resident regions, bank7 free space, centre ship pose8phases, native key-definition table and both joysticks. Player coordinates are pixel values; native AI/weapons/companions retain nearest character coordinates. Background-aware local composition publishes changed bitmap/ECM bytes once. A10x32-raster backing patch and640-cell collision snapshot allow movement through native scene copying. Original selected keys remain active, verified with injected Z/X/C/V bindings, cardinal/diagonal movement, second-joystick up and keyboard/second-stick cancellation. This does not claim user-visible key-definition UI was automated anew; its code remains unchanged.

Development failures were held back: initial background-aware renderer used about66Kcycles/tick and was too expensive; linear scratch passes reduced this to roughly36K in component sweeps. Initial scene-copy locking paused movement. Restore/repaint during IRQ exceeded120Kcycles, rejected. Cached backing and a single publication pass reduced observed gameplay IRQ-prefix maximum to about52Kcycles on the tested route, not a global worst-case bound. Main cache preparation uses a busy guard and bank7-mirrored IRQ entry/exit; bank mapping is restored before saving the bank byte to HOME. Attribute-mapped low-stack sections stayDI. Fixed native stack visibility/entry contracts rather than assuming high ROM/stack survives mapping. Reversal-table source bytes reused for the IRQ mirror are regenerated in HOME5D00 by the existing initializer and continuously checked.

Retained buffers can contain stale bitmap data when their ownership cell is empty: copying those bytes behind the new ship produced rectangular fills. Effective backing now uses the ownership snapshot and treats empty/own temporary cells as black. Enemy owner80 is a valid enemy slot; a temporary experiment excluding it was reverted after reading native owner tagging. Padding at column32/raster160 is not published. A test briefly read apparent key bindings from visible HOME attributes while F4 selected that view; corrected test reads the physical native binding bank. No game key definitions were overwritten.

Component verify_game_overlay:894 native ticks, both planes exact against background reference,22187 observed bitmap writes preserve all common old/new1bits; retained planes restored. Stationary overlapping pixels set the hit flag, while disjoint pixels sharing an8x1 cell do not. Actual verify_pixel_game_death has no death bypass: hit2270, real death2275, respawn2537, active/new cleared-hit state2541, no disk reload. Actual movement test observes sustained one-pixel IRQ steps using the chosen binding. Native fire edges are captured independently of slow world updates:8physical press/releases produce exactly8normal shots,7allocated fromIRQ on the tested route; a later long hold produces exactly1charged beam, no queued duplicates. A separate saturation test makes20IRQ-style calls with all16normal slots occupied, then frees slots0/7/15; native returns stay balanced and no occupied slot is overwritten. Weapon rendering still follows world updates and rounded native coordinates; no constant30/60fps or all-projectile pixel rewrite claim.

R47 all8boss routes complete700actual updates each; full8-level progression/ending/revisited circuit and error gates pass. Initial selected-restart test failed because it forced game-over at an arbitrary API frame boundary inside the new low-stack IRQ helper. Corrected injection occurs at main94F1 with native high stack/map; real death test independently passes. Selected level3/8 cached restarts then pass. Diagnostic phase.png and intermediate sample_200.home.png files under delta_benchmark/R47 were used during inspection; reused paths were overwritten by later captures. Final movement.home.png shows actual new gameplay, not an offline conversion.

## 109 - Bellmite precomputed row-pair caches (2026-11-04)

Added src/bellmite_compiled.asm,build_compiled_game.py,verify_compiled_bellmite.mjs. R48 changes only level5 from frozenR47.569-byte helper uses768-byte normal row pairs atDOCK4:8C00 and768-byte horizontally reversed pairs atDOCK7:F380; vertical flip walks pairs backwards. Core overlap uses a16-byte temporary pair cache, unowned core cells use the original native palette renderer. Temporary graphics stack uses unused DOCK2 tail while it is mapped; original high stack is restored before returns. Sprite helper remains main-only/DI. Source flash is captured before banking at0D30, within reserved0D00..0D3F; the unused padding was05 rather thanFF and was checked before replacement. No assets/code overlap and no read-only-cartridge compatibility claim for this RAM implementation.

384 native whole-sprite normal/horizontal/vertical/both flip, negative/top/right/bottom clipping, empty/ink-on-black/black-on-paper/two-opaque owner and flash comparisons reproduce R47 bitmap+ECM output and owners. Code bank and both pair caches remain intact. Initial reference mismatch came from an uninitialized legacy flash capture byte; reference precondition is now explicit, while R48 captures the real current value for every unowned paint. Aggregate clipped primitive costs fall11.51%; actual700-update boss route32341refreshes versusR4736820(about12.2%less elapsed emulated time). This does not claim faster than the older unmaskedr44game. Actual sample_200.home.bin/boss_compiled.png visually inspected; core and approved H art preserved, with shared-pair overlap colour compromises. Horizontal cache intact after700updates and after all-level cached revisits. Updated native_level5.bin diagnostic asset image from actual cold payload so future previews do not decode the older orb bits.

## 110 - Final r48 cache/packaging gates (2026-11-04)

R48 full progression/ending/second resident circuit:51556refreshes,128blocks, all8levels reused without further disk reads,16520 executableDOCK0/reversal checks,15core/workspace guards, nested folder retained and no directory-change commands. Selected3/8 game-over restarts7117/7158refreshes,575/568code+reversechecks,3guards each, no tape entry or repeated level loads. Four loader-error controls reused from byte-identical bootstrap/loader inputs and recorded provenance. All8boss routes700updates each: seven levels reused by exact region identity to finalR47, level5 rerun with caches. Gameplay input/fire/real-death/component evidence likewise reused only after byte-identity checks of sharedBOOT/level1/overlay; validation_summary.json records provenance.

finalize_compiled_game.py verifies72packaged asset pages, all lengths/SHA256/XOR and ZIP integrity. Includes RTYPE disk game and separate cached/baseline standalone trials; game retains its selected keys, only trials useQAOP. Local package build/fullgame/compiled_game_r48/RType_TS2068_r48.zip SHA256983a16c97845aa12bc9c32db09c0fa7b7d86986224f5893aaa486430f519076d. README documents loading, controls, Bboss shortcut, RAM residency and limits. No physical validation yet. Stock64KB cartridge remains unchanged; no incompatible writable-ROM game image was presented as a cartridge. Original ZIPs/reference projects unchanged. Future relocatable-delta AI-skill note retained, skill itself not edited.


## 111 - R49 material composition and metadata visibility correction (2026-11-04)

R49 supersedes r48. Low gateway now captures owner and commits unowned metadata before mapping DOCK4. Metadata rows16-19 reside in HOME8000-807F; the former shader accesses while F4=19 could modify DOCK4 debug-prefix bytes instead. Added actual640-cell HOME+DOCK ownership checks and immutable debug-prefix checks across384 source/flip/clip/owner/flash cases. All pass, along with foreground RGB preservation, full union coverage, no introduced FLASH, immutable normal/horizontal caches and codebank0. Rejects retain native fallback semantics. Improved material composition recovers back shading in empty/front-filled rows where legal pairs allow it. Artificial worst-overlap primitive totals65984872cycles vs54391372 old: about21% slower there, not a universal speedup. Actual700-update L5 route31891refreshes versus R4736820 (about13.4% less), due cached rows/opaque-row shortcuts and route-specific composition.

All8boss routes rerun finalR49,700updates each: L1 12173,L2 11332,L3 12398,L4 17063,L5 31891,L6 11568,L7 9579,L8 11572refreshes. Invulnerable boss diagnostic, not a successful manual playthrough. L5 horizontal cache intact after route. Full progression/ending/second resident circuit51563refreshes,128blocks,16481 executable-bank/reversal audits,15workspace/core checks; all8revisited without further disk loads, nested directory retained. Shared controls/movement/fire/death/error and selected3/8restart evidence reused only after exactBOOT/non5region/overlay identity; validation_summary.json records provenance. Sprite composition remains expensive; centre player pose and rounded native weapon/AI coordinates remain.

Diagnostic boss_final.png is final native completed route snapshot after boss has left the display, not an artwork preview. boss_composition.png is controlled native compositor replay of25captured actor draws (capture_material_comparison.mjs), visually inspected; do not label it a live gameplay or hardware screenshot. Previous comparison.png predates final bank correction and is development evidence only. Original black-space convention retained. No changes to original ZIPs/reference projects/AI skill.

Final72asset-page length/SHA/XOR and ZIP checks pass. Package build/fullgame/material_game_r49/RType_TS2068_r49.zip includes RTYPE and separate relocatable-delta/baseline movement TAPs. Game key selection preserved; QAOP applies only to trials. Hardware validation pending. Older stock64KB read-only cartridge unchanged. r48 package is superseded and must not be recommended.

Package SHA256 c22a9b7f5cf1713e9b7e47131538bd87a235d16b2a6aa5a5306203e3924fe06f


## 112 - Boss delta experiments and r50 integrated repairs (2026-11-04)

User clarified that the requested relocatable-delta trial was for bosses, not only the player; fixed game keys must not be imposed. Built src/boss_relocatable_trial.asm, capture/build/verify_boss_relocatable scripts. Eight original consecutive25-part draw arrangements are recomposed using r49 and encoded as relocatable paired-plane run deltas; same XOR stream reverses the transition. Native TAP keys1/2/3 select origins, Space pauses. Stream26587bytes+16pointers. Native105cases/7origins,105live completed frames,120519common-pixel checks, pause0writes pass. Mean193829.7publication cycles versus2130180.1source-draw composition cycles; offline composition/encoding omitted, not gameplayFPS. Initial raw ORG without DS produced missing address padding and failed the decoder test; corrected. A reverse-to-forward pivot skipped pose1; live repeated-cycle test caught it, fixed. Diagnostic validated_pose0..7.bin and pose0..7.png, boss_delta.gif, live.home.bin, index.html in build/diagnostics/boss_relocatable. GIF illustrative80ms cadence, not a measured streaming demonstration. boss_delta.gif and poses are native byte-validated output renders, not hardware images.

User then required arbitrary gameplay arrangements in the design. Added scripts/boss_dynamic_renderer.mjs: independent local cel/phase/flip row sample caches, old/new coverage damage sets, priority recomposition of intersecting parts, legal8x1 pair choice after composition and final paired-plane XOR streams. Full core plus independent spheres can move/reorder/change frames/flip/remove/insert over changing background.100arbitrary states match full reference composition and native Z80 publication; byte/pixel clipping, common bits, stationary0dirtycells pass. Mean298.2dirty cells of6144 and21603.9publication cycles on this sample. Composition/encoding are host-side, so NOT a full native compositor, whole-game win or integrated boss update. Interactive build/diagnostics/boss_dynamic/index.html allows dragging/one-pixel arrows, cel/flip/depth changes, rearrangement and independent animation. UI script exercised18draws with DOM/canvas doubles; not actual browser visual QA. preview.png is that canvas render, visually inspected. scene0..90.bin every10cases are native-validated scene planes. No pre-recorded complete boss frame atlas used by dynamic experiment. Future skill note expanded in docs/r50_changes.md and docs/relocatable_deltas.md; skill itself unchanged.

R50 gameplay src/game_pixel_overlay_fast.asm keeps chosen native bindings and both joysticks. Initial3held samples use1px steps, then3px per publication to improve travel without tripling draw cost. Final normal-route100refresh input sample78pixels. Fixed9row damage assumption failed accelerated vertical component test at224,86; corrected to8+abs(dY), max11rows,55bytes/plane F790..F7FD and rowtableF800..F815. Horizontal motion now processes8rows. Final894tick component:10454common bitmap-write checks, max43734cycles, retained planes restored, stationary overlap hit/disjoint shared-cell no-hit pass. Actual game redefined Z/X/C/V table, diagonal/opposed controls and both joysticks pass.8normal releases produce8shots and held input1beam; real pixel-hit→death→respawn passes without death bypass. Ship centre pose and rounded native weapon/AI coordinates remain; no constant update-rate claim.

L1 snake issue confirmed: original100x30 arcade multi-joint strip had been shrunk into every24x24 frame16..19, all the same orientation. Extracted one31x30 joint, native24x24 orientation siblings and authored short bone links matching joins. Existing3x3allocation/pointers/anchors unchanged. Intermediate BOOT palette assumption2000 was wrong (initial game state there, palette E000mirror): resulting cyan dots rejected. Corrected converter uses E000mirror for BOOT and separately loaded level1; identical source frames asserted. Actual normal level1 draws4-5joints along diagonal in six completed captures. Initial disconnected/small source, arcade enlarged reference, old native/live comparison under build/diagnostics/snake_r50; final build/fullgame/responsive_game_r50/snake_frames.png, snake16..19.png and snake_live0..5.home.bin. Final snake_live5.png viewed and connected-joint spacing visibly improved. Authored connectors/rotations are not claimed to be extracted arcade animation cels. Colour style remains refinable.

Title garbage cause: title atlas E400..F8FF aliases post-r47 player engine/cache bank7. Earlier r24-only title checks missed final integration. New381byte src/title_delta_scratch.asm generates suffix base and selectedphase from intact DOCK4 title source into owned HOME A600/A750, preserving/restoring prior scratch. No title fetches from player atlas region. Actual disk loader all116bitmap/ECM states exact; bank7player code and phases unchanged. Corrected test expectations to normal-black7/5 (old r24 expected71/69). title_state10/30/60/80/100/115.home.bin are final diagnostic captures; title_state30/80/115.png rendered and viewed (early image prefixes updated after final validation). Initial combined letters are genuine OR-composed logo pixels, not code bytes. Range/lifetime ownership checks now part of final packaging; use final binary/title-to-game tests, not stale component milestones.

Parallel test startup encountered host out-of-memory errors, not emulated game verdicts; rejected those runs and reran sequentially with bounded Node heap. Final frozen serial run passes controls, charged fire, death, title, snake, selected restarts, four loader-error controls, full progression and all8boss routes700updates each. Final logs final_*.log. Earlier in-progress r50 route timings before damage scratch correction are development only and superseded. Original ZIPs and reference projects unchanged;64KB stock cartridge remains unchanged. Boss experiments are separate from the actual game renderer. Hardware validation pending.

Final full8level/ending/resident revisit: 51348refreshes,128blocks,16427code+reverse checks,15guards. Boss refreshes: [(1, 12148), (2, 11264), (3, 12361), (4, 17033), (5, 32616), (6, 11525), (7, 9572), (8, 11517)]. Selected restarts: [(3, 7111), (8, 7157)].
Final72asset pages length/SHA/XOR and ZIP integrity verified by finalize_responsive_game.py. Deliverable build/fullgame/responsive_game_r50/RType_TS2068_r50.zip SHA256 f0092f0ba13893fbd0a9bd99c76ad12e1181b325b7a3cba1861b6540e6a0fd7c. Includes RTYPE and labelled BOSS_DYNAMIC/BOSS_FIXED trial folders.

R50 final trial colour-policy follow-up: dynamic legal-pair catalogue excludes bright-black pairs, matching hardware black-space requirement. All100native arrangement cases rerun successfully with JIT disabled after transient host allocation failures; no failed resource startup is counted as a pass. Meanpublication21603.78cycles/commonchecks13697 after this policy refinement. 61440 captured attribute bytes independently checked for normal-black policy. Final game diagnostic PNGs regenerated from final captured planes without NumPy. Final package reverified after trial update; preceding package hashes in entry112 were intermediate, superseded by SHA256 a8c8cd0eb86746c58453d812c5f4388531d168e88b8c75d41195c8df87d2715b.


## 113 - Native L5 boss speed and size repair, r51 (2026-11-04)

Confirmed native sphere24x24/core64x64 versus current32x32/96x96:528allocation cells versus original280for24sphere parts+core. Actual native shader765bytes skips completely opaque foreground cells before source decoding and copies unowned cached pairs directly.384exact-output cases match r50 bitmap/ECM, all640HOME+DOCK metadata, flips/clips/flash, caches/DOCK0/debug prefix. Intermediate opaque-row aux experiment passed correctness after branch-range corrections but gave only1.7%extra scene gain and worsened synthetic cost; rejected. Failed assembly plus subsequently stale test result is not final evidence. Final asserts8F10..9000FF; no auxiliary code shipped.

Compact default24px spheres/80pxcore uses native movement anchors,3x3sphere and10x10core descriptors,836bytecore inside prior fixed slot and transparent padding;768byte normal plus768byte flipped caches retained.384independent-source/layout+coverage/foreground+ownership cases pass. Native700update tests bothfull/compact pass. Same25draws2133922→1634424large→1274247compactcycles (23.4%/40.3%less).700update route32616→27508large→22938compactrefreshes (15.7%/29.7%less elapsed time). No constantFPS/hardware claim.

Clearance diagnostic samecaptured25draws uses actual centre player pixel mask:10024→7273boss pixels;18463→21316safe positions, both static left-to-right traversable. Excludes projectiles/terrain/timing, not a difficulty proof. build/fullgame/fast_boss_r51/size_comparison.png and *_preview.png are controlled native-compositor replays, visually inspected. compact_boss_r51/gameplay_160.png and gameplay_200.png rendered from actual completed frames;200viewed. sphere0..2_24.png/core80.png are offline packed-asset previews. All diagnostic images/results retained; scripts/analyze_boss_clearance.py and benchmark_fast_boss.mjs reproduce measurements. No new captured arcade source claimed.

Only level5regions change. Full BOOT/other7region identity to finalr50 asserted; selected inputs/joysticks/player/title/fire/loader regression evidence reused explicitly on that basis. Compact full8levelcache/ending/resident second circuit rerun: 51348refreshes, 16427code/reversal checks,15workspaceguards,128blocks; no additional reads for cached revisits. Both variants72page length/SHA/XOR validations;80unique packagepages/ZIPintegrity pass. RootRTYPE usescompact; optionalALTERNATE_LARGE_ART/LEVEL05.TAP retains32/96art with same fast renderer. Reset/reload required after asset swap to clear resident older RAM.

Deliverable build\fullgame\compact_boss_r51\RType_TS2068_r51.zip SHA256 4f0a8d25fb1ac7c4263576466b5b214a1d1fbaa4809f75e8ef0a8d42f5ffa174. docs/r51_boss_speed.md. Actualnativegame optimization, not substitution of fixed/host-side delta trials. Stock64KBROM unchanged; physical validation pending. Originals/reference projects unchanged.


## 114 - L8 fine bitmap detail and player motion, r52 (2026-11-04)

L8five48x32frames42..46 resampled from verified arcade captures with previous user A-profile gamma1.8/saturation4.5, then Sierra Lite after actual packed-row selection. Other L8palette rows protected;37newdeduplicatedrows fit111available slots. Dimensions/sourcepointers/animationindices unchanged. Representative42mixedbytes136→181of192;1pixelruns127→309;8pixelruns56→11; all1..6run lengths present in every frame. No forced arbitrary pixel patterns. assets/enemy_art_selections.json now records L8r52integration only, not completion of remaining gallery selections.1056native allactiveL8descriptor/fourflip/threeclip/flash cases match independent bitmap+ECM decode.

New src/game_pixel_overlay_responsive.asm2363bytes:1pxfine initialsamples then5pxheld(publicationonce),10x64worldpatch vs10x32. DOCK7pixelsF100..F37F640bytes; DOCK2attrs5D00..5F7F640bytes, distinct fromHOME5D00reverse table and DOCK2private stack5CA0..5CF0. Scratch65bytes/plane F780..F801; rowtableF820..F839; collisionF880..FAFF. Sourcecoldcommoncode is copied before DOCK2tail reused. Attributebank sectionsDI with stackoperations outside hiddenHOME mapping; new actual write guard checks13440cache writes and hidden-stack IRQstate. Engine/phases/flippedspherecache/loader ranges guarded. Empty-row cache ownership reused for8rasters, sky filled0 rather than sampled; a first larger-cache candidate increased world cost, so empty-row fast path added before final freeze.

Actual100refreshselected-keytravel113pixels vs78r50,44.9%farther (intermediatepre-empty optimization108notfinal). Frozen-copy verticaltravel23vs9old.894baselinepattern/collision ticks plus extra20nonemptycopyticks and8emptycopyticks pass:7862bitmapwritecommon-bitchecks, retainedplanes restored, real overlap hit/disjointsamecell no hit. Test-harness reset initially leftWASCOPY1 before directly invoking render at a new location; reset corrected. A retained comparison then included the injected input byteDOCK3:14FA outside playfield; neutralizing injectedinput before comparing fixed the harness. These were not production fixes. Finalcode tests both previously populated and newly empty attr cache. Native sampledmaxIRQprefix52590cycles, no fixedFPS/worst-case guarantee.

Actualfinal controls(chosenZ/X/C/Vtable, bothjoysticks, diagonal/opposed),8normalfire+1beam, actualpixelhitdeath/respawn, title116states, L1snake normalroute, all8boss700updates, selected3/8restarts and fourloadererrorcontrols pass. Full8levelcache/ending/second resident circuit 53442refreshes, 16514code/reversal checks,15coreguards,128blocks. Bossrefreshes [(1, 12767), (2, 12215), (3, 12367), (4, 17618), (5, 23033), (6, 12083), (7, 9950), (8, 11907)]. Optionalr52largeL5route700updates28026refreshes also passes. R51compact shader andart retained; no new delta prototype integrated. Worldrate stillscene-dependent; largerpatch finite, not a promise to remove all movement stalls.

Images: l8_comparison.png(all5packedsource comparisons), L8_42..46.png plus.bits/.attrs(actualpackedpreviews), l8_before_after.png(firstrowcroppedcomparison) and L8_gameplay_160/200.png(nativecompletedframe captures, invulnerable route) underbuild/fullgame/detail_motion_r52. Fullcomparison andgameplay200visuallyinspected. Prior pre-empty-code test snapshots superseded by final rerun; finalsample*.home.bin feed the rendered gameplayPNGs. Comparison is offline packed-source render, gameplayPNGs emulatorcaptures, nonehardwarephotographs. Normalblack/geometry constraints and unchanged otherasset/code ranges checked by finalizer.

Final72assetpages plus8matching-engine optionalL5pages pass length/SHA/XOR/ZIPintegrity. Deliverable build/fullgame/detail_motion_r52/RType_TS2068_r52.zip SHA256 6b00800321e74be3ce29d19c5e430d2a8706e4bd4d32ace3ea25b6a19e9cbae1. READMEloading/selectedcontrols/movementlimits/variantdetails; docs/r52_detail_motion.md. Reset/reload required to clear resident oldlevel assets. Stock64KBROM unchanged, hardwarevalidationpending. Originals/referenceprojectsunchanged.


## 115 - Standard boss rendering/input scheduling, r53 (2026-11-04)

User's standard compact L5 movement stall reproduced. Original DI shader plus half-rate IRQ publication caused 59 player ticks in 480 refreshes on the movement/fire route, only 3 of eight short shots. Separate HOME IRQ stack, raw banked interrupted-stack preservation, temporary DOCK4 IM2 table and carefully DI bank/stack transitions make visible L5 cell work interruptible. All source artwork/dimensions/normal-black palette data unchanged; standard24px spheres/80pxcore retained. HOME5B60..5BBF IRQ stack,5B5B vector trampoline,5BCE raw SP; original HOME5D reverse table preserved. Temporary vector high byte at asserted-zero DOCK4:9000 restored with I84 before return; bank4 core scratch moved8BF0..8BFF. Engine2372bytes, gateway165, shader769; low helper gaps statically FF-checked.

L5 cell-opacity rejection moved before interrupt setup/source decoding. New covered-row path advances source without row decode/blending. Unowned direction/flash and owned row pointer direction chosen once per cell; no extra compositor pass/whole-screen overlap scan. Same25native captured actor draws 1274247 -> 1242620cycles, source overlap rows 1064 -> 554. Synthetic384cases total41754158 -> 41925534cycles (0.41% extra safety/setup in that different workload, not a universal speed gain). All8boss palette lookup removes redundant saves and uses register-preserving byte range checks;5088direct/retained native draw cases exact across observed descriptors/flips/clips/flash, about6-7% less draw CPU in those samples.524288native source pointers verified.384independent compact coverage cases and384byte-exact r52cases pass.7565interrupt injections across sphere/core/orientations/overlaps preserve maps/stacks/registers/draws; audio/input scan stubbed only for this boundary test. Real audio/input tested in full routes.

Unrestricted full-rate publication candidate retained locally in boss_input_priority_r53, NOT shipped as standard: it improved input but consumed scene CPU. Standard samples fire edges on every accepted active-game IRQ, including backing-capture busy periods, with alternate-IRQ player publication and original half-rate charge count. Inactive guard prevents gameplay scans/queuing on menus. Chosen key definition, merged native joystick ports, fine1px/held5px steps retained. Matched L5final 162ticks/480refreshes,8of8shortshots+1beam; all8levels8shots+1beam. L5mainupdates13->10, so no whole-game FPS claim: restoring periodic audio/timers and responsive input consumes CPU. Full profiles/table in docs/r53_boss_speed.md and validation_summary.json; no hardware result claimed.

Development failures retained in diagnostics/logs and superseded: first IRQ prefix guard rejected the intentional new low stack; real stack-switch race then exposed by BAD SP, fixed DI before both bank/SP transitions. A row-step optimization clobbered DE and failed coverage, fixed preservation. A longer JR failed assembly; subsequently invoked stale tests were invalid and not release evidence. Full-rate short holds crossed the old charge threshold, fixed half-rate charge timing. IRQ comparator initially included intentionally changing native timer bytes; restricted to actual planes/ownership/register contracts. A cold input-scan fixture entered uninitialized game paths; boundary-only test now uses explicit scan/audio stubs, with separate real-input game routes. Movement4px edge clamp at x224 was legitimate and added to its harness. Inactive IRQ capture now separately guarded. No failing prototype is the packaged game.

Final frozen serial gates:7565IRQ cases;524288classifier pointers;384independent+384exactL5composition;5088allbossdrawcases;894player ticks+retained/frozen/empty/collision tests; actual selected keys/bothjoysticks;8normal+1chargedfire; real death/respawn;116title states;L1snake;selected3/8restarts;fourloaderfailures;all8boss700updates;full8residentcache/ending/revisit 53389refreshes. Final boss refreshes [(1, 12681), (2, 11996), (3, 12344), (4, 17217), (5, 24703), (6, 12077), (7, 9955), (8, 11792)]. Phase/cache/source art ownership and72pages/XOR/hash/ZIP checked. No new diagnostic images: byte-identical rendering required, native binary/profile captures retained. Original archives/reference projects unchanged. Stock64KBread-only cartridge unchanged.

Deliverable build/fullgame/boss_speed_r53/RType_TS2068_r53.zip SHA256 13e5f302e757ea5a9ae9559d56fde44bad4afd4a06340cafd9baa984e8e93563. Complete matching RTYPEfolder, reset/reload required, older large-art level not compatible. Hardware validation pending.


## 116 - Projectile travel and live-world ship/exhaust spill, r54 (2026-11-04)

User confirms r53player moves well; requests faster projectiles and reports intermittent L5boss fragments around player/exhaust. Clarified flame behind ship, not Force pod. Reproduced stale-rectangle replay in native component: after snapshot, unrelated byte changedA5->3C/attr2; r53republishesA5/attr7. Exact old/new mask-union publication now preserves live pixels outside ship and untouched ECM cells. Retained cleanup likewise uses current ship-only coverage, avoiding a second stale replay.128changing-world cases across8horizontal phases/eightdirections/fine+held steps protect6271872outside-coverage bit checks after publication+cleanup. Coverage includes cached exhaust footprint. No newly authored flame-animation clock; separate flame-symptom question remains for hardware feedback. Legal shared8x1colour conflicts not claimed eliminated.

Player memory: OLD F6C0..F700,NEXT F700..F740,coverageF740..F781,pairedscratchF781..F803,rowpointersF820..F83A,cleanWORLD F83A..F87A,collisionF880..FB00. Helper125bytes F080 belowF100backingpixels; engine2427bytes fitsE400..ED80. Existing phases/flippedcache/palettes/art/IRQgateway/shader/joysticks/audio unchanged. Removed unreachable fast_prepare pixel/attr branches: internal retained-window caller is restore_copy withMETA0; prepare already uses render. Kept ordinary non-copy composition/publication fast path; copied old mask rows withLDI, shared partial-byte merge registers and used full-byte coverage shortcuts. Early mask prototype cost more and reduced input cadence; rejected. Final normal component mean/max 11346.3/49928 versusr5311132.0/48887; matched L5ticks162->158,8shots+1beam,worldupdates10->10. Settings1pxfine/5pxheld retained; no universal equal-FPS claim.

16-slot normal/spread updater takes up to3original travel steps with metadata checks at each native-step endpoint, stops at first enemy/terrain, ignores friendly/dirtyIDs<80, then native final draw/hit path once. Original native stride/collider granularity retained, not a new per-pixel sweep. Normalclear travel2->6cells; actual native slot8->10old/8->14new; bitmap/ECM/metadata match original at same destination. Single-slot example5823->6845cycles.4088native helper direction/bounds/intermediate-blocker/friendly-ID cases pass, full-pool allocator checks pass. Charged beams/other pools retain timing; weapons still world-clocked, not independently higher-rate redraw. Source low-bank FFgaps statically checked. Allnative damage/sound calls retained.

Development diagnostics: baseline replay fail retained as reproduce_player_spill.mjs. First helper tests omitted loading new helper into their fixture and failedSP; fixture corrected. Changing-world comparison initially included injected input byteDOCK3:14FA outside playfield; restored it before comparing. Initial broad retained cleanup also replayed stale neighbours; current-mask cleanup fixes it. Initial sweep stopped on any nonzero cell, corrected to enemy/terrain>=80 to avoid friendly shots/dirty cells. Earlier regression passes during optimization were not release evidence; final serial run freezes all9regionSHA hashes. Diagnostic ship_current.png is an offline packed centre-phase preview, initially blurred then rerenderednearest-neighbour with actual packed colours and viewed; no new gameplay image or physical photo generated. Native HOME/bin/profile captures retained.

Final frozen gates:7565IRQ-boundary injections (scan/audio stubs only in isolated boundary test),16slot capacity,894player ticks plus retained/frozen/empty/collision checks,128live-world-change cases,4088sweep cases,actual native shot comparison, chosen keys/bothjoysticks,8normal+1beam,real death/respawn,title116,snake,restarts3/8,four loader failures,all8boss700updates, full8residentcache/ending/revisit53981refreshes. Bossrefreshes [(1, 12872), (2, 12368), (3, 12529), (4, 17413), (5, 23742), (6, 12257), (7, 10190), (8, 11975)]. Source/cache ownership,72pages/hash/XOR/archive integrity checked. Stock64KBROM,originalarchives,referenceprojects unchanged. Hardware validation pending.

Deliverable build/fullgame/player_weapons_r54/RType_TS2068_r54.zip SHA256 315178184438410255074c62c53f2e8ade9641fb641c2e46b87d478e7b73fa6e. Replace complete RTYPEfolder and reset before RTFULL.TAP; old or larger-art level files must not be mixed.


## 117 - Clarified disappearing flame: original timed plume (2026-11-04)

User clarifies the flame sometimes stops showing and assumed this was planned. Initial response incorrectly called it unintended before inspecting the separate effect; corrected after native verification. The cached centre-pose rear pixels are separate from global sprite0x62 (98), a16x8flame/plume drawn two character cells behind ship. Native9577 checks7A98, skips effect when0, otherwise decrements then draws98 with45/46colour/vertical variation and resets flash throughC07A. Launch8BAE sets56(38hex),respawn path8BD3sets32(20hex); pickup path9931also sets48. Therefore expiry of this separate effect is explicit original behavior, not an always-on thruster failure. No always-on repair/animation patch applied.

Actual r54native9577gate tested with timers0,1,2,32,56 and both parity states:10cases pass; timer0 selects/draws0sprites, positive timers select/draw1and decrement. Fire continuation alone stubbedRET to isolate effect. scripts/verify_thruster_timer.mjs and build/diagnostics/thruster_r55/timer_validation.json. Diagnostic r55directory is investigation-only; no r55release created. Additional1200refresh stationary L5route found0missingframes at the sampled cached-ship rear pixel, not a claim that the separate timed plume should stay visible. profile_thruster_visibility.mjs and stationary_L5.json retain that scope. native98.png is an offline monochrome occupancy preview decoded from original sprite98, not ECM artwork or a hardware capture; inspected bytes/histogram and viewed. Original title/game assets unchanged.

No game binaries or r54package changed. Latest r54 ZIP SHA256 still315178184438410255074c62c53f2e8ade9641fb641c2e46b87d478e7b73fa6e. The earlier boss/background replay fix and faster normal/spread-shot changes remain separate. Leave native timed plume behavior intact.


## 118 - Independent projectile simulation and visible redraw, r55 (2026-11-04)

User rejects r54's sparse visible bolt updates and asks to separate player/projectiles from boss updates. Normal/spread pool5EB4 now serviced by its own alternate IRQ phase, after full-rate input/fire capture; player publication remains on its existing phase. Removes r54's3x world-step updater. One native direction step (8pixels) per serviced phase, original glyphs46/47/48 and normal-black ECMcolours. Isolated x8 open-space bolt has21successive visible positions9..29 rather than roughly3r54normal6-cell jumps. No claim of new bolt artwork frames or universal constant FPS. Eight active slots maximum/phase, fair round-robin16slots; main background capture/copy pauses overlays. Charged beam/other pools keep prior clocks. Native timed launch plume unchanged.

Engine575bytes DOCK2:5880..5ABE, state128bytes5F80..5FFF, distinct private stack below5CA0; tested lowwater5C96above L5scratch5C82. Cold engine atDOCK7F100 is installed only after nativeHOME9880code was copied, and restored from runtimeDOCK2 before resident bank changes. Thus cold/source overlays cannot corrupt nativecode or invalidate cached revisit installation. Gateway91bytes in unreachable oldplayer94F9..9553, hit drain66bytes9DA5..9DE6, old swept helper ranges reclaimed for bank-safe screen/pool shims. Nativecoarse entry remains bypassed94F6; live player engine, fine/held settings, phasecache, damage helper, boss shaders/art/sizes/audio unchanged. Normalblack clear; skips occupied bitmap bytes/colouredpaper, tracks exactly which of16glyphbytes were published, erases only those glyphbits and preserves added starbits. Clears overlays before every worldcopy. Conservative ship exclusion protects independent player composition.

IRQ performs per-step native metadata tests for both cells, queues firstenemy/terraincontact and stops visible bolt. Main resolves enemy/FA contacts usingA490, outside boss composition. Actor script signatures reject stale queued targets. Actual nativehealth3->2once, repeated drain no duplicate; replacing targetsignature retains replacementhealth3. Solidterrain clears slot withoutactorhit. Fullpool/round-robin/expiry/copy cleanup, all5native direction types18/19/1A/21/32, exact originalbitmap/ECMbyte comparison and added-starbit preservation pass. Cold source/RAMmapping/SP/engine save checks pass. Normal active component19389cycles atsteadyposition, emptyphase7637; firstfull16pool phase51569cycles (not claimed maximum steadyfullpoolcost).

Development failures: first component revealed mask pointer advanced after erase and reused for next draw, leaving trails; mask selection now resets at eachpaint. Assembler caught out-of-range JR and oversizedgateway before gameplay; dispatch shortened. Static padding check caught thatL5+retained routine RET is at1927, not padding; IRQ hook starts1928and preservesRET. First broad run stopped because fixture lacked unchangedoverlay.bin/overlay.sym/player_damage.bin; copied exactr54helpers and reran final sequence. Earlier residentcache experiment preceded final signaturechange and is not final evidence. No new diagnostic images generated; tests retain JSON/native RAM/log evidence only.

Final frozen9regionSHA serial run: component,7565interrupt boundary injections with projectilephase enabled through7mappingstates, full16slotcapacity,128live-world ship damage cases, chosen controls/bothjoysticks,8shortshots+1beam, realdeath/respawn,116title states,snake,restarts3/8,loadererrors,all8boss700worldupdates, full8diskloads/ending/cache-only revisit55681refreshes. All8profiles eachcapture8shortshots+1beam over480refreshes. (level,player ticks,projectile phases,world updates) [(1, 157, 87, 28), (2, 115, 66, 43), (3, 149, 84, 30), (4, 184, 134, 15), (5, 155, 127, 9), (6, 147, 75, 30), (7, 129, 50, 32), (8, 164, 112, 27)]. MatchedL5r54player158->155, projectile127phases vs9worldupdates, normal gameplay input cadence retained closely with extra projectile work. Nativeactorinvulnerability/forcedvictories in boss/cache routes are diagnostic, not proof of successful unassisted play or physicalhardware. All72assetpages/TAPXOR/raw reconstruction/ownedranges/ZIP integrity pass. Stock64KBcart, originalarchives and referenceprojects unchanged. Hardware pending.

Deliverable build/fullgame/projectile_clock_r55/RType_TS2068_r55.zip SHA256 7784e1643248b8faf87f5c80b33ff28d1a0b1f3cff6c2a8fefe4ea6094ff000d. Replace entirematchingRTYPEfolder, RESET beforeRTFULL.TAP. docs/r55_projectile_clock.md. SeparateIRQphase is independently scheduled Z80work, not simultaneous CPUthreads.

Post-package reproducibility: rebuilt from scripts into build/diagnostics/projectile_clock_r55/repro; all9regions and gateway byte-identical to frozen release. ZIP hash unchanged.


## 119 - Stale organic-boss fragments around the ship, r56 (2026-11-04)

User reports sporadic L5organic-ball pieces around the player, cleaned only after delay. Reproduced by capturing a real L5native copy entry after100boss updates and comparing the native slow copy with an IRQ-moving player against a clean reference. Empty metadata0/3 cells still contain stale boss bitmap/attribute bytes; they are not valid background. R54exact-mask publication preserved pixels outside ship coverage in those retained cells. Marking them player-owned3 then caused the native8x8cell copier to publish the entire cell, revealing old boss pixels outside the ship. Previous tests bypassed the actual slow native copy and did not cover this empty-to-owned transition.

Newcache preparation zeros only unowned0/3 bytes in its existing10column x64raster patch, in both retained planes and backing. Top aligned to8rasterlines so newly marked character cells cannot copy unsanitized lines above/below the player. Occupied scene cells are preserved. Cleanup reuses exactclean OLD64byte underlay captured by lastpublication into WORLD instead of per-byte banked resampling; normal/moving/frozen cases pass. Newengine2423bytes vsr552427; onlyE400..ED7F changes acrossall9regions. Artwork, boss shaders/sizes, palette assets, playerphases/settings/keys/joysticks, timedplume/audio, independentprojectiles and cache/loader/gate code byte-identical to r55. Stock64KBROMunchanged.

Focused45cases neutral/eightdirections xfiveinterruptintervals: baseline695unexpectedpixel-bytechanges, fixed0. Audio/input/star callbacks stubbed to isolate copy composition, artificialIRQs never nest. Two cases lose one existing star byte each inside sweptshipcoverage, separately recorded, not claimed fixed; snapshotmetadata atthatstar is0. Initialfourright-moving timings compare exactly afterfix.112edge/finephase empty/mixedowner backingcases preserve23936ownedbytes and616448outsidepatchbytes, clean47744unownedbytes. Frozen full894player ticks,128real-varied live-world mutationcases, unchanged componentmean/max11346.274049217001/49928cycles. Full16slotprojectiles/nativeglyph/ECM/hitonce/staleactor/cleanup tests and7565IRQ-boundary injections retained.

Development diagnostics: initial manual-IRQ fixture hung because it could inject a second artificialIRQ before the first returned; fixed harness and stubbed audio/input. Native moving stars initially differed from no-IRQreference; isolated starcallback to measure copy defect. Broader matrix found two missing starbytes inside sweptcoverage; report distinguishes these from addedbossartifacts, rather than hiding differences or claiming full-frame identity. First mixed-cache generator used Buffer.from(arraylike,callback), which ignores callback and generated zeros; corrected to Array.from thenBuffer.from, assert nonzeroownedcoverage, and corrected inherited128case varied-data generator too. The prior r55test's actual data did not match its intendedrandom description; it still tested outside-mask bit changes, but not this ownership defect. Finalreports rerun on corrected fixtures.

Images: build/diagnostics/player_ghost_r56/ghost_before.png, ghost_after.png, ghost_comparison.png. Rendered directly from captured emulatorHOME bitmap/ECM after the same copy/rightmovement; comparison sheet crop/nearest-neighbourzoom visually inspected, not hardwarephotos or newlyauthoredgameart. Capturestate/home/dock0..7, reference.home.bin, baseline.home.bin, clean.home.bin, copy_comparison.json, copy_clean_comparison.json and logs retained. No userphotos/referenceprojects/sourcearchives changed.

Finalfrozen serialrun: cache/copy,projectile/IRQ/capacity,894playercomponent,128worldchanges,movement,chosencontrols/bothjoysticks,8shortshots+1beam,realdeath/respawn,title116,snake,restarts3/8,loaderfailures,all8boss700worldupdates, full8diskload/ending/cache-onlyrevisit56490refreshes. Seven of8inputprofiles8shortshots+1beam; L5unshifted7shortshots+1beam, one-frame-shift L5restores8+1. Dedicatedfunctional8presstestpasses; shorttapsremainworkloadsensitive. r55shift1/2/4/8all8shots, so do not claim this exact miss was reproduced in r55. No control/projectile bytechanges inr56; redraw cost shifts relativeIRQ timing. (level,playerticks,projectilephases,worldupdates) [(1, 165, 86, 28), (2, 114, 73, 43), (3, 146, 87, 30), (4, 181, 136, 15), (5, 155, 131, 9), (6, 153, 82, 28), (7, 132, 52, 32), (8, 165, 115, 27)]. Scripted boss/cache routes use invulnerability/forcedvictory for coverage, not successfulunassistedplay.72assetpages/XOR/rawreconstruction, strictoutside-enginebyteidentity andZIP integrity pass. Separate rebuildall9regions/playerengine byte-identical. Hardwarevalidationpending.

Deliverable build/fullgame/clean_player_r56/RType_TS2068_r56.zip SHA256 2649ed1ae8be771e9f832c1c3f764186409c24620544ee51aa937bef0193f386. ReplacefullmatchingRTYPEfolder, RESET beforeRTFULL.TAP; residentoldbankcode mustbe cleared. docs/r56_clean_player.md. Lesson: ownershipmetadata, not retainedpixelcontents, defines validscene; ECM8x1colour masks do not change native8x8dirty-copy granularity. Test the whole ownership/copy transition, and assert generated testdata actually spans occupied and empty states.


## 120 - Projectile ordering, IRQ re-entry and rapid-fire backlog, r57 (2026-11-04)

User reports one short projectile animating out of sequence, apparently like several projectiles, and rapid-fire input running ahead for several seconds. User explicitly corrects the initial pause/resume interpretation: genuinely out of sequence, L5 on PicoVideo. Exact backward single-shot display on that hardware has not been captured in emulation. Do not describe the report as merely delayed/resumed. Emulator framebuffer, raster and per-byte-paint traces were forward ordered; the release addresses independently verified unsafe re-entry/stale replay paths plus the separately reproduced pauses/backlog.

Observed native input scanning returning withIFF1enabled inside the IRQ. The handler has one saved rawbank/SP slot, so it cannot safely re-enter. Controlled second periodic pulse after EI-returning input scan: r56accepts1nestedIRQ and fails to restore originalcontext within100000instructions; r57masks SCLD source across entirehandler, blocks1secondpulse, returnscorrectly in1063instructions and restoresportFF2. Entryhelper08E2/exit0911use verifiedcommonFFgaps; FD20entrymirror/0971exitrebuilt, sourceunmasked underDI beforeoriginalbank/SP/regrestore. This proves an unsafe ordering/context bug, not the exact user's PicoVideo frame. Mode/source restoration alsochecked against each actualpreIRQmode in7565boundarycases, including legitimate mode0fallbackcases.

Projectile advances during backing preparation and hidden nativecopy, then repaints only its currentposition without an extra travelstep. Postcopy republish requires nativepool type andcoordinates to matchcachedslot; deliberatelycleared/reusedslotscannotresurrectoldpositions. Muzzle/ship exclusion applies tobothclockpaintandpostcopyrepaint. Privategateway nowpreserves callerF4 andalternateAF soE406cleanup cancall it frombank7, withrawmap temporarilyinAF'. Enginehelpers do not exchangeAF'. Renderer2431bytesE400..ED7E; projectile640bytesDOCK2:5880..5AFF/coldF100..F37F, stops exactlybeforeflippedL5cacheF380. Gateway96bytes94F9..9558; transitionreturnmovedto19FC. IRQ/private stacks andallreferenceart/bossgeometry/audio/controlbindingsretained. Source flags and mirror register contracts statically checked. Stock64KBROMunchanged.

Fire capture keeps onlyone latestrelease rather than4queuedshots. Short releases dispatch frombusyIRQ too, via the existingnativeallocator/soundqueue; blockedshortrelease expiresafter8capturepolls.20blockedtapunitcases neverexceed1pending andexpirewithoutreplay. Onephysicalrelease allocatesexactly1shot; chargedrelease survivesnativehandoff. Inactualrapidroute15pulses produced15normalshots,0beams; lastallocationatrefresh117beforeburstend119, queue0andnoallocationafterburst. Inputs canstillcoalesce underload; no universalcaptureguarantee claimed. Functional8release+1chargedbeam passes. Death clears pending flags. User's preferred8pixel travelstep remains; no slow-down multiplier added.

Baseline singleflight in actualslowworldcopyroute lasted238refreshes, withlongblankspans. Finalflight lasts54refreshes, nativeXreaches29, exactly1allocation, visiblefullglyphsamplesmonotonic and no duplicatefullglyph. Collision query bypass only in thisopen-flight diagnostic; scene sprites canoccludefullglyphmatches, so maxnativeposition isseparatefromfullyvisibleglyphsamples. L5single-shot test specificallychecksraster andallprojectilebytepaintpositions, oneallocation/0beams/noearlierpositionreplay andpaintreachesfaredge. R56originalbackwardeventnotreproduced, no hardwarefixproofclaimed. Direct21positionnativeglyph/ECMcomponent, hiddenadvance10..15/no-paint/resumeunchanged, stale-slot rejection, bank89+alternateAFpreservation, full16capacity/nativehitonce/staleactor tests pass.

Development: initialcodegrowingbeyondfixed2432/640bounds rejected byassembler; queue simplification recoveredspace. The first returning-bank prototype read aHOMEflagwhileDOCK2mapped; corrected beforetests to save originalmap inpreservedAF'. Bulkpostcopydraw initiallyneededthe sameshipexclusion asnormalclock; centralized it. IRQunitinitiallyclassifiedIRQ byIFF1andreportednone; actualSP5BAEprovedall8allocationswerewithinIRQdespiteIFF1true, leadingtore-entryinvestigationandsourceguard. Pulseharness originallyinjected overduepulsesback-to-back afterlongIRQs and starvedmain; it nowdropsmissedpulses. Modecheck initiallyassumedalwaysFF2; nativeunownedcorefallback legitimatelyendsmode0, soassertactualentrymodeatIRQreturn. Fullglyphfaredgeassert wasinappropriatewithoccludingactualscenesprites; nativeXextent andvisibleglyphordercheckedseparately, pureemptycomponentchecksall21visiblepositions. Focusedplayercomponentsstubonlybolt-republish; nativecopyregression exercisesrealnestedbankcall. No newdiagnosticPNG/artwork generated. JSON/raster/paint/pulse logs underbuild/diagnostics/projectile_sequence_r57. R56diagnosticbaseline inputs preserved; newcopyresults writtenseparately.

Finalfrozenserialrun: nestedIRQ,L5rasterorder,queue,continuous,flight,rapidfire,112mixedbackingcache,45nativecopycases0unwantedbytes,full16projectiles,7565IRQboundaries,894playercomponent,128realvariedliveworldcases,movement,chosenkeys/bothnativejoysticks,chargedfire,realdeath/respawn,title116,snake,restarts3/8,4loaderfailures,all8boss700worldupdates,full8diskloads/ending/cache-onlyrevisit59250refreshes. Boss/cache diagnostic routes use invulnerability/forcedvictories. All8inputprofiles (level,shortshots,beams,playerticks,projectilephases,worldupdates): [(1, 8, 1, 152, 119, 26), (2, 8, 1, 112, 147, 40), (3, 8, 1, 150, 125, 28), (4, 8, 1, 178, 168, 14), (5, 8, 1, 149, 150, 9), (6, 8, 1, 151, 116, 27), (7, 8, 1, 128, 95, 29), (8, 8, 1, 159, 137, 25)]. Actualworkload-dependentcounts retained, not claimed universalFPS/inputcapture.72assetpages/TAPXOR/rawreconstruction/strictownedranges/ZIP checked; graphics and phase/flip caches unchanged. Separatebuilder reproduction recorded. PicoVideo hardware confirmationpending.

Deliverable build/fullgame/shot_sequence_r57/RType_TS2068_r57.zip SHA256 78163450c7385abac3fc844073254313aa9fbb0e4264e919eb3f8823986b96ce. ReplacewholeRTYPEfolder, RESET beforeRTFULL.TAP. docs/r57_shot_sequence.md. Futurelesson: test re-entry from routines thatexecuteEI, not onlysingle-IRQ boundarypreservation; testactuallyrendered frames/currentnativegeneration aswellascoordinates, and bound input freshness rather than queuingreplay.


## 121 - L5 actor-local two-pixel phase trial, r58 (2026-11-05)

User requests implementing preshifted graphics/2px L5movement per existing boss update. Separate playable trial RType_TS2068_r58_L5_preshift_trial.zip, SHA256 bebe1f0acb9e0fb89ff769aa7f8f91e82271baa6ab9ca0019330d9ec4e94b387. Standardr57 andstock64KBcart unchanged. Original24pxspheres/80pxcore;25parts use0/2/4/6horizontal phases plus raster-row vertical offsets, bothflips, legal8x1pairs/nonblackcoverage. Ordinary8pxtravel spreadinto2px/axis eachworldupdate; larger scripted relocations retained. Native target/animation/attack scripts and chosenkeys/dualjoysticks retained. EnemyAI/collision remainscoarse; not independentbossIRQclock.

7152packedbytes expands9344rawphasebytes duringloading (2374061isolatedcycles), no bossentrance preparation. ReusesDOCK1paletteRAM andalreadycopiedDOCK6source shadow insideexisting512KB; exactprefix reconstruction/native-shadow/tail restore beforecachedbankleave. CodeDC50afterD87Ccopylimit andDBD0..DC50savedtail, cachehelper8C00, stateE200..E400. IRQdecoderusesDOCK2privatestack, distinctfromHOMEplayerstack. Fullmemorycontracts in docs/r58_l5_preshift.md.

Measured700worldupdate route26295r57->36061r58displayrefreshes (37.14%moreelapsed, boot/entranceincluded). Thus NOTa speedup; trialonly. Final480refresh held-input:141player ticks/138projectilephases/6worldupdates/8shortshots+1beam; separate stationarysingle-shot8worldupdates. Rapid15taps->14shots/noafter-releasebacklog. No universalFPS/captureclaim. Large opportunities remain incompiledphasecellplans/repeatedcoordinate/emptywork.

Final14frozenserialchecks:256phase/orientationnativepixelcases;256morecaseswith8IM2injections at5F/1F; exactcacheexpand/restore;700L5worldupdates/25actors/16075motionsamplesand2pxordinarytravelassertions;chosenkeys/bothjoysticks,8release+1beam,realdeath/respawn,title116,snake,4loaderfailures,single-shotorder,rapidqueueexpiry. Actualboss->gameover->cachedboss15890refreshes, onlyRTBOOT/LEVEL05mounted. Full8loads/ending/cache-onlyrevisit59431refreshes/128blocks/37221code+reverseaudits/15workspacechecks. Otherbosses1/2/3/4/6tested200updates,7/8tested700(laterarrival). Invulnerable/forcedvictorydiagnostics are notunassistedplayproof.72TAPpages/hash/XOR/rawreconstruction/strictchangedbytecontracts/ZIP/repro15filespass. Player/projectile/audio/IRQbank7afterE400byteidenticalr57. Hardware/PicoVideopending.

Developmentfailedcandidates/tests: physicalbankownershipconfusion rejected; slowin-frameunpack movedtoloading; emptycellI8Fearlyreturnrepaired; sharedcopyhelpersrelinked; stationarybranchzero bugcaughtbylivecoordinates; banked8CFDfalsehookfixed; restoreEIloadercorruptionfixed; testIRQIM0->actualIM2; L7probeextended; branchrangebuildfailure/staleimageprobeexcluded; previewPythonsyntaxfixed. r57diagnosticbaseline rewrittenduringinitialtrace restoredbyfull8boss700probe; releasearchivehashunchanged. No sourceZIP/reference/skillfilesmodified.

Images: build/diagnostics/l5_preshift_r58/comparison.png,baseline.png,candidate.png,baseline.gif,candidate.gif andindex.html. SixteennativeHOME captures perbuild; GIFusesemulatedupdatespacing andloops excerpt. ComparisonPNGvisuallyinspected, nothardwarephotos. All detailedoutcomes/evidencelimits in docs/r58_l5_preshift.md.

Deliverable build/fullgame/l5_preshift_r58/RType_TS2068_r58_L5_preshift_trial.zip. CopyfullRTYPEfolder,reset,loadRTFULL.TAP;select5,thenB-release-Bingame. Keepseparatefromr57forcomparison.


## 122. r59 - repair L5 global effects and prepare boss cell plans (2026-11-05)

User reports corrupt firing sparks and player explosions in r58 and requests optimization. Proven root cause: expanded phase cache DOCK1 2400..3FDF overwrites global colour IDs still read by native 1561. Bitmap bytes are intact. Preserve 617 nonempty global tags in a collision-checked 715-byte table DOCK7 E000..E2CA; ROM0 0040 lookup installed only in L5. Actor state E300..E33F/cache flag E3F0 disjoint; source-tail backup DF00 and dictionaries DF80/DF90/tail DFB0. Source restoration normalizes mutable cell plans before cached leave/revisit.

Prepared native variable-length cells once per actor; painter reads raw pointer/row mask. Early clipping and verified opaque foreground rejection avoids preparing invisible cells. Owner0/3 retained bytes cannot suppress source. Foreground blending retained. Private DOCK2 stack and HOME/DOCK2 vectors, I8F during preparation; lower metadata read bank4-off protected by DI. Original 24px spheres,80px core,25 parts,2px movement unchanged. Shared bank7 engines after E400 unchanged; boot and all seven other level images exactly r58. Stock64KB/reference/source ZIP/skill unchanged.

Frozen16 checks PASS: nativeFX2568 cases,r58 mismatches840,r59zero againstr57; all111 globaldescriptors/basicflips plus expanded explosions/sparks foreground/flash/clips. Component256 phases/flips+96foreground; independentclipping768+288foreground at right/bottom,left/topwrap,lower-metadata boundary. All legal normalblack ECM, silhouette/referencepixels, exact cache expansion/restoration/table immutability.16 realIM2injections pass (prepare+paint;5F/09/1F). Init2374061cycles. Actual700L5updates/25actor histories <=2pxordinarymotion pass. Customchosenkeys/nativebothjoysticks,chargedfire,title116states bitmap+ECM exact,L1snake,error03/E0/E2/E3,rapidfire,singleflight,realdeath/respawn pass. Actualdeath3931/respawn4324 complete4329; drawnIDs75,82..87,94,95,97,98. Actualboss->gameover->cachedboss15670refreshes,7460code/reversal checks. Full8/end/secondcircuit59443refreshes,37258code/reversal checks,15workspace checks,all8residentrevisitedwithoutdisk pass. 72TAPpages flags/XOR/reconstruction,strictownedbytechanges,all9frozenregionhashes,ZIPCRC pass. Separate clean rebuild matches18helper/asset/region files.

Measured emulator changes vsr58: componentmean includingprepare204098.17->167701.98cycles (17.8%less); heldinput480refreshes player141->173(+22.7%),projectiles138->172(+24.6%),same8shots+1beam.700bossroute36061->35862refreshes (only0.55%less);r57=26295,so stillsloweroverallthanr57. Stationarysingleorder1shot/0beam,173projectilephases/9worldupdates; rapid15requested/14captured,queue0,nolateshots. DoNOTclaimuniversalinputcapture,hardwareFPS ornewbossclock. This candidate mainlyimprovesinterruptibleinputopportunities. Hardwarepending.

Diagnostics build/diagnostics/l5_effects_fast_r59/index.html and effects_comparison.png: isolated actualnative retainedbitmap+ECM (r57reference/r58bad/r59repair),visuallyinspected;red/yellowexplosions/correctsparks restored,notfullgame/hardwarephotos. Raw effect_ID_0/1/2.bin cover75,76,78,81,82,84,87,94,95,97,99..106;earlier40..43 captures were titleletters,excludedfromfinalpreview. Broadallglobalchecks alreadycoveredexplosions,butfocusedlabels correctedusing75DDsequence andactualdeathtrace. InitialprepareIRQcandidate wrongI84withbank4visible rejected, fixedI8F/vectors. Earlyplanwithoutocclusion had slightlyfastertotalroute but fewerheldinputticks; finalcandidate measuredexplicitly. Diagnostic inspection helper failed on list-shapedJSON, no build/test effect. Intermediate results are not final performance claims.

Scripts build_l5_effects_fast.py,run_l5_effects_fast_final.py,verify_l5_effects_fast_*.mjs,profile_l5_effects_fast.mjs,render_l5_effects_fast_fx.py,finalize_l5_effects_fast.py. Detailed docs/r59_l5_effects_fast.md. Deliverable build/fullgame/l5_effects_fast_r59/RType_TS2068_r59.zip SHA256 1e45543d1ed10dd4d4e2e3b38f00cbd7603e79dcd21b8e315cb3f3e04a5ba5b4. Previousr57/r58archivehashesverifiedunchanged. ReplacecompleteRTYPEfolder,reset,loadRTFULL.TAP;select5beforestart,B-release-Bingame;normalkeyselection. Keepseparatefromr57standard; r59supersedesr58trialforFXrepair.


## 123. r60 candidate work in progress (2026-11-05)

User requests other moving bosses at2px, fewerL5spheres, arcade minorenemies/morewalkerframes. No r60release yet; r59 archive retained unchanged. Current expanded-memory candidate includes generic actor phases,12instead24L5spheres,4arcade largewalker poses atnative40x40 andsmallwalker ECM conversions. OriginalsourceZIPs/referenceprojects/stock64KB unchanged. Assetpreview build/graphics/enemy_upgrades_r60/comparison.png visuallyinspected: fourlargewalkingposes,5smallwalkerframes; firingposes/insectcandidates rejected. Assetpreview isnotgameplay/hardware evidence.

Rejected terrain-bank cache/code layout caused nativewriter9CB9 to read code as terrain andoverwriteHOME FDA5/FDAE/FDF7. Genericbank4 nowpreserved entirely; code movedbank5prefix/6tail, immutablephasesbank1, rawcachebank6C000..D800. NativeI84 cannotserveforeignmappingIRQ; dedicatedI D8 vector5B5B->FD20 needed. Coldboot fullhigh-tail copy differsfromcachedcopy, needsnativeworkspace/tail restoration. Bank7FD08 isreversaldata, notHOMEpublisher. Separate nativehelper relocation/callpatches remain underregression. Earlierstale/partialbuildprobes andnoisydebugrunterminatedwithCtrl-C areexcludedfromfinalclaims.

First coherent sustainedgame test passedL1/2/3;L4original50000refreshbound reached593updates, timeoutnotproofhang. Extended90000bound passesL4at63794refreshes/700bossupdates; tooexpensive forspeedupclaim. L1=14983,L2=14118,L3=15551,L5=35296for700bossupdates (plus29prejumpupdates). L2r59matched13348, soL2candidate5.8%slower. L5r59=35862, candidateonly1.6%lesselapsed despitehalvedspherecount; nohardwareFPSclaim. L6thenfailed2pxassert withID19 X216->224. Animation-frame keys exhaust/reset actorhistories; sourcechanged touseactor-onlyhistory exceptL4multipartkeys, notyetrebuilt/validated.

Frozen oldcandidate independentcomponenttest2084casesPASS, inclnormalblackECM andpixelreference/allphases/flips/source/immutablebank1/terrainbank4restoration. RealIM2injectioncheckPASS. Remainingchecks running; final_checks.jsoncurrentlypartial. Nativecaptureimages/script atbuild/diagnostics/boss_motion_r60 andscripts/render_boss_motion_r60.py; onlycompletedlevelcaptures rendered,shortemulated16world-updateloops,notphysicalperformance. Failedviewofnot-yet-renderedL4.png hadnoeffect. docs/r60_boss_motion.md recordscandidateonly. DoNOTpackageuntilrebuiltactorhistoryfix/fullfrozenchecks/reproducibility/contracts/actualframeinspectionpass.


r60 candidate follow-up: actor-only histories (except L4multipart IDs) fix L6frame-reset jumps; all8stages nowcomplete700bossupdates with15875movement samples. L5firstreduction targetedwrong E641homing/SFXtable andwasrejectedbyactor-countassert; reverted entirely. Actualeventstreamcolumn73/event35filteredalternating24->12,coreevent24andotherrecordsretained. Correctednativeactorcount13. L5route25606refreshesvsr5935862 (-28.6%elapsed). L4still63800andrequiresoptimization. L1/2/3/6/7/8=14983/14118/15539/15106/11560/13584approximately;readexactboss_levelJSONforcurrentL1. Fixed-windowheld480:player163/projectiles158 vsr59173/172;8shots+1beam.NooverallIRQ/FPSclaim.

Currentbinarypixelchecks2084,realIM2cases100/200injections,clipping1164PASS. NativeFXinitialfailurewasisolatedfixturemissinggenericinstall_motion (traceexecutedoldbank5code,HLbecame95A5),notproofruntimebankreturnfault. Fixturecorrected;all8*2568=20544nativeeffectcasesmatchr57. Shared1FF7keptnative19mapping;genericentryexplicit29. OrdinaryL1walkertracefiltercorrectedtoexcludeunrelatedglobalFXcalls:4largeposes201..204andall5smallIDs21..25 exercised451draws,2479worldupdates/44194refreshes. Controls/customkeys/bothjoysticks,charged8+1beam,actualdeath/respawn,title116exactstates,snake6captures,errorcases,rapid14/15shortpresses/noafterburst,ordered1shotPASS. Single-orderclonedtestinitiallywroteitsJSONunder r59diagnostics;copiedcurrentresulttor60andcorrectedoutputpaths. r59ZIPhashunchanged. Separate-directoryrebuildmatches32generatedbinaries.

Restarttestfirstreplaycompletedbutextrareadinessassert>8failedbecause500kdelaywasconsumedbynewstartupwork;actualrequired8primingreadssatisfied. A32readfixtureexperiment violatesdevice8readcontract andcorrectlytrippedexternal-writeguard;reverted. Finaltestchecks>=8withdelayedcommandreplies,retains700updatesbefore/aftergameover,and180000refreshboundforL4. Restart/progressionstillrunning. Binaryunchangedsincecorrectedspawnstream. No r60ZIPyet. All8nativecapturePNG/GIFsrenderedunderbuild/diagnostics/boss_motion_r60,actual16completedworldupdates,emulatedtimingsnotphysicalFPS. L4/L6/L5imagesandL5r59endsnapshotvisuallyinspected;coloursretainexistingr59assets. Asset4poseGIFinbuild/graphics/enemy_upgrades_r60/walker_four_poses.gif,notgameplaytiming. Walker_gameplay.png actualordinaryroutecaptured.


r60 FINAL PACKAGED: build/fullgame/boss_motion_r60/RType_TS2068_r60.zip SHA256458a82915addb4ad98ebc8fe1558713807037fc1da32ecc239304cae56a2cb60.17actualtestreports consolidated withfrozen9regionhashcheck;72TAPpages XOR/flags/reconstruction,ZIPCRC,terrainbank4byteidentitygenericstages,sharedE400..FFFFengines/reversals intactexceptFBA7publishergate,RTFULLloaderunchanged,32fileseparaterebuildPASS. Finalnativeall_bosses.pngcontactsheet andall8PNG/GIFsrendered/visuallyinspected. Initial100-updateexcerptsdo notalwaysshowfullbossarrival. Ordinarywalker_gameplay.png andasset4poseGIFseparatelylabelled.

All7selectedboss->gameover->cachedboss routes700updatesbefore/afterPASS (2..8),no rereads,allcode/reversalaudits;L4total119901refreshes,L5total47156. Full8/end/secondcircuit60876refreshesPASS,all8valid/revisitedwithoutdisk,36931code/reversalchecks,15workspacechecks;forcedvictoryloadingtestnotunassistedplaythrough. Delayedselectorsreach101712primingreads onstressroutes;firstL2routeonly8validprotocolreads. Final L1route14985refreshes,othersabove. Candidatehas12actualspheres/core13 and4genuinearcadewalkerposes;notallremainingminorartconverted. Finaldocs/r60_boss_motion.md/README/validation_summary documentL4slowpath,nativecollisioncells,noindependentbossclock,hardwarepending. r59ZIPhashverifiedunchanged;stock64KB/sourceZIP/referenceprojectsuntouched.


## 124. Small walker comparison and corrected pose proposal (2026-11-05)

User sayssmallwalkersdonotlookmoving,requestscomparisonwithpreviousgame. ReadPROJECT_STATE/TEST_HISTORY. Actualr60ordinarygametrace confirmsnativewalk21,22,22,23,23,22,22,21;24/25aregunraisingposes. Comparisondecodesactualr59nativegraphics,loadsactualr60phaseinputarrays. r60incorrectlyassigneduprightarcade1602to23,andduplicate1604to24/25;transparent32x32paddingalsoshrankwalkersunnecessarily. Previousnative21/23bothsidewayslegposes,22alternate;24angledgun/25uprightdistinct. Causeisbadassetselection,notmissingnativeanimationupdates.

Newpreviewonly: arcade1570/1572/1574walk,1600/1602raisinggun. Sharedwalkingcrop(0,7,32,32),sameaspect-fit/baselinebeforeSierraLite/HSV2/gamma1.8;normalblack/legal8x1pairsverified. All5posesunique,3walklegbandsdiffer. No playableimage/ZIPchanged;needsintegration/gameplayverificationbeforeclaimingfixed. ComparisonPNGprevious/r60/proposal three_way.png,actualarcade32pxposeinventoryarcade_pose_inventory.png,old/new/proposedwalkGIFsuseidenticalillustrative360msperpose,notmeasuredFPS. Assetsunderbuild/graphics/small_walker_comparison,HTMLindexwithprovenance/limits. Originalr60previewindexlinkscomparison. Initialcomparison.pngandarcadeinventoryvisuallyinspected;three_way.pnginspectedbeforefinalshared-croprefinement. Scriptsbuild/graphics/compare_small_walkers.pyandcomparison/make_sequences.py/make_proposal.py. Records/sourceZIPs/referenceprojectsandstock64KBunchanged.


## 125. Small walker graphic-art highlight alternatives (2026-11-05)

User requestsstrongerhighlights/shadingoncorrectedarcade-derivedsmallwalkers. Readstate/history. Generated3offlinepixel-artmaterialvariantsacross5correctedposes:steel/cyanrimlights,deepbluearmour,andwarmmetalaccents. Preserveexistingwhitebarrelribs/redlights/bluejoints;enhanceexposededges,lower-faceshadowsandlegstruts. Weightedofflinepalettepairselection,mandatoryblackintransparentcells,all15frameslegalnormal8x1pairs/nohighattributes/transparentsilhouettepreserved. Sharedcorrectedposegeometryandwalkcropretained. Initialvariantflattenedwhiteribsandstripedbluebody;visuallyrejected/refinedtopreserveoriginalfinefeaturesanduseboundaryshadowsinstead. FinalcomparisonPNGvisuallyinspected. PreviewGIFs360ms/poseillustrative,notgameFPS;noROM/ZIPchangeorhardwaretest. build/graphics/small_walker_highlights/index.html/comparison.png/steel.gif/blue.gif/warm.gif/validation.json,scriptbuild/graphics/make_walker_highlights.py. Previouscomparisonpagelinksnewchoices.


## 126. r61 responsive loading, blue walkers, runtime level override / preload-all WIP (2026-11-05)

User approvesBbluearmour;asksimmediatelogo/startscreen,early1..8selection,interruptiblelevel1loading,bigLoadingn-of-k;steersLthen1..8duringgame,andShift-Lpreloadall. Newcandidatebuild/fullgame/startup_r61,NOreleaseZIPyet. r60preserved. Readstate/historybeforechanges. scripts/build_responsive_startup_r61.py reusesr60builderwithoptionalART_OVERRIDES (defaultunchanged)forblue21..25;3walkposes1570/72/74+distinctraise1600/02,sharedcrop/nativegeometry.

Coldloaderembedsstandard-screenapprovedR-TYPElogo(bitmap/deltaattributecolumnsweep),large16pxLEVELn/LOADING/000OF070...;normalblack. Immediate1..8pollingduringdataandprotocolsettles;latestchoicewinsaftercurrent1KBheader/datapairdrained,thenremountSTARTnn.TAP. 48pieces=immutablebanks0/1/4/5/6/7,plusRTCORE22pieces=sharednative8000..BFFF,packedDOCK3workspace,highFC50tail,commonC000..C4AEprefix. All64physical1KBfragmentsreadback/summed/finalaliascheckedbeforehandoff. RuntimeLEVELnn.TAP8-pageformatretained;bigLoading001OF008betweenlevels. Startupdatausesfast8192-iterationguardalreadyusedbyoriginalpreloader;mount/selectretain65536guard. WaitloopnowpollsUIevery~2048iterationswithouttouchingthirdpartytransport. Finalresidentsetupremainscancellableuntilblackhandoff. Relativecwdpreserved.

Directcoldhandoffrecreatesnativephasewarmup,workspace/CPUregs,IRQmirrorFB00..FBC0andmapping9 (mapping1wrongcausednativecodeexecutionfromloader);nativecoldkeyboardC291=FB7E. SharedtailfromBOOTbackupFC50..FFFF. InitialalternatebouncebufferC000duringfinalverifyoverwrotepackedworkspace:fixedcoldbank5bounce8000,workerbounceC000. FD4C/FD4DareNOTfreehotkeybytes:adjacentmusicstackFD50;zeroingremoved (actualprimarylaterfaultwasworkspacebounce). HotkeystateFDA5andjobFDA7..FDAFborrowunusedoriginalpopupbytes,allcallsredirectedlow8since r60. Blankprimarybeforehandoff;firstmode41secondaryattrs0duringcopies. UIerror/stepmovedbelowlargeprogress. Finalcurrentloader6115bytesendsbelow7800;noassemblerwarnings.

Mainloopspare8656NOP3nowCALL00DB,originalBpreview/nativeinput865Fretained. GenericdispatcherDI/mapsbank1CALL3A00/restores9/EI/RET. L-then1..8latchusesnativeselect_start;userbindingsstillnative. L5bank1fullphasecachecannotfitcode,sohotkeysourceinunusedDOCK5A000prefix,dispatcher copiesHOME7B00/callswithbank5off. SharedcoldC000prefixseparateCOREmakesitcorrect;normalcachedcopyalreadybeginsA4AE. All8coldlevels passed151updatesbeforelatesthotkeypolish;latesthotkeybuildcold1/5passed. L3actualdiskjump/cachedL1returnpassed,noLEVEL01read;testinitiallysentreturnduringnativearrivalsequence,correctedwaitforactualmainloopupdates.

Shift-L mainlooponly;alreadyVALIDFF=noop. Snapshot48KBHOMEinto3noncurrent/nonresidentregionsbanks2/3;sourceassetpages2/3neverpreloaded,soall512KBusedwithoutdiscardingresidentloader/currentgame. WORKERloadedRTPRELD.TAPat8000,loadsSTARTnnonlymissingvalidbits,perfragment/finalverify,progressglobalmissing*48(usually336),updatesVALID. Restoreallcurrentbanksuntouched,HOMEbitmap/ECM/common/highnative,AF/BC/DE/HL/IX/IY+alternates/SP/video,thencontinueexactoldmainloopandcachedjump. Initialrestore-driverlinkemptydueorigin-shadowlambda:fixedandassertnonempty. Originalrestoreleft5E00scratchandthenexecutedHOME7CtailaftermappingDOCK3,bothfixed. Snapshotbootstrapnow7F00(unseen),finalrestoretail7C00,restores5E..5FFFvia7E512bounceandfixedlow0E11gateway. SnapshotprivateSP5CC0avoidsclobberingsavedFFECregisterstack. CallerHOME8100scratchusedasexistingnativegatewaydoes. AllsourceZIP/referenceprojects/64KBstockunchanged.

ExactpreloadresumeactualtestsPASSL1andL5:all8currentDOCKbanksbyteexact,bitmap4000..57FF/ECM6000..77FF/common8000..BFFF/highC000..FFFF(exceptVALID)match,registers+alternates+SP/videoequal,native5E..5FFFrestored;50+worldupdatescontinuethenL3cachedjumpwithnodisk. L1snapshot2968/resume11688/finish12275(simdisplayrefreshes),L5snapshot3405/resume12125/finish13071beforefinalUIpolish. Theseareemulatornotphysicaltimes. Noopallresidentimplementednotyetdedicatedtested. Sourcefiles src/responsive_startup.asm,level_hotkeys_r61.asm,preload_snapshot_r61.asm,preload_restore_r61.asm,preload_worker_r61.asm;helpersbuild_preload_helpers_r61.py;fixtureboss_motion_fixture_r61.mjs;verify_direct_start_r61,verify_level_override_r61,verify_preload_all_r61. Remaining:currentfrozenall8cold,midpage/core/verify/final-selectioncancellation,delay/error/alias/noop/controls/FX/components/death/restarts/progression,UIvisuals,repro/contracts/package/docs. NeedaddRAM/BIN/DCKstaticwhereapplicable,diskonlyfeatures;donotclaimnew64KBcartridge.


r61 level-jump hardware feedback follow-up (2026-11-05): User reports first jump works, later jumps corrupt, not specific to L7, using startup_r61. Proven control-flow bug: hot jump returned to 8659 in old world update; replace saved continuation with 8640 (ECM init, 8721 terrain/actor reset, 8BAE ship setup). Actual route 1->7->3->7->5->7->7->2->7 passes, each initialization/reset executes; last visit forcibly clears L7 valid bit and correctly remounts LEVEL07. Earlier cached L7 returns have no disk. Captures jump_0..7 HOME / repeated_jumps.png inspected (actual emulator gameplay, not hardware).

Combined Shift-L/resume/cached-jump found second native-lifetime bug: C496 CALL FDAA, an interior popup entry, escaped prior FDA5-only relocation. Snapshot itself was exact; later execution of job bytes produced bank0:161B write (INC D->0), traced through C496->FDAA. Redirect boot/all8 source A496 to CALL000D, matching relocated popup interior. Conditional/unconditional CALL/JP scan into FDA5..FDE8 now empty across executable ranges. r60 release unchanged. Completion flags already set only after final readback/alias pass in cold/runtime/preload paths; forced invalid flag regression confirms reload. Current loader6137<6144, HOME handler1008<=1024. Full current combined checks still running; no final release claim yet. One no-op test was stopped because it failed to release L between Shift-L and next L command; corrected fixture adds 90 released refreshes, binaries unchanged. Earlier failed partial packager generator had no output/release effect.


r61 FINAL PACKAGED after level-jump repair: build/fullgame/startup_r61/RType_TS2068_r61.zip SHA256 aa4a392c2f527181fe8fb784a780410ce87d69f4515e3fbee77213953ff84ae1. Eight frozen consolidated checks PASS: repeated fresh/cached/same-level/L5 jumps + forced invalid L7 reload; Shift-L exact snapshot/resume from L1 and L5 + all-resident no-op + cached jump; six startup cancellation phases; checksum/alias/timeout/missing-file failures; custom-key/both-joystick controls; ordinary walker451draws/2479updates/all5small+4largeposes; all8 nativeFX20544cases. L1preloadresume11687/finish12503, L5resume12124/finish13313 simulatedrefreshes; not physical timings. No mutation of frozen9regions/launcher/allTAPs during checks. Separate rebuild297buildproducts byte-identical. All8LEVEL64KB andSTART48x1KB payloads/headerflags/XOR reconstructed, CORE22pieces,worker8KB,loader6137<6144,homehandler<=1024,ZIPCRC verified. Native popup CALL/JP scan passes after explicit instruction-boundary exclusions L2D55B(AND FC operand) and L6C732(JP E6DC operand). r60ZIPhashunchanged.

Actual startup ui_20/100/500.home.bin rendered to matching PNGs; ui_500.home.png inspected (logo, LEVEL1, largeprogress); repeated_jumps.png actual post-jump gameplay contact sheet inspected. They are emulator captures, not hardware or new FPS measurements. Full boss-engine suite is inherited from r60 and not rerun as a new performance sweep; current coverage explicitly listed above. Docs/r61_responsive_loading.md,docs/r61_readme.txt,generatedvalidation_summary.json. Reset and replace COMPLETE RTYPE folder before RTFULL.TAP; omit unusedRTBOOTfromZIP. User-facing controls L-release-number,Shift-L,early1..8,M,B-release-B,normalkeydefinitions. Stock64KB/referenceprojectsunchanged; physical confirmation of the reported glitch fix pending.


## 127. r62 Force / preload feedback work (2026-11-05)

User reports L3 glitches hugging bottom terrain, uncollectable/nonfollowing Force objects with visual glitches, Shift-L late audio cutoff/UI, and native-looking L6 art. Read state/history. Controlled native95F6 docking probe: unchanged native routine stays detached without player tags and docks when ID3 is stamped. Pixel integration r47 removed9559's CALL99FE draw, also losing reliable logical player tags. New HOME61byte FDC3 helper aftergatewayFB98 and before9559 marks original4celllogicalfootprint only in empty cells; leaves pixel engines unchanged. Actual controlled-object gameplay tests dock/detach/recall/pickup-upgrade onL1/3/5/6 pass. Testfixture initially used91F2RET alone and left5BC4deathflag latched, suppressingnativeactions; corrected fixture clearsit atmainstep. This isdiagnosticinvulnerability, notgamepatch. PickupsuccessobservedbyForcepowerincrement; doesnotrequireobjectslotremainemptyafterpossible immediate reuse.

ImmediateShiftL: AY8..10 save/zero atrequestacceptance, beeperlow, attribute-onlyLOADING screen beforeMEMDOCKguards; bitmap/ECMuntouched. FullUI aftersnapshot. Genericfeedback3E00 and L5A400..A43E separatefromhotkeyimage; homehot1024bytesends7F00exclusive. Standardattributes5800..5AFF aredeliberatelywaitingUI scratch. Native6thdefinedkeyretained; defaultSpace.

Rejected firsthelperplacement DOCK7E350 overlapped liveboss descriptor table; sustainedL3guardstoppedcompositor atA331withmap6F,DE0101/write0101 after696updates. UnknownglobalID136 inearlierextendedForceprobealsobelongsrejectedtrial. Bothare NOT proofreproducinguser'sr61glitch. RelocatedhelpertoHOMEFDC3..FDFF instead; bank7table/history/palette/player/projectilebytes byteexactr61 exceptFB98continuation. Staticlifetimegatefoundold counted-delayentryFDEB stillcalled (interiorofFDE9). Redirect5commoncallers+C059+4boothightailcallers to0002,preserveB. FDE9already0000,FDAA000D,FDEF/FDF0/FDF8relocated. Rawconditionalbytepatternsproducedoperand/datafalsepositives; finalunconditionalCALL/JPscanplusactualpartialnative-disassemblycallers isbounded, notexhaustiveproof.

Preliminarycorrectlayout9checkrun beforefinaldelayentry/beeperpolish passedForce4levels,preloadL1/L5exactresume/noop/cachejump,8repeatjumps,controls,actualdeath/respawn,20544FX,andordinaryL3bottom2000updates/48675refreshes. Capturesy147/145/152/148/152/139/144/133/133,200..1800updates. Finalfrozenrerununderway; noZIPyet. Immediatefeedbackcapturespreload_immediate_L1/L5.png inspected; LOADINGuses3x5blockletters, actualstandardvideoemulatedcapture. L3_bottom_captures.png actualcompletedworldcapturecontactsheet inspected; noexacthardwareglitchidentified. NoBRIGHT+blackpairs incheckedL3captures400/1000/1800.

L6inventoryconfirms13nativeposes5..17 (fourclawedcreatureposes,fiveflyingheads,fourwallturrets); boss18..33previouslyconverted. Generatedbuild/graphics/l6_remaining_r62/remaining.png,arcade_inventory.png,alternatives.png,index.html,manifest.json; imagesvisuallyinspected. Genuinecapturedarcadecodes2758/2768/2772/2774,2850/2852/2854/2864,324/340/336; aspectfitnative24x24/16x32 thenSierraLiteHSV2gamma1.8/2.4. Mappingsproposed/awaituserreview, noartinstalled. UseraskedA/B/source-revisit viaasync; noanswerasofrecord. Scriptpreview_l6_minor_r62.py. Existingr61ZIPpreserved;stock64KB/referenceprojectsunchanged.


r62 FINAL PACKAGED: build/fullgame/force_loading_r62/RType_TS2068_r62.zip SHA256 e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574. Nine finalfrozenchecksPASS: Forcecontrolledpods/pickupsdock-detach-recall-upgradeL1/3/5/6; ShiftL L1/L5exactbitmap/ECM/common/high/native-scratch/activebanks/registers/SP/videoresume+allresidentnoop+cachedjump; repeatedfresh/cached/samelevel/forcedinvalidL7jumps; customkeyboard/bothjoysticks; realdeath/respawn; nativeFX20544casesall8; ordinarybottomL3 2000worldupdates/45279simulatedrefresheswithfiring andexecutable/sourceguards; title116exactbitmap/ECMstates/1846refreshes. Invulnerableroutes andcontrolledspawnfixturesareexplicitdiagnostics, notunassistedplaythroughs. CurrentnativeForcepowerupstestsuseupgradecounter ratherthandemandtheobjectslotremainemptyafterpossible reuse. No claimedL3hardwareglitchfix.

FinalShiftL acceptance-to-mute 259/344cycles L1/L5; LOADING 27541/27559cycles. Beeperalsooffatacceptance. All3AYvolumessaved/restored; actualtimingishardwareunconfirmedandonlystartswhenthe mainloopacceptskey. DetailedUIstillfollowslongsafesnapshotguards. Immediatepreload_immediate_L1/L5.png and L3_bottom_captures.png renderedfromfinalHOMEcaptures; earlieridenticalmessageandbottomcontactsheetinspected. Sourcebitmap/ECMuntouched;standardattrs5800..5AFFintentionalwaitingUI scratch. NativeForcehelper61bytes HOMEFDC3..FDFF, gatewayFB98; boss tables/histories/playerprojectile/nativeFXbytesE000..FB97/FB9B..FFFFstrictlybyteexactr61. Finalhomehot1024<=1024/loader6137<6144,feedbackgeneric3E00/L5A400..A43E, prefix/sourceboundariesasserted.

Separatecleanrebuild300productsidentical. EightLEVEL8x8KB+START48x1KB payload/flags/XORreconstruction,CORE22pieces,worker8KB,explicitcounteddelaycallers/commonprefix/highhelpercontracts,unconditionalCALL/JPscan andZIPCRCpass. Conditionalbyte-patternscanisNOTclaimedemptyorexhaustive(codeoperand/datafalsepositivesrecorded). ReuseofoldhighroutinesonlyafterFDEBinteriorentryredirected0002withBpreserved; title/death/finalForcecasesrerunafterthis. Previousr61archiveSHAverifiedunchanged. Stock64KB,originalZIPs,referenceprojectsuntouched.

L3hardwareterrain-edgecorruptionremainsunconfirmed; diagnosticbottomy=133,144,133,148,147,138,152,143,138. L6minorgraphics5..17stillnative;13arcadealternativesassetpreviewonlyawaituserreview, no silentreplacement. README/validation_summary.json explicitlylistopenissues. docs/r62_force_loading.md, docs/r62_readme.txt. ReplacecompleteRTYPEfolder/reset/RTFULL.TAP. Physicalfeedbackstillneeded.


## 128. Correct L6 source identification / full-height dome turret previews (2026-11-06)

User rejects previousL6#5arcadeexplosionmatch, identifiesnative5..8aswalker, questions9silhouette, confirms14turretfamilybutrequestsfullsize/morecolour/correctdomeon-offstates. Readstate/history. Oldgallerynowexplicitlysupersededwithcorrectedlink; manifestmarksbadmatchesrejected. No playableassetschanged.

Nativebitmapcomparison: L6#5identicaltoL1#53,L3#31,L4#28,L7#14; thisisreusednativewalkerfamily. NeworiginalROMwalking-celproposalcodes224/226/228/230,palette5fromframe48000(the230objectisactuallycapturedthere); shared32x32canvas/baseline,24x24and32x32(1.33x)alternatives. Walkingposes/legbandsdistinct. Sourceimagewalkcyclevisuallycomparedagainstnativefourframes. Thisisidentity-reviewproposal, notapprovedarcademapping; useraskedwhethermatchnowcorrect. Earlier2850-family9..13matchwithdrawn, nativefiveframeshownwithnoreplacementasserted. Silhouette/rotationcomparisonwith5..8notidentical, so donotjustreusewalkerposesfor9.

Correctedturretgeometry: original320+324objectsreassembled64x64,alphabbox(1,0,64,48); oldsingle324cropped32x48andfitinside16x32became16x24,losing25%height. New16x32crop(40,0,64,48)and24x32crop(28,0,64,48)fillall32rowswithaspectpreserved,biggeroptionadds1.5xwidthwithoutdoubling. Housingarcade-derived;roundedupper/lowerglassdomesAUTHOREDandplannedinown8pixelcolumn, notclaimedverbatimarcadecels. Offblue/cyan, oncyan/whitehighlights; both-off,upper-only,lower-only,both-on. Eachoutput5nonblackcoloursvsnativeflatlimitedpalette;normalblack/legal8x1pairs. Housingpixelsidenticalbetweenall4states; independentlightdiffsconfinedtop3..10/bottom22..29inlast8pixelcolumn; both-onexactunion. GIFstatesordering/timingillustrative280ms,notnativeFPS/actualanimationtrace. No collision/geometry/runtimeperformanceclaim.

Initialautomaticfull-opaque-materialfitcausedbadflatstripingbecauseequalpalettepairsproduced0/0NaNdiffusion; rejected/fixeddistinctpairsandnondegenerateblankcells. Walkeropaquegraybodyusesblue/cyanshadowswithactualsilhouettepreserved;turrethousingretainsordinarysourceSierraandplannedglass, ratherthanrainbowinteriormaterialfit(rejected). Sourcegrayglassrecolouraffectedhousingviaerror-diffusion; removedper-statehousingchangesandvalidatedonlydomeschangenow.

Script scripts/preview_l6_corrected.py. build/graphics/l6_corrected_sources/index.html,walker_comparison.png,turret_comparison.png,walker_arcade/current/24/32GIFs,turret_current/16/24GIFs,unmatched_head_current.gif,validation.json. Finalwalker/turretcontactsvisuallyinspected;turretall4states/nativesizeschecked. All16newframeslegalpairs;8turretposesvisibleheight32;4walkerposes/3+differentlegbands;independentlightsvalidated. inventory_0/1.png(no palettefilter),head_cels.png(ROM176..254candidates),turret_source_zoom.png,turret_pair.pngalsoinspectedandretaineddiagnostics. EarlierbadL6galleryimagesretainedonlyasrejectedproposals. r62ZIPhash e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574 unchanged. Standard64KB/sourceZIP/referenceprojectsunchanged. No emulator/hardware/gameplaytestneeded/claimedforofflineproposals.

WebresearchconsultedSegaR-Typeoriginalmanualtranscriptionhttps://www.smspower.org/seganotebook/rtype/manual/rtypem.htmlforenemycontextbutusedNOremoteimageassetsorunverifiednamesforlocalROMmatches. BobPapePDFfetchandSMSsprite/manualimagefetchesfailed;notidentificationevidence. Native/ROMgeometryisprimaryevidencehere. Pendinguserreviewofcorrectedwalkeridentityand16vs24wideturret;#9stillunmatched.


## 129. L6 family reassignment and full paired-unit review (2026-11-06)

User says224-familyproposalbelongswithnative9..13,NOT5..8walker;lightsaresquashedhalf-domes,notfullspheres;asksaboutpairedparts. Readstate/history. Correctedfamilyplacementshownforreviewwithoutassigning4arcadecelsone-to-oneto5nativeposes.5..8stillunmatched. Oldtwogallerypagesexplicitlysuperseded,wrongmapping/roundbulbs/croppedstriprejected. No gameassetintegration.

VerifiedarcadecapturedspriteRAMpairings: frame48300 codes320+324;48900 1476+336;48600 1488+340. Samepalette/Y,secondX=firstX+32. Two32x64objectscompose64x64storagewith64x48visibleart. Oldx28..64cropomittedmuchleftbody/mountingpart. Neworiginalpiecesandwholeunitshownbeforeconversion. Originalshallowglassoutlinesretained;noauthoredspheres.

Actualr62L6trace1500updates/27743simulatedrefreshes recordsIDs,coords,IYrecordbytesandreturns. Sameactiveactorfirst20turretsamples15,15,16,16,17,17,16,16,15...;14notobserved. Priornative14..17=4independentlampstatesassumptionwithdrawn. IYslotsreusedlater,notpersistentactoridentity. Nativecollision/componentpairingisNOTclaimedsolvedbyarcadeadjacency. Nativeintegration/posemappingstillneedsdesign.

Scriptstrace_l6_components.mjs/preview_l6_assembly.py. Currentreviewbuild/graphics/l6_assembly_review/index.html,native_components.json,validation.json. Sourcecontacts paired_source_comparison.png,threeoriginalpairedposes+individualhalves;whole_unit_comparison.pngSierraLite;material_comparison.pngauthoredsolidmaterialalternative. Allcontactsvisuallyinspected. Completegeometryuniformfit32x24/storage32x24,43x32/storage48x32,48x36/storage48x40;paddingspecified,nostripcrop/stretch. OriginalglassRGBmaskupper/lowerrecoloured;changesconfinedtoaffected8x1cells,housingelsewherestable;bothlitunionoftwolights. Actual3sourceposeanimationand4lightingstudiesseparatelabelled,280msillustrative/notgameFPS. Materialalternativegreen/yellowarmour,coolmetalshadows,red/magentacapsavoidsinventedblackdithering;sourceSierraalsoavailable. No stylechosenforuser.

41arraysvalidatedintegernormal0..7/legal8x1pairs:8headproposals,9pairedsourceposes,12Sierra+12materiallightstates. Sourcehalves/fullassembly/Sierra/materialimagesinspected. Initialnestedtriplequotedscriptwritefailedbeforefilecreation;PowerShellliteralwritefixed. Validatorfirstincorrectlyrequiredonlyuint8/int64, rejectedvalidint16;correctedtoallintegertypesand0..7range,allpass. No gameplaytestclaimedfornewart;nativeemulationisinspectionofunchangedr62. r62ZIPhash e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574 preserved. Stock64KB/sourceZIP/referenceprojectsunchanged.


## 130. L6 source-aware surface refinement (2026-11-06)

User selected 32x32 for native9..13 proposal and requested cleaner source red accents, black/white gray dithering. Generated fine/deeper ordered gray variants from actual 224/226/228/230 source poses; output red confined to source mask, no red invented elsewhere. Added 26..50 black gray-region pixels per cel depending on pose/style. Four arcade to five native pose mapping remains pending; native5..8 walker still unmatched.

For #14 family retained actual paired poses 320+324,1476+336,1488+340; no invented independent lamp states. White/cyan/blue pistons, yellow/cyan/white body, white/normal-black tubing, red/magenta/white shallow dome-tip accents. Horizontal scanline-oriented ordered shading and finer Bayer alternatives; no random diffusion. Normal black avoids reported hardware bright-black trails. Original moving pistons are not lamps. Full paired source fitted43x32 in48x32 storage.

Script scripts/preview_l6_surface_refinement.py; diagnostic directory build/graphics/l6_surface_refinement/. Visually inspected head_comparison.png and machinery_comparison.png; GIF cycles illustrative280ms, not measured game performance. Independent validation of all14 integer arrays: normal0..7, every8x1 at most2 colours; head32x32/source silhouette/red masks pass; each machinery alternative contains3 distinct32x48 poses. validation.json records counts and source IDs. Prior assembly page links new refinement. Offline asset review only, no gameplay or hardware validation claimed; r62 ZIP SHA256 e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574 unchanged. Stock64KB/sourceZIP/referenceprojects untouched.


## 131. L6 darker gray and structural ordered machinery (2026-11-06)

User prefers deeper gray and previous actual paired machinery. Script scripts/preview_l6_ordered_machinery.py generates build/graphics/l6_ordered_machinery/index.html. Head32x32 slightly darker: gray-region black counts45/58/65/41 vs35/43/50/30; source red-mask check passes. Machinery reconverted from original paired source poses, preserving material gradients and horizontal dark support bars; clustered-bar and Bayer alternatives. Source red domes use red/white ordered highlights, side accents retained across actual poses. Independent side-light blink cadence not established; no fabricated source animation claim. First candidate spilled red into metal; restricted red to source accent mask and regenerated. Contact machinery_comparison.png and head_comparison.png visually inspected after correction.10 integer normal0..7 legal8x1 arrays pass;3 distinct machinery poses per alternative. GIF280ms illustrative, not gameplay performance. Preview only; r62 ZIP hash unchanged, stock64KB/source archives/reference projects untouched.


## 132. Cylinder shape and highlight alternatives (2026-11-06)

User rejected structural shading as losing machinery shape, particularly lower cylinder. scripts/preview_l6_cylinder_highlights.py creates build/graphics/l6_cylinder_highlights/index.html and comparison.png: A yellow faces/cyan rims/blue lower shadows; B cool cyan-white cylinder metal contrasted with yellow support. Uses nearest source scaling rather than Lanczos, explicit source dark-stroke retention, reduced ordered dithering threshold strength at mechanical edges. Six frames legal normal0..7 8x1 pairs; transparent pixels remain black; all138/130/125 dark source strokes preserved per pose per style; three original paired poses retained. comparison.png visually inspected. Appearance still subject to user feedback, not asserted equivalent to arcade or approved. Source geometry remains43x32 fit in48x32 storage. Asset review only, no gameplay or performance test. r62 ZIP SHA256 unchanged e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574.


## 133. Correct cylinder diameter treatment and arcade palette flashing (2026-11-06)

User accepts darker32x32 head9..13 from l6_ordered_machinery. Cylinder treatment previously used wrong lower bounds29..46 including support above; corrected to source32..46, same15-row shading region as upper1..15. Both cyan-rim and cool-metal alternatives retained for review, not yet installed.

Added scripts/capture_l6_flash.py. Deterministic MAME original local graphics capture every4 frames47700..49500,451 sprite/palette snapshots in build/graphics/l6_flash_capture. Initial830-second run ended before47700 at55Hz, zero captures; corrected910-second run succeeds and now asserts nonzero captures. Existing archival stand-in PROM/checksum warnings remain; no ROM files changed. MAME-listxml reports55.017606Hz. Original source images decode sprite RAM, actual palettes and paired halves. No manual emulator use.

Added scripts/preview_l6_observed_flash.py plus corrected converter scripts/preview_l6_cylinder_flash.py. Tracked one colour4/y16 actor frames48284..48396,29 consecutive4-frame samples; verified X decreases10px/sample and paired companion atX+32/sameY/colour. Initial1.05px/frame tracking assumption rejected; measured2.5px/frame.15 unique RGBA states despite only3 code pairings: palette changes control light brightness. Earlier forced205-red conversion erased flashing. Restored source intensity for domes and quantized small side-lamp dim/bright phase at source red170 threshold (dim107 off, bright on). Both alternatives validated source lamp on/off: dim states output0 red lamp pixels, lit states2. Authored normal-black off state approximates original dark red because normal palette lacks dark-red intensity. Dome source highlights retained. GIF timing rounds source4/55.017606 seconds to centiseconds with cumulative rounding. Four-frame sampling limits temporal precision; no native blink runtime implemented yet.

Current review build/graphics/l6_cylinder_flash/index.html, observed_states.png, arcade_observed.gif, cyan_rim.gif, cyan_metal.gif, source_sequence.json, validation.json. Full contact visually inspected after palette-intensity correction.30 normal0..7 legal8x1 frames; transparent source stays black and all125..138 dark source strokes retained per pose. Static contract and side-lamp checks in generator pass. Accepted head recorded in validation. Asset preview only, no playable/hardware/performance claim. r62ZIP SHA256 preserved e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574; source archives, stock64KB and reference projects unchanged.


## 134. Selected cyan rims, faster filled-red light (2026-11-06)

User selects cyan rims; darker head9..13 accepted previously. Requests quicker middle-light turn-on, fuller red fill, tiny upper-right white glint, optional magenta lower shading. scripts/preview_l6_light_fill.py generates build/graphics/l6_light_fill/index.html/comparison.png/red.gif/magenta.gif and30 legal8x1 npy frames. Authored light snaps ON at median source-red145, preserving dim132 OFF and lighting source148 phase before181 side-bright phase; side lamps outside affected dome cells unchanged. Initial peak-red125 test kept all states on due highlight brightness; replaced with median145 and assertions that both OFF and ON exist. OFF arrays byte-identical to selected cyan-rim base. ON red fills all but2 of60..76 source dome pixels (one white-glint scanline); alternate uses lower30percent magenta scanlines. White glint isolated on scanline to avoid illegal red/white/black shared cell. Only affected dome8x1 cells change; source transparency remains black. Full red fill may remap metal sharing these cells, a physical ECM tradeoff; appearance shown for feedback. Contact visually inspected after threshold correction.30 normal0..7 legal8x1 frames, off-state/outside-cell equality pass; original side-lamp updates retained. No gameplay integration/test/performance claim. r62ZIP SHA256 preserved e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574.


## 135. r63 selected L6 art integrated and packaged (2026-11-06)

User authorized finishing playable build. New expanded-disk package build/fullgame/l6_selected_r63/RType_TS2068_r63.zip, SHA256739ca53a0e70c7db176275efa2b82d2b00c919c78992084b20277caf4a6c0446,509157bytes. Accepted darker head32x32 assets from l6_ordered_machinery; native9/10/11/12 map arcade224/226/228/230, native13 reuses226 as return pose, no invented fifth ROM cel. Cyan rims selected, lower-magenta red light option installed. Native14/15->paired320+324,16->1476+336,17->1488+340; three OFF and three full-ON cached render variants. Native AI/events retain original IDs; alias mapping affects rendering only. Boss18..25 aliases share existing identical visual caches (18 or20). Native14 not encountered in ordinary route, its static alias is included.

Cache implementation: new build_l6_selected_r63.py builds only L6 cached renderer and preserves r62 transport/native compatibility patches.13 table entries fit belowE3F0; unused L6 walker-state rangeE3D0..E3EF used for table, E3F0 warm flag retained. Enlarged head renders4x4cells with bottom anchor one cell upward; machinery6x4cells at native render origin. Minor sprites lock X to native8pixel grid, share unshifted source across phase pointers; no unused right padding column stored because phaseX is always0. Existing other boss2pixel phase motion retained. Cache preloaded5888/6144bytes, no per-sprite runtime decompression. Shared contiguous preload stream reduced phase payload5269->3522bytes; motion code1146bytes, combined source ends before3A00 hotkey helper. Static pack/unpack, table bounds, loader length and bank limits enforced.

Rejected integration trials: separate packed streams exceeded resident helper source area; cold loader guard caught cache-slot error. Greedy3byte-match packing made payload larger5520; reverted. Shared whole-cache compression fixed source overlap.7A8A native IRQ counter resets each world, stayed5..16 and never selected ON; gameplay assertion caught only3/6 states. Light now follows verified native actor animation-cycle counter IY+8 bit0 with immediate ON; timing follows native game cycle rather than original palette-ramp timing. Side lights included in ON/OFF assets. Moving assembly left over old mount caused visible old-mount pixels in its dark shading; contact rejected and native origin restored. Extra support/mount remains native; no claim all L6 graphics upgraded (5..8 still unchanged/unmatched).

Repeated L6->other-level switch caught visible7800 write in truncated relocated loader. Control test unchanged r62 route passes; byte comparison found old builder had restored loader copy operand0AAB from6137 to2631. Preserve r62 operand and assert actual current loader length. Both cold and cached8-transition route passes incl1->6->3->6->5->6->6->2->6, forced missing completion bit triggers LEVEL06 reload.

Final frozen sequential run_l6_selected_r63_checks.py six groups PASS: ordinary invulnerableL6 600updates, all5 head IDs/all6 machinery variants, executable-write/source/geometry guards; custom keyboard+both native joysticks; repeated cached/cold jumps; ShiftL fromL6 preload all8 then exact bank/bitmap/ECM/register resume and resident no-op; actual L6 death/respawn; Force attach/detach/recall/pickup on1/3/5/6. Death fixture initially inherited title-level5 selection; removed and asserted active region5, final mounts START01/START06/RTCORE only. Emulator tests do not prove unassisted full playthrough or physical hardware.

Final render_l6_selected_r63.py diagnostic images L6_id*.png from completed world HOME snapshots. L6_id9.png inspected after final placement; rejected shifted-placement and earlier offscreen captures retained as diagnostics, not claimed proof of every animation. Source art also previously inspected. Finalize_l6_selected_r63.py checks frozen hashes, full TAP block checksums/LEVEL/START reconstruction, code/assets/loader contracts, isolated reproducibility30primary products with0differences, ZIPCRC. All7 other levels/boot/launcher byte-identical r62; r62ZIP hash preserved e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574. Stock64KB target/reference projects/source ZIPs unchanged. README docs/r63_readme.txt and validation_summary.json state expanded disk scope, native-defined keys, hardware pending, L3 terrain-edge issue remains open.


## 136. r64 title preload, native machinery fit, L7 shading and bolt-ghost cleanup (2026-11-06)

User asks load-all from title as well as game, reports L7 Spectrum-coloured walker, extra/oversized L6 machinery crossing wall. Also supplies codex-clipboard-2c0164e4-e10f-4844-b318-b7479bd1c334.png; confirms r63/PicoVideo fragments persist and stay screen-fixed while scenery scrolls. Photo arrows identify small red/white fragments and raised-platform strip. Do not claim exact photo reproduced or hardware fixed.

Release build/fullgame/native_fit_r64/RType_TS2068_r64.zip,509757bytes,SHA2561f50c30d5fbd79e49f2fcbd1ae31df6b3b65e7f12eb77d05bfcb0128d4c26d41. Reset/replace wholeRTYPEfolder/loadRTFULL.TAP. docs/r64_readme.txt. Expanded512KB disk only; stock64KB unchanged. r63 ZIP hash preserved739ca53a0e70c7db176275efa2b82d2b00c919c78992084b20277caf4a6c0446.

L6: r63 drew complete paired64x48 arcade assembly fitted48x32 for every native16x32 moving-piston sprite, duplicating fixed mount and extending beyond original box. prepare_r64_native_fit.py retains only moving right component, restores16x32 render footprint/origin; no extra actor/event creation. Reduced component re-quantized to legal8x1 pairs. Darker32x32 head family retained. Cached art4352bytes vs5888 inr63; compressed payload3143, motion1146. Metadata/plan source layout rebuilt; native AI/event bytes A4AE..DC50 and global lookup E000..E2D0 unchanged fromr63, statically asserted. Wall clipping uses existing native bounds, not an enlarged composite. Actual gameplay reaches5head IDs/all6 piston ON/OFF states, executable-write guard passes.

L7: inventoried native sprites1..48 and207 captured arcade code/palette combinations from56700..63300. Contacts build/diagnostics/r64/L7_native_contact.png andL7_arcade_contact.png inspected. No uncertain arcade walker mapping installed. Native14..17 walkers receive blue/cyan/white material highlights; families11..13,25..32,36..40 also shaded.18..22 use accepted arcade walking-head art at native24x24.25frames total, original descriptor dimensions/pointers/blank cells and animation scripts retained. Generated build/graphics/r64_native_fit/L7_comparison.png and installed build/fullgame/native_fit_r64/L7_installed_comparison.png; installed contact inspected. Native visible details may change through dithering, not asserted pixel-identical silhouettes. Uses59 unreferenced high palette rows; reserves original0..63/all referenced classes.137/211cells exact palette keys,74 approximate to available legal keys. New rows normal0..7 only, no BRIGHT black. Initial inclusion of legacy BRIGHT/FLASH rows caused invalid palette index; excluded those keys. No added runtime palette conversion or geometry enlargement; no FPS claim.

Title: plainL at R-Type title loads missing levels and returns to title; ShiftL during active game retains preload, L-release-number retains level override. src/level_hotkeys_r64.asm andpreload_snapshot_r64.asm optimize existing helper to1011generic/1023HOMEbytes, within old bounds. Added CALL00DB at existing low title pollingCC2, retained original DI/C00/EI and input flag handling; moved tiny control markerCD4->CD7, native C042 boot call updated. Marker stores nonzero control mode1..4 rather than literal1; selector tests boolean. No new low-bank padding claimed. Rejected00EB stub overlapped L5's live27-byte dispatcher; final bounded checks preserve00EB..00F7. Initial boot helper installation clobbered compressed workspace3400..3FE0; caught global-source guard, fixed by installing helpers only in level regions. RTCORE reconstruction initially omitted existing8656main-loop dispatcher call; restored and contract verified. Initial title detection read7AA4 while helper mapsF4=3 hiding DOCK3 and saw zero during game, triggering preload instead of L-number. Trace proved mapping error; now uses always-visible HOME5BC2 player-live flag. Final title1/title5 plainL/all-resident no-op and active-game level jumps pass.

L3 cleanup: deterministic component reproducer showed redraw of already visible bolt clears row ownership masks30/30->0/0; erase leaves8 bitmap bytes. This is a plausible screen-fixed-fragment mechanism, not a frame-matched reproduction of the supplied photo. src/projectile_continuous_r64.asm retains row ownership if old mask owns row, visible bits still contain glyph and colour matches. Preserves added star bits. Fits existing640-byte ABI/source slot F100..F380: short hit branches, remove redundant final collision test, direct memory loop counters, compact slot pointer; unchanged glyph IDs/flight speed/native hit resolver. Repeated50redraw tests leave0 bolt bytes; added star leaves exactly1star byte; overwritten different-colour foreground remains8bytes intact; cleared copy and reused slot leave0. Baseline bolt_redraw_baseline.json and fixed bolt_redraw_fixed.json retained. Initial exact-bit comparison lost ownership if star added; extended to glyph subset testANDD and regression. Full projectile tests cover21positions,5directions,16slots,collision queue/stale owner/private stack/stars. Old standalone r57 9DE7 restore expectation incompatible with current generic renderer; removed that isolated legacy call, current restoration tested through real-game preload.

Final run_native_fit_r64_checks.py14frozen groups PASS: title1,title5,bolts,projectiles,L6art,L7art,L3play,controls,jumps,preload6,preload5,death6,Force,rapidfire. L3 bottom-edge invulnerable route2000updates/guarded executable/global sources; not an unassisted hardware playthrough. L6/L7 ordinary600updates each; allwalker14..17native animation IDs reached. Keyboard/user bindings+both native joysticks; repeated cold/cached/same-level/missing-bit jumps; all8 resident preload with exact active-bank/bitmap/ECM/register resume; L6 realdeath/respawn; Force attach/detach/recall/pickup on1/3/5/6. Rapid15presses yields14shots and0latequeue. Initial failed jump traces and all test outcomes retained in check logs/debug scripts. Final checks supersede earlier candidate failures.

Gameplay diagnostics L6_id*.home.bin/png, L7_id*.home.bin/png, ordinary_L3_*.home.bin/png rendered by render_native_fit_r64.py. L6_id9.png, L7_id14.png, ordinary_L3_800.png inspected; final L6_id9 refreshed/inspected after final test run. These are emulator completed-world captures, not physical evidence. finalize_native_fit_r64.py isolated rebuild reproduces30primary binary/TAP products byte-for-byte, validates bounded byte changes, native dimensions/AI scope, reserved palette rows, helper budgets, compressed workspace, correct RTCORE hotkey/native marker, all LEVEL/START block checksums/payload reconstruction and ZIPCRC. All source ZIP/reference projects/old releases unchanged. L3 exact hardware photo remains for user confirmation despite reproduced cleanup fault fixed.

Lessons: a skipped screen write must retain valid ownership; test repeated redraws and partial-copy interleavings, not only complete erase/copy/draw cycles. Distinguish source class IDs from published attributes; never normalize encoded IDs as colours. UI/game state must be read from memory visible under the helper's actual bank map. Native-size moving parts must be separated from fixed companion scenery before asset substitution. A working standalone preview does not prove live fit or background composition.


## 137. r65 hardware fire, pause, Load All title return, and key-definition repair (2026-11-06)

User reports hardware joystick fire/start failing, persistent L3 rightmost scenery fragment surviving cached revisit, requests lowercase rtype/rt.tap, P pause with onscreen indicator, return to title after Load All. Adds keyboard setup sometimes stalls for long periods then recovers. Async pause conflict question had no reply; preserve native key assignment: plain P if unbound, Shift-P if P occurs among six bindings (e.g. QAOP). P resumes after release/press/release. No fixed gameplay-key reassignment.

Package D:\T7_Recover\Jon\Personal\Timex\cartridgeconversion\R-Type\build\fullgame\hardware_fire_r65\RType_TS2068_r65.zip, 511310 bytes, SHA256 27187756c65a85e61e126f32f42315e48283852fa9a21491f7b5afc0f5210ff0. Supported ZIP file set excludes obsolete RTBOOT.TAP like prior release; rt.tap and all relative LEVEL/START/RTCORE/RTPRELD data retained. docs/r65_readme.txt. Expanded disk target only, stock64KB unchanged. r64 archive unchanged SHA2561f50c30d5fbd79e49f2fcbd1ae31df6b3b65e7f12eb77d05bfcb0128d4c26d41. Source archives/reference projects/art remain unchanged.

Hardware input: native_input_r65.asm changes raw AND1F->8F at1A37 and BIT4,E->BIT7,E at1A54. Native normalized fire remains bit4. Timex manual reprint https://www.timexsinclair.com/article/ts2068-joystick-operation/index.html corroborates significant raw mask8F. Earlier emulator tests incorrectly supplied EF(bit4) for fire; TSRun itself returns raw joystick bytes and did not need modification. New tests use7F. All32 direction/fire combinations per socket (64total), unused raw bits4..6 negatives, physical fire starts from sockets1/2, actual15rapid pulses yield15shots/no late queue, native redefined keyboard+both sticks pass. No physical hardware pass claimed.

Pause/title: src/ui_controls_r65.asm 315byte handler, separate50byte key bridge and48glyph bytes. Generic DOCK1 3E40..3F7B, bridge3F80..3FB2, glyph3FC0..3FF0; below mode shadow3FF0. L5 DOCK4 9EA0..9FDB within declared unused336byte music/title allocation, bridge8F40..8F72, glyph8F10..8F40 outside palette/render code. Nine-byte shim1B17..1B20 verifies old FF reservation; DI precedes page change to keep native interrupt vector visible whenever interrupts enabled. Candidate initially reused1C8, but L5 has a live IRQ helper there; rejected before release. Initial L5 UI paging allowed interrupt before DI and entered data at8101; trace proved vector visibility fault, fixed with DI in shim. Apparent free84B4..9000 actually contains music; rejected. Exploratory compressed-debug/font work was not installed; full existing debug viewer remains intact.

Pause uses native game state7AA4 under a map keeping DOCK3 visible. Copies48bitmap+48ECM bytes to hidden HOME7C80, draws normal-white/black PAUSED, freezes CPU game/IRQ updates, mutes AY R8..R10 and restores exact volumes/screen on resume. Tests assert exact screen restoration, stable paused screen/world, mute/restored volumes; plain unbound P and bound-P Shift-P cases pass. Candidate paused_L1/L5.home.bin rendered by render_pause_r65.py; paused_L5.png visually inspected, legible centered PAUSED. No fps improvement claim.

Preload restore_r65 restores resident bank context then uses HOME5E00 seven-byte bridge to enter UI title return (generic0B:3E43, L5 19:9EA3), resets native state/live flags and stack, enters8634. Does not restore abandoned gameplay AY volumes or old instruction continuation. All8cache valid mask remainsFF. Actual gameplay Load All from1/5 returns title, physical socket2 starts again without disk reads; L5 already-resident Shift-L also returns title. Initial resident test sent shortcut during early start animation before native active state; test now explicitly waits active ship/native state, and UI tests native state rather than reusing hotkey debounce across title polls. No claim that a pre-game animation is already active gameplay. Original L-release-number cached/cold/same-level/missing-bit transitions still pass.

Keyboard: newer title C011->CC2 selected-level polling bypassed BF92's Enter prelude. UI restores physical Enter -> native BF99 through low mapping trampoline, keeping IX/IY around native definition. Native key selection retained, including duplicate rejection and final release wait. Key completion's AF save/pop pair is replaced by DI/NOP in this expanded build so the bank-return trampoline cannot expose native vector to interrupt under UI map; outer UI restores caller AF and re-enables after native mapping restored. No extra game RAM reservation. Crucially, shared core BFA9 still CALLed FDEF, now the middle of Force helper FDC3..FE03. Reproducer entered first definition then escaped into gameplay without storing keys. Corrected shared core call to existing zero-fill0072; only BOOT's shared-code image/RTCORE patched, level physical bank2 is retained screen storage and must not be treated as another common-code copy. Conservative direct CALL/JP opcode candidate scan HOME8000..C4AE finds0remaining candidates intoFDC3..FE03; data candidates could be false positives, not a complete indirect-call proof. Actual1/5 each define18keys across3rounds, including80-refresh holds, then selected Space starts game and selected right key moves ship (L1 x32->70). Short initial start pulse occurred before title was input-ready; longer held start used to validate bindings. Do not claim every reported long hardware stall reproduced/fixed.

L3 remains open: probe_l3_orphans_r65.mjs used untouchedr64 baseline;1400world updates, no matching stationary white/red orphan detected. Cache probe on initial fire-only candidate:900updates,3deliberate deaths/respawns,2868render source comparisons,0rawcache modifications/failures. Does not establish hardware cache is always sound. Final ordinary L3 bottom-edge invulnerable firing/motion2000updates, executable/global source guards pass; exact user photo not reproduced and no speculative palette/cache patch installed.

Final checks run_ui_r65_checks.py six groups: pause1,pause5,load5,controls,jumps,L3 allpass. run_ui_r65_extra_checks.py keys1,keys5,resident5,rapidfire,boundP,plainP allpass. Tests cover actual native key setup rather than only injected tables. Earlier failed exploratory probes/logs retained, superseded as described. finalize_ui_r65.py verifies bounded modifications (native input, key clear, UI/helper reservations, shared main hook), full tape checksums/LEVEL+START payload reconstruction,30primary products identical on rebuild, ZIPCRC; original release hash preserved. Tests are scripted emulator/invulnerable diagnostics, not unassisted all-level playthrough or hardware proof.

Lessons: audit old direct utility calls when reusing a native helper address, including menu/key setup paths; check pointer/indirect callers separately. Test actual menu key definition and return into gameplay, not only injected bindings. A bank of zero bytes may be retained framebuffer storage, not executable common code; source and runtime maps must agree. Mask interrupts before paging out native vectors. Preserve assigned P movement rather than silently replacing QAOP. Keep exact hardware screenshots open when deterministic diagnostics do not reproduce them.


## 138. r66 initial Shift-L queue and explicit loading stages; L2 review (2026-11-06)

User reports Shift-L ignored during initialL1 transfer, vague big LOADING after pieces, L2boss terrain moving/stationary sections, old Spectrum art and wrong-scale first snake. Clarifies whole boss scenery should move then stop, snake geometry should be compared against original Spectrum. Optional questions pending on32/40isolated-head choice and normal-v-doubleB occurrence; no hardware reproduction claimed.

Release build/fullgame/startup_r66/RType_TS2068_r66.zip, 511569bytes, SHA256 96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60. docs/r66_readme.txt. All r65 input/key-definition/pause/native patches retained. Lowercase rtype/rt.tap; internal assets relative. Replace whole packaged folder/reset. r65ZIP hash preserved27187756c65a85e61e126f32f42315e48283852fa9a21491f7b5afc0f5210ff0. Stock64KB/source archives/reference projects unchanged. No new gameplay artwork or geometry installed.

Cold startup previously polls onlynumberkeys. responsive_startup_r66.asm adds Shift-L detection every paced RX poll/fragment boundary, latches D623 (after D620..D622 digit scratch), displays LOAD ALL QUEUED. D623 initialized0, persists across interrupted/remountedSTART transfers. Cold image copies latch to otherwise unusedFDA6; native dispatcher entered before8634/titleanimation, using an explicit8634return frame. Hotprefix consumes/clearsFDA6 and jumps existingpreload path. Finishes essential selected startup/core and full RAM verification, then loads all missing levels automatically without requiring held Shift-L or waiting through titleanimation. No unsafe mid-TAP-block interruption. All8 valid before title, selected level retained. Tests brief12refresh press atframe124, latch125, released before boot; L1 queue mountsSTART01/core/preloader/START02..08, title10246. Queued request survives selecting3/5: START01 cancellation thenSTART03/05, remaining starts, correct resident region/title. All transfer guards remain active. UI shows queued state immediately, rather than implying it has already left required boot work.

Cold loader already checks each1KB write/readback and after70pieces verifies all64RAM fragments; this is a real verification stage. New normal-size stage field replaces large generic LOADING: READING FILES, VERIFYING MEMORY, PREPARING GAME before bank/workspace/graphics-cache initialization. The separate big attribute-cell LOADING was preload context snapshot feedback; changed its20-byte5row mask to PREP RAM. Big numeric n OF k display retained. Logo attributes were six uniform32byte rows; reduced immutable table192->6bytes and corresponding sweep stepping32->1, retaining colours. This creates room without moving loader into secondary visible attribute memory. Final loader6142bytes under6144limit (r65 6137); generic prefix1012/HOME1024 fits3E00/7F00 boundaries. Removed redundant IX/IY push/pops from prefix normal/jump paths: those registers are not modified there; snapshot abandons game and returns title. Native jump stack balances/controls verified. Main dispatcher source/header copy lengths all regenerated, especially L5's1024byte HOME helper. New helper code never installed in compressed BOOT3A00 workspace. Loader boot/runtime copy counts and startup BASIC launcher regenerated from actual lengths.

Seven sequential final groups run_startup_r66_checks.py pass: queue3,queue5,pause1,pause5,actualrepeatedkeys,jumps,gameLoadAll5. Earlier initialqueue1also passes. Pause includes exact screen restoration/AY mute and native64joystickcombinations; key test completes3setups/18stores and actual bound key start/movement. Jumps cached/cold/same/missingbit, L5 snapshots/loadall returntitle retained. finalize_startup_r66.py asserts loading-only changed ranges, sharedRTCORE andBOOT byte-identicalr65,30primary products byte-identical after rebuild, all TAP checksums/LEVEL+START reconstruction, ZIPCRC, oldreleaseSHA. queue_L3.png standard-colour render visually inspected: logo, LOAD ALL QUEUED, selectedlevel, READING FILES and counter. Capture is a live mid-update loader RAM sample; counter partly drawn, not a claim of atomic text publication. Stages themselves generated from source; no artificial screenshot editing.

L2: probe_l2_boss_r66.mjs double-B diagnostic completes700bossupdates initially, then160update arrival capture; 1bossjump/1native scrollstop, expected IDs3..6,41..44,22..30 reached, source/code/cache guards pass. Rendered scene_L2_30/100/110 and ordinary_L2_col63/64/65/66 inspected. Large boss body still Spectrum-based yellow terrain and mouth41..44, despite upgraded worm heads3..6. Do not call the entire boss arcade-upgraded. Current head3/4 crop included neck object and warm-only scene extraction, losing much shading/scale. Original Spectrum40x40 heads compared against current at identical scale. Decoded original M72 sprite objects frame16800 isolate actual head codes2470/2464 palette6,32x32 each; adjacent neck2486 palette6 and body2454palette5 are separate. New offline32px and40px head trials stay within40x40storage; original Spectrum/current/arcade context and all52frame inventory saved at build/graphics/l2_geometry_review_r66. Low-colour inventory is a review flag, not proof of wrong matching. Isolated head contact visually inspected; first tight screenshot-crop trial included cave texture and was rejected. Final trial uses transparent decoded ROM objects, normal0..7colour previews (RGB components capped205), no playables installed pending user choice. Body and other enemies still require matched conversions, no guessed arcade replacement installed.

L2 normal-route probe (no shortcut) reaches column68 after1675worldupdates/28662refreshes, invulnerable diagnostic. Boss mouth41appears atcolumn65, fixedx104y64; later42..44 animation sharesposition. Additional32consecutive completed-world captures overcolumn63, nativefine0..7/sub0..3. Measured rows72..159 in right/body region x112..239: all31pairs in each8pixel band shiftleft1pixel; no stationary lowerbody band. Wider24x8windows find persistent stationary(40,80) is player ship; other static clusters upperleft moving enemies, not identified terrain. Original-v-converted terrain bit7flags also match426marked/118unmarked cells, so no speculative flash-flag patch applied. This does not refute user's hardware symptom: completed-world RAM does not show intermediate slow-copy/presentation, and other regions/physical capture remain possible. normal_boss_arrival.gif contains actual completed-worldframes, no interpolated frames; page states limitations. Existing L2terrain bug remains open, not marked fixed. L3 stationary hardware fragments remain open too.

All diagnostics/results and failed exploratory states retained under build; no realtime gameplay performance claim. Lessons: queue user intent separately from packet cancellation and complete current transactions; acknowledge queued actions visually. Identify actual post-transfer work instead of a generic loading slogan. Verify helper-copy budgets after every source shift. Match isolated arcade objects rather than brightness-keyed scene crops containing background/necks. Compare geometry against original before changing native actor boxes. Completed-frame correctness does not prove smooth/atomic hardware presentation.


## 139. L2 arcade organic body shading alternatives from RPC reference (2026-11-06)

User reference codex-clipboard-d2a758cc-b758-4be9-993d-2f67ba02d069.png shows RPC conversion with strong red/pink/white tissue, yellow rib shading and organic openings. Copied unchanged into build/graphics/l2_organic_sierra/rpc_reference.png for comparison. No instructions inferred from image. User wants this direction applied to L2boss body; no chosen profile yet.

scripts/preview_l2_organic_sierra.py generates index.html, comparison.png, A-D.png, A-D_scene.png, scaled_source.png, arcade_body.png, arcade_context.png, bitmap/attribute/npy arrays and manifest.json. Original arcade frame17400 shows full body; earlier16800 clipped at right and was appropriate only as worm context. Warm colour mask vs blue cave plus coarse contour hull, nearby neutral highlight retention, crop55,96,329,240 then body bbox and LANCZOS proportional scaling into160x88 before saturation/gamma/error diffusion. Source alpha included in review so imperfect isolation/contour loss can be corrected rather than concealed. Internal openings remain normal black; no background noise/diffusion outside silhouette. No source/reference-project modifications.

A gamma1.35 / rib saturation2.5, B gamma1.8 /3.5, C gamma2.2 /4.5 use serpentine RGB SierraLite stencil forward1/2,next opposite1/4,next same1/4, with no error diffusion across transparency or flesh/rib material boundaries. Pink source tissue hue protected at1.1saturation. Flesh cell candidates red/white or black-edge pairs; rib candidates yellow/white or black/shadow pairs. Dark rib pairs allowed even for opaque cells to retain true ridges/cavities. D gamma1.8 / rib saturation3.5 compares unrestricted palette with scalar coverage-error SierraLite. D still uses hue protection for flesh input, so it is a pair/diffusion comparison, not raw RPC equivalence. Displayed/profile metadata distinguishes these policies. No assertion of bit-identical RPC algorithm/output.

First unrestricted RGB fit made tissue too yellow/red; rejected visually. First material-constrained pass preserved pink but ribs went flat yellow due interior-black prohibition; rejected visually. Final allows dark rib pairs and blocks cross-material error, restoring ridges. Final comparison.png inspected, A retains darkest rib/cavity detail, B brighter. PNGs were regenerated during refinements; final files supersede earlier diagnostic views. Every final8x1cell asserts<=2colours, attrs have neitherBRIGHT norFLASH, transparent pixels reconstruct black exactly, output independently reconstructs from bits+attrs byte-identically. Four assets each160x88, bitmap1760+attrs1760=3520bytes, legal normal0..7; no BRIGHT black. NPY uses normal palette IDs, no runtime conversion yet.

A-D_scene.png are clearly labelled offline scale compositions, not playable or collision-compatible screenshots: original boss region cleared and new160x88 body placed atx96,y72 over actual r66 scene context. Native terrain tile decomposition, source actor/animated mouth integration, collision mask compatibility, horizontal scrolling shared-cell policies and timings remain pending. Existing r66 gameplay unmodified; archiveSHA still96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60. L2 scrolling and L3 hardware fragments remain open. No performance/hardware improvement claim. Asset review is a separate milestone from game integration.

Final139verification: generator source rebuilt with explicit UTF-8 after a Windows default-encoding failure during page annotation; final asset/page generation succeeds. Source now independently reconstructs exported bytes rather than only arrays. Repeated build hashes match for all preview files; validation_summary.json records checks. Blank cells emit zero attributes. Final A_scene.png visually inspected; no new playable release created.


## 140. Correct RPC settings/source pipeline replaces hand-tuned L2 body recipe (2026-11-06)

User supplies superior conversion codex-clipboard-23baba77-713f-4191-a9a0-a952382be04d.png plus settings codex-clipboard-722820c4-274a-4c6b-a9fe-8d20d3e938bb.png: brightness44,contrast54,saturation71,gamma0.98. Copies preserved unchanged in build/graphics/l2_rpc_settings. No instruction taken from image beyond stated conversion settings. Read-only local RetroPixelConverter found ../../retropixel/index.html; TS2068 graphics skill ../../AISkill_TS2068/skills/ts2068-graphics-animation/SKILL.md and references/graphics.md read/applied. No reference modifications. Broad initial filename search completed and found numerous unrelated reference examples; only local retropixel implementation used.

RPCgetAdjustmentParams maps sliders to brightness44*.02-1=-.12, contrast54*.02=1.08,saturation71*.02=1.42,gamma.98. CPU/GPU adjustment order: decode sRGB to linear, contrast about0.18 plus brightness, RGB-luma saturation, pow(max(channel,0),1/gamma), clamp0..1. Thus previous strong gamma/saturation lifted shadows excessively; not an ECM limitation. The skill scalar-coverage converter is explicitly not an RPC clone. New baseline uses actual RPC code rather than claiming equivalent results from generic/hand-restricted SierraLite.

scripts/prepare_l2_rpc_inputs.py uses the same isolated arcade frame17400 body as139, scaled proportionally before conversion to160x88 or192x104 and flattened against black. Mask threshold112. Source mask/coarse contour inherited139 and remains inspectable; unknown user screenshot source/crop/output dimensions mean no pixel-identical claim. scripts/convert_l2_rpc_settings.mjs extracts13named actualRPCfunctions to generated rpc_core_extracted.js, sourceSHA recorded in manifest. Includes CPU adjustment, sRGB transfer, candidate pair generation, segment-coverage and per-block candidate evaluation and whole-row SierraLite diffusion. Executes actual CPU adjustment/diffusion stages under isolated NodeVM scheduling mocks, not a browser/UI claim. Segment-coverage is localRPCdefault; D compares per-block since user screenshot did not specify strategy. Perceptual/GS refinement not applied, explicitly disclosed. GPL-3.0 license/provenance stored in output, reference untouched.

A160x88normal-only, B160x88brightnonblack, C192x104brightnonblack, D160x88per-block brightnonblack, all same supplied44/54/71/.98 adjustments, serpentine SierraLite. No flesh/rib hue locks. Two documented alpha guards in extracted diffusion prevent error into/out of transparent sky; partial cells restricted to normal black-containing pairs. BRIGHT-black candidates excluded, nonblack BRIGHTpairs retained per skill. Source palette uses RPC measured normal/bright RGB values (e.g.normalred207,1,0; brightred255,2,1), unlike earlier simplified205primaries. Black-as-paper canonicalization swaps/inverts normal-black ink pairs; all transparent bitmap bits0, all-black cells attr/bitmap0. Preserve mask1=keepbackground. This is asset packing, not proof of correct arbitrary-background shared-cell compositing.

NativeA/B/D eachbitmap1760+attrs1760=3520bytes, preserve1760extra. C bitmap2496+attrs2496=4992bytes, preserve2496extra. Byte attrs have same-BRIGHT two-colour8x1 legalpairs. publish_l2_rpc_comparison.py independently reconstructs exported bytes, comparesRGBexactly, asserts transparentRGB/bits0, no BRIGHT-black pair, emits indices arrays and full12288byte nonlinear ECMscene exports. A-D_scene.png are labelled offline compositions clearing old boss rect, not playable collision-correct captures. B atx96y72, C atx64y56. Bright pair retention through current game cached renderer, native terrain tile mapping, animated mouth/weakpoint positions, collision shape and scrolling are pending. Do not install by overwriting old art alone.

comparison.png and B_scene.png visually inspected: supplied pipeline restores dark cavities/rib shadows and saturated red/white highlights, closer to RPCreference. Selected_style.json sets B/current suppliedsettings as preferred baseline; A retained normal-only compatibility; C demonstrates detail lost at smaller size; D retains unknown-strategy comparison. User has selected the RPC appearance/settings, not yet a specific new size. No extra confirmation needed to use these numerical settings going forward.

Rebuilt16asset files (.rgb/.bits/.attrs/.preserve) byte-identically; exporter reconstruction and black-edge masks pass for4profiles. Initial publisher typo else64 fixed before validation. validation_summary.json stores outcomes. r66ZIP SHA still96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60; original ZIPs, playable/stock64KB and reference projects unchanged. Graphics preview only, no measured game speed/hardware claim. L2 scenery and L3 hardware fragments remain unresolved.

Lesson: copy slider semantics, gamma direction, transfer space and palette-search strategy before attempting to reproduce another converter. Identical SierraLite stencil does not imply identical output. Preserve source shadows rather than repairing an over-bright transform with material hacks. Brightness may be negative in linear light even when the UI slider is44; saturation71is1.42, not near-max HSV saturation. Keep BRIGHT nonblack pairs while preserving true normal black at edges.


## 141. Selected192x104 L2 RPC body playable integration (2026-11-06)

User selects C More source detail192x104, asks finish level then compare all arcade art by same method. This release finishes that selected L2 boss integration; does not assert every L2 enemy/alllevels is newly converted. No external/reference/source ZIP modifications. Relevant graphics-animation skill/reference previously read; normal black retained, bright nonblack pairs allowed. PROJECT_STATE and TEST_HISTORY read before edits.

Asset/native mapping: scripts/prepare_l2_tiled_r67.py fits accepted C into128-row shared dictionary while preserving fixed common slots0..15 (including duplicate rows). Body uses96additional rows, animated mouth16. Body251exact/61approx8x8 dictionary cells (eachrow stilllegal8x1), mean absRGB2.2086338/255, zero source black/nonblack silhouette changes.18native32x32 tilesIDs19..36, per-tile LZ total2125bytes vs2160availableD442..DCB2, map56..63. Compression offsets generated from final manifest every build. New src/l2_tile_expand_r67.asm uses bank1 helper3848..3A00 and low trampolines1C8..200; native0..18 remain uncompressed. ScratchC700..C790 deliberately outside actorplanC4F2..C636, in original head6 source used exclusively through immutable phase cache. Long diagnostic actually renders3,4,5,6. SharedHOME882D andFF81 hooks installed onL2warmup and restored onleave via boundedDOCK5A480trailer; fixture asserts exact allowed3byte core restoration, all remaining sharedcode unchanged. Repeated cached transitions pass. L2palette lookup and retained-token handling separate from bank/decode; other levels untouched.

scripts/prepare_l2_actors_r67.py builds deterministic inputs from unchanged captured arcadeframes17400,17700,18000,18300, registered fullbody globalcrop64,100..320,240 then190x104scaled/pad192 and32x24weakpoint crop88,8..120,32. Blueorb alpha included explicitly, diffuse only within mask. Actual RPC extracted functions reused by convert_l2_actors_r67.mjs with44/54/71/.98; no HSV/gamma substitute. Mouth native41..44 raw432bytes,CEAE..D05E fits old area before45D0DE; descriptors4x3, nativeevent EAE9 X13->19, Y8unchanged. Thus visible actor and native collision location move together to152,64. All4mouth frames pack with zeroRGBerror into shared palette. Native collision algorithm unchanged; no full boss defeat proven. Body geometry/sceneryownership regenerated, not old invisible body plus foreground sticker.

Head3/4 actual ROM objects2470/2464 palette6 atframe16800; native5=mirror4,6=mirror3 (binary comparisons0/2pixel differences in earlier native family). Original32x32ROMshape centered in40x40storage; no attached neck in crop. RPC conversion then four legal2px phase pairs,3717compressedbytes bank1:2400..3285 before33E6 preload table, decode buffer bank6:C000..C1E0 disjoint. Existing phase plans/cache remain. Source-preserving preshift palette fit permits BRIGHT only two nonblack colours and canonical normal-black edges. No runtime source scaling.

Exploratory failures caught before packaging: bank1 code initially attempted to unmap its own instructions, corrected to low-bank return trampolines; original A lost crossing map switch, fixedstackAF handoff. Palette dedup initially used dictionary cardinality as physical slot ID and collapsed duplicate reserved entries, corrupting common indices; fixed explicit16-row slot array and appended rows. First terrain scratch reused actor-plan address range and compositor consumed native tile bytes as plans, triggering protected-code write assertion; moved outside that range. Hardcoded compressed pointers became stale after repacking, causing code-like bytes/colours in tiles; now regenerate from final manifest. Source tokens must bypass actor-token conversion and preserve dictionary marker through native classification/group colouring. First head payload attempted to occupy apparently spare bank6 but overwrote native map/scripts, causing missing-boss assertion; rejected, restored fromr66, use original bank1 phase area with actual32px isolated heads. No failed candidateZIP shipped. Exploratory bad_write.home.bin/trace_run.log remain diagnostics; early scene_L2_initial and non-multiple-of10 trace images are exploratory/stale, not final gameplay evidence.

Final diagnostics: scripts/run_l2_r67_checks.py seven groups allpass, reports r67_checks.json and check_*.log. probe_l2_boss_r67 160bossupdates then probe_l2_long_r67 700bossupdates, all4heads/all4mouth descriptors, code/stack/phasecache guards pass, one doubleB jump and one native scrollstop. Final boss_preview_validation.json is700update soak (729totalupdates,12692-ish refreshes; final timings may differ by source rounding). Ordinary probe_l2_fine_scroll_r67:1547updates tocol64,32completecol63 fine/subphase captures, no shortcut. analyze_l2_scroll_r67: y72..159 eleven8rowbands move1px inall31pairs; y64partially occupied byotheractors, not blanket stationaryterrain finding. Completed-frame behaviour does not prove atomic physicalvideo presentation. L2 prior hardware symptom still needs retest; L3 open.

verify_level_jumps_r67 route2/1/2/3/2/5/2/6 passes cold/cachedvalidity,mount counts,normalactor/shipinit and exact sharedhook restoration. verify_pause_r67 L2 passes exactbitmap/ECMrestore, worldfreeze, AYrestore,64nativejoystickcombos. Repeated customkeysetup/start/movement passes (existing definition testL1, sharedcode unchanged). verify_boss_motion_death_r67 actualL2hitflag entersdeath/respawn, effects75/82..98 seen, hitflagcleared, no deathbypass; frame2833trigger/2844death/3201respawn/3208complete. verify_preload_title_r67 L2 all8resident,title,restart passes. Hardwarefire127retained. Static primary products30 rebuild identically; others7levelregions/boot/launcher/RTCORE exactr66. EveryTAPchecksum, fullLEVEL/START reconstruction, ZIPCRC pass. r66ZIP hashunchanged. NewZIP513832bytes SHA256 f35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716. docs/r67_readme.txt distinguishes expanded gameplay, unchangedstock64KB and hardware pending.

Performance scripts measure_l2_r66/r67: identical160update no-firing checkpoint route,104523296vs108338030Tstates,3.64965percent higher new world-loop CPU cost. Timing.json under build/diagnostics/l2_r67_perf/r66,r67; no wallclock/hardwareFPS/player-response inference. Comparison/gameplay images finalmultiples10..100, ordinary_L2_col54..64 regenerated with BRIGHT-aware render_l2_r67; scene_L2_30/100 visually inspected. Source/installed body.png,tiled_body.png; arcade_animation_sources.png; mouth_contact.png and M*_installed.png inspected. Review index.html links actual gameplay vs selected C and installed dictionary approximation. This is playable emulation, not just asset preview; hardware pending.

Future comparison inventory:114existing descriptor arcadePNGfiles,68unique per-level sourceimages across8levels, SHA/dimensions/provenance paths in build/graphics/arcade_rpc_inventory_r67/inventory.json. Historicalsourceidentity flagged for review because oldL6/miscmatches were withdrawn. Preserve useracceptedchoices, aspect/silhouette, pairedcomponentplacement and animation sequences; scale before actualRPCconversion, then compare nativeECM/legalphases/cachecost, do not batch-install. Backgrounds need their own scrolling palette/mask analysis rather than treating individual8x1rows as arbitrary scrolling sprites.

Lessons: palette dedup must not renumber reserved physical slots; compressed source pointers and tables must derive from the same final bytes; a RAM range dispatch is an ABI, so scratch there will be interpreted as compiled plans. Apparent bank gaps may contain native world/script data. Native shared hooks require deterministic undo on every exit and cached reload. Graphics preview parity alone does not validate palette-token lifetime, collision location, or video publication. Keep failures as tests and label exploratory images honestly.


## 142. All-level actual RPC conversion/comparison gallery (2026-11-06)

Read PROJECT_STATE/TEST_HISTORY and graphics-animation skill plus graphics.md before edits; user requests conversions/comparison, not installation. scripts/prepare_arcade_rpc_r68.py builds124entries:114historical descriptor sourcePNGentries across8levels,2correctedL2heads,acceptedL2terrainbody,3correctedL6pairedassemblyposes,4correctedL6headposes. Historical L2neck crops and withdrawnL6matches explicitly flagged; never imply verified identity. Corrected sources appear first perlevel. Aspect-preserving native-fit N plus actual1.3x D artwork scale, rounded8pxstoragecanvas; do not accidentally scale to padded dimensions. ExactblackRGB cavities/background become mask0 as well as alpha-edge masking, includingGIFsource black. No source/archive/reference-project edits.

scripts/convert_arcade_rpc_r68.mjs reuses actual local RPC function extraction/CPUlinearadjustment/segment-coverage/SierraLite with settings44/54/71/.98 and documented normal-black/alpha guards, BRIGHTnonblack allowed.248outputs bits/attrs/RGB/preserve/mask/scaledRGBA exported withsourceSHA/functions/provenance manifest; GPLlicense copied. No handhue locks/HSVsubstitute, no GS/perceptualrefinement. Inputs128-ish sizes measured in inputs.json, counts248 verified. Full converter log conversion.log; no app/browser conversion runtime claim.

Current references:91native storedr67source images,32compiledphase0cache extracts,1accepted packed96x96L5core. Dynamic genericpreload table parsed fromactualr67cache code, decompress originalcompressedblocks and slice targetregion, supports consolidated4352byteL6cache and phase-locked no-spillcolactors. Initial assumption peractorcompressedpointer and fixedextra-column failed6L6references; corrected so zero missing references. These are source/phase comparisons, not fullmask/compositing screenshots. L5wholeboss consists oforganic spheres pluscore; acceptedcompleteassembly link provided toavoid misrepresentingcore-only native descriptor as entireboss.

scripts/publish_arcade_rpc_r68.py independently reconstructs all248pixelarrays from bits/attrs and matchesRGBexactly, asserts everycellnoFLASH/legal sharedBRIGHT two-colourpair, excludesBRIGHTblack, outside-maskRGBandbitmapzero. Generates nativePNGgallery, level/status/search filters, fourcolumns arcade/current/N/D, clickfullres andbackgroundtoggle. Correctedvsuncertainfilters; native/current storage dimensions and reference kind displayed. D is detail experiment only, not approvedgeometry/collision/cache/performance. No runtimeassets installed, r67ZIP SHA256 remainsf35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716. No emulator tests warranted for offlinefiles. Existingstock64KB unchanged.

Diagnostic contact_L1..L8.png sheets saved, firstfiveentries perlevel shown; L1/L6/L8 contacts visually inspected. NewRPCgenerally darker/moretextured than existingbrightart, not universally better. Tiny nativecomponents lose detail even withsourcefaithful conversion;1.3xalternative suppliedforreview. Fullpairedmachinery shouldnotreplace smallmovingpiston alone. ContactQAimages are illustrative layouts; complete perentry PNGs retainactualpixels. Gallery opened inCodexbrowser viaopen_in_codex. Validation.json documents248passes/currentreferencecounts. Userreviewpending; all-levelart here means existing inventoried source set pluscorrected additions, not everytile/frameinthearcadeROM orallterraintextures. No claimofcompleteartinventory/nativeintegration.


## 143. Interactive per-family RPC review form and scroll rules (2026-11-06)

User requests selectableaccept/tweak/misidentified/nochange decisions, settingssameforallanimationframes, terraincontext andhorizontalpaletteuntil8pxgap. Readcurrentstate/history andgraphicsreference. ExistingRPC actualfunctionadapterretained. scripts/build_review_r69.py creates124record/248profile embeddedrawinputs,64initialfamilies,8originalmapgeometrypanoramas,arcadebossareareferences,worker.js. src/art_review_r69.js pluspublish_review_r69.py produce self-contained2.84MBHTML withlocalimage/contextlinks. No webservice/server/networkconversion; no sourceZIP/referenceprojects/gamebinaries altered. Local r68 baseline preserved.

Checkboxes mutuallyexclusive,unreviewedinitialstate;notes perentry. FourRPCnumeric/rangesliders,sharedN/Dsize andscrollflag peranimationfamily. Verifiedknownranges+identical-sourcegroups initializefamilies, uncertainhistoricalgroups remainflagged/editable. Familymemberslisted,posecycle notgamecadence. NativeL5organiccomponents9..26/L6heads18..25 linkedalongsidecorrectedL6posefamilies; usermaycorrectgroupIDs. Persistinitialassignments toavoidfuturedefaultregroupinglosinguserchoices. Changingparamsinvalidatesacceptedmembers toTweak; explicitfamilydecisionbutton. Debouncedworkerconvertsallfamilymembers withonesettingsobject;noindependentframeoverrides. Asyncgenerationtokens preventoldresultsreplacingnewsettings. Existingpreviewbeforeliveconversion labelledbaseline. localStorageauto-save catchesunsupportedstorage; export/import rtype-art-review.json storesstate,expandedentrysettings,families,sourceRPCSHA,notes,reviewchoices. Exportbackupneededforagenthandoff/acrossbrowsers. Import/export/controls implemented, notlivebrowsertested.

OriginalscaledRGBAinput reconstructedpremultipliedRGB+mask beforeliveadjustments. Initialtestcaughtreadingr68.rgb (alreadyoverwrittenwithquantizedoutputbyofflineadapter), causingdoubleconversionbaseline mismatch; fixedread_scaled.png andoriginalmask, all248baselineoutputs nowexactRGBbyteparity. ActualRPCCPUlinearbrightness/contrast/saturation/gamma/SierraLitefunctions inBlobworker, BRIGHTnonblack only,normalblackguards. Settings54/62/80/1.35changespixelsverified. NofakeCSSfilterpreview.

Scrolling policy: segment eachsourcerow byoccupiedmask, coalescegap<8, permitpalettechangeonlygap>=8. Holdonenormalblack+inkpairforeachrun; chooseinkbylinearRGBerroracrossrun, retain8x1rowvariation vertically. Conservativeedges/holesrequireblackendpoint; canloseinteriorcolourversusfreeECM. Do not claim thisisanartisticupgradeforallassets. QuantizeonceusingactualRPCdiffusionwithfixedpairs, then shiftindiceswithoutrequantization. Validateall8pixelphases. Wideaspect>=3familiesdefaultscrolltrueasproposedsceneryclassification;toggleofffornonterrainobjects. Noartificialgapsintroduced. Itisconversionpreviewpolicy, notinstallednativescrolleroptimisation. RealL1_016/L3_040/L6assembly0/L2bodytestsall8phaseszero>2colourcells. Syntheticgap7stayssameink;gap8/9/16permitsred/greenindependentinksandall8phaseslegal. Sourcegeometrymask, notdither-createdblack, determinesgaps. scroll_policy_comparison.png visuallyinspected: documentscolourlossforlargeorganicbody;defaultbodypolicyoff. Somewideassetscouldbeenemypartsratherthanterrain,soclassificationeditablebytoggleandhistoricalidentityflagremains.

Terraincontextforeachentry: fulloriginalfoundationnativelevelmapbitmappanorama, monochromeexplicitlylabellednotcurrentECM; viewportpositionrangeplus384x256arcadebosscontextframe. Noattempttopretendisolatedstrippastedintoactualmap. Existingnativeflipsdecodedfrommapbits. Contextopensautomaticallyforwideentries;availableallothers. Fileslevel1..8_geometry.png arediagnosticgeometryviews, notplayablescreenshotsorproofthesecomponentsareterrain. Artpreviewcanvascananimatefamilyposesorscroll8phases;gamecollision/rendering/memory/performancependingafterselectedchanges.

scripts/test_review_engine_r69.mjs:248baselineRGBmatches,actualchangedsettings,4realassets+7/8/9/16syntheticgaptests,allphaseslegal,UIJSsyntaxpass. scripts/test_review_logic_r69.mjs usesexplicitminimalDOMstub(noactualbrowser)tocheck124cards,exclusivechoices,all4correctedL6headframesingammavariantjobs,acceptedfamilyinvalidation,localStoragenotes/export/import/search. Reportsengine_validation.json/review_logic_validation.json. Testsprovedbehaviourunderstubs, notbrowserWorker/CSP/localStorageorvisualQA. InitialWindowsdefaultcp1252readfailedonUTF8JS; correctedexplicitutf8-siginbuilder/editorpaths,finalpublish/testpasses.

BrowserautomationcreateBrowserTab(iab,file:///.../arcade_review_r69/index.html) rejectedbybrowserURLpolicy: protocolfile:notallowed, onlyhttp/https. Noalternatebrowser/UIautomation,proxyorlocalHTTPworkaroundattempted. ContinuedmateriallysaferCPU/DOM-stubvalidationandprovidelocalfileforusertoopen. This isbrowsertoolpolicyblock, notuserapprovaldenial;noUIinteractionclaim. r67ZIP SHA remainsf35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716. Stock64KB unchanged, noemulatorregressionrunneededforreview-onlychanges. READMEdescribesreview/exportworkflowandlimitations. Allrequestedreviewcapabilitiesimplemented;userbrowserconfirmationpending.


## 144. User review import, terrain size hold, and current-game footprint conversions (2026-11-06)

Userfileconvref/rtype-art-review-mostlycomplete.json treatedasstructuredreviewdata,nottaskinstructions. Readstate/historybeforework.124knownuniqueentrykeys,validRPCsourceSHA/format/ranges,52Tweak,6Review,66unmarked(includes2explicitnull),0Accept/Nochange.39tweakedfamilies haveconsistentsettings;nomixedTweak/unreviewedfamilygroups.52TweaksettingsreproducedusingactualRPCworker,notCSSfilters. Do notinferunmarkedentriesareaccepted. ReviewflagkeysL1_016..019,L3_041,L7_051;no notes present. L2historical3..6tweakedwhilecorrectedheadentriesunmarked,donottransfersourcechoicesimplicitly.

scripts/import_art_review_r70.mjs preservesbyte-exactoriginalreview_snapshot/sourceSHA,regenerates52savedsettingsoutputs;publish_review_checkpoint_r70.py independentlyreconstructsRGBandpublishespreviousbaseline/current/savedcomparison. Userthenrequestsreviewterrainenlargementcarefully.30Dentriesidentified,16terrain/assemblyriskincluding15L3thinstripsandL2body;all30held. Native-sizealternativesgeneratedwithidenticalcoloursettings,30additionalindependentroundtrips. L1bossD152x192exceeds160highplayfield,L2D256x136exceeds248wideplayfield,L3mixed8x104Nvs16x136Dcannotbedroppedintoexisting8pxpitchassembly. NoDassetsinstalled. Checkpoint_contact.png inspected. Seeded saved_review_r70.html usesseparatelocalStoragekeywithoutoverwritingoriginalbrowserreview.

Latestuserclarification:scalechoices to same dimensions as CURRENTgame,includingexistingpreviousenlargements,notoriginalSpectrumgeometry. scripts/scale_review_to_current_r71.mjs readsactualr67stored/cachefootprintsfromr69currentreferenceextraction,assertsall52selectedNprofiledims==currentstored_size;allmatch. UsesoriginalscaledRGBinputsandactualRPCparams,notdownscalingalreadyquantizedD. Allbrightness/contrast/saturation/gamma/scrollvaluespreserved;onlyeffectivevariantN.52outputs/39families,sourceoriginalreviewunchangedSHA. effective_review_current_size.json updatesentry/familyvariantNandretainsallnotes/reviewdecisions/unmarkedentries. OriginalreviewcopyretainsoriginalDchoicesforprovenance. Noapprovalstatuschanged.

publish_current_size_r71.py independentlyreconstructsall52bitmap/attrpairsandcomparesRGBexactly,assertsnoFLASH/noBRIGHTblackandoutputdims==currentr67. ExistingL3strips8x104,sidecomponentL3_04080x16,L1boss112x144,L2body192x104,L6heads32x32,L8boss48x32. No descriptor,pitch,originorhitbox changes applied;gamefilesnotmodified. Occupancy/sourceidentity/compositingstillrequireintegrationchecks,unchangedfootprintisnotproofcollisionmaskunchanged. AssembledhorizontalpaletterulesstillpendingforindividualL3strips;userexportscrollflagsfalsepreservedratherthanclaimingperstripindependentpalettesaresafeaswholeterrain.

L2_body currentreferencebugfoundduringaudit:r68genericcurrent(2,41)showed32x24weakpointalthoughbodyis192x104terrain. Correctedbuild_review_r69.py bodycurrent_imagetoinstalledl2_integrated_r67/body.png andstored_size192x104;notreclassifyingnativeactor41asbody. Thisaffectspreviewreferenceonly;bodyoutputNalways192x104. Other52Ntargets==actualcurrentreferencebeforeconversion. r69baselinepage regeneratedwithcorrectbodyreference;nootheruserchoiceschanged.

Current-sizecomparison index.html showscurrentr67sourceversusnewcoloursatsamephysicaldimensionswithlevelfilter; current_size_contact.png L3_047/L3_061/L2body/L8_042visuallyinspected. current_size_review_r71.html preloadsoriginaluserreviewwith52effectiveNchoicesandfamilyNsettings,initializesseparatebrowserstoragekey;Doptiondisabledonthoseentries. Scriptassertsseedstate==effectiveJSON,52Nentries,andDdisabledcodepresent. Untouched/unreviewedrecordsstillmarkedunreviewed. Itdoesnotclaimallhistoricalsourceidentitiesverified. OriginalJSONbytepreserved;gameZIP SHA f35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716 unchanged. validation.jsonstoresall52exactfootprints/roundtripsand39sharedfamilies. Preview/conversionassetsonly,notnewcartridge/diskreleaseorhardwaretest. NobrowserUIautomationattemptafterpriorfileURLpolicydenial;seedchecksarestatic,notbrowserQA. Alloutputsunderbuild;referenceprojects/sourcearchivesunchanged.


## 145. Explicit five-entry evaluation hold (2026-11-06)

Readstate/history. UsernamesL2_003,L2_004,L2_005,L2_006,L3_040forreviewratherthancommit. Authoredstandingholdconfigsrc/art_review_holds.json. Current-sizegenerationretainsall52previews/settingsbutmarksfiveheldForEvaluation/integrationStatusBLOCKED;47remainingcandidateentriesstillrequireordinarychecks,notautomaticapproval. EffectiveJSONentryandstate decisionsswitchheldfivefromTweaktoReview,now47Tweak/11Review/66unmarked;originalconvrefJSONunchanged. Publisherlabelsheldcards,47/5counts,validationreportholds;resumeseedusesnewlocalStoragekeytoavoidoldstatesilentlymaskingupdatedholdwhilepreservingoldbrowseredits. Noassetdeleted,previousr67artuntouched. Exactfive-keyhold/effective-state/countassertionspass;all52dimension/RGBreconstructioncheckspassagain. r67ZIPhashf35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716unchanged. Evaluationofsourceidentity,shape,animationandcomponentplacementpending;nohardware/performanceclaims.


## 146. Reviewed playable r72 and derived future RPC default (2026-11-06)

Read PROJECT_STATE and TEST_HISTORY before changes. User directs latest game from saved choices, preserving current game sizes, excluding five explicit evaluation holds. Source review JSON, arcade/spectrum ZIPs, r67 archive and reference projects unchanged. Build applies 47 choices: L1 four native entries; L2 body; L3 thirty strips; L4 three compiled entries; L6 four reviewed heads with existing alias; L8 five compiled entries. Eleven held/review appearances independently preserved; L5/L7 region binaries identical. Native/cache actor dimensions and placement retained, not a claim that all newly drawn collision pixels are identical.

Rejected L3 full repack exceeded native allocation (6600 versus6336 bytes). Final in-place streams preserve existing transparent-cell layout and shared palette rows used by unselected art; no speculative plan relocation ships. L1 streams fit original allocations. L4 packet overflow resolved by placing first raw-cache packet in retired immutable selected-source DOCK area; fixed palette map retained. L6/L8 coalesced packets preserve untouched raw cache content. Audit caught restart backups sharing old phase storage; final build relocates compressed backups, patches unique source operand and verifies decoded backup equals original plan bytes. Repeated cached 6/8/6/8/4/6/8/1 route validates actual raw cache against immutable packets after each applicable arrival. Active L6 Load All/title/restart and real death/respawn pass after relocation.

L2 reviewed body is 192x104 at original origin/map columns56..63, 19 tiles compressed2152 bytes within2160 allocation. 247/312 cells exact,65 legal-pair approximations, RGB mean error3.0913/255. Mouth41..44 bitmap/colours preserved through palette remapping; held head compressed cache/table byte-identical. L3 palette fitting and transparent-cell masking mean installed art is not pixel-identical to all previews. L4 compiled renderer requires normal-intensity output. Legal same-brightness pairs and normal black asserted. Installed and game screenshots published under build/graphics/reviewed_game_r72; L1/L2/L3/L4 examples visually inspected. Asset preview, scripted gameplay and hardware validation distinguished.

All eight boss scripted tests pass, including700-update L7 approach. Old test assumptions for L6 locked-X minor heads adjusted to current pose policy; strict large-boss 2px checks remain. Main nine groups: L3ordinary2000, L6ordinary600, repeated jumps, pause/native joystick64 combinations, repeated custom key definitions and movement, death/respawn, preload/title/restart, Force pickup/attach/detach/recall, rapidfire15 requested15 shots with no backlog. Three additional backup tests above pass. L2 fine-scroll1547 updates/32 captures analyzed; lower body shifts1px, actor effects prevent blanket whole-screen equivalence claims. Same160-update L2 CPU sample: r67 108338030 Tstates, r72 110157344 (+1.679293965%); not hardware FPS. No new all-level speed claim.

Finalizer verifies30 primary products rebuild identically, every LEVEL/START TAP reconstructs expected banks and has valid checksums, common boot/launcher/core unchanged, all explicit holds and earlier review-only appearances preserved, archive CRC valid. Deterministic ZIP timestamps. Release build/fullgame/reviewed_r72/RType_TS2068_r72.zip,513881 bytes,SHA256 e219bfe39e70e42e2cc4784ed8d0f654c3a2f5786240312641279868f8bba9e9. r67 ZIP remains f35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716. Expanded disk release only; stock64KB target unchanged. Hardware pending; known L3 stationary artifacts remain open. No browser automation workaround after file-URL denial.

scripts/derive_graphics_defaults_r72.py writes src/rpc_default_settings.json and build/diagnostics/graphics_defaults_r72/analysis.json. Excludes holds/unreviewed;37 included families across6 levels. Median within family, then level, then levels prevents L3 component count dominating. Balanced unrounded49.25/64.5/78.25/1.13 => brightness49,contrast65,saturation78,gamma1.13. Family-only alternative50/59/86/1.16 recorded. Actual RPC linear adjustment/segment coverage/serpentine Sierra Lite, normal black, legal8x1 pairs, scale source to current dimensions first. Future default only; saved individual settings retained for r72. No universal quality or automatic deployment claim.


147. Terrain rollback r73 (2026-11-07). User reports uncoordinated 8x8 colours/clash L1-5. Read state/history. scripts/build_terrain_restore_r73.py derives from r72, disables new L3strip/L2body install, reserves all128 L1 palette rows rather than considering only enemy references. Fixes shared terrain palette ownership omission. Byte audit: L1 differs from r67 only within four selected enemy source streams, full palette identical; L2/L3/L5 full64KB images identical r67; L4/L6/L7/L8 identical tested r72. L1 retained enemy colour fitting has modest approximation recorded in native_art_report; no palette mutation. Scripted L1boss160 postjump updates passes protected-code checks. All TAP checksums/fullLEVEL and START bank reconstructions and ZIP CRC pass. Hardware pending; other pre-existing scenery glitches not claimed fixed. Entire previous L2body restored as part of terrain rollback. Existing individual source choices and future preset preserved, not silently changed. Output build\fullgame\terrain_restore_r73\RType_TS2068_r73.zip SHA256 c47df26ddb02d5557a909001a6a3a430bd7cb37ccaca216992fb19dce8ec1390 bytes 552418. Stock64KB unchanged. No reference files modified.


148. r67/r72/r73 visual comparison (2026-11-07). Read state/history. Isolated matching game/tape fixtures under build/graphics/version_comparison_r73; all three releases pass scripted L1-5 double-B boss routes with160 post-jump updates each. scene_Ln_110 captures rendered as ECM; same gameplay update, not identical wall-clock/actor phase. Native asset decode comparisons and binary change counts generated by scripts/compare_versions_r73.py. Page index.html and terrain_comparison.png show actual installed output. No new game modification or hardware test. Initial capture preparation omitted matching tapes and failed ENOENT; corrected before successful15 routes. Static screenshot comparison does not establish scrolling colour stability.


149. Small loading messages r74 (2026-11-07). Read state/history. User photo identifies giant PREP RAM and requests all oversized loading messages removed. One RET byte at feedback entry per level (3E00 or L5 A400) prevents separate attribute-letter screen; cold existing loading UI/PREPARING GAME stays. Active gameplay context snapshot retains prior screen briefly until regular worker loading UI, not a falsely claimed immediate logo redraw. Normal8x8 LEVEL label and digits replace2x text; same32byte digit slots with padding preserve runtime renderer/addresses. Loading UI recompressed/padded in original1650byte allocation; loader remains6142 bytes, launch rt.tap updated. Artwork remains r73 byte-identical outside eight feedback entry bytes. Scripted L5 LoadAll/title/restart passed; final small-UI L2 same passed all8resident/physicalfire restart. AllTAP checksums/LEVEL/START reconstruction and ZIPCRC pass. Static loading_small_text.png inspected (dynamic digits absent until runtime draws). No hardware test. Scripts build_loading_text_r74.py then small_loading_labels_r74.py implement changes. Archive SHA256 5ad1ed9627e73c23f63e74c8a682cb3270c1404db5b2a5fd6c63485266162905 bytes 552122.


150. Confirmed L2 pre-r67 rollback r75 (2026-11-07). Read state/history. User photo shows gaudy cyan/green vertical structures and red/blue ground. Matched ordinary80-update captures from r66 and r74 reproduce exact scheme difference; build/graphics/l2_palette_trace_r75/comparison.png inspected: r66 yellow/purple versus r74 cyan/green/red/blue. r73 incorrectly used r67 as regression baseline. r67 changed palette lookup/token/group paths with body integration; exact faulty path not isolated in this fix. Original terrain cache FBD0 bytes identical across two live samples, so do not falsely attribute to that table. Safe full L2 image rollback to r66 plus one-byte feedback RET retains original coordinated implementation; explicitly also reverts upgraded L2body/mouth/head changes from r67. Other seven levels, loader, smallUI, RTCORE/RTPRELD identicalr74. Scripted L2 LoadAll/all8resident/title/cached physicalfire restart pass; boss preview160 further updates pass code/stack guards. Fixture normalizes optional r67tilehook only when present, accepts native r66core. AllTAP checksum/LEVEL/START reconstruction and ZIPCRC pass. Archive 43000655003df351fafa043a062ea095023512b2e87df8249ccf546857bcc951 550463 bytes. Script build_l2_palette_restore_r75.py. Hardware confirmation pending; stock64KB unchanged. Original source archives/reference projects unchanged.


151. L3 colour-token contamination fixed r76 (2026-11-07). Read state/history. User photo r73 reproduced by route L2->L3: firstscreen cyan/green broad top and blue/red/magenta bottom; fresh L3 normal. r66/r75 fresh L3 palette/terrain unchanged, so earlier whole-level comparisons missed stateful code. Watch FF81: original fresh NOP/NOP; r73 postL2 RES7. Root in r67 keep_dictionary_token: CP90/RES7 stripped original terrain80..8F; restore_trailer hardcoded CB BF from Spectrum instead of full ECM00 00. Fixedkeeper preserves all token bytes, restore writes00 00 while maintaining following12 opcode. Common level initialization resets FF81/82 after native86C3 helper rebuild before warmup; 12byte register-preserving wrapper occupies retired0CF0..0CFFpadding (all45 verified), DC0CALL redirected. Guards run after transition completion; initial test accidentally asserted during key selection while stillL2, corrected; writer trace isolated actual hook writes. Build script/source r76 separate. Static diff permits only hook/wrapper/code edits versusr74; every artwork byte/palette unchanged. r75 fullrollback superseded: upgraded r67L2body/head/mouth reinstated. No claim exact per-instance styles identicalr66; L2scene now coherent yellow/purple, no garish bands.
Eight transitions2/3/2/3/1/3/2/3 covercold/cached entry, hook asserts00 00 outsideL2; all8bossroutes pass (L7700afterjump,others160), LoadAll/all8resident/title/cachedphysicalfire restart pass. FreshL2ordinary80 and switchedL3 screenshots inspected; L3_before_after.png shows reproducedbad versuscorrected. AllTAP checksums/LEVEL/START reconstruction/ZIPCRC pass. Hardware pending, other knownL3stationaryfragment issue not claimed fixed. Stock64KB unchanged. Archive 28d9b6c51d789a17deb82a4fc2f3ce6309ed7145227c99d01a369f9046efdc31 552577bytes.


152. Startup LoadAll continuity r77 (2026-11-07). Read state/history. User r76 missingtotal, blank/block then0to336. Missingtotal caused r74 staticdigit removal while initial startup onlyupdates numerator. Previous queued cold request entered native game then used hot snapshot; replaced with cold branch in existing preloadworker reached beforeprepare via loaderextension. Cold entry counts/loads other7levels and returns selectedregion withall-valid, clearsqueuedrequest, then one normalhandover to title. Cold bank5buffer E000 avoids worker8000 and retained HOME C000 coreworkspace; restores runtime C000 selector. No initialcontextsnapshot required. Hotworkerpath retained, coldflag binaryinitialized0. VALID targetmask initialized on both paths and copied to coldhandover, notcollapsed toselectedbit. Compact8x8digit renderer uses80bytes versus320, extension101bytes occupies reclaimedglyphpadding; loader6142bytes unchanged. UIcompressed1611<=1650, static070total visible, queuedprogress total406 andcoldworker startsdone70/includesinitialfiles, no0of336reset. Source scripts/build_startup_bulk_r77.py.
Initial failed allocation1687>1650 resolved via compactglyphstorage, not shrinkinglogo. Screen-mode assertion initially includedfinalhandover41, scopedtoactivebulk3. Onscreen total sampling initially hit incompletepublication/staleworkerfields; finalverification waitsforcomplete406glyphs. Fontpath corrected. QueuedL1 and changedL3 tests pass all8resident beforetitle (8880/9029frames respectively); standardvideo maintained duringactivebulk, releasedShift-L recognized, actual406glyphs verified. bulk_progress.png inspected, showsnormaltextandvisible406total; capturedinitialverifyingstage stillshowsqueuedlabel. NormalL1/L2/L3 bossroutes pass160postjump; finalcounter change touchesstartup only. FinalhotL5LoadAll/title/cachedsocket2fire restart passes. All8levelimagesandRTCORE identicalr76; allTAP checksums/LEVEL/START reconstruction/ZIPCRCpass. No graphics/gameplaychanges, hardwarepending, stock64KB unchanged. Archive b1de08089d83c8a7b091221dd4a215821e923d1a0a015f4ed0f80ab6641c1c7c 552768bytes.


153. L2/L3 stationary terrain investigation, unresolved (2026-11-07).
Read state/history. Userphoto12972 shows L2 middle/other columns fragmented; L3 also. User confirms latest release and before firing at beginning. Scripts probe_terrain_motion_L2/L3_r77.mjs capture completed updates20..180. Global dominant shift1px each; initial local-motion suspects were enemy pixels, visually checked L2u146. scripts probe_long_L2/L3_r77.mjs capture through700 worldupdates with invulnerable scripted firing/vertical motion; compares original per-level map bitmap, not colour approximation. No >=14pixel mismatch cells exactly matching displaced map +/-8px on sampled every8update topterrain. First matched no-fire L2u80 panoramaoffset280 error1; L3u80 offset88 error12 (mostly star contamination), not a proof all terrain/collision paths are correct.
Intermediate video captures scripts probe_raster_L2/L3_r77.mjs:301L2/251L3 frames in updates70..90. Detected partial-row +/-1pixel scrolling publication, no matched terrain-cell displacement beyond1pixel in these samples. This does not reproduce the persistent large fragments in user photo or exclude hardware publication problems. Do not claim cause found. Actual death tests probe_death_L2/L3_r77.mjs use real hit/death/respawn, no death bypass; FF81 endsC3B80F onL2 (custom preserving keeper) and000012 onL3 as expected. No leaked RES7 observed.
Exact queued startup path probe_queued_game_r77.mjs selectsL2 orL3 during startup, Shift-L queue, all8resident beforetitle, joystickfire starts game then100 no-fire updates. Both complete; top80 map match costs10 at expectedoffset300(L2)/108(L3); queued_game_L2.home.png inspected: coherent columns. So bulk-loader workspace corruption not reproduced on these routes. User pause persistence question remains pending. No arbitrary terrain/asset rollback or unverified fix installed. Reference projects/gamebins unchanged. r77 archive SHA b1de08089d83c8a7b091221dd4a215821e923d1a0a015f4ed0f80ab6641c1c7c unchanged. All diagnostic files remain underbuild; no new release/hardware test. Need hardware follow-up; issue open.


154. Jump ownership and protection countdown r78 (2026-11-07). Read state/history. User distinguishes normal menu start good, L+2 jump bad; reports delayedterrainhits bothpaths. Re-examined existing r76 jump_0_L2 snapshot: broken columns reproduce there, overlooked by prior jump-load/state checks. Map top96 correlation residual1639bits vs coherent menu~93; activeowner130 vs43 differs atinit but resetting owner alone, playerflags alone, renderer-mode alone did not fix. Full8634return candidate enteredprompt/hung; abandoned. Direct-coordinate teleport collision probe violated compositor locality and tripped protectedcode guard; not valid collision evidence, not shipped.
Final jump path calls existing1485/8721, then rebuilds 640initialowner cells from freshly drawn bitmap toFF/0 withinterruptsdisabled, preservesIX, clearsfinephase7A82/83, restoresmap9/EI, enters8646shipsetup. This bypasses old8640resume point only forjump. Helper58bytes fits retiredfeedbackpadding3E01..3E3B orL5A401..A43B, retainsRETatfeedbackentry; noUIoverlap3E40. CF0/D75/D96padding contracts asserted. DC0originalCALL86C3 restored becauseCF0nowjump entry. Oldr76colourtokenkeeper andexitNOPfixes retained; crosslevelhookguards pass. Rebuiltowned columns no longer have the large stationary holes in matched captures; residualmapdifferences remain (notpixel-perfect claim). L2_jump_before_after.png actualcaptures.
Realjoystickup movement test (no teleport/nativecoordinate edits) shows old natural contactdelay184.925s withprotection2 versus0.705s forcedunprotected. PlayerIRQtick previously returnedfromcollision whileprotectioncountstalled. New countdown decrements only nonzero7A98 duringacceptedactiveplayerupdates; actual naturalcontact0.6068s, forcedcontrol0.6238s. No protectionbypass in naturaltest. Source game_pixel_overlay_r78.asm fits2430<=2432 beforeED80phases. Stable5jump-tableentries kept. Four legalshortbranches andoneunconditionaltailcall +equivalentunsignedstate-rangecheck reclaimspace. Conditionaltailcall trial rejected/corrected beforeinstallation.
All8bossroutes pass (L7+700updates, others+160); route2/3/4/5/6/7/8/2/3/5/2 cold/cached passesloadcounts/init/reset/shipchecks. Initcounter observes1485 ratherthan8640 becausejumpentrychanged. Separate4jump L2/L3 contract verifieseach640ownershipcells exactly againstvisiblebitmap. Pause64joystick combinations/exactscreenrestore pass; realL6death/respawn pass; queuedstartupLoadAllL2 allresident beforetitle/visible406 pass; L5LoadAll/title/cachedsocket2fire restart pass. Staticperleveldiffrestrictedtocodehelper/hotoperand/playercode; allpalettes/nativeart/playerphasebytes unchanged, loader/rt.tap/RTCORE/RTPRELD identicalr77. AllTAPchecksum/LEVEL/START reconstruction/ZIPCRCpass. Hardwarepending; stock64KB unchanged. Archive adf0e6e2bc35b37f465ab0a266ee1009f11d9db638fc41d16e8daad407e75e2e 553070bytes. Sourcebuild_world_owner_r78.py +prepare_protection_r78.py; no reference projects/sourceZIPs modified.


155. Native star callback race fixed r79 (2026-11-07). Userphoto12973 r78jumpL2 showsremainingcoloured/scrollingpieces; acknowledgedr78insufficient. Priorbitmap-only ownershipaudits checked an invented invariant ratherthan actualnativeattributeinitialization, so didnotprovefix. Compared menu/jump at8721: nearlyidentical commoncode exceptdiagnosticdeathbypass/IRQcountdowns, but menunative7800attrs all640=47 versusjump622=47 and18colouredliterals41/43/45. Writertrace identifiesBF3D LD(BC),A native starcolourwriter executingbetween86C3clear and8721draw, evenwithplayer5BC2=0. MenuBE62=0, jumpBE62=1. Native73C2 disablescallback,73BC enables; normal8721alreadycalls73BC afterFEEBdraw. Rootis starcallbacklifecycle, not newterrainconversion or hardware-onlypublication.
Finalr79 buildsfromr77 plusretainedr78collisionclock. CF0wrapperCALL73C2,CALL86C3, preserveHL/resetFF81,RET fits16bytes; nativewarmupCALLCF0 retained. R78bitmapownership/finephase/extraD75/D96trampolines removed. No nativecode orframebuffers changed beyondCF0 andplayeroverlayversusr77. Sourceworld_init_r79.asm assemblesbyte-identicalall8wrappers. Exploratory native-state/overlayreset/globalinterrupt/forcedsync prototypes failedorleftgeometryresiduals andwere discarded; one nativebuild failed anassert whilePowerShell continued, thosemixedartifacts were rejected andfinaltests ranonlyaftercheckedbuildsuccess. Preserve originalgraphics-restorationCALL94F9 andnativeIRQtiming; disablingthem wasnotcorrect.
Newverify_world_jump_r79 assertsBE62=0 andeach640nativeattrs=47 immediatelybefore8721. Negativecontrolr78 fails Stars active during world construction; r79 passes12initializations acrossroute2/3/4/5/6/7/8/2/3/5/2, cold/cachedloadcounts andnativeinit/object/ship checks pass. MatchedL2front map correlation improves1639old/333r78 residual to107r79 (ship/stars included; notpixelperfect claim); actual comparison_1.png andL2_jump_before_after.png rendered. No large column holes in inspectedscene. All8bossroutes pass (L7+700,others+160), pause64joysticks/exactrestore, actualL6death/respawn, queuedstartupL2visible406/allresident, L5LoadAll/title/cachedphysicalfire restart pass. Retainedcollisionfix naturalrealjoystickhit0.75684s, no forcedprotectionbypass. Palette/nativeart/playerphaseandloader/rt.tap/RTCORE/RTPRELD unchangedr77; allTAPchecksum/reconstruction/ZIPCRCpass. Hardwarepending; otherunrelatedissuesremainopen; stock64KB unchanged. Archive a7c0bf7fa0533791b00c55372edf880694e4dc50eb3dfce11ec7ab3ae1074f41 552865bytes. r78publishedarchivepreserved; no referenceproject/sourceZIP modifications.


156. Offscreen actor coordinate clipping r80 (2026-11-07). Userphoto12974 r79 four stationary L3 fragments identified as native walkers101..106 (observed101), four waiting objects85B5/85BE/85C7/85D0 with logical X472/424/440/456 Y128. Actor trace700updates shows no entry into viewport. Generic phase smoother multiplies character coordinates in8bit A, then restores sign only: positive bit5/6 lost, wrapping offscreen actors onscreen. Preserve original upper E0 bits for both X/Y, OR smoothed low5 bits. Two11byte blocks padded withNOPs, exact image lengths/symbol addresses maintained; levels2/3/4/6/7/8 corrected; L1/L5 byte-identical. No actors removed, scripts/art/palettes changed, or allocations enlarged. Current sparse walker artwork distinct from clipping issue, not upgraded here.
Matched actual gameplay snapshots scroll_L3_80.home.bin rendered in build/diagnostics/l3_fragments_r80/r79_r80_gameplay_comparison.png: r79 four fragments, r80 absent, terrain retained. Native/cached contact sheets and original/current walker comparison in same diagnostics folder; asset previews are not gameplay. trace_l3_fragment_actors_r79/r80 scripts retain offscreen AI requests. All8 boss routes pass including moving2px assertions and L7+700updates;11 cold/cached switches pass and12 initial640attribute audits preserve r79 fix. Static exact patch scope, allLEVEL/START TAP checksums/reconstruction, unchanged launcher/core/preloader, ZIPCRC pass. No hardware confirmation yet; stock64KB unchanged. Build script build_offscreen_clip_r80.py.
Archive a657f8841b934266f3a15846d6c2b9baab0fb2f660d6cdfd85b7e0b20ee67dc2 552556bytes. No reference projects/source ZIPs modified.


157. L3 enemy ECM r81 (2026-11-07). Photo12976 enemy right of player identified by native contact sheet as four-frame descriptors36-39. No verified arcade match available locally; enhanced existing24x24drawing instead of inventing source provenance. Normal-black paper, silver/cyan/blue scanline shading and magenta/red core accents, two unused dictionary entries126/127. Exact bitmap bytes, descriptor pointers/dimensions/transparency and frame count unchanged. Static diff only those two palette rows and selected cell tags; all other level images identicalr80, no code/runtime draw cost change. Deterministic ordinary L3 route700updates completed, offscreen walker requests remain correctly outside viewport. AllTAP checksums and ZIPCRC pass. Asset comparison build/graphics/l3_enemy_ecm_r81/comparison.png inspected; asset preview distinct from gameplay/hardware test. build_l3_enemy_ecm_r81.py, build/fullgame/l3_enemy_ecm_r81/RType_TS2068_r81.zip 3f98f5291a105e6a923c5752726811cc7ffb4167dbc22017abea545db8e2395b. Hardware pending; stock64KB unchanged.


158. L3 bot/pods/exhaust ECM r82 (2026-11-07). Userphotos12980/12977/12978: upper-right yellow bot31-33, firing pods22-27/88-93 and detached engine/plume34-35. Reuse existing legal black-paper dictionary rows30/92/101/126/127 for metal highlights/cool shadows, warm exhaust red/yellow/white accents. No verified arcade redraw claimed: native silhouettes/bitmap/framecount/dimensions unchanged. No palette dictionary, terrain, code, allocation or otherlevel edits. Exact diff only selected native celltags; otherdescriptor rawbytes unchanged except those selected, transparency and allbitmap bytes asserted unchanged. Ordinary deterministic L3gameplay700updates completed; allTAP checksums/ZIPCRC and unchanged otherlevel images pass. Inspected asset-only build/graphics/l3_pods_ecm_r82/comparison.png; this is not hardware evidence. Builder initial else126 syntax typo corrected before any build succeeded. build/fullgame/l3_pods_ecm_r82/RType_TS2068_r82.zip 8cb8fbef233b09e57db6bb880e25eddad014ce7194c9b74a0cea34439b19dbec. Hardware pending; stock64KB unchanged.


159. L1 stomach machinery restoration r83 (2026-11-07). Compared r82/r67/r59 native descriptor8: current organic surface improves but two openings lost their internal machinery. Restored r67 bitmap/normal palette rows only where complete8x1cell safely inside two authored elliptical apertures. Eight cells in column10, dimensions/descriptor pointer/storage/code unchanged; untouched per-cell rows preserved. Free enemy dictionary slots used for mixed scanline patterns, existing dictionary slots not overwritten. All other descriptors rawbytes unchanged and allotherlevel images identicalr82; static diff restricted to eightcells and previouslyunusedpalette entries. build/graphics/l1_machinery_r83/baseline.png and comparison.png inspected as asset previews. L1 actual emulated doubleBboss test+160updates passes,979native target records; allTAP checksums/ZIPCRC pass. Initial comparison syntax typo corrected before render. Build script build_l1_machinery_r83.py. build/fullgame/l1_machinery_r83/RType_TS2068_r83.zip 64635beb878eedef147a20fafcfcee9d3a81cd752b55ccfe361cce1561503878. Hardware pending; stock64KB unchanged. Broader walker rebuild/corrected elongatedyellowbot and referenceexhaust redesign still pending, not claimed completed by this focused patch.


160. Wider L1 machinery restoration r84 (2026-11-07). User correctly notes r83 restored only centre column. Extend restoration to original silver/black machinery rows across columns9..11, upper y56..79/lower88..123, preserving r83 base on other rows. Restores side detail without wholecell geometric ellipse restriction; only original normal-white/black rows selected. Thirteen affected cells (includes unchanged centre rows), no descriptor dimensions/storage/code change. Other descriptor rawbytes and levels2..8 identicalr83; static diff onlyselectedcells/previouslyunuseddictionary slots. Asset build/graphics/l1_machinery_r84/comparison.png inspected, r83/current/earlier comparison. L1 emulated boss+160updates passed979target records, allTAP checksum/ZIPCRCpass. build_l1_machinery_r84.py; build/fullgame/l1_machinery_r84/RType_TS2068_r84.zip 2e61568b66eb6ce966ebb3727f8aff14714ecd80a2d167ee76d1f0b267fc6ee7. Hardwarepending; stock64KB unchanged. Remaining walkers/yellowbot/exhaust redesign still pending.


161. Wider walker artwork review r85 (2026-11-07), ASSETS ONLY, no game release. Inventory native and actual compiled-phase0 art across8levels. Arrowed elongated yellowbot conclusively native L3#94(32x16); Before31 separate roundwalker. Review13families/54nativeframes/127candidates, L1small/large/round,L3round/yellow/ground,L4small/round,L6round/head,L7round/head/small. Known smallwalkers use original arcade1570/1572/1574/1600/1602; large uses existing201..204ROM extracts; whiteheads224/226/228/230; no reuse of withdrawn explosion2758 match for roundwalkers. Unverified mappings labelled native refinements. Ground101..106 source from foundation originalHOME DC71 etseq, not r59 where source already acts as scratch plan; fullbody restored in proposals.
A actual RPC sourcecolour conversion; B local bevel/material preparation then sameRPC; C AIassisted native-derived roundwalker/yellow94 concepts generated with imagegen skill, originals copied into project, not claimed arcade assets. Native-sized conversion after source scaling. Actual RPC CPU source extraction, segmentcoverage pairs, serpentine SierraLite, alpha-boundary diffusion stops, brightblack forbidden. A/B settings49/65/78/1.13; C56/54/78/1.65 consistently shared across frames/variant. Initial B overlydark corrected before final review; C gamma increased after native-size inspection. 127candidate checks legal8x1/normalblack/nooutsidealpha; profile settings uniformity passes. PNGoverview/priority_comparison/requested_bots inspected. Animation GIF260ms illustrative, no measuredgameplay or new runtimeframes claimed; sheet hasfourAI walking poses but native familycounts retained in candidate sequences.
Review build/graphics/walker_review_r85/index.html supports per-family keep/A/B/C/review plusnotes/localStorage/exportJSON. Provenance and exact dimensions shown. No currentr84game/terrain/loader/referenceproject/sourceZIP changes, no speed or hardwareclaims. Scripts walker_review_r85.py,prepare_walkers_rpc_r85.py,append_ai_walkers_r85.py,convert_walkers_rpc_r85.mjs,render_walker_review_r85.py. Game integration deferred for visual choice among uncertain identity/art-direction proposals as requested, not a permission requirement. Stock64KBunchanged.


162. Playable walkers/exhaust r86 (2026-11-07). Completes the reviewed wider pass in expanded-RAM/disk game:13 four-pose walking groups (52 walking images),6 separate raised-gun poses, correct L3yellow94 and4exhaust pulses,63runtimeimages21groups. Before31 and sharedroundwalkers use generatedSpectrum-derivedfourposes, explicitly not claimed arcade; yellow94usesseparategeneratedreference. Smallwalkers genuine1570/1572/1574 plus authoredintermediatelegs;1576wasvisuallywrong and discarded. Largewalker four earlierarcade cels; heads224/226/228/230. GroundL3originalfoundationHOME source restores lostbody. All scaledbeforeactualRPC; samefamilysettings, legalnormal8x1pairs. Engine measurednative48x16, corrected initial56width beforefinalpackage, native8pixelnozzlerestored. Referencebasedfourpulses warmred/yellowleftandcyan/whitecore/blue structure atnozzleright. Playerexistingtwo-pixelrearflare retintedred in one sharedscanline; bitmap/coverage/size/updateclock unchanged, not an enlargedplayerplume.
Runtime: bank5expandedart B000 (L4B400,L7B200), <=4096bytes each; originalbank6cache retained. NewvirtualframeIDs assignedbyactorIYL-indexed256bytecounter, fourposeswithoutnativeAI-scriptedmovement edits; selectedsmallactors retainnativecellalignedX presentation, bosses retain2pxsmoothing. Animation selector227-229Z80T/call, BC/DE/SP/IYpreserved. Existingmotionimage entrytableload calls appendeddispatcher; L1oldlarge2-IDselector disabled. New code/tablecompressedinimmutablebank1; installer usesexistingdecompressor, load-timeexpandsnewart thenexistingwarmup. No runtimeconversion or extra files. Cold/cache/resident full512KB layout retained. L4tightbudget usesboundedexternaloldpreloadpacket A9C7..B30C, rawB400;L7CEB1..D147 compiled-onlyboss sourceholdsboundedpacket, rawB200. Originalcachebyteidentity verifiedafter11cold/cachedjumps. FinalimmutableendsL1=342D,L3=2EB7,L4=37F6,L6=387D,L7=39B5, allbelow3A00hotloadcode; L1stomachdescriptor8 and terrain palettes/tokens unchanged. Compressedruntimeimage+extension supersedes legacyL_motion.asm alone; generator/manifestidentifycompressedcode.
Tests: exactinstruction Z80dispatcher8calls/group,4distinctframehashesforall13walkinggroups, sourcepointer/memorybounds andBC/DE/SP preservation pass. Actualordinary/boss routes observefourvisibleposes L1large/L3ground16/L6head/L7head; otherfamilies verifieddispatcher/data butnotallnaturallyencountered visually. All8boss-previewroutes passed, L7+700, L3finalcorrected+700.11cold/cachedjumps,12native640attributeinitializationaudits, bank5assetreadback, existingrawcacheidentity, actualL6death/respawn, L5LoadAll/title/physicalfire restart pass. Finalenginecorrection changesonlyL3; other7imagesbyteequalearlierall8-testedcandidate, finalL3andjumpsrerunpass. Actualplayerphasecachevalidatedall8. End-to-end comparableemulatorrouteframecounts withinabout1percent r80,includesboot/loading, notgameplayFPS orhardwareguarantee.
Builderrejections beforevalidbuild: assemblerDBline128limit/ORGindent; L4/L7capacity asserts ledtoexternalpackets; nofailedbuildtested. Oneassetreadbackassert accidentallyranbeforeloadbegan; movedtoload-completepointandpassed. Exactnativefootprintsandvisualframeinspection caughtinvalidfourthtileandexhaustwidth. AllTAPchecksums/64KBLEVEL/48KBSTARTreconstruction, source/terrain/commoncodechange-scope assertions andZIPCRCpass. Staticwhitelistinstaller+immutablepackets+compiled-onlyexternalpacketareas+playerflareattrs; HOMEgameAI/nativecollision/worldcodeunchanged. No referenceprojects/sourceZIPedits. Existing64KBstockcartridgeunchanged; thisreleaseisexpandedgameonly. Hardwarepending.
Exactinstalledart build/graphics/walker_runtime_r86/index.html andintegrated_artwork.png; GIF180msillustrativeonly. gameplay_L3_before_after.png inspected butthisearlycapturedoesnotshowengine/bot, so isnotartconfirmation. OriginalimagegenassetsretainedinprojectandactualRPCsourceprovenanceinmanifest. Scripts prepare_walker_runtime_r86.py,convert_walkers_rpc_r86.mjs,build_walker_runtime_r86.py,finish_player_flame_r86.py,render_integrated_r86.py,verify_four_frame_r86.mjs,verify_walker_game_r86.mjs,finalize_walker_runtime_r86.py.
Archive build/fullgame/walkers_exhaust_r86/RType_TS2068_r86.zip 7545f55647064a8a79ca236a59acf500a248db00979045c341a3d8f4de6ae99e 562507bytes.


163. Walker regression acknowledgement/restoration draft r87 (2026-11-07). User accepts L3yellow/exhaust, rejects other r86walkers and recalls approvedblue21..25/deeperheadwork. ActualRPCfunctions were used, but genericmaterialpreprocessing and new/AI sources displaced approvedpixelart; runtimealso strippedBRIGHT, so sourceconversionpreview wasnotexactinstalledcolour. Acknowledgedmistake. Located exactblue_21..25.npy andhead_deeper_0..3.npy. Draftrestores exactblues, earlierlarge/roundgeometry andfullgroundbodies, L6deeper32head; L7actualearliernative24head18/19/20/22 ratherthanwrongL6head24preview. Keptaccepted94/exhaustrawbytesfromr86. Draft13fourposegroupsunitpass; affected1/3/4/6/7routespass, extendedL3/L7, finalL7+700pass,11cold/cachedassetreadbacks/nativeattributeaudits pass. DetailedL7assetsneededbetterofflinepacketselection withsameZ80decoder plusboundedretiredsmallwalkersourceA998..AB4E packet; finalimmutableend399A, sourceboundsasserted. This remainsaDRAFT, noR87ZIPpublished, because usersteeredtocomparisonsbeforefurtherreplacement.

164. Interactive walker comparisons r88 (2026-11-07). User requests morecomparisons/candidates, keepsblue21..25conditionalonidentity. Exact5savedblueimagespresentedinline andunchanged; asynchronousidentityquestionstillpending, pagehasconfirmationselector. AcceptedL3yellow/exhaustuntouched; r86ZIPsha7545f55647064a8a79ca236a59acf500a248db00979045c341a3d8f4de6ae99e verifiedunchanged. No currentgameassetreplacement. Eighteditablecomparisonblocks: L6head32,L7head24,L7head32(1.33xgeometryproposal),Before31round,L7round,L1large40,L3ground32x16/32x24. Baseline/rejectedr86/sourceatcorrecttargetsize/threecandidates sidebyside. Sourcesprovenance explicit: head224/226/228/230verified, roundandgroundnativeidentityunverified, largepose4crouchneedswalk-gaitreview; no newAIreplacementart. Approvedblue isexcludedfromregeneration.
Actualr69RPCcoreCPUfunctions, linearadjustments, segmentcoverage andserpentineSierraLite worker reused; normalpalette selectedbeforequantization,noafterwardBRIGHTstrip. Astandardpairselection; B/Cadddocumentedsource-redcellconstrainttoavoidinventedred/magentaspeckles. Materialsourcetreatmentsclearlylabelledgray/rim/steel/warm, notclaimedidenticalpreviousapprovedart. Editablebrightness/contrast/saturation/gammaapplytoeveryframeofcandidate. BlobworkeranddataembeddedinHTML,noexternalfetch; synchronizedanimation/pause/step/interval/zoom,pergroupkeep/A/B/C/review,notes,localStorage,export/importversion88JSON. Includesexactblueconfirmation.
Default96candidateframesvalidatedthroughsameworker: legal8x1normalattributes,transparentblack.192changedsettingsframechecks pass with186changedoutputs, sourceredguard andnormalblackhold. Distinctcountsurface:ground24Bdefaultmergestwoframes(3of4); UIwarns ondefault/livecollapse,doesnotclaimfourdistinctatallsettings. JSsyntaxcheckpassed; actualbrowserUIwasnotautomated/noUIrenderclaim. priority_candidates.png andblue_21_25_keep.png inspectedasassetpreviews. Initialpreparerelse-token syntax typo fixedbeforeoutputs. Sourcepreviewinitialunscaled64cel clippingwaspreventedbydisplayingtarget-scaledrawinput. build/graphics/walker_candidates_r88/index.html. Scripts prepare_walker_candidates_r88.py,verify_walker_candidates_r88.mjs,verify_walker_controls_r88.mjs,publish_walker_candidates_r88.py; UI src/walker_candidates_r88.js. Currentplayableremainsr86; nohardwareclaims; stock64KBunchanged.


165. Saved r88 choices applied/new walker r89 (2026-11-07). Userconvref/rtype-walker-candidates-r88.json declaresblue=no, head32B settings52/59/82/0.87, large40C51/67/80/1.44, round3keep; otherentriesunreviewed. Parsedasdata, preservedfile. Exactr88worker/profile-source +selectedsettings reappliedtoall4celsL6head/L1large. Round3KEEP restores exactreviewbaseline31/32/33/32:3distinctnativeimages in4steploop; explicituserchoice takesprecedenceoverinventedfourthframe. UnreviewedL7head/otherfamilies unchangedr86. AcceptedL3yellow/exhaustrawbytes andplayerflare unchangedr86; L1stomachretained.
Newblue replacement options: A freshoriginalarcade1570/1572/1574+authoredfourth,1600/1602raising; Bnewimagegenreference-inspiredmechanicalgunwalker4walk+2raise, native32x24/24x24; Cmodestlylarger40x32/32x32proposalonly. Mainr89usesBbyimplementationjudgment, notclaimeduser-approvedart. SourcescomputedfromoriginalROMforA, newgeneratedsourcecopiedintoprojectforB/C; fallbackdefaultpathusedonlyifprojectcopyabsent. Newsource hasexplicitblue-huepalettecalibration, source-redpairguard, sharedfirst4sourcecanvas/bodyalignment; noAIclaimfororiginalarcadeart. Initialsoftalpha>=180includedwhitehaze; correctedsourcebinaryalpha>=230beforecrop/scaling, visualinspectionconfirmedcleanbackground. Allconversionnormalpalettebeforequantization, noBRIGHTstripcolourdrift. Bsettings56/54/76/1.55, sharedall6cels. Exactselectedhead/largecodesseparatefromnewwalkerproposalsettings.
Runtimegeneratorbasedonr86framework/r87betterofflineLZsameunchangedZ80decoder. BoundsL1immutable34E9,L3=2F3F,L4=3887,L6=386E,L7=3933 below3A00. L7usesexistingboundedretirednativewalker sourceA998..AB4E foronepreloadpacket, plusoldcompiled-onlyboss sourceAEB1..B147; newartB200 notoverlappingpackets/code. Missingpack_optimal_r89import correctedtouseexistingverifiedpack_optimal_r87beforevalidbuild. No partialfailedbuildtested.
Validation: exactZ80dispatcher/order/registerSPpreservation21groups pass; round3explicitexpectedunique3, others4walkingposes. Affected1/3/4/6/7gameplayroutespass, L3/L7+700;11cold/cachedjumps/newbank5readback/nativecacheidentity,12native640attributeaudits pass. Exactinstalledpaletteindices30selected/newframes matchsavedconversionorKEEPbaseline;33otherframesbyte-identicalr86 includingacceptedbot/exhaust. Completelevels2/5/8andplayerflarebyte-identicalr86. InitialRGBphotometriccomparisonfailedbecauseRPCpalette usesmeasuredapproxRGBvalueswhileemulatorrenderuses205primaries; correctedtoexactpalette-index/attributeverification, noinstalleddatawaschangedtohidefailure. AllTAPchecksums/64KBLEVEL/48KBSTARTreconstruction/staticchangescope/ZIPCRCpass. Hardwarepending; stock64KBcartridgeunchanged.
Replacementcomparison build/graphics/walker_selection_r89/index.html showsA/B/C atactualtargetsize, synchronizedfourwalking/tworaising/all6modes, actualRPCsliderssharedall6, export/importversion89JSON, andCsizeproposalclearlylabelled. MainbuildBexplicit. Earlierblue/r86baselineavailable; nofurtherkeep-blueconfirmationaskedbecauseuserblue=noresolvesit. JSsyntaxvalidated, actualbrowserUI notautomated. new_walker_options.png inspectedafteralphacorruptionfixandbluecalibration. AIoriginalsourcepreserved, replayusesprojectcopy, no referenceprojects/originalZIPs modified.
Scripts prepare_walker_selection_r89.py,convert_walker_selection_r89.mjs,integrate_walker_selection_r89.py,build_walker_selection_r89.py,finish_player_flame_r89.py,verify_review_application_r89.py,finalize_walker_selection_r89.py,publish_walker_selection_r89.py. Conversionjobs/userchoicesarecanonical; legacyinputs.profilesmarked superseded.
Archive build/fullgame/walker_selection_r89/RType_TS2068_r89.zip abcf246c05ecda4854fa636783e9db95d721a1dd2a903228bebbbb0459232b86 563335bytes.


166. Selected gunwalker optionA r90 (2026-11-07). Userconvref/rtype-new-gunwalker-r89.json selectsA,B39/C70/S100/G1.01;otherB/Csettingsaredataonly,notselected. Reconvertedactualr89Aoriginalarcadeprofiles withsameRPCworker/source-redguard andnormalpalette. Fourwalkingandtworaisingposes shareexactsettings. InstalledsharedfamilyL1/L4/L7, native32x24/24x24 unchanged. Threeoriginalwalkingcels plusalreadyreviewedauthoredfourth; raises1600/1602. SourceJSONpreserved. No newAIartgenerated.
Exact18installedframepaletteindicesmatchconvertedoutput;45otherframesbyte-identicalr89 includingallpriorapprovedhead/large/Before31, acceptedyellow/exhaust. Completelevels2/3/5/6/8byte-identicalr89; commoncode/terrainpalettes unchanged.21groupsZ80dispatchercontracts pass (keptBefore31still3uniquein4step loop); affected1/4/7gameplaypassed (L7+700),11cold/cachedjumps/bank5readback/nativecacheidentity and12native640attributeaudits pass. AllTAPchecksum/64KBLEVEL/48KBSTARTreconstruction/staticwhitelist/ZIPCRCpass. Immutableends3481/2F3F/3822/386E/38BE below3A00, existingRAMboundsretained. Hardwarepending,stock64KBcartridgeunchanged. Previewexactinstallednativepalette build/graphics/walker_choice_r90/chosen_walker.png generated; no browserFPSclaim.
Scripts prepare_walker_choice_r90.py,convert_walker_choice_r90.mjs,integrate_walker_choice_r90.py,build_walker_selection_r90.py,finish_player_flame_r90.py,verify_walker_choice_r90.py,finalize_walker_choice_r90.py. Archive build/fullgame/walker_choice_r90/RType_TS2068_r90.zip 8abec87edd92ba1e7b8971f183250320ee576d1cc326cfe7eb150f4dac53c20e 561632bytes.


167. r91 native source restoration fix (2026-11-07). User reports r90 L3 corrupt graphics and crash after level switch. Confirmed deterministic L1 -> L3 -> L2 -> cached L3: 66 of77 ship source bytes D2AD..D2F9 wrong at native init8721; build/fullgame/walker_choice_r90/native_source_repro.log and l3_native_source_audit.json. Runtime bank5 extension/raw sprite data overlaps A4AE..BFFF, which cached transition copies back to HOME C4AE..DFFF as original native data. Includes header fields; sufficient cause for graphics corruption and plausible crash cause, no separate hardware crash reproduction claimed.
Fix scripts/build_bank5_restore_r91.py installs33byte native restoration helper below A4AE in five modified levels1/3/4/6/7. L4 helper A48D..A4AD, spritehook A4AE. After old secondary/plan restoration, map2D copies live HOME C4AE..DFFF back to DOCK5 A4AE..BFFF, restores three original disk header bytes (L6 differs), restoresED/private stack/DE. Runtime extension/raw art discarded intentionally on uninstall and rebuilt on warmup. L1 original plan D1C9..D30C also overlaps new raw art, so immutable packed original plan replaces bank5-based plan restore using existing decoder. Other original plan layouts retained. Existing optimal offline packer used, unchanged Z80 decoder. Immutable ends3525/2F31/380B/383A/38DD below3A00. Raw runtime artwork byte-identical r90; complete levels2/5/8 unchanged. Original archives/reference projects/stock64KB target unchanged.
Validation final: verify_world_jump_r91 11switches + verify_native_revisits_r91 12switches all pass; every source byte C4B1..DFFF compared to disk before native init, only three intentionally mutable header bytes excluded. 25initial640attribute audits across both runs. Separate verify_restore_helper_r91 actual Z80 restores all6994bytes including static header, mappingED, SP, DE, executing prefix unchanged and HOME source unchanged for all5levels. verify_four_frame_r91 21groups pass. verify_walker_game_r91 affected1/3/4/6/7 gameplay pass, extendedL3/L7; actual gameplay captures jump/native_jump HOME bins and trace JSON under build/fullgame/bank5_restore_r91, not hardware images or measured performance. verify_death3_r91 actual L3 hit/death/respawn pass frames2673/2680/2973/2977. All TAP checksums,64KBLEVEL/48KBSTART reconstruction, scoped changes, compression identity/bounds, ZIPCRC pass. No new art preview or browser FPS claims.
During testing, initial whole-source assertion incorrectly included native three mutable header bytes; corrected invariant. Broader revisit test then genuinely caught L1 overlapped plan297wrongbytes, fixed with immutable backup and rerun. Attempted packed backups for all levels exceeded L4 immutable capacity; rejected build, narrowed backup to actual L1 overlap before final tests. An earlier gameplay run crossed a rebuild and failed; discarded, final run executed only after binaries frozen and passed. No partial build published.
Lesson: audit lifetimes of native source banks after overlays and after cached returns, not only raw sprite caches/current draw state. Audit original restoration sources too: they may overlap new allocations even when active render/cache bounds pass. Include all modified levels in cached revisit routes, compare native bytes before init, and assert safe executing-code boundary during restoration.
Release build/fullgame/bank5_restore_r91/RType_TS2068_r91.zip dd41895a08631b61ef1c06dec055d08197dad02b081561f6db94e071fdb65b8d 562423bytes. Replace complete rtype folder and RESET to clear stale resident banks. Real hardware confirmation pending.


168. L4 LR_025 speed investigation/trial r92 (2026-11-07). User reports L4 boss practically unplayable and level-change response too slow. Deterministic same480emulated60Hzframe workload after doubleB boss: historicalr67=3worldupdates,r91=3,r92=6. These are world progress counts over8seconds, NOT displayFPS or a measured hardware rate. Compared builds reach different subsequent game states; no claim of cycle-identical replay. LR_025 retains120x56 source footprint,26=96x64,27=96x88. Thus not a new enlargement or r91bankrestore cost; runtime L4 horizontal color synthesis was expensive alreadyr67. Profiles build/diagnostics/l4_speed_r92/masked_L4.json (r91),l4_historical_r67/masked_L4.json,l4_speed_r92_fast/masked_L4.json. PCcyclebuckets inbuckets.json; no diagnosticPNG produced. Actual L4gameplay HOME snapshots scene_L4_100..115.home.bin inbuild/fullgame/l4_speed_r92. Not hardware tests.
Changes: L4 visibility scanner uses cheap exact row-palette presence rather than full color synthesis. Full unshifted/unflipped8row cells return raw paired rows directly. Synth entryphase0fastpath; identical nonzero black-paper pairs can bypass remapping. 4096actualZ80row/color/flip/phasecases verify exact output and visibility equivalence. Equal-pair shortcut initially mishandled ink0/papercolor partial coverage and invisiblepalette0bitmapgarbage; tests caught both, constrained to nonzeroink/blackpaper before final build. Random mixed shifted-row aggregate is slightly slower5566185vs5676603cycles, so do not claim every shifted row sped up. Main speed benefit is removing horizontal synthesis for large L4pieces and avoiding redundant scans.
Explicit speed-trial tradeoff: large L4components25/26/27 use native horizontal cell steps instead of fine2pixel synthesized horizontal phases; fine2pixel vertical movement retained. Other bosses/movement unchanged. No artwork/palette/size/hitbox changes; all runtime art byte-identicalr91. 2xsame-workloadworldprogress, still substantial remaining world cost; player position changes147vs136 in8seconds, independently updated. Not advertised as fully smooth animation.
L4 IRQ level-key latch uses existing HOT_STATE bit7+number, no new RAM bank/state slot. L4 warmup copies bounded29byte wrapper to formerly unused HOMEFA33..FA4F, redirects HOMEFB00 firstCALL to it; wrapper preserves existingF930capture then checks liveplayer/currentlevel4 before mapping29 to L4bank5helper, returnsmap9. No changes to native secondary source copies. Installer executes bank5 under6D, thenreturns6F. Mainbank1hotkeyhandler expands12bytes to exactly3E00 feedback boundary; pending1..8requests are consumed only at safe main-loop boundary, not during partial drawing. Other levels ignore L4 bank5 helper. Brief4frameL then4framenumber2 test latchedframe52, acceptedframe67 (17frames after number began), actual disk-region switchframe322. Disk loading latency separate. Source-state reset and cached transitions verified; no claim of instantaneous asynchronous world abort.
Final tests verify_walker_game_r92 L4boss160updates with ROM/SP guards, native-horizontal/fine-vertical assertion; verify_native_revisits_r92 12cold/cached transitions and native source byte/attribute/cache checks; restore_helper fivelevels/all6994bytes;21fourframegroups;4096synthcases; shortkeys. Staticwhitelist: alllevelsbank1hotkeys, onlyL4compressedruntime/cachecode; native graphics source/terrain/palettes unchanged. All TAP checksums/64KBLEVEL/48KBSTART reconstruction, immutableend38EE<3A00, runtimeA000+2156<A9C7externalpacket, original bank5restore executionboundaryA4AE, ZIPCRCpass. Unchangedboot/rt.tap/RTCORE/RTPRELD, stock64KBtarget unchanged. No reference projects/source ZIPs modified.
Generated-script suffix cloning initially targeted r91test filenames; corrected r92builder/flarefinalizer to emit r92test files and restored r91 fixture imports/audited world-jump test. Existing releasearchives unchanged. Intermediate failedbuilds not published. Failed attempt to place IRQhook in original regionDB00 was rejected by static signature before mutation: that is native source data, not live HOMEgateway. Final hook installed at runtime afterwarmup in actualHOMEcode instead. This reinforces address-space distinction.
Release build/fullgame/l4_speed_r92/RType_TS2068_r92.zip 515fe51c8a0056e21de9b18b0c89c0c04d66e9a009ae70fcdf5ce5e3fdcf2b89 562785bytes. Replace complete rtypefolder andRESET. Hardwarepending; r91 retained as prior fine-horizontal comparison. performance_comparison.json/readme explicitly document tradeoff and remaining expense. Future larger gain: genuine precomputed phase residency/compiled painting needs explicit lifetime-safe allocation; do not reuse immutable bank5 sources again merely to fit phases.


169. L5 boss hardware lockup report / r93 bank repair (2026-11-07). User reports true machine lockup on jumping to L5 boss, last audio held. Build/previous-route question asked asynchronously; not yet answered, so do not assume user-confirmedr92. FreshL5 and L4->L5 boss scripts both pass on r92; twelve repeated boss jumps pass with IRQ/world-progress watchdogs (548updates,3612IRQs). Thus hardware lockup itself NOT reproduced and not conclusively attributed to this fix.
Static review found definite r92regression introduced by finish_l4_keys_r92.py: generic hotkey installer writes alllevelsDOCK1:3A00..3DFF. L5's full bank1 contains compiled Bellmite phase bits/palette-index payload (2400..3FE0 plus tail atDFB0), and has used HOME_VARIANT hotkey code in bank5/A000 ->HOME7B00 since r61. Generic installer missed this exception and changed972bytes of its boss payload. Originalbuild_responsive_startup_r61.py explicitly branches n==5 to HOME dispatcher and never writes bank1hotkeys there. r92staticwhitelist allowedbank1hotkeywrites on every level and gameplay guards did not compare originalL5phasepayload, allowing falsepass despite corruption. No evidence that corrupted palette-index bytes alone explain the reported hard lockup; graphics corruption is confirmed independently.
r93 copies r92 and restores entirelevel05_region.bin plusLEVEL05.TAP/START05.TAP byte-identicalr91 (regionSHA75d3ae7eff3a66e93715c3d9332d8a95f0e37693a3867920454215252a3b122a). OthersevenregionsandalltheirTAPs byte-identicalr92; L4speedtrial tradeoff and keylatch retained. No new art or timings. finish_l4_keys_r92.py now explicitly skipsL5; finalize_l4_speed_r92.py rejects anyL5regiondifference rather than whitelisting bank1. r93immutableL5region/payload/tapes contract added; do not rerun oldbrokenr92installer. r92archive preserved for evidence, DO_NOT_USE_R92.txt marks superseded.
Tests final r93: freshL5boss and L4->L5boss 160updates each, nativeboss descriptors8/30..33, ROM/SP guards; stress_l5_boss_r93 twelveactualdoubleBjump cycles,548updates/3612IRQs, no watchdog stall; verify_native_revisits_r93 twelvecold/cached routes, originalsource and nativeattributes/rawcache/residency guards. Exactfullimage/TAPbaselinecontracts all8, allTAPchecksums/64KBLEVEL/48KBSTART reconstruction, unchangedrt.tap/RTCORE/RTPRELD,ZIPCRCpass. No hardwaretest or screenshot claimed; gameplay scene_L5_100..115.home.bin andboss_level5.home/dock7 bins, l5_gameplay/l4_l5_gameplay/l5_repeat/native_revisits logs under build/fullgame/l5_bank_guard_r93. Initialstress driver stopped after10jumps to correct secondpress edge tracking; complete12cycle run performed afterward on bothr92/r93. Failed attempt to addbroadquiescingorother speculativechanges was not made; only confirmedbankoverwrite repaired.
Lesson: free-space contracts are target/level-specific. A generic allowed-address whitelist is insufficient: validate specialHOME_VARIANT dispatchers and immutable asset payload bytes independently. Emulator forwardprogress/guard success is not equivalent to assetintegrity nor realhardware lockup resolution. Maintain separate claims.
Scripts build_l5_bank_guard_r93.py,finalize_l5_bank_guard_r93.py,verify_walker_game_r93.mjs,repro_l4_l5_boss_r93.mjs,stress_l5_boss_r93.mjs,verify_native_revisits_r93.mjs. Release build/fullgame/l5_bank_guard_r93/RType_TS2068_r93.zip 6fc191080f22edc8b5d38410555d00da2c50083bb9a8d509694ced16365f50bc 563118bytes. Reset andreplacecompletefolder. Hardwarelockupconfirmationpending; stock64KBunchanged; referenceprojects/sourceZIPs unchanged.


170. Continuing L5 hardware freeze / R94 IRQ isolation DIAGNOSTIC (2026-11-07). User thinks update installed but still crashes; clarifies boss is just partly onscreen and slowly moving upward when machine freezes with sound held. This occurs after shortcut construction, so an init-only guard is not sufficient. Exact hardware freeze still NOT reproduced. r93fresh/afterL4/repeatedbossjump tests pass. Added active movement/firing profile,112clipping positions (bottom/right/wrapped coordinates), Iregister andIM2vectorendpoint audits, and synthetic asynchronous IRQ test (3jumps,91additionalIRQs) onr93; no hang/I/vector corruption reproduced. These are emulation diagnostics, not hardware findings.
Actual audit found gameplay reentrancy during boss reconstruction:12r93jumps logged1407callback entries, including275player ticksE400 and274projectilephase5883 while native1485/8721rebuilding; someF930calls were inactiveplayer and are not equivalent to drawing. Timing/ownership hazard is confirmed; causality for reported upward-emergence freeze remains unproven. R94 additionally excludes gameplayIRQcallbacks when savedrawF4 has DOCK4 selected, the L5rawdraw/preparation mapping. Music/nativeIRQ processing is not explicitly disabled or muted, but no claim of AYwrites during rawIRQ or nativeinit: those counters measured0. Overall gameplay AYwrites24170, positive, with zero gameplaycallbacks in508guardedIRQs.
Allocation-safe final R94: L5-only84byte boss hook retains entry1FA3 and special trampoline1FF7..1FFB=3E19D3F4C9. ExistingFD4B latch uses4duringrebuild; finishrestores3. L5warmup calls a64byte installer atDOCK6DFC0..DFFF, beyond palette dictionariesDF80..DFB0 and packedtailDFB0..DFC0. Installer preserves conditionalINIT_CACHE, executes frombank6 underDD->5D so code/DOCK2stackremainvisible; it returns5D to oldwarmup's POPs/5Dexit. Copies22byte gameplayIRQgate to unusedHOMEF89A..F8AF, tenbytefinishstub toHOMEFA33..FA3C, patchesHOMEFB01 target. Does not change DOCK1bossphasepayload or DOCK5source/header. Gate discards onlyFB03return when blocked and returnsHL7A8A to IRQcaller; otherwise jumps originalF930. L4warmup reinstalls its originallatchstub; on L5reentry freshwarmup reinstalls L5guard. Native music/codeF8B0..FA33 preserved. Rawdrawguard remainsinstalled afterL5 until anotherinitializer replacesit, so this is explicitly an isolation trial, not a finalized global IRQpolicy.
Visible build ID: loader's16byte PREPARING GAME string replaced same-length R94 PREPARING; launcher/demandloader/rt.tapdata+checksum updated withoutresizing. All8assetdebugheaders R94 DEBUG. L4runtime/art/phasepolicy unchanged. No graphics,terrain,size,hitbox changes; stock64KBtarget unchanged. Reset/completefolder replacement required.
Final tests: verify_l5_live_guard_r94 twelvejumpcycles, exactlivegate/fullfinishbytes,4->3sentineltransition andcorrect8B06continuation,508blockedIRQs withzeroF930/E400/E40C/5883/8B06callbacks therein,24170overallAYwrites. FreshL5 and L4->L5 boss160updates ROM/SPguardspass;12cold/cachedlevelrevisits/native-source/attributes/cachechecks pass. Final8secondactiveinputsample r93=27worldupdates/92playerpositionchanges, R94=31/80; notdisplayFPS/hardwareperformance and subsequentstatesdiffer. Player/fireupdates canbe lesssmooth; tradeoffisexplicit. Allimmutablephasebank/dictionary/tail/nativegraphics checks,1FF7trampoline/liveadjacentaudiocode boundaries,64KBLEVEL/48KBSTARTTAPreconstruction/checksums,RTCORE/RTPRELDidentity,loaderlabelscope/ZIPCRCpass. Files l5_gameplay,l4_l5_gameplay,native_revisits,live_guard,l5_active logs andscene_L5_100..115.home.bin underbuild/fullgame/boss_guard_r94; baselineclip/audit logs underr93; no newdiagnosticPNG or hardwaretest claimed.
Important rejected drafts before publication: initialgeneral84->93byte boss expansion would overwrite L5's1FF7 return trampoline; rejected and L5-only84byte hook used. A24byte HOMEgate crossed22byteF89A gap into F8B0audio; corrected to22 and liveF8B0..FA33exactidentity asserted. Expandedfinishstub initiallystillcopied7of10bytes; actual livebytecontract caughtmissingfinalJP despite forwardprogress tests passing. Copylengths nowderivedfromassemblerlabeldifferences; strictfinish/continuation test added. Intermediate tests crossingthese changes discarded; finalbinaries frozen and routesrerun. Early AYduringinit/rawIRQ assertions failed because these scopes had0writes; finalvalidation records scopehonestly and onlyassertsoverallAYoutput. Do not reuse stale intermediate boss_irq_gate artifacts; canonical finalfiles l5_serial_guard.asm/bin,specialL5boss_preview_r94.asm andbuild_boss_guard_r94.py. Existing releasedr93archive unchanged.
Lesson reinforced: assert exact destination and executable return continuation, not only checksum/sourcepacket or apparent forward progress. Old ROM padding can contain specialized trampolines. Hardware diagnosis still needs confirmation with identifiablebuild; do not label this as a provenfreeze fix.
Release build/fullgame/boss_guard_r94/RType_TS2068_r94_diagnostic.zip bdd9ca7aebf6a099ab968ee6a0089858ac2fcf7bc20bcc48f4bd632031597d90 564299bytes. Hardwarefreeze unresolved pendingsameupward-emergence test withvisibleR94label. R93retainedbaseline. Referenceprojects/sourceZIPs unchanged.


171. R94 hardware failure photo / R95 checkpoint+cache diagnostic (2026-11-07). User13000.jpg confirms R94 still locks as first boss rows rise immediately above HUD. Source image .codex-remote-attachments/01a19855-5e8b-7c01-9834-206ac0fda11a/4db3419e-6a47-4ae7-b0cc-84a52b015085/1-13000.jpg leftunchanged. Ship is low and BEAMbarfull/charge graphicvisible; treated as a test clue, not proof of cause. R94 IRQisolation has NOT resolvedhardwarefailure. No hardwarefreeze reproduced in emulation; do not describe R95 as afix.
Additional r94photo-like test: low ship, heldfire360frames thenchargedbeamrelease,960frames total;1beam,84worldupdates nohang. r95version83updates/1beam. Heldfire before native startup completed initiallystalled a test harness; stopped it, startedfireonlyafter livegameupdates, bounded15000frames,2actualbossjumps passed (108updates/1217IRQs). Not claimed as a gamefreeze reproduction. Existing112bottom/right/wrappedclippingcases pass again.
R95 checkpoints via documented FE lowborderbits (values0..5 only; beeperbit4neverwritten):1blueactorphase/cachechoice;2redcellvisibility/clippingplanning;3magentaplanningreturned/nativecelldispatch;4greencacheselection/overlapblend;5cyannativepairedrowcopy;0blackcellreturned. Mainmotion addsmarkers withdeadA, preserving callerstack/flags; two9bytePUSHAF/POP AF tail wrappers reuse existing unreachable DOCK4:890A..891F after verifiedunconditionalJPoursat8907; CALL8C00 andCALL1A6E retargetwrappers withoutchangingstackdepth. LowROM097B adds OUT(FE),A afterexistingXORA using exactlytwoFFpaddingbytes beforelivehelper0986. MotioncompiledDC50..DE99 (<DF00backup), warmupDDEF/restoreDE1B absoluteROMgatewayreferences regenerated. No code/data reuse beyond explicitly checked padding;1FF7specialtrampoline andR94liveguard unchanged.
Firstcompiledbossdraw now checks expandedcore7040bytes atDOCK1:2400..3F7F andsphere2304bytes atDOCK6:C000..C8FF against16bitadditivesums from acceptedrawphaseassets. Newchecker uses121bytes of zero/reservedDOCK7:E340..E3EF after64coordinatebytesE300..E33F andbeforecacheflagE3F0. E3F1newcheckedflag resets duringwarmup underDD beforeR94installerreturns5D. Checker preservesAF/BC/DE/HL/SP, leavesDD; noIRQenabledwithinthisshortone-timecheck. Onmismatch it deliberatelymapsD3 with DI, fills HOME4000..57FF bitmapFF and HOME6000..77FF attributes6(core/yellow)or7(spheres/white), thenHALTs requiringreset. Sourcecode/stack notneededaftererror; video remainsvisibleevenif adapter hidesborder. These are diagnosticfailstops, not arbitrarygamecrashes. Adds brief one-timepause; sumsdetectcommondatafaults but are not proof against all RAM faults.
Visible R95 TRACE TEST startupmessage replaces R94 PREPARING atsame16bytelength; allassetdebugheaders R95 DEBUG. Loadingrt.tapblockchecksums recalculated, RTCORE/RTPRELD unchanged. Artwork,dimensions,palettes,collisiongeometry,phasepackets andspecialL5trampoline byte-identicalR94. R94IRQguardtradeoff retained; tracingperturbstiming, so absenceofhangwouldnotestablishfix.
Testsfinal: L5boss160updates allcheckpoints1..5 and0 observed (counts15008/1339/1339/1339/15002/9463), noyellow/white innormalpath;112clippingcases complete; checker goodpath102817steps preservesregisters/SP, flippedcorebyte89758steps solidyellow+HALT, flippedspherebyte115110steps solidwhite+HALT withbitmap/attributecontent asserted. Twelveguardedbossjumps strictlivestubs/criticalcallbackexclusion pass;12generalresidentroutes plus9L5-specific[5,2,5,4,5,1,5,6,5] routes pass withnative-source/cache/residency checks;2heldchargejumps pass. Lowship/chargedbeamrelease scenario pass. AllTAPchecksums/64KBLEVEL/48KBSTART reconstruction, source/art/dictionary/trampoline/phasepayload/codeallocation whitelist, relocatedentrycontracts, ZIPCRC pass. Logs/checkpoint_validation/cache_integrity_validation/l5_revisits_validation/charged_jump_validation underbuild/fullgame/l5_trace_r95; gameplay scene_L5_100..115.home.bin diagnostic RAMsnapshots, no generatedPNG/hardwareoutcome. Everyinjectedfailstop is explicitlylabelled.
Hardware-reference check: TS2068 Technical Manual portmapTable2.1.13-1 atPDFpage34 documents FF andF4read/write; speculation that IN(FF) was invalid is refuted and no suchpatch made. FEborder/soundbits checkedSection2.1.13.2 PDFpage35. https://www.retromaniek.pl/wp-content/uploads/2019/09/Timex-Sinclair-2068-Technical-Manual-best.pdf. Read-onlyinspection of localTSPicoreferencefiles; no firmwarechanges.
Scripts build_l5_trace_r95.py,finalize_l5_trace_r95.py,verify_l5_integrity_r95.mjs,verify_l5_checkpoints_r95.mjs,verify_l5_clipping_r95.mjs,verify_l5_live_guard_r95.mjs,verify_l5_revisits_r95.mjs,verify_l5_charged_jump_r95.mjs,repro_l5_low_charge_r95.mjs. Release build/fullgame/l5_trace_r95/RType_TS2068_r95_trace.zip 6118253d5e0bfd878f987b25be68505dce698b06fc17af724b4f889b51253794 564923bytes. Requestwhole-screenphoto/frozenbordercolour on hardware; solidyellow/white is deliberatecachecheckfailure. Reset/completefolderreplacement required. Hardwarecauseunresolved;R95diagnosticnotproductionfix;stock64KBtargetandreferenceproject/sourceZIPs unchanged.

172. R96 L5 row-selector rollback trial (2026-11-08). User reports R95 border froze RED, after changes; last working release unknown. RED brackets whole-actor visibility/clipping planning. This narrows investigation but does not establish the precise hardware cause. User prefers targeted rollback over testing old releases. Restored exact 450-byte r58 row-selector prefix, removing CALL PREPARE_CELLS from L5 motion. Retained current cache decoder/layout, artwork, 2px motion and player engine. Cache751bytes at8C00..8EEF; INIT8DC2; motion559bytes DC50..DE7E, warmupDDD9/restorationDE01 gateways regenerated. Empty-row CALL1AF6 replaced by threeNOPs to preserve background ownership, matching preplanned empty-cell semantics. Base r93 removes R94 IRQisolation and R95 diagnostic experiments. All other levels identical r93 except same-length debug label. Stock64KB target unchanged.
Tests:256 phase/orientation pixel cases,96 foreground overlap cases,112 clipping positions, empty-row pixel/ownership preservation, exact cache expansion/restoration PASS. Isolated raster fixture uses metadata3 to exercise owned compositor and masks IRQ; irqCount0 explicitly recorded. Old copied component fixture with metadata0 also failed against unchanged r93; not used as rollback evidence. Fully initialized live gameplay separately tests interrupts. L5 160updates/13actors,12 repeated boss jumps (548updates/3612IRQs), nine cold/cached routes [5,2,5,4,5,1,5,6,5], L4-to-L5 entry, active player/rapidfire480frames, low-ship charge/release960frames (1beam/83worldupdates) PASS. Active sample92positionchanges/279travel; no claim of hardware FPS improvement. Hardware lockup NOT reproduced; r96 hardware confirmation pending.
Diagnostic images build/fullgame/l5_row_restore_r96/L5_boss_comparison.png and build/fullgame/l5_bank_guard_r93/L5_boss_comparison.png decoded from actual gameplay HOME bitmap/ECM attributes and visually inspected: current organic boss/machinery renders correctly; poses/timing differ. Asset previews are not hardware verification. All65536byte regions/LEVEL and49152byte START reconstruction/checksums, immutable DOCK1 payload/DOCK7 data/raw graphics, source backup/dictionaries, 1FF7 trampoline, code change whitelist, loader same-length label andZIPCRC PASS. Finalizer initially referenced two absent baseline derived phase files; corrected to compare actual raw core_pairs/sphere_pairs and immutable bank payloads; final runPASS.
Scripts build_l5_row_restore_r96.py,finalize_l5_row_restore_r96.py,verify_l5_row_components_r96.mjs,verify_l5_empty_rows_r96.mjs,verify_l5_clipping_r96.mjs,verify_walker_game_r96.mjs,verify_l5_revisits_r96.mjs,stress_l5_boss_r96.mjs,repro_l4_l5_boss_r96.mjs,profile_l5_active_r96.mjs,repro_l5_low_charge_r96.mjs. Reports/logs under build/fullgame/l5_row_restore_r96; profiles under build/diagnostics/l5_active_r96 and l5_low_charge_r96. Package RType_TS2068_r96.zip SHA256 ca0c76176ca4e6742ba9f1d55065fb94f42a299550072ac7a28b8123b08627fb,563418bytes. Reset and complete rtype folder replacement required; confirm startup R96 ROW RESTORE and test same L5 emergence. Reference projects/source ZIPs unchanged.

173. R96 hardware still freezes; R97 cell-atomic trial (2026-11-08). User: got slightly farther, froze BLACK, border had been changing. Exact route: load only L5 then B/release/B to boss, no level-switch or LoadAll requirement. R96 removed R95 draw checkpoints; remaining border OUTs exist in loader/control code, so black is NOT proof of a particular drawing stage. R95 frozenRED remains earlier evidence, rollback alone did not fixhardware. No confirmed precise root cause; hardware freeze still unreproduced in emulator.
R97 based on R96. Only two EI instructions become NOP: DOCK4:8C89 selector and89B2 compositor, keeping temporary raw-cache source/paired-plane drawing atomic. Normal entry helper01C8 retainsEI between cells; normal IRQhandler unchanged. Explicit preserving9byte tail wrappers in unreachable890A..891B markGREEN select andCYAN copy; return097B restoresI84/9000 and marksBLACK using2formerlyFFpaddingbytes. Callerflags/stackdepth preserved; artwork,size,phasecache,motion,collisiondata unchanged. No new RAM allocations. This is an IRQ/bank isolation trial, not a claimedfix; may affect responsiveness. Static whitelist rejects any other L5 difference except debuglabel; sevenotherlevels identicalR96 exceptdebuglabel.
Direct L5/doubleB160bossupdates PASS; all13bossactors/renderdescriptors; live normalIRQs2278,6887916instructionvisits in tested rawbank selector/compositor ranges withIFF1false throughout. Checkpoints countsBLACK21500/GREEN21495/CYAN9072. Twelve repeatedjumps PASS,548updates/3612IRQs. Lowshipcharge/release960frames PASS1beam/83worldupdates,moves41/travel192 (same positionalcount asR96 sample, nothardwareFPS). Pure raster IRQmasked256phasecases/96overlaps,112clippedpositions andempty-rowownership PASS. Reports logs inbuild/fullgame/l5_cell_atomic_r97; lowcharge reportbuild/diagnostics/l5_low_charge_r97. Actual gameplay RAMcaptures scene_L5_100..115.home.bin, no newPNG generated or visuallyreviewed thistrial. Tests do not reproducehardwarefault.
Buildscriptinitially omitted fixtureJSON dependencies: failed ENOENT before emulation, corrected dependencycopies. Finalizerinitially expected unrunresident-route report; corrected to require actualatomic-validation report; no cachedrouteclaim forR97. Final staticcontracts immutableDOCK1/DOCK5..7/rawassets/motion/trampoline, whitelistedinstructionpatches, allLEVEL/STARTreconstruction/checksums, loaderlength, RTCORE/RTPRELD unchanged andZIPCRC PASS. scripts/build_l5_cell_atomic_r97.py,finalize_l5_cell_atomic_r97.py,verify_l5_atomic_r97.mjs,verify_walker_game_r97.mjs,stress_l5_boss_r97.mjs,repro_l5_low_charge_r97.mjs,verify_l5_row_components_r97.mjs,verify_l5_clipping_r97.mjs,verify_l5_empty_rows_r97.mjs. Package build/fullgame/l5_cell_atomic_r97/RType_TS2068_r97.zip SHA256 e17725407c8ebd2b3ee7242cf69785dc2a40820c30fecccc86e5c61e4b43ecc3,563366bytes. Reset/completefolderreplacement,R97 CELL TEST; repeatdirectL5/doubleB route and report frozenborder ifany. Hardwarepending;stock64KB/referenceprojects/sourcearchivesunchanged.

174. L5 cold-start handoff reproduced and repaired, r98 (2026-11-08). Hardwareuser r97 reaches70/70 thenCELL TEST andblack; clarified afterload, notinitialloaderfailure. Earlier statement attributing this to an r97-onlystartup regression was premature. Newtests selecting5duringinitialload reproduced SAME failure in r96 AND r97: region4,bootneverentered,titlecount0,PC02EE,SP0500,IFFfalse. DefaultL1boot and selecting5onlyaftertitle did notexercise thisroute. Earlier gameplay tests selectedafterboot and patched91F2 gameover; they did NOT establish coldL5startup. scripts/compare_startup_r97.mjs andcompare_selected_startup_r97.mjs; reports startup_comparison.json/startup_selected_comparison.json inr97folder. No newhardwarecause assumed fromblackborder.
Confirmed codefault: r96 rowrollback moveswarmup fromDDDC torDDD9. Builder updated level-switchgateway near0DC0 but missed coldgateway00D4. Its JP at00D8 stilltargetedDDDC, entering the final addressoperand8E of fourbyte ED73EA8E (LD(8EEA),SP). That skips savingMAIN_SP and executes operandasopcode. Source/copy mismatch accounts for actualcoldstart emulatorfailure. r98 changes00D9..00DA toDDD9 and staticallychecks bothcold andruntimegatewaytargets. Fix independent of original laterbossfreeze. R97twoEI->NOP isolationreverted to r96 behavior; explicitgreen/cyan/black wrappers retained; no othergameplay/art change. Othersevenlevels unchangedr97 exceptdebuglabel; bankpayload/coregraphics/motion/trampolineidentical.
Exact startup/title test withoutgamecodebypass: defaultL1 boot1540/titlepublications232/1474IRQs, initialselectedL5 boot1653/titlepublications116/699IRQs, correctregions0/4; nofatal. BeforefixselectedL5boot-1/title0 bothr96/97. ExactearlyselectedL5 thenstart/doubleB test160postbossupdates PASS;12repeatedjumps fromearlyL5startupPASS (548updates,3485IRQs,7264frames). Gameplaystress retainsgameoverbypass91F2 so distinguishedfromunmodifiedtitle/startup. NewgameplayRAMscene_L5_100..115.home.bin andstartup_L1/L5.home.bin generated; no newPNG orvisualQAclaim. Static patchwhitelist onlycoldtarget/twoEIrestore/debuglabel; source/assets/layout/loaderlength/core/preloaderimmutability, allTAPchecksum/LEVEL64KB/START48KB reconstruction/ZIPCRC PASS. READMEinstructionexplanation corrected beforefinalZIP: failinginstructionisLD(MAIN_SP),SP,notLD A,(E3F0). Finalizerchecksactualtestsrun, no claimednewphase/clippingtest.
Scripts build_l5_cold_start_r98.py,finalize_l5_cold_start_r98.py,boss_motion_fixture_r98.mjs,verify_selected_startup_r98.mjs,verify_walker_game_r98.mjs,stress_l5_boss_r98.mjs. Future relocationmustauditALLabsolutegatewayreferencesincludingcold00D4 andruntime0DC0; mandatoryregressionselecteachspeciallayoutlevelBEFOREloadcomplete,notjustafterboot. R96/R97archivespreserved;DO_NOT_USE_R97 notice. Release build/fullgame/l5_cold_start_r98/RType_TS2068_r98.zip SHA256 0ee662b3411683c4cbfd6f481d48a9ad9a1ee270c458d116dc118b55bb4cbf29,563578bytes. ConfirmR98 START FIX,resetcompletefolder,earlyselectL5andB/release/B. Reproducedstartupbugfixedinemulation; realhardwarestartupconfirmationandoriginalL5bossfreezestillpending. Stock64KB/externalreferenceprojects/sourcearchivesunchanged.

175. R98 hardwarefire reboot; conservative rollback and IM2 layout repair r99 (2026-11-08). User reports startup began, then fire causedcrash/reboot. Acknowledgedregressionprogression; no furtherhardwarecauseclaimed. Readstate/history. New no-gamecode-bypass coldL5 tests fireat0/300/800frames afterboot1653, thenrapidfire:399/424/388worldupdates,4276/4362/4278IRQs, noHOME-ROM execution/reset/fatal. Thus hardware reboot not reproduced; don'tclaim this testfixesit. Reportsr98 unmodified_fire_validation.json/log. Compare r84->r93 L5region: only9shipflamephasebytes changed; originalL5executionnotrecentlyrewrittenbeforediagnosticseries, so broadrecent-codeassumptionnotproven.
Auditconfirmed temporaryI8F table8F00..8FFF wasoverlapped by r65 pauseglyphs8F10..8F3F andkeyboardbridge8F40..8F71. 98bytesnon5B produce99non5B5Bvectorentries. TSRun/z80.js irqZ80 hardcodes lowvectorFF; previoustestscoveredonlylastentry. HardwareactualvectorNOTmeasured, so defectnotestablishedasrebootcause. Correcttableforarbitraryvectorsandreservefullpage; don'tconfuseinjectedvectorrobustnesswithhardwareevidence. EarlierIvectorauditonlycheckedIand9000,missinginteriorpagecontents.
R99 rolls ALLr94-r98L5executionexperimentsbacktor93 (includingplanner,rowselector,IRQisolation,tracing,coldgatewaychanges), retainingr93assetoverwritefixandallgraphics. Originalcold/runtimewarmupDDDCgatewaysmatch. OnlyL5UIrelocation/debuglabelandloaderlabeladded: reassembledui_home.asm old365bytesreproducedexisting315bytemain+50bytekeyexactlybeforechanges. Newbridge8B30..8B61,font8B70..8B9F inassertedFFcompositorpadding8B30..8B9F; compositorvariablesend8B21 andboundaryscratch8BF0..8BFFpreserved. MainUI315bytes9EA0..9FDA regeneratedonlyforrelocatedreferences. Table8F00..8FFFfilled5B; temporary9000endpointhelperunchanged. Other7levelsidenticalr93exceptdebuglabel. Art/cachepayload/motion/nativecodebitidenticalr93 outsideUIranges.
Validation:unmodifieddefaultL1boot1540/title232 andearlyL5boot1653/title116pass; no bypassinstartuptest. No-bypassfiretimings0/300/800passsame399/424/388updates. EarlyL5/doubleB160postbossupdatesPASS;12repeatedentries548updates/3485IRQsPASS (stressuses91F2gameoverbypass, explicitlydistinguished). All256vectoraddressescheckedfromlive rawmapping5F with9000endpointset5B,alltarget5B5B; actualIRQhandlerreturnprobes00/FFpreserveSP/mapping/I. Other254entrieshaveidenticaltarget; notclaimed256separatehandlerexecutions. Initialtestattempted256identicalhandlerreplaysandranlong; interruptedwithCtrlC, boundedtestreducedto2actualreturns+256targetchecks thenPASS. ProbeoldBadEntries99. Pause/resumeexactbitmap/ECM/audio/worldfreezePASS,64joystickcombosbothsocketsPASS,unusedbitsnotfire. Movedkeyboardbridgeitselfreassembled/staticaddresscontract; no newmanualkeydefinitiontestclaim. No newPNGgenerated/visuallyreviewed; gameplay/homecapturesunderbuild/fullgame/irq_layout_r99. EarlierfiringassertsnoHOME-ROMexecutionafterboot; neitherhardwarefirefaultnorlatebossfreezereproduced.
FinalizerwhitelistsUI/tablechangesonlyagainst r93, verifiesall8regions/TAP64KBLEVEL/48KBSTARTreconstruction/checksum/RTCORE/RTPRELDimmutability, cold/runtimegateways, immutableart/1FF7trampoline/motion/sourcebanks, loaderonly16bytelabel,ZIPCRC. Scripts build_irq_layout_r99.py,finalize_irq_layout_r99.py,verify_selected_startup_r99.mjs,verify_cold_fire_r99.mjs,verify_all_vectors_r99.mjs,verify_pause_r99.mjs,verify_walker_game_r99.mjs,stress_l5_boss_r99.mjs. Releasebuild/fullgame/irq_layout_r99/RType_TS2068_r99.zip SHA256 fa1d6a4d67b854f1acd5e3495dff564eac30bfc6b4d0b2175de00bbfdaa58c5a,565039bytes. Resetcompletefolder/R99 PREPARING. Do NOTcallr93lastconfirmedhardwaregood (unknown) orclaimrebootfixed. Stock64KB/referenceprojects/sourcearchivesunchanged.

176. Hardware confirmation and clean release promotion r100 (2026-11-08). User confirms r99 "yes that's working again now." Record scoped to reported regression route; noall-levelhardwareclaim ormeasuredIRQvectorclaim. r99archiveimmutable; newhardware_confirmation.json adds provenancewithoutrewritinghistoricaltests. r100promotesr99withONLYsame-length release/info labels (R100 PREPARING/R100 INFO); no executablebehavior/art changes. No r94-r98experimentsreintroduced. Full8leveldisk/512KBpackage;stock64KBtargetpreservedseparatelyunchanged.
Builder pinsr99ZIPhashfa1d6a4d67b854f1acd5e3495dff564eac30bfc6b4d0b2175de00bbfdaa58c5a andverifiesTAPinputsagainstarchive. Freshr100unmodifiedL1/earlyL5startup andthreefiretimingsPASS; all8levelregionsversion-onlyidenticalr99,64KBLEVEL/48KBSTARTreconstruction/allTAPchecksums,boot/core/preloaderimmutability, L5full8F00vectorpage, bothwarmupgateways/1FF7trampoline, loaderlabel-only, ZIPCRCpass. Earlier r99vector/boss/pause/joystickcoverageinheritedbybinaryidentity, notclaimedrerun. No newdiagnosticPNG; startupRAMcapturesandlogsunderbuild/releases/r100. Releasehardwarebaseline r99; noadditionalr100hardwaretestclaimed.
UpdatedREADMEcurrentheader/historicalboundary, PROJECT_STATEcurrentheader, docs/CURRENT_RELEASE.md, AGENTSmemory/gateway/regressionrules, src/l5_ui_release.asm correctedplacementsource, reusablebuild/finalize/releaseentry scripts, release_manifest/SHA256SUMS/latest.json/latestZIP. Originalhistoricalnotes/archivespreserved. Release build/releases/r100/RType_TS2068_r100.zip SHA256 a73683bbca15a94b1e6f978c5f1e38f5b4c4be6dc7337ea503a560726d0cb6c8 564759bytes. Reset/completefolderreplacement. References/sourceZIPsunchanged.

177. L1smallwalker/L2terrain/exhaust artwork audit and r101 offline comparisons (2026-11-08). User reports smallL1walkerstrange, largeacceptable; L2sprites/terrainstillweak,rocketexhaustunimproved;confirmedL@meansL2. AskedlargeL3plumevsplayersmallflame clarification asynchronously; nopendinganswerassumedrequired. Stable r100 preserved byte-for-byte; no release/latestpointer change. Auditedactualr100walker_runtime andrawart: L1smallIDs21-25 are newlyredrawngunwalker32x24fourposes; largeunchanged. L3exhaustIDs34/35have48x16fourruntimeposes. Separateplayerflamefinish_player_flame_r90.py ONLYretints twoexistingflarepixels,notrequestedreferenceplume. Generalr73integration explicitlyEDITS[2]={},EDITS[3]={}; priorL2_003..006heldforreview, notsilentlyacceptednow.
Capturedactualr100earlyL2gameplayHOME atupdates8/16/24 (coldselectedL2,boot1610,24updates/frame2651). Renderedcurrent_scene.pngfromL2_16.home.bin; terrainmostlyyellowconfirmed. Comparisonsuseactualr100runtimeart extraction, correctisolatedL2heads3/4fromsavedarcadesource(no withdrawnneckcrops), priorarcadebluearmourwalkerfourframesvsrefinedcurrentgunwalker, andauthoredrocketphotograph-inspired48x16plume.White/blueatrightnozzle,red/yellowlefttail. Notclaimedarcadeexhaustextraction. ConversionusesactuallocalRetroPixelConverterCPUfunctions/serpentineSierraLite, sharedfamilysettings; scalingbeforeconversion. Plumeredrawisapixel-artstudy,notnewAIimage. Currentlargewalkeruntouched.
Terrainmaterialstudiesretain256x160existinggeometry/silhouette/holes,olive/ivoryandorganicred/creamdirectionsinformedbyarcadereference. Commonpairforeachscanlineislanduntil>=8blackpixelgap; all8horizontalshiftphasescheckedlegal8x1onterrainlayer. Thisisnotdirectarcadeterrainbitmapreplacement,notinstalled,notcollision/performancevalidation. VisualQA:olivequantizesmostlyyellow/remainstooflat;red/ivoryaddscontrastbutvisiblybands. ExplicitlymarkedNOTready/notrecommendedinpage,notpresentedasfinishedimprovement. Needbetterlocalmaterialdetail/geometricbreakplanningbeforeterrainintegration. Donotrepeatpreviousgaudypalette/gameplayregression. Rendered/inspectedcurrent_scene.png,scene_olive.png,scene_organic.png,walker_B_0.png,exhaust_0.png. All18RPCprofilesmask/normalblack/noFLASH/legal8x1PASS;2x8terrainshiftchecksPASS. GIFtimingillustrative,notmeasuredFPS. Sourceandconvertedframes/GIFs/HTML/validationunderbuild/graphics/l2_art_review_r101; scriptscapture_l2_art_r101.mjs,prepare_art_review_r101.py,convert_art_review_r101.mjs,publish_art_review_r101.py. r100hardwarebaseline/sourcearchives/referenceprojectsunchanged.

178. Photoexhaust provenance/live-path audit (2026-11-08). User reiterates priorphotoreferenceworknotincorporated. Locatedoriginalsavedphoto-derivedfour-frame sheet build/graphics/walker_runtime_r86/exhaust_source.png, visuallyinspectedalongsideactualr100L3_exhaust_current_0.png. Allfouractualr100runtimeframes224..227 exactlymatchcanonicalpackedoriginalr86photo-derivedconversion(192bytes/frame). Mappedonlynative34/35, whileplayerflameisaseparate2pixelretint. Thuscannotclaimphotoworkwaslostfromfiles;needdistinguishpackagingfromvisiblepath.
ScriptedL3bossencounter700updates/15948nativetargetsPASS, zero34/35actor-targetcalls/zeroexhaustruntimehooks; observed40bodyamongotherIDs. Commentaryidentified40asencounterdrawtargetbutthisdoesNOTestablish40isexhaust. ContactsheetL3_identification.pngshows40is80x16separatebody; DONOTblindlyreplacebodyorremapwithoutidentification. Norzeroactorhookscountsproveexhaustneverdrawsbyothernativepaths. Auditreportintegration_audit.jsonstateslimitation. No game/releasechanged; nofalsefixclaim. ExistingpendingclarificationlargeL3rocketplumevsplayersmallflameneededtoavoidwrongassetintegration. scripts/trace_exhaust_route_r100.mjs results/asset_identity/native_targets/actual_walker_draws underbuild/graphics/exhaust_integration_audit. Stable r100 retained. Previousnewr101authoredplumestudyisNOTtheapprovedoriginalphotoconversionandnotasubstitutefortracingit.

179. LargeL3rocketconfirmed; correctdirectplumedispatch r102 (2026-11-08). UserclarifieslargeL3rocket. Ordinary L3trace(noBBjump) findsnative34/35datareads atHOME8E9A/8D0B/1509 beginningu127, whileactor9172andcompiledhookneversee34/35. DedicatedHOMEF22D CALL8E85 thenCALL8CFD bypassedupgradedrenderer. Priorbosstestwaswrongroute; zerohookcountdidnotmeanabsenceofplume. Descriptor40isaseparatebody andisNOTreplaced. Originalphoto-derived4framesstillidenticalr100,nowactuallyselectedthroughcorrectcall.
Patch onlyregion3:HOMEF22D/sourceD22D..D232 sixbytesbecomeCALL01C8+3NOP. New25bytehelper01C8..01E0 usesasserted56FFpadding, invokesoriginal8E85lookup, provideszeroorientationAFstackslot,callsexisting1B14compiledgate/8CFDdraw,restorescaller's5BE4sharedID. Normalnativeowner80preserved(noincorrectspriteIDassignment). NoextraRAMbanks/artresize/rendererrewrite/playerflamechanges. Existing48x16frames224..227reusedunchanged. All7otherlevels,especiallyL5,bitidenticalr100. LoaderlabelR102 PREPARINGonly16bytetext/checksums;nootherloaderchanges. Originalr100ZIPhasha73683bbca15a94b1e6f978c5f1e38f5b4c4be6dc7337ea503a560726d0cb6c8verifiedunchanged;lateststablepointerretainedr100pendinghardware.
FinalordinaryL3rapidfirestress400updates/81plumecallscyclesall4frames;81returnchecksSP/IY/sharedID/nativeowner/savedinputBC/DOCK0codePASS;gameoverbypass91F2explicit. InitialBCreturnassertfailedbecause8CFDnormallyadvancesitsloopBC,correctedtochecksavedinputcoordinate; firstreadusedHOME DF3Cincorrectly,correctedtoDOCK6physical1F3C. No gamemutationswereaddedtosatisfytests. Laternativeownerassertexpected34failedbecause8E85lookupintentionallyretainsowner80;correctedtosnapshot/compareoriginalowner. FinaltestsallPASS. Separate3coldL3startup/firetimings0/300/800,no gameplay/game-overpatch:allregion2andpassed. Twelve cold/cachedlevelroutes/native-source/attributechecksPASS. Final25bytehelper rechecked afterearlier16/20bytevariants; noearlierpackagepublishedasfinal.
Renderedandvisuallyinspectedplume_before_after.png(initialworkingvariant)andplume_gameplay_comparison.png(final25bytehelpercapture)fromactualold/newordinary160HOMEplanes. Finalimagewhite/blueatrightnozzle,warmred/yellowlefttailvisible;originalbodyandplayerunchanged. ScreenshotcomparisonsarenotFPSmeasurementsorhardwaretests. Capturedordinary20..240HOMEbinary/PNGartefactsunderbuild/fullgame/photo_exhaust_r102 andbaselinebuild/graphics/exhaust_integration_audit. Noarcadeassetidentityguess/AInewplumeused.
Scriptsbuild_photo_exhaust_r102.py,verify_photo_exhaust_state_r102.mjs,verify_cold_fire_r102.mjs,verify_native_revisits_r102.mjs,render_photo_exhaust_r102.py,finalize_photo_exhaust_r102.py; source src/l3_photo_exhaust_bridge.asm; docs/photo_exhaust_r102.md. Finalscopewhitelist/sourceart/runtimeimage/playerphases/7regions/corepreloaderimmutability/allTAPchecksums/LEVEL64KB/START48KBreconstruction/ZIPCRCpass. Package RType_TS2068_r102.zip SHA256 df5552efa47174a45b79ef9737010b0e2a4eb89c3703fad9a526c4a90ba27ec4 566758bytes. Hardwareconfirmationpending;resetcompletefolder,ordinaryL3encounter(noBB). Stock64KB/referenceprojects/sourcearchivesunchanged.

180. Large L3 plume diameter r103 (2026-11-08). User requests plume diameter match nozzle. Actualr102last8pixelnozzlecolumn has16pixelverticalextent; oldphoto-basedcol32only4opaque pixelsandcol39transparent,visiblythinnerthanmouth. Widenedoriginalphoto-derivedRGBAvertically,usingcolumn-localalphabounds/rampfromx6tonearnozzle16pixels; original40pixelplumelength/48x16fullspritebounds retained. SameRPCsettings56/54/78/gamma1.65andserpentineSierraLiteacross4frames. Canonicalnormal-black phasepacking; overwritefinal8pixelnozzlecolumnfromr102raw toguaranteebyteidentity. All4renderedmouthcolumnsx39nonblack16pixels; noFLASH/brightblack.
Runtimeart remains2752bytes; only4exhaustframes'first160bytesmaychange, nozzle32bytes/frameandallotherartidentical. RepackwithinexistingDOCK1allocation:rawsource25A8unchanged,compressedruntimeimage2A20->2AE8(200byteslater),end2FF9<3A00. Runtimeimagebytesunchanged;onlyLDHLsourceimmediateDF? exactoperandDEE1 updated, recordeddiameter_contract.install_operand57057. Nofunction/gatewayrelocation,rendererbridge25bytesidenticalr102, noextraRAMbanks. All7otherlevelregions/L5/playerphases/sharedcore/preloader/nativecodeunchanged. LoaderlabelR103 PREPARING onlytextdelta. Do not confusecompressedsourceoffsetrelocationwithlivecodeentryrelocation.
Final81plumecalls/all4poses/81callerstatechecks SP/IY/sharedID/owner80/savedBC/code PASS during400updaterapidfirestress(gameoverbypassexplicit). Twelve cold/cachednative-source/attributelevelroutesPASS. Separate3coldL3startup/firetimingswithoutgameoverpatchPASS/allregion2. Staticrawchanged-bytewhitelist/nozzleidentity/runtimeimageidentity/packetdecode/boundaries/all8LEVEL64KB/START48KBreconstruction/TAPchecksum/ZIPCRCpass. Actualordinary160HOMEbefore/afterrenderplume_diameter_comparison.png visuallyinspected:broaderblue-whiteflowmatchesnozzle, warmlefttailretained. Fullordinary160PNGandHOMEcapturesrecorded. NoFPS/hardwareclaim; fixedspriteboundsnoadditionaldrawcells. Runtimeart_size_unchangedcontractrenamedfromambiguousraw_bytes_unchangedbeforerelease.
Scripts prepare_plume_diameter_r103.py,convert_plume_diameter_r103.mjs,build_plume_diameter_r103.py,verify_photo_exhaust_state_r103.mjs,verify_native_revisits_r103.mjs,verify_cold_fire_r103.mjs,render_plume_diameter_r103.py,finalize_plume_diameter_r103.py. Originalphotowork/r102/r100archivespreserved. build/fullgame/plume_diameter_r103/RType_TS2068_r103.zip SHA256 ef273367cf4ee4a28df5810d035a440c338ea5a3a519d1701fb788ae1cb89a8e 567449bytes. R103 PREPARING/resetcompletefolder;ordinaryL3notBBshortcut. Hardwarepending;lateststablepointerr100unchanged. Stock64KB/referenceprojects/sourceZIPsunchanged.

181. Correct plume/nozzle classification, full photo plume r104 (2026-11-08). Userattached codex-clipboard-14a64a94-2a33-429f-aecd-5906a1f90211.png markscheckeredbandbetweenredbars:thatisrocketexhaust,notnozzle. Acknowledgedr103classificationerror; priornozzle-columnpreservationcontractwaswrong. Asset-coordinateimage build/graphics/plume_diameter_r103/asset_coordinates.png generated/visuallyinspected, confirmscolumns40..47arelegacycheckeredexhaust; actualmechanicalrim/bodysitsbeyondplumesprite. Replacedcomplete48x16four-frameplumefromr103photo-derivedfirst40columns,rescaledhorizontallyto48beforeRPC. No oldlast8columncopy; all192bytes/frameeligibleforartchange. SharedRPC56/54/78/gamma1.65/serpentineSierraLite; normalblack/noFLASH/no brightblack. Full16pixeljoinheightpreserved. No unrelatedsmallwalker/L2terrainchanges.
OnlyL3virtual224..227pixeldataandpacked-sourceaddress/layoutchangefromr103; allotherart/nativebody40,mechanicalrim/playerphases/runtimeimage/25bytebridgeand7levelregionsidentical. No new RAMbanks/spritebounds/renderercode/cadencechanges. Compressedpayloadend 0x303e <3A00; artloadsource25A8retained, compressedruntimeimage 0x2ae8->0x2b2d; updateonlyexistinginstallsourceoperand. Sourcecodeentry/gatewaysunchanged. Frame40..47rawbytesasserteddifferentfromlegacyinall4frames. Materialartmatchnotclaimedhardwaretested.
Final400updateplumestress81draws/81callerSP/IY/sharedID/owner80/savedBC/codechecks/all4posesPASS,gameoverbypassnoted. ThreecoldL3startup/firetimingswithoutgameoverpatchPASS. Twelve cold/cached/native-source/attributelevelroutesPASS. Finalraw/regionchanged-bytewhitelists, runtimeimage/player/7levels/corepreloaderimmutability, packetdecode/boundaries/allTAPchecksum/LEVEL64KB/START48KBreconstruction/ZIPCRCpass. Actualbefore/afterordinary160HOME image full_plume_comparison.png generated/visuallyinspected:checkerbandgone,photoplumecontinuesrighttoseparatemechanicalrim;rimunchanged. No FPS orhardwareclaim. Originaluserannotationleftunchanged; originalr100/r102/r103archivesretained.
Scripts prepare_full_plume_r104.py,convert_full_plume_r104.mjs,build_full_plume_r104.py,verify_photo_exhaust_state_r104.mjs,verify_native_revisits_r104.mjs,verify_cold_fire_r104.mjs,render_full_plume_r104.py,finalize_full_plume_r104.py. Profilesunderbuild/graphics/full_plume_r104; gameplayreports/imagesunderbuild/fullgame/full_plume_r104. PackageRType_TS2068_r104.zip SHA256 daea992fe24347add60b7fba47f5dae49f1a8fab40d0339f9f34056f0748474b 567659bytes. R104 PREPARING/resetcompletefolder;ordinaryL3notBB. Hardwarepending;lateststablepointerr100unchanged. Stock64KB/references/sourcearchivesunchanged.

182. PhotographedL1roundwalker identification/improvementreview andarcadesnake ref (2026-11-09). User13021.jpg showsgroundwalkerbeneathshipandgrey-loopL1snake; askswalkerimprovementandarcadesnakeref. Identifiedbyactualr104runtimeart asnative53-56/virtual208-211roundfamily,notbluegunwalker21-25. All4stored24x24butvisible16x15,16x15,15x15,15x15. Existing AI-assistedr86gold/steelwalker source2172x724 sheetwasreducedwithlargeexcessmargins,discardingdetail. Earlierdesignexisted,butcurrentfootprintunderused. Currentruntime24pximagesdecodedfromr104L1_runtime_art.bin forcomparison(notstaleassetpreview).
OfflineAcorrectsmarginsusingcoloured-contentmaskRGB>35andsharedunioncropforall4poses; clearblue darkmetal; same24x24storage,visible24x23. RPC56/54/78/gamma1.65(sharedallframes). OfflineBactualarcadeL1groundwalker at24x24visible24x22; C32x32visible32x29needsnewallocation/overlapreviewnotinstalled. ROMcels256/258andcapturedpalettegroup7fromframe003300,objectx31,y192,w/h32. Cels260/262shownasboostposes,NOTusedasfakewalkingframes. B/C4posecyclesuse2originalwalkingposesand2explicitlyauthored1pixellegintermediates; noexactSpectrum/arcadeIDmappingclaim. B/Csettings52/54/65/gamma1.5. Firstlower-gammastudiesgaveexcessred; adjustedbeforefinalreviewto betterretainyellow/steel, stillallowuserchoice. ActualRPCextractedCPU+serpentineSierraLite,all12legal8x1/alpha-normalblack/noFLASH/no brightblackPASS;4distinctconvertedframesineachfamilyconfirmedbyspritepairhashes. GIF180msillustrative,notgameFPS.
ArcadeL1snakecontextverifiedinactualframe004800.png (also5100/5400); goldcircularshells/darksteelcentres/blue-whitehighlights andoverlappingconnectedsegments,unlikethinwhiteUconversion. Preparedsnake_arcade_context.png768x512from384x256capture,unchangedaspect; snake_arcade_strip.png800x240fromsavedROMsource100x30(nevercompresswholemultijointstriptoonecell). Earlierbuild_responsive_game.py r50takesone31x30jointcrop30,0,61,30,rotatesint24x24thenfitsunchangednativepalette; colour/detaillostnotfullfaithfularcadeupdate. Currentgameunchanged; snakeonlyreference,notinstalled. Twoarcadecontactimagesfirst1200..3300andlater3600..5700recorded,visuallyinspected. walker_arcade_poses.png,walker_comparison.png,current/source/convertedframes/GIFsandHTMLreviewgenerated/visuallyinspected. No userphotoedit ornewAIgeneration.
Scripts prepare_l1_walker_r105.py,convert_l1_walker_r105.mjs,publish_l1_walker_r105.py; assets/ref/provenance/validationunderbuild/graphics/l1_walker_snake_r105/index.html. No gameplaybank/code/artreleasechange; r104/r100archives/lateststable100preserved. NeeduserdirectionA24metal/B24arcade/C32beforeinstallingreplacementoraddingdimensions. No speed/collision/hardwarevalidationclaimedforofflineproposals;stock64KB/references/sourceZIPsunchanged.

183. InteractiveRPC-derivedL1walker/snakeconverter (2026-11-09). Userrequestsinteractiveconverter/optionsforredoingbothfamilies. Deliveredself-containedfile://HTML atbuild/graphics/l1_art_converter/index.html plusZIPbundlewithGPLsource/licence, no server/API/networkrequired. Sourcefamilies:earlierAI-assistedwalker4poses,2realarcadewalkingcels256/258,4posearcade+labelledauthoredintermediates,currentr104walker4; snake10originalROM/capturedpaletteorientationsincludingverified2708joint,12capturedassemblypositions,currentnative16-19. Earlierfilter400..447omitted2708; inspectedextra_joint_2708.pngconfirmedintactjointandadded,avoidingfalseassemblygap. No originalROMZIPsdistributed/modified.
UIhasindependentperfamilysource/brightness/contrast/saturation/gamma, presets,shareduniontrim/blackcutout/alpha/manualcrop,size/scale/resampling/placement/rotation/mirror,normalpalettecheckboxes/optionalBRIGHT(no brightblack),RPCsegment/minerror,SierraLite/FloydSteinberg/orderedBayer4/none,optional8pixelhorizontalgapcoherence; frameplay/scrub/filmstrip/speed/zoom/background/grid/cellinspector; snakecapturedassemblyspacingandpost-overlap3colourcellcounts; arcadereferencepane; optionaluserimagesheets; per-familydecision/notes/autosave/import/export. Settingssharedacrossallfamilyframes,notindividualposecontrols. Autosavebrowserlocal;JSONportable. ExportbothZIPwithPNGframes/sheets,rowmajorbits/attrs/preservemask,columnmajorpairedrows,settings/provenance. Maskdoesnotsolveoverlapcolourconflictsandtoolstatesintegrationstillrequirespreshift/RAM/collisionreview. No gameplaycodeorcartridgewrites.
EngineadaptsactualRPCCPUfunctionsfrompriorverifiedworker/localupstreamhashc6be156532643baed7476882a2cdb2eabbde81d5e95c9c38bdc7fe8e708ccd89. Wrappersenforcealpha/normalblack/paletterestrictions;SierraLite/FloydkernelsuseRPCdiffusion;Bayer/nearestareexplicitadapters. Core32dither/strategy/BRIGHT/coherencecombinations+restrictedpalettePASS;normalblack/noFLASH/no brightblack/legal8x1/exactpreservemask/differingditheroutputs. FinalheadlessChromeonlocalfilePASSfamilyindependence/all4dithers/coherence/source/size/autosave/JSONroundtrip/actualZIP+PNGdownloads/no pageerrors. ExtraUItestsPASSexportduringpendingconversion/manualcrop/scale/rotation/mirroring/nearest/minerror/palettecheckbox/customsheet/mobile390pxnooverflow/UTF8labels. TestharnessinitialoldsystemNodefailedmodernsyntax;allactualchecksusepinnedNode24. WindowsESMpathcorrectedtofileURL. Hiddenmanualcropandcustomsheetdisclosurescausedtesttimeouts,correctedharnesstoopenthem(noappfailure). Worker/HTMLtestSHAsbindreportstoartifacts.
QAfixes:UTF8readexplicittoavoidmojibake;smallsourcepanemagnified;completed-cacheguardandclearqueueddebouncebeforeexportpreventpartial/cancelledexports;workerwrite_bytesUTF8normalizesLFsoprovenancehashmatchesactualsource(firstfinalizationcaughtCRLFmismatch). ActualbrowserZIP14framesCRC/nativepairlayout/PNGalpha-preservemask/shared-familysettingsPASS. PNGs walker_ui.png,snake_ui.png,mobile_ui.png captured;desktopfullpageimagesvisuallyreviewed,firstmojibakelabelsfixedthenfreshscreenshotsrecorded;mobilelayoutcheckedautomatically. ScreenshotsareeditorQA,notgameplay/performanceproof.
Sources src/l1_art_converter.html/.css/.js; scripts/build_l1_art_converter.py,verify_l1_art_converter_core.mjs,verify_l1_art_converter_browser.mjs,verify_l1_art_converter_extra.mjs,finalize_l1_art_converter.py. docs/l1_art_converter.txt andREADMElinkupdated. Bundle RType_L1_Art_Converter.zip SHA256 f98dfb38872b7c529af17969d86057b7bee5948a6f0279558e6d3b4b1515e6bd 4172551bytes;HTMLSHA256 5eb6ef6636717ebb5c68e4226b0118bf334eb62c3f0bb5e5d81ddabba30bcfb7. Fullvalidation_summary/engine/browser/extra/exportreportsunderoutputfolder. Stable r100ZIP/r104ZIPhashesverifiedunchanged;nogame/release/latestpointer/nativeROM/stock64KB/referenceproject/sourcearchivechanges. UsercanexportchoicesJSONforbothfamiliesforlaterintegration.

184. Selected L1 walker/snake integration r107 (2026-11-09). User supplies convref/rtype-l1-walker-snake-assets.zip as chosen versions; explicit instruction overrides exported decision=tweak fields. Original ZIP unchanged/CRCpass. Four chosen AI-source round-walker24x24poses installed exactly as exported pairs at native53-56/virtual208-211; other walkers unchanged. Snake native16-19+two flipflags map through16entryorientationlookup to seven captured chosen poses0,1,2,4,5,6,9. All10originalexportposes remain in sourceZIP. Open-side radial occupancy matches orientation, not random animation cycling; existing actor paths/spacing/collision unchanged. Small diagonal gaps visible in actual gameplay remain; disclosed for feedback, not falsely described as a continuous corrected arcade chain. No reconversion or artwork recolouring.
Runtime art3232->4240bytes relocated B000->A900, endsB990; runtime image endsA811, no overlap. Native-bank restore helper retained atA47B; spritehook adds snakeorientation dispatch, reads callerorientation atMAIN_SP+3 through6D, clears two consumedflipbits as existing genericrenderer does, restoresED. Existing walkerphasebehaviour retained. Packed payload ends39DA<3A00. Initial16flippedcopies exceeded3A00(3C19); all10directcopies also exceeded(3B54); storing only seven referenced exactposes fits, no overflow build published. No newbanks/nativecode/planbackup changes; onlyL1packedart/runtimeimage and two install operands differ fromr104. Other7regions includingL3fullphotoexhaust/L5 byteidentical. Stock64KBtarget andreferences untouched; stablelatest remainsr100.
Tests: ordinary700update rapidfire36snakedraws/392rounddraws and nofire330snakedraws/403rounddraws/all4walkerposes/actualbank5artidentity PASS. Gameoverbypass91F2 explicitly used for longtraces. Initialhookstacktest failed by4bytes because hook_done precedesPOPDE/POPBC; corrected expectedSP-4; gamecode not changed for test. ColdL1 andL3 threefiretimings each WITHOUTgameoverbypass PASS. Twelve cold/cachedlevelroutes/native-source/attributes/corepreservation/expectedresidentart PASS. Static exactexportpairs/otherartidentity/scopewhitelist/runtimepacketdecode/bankbounds/all16LEVEL/START reconstruction/allTAPchecksums/ZIPCRC PASS. No hardware orFPSclaim.
Diagnostic orientation_review.png underbuild/graphics/l1_chosen_r107 generated/visuallyinspected. Ordinary rapidfirel1_20..600.home.png andnofirel1_nofire_160/180/200/220.home.png plus snake_gameplay_review.png generatedfromactualRAM; montagevisuallyinspected andgaplimitationidentified. selected_art.png offlineexportcontactsheet generated/visuallyinspected; not gameplayperformanceproof. Other30nofireHOMEbins retained. Scriptsbuild_l1_chosen_r107.py,verify_l1_chosen_r107.mjs,verify_l1_nofire_r107.mjs,verify_cold_l1_fire_r107.mjs,verify_cold_fire_r107.mjs,verify_native_revisits_r107.mjs,finalize_l1_chosen_r107.py;docs/l1_chosen_r107.txt. Candidate package build/fullgame/l1_chosen_r107/RType_TS2068_r107.zip SHA256 fdc33e6320db69bb4ea0b432923fcf6422e22adf6633bb692cb37e12b328c297, 743083bytes. Replacecompletefolder/reset/ordinaryL1. Hardwarepending; ask feedback on chosen artwork inplay and diagonaljointspacing.

185. Magenta-front shell-walker identity confirmation (2026-11-09). User13022.jpg identifies old Spectrum-looking walker and asks to confirm which existing ECM design because several were developed. Compared nativeL1 contact sheet: exactfamily30-33, distinct from round53-56 and gunwalker21-25. All4bitmap payloads exactlymatch L3native36-39 respectively, whose ECMperlinecolourupgrade datesr81. Prepared identity_confirmation.png topoldL1/bottomexistingL3, generatedandvisuallyinspected; bottomuseswhite/cyan/bluewithred/magentaaccents, notnewAIart. Sentcomparisonandaskeduserconfirmbottomrow before publishingreplacement. Isolatedr108candidatecopiesonlytwo unusedL1dictionaryrows126/127 andtargetcelltagsfromL3. Nativebitmap/dimensions/otherdescriptors/runtimecode/banklayoutunchanged. build_l1_shared_ecm_r108.py scopeassertPASS; noZIPpublished, stable/latestand r107remainunchanged pendingvisualchoice.
CandidateordinaryL1nofire700updatesPASS,79drawsofnative30-33/all4IDsseen; walker/snakeexistingchecksPASS. Longtracegameoverbypassexplicit. ThreecoldL1firetimingswithoutgameoverbypassPASS. Twelve cold/cachedroutes/native-restoration/attributes/core/assetidentityPASS. Scriptsverify_l1_nofire_r108.mjs,verify_cold_l1_fire_r108.mjs,verify_native_revisits_r108.mjs. Diagnosticidentity_confirmation.png andactualRAMbinsunderbuild/fullgame/l1_shared_ecm_r108; RAMbinsnotrendered/claimedasvisualperformanceproof. No hardware/FPSclaim. Existingartchoicesnotconflatedwithconfirmationofuser'spreferredredesign.

186. Earlier modified head alternatives located (2026-11-09). User recalls another similar ECM walker with mods. Found saved r88 head32 choice B with exact52/59/82/gamma0.87, appliedr89/r90 toL6head32. Distinguished existingL3r81perline recolour from arcade-derived deepergray/cleanred and later chosenmodifiedconversion. head24/L7 and enlargedhead32_l7 remainedunreviewed. Generated earlier_modified_heads.png usingactualsavedr81/r63deeper/r90convertedPNGs, same3xpixelzoom (24vs32shownhonestly), visuallyreviewed. No newconversion/gamechange/package. Candidate r108 remainsunpublished pendingwhichversionusermeans; sourceidentity similaritydoesnotautomaticallyauthorize32x32geometryreplacementforL1native24x24.

187. Confirmed C conversion / scale review pending (2026-11-09). User selects C (modified head32 B52/C59/S82/gamma0.87); prepared four24x24source profiles by scaling RGB/mask BEFORE actualr88RPCworker, not resizingquantized32x32. Worker all4normalpalette/conversionPASS. Initial native-slot draft clips92pixels inpose32 and10inpose33 because old54emptycells; draftNOTpublished. Ordinarytests ofdraftnotaccepted asfinalvisualproof. Fullnewraw conversion uses8nonemptycells/73bytes each; four292bytes exceed original30-33pool284by8, nativepackingstillunresolved. No gameZIPreleased. User objects toscalechangesandrequestscomparison. Generated scale_comparison.png atsame4xpixelzoom:actualselected32x32r90vscomplete24x24newconversionbeforepacking; all4complete PNGssaved, nooldcellmaskclipping. Comparisonvisuallyreviewed; sizechoicependingbeforefurtherintegration. Source/convert/buildscripts prepare_l1_head_c_r109.py,convert_l1_head_c_r109.mjs,build_l1_head_c_r109.py. Currentcandidateunpublished;stable100/latestandplayabler107unchanged.

188. Full32x32 selected C shell integration r110 (2026-11-09). User accepts24butprefers32iffitsandrequestsattentiontoupdateratewithsnake. Builtfromr107, notclippedunpublishedr109. Native30-33mapstaticvirtual176-179 viaexistinghook toexactfourchosenr90L6_head32pairedpixels52/59/82/gamma0.87. Originalnativeposeorder retained, nofake4stepgaitcycling. Nativebitmap/descriptordata, coordinates/collisionlogic unchanged. Exact32x32storageall4poses; nofit-to-old54maskclipping. Previouslychosenr107roundwalker/snake/artprefixunchanged andother7regionsbitidentical.
Space: existing3024byteexpandedcache solelyholds21-25/201-204, allalreadyredirectedbyid_map; everyactivetablepointerusesbank5art. Retiredduplicatecachecontent, keptsame3024bytezeroexpandedinitialization toavoidchangingpreloaderloop. Originalexpandedcachearchived. Movedpackedplanbackup/preloadtable/art/runtimeimagewithallcorrespondingoperandsadjusted; planbackupdecodeidentityPASS. RuntimeimageendA83D < A900, artendBD90<C000, payloadend3729<3A00. Nativebankrestorehelperandcoremotionlogicunchangedapartfromplanbackupsourceoperand. Native-sourcecontractinitialfieldcomparedA000..E000whichincludesintentionalcacheloaderoperands; clarifiedtocorrectnativebitmap/sourceA000..BFFF, assertionPASS. No extraRAMbank/sourcearchive/reference/stock64KBchange.
Actualordinary700updates/nofire79sharedheaddraws/all4virtualposes176-179,403rounddraws/330snakedrawsPASS. Longtracegameoverbypassexplicit. ThreecoldL1firetimingswithoutbypassPASS. Twelve cold/cachedroutes/native-source/attributes/core/assetidentityPASS. StaticexactCbytes/previousrawprefix/scopewhitelist/7regions/planbackup/zero-preload/runtimepacketdecode/bankbounds/all16LEVEL/STARTreconstruction/allTAPchecksums/ZIPCRCpass.
Five deterministic520updateruns measureactualCPUcyclesatnative94F1boundaries3528000Hz, nofire,gameoverbypass: old24baseline,C24samepipeline,C32,andC24/C32controlledsnakestress. StresssubstitutesonlydrawID30-33forroundwalker53-56duringu155..240; shippinggameunchanged. Activecompiledcachebasechecked405baseline/484eachnewrun, allA900..BFFF, noneusesretiredC000cache. Naturalheadwindow425..500: C24mean182.94ms/5.466updates/s,C32mean192.76ms/5.188updates/s (+5.37%time). Controlledhead+snakewindow155..240:C24mean202.35ms/4.942updates/s,C32mean206.61ms/4.840updates/s (+2.10%time). Normal130..500overall+1.11%time32vs24. CPUemulationmeasurementsNOTphysicalFPSorplayerinterruptcadence. Ordinarysnakewindownearlysamewhenheadabsent.
ActualRAMu440head_gameplay_0.png(r107)/head_gameplay_1.png(r110)andhead32_gameplay_comparison.pnggenerated/visuallyinspected: selectedlargerheadintact,inairaboveterrain, nooldmaskmissinghead. Noanchorcorrectionneededforobservedairbornepose. OtherordinarycapturedHOMEbinsretainedwithoutclaimofrenderedimages. Earlier24draftclipped92/10pixelswasnotpublished/reused. Comparison24timingtargetunpublished, onlysamplerendererassetssmaller. Scriptsbuild_l1_head32_r110.py,build_l1_head24_timing_r110.py,measure_l1_head32_r110.mjs,verify_l1_nofire_r110.mjs,verify_cold_l1_fire_r110.mjs,verify_native_revisits_r110.mjs,finalize_l1_head32_r110.py. Docs/l1_head32_r110.txt. Package build/fullgame/l1_head32_r110/RType_TS2068_r110.zip SHA25654d5c7dacf57c8402a57b6fba804f6159d4573af9dd596f870d3407f6d5009c9, 573611bytes. Hardwarepending;lateststable100andallpriorarchivespreserved.

189. Interactive arcadeghost conversion editor (2026-11-09). User13026.jpg whiteenemiesright, requestsarcadesource+interactivetweaks; userthenconfirms454palette6. NativeL1family35-37identifiedfromactualr110nativebitmapcontact,24x24. Independentlydecodedall177uniqueearlyL1arcadeobjects1200..8100, generatedarcade_identity_contact.png/inventory, visuallyreviewed; exactlongcrest/arm/sideeye source450/452/454 palette6 matched. Actualcapturedobjects450/frame3600,452/3900,454/4200,32x32; all3genuineposes, no448guess or inventedintermediate. identity_comparison.png topnative/bottomarcadegenerated/visuallyreviewed, wholeobjectimagesnotpartialscreenclip. Userconfirms454p6; editorstartspausedonframeindex2, nativeposeorder450/452/454retained.
Standalonefile://UIreuseverifiedRPC-derivedworker andcontrols withsingleghostfamily, isolatedautosave/schema/exportfilenames, sourcecurrentvsarcade, samefamilysettingsacrossallframes,24/32sizecontrols,crop/resample/mask/scale/rotation,palettes,4dithermodes,8x1inspection,animation,presetsincludingpriorC52/59/82/.87, JSON/PNG/nativeZIPexports. No gameimagechanges. Genuinegray/gold/redarcadepalette retained asRGBsource; conversionsuser-tweakable. User's32x32previouswalkerisNOTsubstitutedforthisdistinctenemy. Worker32corecombinations/palette/normalblack/preservemask/legalpairs PASS. FinalChromeheadlessfile:// all3poses/confirmed454initialpreview/4dithers/gammasettings/24and32/currentvsarcadesource/preset/reset/autosave/JSONroundtrip/actualZIPdownloads/mobile390nooverflow/noJSerrors PASS. ExportZIP3framesCRC/columnmajorpairs/rowmajorbitsattrs/PNGalpha-preservemask/noFLASH/brightblackPASS. Initialbrowserfoundleftoverexportbothlabel,corrected; theninitialpausedbuttonstillPausecaught,fixedUTF8builderinsert; finalbrowserPASS. No falsegameplay/FPS/hardwareclaim.
Ghost_ui.png fullpagegeneratedandvisuallyreviewed; finalfreshghost_ui.png/ghost_mobile.pngcapturedafterlabelfix (layoutunchanged), allimagesdiagnosticUIonly. Sources src/ghost_art_converter.js/.html plus existingCSS; scriptsidentify_l1_ghost.py,build_ghost_art_converter.py,verify_ghost_converter_core.mjs,verify_ghost_converter_browser.mjs,finalize_ghost_converter.py; docs/ghost_art_converter.txt. build/graphics/l1_ghost_converter/index.html standalone andRType_L1_Ghost_Converter.zip SHA2564bc2b938d000593fa198973ced2c55373733b71ca185db0db4712dff94516e09, 88212bytes. OriginalROMZIPs/referenceprojects/read-onlynativegame/releases/r110unchanged. Futureintegrationrequiresuserexportchoice andsize/performance/overlapreview.

190. Chosen ghost32 integration + precomputed plans r114 (2026-11-09). User supplies convref/rtype-l1-ghost-assets.zip; CRCpass/SHAd40eb98a0968e7babd7c21b51badf9876bcca6257b5397b09ab7f649205f0da5. Explicitchoicesinstructionoverridesexportdecision=tweak. Exact3columnpaired32x32frames450/452/454palette6,56brightness66contrast89saturationgamma.74/SierraLite installednative35-37->staticvirtual180-182, nativeposeorderretained. No reconversion/resize/newart. Allpriorrawartprefixunchanged; allother7regionsidenticalr110includingL3exhaust/L5. Nativebitmap/palette/descriptors/coordinates/collisionunchanged.
Art6032bytes requiresA870..BFFF exactly; runtimeendA85Eplus18byteA7guardtoA870; guardintactafter1800updates. No extraRAMbank. Payload397B<3A00. Unoptimizedr113initial700updatetestfoundnoghosts(targetnotyetspawned); extendedto1800, firstghostu902,10866draws/all3virtualposesPASS. Initialbenchmarkscriptbadclosingbracketfixed,testonly. Unoptimizedghostmean440.71ms/2.269updates/svsr110old24mean311.33ms/3.212updates/s inwindow920..1100. Nativeper-poseprecomputedvisibilityrequestedbyquality/performanceintent: exactsameart, 3x16flags +C100helper inretiredDOCK6cache,768bytepreload, skipsoriginalsource-scanningandrowmaskbuildingforghostsphase0 only; allothersfallbackDCEF. SourcepointersderivedfromalignedBD00/BE00/BF00 plusflipmask, not arbitrarycalleraddresses. Existing0080foreground+clipchecks andrawIRQvectorsetup retained; targetplansbuiltusingexistingA44D/A45E helpers. Full4fliptemplates exceededcompressed3A00 (3BCC); compact4bytetriplesstill3A5C, reducedto48flagbytes+253bytehelperfits397B, no overflowartifactreleased.
EquivalenceharnessinitialgenericFFE0stackinvalidunderbankmapping(loopPC3), correctedtesttoexistingbankstableDOCK2private5CE0stack. First96caseattemptcaughtstalescreen_x/yDDA7/DDA8fromoldsource; actualcurrentmetadataDE27/DE28, correctedbeforegameplay/package. Final96cases all3poses4flips8positionsincludingclipped/foregroundcomparemeaningfulplanheaders/end/IX/map/IexactPASS. No mismatchingoptimizedversionpublished.
Finaloptimized1800updates/10866ghostdraws/all3poses, previoussnake674round783head79draws, exactRAMart/18byteguardPASS. Longtracegameoverbypassexplicit. ThreecoldL1firetimingswithoutbypassPASS. Twelvecold/cachedroutes/native-source/attributes/core/artidentityPASS. Staticexactexportassetprefix/7regions/scope/nativebitmap/palette/backup/runtime/cachepacket/bankbounds/all16LEVELSTARTreconstructions/allTAPchecksums/ZIPCRCpass. Optimizedghostmean420.10ms/2.380updates/s, 4.68%timeimprovementoverunoptimizedbutstill+34.94%timevsoldwhite24. Snakewindow201.42vs201.44ms, head193.73vs192.76ms, earlyoverall177.43vs176.75ms. Explicitlyreportedcrowdedghostslowdown,nofalseperformanceequivalenceclaim. AlltimingsdeterministicemulatedCPUcycles3528000Hz,nothardwareFPS/playerIRQcadence.
ActualRAMghost_920/940/960/1000.pngr113generated;ghost_940visuallyinspected. r113ghost_gameplay_comparison.pngrecorded. Finalr114ghost_gameplay_0/1.pngandghost_gameplay_comparison.pngu960generated/visuallyreviewed:goldgrayredchosenheadsintact,3poseslargerthanold24. Earlierheadcomparison andeditorimagesunchanged. Scriptsbuild_l1_ghost_r113/114.py,prepare_ghost_precomputed_plan.py,verify_ghost_precomputed_equivalence.mjs,verify_l1_nofire_r113/114.mjs,verify_cold_l1_fire_r113/114.mjs,verify_native_revisits_r113/114.mjs,measure_l1_ghost_r113/114.mjs,finalize_l1_ghost_r114.py;src/l1_ghost_precomputed_plan.asm;docs/l1_ghost_r114.txt. Packagebuild/fullgame/l1_ghost_r114/RType_TS2068_r114.zip SHA256583633668558e0beff71ba71c87f3a3ed73d52e725da4a66865a8316ef81f57a 581317bytes. Hardwarepending;stablelatest100andpriorr110preserved;references/sourcearchives/stock64KBunchanged.

191. Picturedcyancrestednative41 /246comparisoneditor (2026-11-09). User13027.jpg asksbetterarcadematchthan246p6andinteractivecomparison. Exactr114native41visualidentityconfirmed40x40, distinctfromalreadyupgradednative43/44andvirtual201-204. LocalROM/capturedobjectcomparison246p6/frame2400,246p11/2700,246p2/3900haveidenticalRGBA SHAef6baf87a67c..., notgenuinedifferentpalettes. Captured256p11/3000and258p7/3300providesamefamilywalkingalternatives. Captured258facingoppositetocaptured256; editorusescanonicalROMunflipped256/258, notalternatingfacingasfakegait. ROM260/262explicitlylabelledaction/boost, notwalkingintermediates. No claimthesewalkposesautomaticallymatchnative41'ssingleposebehaviour. No forcedsourceidentitywithacceptedotherwalkerfamily.
Generatedsource_candidates.png8images/currentnativeandcaptured246variants/256/258/action260/262visuallyinspected; canonical246assertbyteidenticalactualcaptured246p6. canonical246/256/258/260/262.pngsavedfromoriginalROM; noAI/newart. Interactiveonebluefamily editor choices A246single,Bwalk256/258,Caction260/262,currentnative41; default40x40matchescurrentfootprint,32originalsizeoption. Sharedsettingsperselectedposes, default56/66/89/.74aslastghostchoice, presetsinclpriorC/neutral/soft, fullRPC/SierraLite/dither/palette/crop/size/animation/cellinspector/exportcontrols. Blue-onlyautosave/schema/filenames,sourcegalleryembedded,noexternalnetwork/server. No gameplay/bank/cartridgechange.
Worker32corecombinations/paletterestriction/normalblack/preservemask/legalpairsPASS. FinalheadlessChrome file:// A1/B2/C2/current1pose selection; all4dithers/sharedgamma/32and40sizes/animationplaypause/presets/autosave/reset/JSONroundtrip/actualAandBZIPdownloads/mobile390nooverflow/noJSerrorsPASS. ZIPexports3framesCRC/rowmajorbitsattrs/preserve mask/columnpairedrows/PNGalphaexact/sharedsize/noFLASH/brightblackPASS. blue246_ui.png,walking_alternative_ui.png,blue_mobile.pngcaptured;walkingalternativefullpagevisuallyreviewed. UIanimationNOTgameFPS,nofit/speed/hardwareclaim.
Scriptsidentify_l1_blue_enemy.py,build_blue_enemy_converter.py,verify_blue_enemy_core.mjs,verify_blue_enemy_browser.mjs,finalize_blue_enemy_converter.py;src/blue_enemy_converter.js/.html;docs/blue_enemy_converter.txt. Standalonebuild/graphics/l1_blue_enemy_converter/index.html, ZIPRType_L1_Blue_Enemy_Converter.zip SHA2560139a1ec64a744e312d91ecdfe6b9539e0185d62fb63e98bef1502f1436bcfd2 111586bytes. OriginalROMZIPs/referenceprojects/gameversionsr114andearlierunchanged. Futureintegrationrequiresuserselectedsource/settings/sizeandperformance/behaviourreview.

192. Exactchosen40x40flyingboostintegration r116 (2026-11-09). Userchoosesaction/boostfromconvref/rtype-l1-blue-enemy-assets.zip SHAd07a4a3f5b69aceb00d55a7416eb735b771739ccd91eb7d1bfd502ae3915732a/CRCpass. Exact2x400bytecolumnpairs ROM260/262,56brightness56contrast100saturationgamma.35/SierraLite. Native41->184/185twoframeactor-localcounterwhileflying, notwalkingposes. Existing40x40footprint/nativeflight/collisionunchanged. Allbank5art6032byteprefixand7otherregionsidenticalr114; priorghost/snake/acceptedwalkers/L3exhaustretained.
Memory: new800byteart C300..C61F inretiredDOCK6cacheafter768byteghostpreload; ghosthelperC100/bluegatherloaderC200/chunktableC260/ghostvarsC2F0 separate. Packedsource411bytes initiallytestedatDOCK7F900zerosbeyondnativecopyF87C; ordinaryinitialartpassbutsourceoverwrittenandcachedL1revisitcorruptedresidentart. Testcaughtfailure, noZIPreleased. Replacedwith22scatterranges/411bytesin52unreferencedpalette rows includingrow54whichisneverreadascolour(transparentmarker). Allfirst16andallactualnativecolourrows/staticnativeframesunchanged. GatherstoC900..CA9A, decompressC300, bank7nowentirelyidenticalr114. Firstpalettecapacityexcluding54was408bytes;3bytestailfititerationand3A1Eoverflowdiscarded. Includedunused54rowandremovedredundantphaseclear/post-gathermapwrite, usedstackcounterloop; fits39FE<3A00 with2bytesmargin. Source rangesareRESERVEDinblue_contractforfutureconverters, donotreusethemforpaletteart. Exactstaticproofusednativecolourrowsnotchangedandsourcepackeddecode800pass.
Runtime205entryidmapplusCP205guardpreventsoutofboundslookups; native201..204mappingretained. Specialbase184usesAND1, other4posegroupsunchanged. LoaderwrapssaveSP C7F2/privateSP C7F0 aroundpreloadandgather; alwaysvisibleDOCK6 through6F/ED mappings. Helperdoesnotresettooverlapping5CF0; addressedbeforefirsttestedbuild, no suchbrokenversionreleased. Expandedruntimealwaysfreshlyzerosactor_phases; redundantLDIRclearremovedforpacking. Finalguard31A7bytesendA870 andexistingartendsC000; bluecacheendsC620, privatestackC7F0, scratchC900 nonoverlap. ActualloadercallerSP/map restored2timesinmeasuredstartup.
Final1800ordinaryupdates/1320boostdraws/bothvirtual184185/exactresidentbank6art/sourceguardPASS; sourcefirstu480tou1799. Previousghost10866draws/all3poses, snake674round783head79drawsPASS. Longtracesgameoverbypassexplicit. ThreecoldfiretimingswithoutbypassPASS;12cold/cachedroutesincludingpreviouslyfailingL1returns verifyboostart+sourcebyteidentityPASS;96ghostplan-equivalencecasesPASSwithfinalsharedcache. StaticexactZIPframes/preservedbank5art/7regions/usedpaletterows/nativebitmap+descriptors/bank7/scope/bounds/packetdecode/planbackup/all16LEVELSTARTreconstruction/allTAPchecksums/ZIPCRCpass.
Timingmatchednofireroute: r114vsr116early130..500mean177.43->178.29ms (+0.49%time); busyghost920..1100mean420.10->414.10ms (-1.43%time). Nativeupdate-boundaryCPUcycles3528000Hz, nothardwareFPS/playerIRQcadence/universalgain; IRQtimingvarieswithartcost. Complete1800run41976->42554emulatedframes includesstartup+differentlaterencounters. No claimtocureexistingr114ghostslowdown.
ActualRAMu960blue_gameplay_0/1.pngandblue_gameplay_comparison.pnggenerated/visuallyinspected: originalcyanreplacedbychosenred/gold/whitebodywithblueboostexhaust, whole40x40 retained, twoactionposes. No userimageediting/sourceAI. Sourcesbuild_l1_blue_boost_r116.py/src/l1_blue_art_load.asm; scriptsverify_l1_nofire_r116.mjs,verify_cold_l1_fire_r116.mjs,verify_native_revisits_r116.mjs,verify_ghost_precomputed_equivalence_r116.mjs,measure_l1_blue_boost_r116.mjs,finalize_l1_blue_boost_r116.py;docs/l1_blue_boost_r116.txt. Packagebuild/fullgame/l1_blue_boost_r116/RType_TS2068_r116.zip SHA256b570a2dfcd4345947c4c59efa1bd2e160e63e9100ffedb30d1290da6f119dc45 582746bytes. Hardwarepending,stablelatest100/previousr114preserved;sourcearchives/referenceprojects/stock64KBunchanged.

193. L2 photo13028-13032 seven-issue artwork/scroll investigation and interactive reviewr117 (2026-11-09). Currentr116gameunchanged. Generated current52descriptorinventory (emptydescriptorshandled; initialPNGsaveonemptydescriptorfailedthenfixed) and originalL2arcadecaptureinventory. Small shell34..38comparedtoexactapprovedChead4poses; scorpion32/33and chain22..30sources explicitlytentative,whitelegs19/20compared2402/2404/2406,rolling3..6isolated2470/2464. No forcedsourceidentityorunverifiedgaitclaim. Terrainfixed256x160mask,arcadematerialprojectionlabellednotexacttilematch; bosssource192x104existingproposal. SharedRPCsettings/crop/scales,4dithers,palettecontrols,normalblack,gap8/fullrowpolicies,phasepreview,JSON/nativeZIPexport. TerrainlockedonUIandimport; scrollingpalettehonorsenabledcolours. All7families/27sourceframes legalpairs/browserexports/independent8phaseauditPASS. Chromeclosedbeforetest; installedEdgepassed. *_ui.pngcaptured;whitelegs_ui.pngvisuallyreviewed. build/graphics/l2_review_r117/index.html andRType_L2_Art_Review_r117.zip.
OrdinarycurrentL2trace1547updates/27310emulatedframes death/gameoverbypassexplicit,noBB. Capturedcolumns54..64andfine0..7, renderedallRAMcaptures. Bossstoredtilepayloadanddictionarybyteidenticalr67. fineapproachbitmaptranslationmostlyexact1pixelwithsomeobjectoverlapdifferences; doesNOTproveallgeometrycorrect. Red/yellowpatch reproduced/scrollcolourconstraintidentified; runtimepalette/tileassemblyfix NOTcompleted. No gameZIPpublished,nohardware/performanceclaim,stock64KBunchanged. Scriptsbuild_l2_art_review_r117.py,verify_l2_art_review_r117.mjs,probe_l2_r117.mjs;docs/l2_review_r117.txt. Proposedscrollsafeentrance/stationarydetail/tentaclerevealstillpendingintegrationandtests. PackageSHA 5b9fec30279a8bd0f1193174a901552a00dc4a5538590168ca36e394abf7ed49

194. L2userexportanalysis/reviewr118 (2026-11-09). Readconvref/rtype-l2-art-assets.zip CRCpass/settingsnotesretained. Usercorrectlyidentifiedhalfscorpionandwrongchain. Actualcapturedsame-y/palette/adjacent-x32/consecutiveoffset8objects pairinto64x64scorpions;10uniquecompleteRGBAposes gathered, rawdescriptors/SHAs inassembly_evidence.json. No arbitrarygaitclaim. Actualframe15900snakeoffsets124..292has22placements/6uniqueRGBAparts,2450/2454body/headterminal2480/2496/2482/2464. Skeletalcandidatewithdrawn. Capturedpositions/fliprenderingretained; connectedassembly source displayed. ApprovedCwalkerexistingr110sourceconfirmed, no new replacementinvented. All7familysettings/notesretained,reviewflagsnotaccepted. Correctedsourcecropresetonlyscorpion/snake. Userbossproposalofflineprototype: exactexportentrance, stopatx64, whole8x1cell dissolve toprevious192x104detail; enlargedpreviewreferencefirstdetectedandcorrectedbeforedelivery. Notgameplayfix.
Edgeall7families/scorpion10frames40x40/snake6frames24x24/settingsidentity/4dithers/gapfullrow/independent8phase/nativeZIPCRCpass. Cachedstatuslinecanretainpriorfamilytextbutdataandcanvasescorrect; validationJSONusesactualsnapshot. scorpion_ui.png/assemblyvisuallyreviewed. Scriptsbuild_l2_review_r118.py/verify_l2_art_review_r118.mjs,src/l2_art_review_r118.*,docs/l2_review_r118.txt. Packagebuild/graphics/l2_review_r118/RType_L2_Art_Review_r118.zip SHA13639832c79c5a9c2be67f3f68335001aa4bf1b647a7461e8e270e6b9cf2deb8. Gameunchangedr116;runtimeintegration/orientationmapping/scrollfixremainpending,nostock64KB/referenceproject/sourceZIPchanges.

195. L2v2export accepted/all10scorpiondirective (2026-11-09). convref/rtype-l2-art-assets_v2.zip CRCpass; all7settings/notesread. Prepared exact10x40x40scorpion PNG/pairs/bitmap/attribute/preserveexports inbuild/graphics/l2_scorpion_all10_r119 with sourceZIP/frameSHAs. VerifiedoriginalRGBAflipidentities: base0->frames0/1(Y)/4(X)/6(XY),base2->2/5(Y),base3->3/7(X)/9(Y),base8->8. Fouroriginalposeclasses, tenexportedframesretainedbecauseconversiondifferencesnotassumedidentical. Capturedorientationinventory atindex.html/orientation_contract.json. Do notcycleallheadingvariantsasonearbitrarygait. Userrequiresall10; initial2poseimplementation superseded.
UNPUBLISHEDFAILEDdraftbuild/fullgame/l2_actors_r119 markedDO_NOT_USE.txt. Initialbank1capacityassertfail41D9/3DDE/3E36caught; noZIP. Attemptedplanarpacking/C000..C3DFscratch/privateC4D0loaderstack/sourcepoolreuse inbank7retired3..6/19..38, preservingnativebank5beforeoverlay. Exactpacketdecodeandboundsstaticpass357C/A7C9/A7E0..B370, butstartupordinaryprobeu0andtransitionroutefailsenteringL2. No release/nohardwarefixclaim. Testedstackprivate/save,IXpreservation,reservedL2tileinstallerA480trailerbyextensionatA4B0; original-baselineshortprobegets11updatesby3029frames,newcandidateu0at7000. LowPC3tracealsooccursbaselineandisnotbyitselfafailurecriterion. Originalr116ZIP/LEVEL02TAPidentityverifiedunchanged. Earlierfulltrace/revisitfailuresretained; do notclaimgameplaypass. Nativepoolsource-lifetime/layoutrequiresredesign; all10memoryintegration/terrain/bossdissolveremainunfinished. Currentplayablecandidate staysr116; stablelatest100unchanged.

196. L2 selected actor integration candidate r123 (2026-11-10). Userv2ZIP SHAe16427f3fea28674b16bc8f3399a4acaa0c161a661f96b8fb9009e640c456ac6. All10scorpion40x40exports retained via normalized4bases+6losslessXORdeltas, existingcallerflips retained; 27actualZ80decodepackets matchselectedpairs exactly. ApprovedCwalker4poses24x24,whitelegs3poses24x24,snake8orientedparts24x24,emergence2heads40x40+nativeflips integrated. Headhorizontalnative8px/vertical2px; noAI/collisiongeometrychange.
Found/corrected draft bank7mapping/source reuse error, compressedvsrawfetch, overwrittenA480uninstalltrailer, installerAF/carryloss, self-overwritingrestorehelper. Finalsourcepackets inbank1andretiredDOCK5A84C..AB75/ABC7..AEAD; nativeprefixA4B0..A84B snapshot inDOCK6C700..CA9B; restorehelperbank1:3920, save3980; fullIM2page/DOCK4/DOCK7preserved. ExtraHOMEplanrestoreonexit.
Tests: actual27decodeframes/all10scorpionIDs observed; ordinary1547worldupdates39205emulatedframes throughboss with invulnerability/gameoverbypass; sourcesimmutable. ThreeunmodifiedearlyL2firetimingsPASS;12generalcold/cachedroutesPASS;6longboss/samelevelreset/revisitroutesPASS. Overlystrictsourceaudit initiallyfailedbothr123andr116 because HOME C4F2..C635 rendererplan and C700..C78F expandedtile are intentionalworkspace; narrowlyexcludedonlywhileL2installed,othernativebytesstillchecked. All256IM2wordsinactualRAMresolve5B5B; emulatorfixedFF,nothardwareIRQprobes. All16level/STARTtapereconstruction/checksums,rtidentity,ZIPCRC,other7regionsr116identicalPASS. ActualRAMimages ordinary_L2_col54.home.bin.png/ordinary_L2_col67.home.bin.png rendered; col54 visuallyinspected.
PERFORMANCE/LIMITATIONS: selectedlargeractors costtime; prior1547updateapproach~39kframesvsr116~27k,notaspeedgain. Fullscreenpaletteexperimentr122activehookscanned4800cells/update,rejected/quarantinedDO_NOT_USE. Terrainstripdimensions/maps/detailedbossart remainr116; terrain/bossscrollpaletteanddissolveintegrationSTILLPENDING. r123completesactorintegrationonly,notwholeL2request. Hardwarepending; stock64KB/stablelatest100/referenceprojects/originalZIPsunchanged. Candidatebuild/fullgame/l2_integrated_r123/RType_TS2068_r123.zip SHAebfba475f3fbf491b39992318504c0ac33b90b707e72ff053aa2f9a770404583. docs/l2_integrated_r123.txt.

197. Complete selected L2 integration r124 (2026-11-10). Actor27packets/all10scorpions retained fromv2ZIP e16427f3fea28674b16bc8f3399a4acaa0c161a661f96b8fb9009e640c456ac6. Native34terrainIDs0..33 restored with original bitmaps/dimensions, independentbossIDs34..51 replace old19..36 collision. Sky7cells retained; marking emptycells86 reproduced huge player smear via native RL terrain writer8970, fixed. Selected material rowinks at8343/boss83E3; conservative fullrow palette policy (not exact gap8 projection or new arcade silhouettes). Movingboss nonblackunion mask; selected richpairs restored after DOCK3:7A8E stop,18occupiedtiles/oneperupdate using8CFD into backbuffer and primary. Bypassnativeocclusion only during explicitrepaint via balancedPOP AF/SCF/RET guard. SharedHOME868C hook installed/restored, fullmain+alternate registers preserved. Finepalette0100runsmap3,lookup0F80runs0B; preserve0190/01A0/0FC3 nativehelpers. Worldstate readmap1B withIRQpreserved. No fullscreen scan.
Bounded1levelXOR/LZ tilecodec5521bytes, nativefloorB442..C762 plusretiredlowpalette; duplicatepackets aliased; scratch82B3..8342 fromdebugduplicatefont. DebugROMfont3D00,codeends82B3; fixedowneddata ends84B4. Baseline fontarea read/write audit empty; DOCK7unusedspace proposal rejected by actual heavycode/datareads/writes. NativeprefixA458..A84B snapshotDOCK6C700..CAF3, lowownedflag; restoreHOMEprefix thennativehighsource toDOCK6 LAST. No bank7 reuse. Loader3848..39FA; boundaries asserted.
PASS:128actualZ80tilecases,27actorpackets,all10scorpionIDsdrawn,all8finephasescaptured,1547ordinaryupdates38775emulatedframes;3unmodifiedcold/firecases;12generalcold/cachedroutes;6longboss/samelevelreset/revisitroutes;256actualRAMIM2words5B5B(fixedFFemulator,notactual256IRQprobes);all16tapesreconstructed/checksums,other7regionsr123identical,DOCK7unchanged,ZIPCRC. Revealtraceboss_stop_probe.json no revealbeforestop/all18complete. Directdebugentry/ROMfont/SpaceRAMredrawPASS; initial livechord test did notestablish takeover (pc8383/map89), forcedFD20also notvalid; no liveIRQclaim. DebugactualRAMimage debug_final.png readable. Images boss_probe_160.home.png and ordinary_L2_col54.home.png inspected; intermediatefailedsky/primaryonlyrepaint experiments notdelivered. Diagnostics inbuild/fullgame/l2_complete_r124 andbuild/graphics/l2_integrate_r119. Sourcechecker excludesonlyintentionalL2HOMEplanC4F2..C635/tileC700..C78Fwhileinstalled; restexact.
Performance smallr12339205tor12438775emulatedframesfor1547updates;not hardwareFPS,largeractorsstillcostly. Hardwarepending;stable99/100,stock64KB,referenceprojects/sourceZIPsunchanged. Candidatebuild/fullgame/l2_complete_r124/RType_TS2068_r124.zip SHA574c10a09657682502fe1e89fd464c7d43c856a43021641ecc96a00eaba2af15;docs/l2_complete_r124.txt.

198. r125 L2 post-first-frame terrain yellow and corrupted player missile regressions (2026-11-10). Rootcauses: r124 changed initial/boundary colour paths but left flat0E40 and slow0E00 resolving86 through oldFBD0 yellow row; r124 incorrectly retired liveglobal actor/projectile palette1B20..1E1F. Fixed highmarked0E91 resolver to row_palette via0FB1; actualIN A,(F4) caller mapping preserved, not hardcoded3. Initial forced-map3 draft produced large vertical bitmap streaks in backbuffer updates despite directdecoder tests; visuallycaught/quarantined, actualmap-preserving fix verified. Teststack5CE0 invalidwhenmap7 mapsDOCK2, movedteststacktoHOMEFFF0; both3/7 returnmapping and160scanlines nowchecked.
Lossless planar tilecodec5185bytes (nativeattrs redundant/derived from cellpixels) frees room for423bytecompressed ORIGINAL768byteglobalpalette. Originalsource1B20 nowintentionallyreused onlywithrenderer157A CALLglobal_palette instead ofLDBC1B20. Firstglobalcall AFTERcoldbootstrap expands intoDOCK6D940..DC3F; lowGLOBAL_FLAG prevents repeateddecompression. ColdbankimageD920..DC40 remainsbyte-identicaltor124. Initial proposedstaticbank6relocation FAILEDstartup because D930+is audio/bootstrapsource mirroredHOMEF930+,notfree; rejected. No bank7reuse. Pointertable1160..11C7, reveal106C..10EE usesretiredauthoringpaletteconstantregions; fullbaselinefiringauditfoundonlyinitialloadcopies (PC5E04), newtargetreads separatelyexpected. Nativeattributereconstruction39E0; interleave~1DEAx; globalhelper3998. Actual128decoderoutputs exact; all27actors/all10scorpions retained.
PASS finalbinary:96sharedglobalpalette rows exact,160terrainrows bothmaps3/7,128tilecases/27actorpackets,256actualRAMIM2words(fixedFFemulator/not256actualIRQprobes),1547sustainedfireupdates38561emulatedframes,all10scorpionIDs,all8finephases;3unmodifiedcoldfiretimings;12generaltransitions;6longboss/samelevel/cachedrevisits;18bossrevealafterstop;debugdirectentry/SpaceRAMredraw;all16tapechecksums/reconstruction,other7levelsidenticalr124,bank7unchanged,ZIPCRC. Visualfiring_64.home.png/ordinary_L2_col54.home.png/boss_probe_160.home.png inspected (finalcorrectterrain/noverticalstreaks); diagnosticsbuild/fullgame/l2_scroll_projectile_r125. Failedflat-map3captures overwrittenbyfinalcapture, failuredescription here; low_spare_audit.json/bank6_spare_audit.json retainedunderl2_complete_r124. No hardwareconfirmation. Priorr124staticdecodercoveragewasinsufficienttoestablishlivepaletteownership/end-to-endscrolling; futurechecks include actualpalettebytes, bank-sensitivecallercontracts and sustainedfirevisuals.
Candidatebuild/fullgame/l2_scroll_projectile_r125/RType_TS2068_r125.zip SHA728bf4496e9a3c4f801d7cff04e8505592d1c952905b22706efa66e229161959; docs/l2_scroll_projectile_r125.txt. Stable99/100,stock64KB/referenceprojects/originalZIPsunchanged.

199. r126 L2 snake part identity fix (2026-11-10). Userphotos13087/13088 show native bodyanimation alternating anatomically different exported parts. v2choices provenance explicitly says parts/orientations, not gaitcycle:cel2450p5offset140 commonbody vs2454p5offset236 alternatepart. Priorintegration mappednative22->198(frame03/2454),23->199(frame02/2450). Both now199;25..30head/tail orientations unchanged. ExactlyONE expandedruntimebyteA704(physicalimage704)198->199. Compressedmotion sourceend3831same;noextra code,cache,memoryoranimationcost. Allchosenimagesretained,normalbodyusesrepeatedsource2450.
PASS actualgameplay455bodydraws(221native22/234native23) all199 through180post-BBupdates;head/tailmapsunchanged. All27actorpacketsdecodeexact;96sharedpalette rows/160frontbackterrainrowsPASS;12cold/cachedroutesPASS;all16tapechecksums/reconstruction,other7levelsidenticalr125,ZIPCRC. Imagebuild/fullgame/l2_snake_parts_r126/boss_probe_160.home.png rendered/visuallyinspected;trace snake_gameplay_validation.json. Scriptedbossrouteusespriorinvulnerability/gameoverbypass,notnormalcompletion/hardwareconfirmation. No fresh3coldfireorlongfullapproach rerun:exactmapping-onlychange,existingstart/transitioncoverageappropriate. SourceZIPs/referenceprojects/stable99/100/stock64KBunchanged. Candidatebuild/fullgame/l2_snake_parts_r126/RType_TS2068_r126.zip SHAcb4eb7f618979d4da24c7b35bbd9f4df618734cafd2561914c95449b6f5ce748;docs/l2_snake_parts_r126.txt.


200. UNRELEASED r127 L2 snake anatomy / boss-erasure investigation (2026-11-10). User photo13089 asks for head, round body and spiny body, stable anatomical roles. Arcade assembly evidence: 12 round2450p5 and6 spiny2454p5 source records plus terminal pieces. Implemented chain-relative ordinal selection over native role5 records:9 round199 then4 spiny198 in the native13-body chain; head/tail orientations unchanged. A 700-update scripted encounter recorded4669 selected part draws with stable per-slot roles (invulnerability/game-over bypass, not hardware).
Boss damage investigation: native opaque actor/shot drawing can punch persistent holes in the upgraded stopped backdrop. Several unpublished repair experiments were attempted: mouth precomposition, touched-tile restoration, explicit colour-row copying, and a full repaint fallback. These are NOT release-ready. Strict comparisons exposed stale colours/remaining pixels, and some experimental revisions corrupt low code or stall. An alternate-HL preservation defect in the new 8CFD gateway was corrected; a transition fixture error used offset4FD instead of8FD when normalizing native8CFD and has been corrected. Native cold/cached transition coverage subsequently passed in an intermediate revision, but this does NOT validate the current failed candidate. Optional helper interrupt/stack/mapping behavior still needs isolation. Earlier passing JSON/captures in this directory span revisions and must not be reused as final evidence.
No r127 ZIP generated. build/fullgame/l2_roles_restore_r127/DO_NOT_USE.txt and validation_summary.json mark failure. Source prototypes under src/l2_*_r127.asm and scripts/build_l2_roles_r127.py are experimental, not invoked by stable release_latest.py. Stable r99/r100, released r126, stock64KB target, original ZIPs and reference projects remain unchanged. Need complete repair and rerun final-binary checks before any release.


201. Completed r127 L2 snake/boss fix (2026-11-10), supersedes failed diagnostic entry200. Native13-body chain uses stable9round2450/4spiny2454 roles plus unchanged head/tail orientations. Boss backdrop cached as18x144byte native tiles in DOCK6 CB00..D51F (2592bytes), after snapshot C700..CAF3 and before IM2 D800; palette D940 and live raw actor caches C000/C200 preserved. Capture59bytes atA7CC..A806 uses bank4 scratch82B3 only after tile decode; direct copier122bytes B002..B07B restores bitmap and8x1 colours including black rows. DI before EVERY exposure of bank4 (active I84 vector hidden), map9 restored before outer alternate registers/IFF. Original8CFD entry and native0FB8 helper retained. Full native repaint reference passed but cost1287781 cycles/call; cached copy 273613 cycles/call, 78.8% less per-call cost, not hardware FPS. Fullcopy may be invoked multiple times per native world update.
Root causes found in rejected prototypes: reused live0FB8 native helper, missed reverse_cache caller at0F9F after helper moved397D->3980, unsafe bank4 mapping between repeated calls, and a faulty mouth43 delta table. Final43 aliases raw42; all31 runtime-table/decoder packets checked. No artwork dimension changes:mouth32x24, original tile silhouettes. Debug full capture retained, display compacted16fields. No new native joystick/input behavior.
PASS finalbinary:700 post-BB updates/sustained firing; immutable18tile cache exact at5 checkpoints; each checkpoint1744 visible source scanline/cells, all pixels/visible colours exact in background. Snake 3845 body draws both roles stable. 31 actor packets incl4mouths/10scorpions;128tiles;96palette rows/160frontbackscanlines;256actual RAM IM2words (fixedFF emulator, not actual256IRQ/hardware probes);12cold/cached routes;6boss/reset/revisit routes;3normalcold/fire cases;debugdirectentry/Space redraw;16level/start TAP checksums/reconstruction plusrt.tap;other7regions/bank7/coldbootstrap/projectile sourceA816..A84B unchanged; ZIP CRC. Boss stress uses invulnerability/gameover bypass. Actual captures boss_probe_690.home.png and others inspected; foreground temporary matte/shared-cell clash remains possible, permanentbackgrounddamage fixed.
Cache boundaries and contracts in build/fullgame/l2_roles_restore_r127; previous rejected logs/JSON there are historical, final validation_summary binds region SHA. No hardware confirmation. Candidate RType_TS2068_r127.zip SHA4b25938e18a233a39930d78135527e47944a9536c4c4ee81080f1625aa3a4daf. Stable99/100/stock64KB/sourceZIPs/reference projects unchanged. docs/l2_roles_restore_r127.txt.


202. Completed r127 L2 snake/boss fix (2026-11-10), supersedes failed diagnostic entries200/201. Native13-body chain uses stable9round2450/4spiny2454 roles plus unchanged head/tail orientations. Boss backdrop cached as18x144byte native tiles in DOCK6 CB00..D51F (2592bytes), after snapshot C700..CAF3 and before IM2 D800; palette D940 and live raw actor caches C000/C200 preserved. Capture59bytes atA7CC..A806 uses bank4 scratch82B3 only after tile decode; direct copier189bytes B002..B0BE restores bitmap and8x1 colours including black rows. Damage comparison only marks changed cells dirty; all288 cells exercised by injection test (unchanged cells retain flags). Native7800 attribute/7E00 dirty-cell maps updated to schedule visible refresh (the first cached draft repaired only the backbuffer and failed visual QA; withheld archive renamed pending_front_validation). DI before EVERY exposure of bank4 (active I84 vector hidden), map9 restored before outer alternate registers/IFF. Original8CFD entry and native0FB8 helper retained. Full native repaint reference passed but cost1287781 cycles/call; cached copy 503890 cycles/call, 60.9% less per-call cost, not hardware FPS. Fullcopy may be invoked multiple times per native world update.
Root causes found in rejected prototypes: reused live0FB8 native helper, missed reverse_cache caller at0F9F after helper moved397D->3980, unsafe bank4 mapping between repeated calls, and a faulty mouth43 delta table. Final reverse-cache helper is3820, global-palette helper3980, both callers explicitly audited; demand notification covers both palette paths. Warm HOME source repair extended ABC7..B0DD to include the new retired mouth/cache-code range; lower dirty rows use HOME8000..807F, never bank4 debug code. Final43 aliases raw42; all31 runtime-table/decoder packets checked. No artwork dimension changes:mouth32x24, original tile silhouettes. Debug full capture retained, display compacted16fields. No new native joystick/input behavior.
PASS finalbinary:700 post-BB updates/sustained firing; immutable18tile cache exact at5 checkpoints; each checkpoint1744 visible source scanline/cells, all pixels/visible colours exact in background. Snake 3735 body draws both roles stable. 31 actor packets incl4mouths/10scorpions;128tiles;96palette rows/160frontbackscanlines;256actual RAM IM2words (fixedFF emulator, not actual256IRQ/hardware probes);12cold/cached routes;6boss/reset/revisit routes;3normalcold/fire cases;debugdirectentry/Space redraw;16level/start TAP checksums/reconstruction plusrt.tap;other7regions/bank7/coldbootstrap/projectile sourceA816..A84B unchanged; ZIP CRC. Boss stress uses invulnerability/gameover bypass. Actual captures boss_probe_690.home.png and others inspected; foreground temporary matte/shared-cell clash remains possible, permanentbackgrounddamage fixed.
Cache boundaries and contracts in build/fullgame/l2_roles_restore_r127; previous rejected logs/JSON there are historical, final validation_summary binds region SHA. No hardware confirmation. Candidate RType_TS2068_r127.zip SHAfb0a3ff44bfab1f3eeb6ca2801edd733cd47f42525ff8bae78e13234b69c8330. Stable99/100/stock64KB/sourceZIPs/reference projects unchanged. docs/l2_roles_restore_r127.txt.


203. r128 L2 orientation/anatomy correction (2026-11-10). User supplied all scorpion direction corrections, confirmed Frame3 falseX/trueY. ConventionfalseX=headright,falseY=headdown. All10source captures indexed with [0,2,1,2,1,3,3,3,2,0]bits; native canonical-left/up normalization[3,1,2,1,2,0,0,0,1,3]. Old labels disagreed with actual normalized game packets; actual reversed frames2/5 fixed by mirroring scorpion_base2 anddelta5 in BOTH axes, preserving paired bitmap/ECMplanes and exact exports. Compressed295->291 and193->181bytes inexisting slots, other packets untouched. Source64x64RGBA family comparisons exact after corrected whole-image flips (including3vs9 vertical), all31actualZ80decodes match and all10scorpions independently match chosen exports.
Native snake role4 is already a separate neck piece. Final head/neck/4spiny/9round/tail order usesbodyordinals0..3=198,4..12=199. An initial unreleased draft added an extra round body before spines; corrected after checking native role4 and arcade assembly. Final actualgame700update trace verifies all13ordinals and stable type across22/23 phases. Exactly two runtime bytes A7B1:09->04 andA7B4:38->30; image size unchanged,A7BAend<unpatchA7C0/captureA7CC. Packedruntimeends3814<3820. No new memory allocation,geometry,animationorder/rate or bankcode changes. Allregion changes constrained to2packets,compressedruntime,debugversion. Other7levels andr127bossrepair bitidentical.
PASS:1547ordinary approach updates/all10scorpionIDs;700boss/firingupdates/5exactcache+backgroundchecks/13bodyroles;31decodes/128tiles/96palette160rows/288dirtyinjections;12coldcachedtransitions/6longbossresetrevisits/3normalcoldfire/debug/Space redraw;256actualRAM IM2words(fixedFF,not256hardwareIRQprobes);16TAPreconstruction/checksums,ZIPCRC. Previews headings.png/comparison.png and interactive index atbuild/graphics/l2_orientations_r128 are asset comparisons; actualboss_probe_690.home.png and ordinary approach captures are emulatedgameplay, not hardware. Images inspected. Longgame tests useinvulnerability/gameoverbypass. No hardwareconfirmation. SourceZIPs/referenceprojects/stable99/100/stock64KBunchanged. Candidatebuild\fullgame\l2_orientations_r128\RType_TS2068_r128.zip SHA7a55a56e7b383ea1ab9b552216ff34ebacc9a13bffb8b229ce8ddb62ad43babf. docs/l2_orientations_r128.txt.


204. r129 L2 boss/snake foreground and speed (2026-11-10).
Native main copy is8653/CALL8979; entity drawing follows. Previous background-only repair did not prevent visible actor padding/cleanup erasing stopped boss. Hook8689 replaces CALL1400 with CALL10D1, invokes1160 repair then1400, before original868C timing poll. Restore both actual front bitmap/ECM planes for218 nonempty cached cells; boss wins overlapping8x8cells including black padding, not per-pixel alpha. Restore background only where native7E00..807F actor ownership is nonzero, clear owner/native7800 tag; skip70empty cachecells. Ownership plane crosses DOCK3/HOME; bank4 must be unmapped before reading. DI around bank4 coordinate reads, restoremap9 before IFF/registers.216byte copierB002..B0D9,15byte empty helperA807..A815, projectileA816..A84B unchanged, low11C9 reused. CacheCB00..D51F unchanged; runtime image bitidenticalr128. Gateway relocation audit: reverse3820/global398B,cold1DE,renderer157B,FA0,runtime restore and installer save targets; unpatch restores8689 and868C. Other7regions/bank7/coldD920..DC3F/projectile source unchanged.
Rejected unreleased shortcuts: interpreting owner0 as dirty and front cell-tag validity both failed exact visible-pixel checks. Final safe path always restores nonempty foreground, only selective background. PASS two700update sustained-fire/ceasefire tests,5checkpoints each7523visiblepixels plus1744backgroundscanlinecells;221art/67empty direct-fixture ownership injection/codebank check;12coldcached transitions/6longbossrevisits/3unmodifiedcoldfire/31actors/128tiles/96palette160terrainrows/debug;256actualRAM IM2words,not256hardware IRQ probes;all16TAP reconstructions and ZIPCRC. Longgame tests use bypasses. Actual boss_visible_690.home.png inspected; emulatedgameplay notassetpreview/hardware. Matched update-indexed controls updates100..230: r128 1820757.14 vsr129 1637107.29 cycles/update (10.09% fewer),not hardwareFPS. No geometry/segment/rate reduction. Candidate build\fullgame\l2_pre_copy_r129\RType_TS2068_r129.zip SHA58dc29c371a9d768e9442e557d519af8c5aede247bed8fd98927ca7ded1590c1. Hardwarepending;stable100/stock64KB/referenceprojects unchanged.


205. r130 L2 interrupt star occlusion (2026-11-10).
User observes trails/holes between boss redraws. NativeBEFF/BF01/BF03 erase andBF25/BF40/BF42 draw run inIRQ, independently of8689 finalcomposition. Native sweep of19active records/21slots x4speeds x32positions x4clockphases=9728cases reproduced11408writes into boss inr129. Final explicit BEEA CALL11BE guards old erase cell and preserves DEC C/result flags; BF11 CALL10D7 guards new draw cell and native early return. Shared predicate10E2 uses stopped7A8E and xcolumn>=8; conservative horizontal occlusion x64..255, including black gaps, not per-pixel masking. Native wrap cleanup x0 cannot touch boss. Ordinary stars and left-quarter stars remain native. Exact r129copier/asset/runtime/cache bytes retained; no extra redraw. Guard10D7..10EE,cleanup11BE..11C8,not overlappingmusic11D0. No sharednative metadata modifications.
Discarded unreleased prototypes tried7B/7E/81metadata markers. Direct sweeps could pass while liveIRQwatch caught native copy clearingflags;7E-marker optimization also failed exactbackgroundcolour checks. No failed prototype ZIP released. Final guard sweep zero inside/3552outside; live700update firing zero inside/30974outside whilebossactuallypresent; both700firing/ceasefire runs exact7523actualvisiblepixels x5checks. Firing background1744scanlinecells x5exact; quiet intermediatebackground differs1517 bitmap/colour comparisons at300, other4checkpoints exact. Probe separates intermediateback fromactualfront; allactualfrontchecksPASS. Do not claim quietbackgroundidentity; diagnosticretained. Scene-presence gating excludes post-boss star writes, which are legitimate. Short140update diagnostic proved starzero but intentionally failed13-role coverage (only4observed); final700update rolecoveragepasses.
Installer uses existingbank1padding3836/39CB. Restore39F2->39D6 returns original BEEA0A0DA7/BF110AA7C0. Initial cached-core audit caught writes going toDOCK5 under6F; fixedunpatch switches4F toexposeHOMEbank5, restores6F beforeDOCK5caller. Redundant868Cpoll restoration removed (installer neverchangespoll); complete cold/runtime references audited: reverse3820/gettile3870/global398B/save3974/restore3927 unchanged fromr129 afterfinallayout, lowcold1DE/render157B/FA0/highinstaller/runtimeCall checked. Native core/cachedworkspace/stack integrity pass12transitions/6longbossroutes. Source regiondiffrestricted lowguardspadding/native loader/debugversion; A000..FFFFbitidenticalr129,other7regionsbitidentical. All31actor/128tile/96palette160terrain/debug/3unmodifiedcoldfire/256RAMIM2words/16TAPreconstruction/ZIPCRC pass. FixedFF,not256hardware IRQ probes;longgame usesbypasses. CPU matched100..230update mean 1637107.29r129 vs1642279.82r130 (+0.3160%),not hardwareFPS. Actual boss_visible_690.home.png inspected after final render; emulatedgameplay,hardwarepending. Candidate build\fullgame\l2_star_guard_r130\RType_TS2068_r130.zip SHA697a6f02faebbb31fb9bf3396220444650c7a1cbd7d71408d2c9f29e691bafa1. Stable100/stock64KB/referenceprojects/sourceZIPs unchanged.

206. r130 final archive confirmation: exact final binary quiet-phase probe repeated700updates; all7523visiblepixels pass5checks, intermediateback diagnostic unchanged. ZIP now uses fixed entry timestamps/permissions for reproducible packaging. Final SHA8c3dd11edfbd228cdf1565417953680c1a926b8191f4638a7e568bf4414fc138 supersedes entry205 archive checksum only; regionc80ff11af018e5f0f6cb36c5f24df8a4e131dd1920a3daaf513a69ea57bb75d0,TAPmanifest andgamebehavior unchanged.


207. r131 L4 shared approved ECM walkers (2026-11-12).
Exact original bitmap/dimension comparisons confirm L4ghost19..21=L1native35..37; L4head6..9=L1native30..33 (also L6head10..13), extraL4head5=L6native9. L4round28..31=L1native53..56. Previous L4maps omitted ghost/head, and round stillusedr90olderassets. Reuse EXACT chosen3ghost32poses from convref/rtype-l1-ghost-assets.zip,4Chead32poses from saved walker_choice_r90/L6_head files (same latestL1),4round24poses from convref/rtype-l1-walker-snake-assets.zip. All11runtimeassets independently match bothlatestL1 and originalchosen exports, legalnormal8x1pairs. Noresampling/settings/newart. All12nativeIDs mapped; firstnativehead5usesapprovedpose0,6..9match4nativeposes; roundretains4celcycle. Existing gunwalker14..18 unchanged.
Raw3424bytes B280..BFDF, codeendA8EE<A9C7,immutableend39A6<3A00. Nativeboss expanded5744bytes unchanged, preloadsplit1000 externalA9C7..B3C7 extends onlyinto nowredirectedround28..31 source. Aux366bytesA4E9..A656 reusesonlyredirectedhead5..9 packets; HOME C4E9backup -> temporaryB280prefix -> expand tailBD00..BFDF, thenmain2688byteprefix. Originalpreload relocatedbeforeart torespectsource lifetime; originalwarmupconditionalCALL removed andcache-validE3F0gate retained innewentry. Scratchstack5CF0keptvisible across6F/ED/2Fmaps,IX/nativeSPpreserved. Initialunreleased probes caught earlypreloadcallerstackvisibility, wronglycheckingboss cachebeforepreload, secondinitializationdecompressingoverwrittenstorage, and directtestsentinelwrittenHOMEwhileDOCK7mapped; allcorrectedbeforeZIP. Actualsource-lifetime/code/RAMtests nowpass title+gamestart2loads andcachedtransitions. Every cold/runtimegateway patched: preloadtableDEB4/5, imageDEE1/2, fastvisibilityDDBB/C, fastpairDF6C; newprefix fastsynthjump updated andintraextension symbolsreassembled. Otherregiondifferencesrestricted bank1packets/retiredsource7gatewaybytes;L4palette2000..27FF,bank4code/IM2,bank7,allother7levels bitidenticalr130.
PASS actualZ80coldL4+600ordinaryupdates/all3familiesnaturallyobserved/3424exactliveartbytes/5744exactbosscachebytes/12nativeIDposehookcases;600ordinary+400BBbossupdates/artretention;12coldcachedtransitionsincluding2L4visits/nativecore+cachedsource+640attrsperaudit;16TAPreconstruction/checksums/ZIPCRC. Diagnosticinvulnerability,not hardware. Comparisonconfirmed_families.png isassetpreview; L4_ordinary_500.home.png andL4_boss_300.home.png actualemulatedgameplay, inspected. No hardwareFPSclaim. Terrain/L4bossart,r130L2starfix,stable100,stock64KB/referenceprojects/originalZIPs unchanged. Candidatebuild\fullgame\l4_shared_r131\RType_TS2068_r131.zip SHAbe0fd3d3e66712d392b6995290e11db4ee2b0ba8bb5c2c328057a3bcaafeef97.


208. L4 armoured snake source match and interactive RPC editor (2026-11-12).
Userphoto13114 yellow/green/red linked enemy identified as current L4native33..35,24x24; earlier familybitmaps are also reusedbyL1, but actual arcadeL4match is red/orangeframe/greencore/silverlink armouredhead object1538. Locallydecodedactual M72 captures:1538palette4/frame30300,1540p2/frame31800,1542p5/frame33900,1554p6/frame32400; stored actualobject flags/flips/provenance. Earlybroad30000..42000inventory included laterbrownwormstage; thoseunrelatedbrownobjects wereexcluded. Actualreference31800 confirms greenorbchainsandarmouredheads; nativepicturedchainreuseslargehead/jointartforlinks. No claimofidenticalarcadebodytopology. Fourcapturedorientationposes are not agait; native33..35pose/flipmappingexplicitlypendingbeforeintegration.
Newbuild/graphics/l4_snake_converter/index.html standalonefile editor embeds sourceRGBA,originalreference,unchangedRPCworker/GPLlicense/provenance. Sharedbrightness/contrast/saturation/gamma,crop/trim/scale/rotation/flips/palette,SierraLite/FloydSteinberg/Bayer4/no-dither,24default/32option/8x1inspection,autosave/choiceimportexport/4frameassetZIP. Repeatedhorizontalheadpreviewisexplicitlyillustrative,notcapturedmotion; overlapclashcountretained. Defaultnormalblack,noBRIGHTblack. SourceR131nativecomparisonreadonly; game/cartridgefilesnotchanged.
PASS32core conversioncases plusactualChrome fileprotocol/sharedgamma/4dithers/source3vs4poses/24and32size/normalblack/legalpairs/illustrativelabel/autosave/importexport/ZIP/mobilelayout/noJSerrors. Testexport4x144byte24x24pairedframes,choicesmetadataandZIPCRCverified. Diagnosticsarcade_candidates.png/native_contact.png/head_candidates.png/identity_comparison.png assetidentification sheets; converter_desktop.png(gamma1.5/32size teststate) andconverter_mobile.png UIcaptures inspected,notgameplay. Builder scripts/build_l4_snake_converter.py; testsverify_l4_snake_converter_core.mjs and_browser.mjs. HTMLSHA1aa86d842799181e7ea5e53b1ef4bc240fc04118e722064e715045e8da27fa39. Currentgame remainsr131,stable100/stock64KB/referenceprojects/originalZIPs unchanged.


209. Twin-rocket craft editor and correction to208source-family claim (2026-11-12).
User clarifies craft has two red rockets/nozzles and selects left1538image asclosest; flags other1538-page forms asnotmatching. Earlier208claim1540/1542/1554wereconfirmedturningposes wasunsupported andiswithdrawn. Arcadecodes/actualRGBAwerecorrectlydecoded but adjacency/capture alone didnotprove sharedidentityoranimation. Separate user-selected1538singleview(capture30300/p4,flipXtrue), actual1538otherhorizontalfacing(33000/p1), and upright1042candidate(30300/p4) into distinct sourceoptions.1042notpixel-identicalto1538underrotation/mirroring, so labelledcandidate,notconfirmedrotatedpose. Nativecomparison52..54isredangular/cyancoretwin-launcher family; otherredtriangular55..57and242/244references investigatedbutnot substitutedafteruserclarification.
Newbuild/graphics/l4_twin_launcher_converter/index.html usesunchangedRPCworker/sharedsettings/crop/palette/SierraLiteotherdithers/importexport/assetZIP/default24optional32. All1538/1042recordsinclude actualspriteflags/palette/captureprovenance. Referenceannotatedactual30300image yellow1538/cyan1042. No inventedgait ornewframes. Corrected previoussnakeeditor: default1538isolated,1540/1542/1554onlyunverifiedreviewoption; native33..35snakeidentity/posemappingunconfirmed. Existingautosavekeypreserved, no sliderchoicesdeleted. RebuildwritesbothsourcecorrectedmetadataandHTML; currenttestsnakeZIPnowexportsone1538viewinsteadold4formpack.
PASS32corecases,actualChrome fileprotocol/sourcecounts1/2/1/3/sharedgamma/all4dithers/24and32size/legal8x1/normalblack/autosave/importexport/assetZIP/mobileresponsive/noJSerrors. Initialmobiletestfoundlongframelabel7pxoverflow; localtransportwrapfixpass. Bothdefaultexportsone144byte24x24pairedframe,ZIPCRCverified. identity_comparison.png andarcade_reference_annotated.png areasset/sourceviews;converter_desktop.png/mobile.png inspectedUIcaptures,notgameplay. LauncherHTMLSHAda7b41ae3c7541f878a71a08ce7fd54c364604b61cc26f9ed608c903d352cb46,correctedSnakeHTMLSHA6b9ef1a7d98c8d255155366f20ab42fcede7676fba7a0a4cba72a36bfe983b34. Builderbuild_l4_twin_launcher_converter.py; testsverify_l4_twin_launcher_converter_core.mjs/_browser.mjs. No gamefileschanged;r131/stable100/stock64KB/referenceprojects/sourceZIPspreserved.

210. L4 boss killability investigation (2026-11-12).
Current r131 render/BB tests did NOT establish defeat. Deterministic probes:600 ordinary updates then BB; weak-point trace400 boss updates. Three hull actors HP63 (invulnerable), three weak actors HP32, native descriptors58/60/62. Actual native descriptor returns retain24x8,8x24,24x8 geometry. Weak actors repeatedly reach1B14/8E85/8EA1 but zero collision-grid writes for owners84/87/8A; sampled grid has hull81/82/83 only. Trace reveals occupied-cell compositor rejects native weak sources outside cache C9C7..CF43 and returns through0D22/8EDA without painting/publishing weak ownership. This is evidence of blocked weak-point publication, not a completed defeat proof. True victory isF59D setting7A84=65 after three parents destroyed; unrelated7A9B exit timer MUST NOT be called victory. Earlier977-update exploratory probe natural exit with no HP decrement was not a kill. Automated aim input did not move ship, so bot cannot support any reachability/defeat claim. Scripts probe_l4_killability_r131.mjs, probe_l4_weakpoints_r131.mjs, probe_l4_paint_r131.mjs; JSON/log outputs under build/fullgame/l4_shared_r131. No new images; HOME diagnostic snapshots retained. No release/game binary changed; repair and real-shot defeat regression remain outstanding.

211. Twin-launcher native-shape shading assist (2026-11-12).
User asks to retain diagonal Spectrum poses and algorithmic symmetry rather than slider-only arcade resizing. Actual native52upright/53diagonal/54horizontal retained together. New assisted source uses identical coloured silhouettes/holes with black background cutout, per-material red/jade/silver ramps, and symmetric distance-to-silhouette rim shading. Shared0..100strength plus existing RPC/SierraLite/settings across all3poses. This is enhanced Spectrum artwork inspired by arcade shading, not extracted new arcade frames or installed gameplay. Unchanged RPC worker/license. Browser test verifies3poses, strength changes output, exact prepared-mask equality at0/80strength, legal8x1/noBRIGHTblack, original source choices, import/export/autosave/ZIP/mobile/noJSerrors. symmetric_shading_desktop.png inspected; first attempt treated opaque black as solid and was corrected to coloured-silhouette distances before completion. Editor build/graphics/l4_twin_launcher_converter/index.html; reproducible builder build_l4_twin_launcher_converter.py. Existing source approvals/settings preserved; game artwork not replaced by this trial.

212. r132 boss target repair and eight-level review (2026-11-12).
L4 r131 weakpoint native overlays were rejected on occupied cached hull, producing no84/87/8A collision owners. New L4 typed3B/4B/5B dispatch allows only matching parent3/2/1. Native fallback coordinates for58/60 now derive from parent positions +3/+3 and+0/+4, aligned with visible front/middle green bulbs;62retains+7/+2 and becomes24x16 to match rear green target. Its54native packet bytes use retired redirected round31HOME D400..D436 (fileB400), outside external compressed-source lifetime endingD3C7. Descriptor62only changed atfileBC09. Native damage32perweakpoint and all boss movement scripts unchanged. New dispatchA8EE, end/packet limits in weakpoint_contract/l4_shared_contract/walker_runtime; complete image remains belowA9C7 and immutable packet below3A00.252actor/parent/register/stack/map cases pass. Do not call these source-boundary tests: final gate selects native actor types.
Real player key input, predicted target tracking, ordinary shot edges; player protection and death bypass only, no enemyHP/timing edits. Exactly32nativeA57D shot decrements for each851C/8537/8552, all reach0; actualF59D victory observed atboss update237. Earlier probes that merely reached7A9B/script exit were NOT kills. Initial bot aimed using stale coarse7AA1/2; corrected to pixel positionF680/1 and explicit test-defined key bindings. Dead collision entries excluded; predictive aiming tracks before short exposure windows. Failed/helper-packing/native-branch-first-match attempts not release evidence; corrected to native fallback last-match.
All8native BBscenes audited separately, actor ownership/ray opportunities/onscreen counts/native sprite submissions. Found L1openeye type11/actor2 had no owner; compact existing0D01gate permits native open eye. Its owner now452samples and real health decreases. L3 native25/26gun mounts and96..100engine actors similarly lacked ownership over cached ship; final actor-table/type4/6/38 dispatcher publishes native ownership then tail-enters original compositor, retaining cached pixels. Duplicate native-pixel-copy and extra-CALL variants failed coldL3/code-integrity checks and were discarded. Final metadata-only implementation passes cold startup/fire; all flagged target actors now have ownership. L1body is invulnerable; L8actor28 is non-drawing/offscreen controller, not a required visible target. Ownership/reachability audit is NOT a claim of complete victories on all8bosses, or universally clear left-edge rays: some targets sit behind other parts/approach directions. Full native victory established forL4 only in this change.
PASS all8target reports, exact static mutation ranges, all16START/LEVEL tape reconstructions/checksums, unchanged other5regions,252L4gatewaycases, unmodified cold1/3/4fire,12cold/cached native-source/core/attribute transitions, final ZIP CRC. Test invulnerability changed from1to255 because accepted IRQs consume1before next main update; this is harness protection, not a gameplay patch. New allocation ends are authoritative to prevent future helper reuse. Stable r100, stock64KB, r131archive, originalROM ZIPs/reference projects unchanged. New offline editor trials remain uninstalled. Candidate build/fullgame/boss_targets_r132/RType_TS2068_r132.zip SHA4d673a78e55d594c894f2855ff6d8d6053837c6d66014a2a9625afeb6cef98c5. Hardware pending. Diagnostic flagged_actor_art.png and L1_43.png are identification sheets, not gameplay. L4_targets_80.png is an entrance/rapid-fire capture, not a completed-frame quality claim; completed180frame diagnostic captured separately.

212visual follow-up: L4_targets_completed_180.png rendered from native-loop868Cafter180updates with firingdisabled; inspected actual completed game frame, not an asset mockup. New front/middle green overlays are visible; some8x1 colour sharing persists around small modules, not a full visual redesign. Native-victory saved probe counter237; earlier progress message rounded it to236(last health-decrement update).

213. r133 selected twin-rocket launcher integration (2026-11-12).
User provides convref/rtype-l4-twin-launcher-choices.json. Explicit user selection overrides its remaining generic decision=tweak metadata. Imported with unchanged offline RPC worker through actualChrome editor and exported all3poses. Source assisted native Spectrum silhouettes, shared assist83/brightness39/contrast40/saturation74/gamma1.12/SierraLite/24x24/trimtrue; no rotation/flips or invented animation. Native52upright ->184,53diagonal ->185,54horizontal ->186; original native pose/flip scripts unchanged. Exact432pairedbytes from exported ZIP installed atDOCK5B0C0..B270, normalblack/noBRIGHTblack/legal8x1. selected_editor.png, selected_sheet.png and selected_sheet_8x.png are asset/UI previews, not gameplay captures.
Preserves r132 other7regions bit-for-bit and existing3424L4raw sprite bytes/5744boss cache. Tight immutable storage solved by four safe streams: selected launcher358byte packet replaces retired native14..18source fileA72E..A894 (HOME C72E); oldraw first256byte prefix packs207bytes into newly retired native52..54source fileB64D..B71C (HOME D64D). Loader completes boss preload first, then copies launcher/prefix/aux packets from HOME to commonB380scratch and expands B0C0/B280/BD00 respectively; immutable main remainder expands B380..BD00 last. No in-place compressed-source overwrite. Packet source ranges and2noncontiguous final asset segments recorded in launcher_contract/l4_shared_contract/walker_runtime. All moved post-loader references relinked: sprite table, idmap, phases/latch/fast visibility/synthesis/pair helpers, native-coordinate CALL, weakpoint dispatcher gateway and immutable image pointer. Runtime endsA985<A9C7, packed bank1end39C7<3A00. Existing L4weakpoint packetD400 and descriptor62 unchanged.
PASS exact selected432bytes plus old3424livebytes and5744cache onactualcoldinitialization/600ordinaryupdates; actualZ80native52/53/54selector mappings and otherapprovedposehooks;12cold/cached transitions includingexplicit432byte checks onL4returns; unmodifiedcoldL4startup/fire; all16START/LEVEL tapes reconstructed/checksummed; staticmutation-range proof, unchangedother7regions, ZIPCRC. L4nativevictory again observed in actualshot test:32health decrements on each of3targets, no enemyHP/timing edits; player protection only. Hardware pending. No blanket all-boss defeat claim added. SourceZIPs/references/stable100/stock64KB/r132archive untouched.
Reproducible export_launcher_selected_r133.mjs/build_launcher_r133.py/finalize_launcher_r133.py. Candidate build/fullgame/launcher_r133/RType_TS2068_r133.zip SHA396ec44107bc2d2245b1a5a1da735ad887edf95ba51784862f6016a4566e0de2. Replace complete rtype folder and reset; startup R133 PREPARING. Split-stream allocation metadata is authoritative for future asset work.

214. Snake converter removes withdrawn launcher candidates (2026-11-12).
User flags residual launcher imagery. Removed all1538/1540/1542/1554source choices, incorrect arcade scene reference, and mixed comparison gallery from build_l4_snake_converter.py and generated page/data/provenance. Page now embeds only actual native33/34/35snake poses fromr133. No substitute arcade identity is asserted; arcade match pending. Gallery/reference both show the native snake. RPCworker unchanged. Archived old generatedcandidate/matched PNGs, inventory and trial ZIP outside converter under build/graphics/l4_snake_withdrawn_sources_20261112; originalROM ZIPs/referenceprojects untouched. Kept localStorage key; removed source IDs fall back to current snake while slider values/notes survive. Dedicated browserPASSnative-only3poses/no1538/noextraselector, oldsource migration withgamma1.41/notes preserved,4dithers/legal8x1/normalblack/export3frameZIPCRC/mobile/noJSerrors. Updated combinedlauncher browser test to require separate snake-only sources. converter_desktop.png/mobile.png and native-onlyidentity_comparison.png inspectedUI/assetcaptures, not gameplay. No game/buildarchivechanged; r133 SHA396ec44107bc2d2245b1a5a1da735ad887edf95ba51784862f6016a4566e0de2 remainsunchanged.

215. Restore the retained snake arcade reference (2026-11-12).
User corrects214over-removal: only first1538frame was the missile launcher; restore other3referenceframes1540/p2/capture31800,1542/p5/33900,1554/p6/32400. Re-decoded actualROMcaptures, restored3framearcade source/default and native33..35comparison, both in gallery/reference. No1538pixel asset included; sourceimage hashes checked against launcher1538exclusion. Native runtime orientation mapping stillpending before integration. Existingreview source migrates to arcade, sliders/notes preserved. BrowserPASS3arcade+3native/source switching/reviewmigration/gamma+notes/4dithers/legal8x1/normalblack/mobile/noJSerrors/3framearcadeZIPCRC. identity_comparison.png and updateddesktop/mobile inspectedUI/assetpreviews only. Corrects214native-only scope; game/r133archiveunchanged.


216. r134 selected L4 snake integration (2026-11-12).
Imported convref/rtype-l4-snake-assets.zip (SHA256 c01005b3861918ebebebf809ef320cc1616a981bc29b8676957200492d4356bb), all three selected24x24 paired ECM poses. Settings brightness52/contrast76/saturation69/gamma1.1/SierraLite, no BRIGHT black. Native33left connector -> source2/id189; native34lower-left -> source1 vertically mirrored/id188; native35down -> source0/id187. Exact selected bytes preserved apart from that row reversal; no added animation cycle. chosen_snake.png remains an asset preview, not a gameplay image.
Rejected development allocation AE00..AFB0: cold600updates passed but cached L4 return corrupted the boss cache because expanded snake bytes replaced compressed reload sources. A second rejected D680 placement overlapped warmup D800 vector initialization (last48bytes). Final snake allocation is DOCK6 DA00..DBB0, beyond boss raw cache C000..D670, IM2 D800..D900 and D910 row scratch, below DC50 cache code. Two immutable189/203byte packets remain in retired ghost/snake source slots fileA8E4/B474, copied via B380 scratch. Boss preload first, snake into DOCK6, then existing launcher/prefix/aux/main streams. Runtime endA9BE, packed end39FB. Lesson: cold-load checks alone do not prove cached-source lifetime safety; verify expanded artwork after transitions and account for full vector/scratch reservations.
Final tests PASS: exact432snake+432launcher+3424existing art RAM and5744boss cache,600ordinaryupdates plus actual Z80native pose selectors;12cold/cached transitions including exact snake and launcher comparisons; unmodified cold L4startup/fire; native L4 victory F59D with32real-shot health decrements per target (protected test player, no enemy HP/timing edits); all16START/LEVEL tape reconstruction/checksums, permitted mutation ranges, exact ZIP input-pixel mapping, normal-black ECM and archiveCRC. Other7level regions bitidentical r133; r133launcher/r132boss fixes retained. Hardware pending; not all bosses claimed defeated. Stable r100/stock64KB/r99/reference projects and originalZIPs unchanged.
Build scripts build_snake_r134.py/finalize_snake_r134.py; verification scripts verify_snake_runtime_r134.mjs/verify_native_revisits_r134.mjs/verify_cold_launcher_r134.mjs/probe_l4_damage_r134.mjs. Candidate build/fullgame/snake_r134/RType_TS2068_r134.zip. Replace complete rtype folder, reset, launch rtype/rt.tap; startup R134 PREPARING.


217. L4 boss target confirmation and star-cost comparison (2026-11-12).
User questions practical killability/speed inr134. Confirmed packaged coordinate/typed-parent ownership repair fromr132 remains: front+middle follow parent positions, rear24x16; actualshot probe reachesF59D with32nativehealth decrements each. Diagnostic uses invulnerable predictive pilot, so does not establish human difficulty. New profile_l4_stars_r134.mjs compares same setup over60bossupdates (40..100): normal167189022Tstates ~1.266Hz; stars disabled151945001 ~1.393Hz at3.528MHz, ~10.0%cadence improvement. Diagnostic-only flagBE62 manipulation, no released binary changes. Stars are measurable overhead but their complete removal does not solve dominant boss cost. Different timing can alter shot/actor trajectories, so this is a gameplay comparison, not an isolated instruction-cycle census. Logs/profile summary underbuild/fullgame/snake_r134; no image produced. r134ZIP/stable release unchanged; hardware performance not measured.


218. r135 L4 direct prepared-cell path and target-location image (2026-11-12).
User requests significant boss-drawing speedup and an exact target image. Profile over boss updates40..100 exposed repeated merge loops and independent projectile screen reads. Unreleased unrolled-shift helper gave only~0.5% matched no-firing cadence gain. Projectile helper and inline early-out experiments were also not worthwhile; all discarded, including cold CORE/copy-length changes. Final RTCORE and other7level regions are bitidentical r134; no projectile changes retained.
Final runtime stores incoming prior-cell owner in previously unused src low byteA3FB. At the prepared-cell copy branch, an11byte resident DOCK6 DBB0..DBBB helper returns Z for empty/same-actor ownership; these cells use the existing forward/reverse/flash copy. Other-owner overlaps retain the compositor. Collision/target scripts and artwork unchanged. Helper is appended to the second snake packet, within retired native33..35source capacity B474..B567; final raw snake432bytes unchanged atDA00..DBB0. No code relocation, new IM2 allocation or extra RAM bank. Explicit packet bounds and helper reservation recorded. Current asm source compositor is historical; final binary patch is reproduced by build_l4_speed_r135.py.
Matched no-firing emulator60-update sample: r134138729333Tstates (1.52585Hz), r135132635065Tstates (1.59596Hz), cadence+4.595%. This is modest, not the requested substantial speedup; stars unchanged. Earlier firing benchmark measurements were timing/target-destruction dependent, so not used as isolated draw speed proof. More ambitious fully preshifted/mapped object caches still require a safe additional bank layout; not implemented in this candidate.
PASS:600ordinaryupdates/exactsnake+launcher+oldraw/bosscache/posehooks;12coldcached transitions; unmodifiedcoldL4fire; actualnativeF59Dvictory at234bossupdates with32A57Dhealthdecrements per target, protected testpilot only; all16START/LEVELtapes/checksums, constrainedmutationranges/exactselectedassetbytes/helperbytes, ZIPCRC. Hardware pending.
Image build/fullgame/snake_r134/L4_targets_marked.png is actual undamaged emulated boss capture after120updates, not an artwork montage. Boxes computed from parent actor coordinates using the shipped r132/r134rules: frontparent3+(3,3)16x16, middleparent2+(0,4)16x16, rearparent1+(7,2)24x16. Captured cell coordinates(14,5),(17,6),(20,7). Closed/open states differ; only rear owner138 is active in this frame. Earlier42update capture was before boss spawn and was rejected/replaced; finalmarked/unmarked PNGs inspected. Capture script capture_l4_targets_r134.mjs; no manual/art-image target guesses.
Candidate build/fullgame/l4_speed_r135/RType_TS2068_r135.zip SHA25624e966c25cee8d606e17e0a22dc5b06f61b7cfe786c16fb085a1b19eb14f80f3. Replace complete rtype folder/reset; R135 PREPARING. r134/r99/stable100/stock64KB/originalZIPs/referenceprojects unchanged.


219. r136 L4 boss-shortcut collectibles and native follower delay (2026-11-12).
User cannot see targets open/reach rear target from unpowered BB shortcut, asks collectible and faster followers. Explicit preference: place a collectible, not automatic rear Force. L4-only BB now calls a27->51byte pickup helper at DOCK0 01C8 below0200 (final actual size in follower_contract): native8BAE first, then two ordinary type2 weapon pickups in native slots7AC1/7AC5 at shipX+4/+6 and shipY. Two chosen to provide the powered Force state exercised by the rear-fire test; no automatic equipment. Other levels' BB helpers unchanged. L5 01C8 IRQ helper and8F00..9000 reservations unchanged.
Native Force recall state6 previously gated by frame&3 at972C; AND00 now permits movement every game update. Native Bits position history99EC..99F8 now reads previous sample rather than the sample three updates old, retaining history write/ring-wrap and vertical offsets. No IRQ-native renderer calls or higher draw-rate claims: drawing remains on the main game clock. Patches installed in cold RTCORE and all common region images, preserving all artwork/caches andr135directcopy.
Tests PASS: actual Z80 history output[5,5,7,9,11,13,15,17] against scripted playerX4,6,... demonstrates1samplelag; recall position[20,15] ->[19,14],[18,13],[17,12],[16,11] over4game ticks. Live L4BB: both ordinary collectibles exist withForcepower0, move into both ->power2, normal arrival docksrear(state2/A3=2), then normalfire activates native laser descriptors in HOME5F00/5F34/5F68 with rear directions1/3/5. Initial rear-fire assertion watched wrong5EB4small-bullet buffer and was corrected to native Force beam storage. Older controlled Force fixture fromr72 failed attachment on BOTH r135 baseline andr136 (also with a one-row adjustment); no docking regression conclusion inferred from that stale fixture. Replaced acceptance with actual pickup->rear dock->fire proof; separate native stamped-contact probe confirms front/rear contact poses. Do not report the stale fixture as passing.
Final regressions PASS600ordinaryupdates/exactassets+boss cache/nativeposehooks,12cold/cached transitions, unmodified coldL1/L4/L5startup/fire, actualnativeL4victory and32healthdecrements pertarget using protected entrance-phase aiming test,16START/LEVEL TAP checksums/reconstruction, exactCOREmutationcontract/L5reservations/inputassets/helperbytes/ZIPCRC. Hardwarepending.
CRITICAL CORRECTION: prior claim that L4 targets open/close was unsupported. Native damage path subtracts health when hit; no opening-animation verification exists. Actual all-targets-alive snapshot at120updates has no collision-owned front/middle target cells, rearowner138 atx20..22,y7..8 but first occupied owner fromleft is131 andfromright130. Overlapping enlarged hulls obstruct these shot rays. Entrance-phase automated kill does NOT prove settled-fight practical reachability. Audit settled_target_obstruction.json records exact snapshot cells/actors. r136 does not fix geometry. Asked user preference: exposed exterior targets vs preserving openings with redesigned surrounding hull gaps; pending. TEST_HISTORY218 image caption wording about open/closed states is superseded by this correction. Source images/geometry otherwiseunchanged.
Candidate build/fullgame/boss_pickup_r136/RType_TS2068_r136.zip SHAc19c2843f90c6620524071105f3de2cf4b29943a517f27ed687b707000f17a00. README explicitly states obstruction remains. Complete rtype folder replacement/reset/R136 PREPARING. Stable100/r99/stock64KB/referenceprojects/originalZIPs unchanged.


220. r137 restores original Spectrum L4 openings and verifies settled defeat (2026-11-12).
User rejects exterior-target relocation, requests comparison with original Spectrum artwork and functional native animation/openings. Read current state/history/release rules. Compared foundation level04.raw and actual native-engine foundation DCK boss animation (existing TS2068 compatibility patches, scripted boss-map jump and protected player). Original hull sizes are ALREADY120x56,96x64,96x88; previous enlarged-hull wording was inaccurate. The conversion filled47of78original transparent8x8cells (14/9/24 across native25/26/27), including access gaps. r132also moved front/middle targets from native actor-supplied coordinates to invented parent offsets, and enlarged rear from24x8to24x16. Earlier target diagram's front/middle16x16 assumption was wrong: original sizes are24x8,8x24,24x8.
Final repair zeroes paired bits/attributes only for exact original tag54cells, preserving all other ECM cache bytes/shading, sizes and the approved artwork elsewhere. Repacked5744boss raw bytes in existing4096+1648preload blocks (new first2272bytes and tail1008bytes, within existing allocations). Native target-coordinate helper now loads originalDF3C BC and returns; no exterior relocation or rewritten movement script. Rear descriptor62 restored3x1/sourceD821. All three original motion-script ranges ED69..EE06/EE06..EEA7/EEA7..EF00 byte-identical to original Spectrum snapshot. Original native actor poses58/60/62 and the moving hull sections govern exposure; no invented opening-animation cycle.
VISUAL REGRESSION FOUND: r135directcopy change produces repeated hull rows. Matched isolation (coordinate-only withr135 vs masked openings with proven compositor) pinpointed it; reverted src22FBA3/owner dispatch3A03A4B720, removed the11byteDBB0helper and restored snake-only203byte second packet. r135's4.6%speed result and ordinaryRAM/defeat checks were insufficient visual validation. r137 withdraws that optimization; r135/r136 retain their historical archives but should be superseded. Source/binary companions, weakpoint/packet/immutable-end metadata updated to prevent reintroduction. Code layout/gateways/IM2 addresses unchanged. Lesson: exact cache/RAM and hit-count tests do not prove blitter output; require actual matched full-boss screenshots in multiple poses before shipping drawing optimizations.
Actual screenshots Spectrum_L4_120/200.png and L4_openings_120/200.png, Spectrum_ECM_animation_comparison.png and targets_open_annotated.png inspected. Spectrum side is actual original-art/native-engine emulation, not a recoloured montage or hardware capture. ECM annotations use actual collision-owned cells at update200: front3cells horizontal, middle vertical, rear3cells horizontal. Historical initial repeated-row/contact-sheet variants rejected and replaced by final captures. Static comparison build/graphics/l4_spectrum_openings_r137/comparison.png shows original/current/mask-restored asset layouts; isolation.png demonstrates the r135 regression. These are distinctly labelled asset/isolation/gameplay images.
Settled ownership audit runs300bossupdates with no fire input afterjump and controlled suppression of shortcut pickups/residual projectile state; all3targets remain alive (one native contact/remaining-hit decrement seen in one audit, no target destruction). After120updates, front has98clear-left windows, middle16clear-left, rear78clear-right in181sampledupdates. Visibility alone is not the defeat acceptance gate.
REAL SETTLED DEFEAT PASS: probe_l4_settled_force_r137.mjs collects both real pickups, docksrear through native logic, waits200bossupdates before firing. First hit204; rear gets32nativeA57Dhealthdecrements204..301 from the right with rearForce, middle32at492..527 and front32at566..612 using forward fire; nativeF59Dvictory at613. Initial health32 and final0 verified separately for all3;96registered damage hits, all>=200. Player protected; normal bound-key input pilot; no enemyhealth/timer edits. Traversal uses protection, so this is weapon/target access+defeat proof, not no-damage human playthrough. Preliminary plain-bullet-only left-side pilot failed; its later reused actor slots after level change are NOT credited as boss damage. An initial rearForce test falsely broke at201 because it read levelidentity through a transient mapped bus; fixed by resident DOCK3 identity. Eight-pixel targets also required correcting testaim (+.125 vs old+.625) for the shot origin's4pixel offset.
Performance: matched intact-boss/no-fire/no-equipment60updates200..260, r136277326480Tstates vsr137220916441,20.34%fewer cycles /25.53%higher cadence (0.7633->0.9582Hz at3.528MHz). This measures full geometry/compositor repair in emulation, not isolated instruction timing or hardware speed; star policy unchanged. Transparent-cell restoration removes drawing work despite withdrawing r135fastcopy.
Other final PASS:600ordinaryupdates/exactsnake+launcher+oldraw/bosscache/nativeposehooks;12coldcached transitions; unmodifiedcoldL1/L4/L5startup/fire; live nativepickup->rear docking->rear laser and followerdelay checks;16START/LEVELTAPreconstruction/checksums; exact allowed mutation ranges/cachemask provenance/native scripts/runtimepatches/snake-only packet/ZIPCRC. Other7level regions andRTCORE bitidentical r136, so r136 follower/pickup fixes retained. L5vectors/UI/reservations untouched. No joystick-only detach gesture added; configured keyboard action still needed. Hardware pending.
Reproducible build_l4_openings_r137.py/finalize_l4_openings_r137.py, capture_spectrum_l4_boss_r137.mjs/audit_l4_openings_r137.mjs/probe_l4_settled_force_r137.mjs/render_l4_openings_r137.py. Candidate build/fullgame/l4_openings_r137/RType_TS2068_r137.zip SHA2568e6989a45b79d1b30818141436cf285c6679128025e4989f8bfdd9d83213239d. Complete rtype folder replacement/reset/R137 PREPARING. Stable r100/r99/stock64KB/originalZIPs/referenceprojects unchanged.


## 221. L7 cyan/blue/white armoured walker interactive review (2026-11-12)
- Photo 13152 far-right walker identified as native L7 14-17 (24x24), separate from walking-head 18-22 and gunwalker 25-29. Closest arcade anatomy match is cels 450/452/454: arched armour, forward cannon, torso and piston legs. Cel 448 is unrelated and excluded. Canonical left-facing ROM poses use one frame057000 palette12. Three actual arcade poses versus four native poses; runtime mapping remains pending user review.
- Added scripts/build_l7_walker_converter.py and src/l7_walker_converter.{html,js}; generated offline editor build/graphics/l7_walker_converter/index.html, comparison identity_comparison.png, provenance and RPC licence. Shared brightness/contrast/saturation/gamma, crop, size, palette and dither settings across all poses; 24x24 default and 32x32 detail option.
- Scripted Chrome file-protocol checks PASS: 3 arcade/4 current frames, 24/32 sizes, all four dithers, legal 8x1 two-colour cells, shared settings/autosave, ZIP export CRC, mobile no overflow and no browser exceptions. Diagnostics walker_ui.png and walker_mobile.png; desktop UI visually inspected. This is an asset editor, not playable integration, hardware or speed validation. Game release r137 and stable archives unchanged.


222. r138 post-death high-score display repair (2026-11-12).
Photo13153: L7 score/name screen retained gameplay ECM pixels/colours. Reproduced after coldL7/20updates: native death caller92EF still CALL7690, bypassing existing title score restore19D2; video remained2. Redirect common caller to19D2 in all8region images/RTCORE/RTBOOT. Simply switching video0 left stale standard attributes (render inspected and rejected). An intermediate L7 free-slot helper also failed: FDF0 is not the correct resident fill entry in this build. Withdrawn, no new slot used. Final existing17-byte19D2..19E2 helper replaced in place: CALL1466 menu restore (mode/shadow0, mapping09, stars disabled), HL5800/BC0300/A47, CALL0073 resident fill, JP7690 native table draw. No extra allocation; all private01C8 users, L5reservations, art and r137L4opening repair unchanged.
Verification scripts/probe_highscore_r138.mjs and verify_highscore_r138.mjs. Baseline/restored diagnostic RAM under build/diagnostics/highscore_r138. All8cold selected levels boot/fire and reach20game updates; invoke actual92EF caller with entry mapping normalized09 because frame-end can be inside a temporary bank mapping. Mode0/shadow0/bank09/scoretableflag asserted. This is an injected score-display transition, NOT a natural death/name-entry interaction or hardware test. One intermediate probe incorrectly sampled temporary mapping27 and failed; boundary stepping without IRQ delivery also rejected. L7 all768standardattrs exact47exceptzeroedgecolumns; L7_scores.png rendered and visually inspected clean white text/black. AllTAPchecksums, ZIPCRC and region exactdiffscope (scorehelper/caller/versionlabels only) PASS. All existing artwork retained.
Reproducible scripts/build_highscore_r138.py and finalize_highscore_r138.py. Candidate build/fullgame/highscore_r138/RType_TS2068_r138.zip SHA256b4e73186e0d94f4158988fe821cecac505e7709daae94c7cf19cb0159627ab0b. Complete rtypefolder replacement/reset. Stable100/priorarchives/stock64KB/referenceprojects unchanged. Hardware confirmation pending.


223. L7 native37 red/yellow/green enemy review (2026-11-12). Photo13155 matches native37; native36 is different and excluded after enlarged comparison. Arcade598 from frame061500 palette1 is a tentative mechanical-head candidate, NOT confirmed match. Earlier586 canonical crop invalid/mismatched and excluded. Interactive build/graphics/l7_round_enemy_converter/index.html shows native37 and tentative598; identity requires user review before integration. Single source image, not invented animation sequence. Shared RPC worker/controls,24default32option; no game changes. Scripted browser legal8x1/fourdithers/size/source/autosave/ZIP/mobile/pageerror checks PASS; identity_comparison.png and walker_ui.png diagnostics. Asset editor only, no runtime/hardware/performance claims. Scripts/build_l7_round_enemy_converter.py and verify_l7_round_enemy_converter_browser.mjs. r138 retained.


224. L7 yellow asteroid/orb interactive review (2026-11-12). Photo13156 upper-left yellow object matches native35,16x16. Expanded original arcade object scan57000..66300 to include16pixel objects; contact candidate_contact.png and candidates.json. Shaded arcade orbs6/7/5 are tentative appearance alternatives, NOT verified enemy identity or animation sequence. Each is a separate source selection, actual captured orientation/palette retained. Current native35 also selectable;16x16default/24and32proposalbuttons. Shared unchanged RPC worker with brightness/contrast/saturation/gamma, SierraLite/ordered/Floyd/none, legal8x1 pair controls and ZIPexport. No game integration.
Scripts/build_l7_asteroid_converter.py and verify_l7_asteroid_converter_browser.mjs; output build/graphics/l7_asteroid_converter/index.html. Browser checks PASS allthreecandidate/current sources,sizes16/24/32,fourdithers/legalpairs/autosave/export/mobile/noexceptions. ZIPCRC PASS. identity_comparison.png visually inspected; walker_ui.png/walker_mobile.png generated diagnosticUI captures. Asset review only, no gameplay/hardware/performance claims. Arcade identity remains pending; r138 game retained.


225. L7 native51 emerging-object review (2026-11-12). Photo13157 matches current24x48 compiled51. Foundation original sprite is a curved mechanical form, NOT the blocky red/cyan current artwork. Inventory confirms descriptor049and051historically share identical32x18 arcade source SHAaa3c3263b979406ad8ba48f88f3a7ee0230b6ce63867560266977481859d6b96; squeezing this into24x48 causes severe distortion.52/53/54also share128x48source and need separate identity review. Diagnostic build/graphics/l7_emergence_review/native_current.png compares original and current49/51..54, visually inspected. No assertion of runtime memory corruption from this evidence.
Interactive build/graphics/l7_emergence_converter/index.html defaults original Spectrum51 shape at24x48; shows incorrect current separately and tentative arcade2248/2982capturedobjects as independent alternatives, NOT confirmed pose family. Original source has no new AI artwork. Shared RPCcontrols, source/size/dither/export/browserchecks PASS via verify_l7_emergence_converter_browser.mjs; UI screenshots walker_ui.png/walker_mobile.png. This is asset review only; identity/matching and actual game repair pending. No game changes; r138 retained.


226. L7 wall lens/body and red moving part review (2026-11-12). Photo13158 identifies native41body and42..45redmovingcomponents, each16x32. Captured704(frame61500,p11,32x64)strongly matchescyanlens/housing;692(frame61800,p11,32x64)related mechanical view butfullassembly/pose correspondence remains unconfirmed. Do not map these as interchangeable parts or call five native components a full-enemy animation. candidate_contact.png visually inspected, allnativepieces andmultiplelargearcadeobjects compared.
Interactive build/graphics/l7_wall_converter/index.html: separatelyselectable704/692actualcaptures andcurrent5nativecomponents, sharedRPCsettings, aspect-preserving32x64default/24x48proposal. Nativecomponents for manualinspection; no runtime or collisionchanges. verify_l7_wall_converter_browser.mjs PASS sources,current5parts,size/aspect,fourdithers/legal8x1/autosave/ZIP/mobile/noexceptions. UI screenshots walker_ui.png/walker_mobile.png, identity_comparison.png;ZIPCRC PASS. Asset review only, no installedreplacement or hardware/performanceclaim. Scripts/build_l7_wall_converter.py. r138 retained.


227. L7 selected exports staged, wall assembly correction and walker variant (2026-11-13). Read four user ZIPs as asset selections, not instructions. Exact originals preserved inconvref; stagedcheckedPNGs/bits/attrs/preserve/pairs/choices underbuild/graphics/l7_wall_assembled/selected. selected_manifest.json recordsSHA256,dimensions,settings,nativeIDs. Chosenwalker3x24x24(49/88/78/1.29),native37x24x24(49/75/78/.67),orb35x16x16(49/29/96/1.41),emerging51x24x48(49/79/78/1.05). AllZIPCRC,lengths,normalblack/noFLASH and legalpairflagsPASS.
NativeL7 trace2600updates with protected/game-over bypass:604dispatchrecords,actualmovingIDs42(222samples),43(32),44(32),45(16), body41doesnot appear inmovingactorhook. ScriptF313etccontains42/43/44/45/44/43sequence. Resthold52updates versus2perintermediatepose,26:1ratio. Earlier1800updatehook-onlytracefoundnonebecauseencounterbegins2123; expandedwrite/dispatchtrace corrected sampling. Native traceJSON retained.
CRITICAL priorgalleryerror: decoderexcludesobjectswhollyrightof384; atframe61800arm692x380y88andbody704x412y88both32x64,p11areadjacentparts. Severalothercapturesconfirm+32x, samey. Earlier704/692separate-alternativepreviewwasincomplete. build/graphics/l7_wall_assembled/index.html nowcomparesfull64x64capturedassembly,originalnative41+42..45assembly, andexplicitlylabelledderivedarticulation. Derivedfourposesrotateonecapturedarmaroundjoint; NOTclaimedcapturedarcadeframes. SharedRPCconversionappliedafterassembly,32x32default/24x24proposals. Playbackforward/reversewith26:1holdratio,adjustablepresentationtimeNOThardwareFPS. BrowserPASSactual1/native4/derived4,sizes,fourdithers/legal8x1,autosave,ZIPexport,mobile/noexceptions. assembly_and_walker_comparison.png visuallyinspected; UI diagnosticPNGssaved.
Separateinteractivebuild/graphics/l7_walker_variant/index.html retainsselectedoriginalsettingsandaddsblue/cyanmaterialvariantacross3actualarcadeposes. Originalselectionnotreplacedbyvariant. BrowserchecksPASSoriginal/cool/current,sizes,fourdithers,pairs,autosave,ZIP/mobile. selected_reproduction.json records exactselectedpaircomparison.
UNRELEASEDgameintegrationexperimentbuild/fullgame/l7_choices_r139 FAILEDcoldL7startup(0updates)andcachedL6->L7codeintegrity(DOCK0bytes0/6changed). Initialpackedbank1end3C83exceeded3A00; proposalusingD300..D7CBcachetailpacketfit37D3butfailedactualemulation/source-lifetimeacceptance. NoZIP;DO_NOT_USE.txtexplicit. Newartnotinstalledinanyreleasedgame. Retainr138. Do notreuseproposedD300allocationwithoutcompletecoldbootstrap/runtimevisibilityaudit. All4selectedexportsretainedandvalidated; integrationremainsunfinished.
Scripts/build_l7_wall_assembled.py,trace_l7_wall_assembly.mjs,build_l7_walker_variant.py andbrowserchecks; experimentbuild_l7_choices_r139.py/verify_l7_choices_r139.mjs. Stable100/priorreleases/referenceprojectsunchanged.

227 additional converter reproduction check: same-settings regenerated walker does NOT reproduce user ZIP byte-exact (PNG pixel differences15/18/19perpose); selected_reproduction.json exact=false. Original ZIP pairs remain staged byte-exact and are the integration source, never regenerated preview. Do not claim repeat conversion exact across browsers. Variant is a new proposal; approved original is shown from actual exported PNGs in comparison.


228. r140 complete six-pack L7 integration (2026-11-13). Supersedes unfinished integration in227; r139 remains a failed historical experiment. Exact inputZIPbytes preserved; chosen_assets_manifest.json records all6ZIP SHA/settings/frame SHA. White14..17 uses3chosenposes0/1/2/1; cyan30..32 usesall3variantposes;35orb16x16;37red/yellow/green24x24;51emerging24x48. Wall chosenarticulated4x32x32 retained in cache; moving42..45drawleft16x32, fixed41housingdrawsright16x32restpose via nativebackground path. Native42/43/44/45/44/43script/timing andoriginalpartfootprints preserved; housingno longer moveswitharm or redrawson eachpose. Stablehousingusesrest-framecolouringratherthan the minor right-half dither difference inonearticulatedframe.
Storage: noD300packet. Failedr139 proposal overwrote initial native level-script storage; also a directCALLtopreload returnedafterF4ED whileSPstillpointedHOMEFFxx, producing invalidPC0. Fixed by invoking combinedpreload only fromexisting warmup/safe5CF0stack, resetting bank7E3F0flag before warmup. PreserveA494loadentry/routinefootprint andA4AElifecycle boundary. Neither dual-use native script pages nor stack mapping may be inferred free from post-init cache usage.
Losslessplanar raw3136bytes andcache4864bytes sharea bounded combined8448byte loadstream startingB200, zero448bytegapBE40..BFFF, thenC000..D2FF. Existing sourcesAEB1..B147 andA998..AB4E holdfirst988/524decodedbytes; remainingpacketstarts2400. Compactin-place cycleinterleave inlinkedinitializationhelper; no addedworkspace, no per-framecodec. Packedend39FB(3A00limit,5bytesspare). Old51four-phasecacheC980..CF80 reused forcyanC980..CB30andwallCB30..CF30;51chosenfixedimage nowBD20..BE40. Metadata updated withactualcombinedB200destinations andretiredcacheallocation, notold51phaseclaims.
Native source/erase masks updated alongside paired art. White17aliases15 becausechosenposeorder repeatsmiddlepose; freedold17sourceholds cyan30,31/32repackedwithintheiroriginalfamily spanCB4E..CC31. Orb35/round37masks updatedinplace. Wall42..45compactmaskstreamCDD9..CEA1fitsoriginal216bytespanendingCEB1. Housing41native72bytesAD91..ADD9 uses8newECMrowkeys98/99/100/101/102/104/105/106; slots provenunused byallremainingnativefamilies, includingterrain49/50/52/53/54. Allnative43etcdescriptorbounds parsed afterrepack. Selectedcompiledpairbytesneverregenerated throughbrowser; allsixexactZIPassets hashchecked.
PASS: independentZ80shuffle3136/4864byte tests434733/974279steps,5211459/11649372Tstates,total16860831(~4.8sat3.528MHz) plusdecompressionduringL7preparation; notgameplayFPS.600protectedfiringupdates with6exactraw/cachechecks;2160-updateprotectedwallrun with21exactchecks, allselectedIDs/4armposesobserved;12cold/cachedtransitionswithnative-source restoration; no-bypassL7coldstartup/fire523updates,3976IRQs(finalgameoverreturnedregion0,notfalseL7regionassertion); post-deathscorecallertransitionprobe;all20TAPchecksums/LEVEL07andSTART07reconstruction; allother7regions/RTCORE byteidenticalr138; nativeD300..D800scriptstorage andD800..D910IM2/helper unchanged. All256L5temporaryvector targets5B5B; actualIRQreturnboundaryprobes0/255, remainingtargetsidentical, fixedFFemulation nothardwareconfirmation. L5BB160updatecoveragepassed.
Actual captures wall_final_comparison.png/final_gameplay_review.png inspected. Persistentbluefield/trailinprotectedtestalsoappearsr138baselineunderidenticalconditions; removingforcedspawn-timerrefreshalone didnoteliminateit. Do NOTclaimnewmaskrepairsolvesthatpre-existing/protected-testartifact. Death-bypassrunsarenotnaturalplaythroughproof. Fixedwallhousing/arm andemergenceart changesvisiblyconfirmed; nohardwaretestclaimed. Otherpriorartandhighscorerepairretained.
Scripts prepare_l7_final_inputs.py ->build_l7_all_choices_r140.py;verify_l7_shuffle_r140.mjs,verify_l7_choices_r140.mjs,verify_native_revisits_r140.mjs,capture_l7_wall_final_r140.mjs,capture_l7_wall_clean_r140.mjs,verify_cold_launcher_r140.mjs,verify_highscore_r140.mjs,verify_all_vectors_r140.mjs,verify_l7_static_r140.py,finalize_l7_all_choices_r140.py. DeterministicZIPpackaging repeatedtwicewithidenticalSHA. Candidate build/fullgame/l7_all_choices_r140/RType_TS2068_r140.zip SHA256d1a29adec8bc131bec1417ed07ea0998db98e2af7a4b56e75b0266bb7175e696. Fullrtypefolderreplacement/reset/R140PREPARING. Hardwarepending. Stable100/r99,stock64KBtarget,priorarchives andreferenceprojectsunchanged.


229. r141 L4 boss checkpoint weapon recovery (2026-11-13). Usernotesrearweaponslostafterdeath. Actualnativehit-flagdeath confirmsForcepower/dockstatecleared onrespawn. Existingr136/r137twoBBpickups areone-shotshortcutprovision, insufficientforlaterlives. Realfirstrespawn returnscolumn73with7A8E=0; stopped-screen gatealone missesrequiredreturnapproach.
FinalpolicyisL4-onlyexistingbank0inputhook: atcolumn>=73, Forcepower7ABE<2 andbothpickuptypes7AC1/7AC5zero, spawntwoordinarytype2collectibles atcells(12,10)/(14,10), nearthe normal(8,10)spawn. Do notoverwriteexistingpickups orgrantanyequipment. Remainsavailableonrepeateddeaths/missedpickupsuntilupgraded; ordinaryearlierL4scrollingunchanged. BBstillspawnsitsoriginaltwocollectibles. 55-bytehelperfitsreserved01C8..01FF;1FA3originalLD BC7FFE becomesCALLmain_input,whichpreservesHLandsetsBC7FFEbeforeoriginalkeyboardIN. Noaddedallocation,I/OorcommonRAMrespawnpatch. OnlyL4bank0helper/input bytesplusversionlabeldifferfromr140. All6L7choices/other7regions/RTCORE/IM2unchanged.
REJECTEDprototypepatchedHOME8BD5andinstalledfromL4initializer0CF3; cachedL4->otherlevelassertionprovedsharedRAMhookleaked. Fullywithdrawn,final8BD5remainsnative32987Aandall12transitionassertionschecknormalopcode. A1485initializercallassumptionwasstale(currentCALL0DC0gateway), correctedthroughactualbytesbeforeprototype; finaldoesnotpatchinitializers.
PASSpolicyunitcases: ordinaryscrollcol72,nospawn;alreadyupgraded,nospawn;existingpickup,nospawn;missingForcecol73,spawn;power1,spawn; repeatedcallsdonotduplicates/overwrite;HL/BCandForcepowerpreserved. Nativepickupanimationmayadvancephaseto1beforeframe-end; exacttype/positionassertionsallowthatnormalanimation.
Actualrecoveryprobe firstcollectsBBpickupsanddocksrear,thenrestoresnative91F2deathentry(removesinitialapproachprotection)andsetsrealpixelhitflag5BC4. TwoREALnative death->respawn->pickup->rear-dock->rear-firecyclesPASS: deathframes5/8,respawn245/240,refill246/241; eachresetForcepower0beforecollection; requirednormalcollection,dockingandactualnativebeamdirections1/3/5. Priorfullyheldfireprobeandshortpulseprobe missedbeams; charge/release120on/60offmatchednativefiringandverifiedrearfire. Do notcreditearlierfailedrear-beamtestsaspassing. Initialapproach/BBsetupwasprotected; actualtwo death/recoverycycleswereunbypassednativeflow, notentireunmodifiedplaythrough.
OtherPASS:12cold/cachedtransitionsincludingL4revisit/nohookleak; unmodifiedcoldL4startup/fire340updates/4218IRQs; exactL4mutationranges,other7regions/COREidentity,allTAPchecksumandLEVEL04/START04reconstruction,ZIPCRC. Previousr140L5all256vectortargetproofretainedbyexactunchangedL5/COREidentity;no newIRQ/hardwareclaim. Hardwarepending.
Scripts/build_respawn_pickups_r141.py,verify_pickup_policy_r141.mjs,verify_respawn_recovery_r141.mjs,verify_native_revisits_r141.mjs,verify_cold_launcher_r141.mjs,finalize_respawn_pickups_r141.py. Candidatebuild/fullgame/respawn_pickups_r141/RType_TS2068_r141.zip SHA256b5fae1c47d52a60b5f175a660a797418ea25abeaf75294a97d3fbaa3ba2f68bd. Fullrtypefolderreplacement/reset/R141PREPARING. Allr140artretained; priorarchives/stable100/stock64KB/referenceprojectsunchanged.
Lesson: boss-targetaccessauditsmustincludeactualdeath/respawn, equipmentloss, obtainablereplacementsandrealrear-fire recovery, notjustaBB-equippedentrance. Otherbosscheckpointrequirementsremainpartoffuturelevelreviews; thisrepairtargetsconfirmedL4rear-targetneed.


230. r142 L4 boss health halved (2026-11-13). Only native health sources EF5A/EF61/EF68 (region CF5A/CF61/CF68) changed32->16 relative to r141; all other region bytes, other7levels and CORE identical. Scripted settled encounter: normal pickup/docking/input, firing starts after200boss updates;16 native one-point hits per target,48total, native F59D victory at encounter590. Player protection only; no enemy HP/timer edits during test. Two real native death/respawn/recollect/rear-dock/rear-fire cycles PASS. All20TAP checksums and LEVEL04/START04 reconstruction, ZIP CRC PASS. Diagnostic trace_l4_health_init.mjs intentionally stopped at201 to locate32HP source writes; its failed defeat result is not credited as a passing test and may replace loose r141 diagnostic JSON; archived r141 ZIP unchanged. No new interrupt or hardware claim; unchanged L5/CORE preserves earlier reservations/proofs. Hardwarepending. build/fullgame/l4_health_r142/RType_TS2068_r142.zip SHA256b7618e84827c9bb63dfeb1c9f45551ca2120f1730646d4cfef60ef158b63add2. Scripts build_l4_health_r142.py,probe_l4_settled_force_r142.mjs,verify_respawn_recovery_r142.mjs,finalize_l4_health_r142.py. Stable100/stock64KB/referenceprojects/priorarchivesunchanged.


231. r143 score color restoration. r138 repair forced white attributes; replace existing17byte19D2 helper fill with native76CB palette initialization, retaining CALL1466 standard-mode restoration and JP7690. Original alternating white/color rows and seven-color phase preserved; no new allocation. L4/L7 cold20updates then real92EF score caller PASS mode0/map09/shadow0, colored+white attrs; direct76CB call advances colors. Not natural full death/name-entry or hardware proof. Initial test incorrectly entered76CE(mid-instruction), rejected/corrected using original snapshot signature76CB. Initial strict modulo64 layout assertion did not match native INC L row pattern; corrected to native color/coexistence/phase assertions, no runtime changes for assertion. Only19D2..19E2 differs in all8regions; CORE unchanged.20TAP checksums,allLEVEL/START reconstruction,ZIPCRC PASS. Stable100/stock64KB/priorarchives unchanged. build\fullgame\score_colour_r143\RType_TS2068_r143.zip SHA2566ca7533e7acbb95bb56c9b8842bc58f103c762a1182a9a4b6d6bebd85bde8a09 Hardwarepending.


232. r144 clean silent L7 preparation. User reports long delay/residual sound/garbage on L7 start and transitions. Both00D4 cold and0DC0 runtime JPDEDB now routeDF50wrapper; maps unchanged49, executes fromDOCK6, HOMEdisplay remains visible.163bytesDF50..DFF2 audited free beyond generic cache helper DSDF50 and livevarsDF30..DF44; does not reuse D300scripts,D800IM2,nor packedbank1. DI, beeper0, AYvol8/9/10=0, standardFFmode/shadow0, clearHOME4000..57FF and normal5800attrs; small7pxPREPARINGLEVEL bitmappublished then JPDEDB original warmup. Originalwarmup safe5CF0stack andcodec/planarart unchanged. No extra gameplay/frame cost. Cold preparation293displayframes stablebitmap+zeroAYuntilwarmupreturn then30realgameupdates PASS. Coldfire526updates3909IRQs PASS.12cachedroutes and4L7preparationinvocationsstable/silent PASS; initial exactly2invocation expectation rejected because native initialization usesadditionalpasses, assertion now coversall. Diagnostic preparing_screen.png rendered and inspected: cleanblack, smallwhitecenteredtext. OnlyL7gatewaytargets and163wrapperbytes plusversionlabels differ; other7regions/CORE exactidentity,all20TAPchecksum/reconstruction/ZIPCRC PASS. No hardwareconfirmation; no change to other levels presentation. Scripts build_preparing_r144.py,verify_preparation_r144.mjs,verify_cold_launcher_r144.mjs,verify_native_revisits_r144.mjs,finalize_preparing_r144.py. build\fullgame\preparing_r144\RType_TS2068_r144.zip SHA256cdd1f75ac85d31ec724c22dd12b285dc98054799a8db92e0542a1d59f89dd5bd Stable100/stock64KB/priorarchives/referenceprojectsunchanged.


233. L1 intermittent projectile pass-through investigation (2026-11-13), r144 unchanged. User identifies red flyers plus walkers, so enlarged32px walker/ghost versus original24px collision footprint is not sufficient explanation. scripts/trace_l1_hits_r144.mjs,trace_l1_actors_r144.mjs,trace_l1_damage_r144.mjs: protected stationary-player firing through1305native updates,120queued contacts,112accepted actor-signature comparisons,0stale rejections,112nativeA551resolver entries,79nativeA57Ddamage-path entries. Those counts do NOT prove all visually intersecting shots detected, nor that all112contacts shoulddamage (nativezero-health/invulnerability handling retained). Interim actor trace overwrites same diagnosticJSON; final build/fullgame/preparing_r144/l1_hit_trace.json records damage trace. No fix/release or hardware claim. Need targeted visual/contact-map reproduction before altering geometry or projectile logic.


234. r145 displayed-frame projectile collision (2026-11-13). User requests artwork-matching collision everywhere intended. Correct earlier incomplete24vs32descriptor inference: compiled renderer supplies enlarged dimensions and visibility plans to native owner publication;1500actualL1draws IDs12/18/19/30-33/41/49-51/53-55 have0nonemptycells missing ownership immediately after draw. Native descriptors alone do not establish compiled collision footprint. Timing trace1305updates found91projectile queries with workingowner<80but retained displayedowner81..F9; no stale-signature rejects. IRQ bolts were querying future working7E00grid while visible frame still had actor atpreviousposition.
Minimal final fix retains original640byte clock instructions except3lookupCALLtargets, adds23byte visible_owner at5B00..5B16: originalC0E4computesDE, add7A80toaddress retainedF880+cell, map8Dread, restore0D, returnowner; BC/HLpreserved, DEscratch asnative. Reuseexistingplayerretainedmap; no frame scans, no mask/rectangleinflation; native charged/missile/main-loopdamage rules unchanged. Both cold/runtime COREcopycounts640->663 (only2changedbytes atconcatenated152E/1DF5). SourceF100..F396 grows23bytes intoobsoleteL5flippedcacheprefix. Currentmotion/cacheimages andnativecompositorhave no LD DE/HL,F380base reference; actualcold/boss160update13componenttrace has0non-block graphicsreads ofretiredprefix. Testfixturebridges5E04/7B04 explicitlyinspect bankcopies, Z80blockcopyCPU.pc maypointpastEDB0; audit excludes those knowncopies, not general reads. AllL5IM2/UI reservations unchanged, runtimeend5B17 safely below5B5Bvector and5B60privateworkspace.
Rejectedcompact prototypes failed size, and an automaticJP->JR trial broke fixed3byte dispatch entries; never released, final original jump table and all clock body behavior retained. Early isolated tests carriedrunning CPU/bankstate and misdispatch artifacts fromrejectedprototype; final directprivate-stack unitcases use explicitmode2 and unchanged dispatch. Negativecontrols: oldclock misses retainedenemy andhits futureenemy; finalreversesboth. ActualnativeHP3->2 onshownenemy; future/empty/reusedactor no damage, terrainqueuednormally. RealL1protectedfiring1287updates154queued/146resolver/85damage-pathentries,0stale rejects; baselinecounts are notsame-gameplaytrajectory orproofeveryintersectingpixelhits.
PASS14transitions coverall8levels includingcoldL5/L8, cachedL7preparationstable/silent; coldunmodifiedL1fire488updates3655IRQs/L5fire424updates4372IRQs. L4settlednormalpickup/reardock pilot16hits each/nativevictory encounter575, playerprotected,noenemyHP/timeredits. L5BBboss160updates13components,256vectorentriesidentical5B5B, actualreturnprobes0/255/fixedFFemulation; nohardwareclaim. Olderall-bossmotionharnesshit establishedC7F0preloadstack, knownL2selfmods and locked-axisL2snakes; corrected allowances/skip but finalvector/bossclaim scopedL5, notallbossdefeats. All20TAPchecksum/allLEVELSTARTreconstruction/staticmutation/ZIPCRC PASS. Activeart/descriptors/bossopenings/armor/pickupbehavior unchanged; stable100/stock64KB/priorarchives/referencesunchanged. build\fullgame\visible_hits_r145\RType_TS2068_r145.zip SHA256bb0c9311569bbb3c688de3fa2cc36816f69b0a2397275c7228d55a45799eefcf Hardwarepending. Scripts build_visible_hits_r145.py,verify_visible_collision_r145.mjs,trace_owner_coverage_r144.mjs,trace_l1_collision_timing_r144.mjs,trace_l1_damage_r145.mjs,verify_native_revisits_r145.mjs,verify_cold_launcher_r145.mjs,verify_all_vectors_r145.mjs,probe_l4_settled_force_r145.mjs,finalize_visible_hits_r145.py.


235. Individualcartridgeport begun, NOT COMPLETE (2026-11-13). Located all8foundation/levelNN.dck, eachheader[0,2,2,2,2,2,2,2,2]; contrastnewerECMpreviews[0,2,3,3,3,2,2,2,2]. Usercorrecttherewereall-levelread-onlycartridgefoundations; thoseareoriginalnativegraphics, notcurrentECMruntime. scripts/verify_cartridge_references_r146.mjs runscopiesfromreset, nativekeyboardPstart/restarts,150actualgameupdates/no deathbypass,0postentrymappedROMwriteattempts,allbanksimmutable/noDOCKRAM. Each8192firmwareRAMprobewritesbeforeentry ignored/countseparately. InitialsinglePpulseL8lostlivesbefore150updates; rejectedascompleteproof, periodicnormalrestartsfinalall8PASS. No physicalhardwaretest. scripts/build_cartridge_inputs_r146.py packs6r145regionpages0/1/4/5/6/7plus22528sharedcorebytes inexistingZ80LZformat, everyinputroundtrip. Totals55180/56192/51133/53587/51226/51280/54151/47691bytes forL1..8, excludingbootstrap/stockruntimeadapters. build/cartridges/r146_work/manifest.json marksall8updated_stock_rom_ready=false. Generatedpackedinputs/native-referenceDCKcopiesareNOTnewECMPicoROMoutputs. Oldreadonly/stable100/r145/sourceZIPs/referencesunchanged. Stock48KBlayout/currentmutablebank2/3/5/6/7adapterstillrequired. docs/individual_cartridges_r146_work.txt recordsremainingimplementation. No updatedcartridgebuildorreleaseclaimed.


236. r147 stock-ROM artwork/cache integration trial (2026-11-13), incomplete all-level release. Read project/test state before changes. Only new scripts and build/cartridges/r147_work changed; r145/stable100/r99/old ROMs/reference projects preserved. First integrated four chosen L1 shell32 poses176-179 into actual r24 read-only ROM. Native32x32 descriptor footprints,25 deduplicated8-line palettes, header-pointer resolver;16 direct then32 direct/retained component comparisons PASS. Flip comparison exposed inherited r24 ROM FD01=00 in otherwise correct bit-reversal table; boot copied it to HOME5D01, dropping mirrored single-bit detail. Canonical table changes that byte to80. Initial hardcoded joystick offsets failed signature assertion; final signature-anchored patches use physical raw bit7 and mask8F. Initial background mask offset assumption rejected; located exact instruction inside known function. Shell prototype superseded by generic cache trial; not a current release.

Current r145 L1 actual selector is CALL target at HOME9172 (1B14), not original8E85. Capture actual selector and native painter for nativeIDs1-70,4phase values,4flip requests; undo geometric flip while preserving deliberate source-pose changes. Native unused zero descriptors explicitly skipped after initial ID10 assertion. 1120 requested variants,70 deduplicated frames,307 unique8-line palette rows. Chosen shell30 capture exactly equals approved asset176. This is rendered actor extraction; custom terrain overlays and other gameplay code are not automatically captured.

Compressed stock bootstrap: five HOME8KB images use3755/3991/2835/6314/6232 packedbytes before selector-hook change. Reclaim original bitmap C4CE..D7F8, leave descriptors/control/scripts. Z80 LZ executes permanent ROM0, private stacks BE00..BE1F and5A00..5A7F avoid source/destination hiding. Final HOME8000 decode unmaps bootROM4 only from decoder, restores it before return; required OUT-before-CALL and deferred last ROM4 unmapping. Rejected initial attempts entered firmware0000 and wrote mapped9FFF; subsequent prematurely mapped destination8000 and early ROM4 hiding failed. No rejected intermediate published. Final compressed initialization required copied HOME bytes PASS; initial all48KB zero expectation rejected because HOME6000..77FF is untouched firmware scratch, and58FD..5900 are documented register-restoration slots. Final assertion explicitly excludes those, not general RAM differences. All required copied bytes exact,0post-entry ROMwrites. Music grammar relocated to ROM3 through existing byte-reader hook; permanentROM1 3A88..3FFF freed for new kernel.

Generic L1 trial: ROM0 LZ decoder,467byte permanent kernel inROM1, directory/variant arraysROM6, compressed framesROM2/3/4/5/7. ROM6 cannot source compressed frames while destination/private stack are HOME Cxxx; used only for safe byte-read directory. Palette poolROM5; complete8-line rows restored from temporary reads. Local frame tags reserve native empty54; initial54-row limit failed on56-row boss, fixed with reserved hole. Initial packet allocation overflow/fragmentation rejected; directories movedROM6 and large-first frame packing passes all bank bounds. HOME C4CE phase bytes, C5CE context/private C63C stack, C63E frame cache; max1497bytes endsCC17, safely beforeD7F9 descriptor boundary. Last-frame sentinel/index avoids repeat decode. Temporary banking/decode saves caller IFF; renderer palette read also masks/restores interrupts. Physical joystick fire mask/bit corrected; keyboard+joystick architecture retained. Retained palette IDs use markerbit5 plus highindexbit2; dirty/scroll paths preserveE4 and replacement clears1B. No mutable DOCK memory.

PASS scripts/verify_stock_actor_cache_r147.mjs:1760 actual native selector/painter comparisons covering all nonempty IDs/phases/flips, direct and retained publication, exact visible colours and nonblack brightness,0ROMwrites/immutable banks. PASS verify_stock_actor_gameplay_r147.mjs: reset->600 native game updates,5583 emulator frames,4normal keyboard starts/restarts, no death bypass,0post-entry ROMwrites;8192 firmware probe writes before entry counted separately. This is sustained component gameplay, NOT complete level/boss defeat or hardware proof. Timing not a claimed speedup benchmark. verify_stock_compressed_boot_r147.mjs tests pre-cache intermediate initialization only. Final trial ROM/BIN65536bytes, DCK65545bytes flags[0,2,2,2,2,2,2,2,2], trial ZIP CRC/identity verified.

Current actor art/cache renderer present, but latest terrain/palette scrolling adapters, latest1pixel/projectile clock, title/audio/native compatibility parity and remaining7levels NOT complete. No updated all-level cartridge release claimed. build/cartridges/r147_work/README.txt and trial_manifest.json state limitations explicitly. RType_L1_stock_actor_trial_r147.zip is experimental only. Latest playable expanded r145 remains unchanged.


237. Complete-integration release hold (2026-11-13). User explicitly requires all work integrated before any further release. No new ZIP/BIN distribution or latest-release pointer change this turn. build/cartridges/integration_work/integration_status.json records all8 levels against r145 source hashes, with terrain/composite bosses/current player/projectile/input/title/audio/weakpoints/cartridge flow/runtime/death-restart parity still pending. scripts/check_stock_cartridge_release.py rejects partial matrices, missing/stale evidence, missing output hashes, non65536 ROM, ROM/BIN differences or writable-bank DCKs. Negative invocation on current incomplete matrix returns1/publish_ready=false as intended; not a failed gameplay test. This gate is for the new cartridge path; stable r100 entry point remains unchanged.

scripts/extract_stock_all_levels.mjs extends actual current renderer capture across8 native layouts. Initial L2 capture erroneously had no separate actor metadata (walker_runtime excludes L2); detected phase repetition, loaded L2_actor_extension.sym separately. L2 scorpions now10 distinct chosen poses each, three-phase19/20 and four-phase34..38 captured. Scratch clearing now preserves level identifier. Earlier suspicion that clearing that identifier alone explained missing animations was insufficient: the separate phase metadata was the confirmed cause. Snake preceding-actor test initially startedIY-13, missing actualIY-4 firststatus; corrected starti0 reproduces native9-segment classification and separates native22/23 body appearances. L8 native frame32 height21 initially rejected20row viewport bound; diagnostic-only four native CP20 clipping checks extendedto24 to capture complete source height. First assumption allfour bounds useJP NC failed(oneJP/threeJR NC); exact4 opcode-anchored replacements now verified. Gameplay clipping code is unchanged. Every capture artifact is internal and not a proof of all composite boss/terrain coverage.

scripts/build_stock_level_base.py preserves each level's native payload/descriptors/map and selects corresponding music grammar, compressing into stock ROM layout. scripts/build_stock_level_actor_cache.py implements per-levelactor ROM cache with safe no-stack-while-mapped directory byte reads, including ROM6/ROM7. Original read_byte stack push would be hidden by ROM7; new helper savesBC before mapping and pops after restoring. L1 first allocation failed because frame-compatible ROM space was occupied by directories whileROM6free; preferROM6 for directories, leaving decompression sources outside HOME Cxxx bank. L2 adapter ports actual snake role chooser and period3/4/10 phase counters instead of naive16phase cycle. No packed-frame cache exceeds native descriptor boundary. No new hardware claim.

PASS internal perlevel component comparisons: L1 1760,L2 4992,L3 3264,L4 2624,L5 1184,L6 960,L7 1440,L8 1408 =17632 total. Actual native selector/painter/direct+retained rows, requested phase/flip variants, visible colour and nonblack brightness, immutable ROM,0post-entryROMwrite attempts. scripts/verify_stock_level_actor_cache.mjs includes diagnostic source-height rendering forL8; does not alter in-game clip behavior. PASS reset->150 native updates for each8 internalbuilds, normal keyboard starts/restarts, no death bypass,0post-entryROMwrites;8192 firmware RAM-probe writes each before entry counted separately. Frames2075/3641/2055/2672/2025/2085/2417/1710, starts2/4/1/3/1/2/3/1. These are actor-cache integration checks, NOT current whole-game code parity, complete levels or boss victories.

Terrain extraction first direct-painter probe produced only black palette rows; REJECTED and explicitly marked integration_eligible=false in L2_terrain_frames.json. Current terrain palette publication/dynamic L2 tile expansion and composite-body reveal must be ported via their real paths; do not accept a pixel-only/manual painter preview as terrain integration. scripts/extract_stock_terrain.mjs remains diagnostic-only. No release produced; r145/r100/previous archives/reference projects untouched. Current work continues to require terrain/current1pixel+projectiles/nativecontrols/title/audio/boss+collision parity before packaging.


238. Internal stock cartridge player/projectile lifecycle integration (2026-11-13). Still NOT a release: all eight full integration requirements remain gated. Current ROM/DCK files stay under build/cartridges/integration_work; no ZIP/latest pointer changes. Original r99/r100/r145 archives and reference projects unchanged.

All eight builders now link the current player and independent projectile engines into permanent ROM, with per-level HOME RAM allocation, shared current actor/common glyph cache, compressed full frames and nonrecursive sparse overwrite deltas. Every frame packet is round-tripped and delta offsets checked against its actual target. Initial phases are read from permanent ROM1 so the bootstrap stack stays visible. Reclaimed obsolete loading-screen/compiled-cell bytes reduce the initial 8KB packet to447bytes. Native projectile slots5E00..5FFF remain reserved. Fixed finalizer constants now reflect the actual cleared HOME bytes. Native selector/palette/restore routines mask the periodic interrupt source before LD A,I sampling.

Found/fixed: old relocation manifest had treated indexed CB bit instructions at HOME9152 andC1E5 as addresses; restore their exact native instructions. Old orb callback wrote retired native graphics and is disabled in favor of the new cache. An initially over-broad ROM reclamation overwrote active SFX directory0480 and effects04C2..08C0; rejected after native failure, all those bytes now preserved. Retained player backend now reads clean compact source attributes and merges current ship attributes during the actual native screen copy, without contaminating background tokens. L7 context is onC4 rather thanC5: hardcoded palette scratch page caused the retained-colour comparison to fail; derived page test fixes it. Bootstrap phase-source draft in ROM7 hid the FFFF stack, caught by ROM-write guard; permanentROM1 placement fixes it. Hook signature checks initially compared hex-string character length and expected IX instead of actual HL for native9DA5; corrected against original bytes before linking.

Native hooks:94F6 sync,9560 coarse movement bypass,9563 collision,BE2D IRQ callback,8979/8AFE/C290 screen copies. PermanentROM0 lifecycle gateway initializes private state/phases, polls native selected controls, calls current player tick, independently clocks normal bolts, and brackets native8842 copies with prepare/cleanup. Current normal-shot hit consumption replaces native9DA5 and hands damage to nativeA490 only in the main loop; relocated B7E1/B7E2 coordinates preserved. Player restore calls permanent projectile dispatcher directly, retaining native9501 code. L4 health sourcesEF5A/EF61/EF68 are16 as requested, replacing32; boss victory/recovery not yet revalidated on the cartridge target.

PASS final internal run scripts/validate_stock_integration.py: all8 exact64KB ROM/all-ROM DCK builds,23392 native direct/retained actor+common comparisons (L1 2480,L2 5712,L3 3984,L4 3344,L5 1904,L6 1680,L7 2160,L8 2128), current fine tap/held player movement, native8842 retained ship publication and clean working-buffer restoration, ordered independent projectile component positions9..16, retained-owner collision despite empty future map. All8 reset-to150 genuine native world updates with ordinary keyboard starts/restarts, no death bypass and0post-entryROM writes. IRQ/tick/copy/sync/shot-clock/hit-drain calls explicitly counted so input polls cannot masquerade as world updates. All256 computed HOME8400 vector targets per cartridge resolve8383 and actually return (2048 probes total): fixed-FF emulator with explicit computed-target injection, NOT measured hardware vectors. Current_component_run.json binds every evidence file and ROM SHA. Logs and per-level summaries retained. No images generated this step and no hardware/FPS/full-boss claim.

Remaining release blockers: current terrain art/scrolling palettes and instance group rules, composite boss code/art and all weakpoint/recovery paths, current title animation/audio/input/menu parity, cartridge completion/loading flow, and longer full-game/death/boss validation. Common capture uses canonical L1 shared frames; level-dependent common palette coverage is not established. Current RAM tail allocations and basic lifecycle tests do not prove complete-level lifetime safety. Existing direct terrain probe remains rejected. New real L2 getter01D8 probe returns C700 and ordinary header86, but manual background painter still yields unpublished/black raster attributes; L2_terrain_getter_probe.json explicitly integration_eligible=false. Need capture actual retained publication or decode current token/group conventions, not accept that preview. Full release matrix remains false deliberately.

239. Internal all-eight stock integration continued (2026-11-13); NO new release/ZIP/latest pointer. Current source remains r145, stock outputs remain internal. Exact current ordinary terrain getters captured for all8 levels (22/34/14/15/5/23/37/16 native32x32 tiles), current FBD0 palettes retained, compact instance group tables generated over unchanged native maps/dimensions. Initial direct black-palette probes remain rejected. All8 ordinary terrain direct/retained/four-flip tests passed in earlier complete component runs. Startup regression during linking traced to overwriting live ROM0 F20 in padding around terrain lookup F80; linker now replaces only the opcode-anchored F80 lookup body and preserves F20. This was a real implementation error, fixed before release.

Current selected title delta animation restored by generating the exact5376byte phase atlas from the final3072byte logo into borrowed HOME C700..DBFF. Permanent ROM1 title/restore gateways restore the packed original C000..DFFF level image before gameplay and reinitialize player phases/state. Exact atlas,116actual animation-helper updates, final logo bitmap/attrs and native image restoration tests added. Native world updates assert borrowed-title flag cleared. No second stored atlas needed.

Added native-selected-keyboard/native-both-stick fire tests, P/Shift-P pause with exact overlay restoration and AY8..10 mute/restore (R14/R15 preserved), M edge toggle, double-B native boss setup and ordinary collectible pickups, L4 respawn pickup helper and faster Force follower patches. Completion now uses normal small text, normal black space, no next-tape request, and joystick-fire soft reboot/replay of the same cartridge. Actual completion bitmap/attrs/mute/replay tested. Source modules stock_controls.asm, stock_completion.asm and stock_title_lifetime.asm. Old stock helper1FA3 is live through1FAA; installer uses verified free1FF8 instead. Original SFX0480..08C0 preserved (matches current effect data).

L2 composite body: captured52native terrain tiles with actual stopped flag in DOCK3, expanded current rich palette and18body placements, appended18rich4x4 cache frames without any new palette rows (all already shared). Moving silhouette uses the same geometry with a legal scrolling palette; stopped body uses current chosen rich ECM. First capture accidentally wrote HOME rather than mapped DOCK3 stopped flag; rejected and repeated. One component mismatch came from missing BE00=2 in test fixture; fixed fixture. Native copy tickets must be1 rather than terrainDC or empty0: ticket1 forces publication and is cleared after native8842. New selective repair preserves foreground actors, only repairs owner-empty damaged/terrain cells, and clears its own dirty tickets after copying;320bytes explicitly inside verified free HOME segment, cleared on every player reset/replay. Compact row page computation initially ORed7E rather than adding it (rows16+ wrong); exact erase/repair pixel comparison caught it and addition fixed. PASS18moving getter cases,18stopped tiles,17920visible pixel comparisons, erased bitmap/attribute repair, actor preservation and idle skipping; zero ROM writes. Star hooks preserve existing dirty guards and conservatively exclude stopped-body x64..255. No hardware claim.

Added live boss stress test using actual native double-B initializer and ordinary firing, refreshing invulnerability only for encounter coverage (NOT victory/full-game evidence). First L2 full-body repair took3600frames for165updates and failed the240update time bound, motivating selective repair; later bounded runs complete240updates without ROM writes. L5 also completes240updates without lockup. Do not infer a measured real-hardware frame rate or full renderer parity from this. Final all-eight suite is being rerun and its hash-bound summaries remain the authoritative current results.

Added actual native one-pixel terrain scroll test: full1435/8721/8BAE initialization,256px fill then64consecutive updates covering8phases,2129920bitmap+2129920visible-colour comparisons per level over interiorx16..223. First fixture called only1435 and produced misleading colour failures; full native scene initializer fixes this without changing game code. L1..L6 passed so far; remaining outcomes recorded in perlevel scroll_validation.json. No diagnostic images generated in this step. Remaining work: full composite boss/code/motion parity, L4 actual victory/death recovery on stock, common effect palette variation, longer score/death coverage and final packaging contracts. Integration matrix remains deliberately false until earned; no playable release claimed.

T239 final update: final all8 component suite PASS after score repair (L4 rerun after withdrawn trial); all8 actual terrain scroll tests PASS,17039360 bitmap comparisons plus17039360visible-colour comparisons. All8 completed240native boss world updates under firing stress without ROM writes; invulnerability refreshed, NOT victories. All8 actual death/respawn paths passed twice after simulated current-player collision flags, with original death entry/no death bypass (16cycles total); not game-over/name-entry coverage. Final ROM SHA and all evidence hashes rechecked and current_component_run.json merged across all8, not just the last targeted L4 rerun. integration_status component_progress refreshed; release requirements deliberately remain held.

Found actual stock score regression:92EF called nativeBC90 without restoring video output, leaving portFF=2 despite MODE=0. Added12byte permanent score gateway at C06 (L2C15), restores MODE/portFF0, calls original nativeBCCB colour routine and nativeBC90 score draw. PASS actual post-death caller plus multicolour/animated palette all8; no natural game-over/name-entry claim. Initial disassembly suspicion that B79C was being overwritten by drawing was not supported: trace found no writes during200boss updates and later only bootstrap/reset restoration; diagnostic progress had mistakenly read719C (standard attributes) rather than relocatedB79C. Do not treat that suspicion as a confirmed memory bug.

L4 defeat pilot remains FAILED: two targets register16native damage hits each, front target registers0before native scripted removal. Native target HP/coordinates were not edited. Tested parent-specific visibility port with1275positive/negative unit cases; it then FAILED actual collectible pickup/docking integration. Withdrawn from builders and final ROMs; stock_l4_weakpoint_visibility.asm and its unit test remain unlinked experiment only. Final L4 retains previous native occupancy gate and passes standard suite again. No victory/recovery claim for stock, and no package published. Per-level common capture audit2..8 showed lost palettes/empty art in some source lifetimes (L2allzero); marked explicitly integration_eligible=false, not fed to builders. Canonical L1 shared frames still used; full perlevel common palette parity remains open. Remaining blockers are substantive integration work, not a request for permission: composite/boss movement/context parity, verified L4 target defeat/recovery, reliable perlevel common effect capture and final full release acceptance.

240. Finishing stock cartridge integration (2026-11-13, in progress). No package promoted at this point. Corrected shared-effect capture: traced actual write addresses/mapping and found the legacy common painter writes its ECM colors to HOME, while the compiled actor path uses banked output. Empty L2/L3/L5/L8 common captures were a diagnostic-plane error, not missing game art. New extract_stock_common_direct.mjs captures direct bitmap plus HOME6000 colors with scene ownership cleared, all8 now90frames/87,89,87,89,86,89,87,86palette rows. extract_stock_written_levels.mjs captures actual bitmap/color write values across both render paths; selected artwork keeps original current sizes, including diagnostic-only extended clip for the L8 source height. Builders now use perlevel corrected shared effects and write-captured actors. Prior rejected common captures remain rejected, not silently reused.

L4 actual defeat PASS with unchanged native occupancy gate:48registered native A57D decrements,16per target, actualF59D victory observed. Earlier front-target failure was a pilot aim error: front opening's visible pixels require playerY near targetY*8-3, rather than targetY*8+1. No enemyHP/target-position edits. Native death entry bypassed only for the automated target pilot, separately covered by actual death tests. Withdrawn visibility trial remains unlinked. It also ignored mutable8EDA, which the native pickup/weapon painter toggles RET/NOP to enable collision collection; future attempts must preserve this protocol, not replace it with an unconditional return.

Found/fixed real pickup timing issue: fine player metadata was sometimes restored only on a later IRQ after native screen copy, allowing native world pickup checks to run with no player ownership. stock_live_player sync now calls the current fast_mark_owners synchronously after fine-position sync. It stamps owner3 only on empty cells and does not overwrite terrain/enemy ownership. PASS two L4 real death/respawn/equipment-loss/replacement pickup cycles, native collection/rear docking/rear firing. Actual death entry restored for each death; automated recollection/fire pilot uses protection, not a survival-difficulty claim. Cold normal gameplay/death tests remain separate and without death bypass.

Corrected artwork initially exceeded available L2 ROM packet windows. No frames removed: L2's52repeated64byte phase rows become24unique rows plus52indices (1740bytes saved); all common normalized flip entries proved identical and are stored once per ID rather than four times (333bytes saved). Sparse delta packets may use ROM6 through the existing bank-safe byte reader; full LZ bases remain excluded from ROM6 because it hides cache/private stack. Exact5712L2 direct/retained component comparisons including these packets PASS/noROMwrites. Frame packets remain bounded, one full base plus nonrecursive deltas, each round-tripped before linking.

Normal-black policy enforced in ECM palettes when either color is black; empty-cell restore now uses normal black, and mirrored native HUD clears BRIGHT. Original standard-video animated high-score colors remain bright and unchanged. This addresses the user's video-output requirement without treating the emulator's identical black/bright-black rendering as sufficient evidence. Final full suite is running against this policy.

Game-over test now follows the native five-life initializer86A9, real player death flags and joystick-fire game-over prompt, with a seeded qualifying score solely to enter the real score/name path. Earlier failures omitted the life initializer (zero underflowed to255) or left the native prompt unactivated; these were fixture errors, not game patches. Initial all8 full game-over tests passed five actual deaths/four respawns/real92F2score entry/standard video,0ROMwrites; name typing not automated. Final rebuilt binaries are being rechecked. Boss stress now explicitly documents death-entry bypass for encounter coverage and counts only active native updates; accepts normal native completion after100updates rather than falsely failing if a boss/level ends before240. All capture/test images and final packaging acceptance still to follow; no hardware claim.


T240 COMPLETE: separate r148 stock cartridge release generated at build/cartridges/r148/RType_TS2068_64K_cartridges_r148.zip, SHA256 f0a0e6573317a3147197007678208eac0a8443ecfb741d9412161f4b9d552f77. All8exact65536byte rawROM/BIN pairs and ROM-only DCKs,8acceptance records, checksums and diagnostic snapshots packaged only after the full96-requirement gate passes. Every archived SHA256 and ZIP CRC verified, ROM/BIN identity and all-ROM descriptors rechecked from ZIP. Source r145, r99/r100 and reference projects unchanged; stable disk latest pointer unchanged. docs/STOCK_CARTRIDGES.md and release_stock_cartridges.py are the separate stock entry point.

Final all8 rebuilds PASS 23392direct/retained actor+common comparisons, all ordinary terrain/four-flip tests,17039360pixel plus17039360colour comparisons over actual one-pixel scrolling, title/control/pause/audio toggle/completion replay,16simulated-hit real death/respawn cycles,40actual native deaths/five-life game-over/qualifying-score paths with joystick prompt activation,2048explicit computed-vector IRQ returns, and cold native firing/gameplay. All game ROM-write counters0. L4 full victory16+16+16 native hits and two actual equipment-loss/recovery/rear-fire cycles pass. Boss stress counts active world updates only; L5 reaches normal native completion after203updates, other levels reach240, no lockup. Stress uses explicit death-entry bypass; natural death/game-over tests do not. Not a measured hardware/FPS claim or all-boss victory claim.

Final data audit found only the last two SFX payload bytes differed from L1 in several source levels; now each cartridge copies and verifies its complete current perlevel0480..08BFSFX payload. All perlevel grammar pairs, sequences, directories and frame bytes match current music data exactly. ECM palette normal-black, empty-cell restoration and native HUD black policy verified; standard score colour animation remains bright. Native boss event cadence/placement retained in stock builds; expanded-memory bank motion caches and level switching are not claimed.

Diagnostic images: build/cartridges/integration_work/boss_contact_sheet.png and level01..08/boss_runtime.screen.png, generated from final emulator memory at active update100, reviewed as static ECM snapshots/flash phase0. Earlier end-of-run L5 snapshot was empty because the native completion screen had already been reached; capture moved to update100. Contactsheet shows selected boss/terrain art and native weapon effects; it is not hardware footage or an animation performance measure. Final archive includes perlevel snapshots. Hardware and name typing remain pending.


241. r148 hardware regression and targeted normal-shot repair (2026-11-13). User reports L4 movement ghosting, variable music, no enemies, unresponsive double-B and missing repeated normal shots despite working missiles. r148 is not recommended as a completed hardware release. Found an omitted gateway handoff: relocated fine-player dispatch sets FLAGS+8 / coordinates FLAGS+9..10, but stock_live_player.asm never consumed that request, unlike the expanded gateway. Restored clearing the request and calling native9D5C after the player tick. Six selected-key short taps against archived r148 produce0spawns/pending1; same test against corrected internal ROM produces6spawns/pending0. All8levels pass the keyboard regression and player/projectile/retained-copy components; L4 additionally passes both physical joystick socket models (6shots each), controls,256vectors,150native updates, and existing L4 target victory pilot (documented death-entry bypass).0gameROMwrites. Added scripts/verify_stock_repeated_fire.mjs to validate_stock_integration.py. These are emulator/component tests, NOT hardware confirmation or a fix for all hardware symptoms.
Live movement diagnostic scripts/reproduce_stock_l4_live.mjs exposed low world-loop cadence; sustained movement/short taps/double-B need stronger end-to-end performance criteria. The first probe incorrectly counted IRQ exits atBE5D; corrected toFD45. Max observed nesting1. Stack-alias hypothesis rejected: actual inherited FD20 trampoline uses native stack, not5BC0/5BCE. Do not cite this rejected hypothesis as a diagnosis. No diagnostic image generated this entry. Targeted L4 test files in build/cartridges/r149_shooting_test; manifest records SHA256 and remaining issues. Archived r148/r99/r100/r145/reference projects unchanged. No full release/latest update.


242. TAP/cartridge gameplay-parity correction (2026-11-13). User requires shared gameplay logic. Read actual archived r145 gateway.bin, which is the current TAP development source used for stock player/projectile engines (stable r100 preserved). Found further adapter drift: stock omitted alternate-IRQ redraw gate and busy/alternate-IRQ fire capture. Restored both decisions in src/stock_live_player.asm, retaining stock bank/compact-buffer adapters and native short-shot handoff. Added verify_stock_irq_schedule.mjs anchored to actual reference busy+phase branch bytes; first test mistakenly included one extra opcode byte in reference slice, corrected range3..21. All8internal ROMs rebuilt: each passes6redraws+6input-only calls over12IRQs,0redraws+12input-only calls whilebusy with retainedshortshot,6short keyboardshots and6perjoysticksocket, existing player/projectile/retained-copy components;0ROMwrites. L4 additionally256IRQvector returns,150native live updates and native boss victory pilot pass (pilot death-entry bypass unchanged/documented). L4 live150updates takes2574emulated frames vs2605before scheduling correction; do not call this a measured hardware speedup. Scripted movement/fire probe maxnestedIRQ1; not full gameplay parity, audio cadence or ghosting proof. No diagnostic images generated.
Created build/cartridges/r150_tap_schedule_test/rt_l4_r150_test.rom/.bin/.dck as targeted test only; SHA256 in test_manifest.json. Preserve r148 and r149test, stable r100/r99/r145/reference projects. No full release/latest changes. docs/STOCK_CARTRIDGES.md now records gameplay parity as a requirement, with renderer/storage adapters separate and remaining end-to-end gaps explicit.


243. Reproduced and repaired no-enemy start and retained-copy ship ghosts (2026-11-13). User confirms both persist in latest test. Ghost diagnostic initially tested normal movement only:0residuals; with actual prepare/10movement updates/native8842copy/cleanup cycles it leaves up to32nonzero bytes outside current footprint. Found src/player_damage.asm old_mask does low-byte-only DE-=65, originally safe atF7xx; stock scratch5C01 requires borrowing into5BC0, but code wrote5CC0 instead, corrupting scratch and omitting old footprint damage. Stock compiler now emits full16bit subtraction preservingHL. Corrected exact reproduction0residuals; enhanced80publications in right/down/left/up across8copycycles0ghostbytes for all8levels. Original TAP source unchanged.
True cold-menu/start probe shows NO8E85enemy calls at100updates, live7A90eventpointer0000, despite loop-advance tests previously passing. Native8696 initializesC4AFcheckpoint fromC4B4; stock title RAM restore subsequently re-expandedC000..DFFF from original zero-header snapshot, erasing it. src/stock_title_lifetime.asm now saves/restores liveC4AE..C4B1 around expansion. With same cold start L4 has26distinct enemy IDs selected at100updates and liveeventpointerE6CF. Strengthened title test calls actual8696 before restore and compares liveheader. Shared gameplay gate now requires actual enemy selectors plus nonzero eventpointer, in addition to150nativeupdates; all8PASS, no death bypass and0gameROMwrites. All8 also pass retainedcopy, repeatedkeyboard/bothjoysticks, scheduling and256vector returns. L4 controls and5native deaths/4respawns/score entry after simulated hits PASS, no death bypass in that test. Fixture initial k-reference error and Python image-render whitespace syntax error corrected; not game bugs.
Diagnostic build/cartridges/integration_work/level04/enemy_probe.screen.bin/.png captured from actual cold menu-start at100updates, rendered/visually inspected: enemies now visible. Snapshot also shows solid colored cells; their general graphics status is not covered by this fix and remains to audit. Static snapshot is not hardware footage/performance. Probe scripts probe_stock_ghosts.mjs/probe_stock_enemies.mjs, required scripts verify_stock_moving_player.mjs and strengthened verify_stock_shared_gameplay.mjs/verify_stock_title.mjs.
Targeted L4 files build/cartridges/r151_ghost_enemy_test/rt_l4_r151_test.rom/.bin/.dck, exact65536raw/ROM-onlyDCK; test_manifest.json binds all8internalSHA256 and summarized evidence. No full release/latest update. r148/r149/r150,r99/r100/r145 archives and references preserved. Hardware validation pending; do not claim all music/control/graphics reports fixed.


244. L1 final walker shooting verification and shared collision audit (2026-11-13). User reports difficult hits on last walker after boss shortcut in previous version; asks verify/fix same class elsewhere. No additional runtime collision edit was required by final reproduced cases; current internal ROM contains T241..243 fixes already. Identified actual walker at native actor85D0, owner98, graphics43/44/47/48. First probe incorrectly used direct initializers without real menu start and captured game0/empty published map; corrected to cold/menu/game3 before invoking stock main-loop boss setup. This avoids declaring an inactive-state fixture issue a game bug. Actual captured active update50 has12visible walker cells (including cell25,16 absent from futuremap): every published cell queues98 and native HP40->39. Both directions of native missile9DFA tested from captured state:40->37 (3damage each). Frozen state tests use real captured actor/maps, not synthetic ownership for this walker.
Selected-key moving stock pilot: normal short taps28spawns/8native damage hits, defeat byupdate49/frame775; held-fire pilot2normal-dispatch entries plus native held/charged path,8damage hits, defeat byupdate60/frame943. Native health sequence40..32 means8->0 lowfiveHP; final actor death-animation bit7set. No enemy-health/armor/timer edits, no native death-entry bypass; player protection refreshed only to keep aiming test alive. Actual TAP r145 reference menu/start and main-loop double-B entry/native joystick pilot likewise reaches8damage hits/zeroHP: normal54updates, held-fire69updates. Trajectories and fire periods differ; these are behavioral defeat comparisons, not cycle/FPS equivalence. Early TAP fixture lacked z import, then assumed stock-style key selection mapping and produced1spawn/nohits; corrected reference uses native joystick. Initial long60/90 held-release pilot missed with0hits; shortened18/36 release cadence succeeds; record this as unsuccessful aiming trajectory, not proof of an engine bug or blanket charged-weapon parity.
All8 pass23392 direct/retained art/phase/flip comparisons with ownership assertion on every nonblack actor cell; common decorative/effect frames remain excluded from required actor ownership (still compared visually). All8 actual normal-shot queue/native resolver cases: displayed enemy HP3->2; future-only/empty/reusedslot no damage; terrain queued but no actor damage.0ROMwrites. This establishes shared ownership/normal-shot damage behavior for these cases; does NOT establish every enemy's armor/weak-point rules, every moving missile intersection, or all-boss reachability. Added required verify_stock_actor_ownership.mjs, verify_stock_visible_collision.mjs, verify_stock_l1_walker_cells.mjs, normal/held verify_stock_l1_walker_pilot.mjs to internal validator. Independent reference verify_tap_l1_walker_pilot.mjs saves only under stock workarea; original TAP/source/archives unchanged.
Diagnostic build/cartridges/integration_work/level01/walker_live.screen.bin/.png from actual active encounter update50; rendered and visually inspected to confirm the small final walker on right, ownership atrows15..17. Static emulator snapshot, not hardware video/performance. JSON walker_live_cells_validation.json, walker_live_pilot.json, walker_charged_pilot.json andtap_walker_* bind case outcomes. Reproducible package_stock_l1_collision_test.py produces build/cartridges/r152_l1_collision_test/rt_l1_r152_test.rom/.bin/.dck, exact64KBread-onlyROM, manifest bindsROM+evidence hashes. Same corrected L1 runtime as previous internal build, new verification/export only. No full release/latest update; r99/r100/r145/r148..151archives/referenceprojects preserved. Hardware confirmation, other visual/audio/performance reports and exhaustive boss/weapon combinations remain pending.


245. L4 corrupt/block colors: live renderer fix (2026-11-13). User reports latest L4 blocky/corrupt and not showing expected upgraded art. Reproduced using exact previously distributed r151 L4 ROM-onlyDCK. Existing isolated frame comparisons did not cover the native global color refresh after compact dictionary publication; T243's observed solid cells should have blocked hardware handoff, rather than being left as a follow-up.
Trace cell10,2: compact dictionary palette ID98 from adjacent cell entered standard5800plane via stock copy_front2294. Native horizontal color interpolation18A7 reads neighboring standard attributes; it interpreted98 as paper-green/red plain attribute. Other high-bit dictionary IDs could be misinterpreted as terrain indices, reading beyond the sixteen-rowFBD0palette into executable data. Raw-attribute-only E00 correction did NOT remove all blocks; dictionary-aware E00/E40 without correcting adjacent standard-cell publication also failed. Both incomplete internal candidates rejected, no test files published. Final: copy_front emits neutral7 in legacy standard cells for dictionary tokens while retaining compact row IDs/flags; global single/bulk refresh detects dictionary cells and resolves their actual8x1pairs through0206. Plain attributes bypass palette-index lookup and use normal-black brightness policy; encoded terrain rows retain native path. Current source art and gameplay rules unchanged.
New source src/stock_legacy_palette.asm and stock_legacy_dictionary.asm, builder uses assembler symbols for single/bulk gateways. Initial160byte reservation failed L2 fragmented-ROM allocation; no art dropped/RAM changed. Split exact84byte main plus24byte predicate fits L2's87byte and46byte gaps. A substring symbol regex initially matched plain_bulk and failed the bulk palette test; changed to anchored bulk symbol, reassembled before final tests. No failed candidate released.
Negative control verify_stock_live_colours.mjs on archivedr151:7spurious uniform nonblack cells in nonactor/sky at actual menu-start update100. Final same-world-update test0cells; actual150nativeupdates/real enemy selections/no death bypass/0ROMwrites. All8rebuilt:38736dictionary single/bulk row/orientation/register cases plus all16encodedterrain rows/plainattributes;23392art/phase/flip ownership comparisons, retained player,80fourdirection ship publications, native singlepixelscroll, repeatedkeyboard/bothjoystick shots,256vectors/level, shown/future/terrain/slotreuse native hit tests PASS. L4 additionally controls, exact title/finalcolors/liveheader, native multicolor animated scores,5actual deaths/4respawns/score after simulated hits PASS. L4boss stress240activeupdates/293copies/877actorcalls in8154emulatorframes, no ROMwrites/lockup; native death-entry bypass/playerprotection only for this stress, not victory/hardware/FPS claim.
Diagnostics actual emulator memory: level04/colour_baseline.screen.bin/.png and colour_fixed.screen.bin/.png, l4_colour_before_after.png atworldupdate100. Boss runtime.screen.bin/.png atbossupdate100. Rendered with scripts/render_stock_diagnostic.py; inspected full/detail regular scene and boss. Detail l4_right_detail.png shows restored rich terrain/enemies without solid cells. These are static snapshots, not hardware footage or proof every stage looks correct. Added required global_colour_validation and L4 live_colour_validation to internal validator.
Reproducible scripts/package_stock_colour_test.py exports build/cartridges/r153_colour_fix_test/rt_l1..8_r153_test.rom/.bin/.dck and ZIP with per-ROM/evidenceSHA256, before/after/boss diagnostics. Exact65536raw ROM/BIN, ROM-only DCK; ZIPCRC verified. New L4 hardware test rt_l4_r153_test.rom. Scoped shared-renderer test only, not full release/latest promotion; stable r100/r99/r145/referenceprojects and earlier test archives unchanged. Hardware and remaining audio/performance/full-game reports remain pending.


246. Actual TAP/cartridge paired runtime audit (2026-11-13). User explicitly requests comparison against TAP. Read project state/test history/current release first. Added compare_tap_cartridge.mjs and paired_runtime_controls.mjs: actual r145 TAP protocol/early level selection/menu start versus packagedr153 ROM-onlyDCK;120nativeupdates perlevel, neutral/playerprotection only, noenemyHP/deathentrybypass. All28full9byteactorrecords,eventpointers,camera captured; sixshortfire taps/movement and shown/future/terrain/slotreuse damage component tests pair exactly all8.0ROMwrites. L8naturalROM-samplingRNG causes divergent spawns; controlling onlyC069 was insufficient. Traced secondaryF122return, fixturecontrols both;120states match, no binary RNG change. Boss traces120states: L3/4/6/7/8match; L1diff4states (enemybullet disappears sooner); L2diff25states (actor0x differs6cells starting96); L5diff65originalstates/eventoffset60. Current TAP12spheres versus original24 stockevents identified and corrected boundednativeeventrange in build_stock_level_base.py; candidateeventpointers nowmatch,39latermotionstates stilldiffer. These are OPEN discrepancies, not fullparity.
L2paletteoverride removed in prepare_stock_terrain.py; candidateFBD0matchesTAP but actualcolors stilldiffer8088/7219/5801terrainpixels atupdates32/64/120. Rootpath audit identifies unported TAPr124/r125screen-rowinks; palette-onlychange insufficient. No falsefix/release. Terraingeometry sampled bothownerFF matchesall8; colorszeroL1/3/4/6/7/8, L5tiny32/0/24differences unresolved. Screenscapturedinside94F1nativeupdate, differentactorpublicationphases: paired_scenes.png visuallyinspected diagnostic, NOTfinishedframe/missingactor proof. Added repeatablesummarize_tap_cartridge.py/summary.json/parity_gate.json (FAIL)/REPORT.md underbuild/cartridges/tap_comparison. Fullreports inputSHA bindTAP/DCK. Emulatedrefresh counts inreport; nothardwareFPS/musictempo parity. Musiccalls==acceptedIRQs, notwalltime guarantee. L2/L5candidates pass12globalcolor/scroll/fire/vector/artownership/visiblecollisionregressions. Initialgitstatuscheck foundnon-git workspace; noGitchangesperformed. No newexport/latestpromotion; r99/r100/r145/r153archives/referenceprojects unchanged. FurtherL2palette/L1L2L5motion and completedframe/hardware acceptance required. Do not callallcartridgesworking basedonearlygameplay pass.


247. L1 cartridge double-B fails from cold gameplay (2026-11-13). Reproduced actual menu/start/live keyboard loop:299boss polls,246activeupdates,0jumps; FD4B remains193 (C1 inherited native code), not a clean latch. Prior direct control test explicitly initializedFD4B=0 and therefore missed real startup. Fix src/stock_controls.asm neutral release handler: retainvalidarmed2, advancepressed1to2, clearcompleted3 AND invalidcoldvalues to0. No RAM allocation/gameplay/art changes. Added verify_stock_live_boss_key.mjs and requiredvalidation gate: coldmenu/joystickstart, physicalkeyboardmatrix Bheld/release/Bheld, actualbossentry notdirectcall, assertnotbeforesecondpress/exactly1jump,50activeupdates/playerprotection only/noenemyHP/no deathbypass. ExportedL1r154 exactDCK: coldlatch193->0->1->2->3,1jump,50updates,1265emulatorframes. No hardwareFPSclaim. All8internalsharedrebuild/controltests pass; initialL7second100refreshpress missed due382refreshgap in mainpoll, longerheldsecondpressworks; inputlatency remainsopen, notfixedbylatchrepair. L1normalwalkermovingpilot8damagehits/deathflag andsixrepeatedkeyboard/bothjoystickshortshotsPASS. No diagnosticimagesgenerated. Reproduciblepackage_stock_boss_key_test.py exportsr154_l1_boss_key_test/rt_l1_r154_test.rom/.bin/.dck andZIP,65536rawROM/ROM-onlyDCK/hash-boundevidence. Exactexportcold-keytestPASS. Otherlevelinternalfixnotexported; T246overallparityFAIL stillapplies. Stable99/100/145/prior153 unchanged, no latestpromotion.


248. L4 stationary small-orb report investigation (2026-11-13), INCOMPLETE. User identifies opening oflevel/r153. Added probe_stock_l4_orbs.mjs usingexactarchivedr153ROM-onlyDCK,actualcoldmenu/joystickstart,340nativeupdates/7483emulatedrefreshes,neutralinput/playerprotection refreshed atnativeworldentry. Capturesafterdraw at865F every20updates plusnative28actorrecords inorb_trace.json. Renderedorb_40/100/200/320.screen.png andvisuallyinspected. Whitehangingringchains moveleftbetweencaptures; separatefixedsmallorbsnotyetpositivelyidentified/reproduced. Actorlife/death/resetmayoccurinthisneutralrun; notsurvival/performance/hardwareacceptance. Askedcolor/position toidentifyreportedobjects. No speculative renderer/gameplaychangeornewcartridgeexport. Diagnosticsunderbuild/cartridges/integration_work/level04. ExistingT246parityblockersunchanged.


249. L4 r153 hanging white/green destructible chains leave unerased pixels (2026-11-13). User clarified openingpassageway/verticalchains andsmallgreenobjects droppedbylauncher. IdentifiednativeFA collision-backedworldobjects, notordinary28actorrecords; earlierT248observationthatwholechainsscroll didnotestablishdestruction. Actualr153update100cells15,6and18,4each35nonblackpixels/nativeownerFA. NativeA4E5andordinaryshortbolt -> projectileclock ->9DA5nativehitresolver bothclearowner0butleave35pixels: reproducednegativecontrol. Rootcause: nativegrow/erasefragmentIDs64..95containintentionalblankcells (includingentireblank72/87); capturecacheencodedthoseas54transparent-skiptokens, preventingnativeblankredrawfromremovingoldworldpixels.
Fixbuild_stock_shared_cache.py L4-only: separateframecopiesforthisfamily, expandonlyskippedblankcellstopalette7/zero8rasters; preservevisibleart/sourcefiles/geometry, otherfamilies unchanged. Nativeblank/partialfragmentnowpaintsblackasintended. Bothnativeeraseandactualshortbolthandoffonbothrealcells35->0pixels/FA->0. Addedverify_stock_l4_orb_erase.mjs, requiredlivecapture+erasercheckininternalvalidator; missing-artnegativecontrolstillfailsr153. ExtendedactorownershipfixturetoprefilloldvisiblepixelsforL4family64..95instead ofstartblank:3344totaldirect/retainedphase/flipcasesPASS, includingopaqueblankoverwrite. FullL4internalregression92.91secondsPASS: color/livecolors/art/ownership/player/IRQ/shortfire/terrain/scroll/title/scores/deathgameover/controls/liveBB/vectors/gameplay/completion; nativevictory/recovery and240updatebossstressseparatescopesaspreviouslydocumented. Notfull-game/hardware/FPS acceptance.
Diagnosticsorb_40/100/200/320.screen.png, completedTAP100andorb_erased.screen.png rendered/visuallyinspected. Newcompareharnesscapturescompleted865Fscreen100andearlydrawentrytrace; old94F1insideupdatepictureswerenotcompletedframes. No newTAPparityclaim. Negativebaselineandinternal/exporterasereportsseparate; aninitialexporttestreportusedbaselinefilename, correctedfilenamesandreranallthreebeforefinalpackage. scripts/package_stock_orb_test.py exportsbuild/cartridges/r155_l4_orb_test/rt_l4_r155_test.rom/.bin/.dck/ZIP,exact65536read-onlyrawROMandROM-onlyDCK,ZIPCRC/hashboundsummary. Exactexportnativeerase/boltchecksPASS. IncludesT247doubleBlatchfix. No latest/fullreleasepromotion; prior99/100/145/153/154andreferenceprojects unchanged. T246overallparityFAILotherissuesremain.


250. L1 corrupt pilot respawn message / shared pause-font overlap (2026-11-13). User reports messageafterdying. Initialolddeathfixtureuseddirectinitializers/uninitializedlives, producedrepeatedHUDicons; correctedtesttoactualcoldmenu/joystickstart. Normalrealmenurespawnfontintact/messagebitmapcorrect (staleECMscorecolorsremainexistingstyle). Foundconfirmedpausebackup7C80..7CE2overlapsnativefont7AE8..7CE7, includingT/Y/etc: addedfontpreservationasserttoverify_stock_controls; originalL1fails'Pause overwrote native message font'. Notconfirmedwhetheruserhadpaused; thisisverifiedcorruptionpath, notclaimofeverypossiblemessageissue.
Fixstock_controls.asm/build_stock_shared_cache.py: freezeIRQasbefore, borrow99bytesofreserveddecodedframecache(96pixel/colorbackup+3AYvolumes), restorerealpixels/attributes/AY, invalidateCTX+17framecachebeforeEI. Main-looppauseonly/noinflightselector, ROM/fontuntouched; pause_ram_contract.json assertscache>=99. Initialadded8bytesfragmentedL2ROM, failed84bytelegacyhelperallocation; removedunnecessaryIX/IYpush/pop (pauseroutinetouchesneither), all8buildsfit/pausecontrols+pause/twodeathchecksPASS. No artworkdropped/nootherRAMborrowed. Realmenupause/nativetwodeath+respawncheckscompareeveryPILOTSTANDBYbitmapbyte(16rastersperchar)againstpreservedfont, require2messages; messagefontpreservedall8. Collisiontriggerflagsinjectedonly,nodeathbypass/noenemyHPchanges.
L1fullregressionreachedchargedwalkerassertionfailure twice: pilotcounted13sameframebeamcontacts althoughHPfirstreached0oneighthhit/deathflagset; oldhits==8assertincorrectlycountedpost-lethalcontacts. Preserveall13writesinwalker_charged_attempt.json, requirefirstzerohitindex7ANDnativedeathbit7, notjustcount; no runtimeHP/weaponchange. Additional5contactsafterzero remainnativebehavior/notfixedorblanketweaponclaim. AddedfreshattemptJSONbeforeassertsofailuresdon'tleaveonlystalepassfiles. Correctedchargedcasepasses1041frames/61updates, normalpilotpasses; allpriorL1color/art/ownership/scroll/player/fire/IRQ/death/title/score/gameover/controls/BB/completioncheckscompleted, thenremaining240updatebossstresscompletedseparately,summarymarkedresumed_after_charged_assertion_correction/secondsnull(not0.01sfullrun). Fullvalidationnotrepeatedafteronlytestassertionchange. No newhardware/FPS/TAPparityclaim.
Diagnosticsrespawn_message.screen.bin/.png/home/font recordedandrendered; fullimagepreviewomittedtextvisuallydespite5022nonblackcroppixels, savedrespawn_detail.pngcropandvisuallyinspectedclearPILOTSTANDBY! (whitetop/magentabottom). Reproduciblepackage_stock_respawn_test.py exportsbuild/cartridges/r156_l1_respawn_test/rt_l1_r156_test.rom/.bin/.dck/ZIP,exact65536rawROM/ROM-onlyDCK/hashboundsummary/ZIPCRC. Exactexportactualmenupause/twonativedeath/messagesPASS908frames89updates0ROMwrites. IncludesT247doubleBfix. Other7sharedfixesinternalonly;stable99/100/145/prior153/154/155unchanged,no latest/fullreleasepromotion,T246parityblockersremain.


251. Coordinated cartridge/TAP parity work IN PROGRESS (2026-11-13), userauthorizesalllevelsfollowTAPcode/play/art. L2rowpaletteportinternal: exactTAPregion8343..83E3terrain160inks,83E3..844Bboss104inks dedup17rows+33rowmap169ROM0bytes. ReplacedobsoleteL2groupmasktablewithrowmap (src/stock_l2_row_terrain.asm); sourceordinaryterrain/pixelsunchanged. Globalpalette/dictionarypredicateL2includesflag6terrain; backendusesactualscreenrowsoverticaltileflipcannotreverseshading. Every160screenrow/bothflips/columns8,55,56,64global single/bulk2560checksPASS; stoppedbody18tiles17920pixels/repairPASS. Firsttoken-onlycandidateleft2415/1924/1165differences (verticalflips); directrowbackendreduces174/168/146at32/64/120. Everyremainingdifferenceatsample64isTAPwrongvsdeclaredrowink andstockcorrect(168foregroundpixels, periodiclefttileedge); referenceedge-interpolatorartifactclassificationstillpending, nofalsezero-pixelparityclaim.
Actualeventdataauditall8: L2onechangedbyteEAE9x13->19notported; L5current12sphereeventsdiffer84bytes; other6eventsidentical. build_stock_level_base.py nowimportsboundedeventrangeforeverylevelandhashesnative_event_contract.json. L2paired120bossevents/fullactorrecordsnow0differences, previously25. SeededfixturecontrolsallnativeLD A,RreadsplusC069andL8F122; no gamebinaryRNGchanges. Menujoyfirefixtureheldthroughnativeentryproduceddifferentresidualnormalshots; nowreleaseat863D,verify0shotsbothneutralbossruns. L1still4actorstatesdifferent(enemybullet),L5still28states(firstHP26vs24, notcurrentcoordsafterRcontrol). Removedstock-onlysync_player MARK_OWNERS asinternalhypothesis tomatchTAPpublicationtiming, comparingL1/L5now; mustverifypickup/collisionregressionsbeforekeeping. No newexport/latestpromotion. Approvalreviewtimeoutononecomparisoncommand; singleauthorizedretry succeeded. Keepworking;T246paritygateNOTsatisfied.

251 progress continuation (2026-11-14). L5paired120actorstatesbecomematch0diffafterremovingearlysyncMARK_OWNERS; L1neutraldifferenceactuallyTAPdeathat115 (allactorscleared), safeidenticalstart4,2gives120match0diff/deaths0both. Addeddeathsrecord/gateandseparatesafeartifactpath. Do not presentoriginalinvulnerabilityfixtureasreliabledeathprevention. Directshot/collisioncomponentsL1/L5stillPASS. RemovingearlyownersbrokeL4postdeathpickup/reardock: reproduced. Addedstock_pickup_contact.asm fallbacknativepickup9885andForce97F9checksactualfineplayerboundswithoutpublishingcollisionowners; firstpickuponlydraftcollectedbutfaileddock, finalForcefallbackrecoveryPASS. Fixedalready-dockedreturnmustreturn0unlessexisting7A95contacts (notreturnsideascount). HelperfixedROM0C21linkedbeforeHOME8000compression; initiallate-repackdraftremovedtoavoidcompressedallocationoverwrite. Allchangesinternal; latest7A95fallbackbuildL2fits64KB/global6066cases/scroll2129920pixel+colorchecksPASS. CurrentTAP2pixelbossgraphicsphasesnotyetported(stockextractorresetsmotionstateandcaptureswholecellphases); mustaddressbeforereleaseequivalenceclaim. ConsideringauditingunusedHOME8000..8382asruntimeworkspaceforgenericshiftedrenderer; NOTyetclaimedfree/modified. No newexport/latest.


251 progress continuation 2026-11-14. All8 coordinated suites PASS for current shared-fix baseline; hash-bound ROM/DCK/layout/summary copied internally to build/cartridges/t251_static_baseline, not released. HOME8000..8382 audit proves live owner/ECM flags; NOT free. L2 variant table losslessly period-compressed. Rebuild exposed relocated legacy helper still referencing FBD0 outside ROM0: corrected symbolic source before assembly. L2 initial direct vertically flipped palette also wrong despite global refresh tests: actual screen-row lookup plus reversed source patterns now passes272 direct/retained native tile/flip cases;2560 row checks added to required suite. Existing source terrain/art dimensions retained.
Active r145 fractional motion captured using actual8501 actor, cleared scenery and actor_phases+IYL; L3#40 inactive, #101..106 vertical. Other active IDs: L2#3..6 vertical; L4#25..27 XY; L5#8/30..33 XY; L6#18..25 XY; L7#49..54 (51 X-locked); L8#42..46 XY. Exact offline vertical factorization passes3,385,344 pixel/color comparisons; not runtime/performance. Naive full16-phase copies exceed L2/L4/L5/L7 storage. No dropped art.
Opt-in STOCK_TAP_MOTION=1 implementation for L3/L6/L8 preserves native targets and approaches2pixels/draw with signed offscreen coordinates, explicit64byte state/cache RAM. Exact actual native direct/retained motion art/brightness/hit ownership cases PASS: L3 768, L6 1024, L8 640. Rejected first trial wrote BC at IX+4/+5 (return address): ROM write guard caught it; corrected IX+2/+3 and excluded common effects. L8 exposed IFDEF-on-EQU omitted reset; explicit builder-linked CALL now asserted in binary. Intermediate failed assembler followed by stale-ROM tests when PowerShell continued: NOT accepted as evidence. Corrected stop-on-error command built fresh L8 and passed2128 ordinary art/common plus640 motion cases. Full post-reset L3/L6/L8 suites running. Default motion still opt-in; L2/L4/L5/L7 phase ports and whole-game/completed-frame/audio/hardware acceptance remain open. No newexport/latest promotion.
History contains mixed encodings: default cp1252 and then UTF8 reads both failed before writes; append this ASCII note as bytes, preserve all prior bytes.


251 further progress 2026-11-14. Exact TAP 2px phase ports now pass full internal suites for L2/L3/L5/L6/L7/L8, not just isolated previews. L2 128, L3 768, L5 640, L6 1024, L7 672, L8 640 direct/retained phase/brightness/owner cases. L2 uses exact vertical reconstruction with explicit200byte dense scratch and formally reserved320byte boss workspace; source bank for typed packet headers must be set before reads (failed initial constructor fixed). Its target palette-pair dictionary is lossless; bounded ROM6 compressed packets stage via allocated scratch with all banks/stack safe. Clean phase0 captures replace old static captures that retained scenery ownership and omitted some actor pixels. Only unreferenced/identical frames/palette rows are removed.
L5/L7 palettes exceed512rows: packed pair pages and11bit compact IDs use previously unallocated flag bits3/4; transport masks move those bits with the source. Dictionary publication clears stale high-ID bits. Palette pages do not hide stack/context; actual global/painter/IRQ tests pass. L7 saves480RAM bytes by snapshotting80 token/flag cells instead of640 expanded attrs. Full64-row/10column player backing window retained, not shrunk; all640 captured raster attributes still match after source maps mutate. Complete L7 suite48.58s PASS, source capture work is reduced. Normal builds now enable these six tested motion ports via stock_tap_motion_config.py; L4 full phase experiment is separate and unpublished.
L4 full exact naive phase layout fails:30408frame bytes versus13399available after code/palettes. Rejected without removing approved art. Actual TAP phase exploration120updates showed only horizontal phases, but600updates (explicit native-death bypass for coverage only) reveals vertical/diagonal phases too: do NOT infer unused artwork from a short sample. Shared grammar and byte predictors measured and rejected as larger/insufficient. Full L4 fractional port remains OPEN, default L4 restored/retested working whole-cell configuration (91.95s fullsuite PASS). All8 metadata tables now receive lossless period encoding and unused-palette pruning for additional space; coordinated rebuild after that optimization is pending.
Paired actual TAP early/boss120-update tests match native actors/events for L1/2/3/5/6/8. L7 TAP dies despite fixture7A98=254; deathtrace proves fineflag0 and native C3CD/C3CE coarse projectile death ignores invulnerability, before later actor/event divergence. Cartridge did not take that timing-dependent coarse hit. Unmodified failing reports preserved; no runtime game patch claimed. Added separately labeled --shield-native comparison-only C3814B->2D in both machines (absorb native coarse hits while comparing protected AI), not evidence of unmodified survival or a game fix. Scope remains open. Six tested ports preserved internally at t251_motion_stage, no public cartridge ZIP/latest promotion; r99/r100/r145/prior test archives unchanged.

T251 continued: Final default all-eight component run passed (L1 52.30s, L2 85.51s, L3 50.30s, L4 93.20s, L5 54.31s, L6 47.49s, L7 49.49s, L8 45.52s). L1 was subsequently restored/revalidated in 51.92s after the optional STOCK_IRQ_DECODE pilot failed its injected-IRQ ROM-write guard (write0000, PC0035). Pilot remains disabled; no music/performance improvement claimed. Disabled builds now remove stale experimental decode contracts. Current paired TAP/cartridge scenarios are being refreshed against final binary hashes. L7 comparison-only coarse-projectile death bypass passes both early/boss scenarios; these are protected AI/state comparisons, not survival or hardware acceptance. L4 full fractional-phase artwork still exceeds64KB; tested whole-cell fallback remains. No public release promoted.

T251 diagnostic image: build/cartridges/integration_work/fractional_phase_components.png rendered and inspected. These are isolated seeded component canvases, NOT gameplay screens: rainbow bands outside the cleared actor rectangle are retained test-fixture attributes. Actor detail is visible within cleared rectangles. Do not use this montage as gameplay/visual parity evidence; completed native-update paired screens are generated separately.

T251 completed-frame montage build/cartridges/integration_work/current_paired_completed.png inspected: despite all16 actor/event scenarios passing, L2 boss color and several boss compositions differ visibly. Visual acceptance FAIL; no release. Found two L2 repair lifetime problems: interrupts can replace in-use cache; cleanup erased all cell flags, including ECM dictionary/high palette ID bits. Repair now holds input-only IRQ guard (STATE+10, outside pointer STATE+8/+9), cleanup masksFC, repair dirtiness checks only low2bits. Injected IRQ tests pass2 actual interrupts, all17920 boss pixels and280 post-cleanup palette-restored cells pass. Initial test asserted guard0 instead of restoring actual value; corrected. First implementation saved guard in pointer high byte STATE+9 and failed, fixed toSTATE+10. Guard-only live image l2_cache_guard_completed.png inspected: color still wrong, motivating separate dictionary cleanup fix. Full L2 and final paired reruns pending.

T251 L2 runtime investigation continued: preserving cleanup metadata and IRQ guard passed fullsuite81.91s, but actual completed boss entrance still differed (red silhouette). Traced the moving getter: stock-only material conversion intentionally threw away rich bitmap/paper shading while approaching. Replaced with exact rich tile bits/local ECM row pairs; all18 moving getters now checked bitmap+8row pairs percell against the current TAP-derived body assets. These are source artwork, no recoloring/rescale. Fullsuite and refreshed early/boss paired runs pending for this final change. Previous completed-frame report is stale for L2 until refreshed; publish_ready remainsfalse.

T251 rejected rich-entrance trial: full isolated suite75.81s and paired actor/event checks passed, but inspected l2_rich_entrance_completed.png shows incorrect position/color bands. Native scrolling tile copy/header processing does not preserve local frame palette context. Rejected trial source retained at build/cartridges/integration_work/level02/rejected_rich_entrance.asm; restored material-only getter. Existing rich source has96 palette rows (A0..FF), so a correct port must preserve/translate stable headers through the entire native copy/scroll path, not return local cached tags. Separate IRQ guard and metadata cleanup fixes retained. Final stable regression rerun underway. Not release eligible.

T251 final stable checkpoint: restored L2 complete suite PASS88.95s; refreshed early/control and boss actor/event paired traces PASS. scripts/summarize_current_stock_integration.py verifies all8 ROM hashes, every component evidence hash, and all16 final DCK/paired trace hashes. current_integration_report.json: componentsPASS, paired-state scenariosPASS, visual_parity_confirmed=false, publish_ready=false. Completed montage regenerated from final stable binaries; visual rejection already recorded. Public latest/export pointers unchanged.

252 continued TAP parity repair (2026-11-14): Actual L2 trace proves both stop at column64; runtime reveal had FF terrain owners/flag64 so isolated owner0 painter tests were insufficient. New direct cell repair copies eligible body bits to retained and front planes, publishes global ECM IDs, protects native copy until cleanup, preserves actor-owned cells. One-time entrance retirement clears old FF silhouette. Actual TAP getter+painter recapture exposed incorrect manually sliced bossPalette; scripts/extract_stock_l2_painted.mjs now captures18 tiles as native raster writes. Rich source renders correct red/white shading; l2_reset_completed.png inspected against TAP, old silhouette gone, core body agrees. New regression seeds FF/64, checks17920pixels,280post-cleanup palette restores,2actual repair IRQs. Full L2PASS84.28s after shared reset; L5PASS54.86s. Shared full initialization now clears640nativeowners+640flags without touching8383vectors/reversal/font. Native gameplay150update budget extended7000->8000 after one run reached149at7000; elapsed counts retained, not a speed improvement. Internal checkpoints t252_l2_checkpoint; no release.
L5drawtrace:832 actual9172/9175 selector origins/dimensions match, sampled/full owner maps match. TAP compiled selector draws directly and returns54transparentcells to suppress native repaint; stock fallback whole-cell painter lacks the TAP overlap compositor. Current screenshot differences therefore need compositor transfer, not position guessing. L4in-place codec feasibility:323680pixel checks show89used source-color/target-pair quantizer keys with0conflicts; can reconstruct horizontal phases from phase0 plus captured pair maps. No runtime implementation/performance claim yet.

252 compositor implementation checkpoint: Opt-in STOCK_L5_COMPOSITION allocates256RAMpalette rows2048B, hashes256B, references32B, state64B; compact80-cell player attribute snapshot saves480B, leaving382B. Static L5palette IDs remain<1024; dynamic IDs1024..1279 use existing11bit publication. Actual native/player readers pass2048dynamic lookups; exhaustion preserves live rows, free rows reclaimed, player snapshots included in reference scan. Source pool dispatch missing on first attempt was caught by ROM-write guard and corrected; no release.
Transferred Bellmite front-to-back normal/black pair rules:24576independent row cases +512actual native overlap cells/all4flips PASS, ownership preserved. Actual runtime gate9172 now holds decoded frame across selector/painter and returns a transparent native tail. All256vector boundary probes plus orientations/nestedguard (263cases) PASS forL2/L5 with263real player ticks during actor paint; common cached FX deferred only while busy2, strict composite/reveal busy1 still input/music-only. Shared directory reads now map once atomically rather than3read_byte calls; permanent source/stack visibility retained. L2kernel992+32star guard exactlyfits1024; star protected() already returns correctZ, redundantORAremoved. Other six levels need rebuilt/tested against shared gate. Current L5 is opt-in internal candidate, not default/release. Full L5/L2 suites and actual boss comparison running.

253 stock integration continuation (2026-11-14): All8 current ROM builds now pass the rebuilt component suites and refreshed16 paired early/boss actor/event/control scenarios against r145 TAP. The shared full-painter actor cache guard and native owner/flag reset are included across all8. Actual263 IRQ injection cases (all256 vectors, orientations and nested guard), real player ticks preserved; ROM writes0. L2 captured native painted body/direct retained repair and FF-owner lifetime fixes retained. Public release pointers unchanged.
L5 compositor now default enabled (STOCK_L5_COMPOSITION=0 retains diagnostic fallback). All foreground/back pair rules,24576 independent rows,512 native cells/allflips,16 raw/terrain/reversed palette policies,3 actual opaque-cell skip cases PASS. Dynamic192-row palette pool,72B state, expanded640B player attribute snapshot;286RAM spare. Cache hash/reclaim churn1024 cases and no live-row overwrite PASS. Optimized one old-palette read per cell, source block copies for ordinary nonflashing cells, foreground full-mask early-out, and output opacity metadata. Live240world-update boss stress11977refreshes,0ROMwrites,0palette overflows; explicit native death bypass, NOT survival/victory/hardware FPS. Intermediate candidates106/167/172/223/210/229/237 updates in12000refreshes failed the unchanged240 target and were not accepted. Final suite89.09s PASS. Normal default rebuild byte-identical to tested opt-in binary.
L4 still uses whole-cell boss movement: exact2px phase codec is NOT integrated. Offline48-frame reconstruction checks prove323680 colour quantizer checks/0conflicts,428 mapping patterns/0pixel errors, backward source dependency schedule max151Bpadding/1233Bscratch. This is only storage/constructor feasibility. Sparse shift-correction alternative3642B is worse than factorized mappings; no runtime/performance claim.
Current report hashes all8 ROMs, component artifacts and16 paired DCK traces; publish_ready=false/visual_parity_confirmed=false. Elapsed TAP/cartridge pacing differs, L4 fractional port remains, L7 comparison uses explicit shared coarse-death shield. No new public release or full hardware/all-boss acceptance. See current_integration_report.json and current_paired_completed.png.

254 clean actor-capture integration (2026-11-14), supersedes earlier T253 checkpoints: completed-frame review found live L5 enemies missing despite matching actor state. Initial compiled-placeholder hypothesis was narrowed by an actual selector-write trace: stale native ownership/flags in the extraction fixture suppressed ordinary native painter output. extract_stock_written_levels.mjs now clears full DOCK owner area and HOME8000..8380, captures BOTH selector/painter writes at the returned origin, and emits mandatory captureContract v2. Builder refuses old captures. Regenerated ALL8 actor sets. Recovered nonempty IDs include L2:1,2,16,17,18,31,45..52; L3:1,2,5..30,36..40,88..93,96..100; L8:3..31,33..36,38..41. L5 missing35/36/37 are now nonempty; their prior recapture predates the perlevel backup so not included in that delta list. L6 poses grew from19 to91 distinct frames with proper shading. Source ZIPs/TAP/reference projects unchanged.
RAM planning now uses the actual written actor and perlevel common captures, includes motion maximum, and is a mandatory validation rebuild step. L1 needed a larger decoded-cache reservation. L8 >20-row isolated diagnostics clear extra off-playfield owner slots consistently with the extractor and their already-expanded diagnostic viewport; actual game clipping stays20rows, no IRQ-page borrowing in gameplay.
Restored L5 art fit required splitting the exact row blender into permanent ROM0, and lossless delta-coded vertical palette headers restored in RAM before native painting. L6 uses existing exact palette-pair storage plus delta-coded full-frame palette headers (decoded only on fresh frames, not repeated cache hits). Pixel/colour, allflips, ownership, cache, ROM guard and runtime checks validate those formats. Cross-shape packet reuse and first-use local palette sorting trials did not save enough and were withdrawn.
L5 exact equal-palette row shortcut passes24576 independent cases (including empty/full foreground boundaries),512 actual native overlap cells/allflips,16 bulk palette policies and3 opaque early-out cases. Reference bits now conservatively accumulate all new/matched published rows; exhaustion triggers live-grid/snapshot rescan. Removed unconditional640-cell rescan at each world copy.1024 ordinary hash-chain churn plus1024 sparse allocations protecting32 live rows pass; sparse test required6 rescans,0ROMwrites/overwrites. Final complete L5 suite80.24s PASS; boss240updates/11957refreshes,0ROMwrites/0pool overflows. It still only narrowly passes the cadence bound; not a hardware FPS/survival/victory claim.
All8 final complete component suites PASS (L1:57.19s,L2:90.05s,L3:58.59s,L4:97.94s,L5:80.24s,L6:51.81s,L7:54.02s,L8:59.91s).16 refreshed paired early/boss actor/event/control scenarios PASS with final DCK hashes; L7 explicitly shared coarse-death shield remains comparison-only. Actual completed L5 image inspected: the missing enemy chain now agrees in position/shape/palette with TAP. Stars/player effects differ with elapsed IRQ time. Actor-count instrumentation now targets the actual stock_select symbol, covering custom paths outside9172; the previous empty actor count in the restored L5 cold test was instrumentation, not absent gameplay. Natural cold test150updates/4703refreshes/3starts sees10 actor IDs and0ROMwrites, no death bypass.
Hash-bound current_integration_report.json regenerated and internal recovery checkpoint saved under build/cartridges/t254_corrected_capture_checkpoint/. No public ZIP/latest pointer promotion. Remaining: L4 exact2px boss movement codec not integrated, elapsed world/music/input pacing parity, completed-frame acceptance of remaining dynamic differences, L7 unmodified survival parity and hardware/all-boss coverage. publish_ready=false and visual_parity_confirmed=false. Do NOT call all cartridges finished.


255 stock cartridge consolidation r157 (2026-11-14): all8 current default ROMs rebuilt and complete component suites PASS (L1:57.48s, L2:88.41s, L3:59.56s, L4:99.55s, L5:78.34s, L6:53.09s, L7:52.5s, L8:58.36s); all16 hash-bound early/boss TAP actor/event/control comparisons PASS, refreshed L1..L4 traces after relevant trials, unchanged hashes retain L5..L8 evidence. All96 package requirements and source/data/RAM/audio checks PASS. ZIP CRC, every raw BIN/ROM identity, all8 ROM-only DCK headers and exact65536-byte images PASS. Archive: build/cartridges/r157/RType_TS2068_64K_cartridges_r157.zip SHA256 004354258421463cf70a5e1ee0718dbaeee383748db2365dcc50ff28f5d64ab5. Includes T241..254 fixes/current recovered actor art, L2 painted-body/row-colour repair and L5 exact overlap composition. Source/r99/r100/r145/reference archives unchanged. Release builder now uses protected explicit version folders, refuses archived/version overwrite, verifies comparison hashes before packaging, and includes acceptance evidence plus comparison image/report.
L4 accepted release binary is byte-identical to t254_corrected_capture_checkpoint/level04, retaining faster native whole-cell boss movement. Full L4 suite PASS; actual16hits per3targets/native victory, two real death/pickup/rear-dock/rear-fire recovery cycles, orb erase and cold BB tests PASS. Boss stress240updates/7746emulated refreshes,0ROMwrites. L5 stress240/11957refreshes,0ROMwrites,0palette overflows;24576 row rules/512 native cell cases/all4flips,16 palette policies,3 occlusion cases PASS. Dynamic palette churn1024+1024 protecting32live rows PASS.
Unreleased L4 exact fractional experiment: base decode/horizontal shifts/sparse corrections/vertical extraction fits64KB; latest indexed palette-quad constructor384 direct/retained phase cases PASS,0ROMwrites. Early row-block candidate193updates/12000 FAIL, shared-source-cache185 FAIL, indexed-quad candidate203 FAIL, no-stars206 FAIL against unchanged240 bound. A partial zero edge guard caused shifted stray pixels; phase test caught it, full8-byte zero guard restored and all384cases PASS.203 timing predates that guard restoration; no final fractional gameplay acceptance claimed. Earlier32 generation checks and256constructor IRQ return injections passed, but actual procedural IRQ attribute-call count0, so those probes are not proof of deep palette-miss IRQ coverage. Trial preserved separately under build/cartridges/t255_l4_fractional_experiment/ with explicit STATUS; not packaged. Default L4 boot data retains original working image; its experimental cleared image is conditional. Do not enable the fractional option as a release default without resolving speed and completing final IRQ/live checks.
Diagnostic image: build/cartridges/integration_work/current_paired_completed.png regenerated from16completed world-update100 screens; archived as r157/comparison.png. Actual TAP left/stock right inspected: principal terrain/actor/boss layouts present, with elapsed-IRQ player/star/effect/dynamic-colour differences. No pixel/cycle parity certification. L7 paired comparison retains explicit shared coarse-death shield. Native whole-game timing, physical PicoROM/PicoVideo acceptance and all-boss natural-survival/victory coverage remain limitations, not claimed complete. Broader current_integration_report publish_ready=false is preserved; separate stock_component_package_ready=true and release matrix pass. docs/STOCK_CARTRIDGES.md and separate stock link updated; stable disk pointer unchanged.


256 L4 fractional cartridge completed, r159 (2026-11-14): exact r145 2-pixel presentation now enabled by default for L4; all7 moving bosses have fractional ports, L1 remains static. The final immutable adjacent-quads-v2 codec uses704 adjacent-row recipes (457 implicit-lower defaults plus247 exceptions),3059 valid permanent/static colour IDs,12-bit native token flags,156 bounded expanded-row cache entries, and compressed base/shift corrections. It fits an exact65536-byte read-only cartridge without resizing artwork. L4 logical art:215frames,47488unpacked native frame bytes,1939oracle palette rows,1261-byte decoded frame cache. Other7 cartridge binaries remain byte-identical to r157.
Final full L4 suite PASS in120.14s;384 direct/retained phase cases,3059colour IDs/32720 raster reads and1024 cache evictions,256 reversal bytes,640 compact-snapshot reads,2048ROM-font cases,256 actual constructor IRQ/forced-colour-return probes PASS.96 saved-IFF off/on constructor cases cover545580mapped instruction fetches with no interrupt-enabled mapping; deliberately removing read guards is detected by a negative control. Native48-hit victory and two genuine death/equipment-loss/recollection/rear-docking/rear-fire cycles PASS. Recovery pilot now uses ordinary movement/detach input if initial docking is at the front; no enemy HP/timer edits. Final boss stress240updates/11804emulated refreshes PASS against unchanged12000 bound; all240 HUD samples have0paper errors;0ROMwrites.
All16 hash-bound TAP early/boss actor/event/control comparisons and all8 release data/memory/audio gates PASS. Final image inspected: build/cartridges/r159/l4_completed100.png (TAP left, cartridge right, completed boss update100); HUD paper errors0 in both. Full comparison: build/cartridges/r159/comparison.png. Elapsed-IRQ player/star/effect differences remain; not cycle/pixel parity or a hardware/all-boss natural-survival claim. L7 paired shield remains explicit. Broader publish_ready=false is retained, stock_component_package_ready=true.
Archive build/cartridges/r159/RType_TS2068_64K_cartridges_r159.zip SHA256 3db00638d0a48a16d4b84143f327da4f58c418ff411bdd5b4f56ca2da3b5e290. ZIP CRC, all8 exact65536-byte BIN/ROM identities and ROM-only DCK headers PASS. docs/STOCK_CARTRIDGES.md and separate stock link updated; r99/r100/r145/r157 archives, original ZIPs, reference projects and stable disk pointer unchanged. The unpromoted r158 archive is withdrawn (WITHDRAWN.txt): visual review found416 corrupted HUD paper cells at boss update100. Standard attrs5A80..5AFF must stay native HUD storage; cache now ends5A80. No release pointer promotes r158.
Lessons: immutable colour identity must outlive frame/cache generations; phase bits must be mixed before cache hashing (raw modulo grouping exhausted only one quarter of buckets); all256vector-return probes do not prove safety of every bank-read window, so add instruction-window checks and negative controls; retired ECM standard attrs are not wholly free while native HUD mirrors still read them. Keep all8 interleaved lower32-row working-image code/variable gaps and the8080scanline-pointer table intact. Glyph borrowing is restricted to7B08..7CC7, with native font reads redirected to existing ROM4, and no high-score/music-variable borrowing. Earlier ordinal/mutable-pool/direct/four-way cache trials failed speed or lifetime checks; t256_l4_cache_trials preserves the pre-adjacent-codec source checkpoint. Hardware PicoROM/PicoVideo confirmation remains pending.


## 2026-11-14: r160 L4 twin-launcher layering repair

All three selected launcher poses already contained both rockets. Live r159
update43 showed projectile owner FA suppressing whole cells:40 painted bytes
versus72 with owners cleared, with32 raster mismatches. Repair is scoped to
native IDs52-54: temporary visual predicates ignore FA, then native predicate
code and all saved projectile collision owners are restored. Actor/projectile
records remain unchanged. The first prototype changed seven strict paired
actor coordinates; restoring collision ownership resolved those differences
without weakening comparisons.

PASS72 pose/flip/direct-retained/layer cases; PASS263 launcher IRQ/guard probes
including all256 vectors. Strict early and boss TAP comparisons pass. Full L4
suite passed in130.36 seconds. Boss stress240 updates/11790 refreshes under
unchanged12000 limit;240 HUD samples, zero paper errors and ROM writes.
All eight release contracts and16 hash-bound paired comparisons pass. Other
seven ROMs remain byte-identical to r159. Hardware confirmation remains pending;
publish_ready=false still denotes broader cycle/pixel/hardware parity scope.

Inspected diagnostics: build/cartridges/launcher_review_r160/launcher_before.png
and build/launcher_review_r160/launcher_before_after.png; packaged comparison:
build/cartridges/r160/launcher_comparison.png. Live capture uses explicit death
bypass for diagnostic coverage, not natural-survival certification.

Release: build/cartridges/r160/RType_TS2068_64K_cartridges_r160.zip
SHA256:292725eb5e53efb1f6ce9003164094a2a23b06aeab336893f82308ec792a5c2f
ZIP CRC, raw BIN/ROM identity and read-only DCK headers pass. Original ZIPs,
reference projects, protected release archives and stable disk pointer unchanged.


## 2026-11-14: R-Type r160 web publication

Prepared R-Type/ for jon0x0/ts2068 with all eight r160 read-only carts, source
snapshot, release evidence, TSRun ZIP, project/keyboard guide and isolated
Berzerk/Sinistar Virtual DPad runtime. Original runtime hashes all match its
provenance manifest; all DCK/BIN bytes match r160. Keyboard bindings remain
in-game; verified O/P/Q/A/Space/Enter definition. Browser L+number switches
cartridges; physical cartridges remain single-level.
Actual Edge/Playwright: all8 browser startup/resource checks and L4 switch PASS,
zero JS/HTTP errors. Real OPQA definition, native touch Fire, P movement and
Shift-P pause/resume exercised; screenshots playing-defined.png and
paused-defined.png inspected (visible ship moves and PAUSED overlay). Double-B
input exercised; native boss acceptance remains in existing component tests.
Desktop, key-setup and390px phone screenshots inspected. Native runtime has
not been modified. ZIP CRC, pinned TSRun hashes, cart identities and local page
links PASS. Diagnostics under build/publication_r160 and published web-validation/.
Hub generator lists Remastered games, Arcade ports, Spectrum ports and8 new
cartridge entries (19 total). Physical hardware acceptance remains separate.

Web publication follow-up: touch Boss now acknowledges native FD4B latch
press/release/press instead of assuming a frame rate or initialized chord.
Actual Edge test PASS: mode3, column15 to98, latch3, all keyboard contacts
released. No native RAM edits. Diagnostic inspect API removed from final
adapter. Maintained frontend lives in web/ and is overlaid by staging script.
First public commit56eb577 deployed successfully; final control/archive update
follows. Public Pages project/player/hub and ZIP/DCK returned HTTP200.

Publication complete: GitHub main ff8ae7d5c86363f5e65ca30d103845a0d8f88b9e,
Pages status built. Live project/player/hub HTTP200. Deployed browser L4 startup
and Virtual DPad hide/restore PASS with zero JS/HTTP errors. Public final TSRun
ZIP SHA256 2c77bef360c8eb1fe044fbf6944c454362b6e09009df8e9aa6b8c32f41185057
verified; latch-aware adapter deployed without diagnostic inspect API. Exact
live resource evidence: build/publication_r160/live_publication_validation.json.
Git checkout build/publish_rtype_hub is clean. No original cartridge or disk
archive changed.


## 2026-11-14: publish full disk/TSPico download

User clarified that the hardware archive is required, not only the TSRun ZIP.
Published preserved r145 full-game archive as
R-Type/downloads/RType_TS2068_TSPico_r145.zip, with complete rtype/ folder and
rtype/rt.tap entry point. Also published the20 loose companion TAP files under
R-Type/rtype/. ZIP CRC,20 manifest hashes and962 TAP block checksums PASS.
SHA256 bb0c9311569bbb3c688de3fa2cc36816f69b0a2397275c7228d55a45799eefcf.
Project page/README and all3 hub category download links now prioritize this
full disk edition. Installation: extract to /TAP/, keep /TAP/rtype/ intact,
reset and launch rtype/rt.tap. Distinct from cartridge/browser r160; no new
hardware claim or relabeling. Stable r99/r100 archives unchanged.

TSRun player guide now links the TSPico full-game ZIP and explains full512KB RAM whole-game preloading or per-level loading/caching, plus /TAP/rtype/rt.tap installation. Maintained web source and offline TSRun ZIP synchronized; ZIP CRC and embedded link/text checked. No game/cartridge changes.

2026-11-15 BW browser option: display-only grayscale button next to CRT. Native core/art/cartridge bytes unchanged; colour UI retained. Actual Edge PASS toggle/colour restore/retained level switch, zero JS errors. Screenshot interior chroma PASS: colour has non-gray pixels, BW zero (tolerance2). Exclude1px fractional-bounds parent-background edge, which caused initial whole-image check failure. Diagnostics build/bw_colour.png and build/bw_grayscale.png inspected; published web-validation/bw_validation.json. Offline browser ZIP synchronized and CRC PASS.


2026-11-15 r161 normal-black game output. Treat bright black as valid; fix unintended black-paper producers rather than emulator palette. TAP r145 title already normal, scores were not. Stock r24-derived title clear/HOME FC80 delta helper retained47/45. Fix typed title attrs/constants, native initial actual black-paper fill, score white/cycle constants (native multicolour animation retained), both stock title-attract/post-death score gateways prepare attrs before mode0. Keep ECM during title legacy attribute copy (40->42). TAP CORE and eight LEVEL/START cold/cached sources fixed; L7 Preparing level36,47->36,07. Native descriptors/encoded palette IDs/art dimensions/gameplay untouched.
Frame audit found stock L4 old cyan-on-black returned by flat restoration, despite normalized cache. Conditional actual-attribute helper0F50..0F68 (existing ROM0 padding below0F80), branch164Etarget16C9, CALL in retired JR/AND bytes16C9..16CC, all following entries unchanged. Preserve BC/DE/HL and BRIGHT for two-nonblack pairs. All256 actual-ROM inputs checked perlevel. No new RAM or cache relocation from this helper. Rejected mirror-back experiment added unnecessary work and did not fix separate title-score gateway; final mirror remains7EE63F, unchanged.
PASS all8 full component suites/ROM-RAM-data-audio contracts and16 hash-bound TAP/cart early/boss scenarios. Actual displayed-RAM audits after native bootstrap:31208stock+31133TAP primary display frames, zero unintended exposed bright-black pixels; secondary hidden loader and pre-title ROM-unpacking workspace excluded. Original L1 title edge example2973 and score40148 exposed bright-black pixels; original title-clear frames up to49152. Diagnostic build/normal_black_audit/before_after.png inspected: original palette with index8gray, fixed black edges/paper, animated score colours retained; this is actual RAM rendering, not hardware/complete raster-latch proof.14cold/cached routes all8levels, final coldL1/L5fire,7collision positive/negative cases, L5boss160updates/all256vectors PASS (actual IRQreturn0/255; other targets identical). Harness corrections: read game state through current bank mapping, negative collision control always preserved r144 clock, normal native initial attr expectation7 replaces71. Original archives/referenceprojects/stable99/100 untouched. Physical hardware and all-boss natural playthrough pending. TAP archive cc2edbd1d25c4b51a8077de031ccaf7528de342525b761b84d72f0880e2f40d9.

r161 final stock package: build/cartridges/r161/RType_TS2068_64K_cartridges_r161.zip SHA256 ddcc30a673e724cba5f8ec5e3a6bcf3af54f23549138cfcf61df5f2ec3c69b17. All8component/source-data-RAM-audio/package gates,16paired scenarios and ZIP/ROM/BIN/DCK checks PASS. Software component package acceptance is distinct from broader cycle/pixel parity publish_ready=false and hardware acceptance.

r161 browser smoke: Edge local HTTP, published TSRun core/palette unchanged; r161 L1/L4 DCK requests200, BW toggle/colour restore PASS,0JS errors. Actual cropped browser_colour.png (inspected) has0pixels at original bright-black RGB51/51/51; browser_bw.png has0non-gray pixels tolerance2. Diagnostics and report under R-Type/web-validation/normal-black-r161/. No emulator palette flattening.

Published r161 game fixes to jon0x0/ts2068 main commit31b9db93d3b339da49cd125b5046acd2356b6d52. Clean publication worktree build/publication_r161_hub; original build/publish_rtype_hub emulator investigation remains untouched/unpublished. TAP/cart/TSRun ZIP CRCs, all8headers, source checksums and actual Edge startup/BW/black-background capture passed; Pages deployment being verified.

Pages deployment43731592124 success. Live HTTP verification: all3r161 ZIP downloads byte-exact to local archives, L1DCK/adapter exact, browserHTMLr161/cache-busted controls, all3hub category links updated. Evidence build/normal_black_audit/live_publication.json.

2026-11-15 r162 player-adjacent coloured-paper artifacts. User browser screenshot green/cyan rectangles after movement/firing. Reproduced with exact published TSRun core and archived r161 L1 ROM, ordinary joystick input:1551frames/229badframes/max5empty-paper cells; fixed0badframes, no memory hacks in natural sequence. Trace native stock_restore passedA3 for cleared/unowned source but dictionary flag/tag survived: palette325 row29,29,29,01..hex (cyan paper) restored into erased bitmap. Original treatsallnonzero aslive. Match existing backing-cache contract where0/3empty; markers1/2ownedretain shading. Actual-gateway negativecontrol provesoldA3copiesrow; fixedA3allblackpaper, A1/A2byte-exact old rows.
Final12byte helper0F70..0F7B, replaces original4byteOR/JPdispatch withCALL/NOP; discards only its own helper return on0/3tailcall toexisting162F. All8ROMs differ exactly16bytes fromr161:12padding+4dispatch; kernel sizes/entries/RAM layouts/art/code/audio otherwisebyte-identical. Growingkernel8byte trialfailedL2starwrapper2400boundary, rejected; finalpaddingversion passes. Full8component/source-data-RAM-audio/IRQ/boss/16pairedTAP-cart checks PASS. TAP remainsr161 (different full retained colour plane); no relabel/no emulatorcore change. Hardware/all-boss naturalplaythrough not claimed. Docs CLEARED_CELLS_R162.md, scripts verify_player_clear_r162/verify_player_natural_r162, src/stock_clear_dispatch.asm.
Diagnostic build/player_paper_r162/before_after.png inspected: cyan bars beside ship removed; paper_3/paper_5 reproduce stalepaper. paper_4 textured candidate not proof; charge_case.png/green_case.png initial green detector falsepositives legitimatebeam/shipdetail, notfixed away. Keyboard/neutralshortshot scans initiallynonrepro; movement+firing reliable. Original/heldlatch emulators CPU/RAMsame, artefact in actualRAM.

r162 final package33ec9c7b973a6d05999a2cb4d11626a43cb15c7991232b7a3d9f93a59c1d2e68. Final actual Edge browser L1/L4r162asset requests200/BWtoggle/colourrestore/0JSerrors PASS; screenshots browser_colour.png/browser_bw.png under web-validation/player-clear-r162. Eight64KB rawROM/BINidentity/readonlyDCKheaders/ZIPCRC/source-RAM-audio/packageacceptance PASS;16pairedscenarios and natural229->0 regression PASS. Staging preserves161TAP and TSRun core; no hardwareclaim.
