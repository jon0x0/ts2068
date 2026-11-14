CURRENT RELEASE - r100, 2026-11-08
User confirmed r99 is working again on real hardware after reported startup/fire/L5boss failures. Preserve r99 ZIP fa1d6a4d67b854f1acd5e3495dff564eac30bfc6b4d0b2175de00bbfdaa58c5a. r100 is the release promotion: only fixed-length version strings differ; no gameplay/art changes. Full disk/512KB package build/releases/r100/RType_TS2068_r100.zip; latest copy build/releases/RType_TS2068_latest.zip; SHA256 a73683bbca15a94b1e6f978c5f1e38f5b4c4be6dc7337ea503a560726d0cb6c8. Fresh unmodified initialL1/earlyL5 startup and threefiretimings pass; all8region/tape/image/checksum/version-only/fullIM2/gateway/ZIPcontracts pass. Hardware confirmation applies to r99's reported regression route, not all levels or new independent r100hardwarecoverage. Use python scripts/release_latest.py; docs/CURRENT_RELEASE.md. Stock64KB cartridge separate/unchanged. Historical pending-hardware entries below are superseded by this confirmation for that reported route.

## r22: M toggles music independently of effects (2026-11-02)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r22.dck`.
Current64KB read-only PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r22.rom`.
Press M once to mute music, again to resume at the current song position.
Held keys do not repeat; fire/death effects remain active; music defaults on.
CPU and Fuse toggle checks pass on both targets. Scope remains level one with
one looping2019 AY arrangement. Levels2–8 and their music are not integrated;
boss colour/shading mostly uses Spectrum geometry, not fully converted arcade art.
See docs/r22_music_toggle_and_coverage.md and TEST_HISTORY058. Hardware untested.

Theme update (2026-11-02): assets/terrain_themes.json now defines eight authored
level-theme families, each with two complementary group arrangements. Level1
uses the accepted r21 colours unchanged; levels2–8 have prepared palette assets
under build/art_assets/level_themes but gameplay conversion remains pending.
Both cartridge hashes unchanged. See TEST_HISTORY057.

## r21: distinct palettes for separate level instances (2026-11-02)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r21.dck`.
Current64KB read-only PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r21.rom`.
Corrects r20's source-tile reuse: the same source cell can now use warm or cool
arrangements in different terrain groups. Actual107-column map analysed, not
the subsequent enemy data. Initial draw, streaming and repaint retain the style.
181 reused source cells verified with both arrangements on both targets; all8
Fuse scroll phases and extended motion checks pass. Death65/faster title retained.
See docs/r21_instance_terrain_groups.md and TEST_HISTORY056. Hardware untested.

## r20: selected65 death sound, faster title, separated terrain palettes (2026-11-02)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r20.dck`.
Current 64KB read-only PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r20.rom`.
Selected audition65 now plays natively, including triangle envelope and noise;
music C continues during death. Title sweep/spread take about half the time.
Offline terrain colour-island analysis permits separate vertical arrangements
where foreground groups are separated by more than8 pixels; no new frame work.
All8 Fuse scrolling phases pass. Level one; hardware untested.
See `docs/r20_selected65_title_islands.md` and TEST_HISTORY055.

## r19: warmer arcade-guided terrain colours (2026-11-02)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r19.dck`.
Current64KB read-onlyPicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r19.rom`.
Default arcade palette adds gold/copper/silver shading derived from the original
platform/pillar captures. Preserve/chroma comparisons remain available. Shared
scanline/mirror compatibility and collision flags retained; renderer/RAM unchanged.
Extendedmotion checks601040SRAM/529632ROMbytes:0pixel/colour errors; all8Fusephases
pass. Sounddefault unchanged. Separate triangle trials61–68 use preferred50/59.
See docs/r19_arcade_terrain.md andhistory054. Levelone; hardwareuntested.

Death audition update2026-11-02:choices41–60now combine33noise,37contour and
arcade up/down pitch guidance;53–60are actualspeech2ay/Ayumi optimized variants.
Open `build/audio/death_pitch_variants/index.html`. No cartridge defaultchanged.
See docs/death_pitch_variants.md andhistory052.

Sound audition update2026-11-02:preferred14now has20additionalvariants21–40 in
`build/audio/death_14_variants/index.html`, withoriginal14andarcadereferences.
No newdefaultselected; r18cartridges unchanged. See docs/death_14_variants.md.

## r18: clean whole-screen ECM title initialization (2026-11-02)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r18.dck`.
Current read-only64KB PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r18.rom`.
Fixes the reported coloured ghost text and stripes outside the moving logo:
both complete HOME display planes are initialized before mode2 is enabled.
The correctly banked mode shadow is initialized once. Whole-screen checks cover
all90animation states and mid-sweep Fuse captures on both targets. Sound choices
and all20auditions are unchanged. See `docs/r18_full_title_screen.md`, history050.
Level one; physical hardware untested. Historical notes follow.

Death-effect audition update2026-11-02:20choices ready in
`build/audio/death_20/index.html` (solo/music modes). No new default selected;
r17cartridges unchanged. See `docs/death_20_audition.md`, TEST_HISTORY049.

## r17: smoother coherent title and two-channel death noise (2026-11-02)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r17.dck`.
Current read-only64KB PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r17.rom`.
The overlapped title moves in4-pixel phases with a shared vertical white/cyan
division. Each glyph restores its original colours as it separates. Death53 now
uses a noise-led two-channel Ayumi fit, temporarily reserving musicC. Coin99 and43
are unchanged. Same native death event as the old2019effect11, different waveform.
See `docs/r17_title_death_noise.md`, comparison page and TEST_HISTORY046 onward.
Level one; physical hardware untested. Historical notes follow.

## r16: new-logo motion, level-one music and replacement effects (2026-11-02)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r16.dck`.
Current read-only64KB PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r16.rom`.
The new coloured glyphs now replace the original logo throughout its sweep and
spread animation. Offscreen composition avoids visible erase/redraw blanking.
Original2019 level-one AY music loops during play. The rejected2019 effects are
replaced by eight arcade-derived speech2ay sounds across21event slots; effects
borrowA and leave musicB/C active. Exact secondary event assignments are provisional.
See `docs/r16_logo_music_arcade_sfx.md`, A/B audio and TEST_HISTORY042 onward.
Level one; physical hardware untested. Historical notes follow.

## r15: AY effects, faster rendering and coloured title reveal (2026-11-01)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r15.dck`.
Current 64KB read-only PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r15.rom`.
Adds original2019 AY effects with native joystick support, clean row/run skips,
a small live SRAM compiled-cell cache, resident terrain palettes and interruptible
graphics work. Final coloured title art now reveals in8-pixel strips.
Direct drawing saves12% SRAM /30% ROM cycles for the isolated ship test; the
production renderer remains buffered pending overlap/collision validation.
Fuse exposed an input IFF sampling race, now fixed. Level one only; hardware
untested; no new live512KB consumer. See `docs/r15_audio_rendering.md` and
TEST_HISTORY038 onward for measurements, diagnostics and exact output hashes.
Measured380-update window: SRAM11.69->14.05/sec (+20.2%), ROM9.86->10.41/sec
(+5.6%); diagnostic workload, not universal FPS.

Historical revision notes follow.

## r14: first-screen terrain initialization and scan speed (2026-11-01)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r14.dck`.
Current64KB read-only PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r14.rom`.
r13 did NOT fix the user's marked first-screen buildings. Its tests filtered out
those cells because their scrolling tags were already missing. Initial direct
terrain drawing now publishes native attributes, orientation and ROM category
metadata; sprite overlays still preserve retained background tags. Later streamed
terrain remains on its separate existing path. New source-derived coverage tests
reproduce r13 failures and require correct tags and actual initial pixel motion.

Both targets now skip clean empty-cell repairs; ROM also skips token decoding
for flat attributes. Identical80-update workload: SRAM10.69->11.33updates/sec
(+5.9%), ROM8.68->9.67(+11.4%). This is an emulator diagnostic window, not a
universal frame rate. Beeper waits, remaining grid scans and draw overhead still
limit performance. No new512KB consumer or nonblocking AY replacement is claimed.
All final emulator gates pass; level one and physical-hardware limits remain.
See `docs/r14_initial_terrain_speed.md` and TEST_HISTORY035-037.

Historical revision notes follow.

## r13: coherent building and ground scrolling (2026-11-01)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r13.dck`.
Current64KB read-only PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r13.rom`.
Supersedes r12's incompatible per-cell terrain colours. The bitmap moved correctly,
but arbitrary neighbouring8x1 palette pairs recoloured moving pixels. Terrain now
uses scanline pairs shared across both arcade material references and their vertical
mirrors. Quantized texture shifts unchanged; vertical colour variation is retained.
Horizontal colour freedom is reduced to keep mixed scrolling cells compatible.

Actual colour-motion regression over8000refreshes checks540240 SRAM/436456 ROM
terrain bytes: zero pixel or foreground-colour motion mismatches. An explicitly
diagnostic death bypass permits later terrain coverage; it is absent from outputs.
Unmodified ROM execution and all eight Fuse scroll phases also pass. Level one
only; physical hardware remains untested. See TEST_HISTORY033-034 and
`docs/r13_terrain_motion.md`. Old r12 cartridges remain for regression comparison.

Historical revision notes follow.

## r12: internal terrain gap, arcade materials and live title (2026-11-01)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r12.dck`.
Current read-only 64KB PicoROM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r12.rom`.
The internal black terrain column is fixed: native attribute publication excludes
staging column31, so its black front sentinel must not supply column30 colours.
The compositor now uses its real incoming background palette and hides staging31.
Arcade-derived material textures use per8x1 colours within the original terrain
profile, with both preserve and colour-emphasized conversion assets retained.
The chosen enlarged title is integrated with one-time bitmap/colour publication.
One16x16 orb now animates three original arcade cels; ordinary enemy materials
avoid the old repeating colour ramps. Other enemy geometry remains Spectrum-derived.

Both builds pass deterministic CPU and Fuse checks. Natural timing window:
SRAM114 updates/600refreshes (~11.4/sec), ROM80 (~8.0/sec), including restart pauses.
These are different evolving scenes, not a universal speed comparison. ROM remains
slower and further optimization is needed. Level one only; physical hardware untested.
See `docs/r12_graphics.md` and TEST_HISTORY028-032 for design, diagnostics and limits.

Historical revision notes follow.

## r11: small-enemy material regions and title alignment study (2026-11-01)

Current SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r11.dck`.
Current read-only64KB ECM: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r11.rom`.
The small raw level enemies now have pose-local shell/highlight/core colours,
replacing r10's repeated eight-line rainbow ramps. Source bitmaps/collisions,
large-boss materials, original menu and terrain fix are unchanged. Comparison:
`build/diagnostics/r11_small_enemies_comparison.png`.

A separate arcade-derived enlarged title study is at
`build/graphics/title_alignment/title_alignment_comparison.png`. Best tested
size239x39, x4,y101; maximum248x40 has more mixed-material8x1 cells. The protected
palette keeps neutral strokes neutral when blue shares a cell. Some incompatible
blue fragments must be sacrificed; scaling alone cannot remove every conflict.
This is a static asset/ROM comparison, NOT integrated into the moving menu.
The original arcade boss comparison and both styles remain available.

Emulator validation passes. Level one only; physical hardware remains untested.
See TEST_HISTORY026-027 for exact checks and remaining title integration work.

Historical revision notes follow.

## r10: building edges, multicolour enemies and arcade comparison (2026-11-01)

Current playable TSPico SRAM: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r10.dck`.
Current read-only64KB ECM cartridge: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r10.rom`.
Matching ROM-only `.dck` is in that folder. r9 is superseded for these tests.

The original pixel scroller includes a left spill cell omitted by r9 colour
publication. r10 colours it after the pixel shift, using the entering terrain's
palette throughout fine scrolling. Other mixed cells select source colours from
their actual shifted pixels. Pixel scroller bounds are reused; unchanged palette
runs skip work. Both targets pass all eight actual fine-scroll phases.

All55 nonempty level-enemy frames now use cached per8x1 colours, including the
large boss and16x16 frames formerly using flat source attributes. Boss head,
armour and vent materials are authored on Spectrum geometry. No collision bitmap
or original title/menu recolouring was introduced.

Original arcade boss conversion is retained separately at
`build/graphics/arcade_boss_compare/boss_comparison.png`: arcade RGB, ECM preserving
palette, ECM with chroma emphasis, and Spectrum r10. `.pixels`, `.colours` and
`.preserve_mask` assets are exported. Its separate64KB graphics viewer is a
comparison slideshow, NOT the playable port. Arcade geometry is not yet integrated
into r10 gameplay. Both comparison styles are kept.

Final natural600-refresh test1400-1999 counts104 SRAM r10 updates versus116 r9;
ROM r10 counts99. These are diverging gameplay runs including restart pauses,
not universal FPS or a speedup claim. Correct colour publication has a measured
cost; further speed work remains. Retrace96/97 refreshes passes without trails.
Both playable builds remain level one, with physical hardware testing pending.
Expanded512KB assets remain staging-only. See TEST_HISTORY sections023-025.

Historical revision notes follow.

## r9: terrain scrolling and genuine read-only ECM cartridge (2026-11-01)

Current writable TSPico test: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r9.dck`.
The r8 terrain colour drift is fixed: live ECM colours are republished with the
terrain at its publication phase, including the coarse-scroll ID transition.
All eight phases match current terrain attributes at frames1200 and1600.

Current read-only target: `build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r9.rom`
(65536 raw bytes), with matching `.bin` and Fuse `.dck`. All eight cartridge banks
are ROM; writable game state resides in HOME RAM. This derives from the r9 ECM
colour cache and compatibility/input baseline, rather than the older stock-colour
ROM. Original title/menu colouring and animation remain unchanged. Native joystick
and keyboard remain simultaneously active. See `docs/readonly_ecm.md`.

Both builds currently contain level one. Physical cartridge testing is pending.
The expanded512KB asset bundle remains staging data, with no live banked consumer.

Historical notes below describe earlier revisions.

# R-Type TS2068 project state

## 2026-11-01 - native level-one baseline and graphics milestone

Targets remain **both**: a native 64KB DOCK cartridge and TSPico with its
already-demonstrated complete **512KB RAM**. Graphics quality and richer ECM
colour are primary requirements. Keyboard and native joysticks should be
simultaneously active. Elite and the other reference projects are unchanged.

Current live ECM test: `build/ecm_native/RType_level1_ECM_TSPico_RAM_r8.dck`.
This is actual level-one gameplay with per-8x1 sprite colour and two foreground
colours inside originally solid strips. It requires writable DOCK1, DOCK2 and DOCK3
(the TSPico SRAM branch). It is **not a ROM-only PicoROM cartridge**. The initial
64KB SRAM image is not a claim that 512KB capacity has been integrated into the
game yet. Stock 64KB ROM remains a target; r2 stays byte-identical and original-colour.

The separate `build/graphics/RType_ECM_graphics_proof.dck` / 65536-byte `.bin`
remains the five-page arcade-art viewer. Full arcade sprite geometry and scene
conversion are not yet integrated into gameplay. r3 shades original Spectrum
geometry, with authored colour families; do not describe it as complete arcade art.

## Source findings

- `arcade/rtype.zip` and `rtypeb.zip` are byte-for-byte identical. All 20 CPU/
  graphics ROMs match MAME CRCs. Eight original captures provide genuine runtime
  palette, sprite and tile data. The extracted ship matches captured arcade RGB
  exactly. Five missing non-emulated archival PROM/PLD regions use explicitly
  labelled diagnostic stand-ins for local MAME; FF versus 00 produced 48 identical
  captures/data files. See README for the caveat; these are not authentic dumps.
- Standard Spectrum TAP contains eight level payloads totalling 94886 bytes;
  all eight match the +D wrapper. Native load addresses: part1=$7000 (21678 bytes),
  part2=$DD18 (8841 bytes), BASIC handoff=$85FD. Level headers name destination
  $C4AE; runtime ownership/overlays still require tracing, not address guessing.
- Torasoft TZX BASIC explicitly identifies a 1993 128K remix with trainer; do
  not assume its changes belong in the faithful baseline.
- Existing Spectrum128_PicoCartridge documents physical TSPico paging tests.
  Reuse the demonstrated banking/transfer work and the recent 512KB video path.

## Confirmed art direction

Lead with the more colourful, chroma-emphasized ECM style (user preference
after viewing the title sequence); keep palette-preserving ECM for comparison. Retain ordered and Sierra Lite alternatives; evaluate
moving-scene stability separately from still-image quality.

## Spectrum execution baseline

Unmodified standard TAP captured in Fuse 48K at frames 8000 and 14000:
REWIND SIDE 2 and STOP TAPE prompts respectively. Scripted Space events at
frames 8100 and 14500 reach the original post-level-loader return at $8634.
The full $4000-$FFFF RAM and pre-freeze CPU state are retained under
build/spectrum_baseline. At checkpoint: frame14500, SP=$FFFE, I=$84, IM2,
interrupts enabled. Original $8400-$8500 vector table already contains 257
bytes of $83; do not transplant Elite interrupt fixes without evidence.
This establishes a loader checkpoint, not native gameplay validation.

## Graphics implemented

- Decode 4096 16x16 arcade sprite tiles and two 4096-entry 8x8 tile banks.
- Capture real arcade palette RAM; assemble ship code34/palette0 and enemy
  code54/palette5 with native masks. These palette assignments are verified
  stage/frame samples, not universal assignments for every ROM tile.
- Generate eight finite masked phases with Sinistar's interleaved preserve-mask,
  pixel, attribute format. Row-coherent sprite pairs are quantized once, then
  shifted; padding is transparent. An arbitrary coloured background still needs
  shared-cell recomposition. A runtime scrolling sprite compositor is not built.
- Legal 8x1 ECM conversion with scalar serpentine Sierra Lite; ordered and
  coherent-row comparisons; legal 8x8 baseline; explicit 2.5x chroma-emphasis
  alternative. Both planes use the nonlinear TS2068 layout. FLASH is disabled.
- Stage sample: 8x8 baseline uses 9 distinct RGB colours, ECM/Sierra 14,
  colour-emphasized ECM 15. These counts are one sample, not a quality score.
  Title comparison demonstrates cyan/white shading gained with vertical pairs.

## Reuse and budget decisions

Use the TS2068 graphics skill's Sinistar experience: finite phases/masks,
retained composition with layer-order restoration, explicit dirty dimensions,
row palettes, and measured cache/publication costs. Reuse architecture; do not
blindly transplant its fixed addresses or game-specific palette restrictions.

The 32x16 sample poses cost 912 bytes for four even phases or 1872 for all eight.
Four-phase rendering is only a candidate if motion/camera parity permits it.
Full-game fit in 64KB remains unproven. The current viewer's 61440 raw picture
bytes plus 1830 code/table bytes are a bank-layout proof, not a game budget.

Optional opening animation: TSVideoCodec ECM, matching the arcade sequence or
an improved interpretation, separately budgeted for 64KB and 512KB. Not yet built.
Compare ordered dithering (existing TSPico streaming performance profile) with
Sierra Lite for preconverted art/video; measure visual quality, temporal stability,
storage and decoding/streaming time separately. No moving-scene quality claim yet.

Audio: reuse speech2ay's frame-based synthesis for gameplay; reserve blocking
DAC clips for appropriate pauses unless measured integration proves otherwise.
Its init/stop FF writes and AY register ownership need adaptation for ECM and
joystick coexistence. Audio integration has not started.

## r2 key-selection repair

Stock ROM baseline files: build/native/RType_level1_native_experimental_r2.bin
and .dck (unversioned aliases contain identical bytes). Original key redefinition
could immediately re-enter when final Enter remained held, clearing all six new
bindings. ROM wrapper $1B00 now waits for all keys released after completion,
then returns to the menu. No game workspace is reserved. Scripted reproduction:
r1 entered twice and cleared keys; r2 enters once, retains all six, starts with
chosen Space fire and reaches player update $94F1. Native input CPU and RAM
handoff regressions still pass. See history011 and verify_key_selection.py.

## Native level-one baseline implemented

`build/native/RType_level1_native_experimental.dck` and exact 65536-byte `.bin`
now run original level-one gameplay on Fuse TS2068. This is separate from the
five-page ECM art viewer. Gameplay still uses the Spectrum 8x8 colour renderer.
A deterministic capture of the original level-loader return supplies the initial
48KB state; this is not yet a native multilevel loader.

Copy-and-run bootstrap restores all 49152 HOME RAM bytes exactly, including
removing its temporary helper and screen stack. All general registers/flags
except dead A match the checkpoint; R/frame phase are deliberately not restored.
The original full IM2 table is retained. Native input is ROM-resident at DOCK0
$1A00, HSR=$01, avoiding game workspace entirely. Both joystick ports merge with
the selected keyboard on every poll; native fire also starts the game. Default
is the original redefinable Q/W/O/K/P/Space table, not a new joystick mode.

4096 real-Z80 input contract cases pass: all 1024 port pairs, keyboard neutral/
retained, interrupts off/on, Z flag, preserved DE/HL and balanced stack. Live
port1 right moves player X8->12; port2 left X8->4 at frame1820 after input during
1800-1809. Scripted runs reach frame8000, including deaths/return to attract.
This is not a level-completion or physical-hardware claim.

Static audit traverses 5469 instructions (partial, indirect/self-modified paths
remain). Verified unconverted tape CALL $0562 at $8F2A prevents claiming complete
multilevel support. Two CALL $0000 placeholders are self-modified dispatches,
not blindly replaced ROM calls. ECM plane $6000-$77FF overlaps live code/data;
audit lists 135 candidate references. Relocation/compositor work is next.

Build: `python scripts/build_native.py --native-input`.
See docs/native_memory.md for bank map, contracts, validation and limitations.

## r3 live ECM colour implemented (TSPico RAM prototype)

Game work buffer/code at logical $6000-$7FFF now lives in writable DOCK3;
HOME $6000-$77FF is independently owned by ECM attributes. Startup copies original
DOCK3 payload to HOME5 before repurposing it. DOCK1 is reused only after copying
its payload; it holds source-cell metadata for 786 headers/617 nonempty cells.

The original $8EA2 tile helper routes through ROM0 shader code. Colours follow
source-local sprite rows/cells, including all four mirror variants. Ship hull
uses cyan/white/blue; explosions use dark/bright red, dark/bright yellow and white.
Only originally fully set eight-pixel strips get a fixed checker texture with two
nonblack ink/paper colours sharing BRIGHT; partly transparent edges retain black.
No background-coloured rectangle is introduced. Original legacy attributes, ID
cache writes and function register/flag contracts are preserved. HUD is mirrored
per frame. Attract/menu returns to original mode0; gameplay selects mode2.

Live explosion frame984 contains five nonblack colours and two 8x1 strips with
two nonblack foreground colours. Earlier explosion pose4B at frame964 has eight
such strips. 512 source pixels in nontransparent cells match original occupancy.
Ship frame800 includes cyan+white in a single 8x1 hull strip. Actual HOME RAM is
decoded in explosion_comparison.png; its white reference uses the same silhouette.

Validation: full 8128-byte metadata comparison; 136 CPU tile tests across four
mirrors, both IFF states and original forced-attribute path; 4096 native input
cases; six-key selection -> play; native ports move X4 to X6/X2; frame8000 returns
to mode0 attract. Tile-hook cost measured1565-1700 T-states (IRQ-off samples,
mean1617.8), not a measured whole-game frame rate or physical timing result.

Build: `python scripts/build_ecm_native.py`. See docs/ecm_renderer.md.
BIN/SRAM image SHA256368FDF50E000D03FC510B3ADDE189EEEA5224415F0F3E137E69D0AB25C509780.
DCK SHA256DAD528A788C24414384781C2F4EBE0CE0A2AE14B4328FABE453994DB5E4B081B.
Physical TSPico deployment, ROM-only ECM memory relocation, full arcade artwork,
full mixed-cell RGB composition, full multilevel loading and enhanced audio remain.

## r4 trail/background repair (2026-11-01)

r3 left cyan8x1 strips after upward motion. Reproduced actual empty bitmap bytes
with coloured paper at40,76 and40,84; preserved under build/diagnostics/r4_trails.
Root causes: tile shim incorrectly hardcoded original self-modified8EBF base60
instead of honoring direct40/background60, and dirty repair8842 restored pixels
but did not restore ECM colours. The r3 tile contract tests had only exercised60.

r4 reproduces both original draw modes/flags exactly. DOCK2 is writable retained
background ECM attrs4000-57FF after its boot payload is consumed. Background-mode
draws write that shadow; direct draws write HOME ECM. Dirty-restore gate8883 copies
shadow colour for real background cells. For original ID0(empty sky), it clears
paper/FLASH while retaining legacy ink/BRIGHT, so old sprite paper cannot remain.
Original conditional branch, caller stack, flags, registers and collision ID are
preserved. No hit-detection branch or invulnerability setting is changed.

Regression flies fromY10 up toY2 and back through all previous cells, waits for
original deferred publication, then checks colours, dense residual bits and all
27 logical collision cells. r4:zero trails/stale IDs/deaths, pose2,Y10,X4,frames
1401-1565. Preserved r3 fails with strips40,20 and40,28; its collision IDs also0
and no deaths on this particular route. Therefore the reported death was not
proved to be collision with the visual strips; do not claim that causal link.
Actual before_after.png shows identical scripted route regions, with stars intact.

272 renderer CPU cases cover40/60 and four mirrors/IFF/override, four dirty-restore
cases coverempty/retained palette and IFF states,8128 metadata bytes,4096 input
cases, six-key selection/start and natural explosions pass. Frame8000 still runs.
Five-colour/two-foreground-strip explosion and512-pixel silhouette checks pass.
DCK descriptors2,3,3,3,2,2,2,2. Current SRAM BIN SHA256:
32832d91ae27f7b08b5a3ec8f674f8e5c5997b5e7e6f3f45422a7179e77e96cf
DCK SHA256:298bbdcc565ebeb07ec280098462d7e73bd54db2a2fa4072d3f63259ff765258

r4 files are versioned; older r3 retained for reproduction. Use writable SRAM,
not ROM-only PicoROM. Stock r2 ROM baseline remains byte-identical.

## Next implementation

1. Map renderer and writable data lifetimes; free the full ECM attribute plane
   without corrupting game code/data. Compare the 128K remix bank usage.
2. Extend the native baseline with level loading and broader compatibility audits.
3. Integrate one scrolling section and masked actors, with composed ECM cells,
   background repair and measured raster/frame budget. Preserve collision logic.
4. Budget original/converted level content for 64KB; use the proven 512KB TSPico
   storage/cache system for the enhanced target.
5. Add effects/music and optional intro after gameplay performance is measured.

Physical tests and complete-game validation remain outstanding.

## 2026-11-01 - verified Goodboy/Tiboh 2019 audio source

Actual RTYPE_GT.SCL release downloaded, checksummed and booted in isolated Fuse
Pentagon/TR-DOS. Its menu explicitly offers MSX/CPC sounds. Intro bank3 and game
audio bank7 extracted; native AY writer and game tune/effect hooks verified.
See docs/goodboy_tiboh_audio.md for provenance, addresses and integration limits.
This is research, not integrated audio or a new cartridge build. Full tune/effect
inventory, branch mapping, register traces, 50-Hz scheduling and TS2068 joystick
coexistence remain to implement/verify. Existing r4 gameplay outputs unchanged.

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



## Current full-game candidate — r23 (2026-11-02)

The TSPico512 build now actively runs all eight native levels with eight level AY songs, arcade-derived boss assets, per-level themes/group variation, M music control and selected death65. Native ending/restart works in deterministic testing. Download/use build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r23.zip; copy RTYPE to SD root and load RTFULL.TAP. Raw eight-region image: build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r23.ram512. Image SHA256 a2133a307bfdff576dc7590403d6dda322d29d75a4c38efe9936772fe7d0db02.

All-level sustained gameplay, 10416 boss/frame/clip/flash comparisons, source-exact music loops, M/SFX coexistence, eight MEMDOCK transitions, ending/restart, full SD loading/readback and negative alias control pass. Reports are under build/fullgame; docs/fullgame_r23.md explains exact scope. Progression tests use diagnostic victories/death bypass, not normal boss playthroughs. Physical hardware remains untested. Remaining eight extracted music entries are prepared, not event-selected; boss art retains native AI/cell envelopes and is open to visual refinement, especially Gomander's conservative body palette.

scripts/build_fullgame.py reproduces and validates this separate release. Normal builds still reproduce accepted r22 exactly; its64KB read-only PicoROM remains level-one only. Do not substitute .ram512 for .rom/.dck or describe r23 as a standalone64KB cartridge. Earlier statements that all other level assets or512KB consumers are staging-only are superseded for this r23 TSPico candidate; earlier r22 coverage statements remain correct for r22.


## Current title/text fix — r24 (2026-11-02)

Use build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r24.zip for all eight levels with protected menu text and the new retained delta title. Full image SHA256 a3a23d3067c5da8d434c46c8874396c3e067906855890acdd8342a49938a174b. Read-only level-one output: build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r24.rom (.bin/.dck also); flat ROM SHA256 0ac6250db0d99276456a558b2c36afb987f3709eea6551c260a9e8ccf6cea041. Level-one SRAM title preview: build/ecm_native/RType_level1_ECM_TSPico_RAM_r24.dck.

Stars no longer erase the top instruction lines; copyright is guarded without overwriting the IRQ grid boundary. Reusable shifted suffixes replace narrow old/new windows, settling final multicolour art as letters separate.116 states/3.762 emulated seconds vs46/4.393 previously. All pixel/colour states, repeated stars, Fuse text captures, ROM writes, sprite/music/joystick/IRQ and full-game regressions pass. Physical hardware remains untested. Both64KB and512KB target limits remain as documented above.

Docs: docs/title_delta_r24.md and docs/fullgame_r24.md. Build with RTYPE_TITLE_DELTA=1; accepted r22 defaults and r23 versioned releases are preserved. Preview: build/diagnostics/title_delta_r24/title_delta.gif.


## Current full-game release — r25 starting-level selection (2026-11-02)

Use build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r25.zip. At the title, press1..8, confirm "1-8 LEVEL n", release, then press joystick Fire or keyboard0. Default1; preference persists across new games. The choice is applied only to new games, not ordinary stage progression or respawns. The high-score page is left intact. Full image hash 885566b16ffa128b50b3c37afe1040d50d3c0d740bcf16245ff7b02dae2593c7; ZIP hash e0d834b0ac9905a2bdc00eda81dc8a0127503fc9a22299dd04d519ee45f3f301.

All eight keyboard-selected starts run140 gameplay updates with matching level headers/palettes; keyboard0 starts, no-start-on-number, indicator/page safety,10416 enemy cases, normal progression, ending, preloader and r24 title regressions pass. Hardware untested. ZIP also includes eight single-level Fuse preview DCKs (choose the file; no next-level loading after victory). Full number selection requires the512KB TSPico package. The64KB read-only r24 build remains level-one only.

Build flags: RTYPE_TITLE_DELTA=1, RTYPE_LEVEL_SELECT=1. Source: src/fullgame_level_select.asm; reproducible image builder/publisher and scripts/validate_level_select.py. Details and scope: docs/fullgame_r25.md and TEST_HISTORY061.


## L2 display artifact investigation (2026-11-02)

User sees static blue zones and faint title residue in Fuse Level_2.dck. Same source cartridge is clean in native screen RAM, TSRun raster output, and Fuse1.7/1.10 recorded FMF frames. Visible GUI/scaler/cache artifact is suspected but not confirmed. No terrain edits made. Diagnostic build: build/fullgame/previews_r26/Level_2_clean_redraw_r26.dck, SHA256 f2722a6c92954e2881225f4567b8001ebf9bdd0943b251868e57c3b91f00422a; it forces one complete black video refresh before ECM, with scenery/collision unchanged.8000refreshes and scripted Fuse1.10 pass. User-visible resolution remains to be confirmed; this is not a published full-game r26. r25 and r24 read-only files remain unchanged. See TEST_HISTORY062 and diagnostic README.


## Current full-game release — r27 retained-palette fix (2026-11-02)

Use build/fullgame/RType_TS2068_ECM_fullgame_TSPico512_r27.zip. Corrects the actual L2/L4 blue-rectangle bug: enemy dictionary IDs were being restored/scrolled as Spectrum attributes. Dedicated retained tags plus native fast colours now decode every8x1 row correctly; applied across all8 levels. The r26 clean-redraw diagnostic is superseded. Image SHA256 741ad3721c27166265d4c260235f10b8919f9f36e9ee5951702c35135ddc87a1; ZIP 8b25d331c4ee16169d6401830ac6a127aa953c484fb48e9da532e6b55242b225.

Direct Fuse previews: build/fullgame/previews_r27/Level_2_palette_fix_r27.dck and Level_4_palette_fix_r27.dck (all8 present). Actual Fuse1.10 L4 capture424 blue-paper bytes before,0 after; L2 stress110 bad copies before,0 after. 23800 retained cases and all gameplay/boss/music/selector/progression/title/preloader regressions pass. Hardware untested. The64KB read-only r24 target is unchanged. See docs/retained_palette_r27.md and TEST_HISTORY063 for source bounds, exact tests, timing limits and hashes.


## L7 preview follow-up (2026-11-02)

Older r25 Level_7.dck reproduces blue rectangles; magenta was not reproduced in the sampled scenes. Current previews_r27/Level_7_palette_fix_r27.dck is clean in9 sampled native scenes and a scripted Fuse1.10 refresh2000 capture; BIN SHA256 32bf6bf34aa14f092c93d79a9acf83e44c6e50fe87411aaf5350009291000097. Provide that exact direct preview. User's screenshot file version remains unconfirmed; no new engine change made. Evidence: TEST_HISTORY064, build/diagnostics/l7_boxes, l7_rect_compare.json and Fuse probe_2000_joy_l7_{old,r27}.*.


## L8 contour palette planning (2026-11-02)
Offline planner scripts/l8_contour_palette.py detects per-scanline eight-pixel gaps, constrains reused/flipped tiles, and verifies all eight scroll phases. Candidate119/128 dictionary rows; zero planned shared-cell conflicts. Preview build/diagnostics/l8_contours/level8_contour_plan.png. Asset proof only: runtime terrain decoding/reversal/retained publication and native edge reconciliation remain, r27 playable files unchanged. See TEST_HISTORY065.



## Loading instructions overlay r28 (2026-11-02)
Updated disk package and level-one read-only cartridge: build/fullgame/loading_text_r28. Replaces obsolete tape rewind/start/stop instructions with neutral level-ready/read-data/wait wording, no device branding. scripts/build_loading_text.py reproduces from preserved r27/r24; same-length high-bit strings only,64 disk pages/checksums verified. Graphics remain r27/r24 respectively; no new gameplay/hardware validation claim. TEST_HISTORY067.



## Standalone preview completion r29 (2026-11-02)
Use build/fullgame/preview_end_r29/RType_standalone_previews_r29.zip or individual Level_N_preview_r29.dck / RType_level1_cartridge_r29.rom. Obsolete tape loader now displays PREVIEW COMPLETE / RESET TO REPLAY, with no cassette attempt after keys. Nine forced-entry runtime cases pass; display visually checked. Full disk r28 remains separate and all8 automatic gateway hooks are intact. This fixes the misleading r28 standalone load behavior; graphics unchanged. TEST_HISTORY068.



## Disk installation correction r30 (2026-11-02)
Use build/fullgame/disk_layout_r30/RType_TS2068_disk_r30.zip, extract to SD root preserving TAP/RTYPE. Public root cd / maps to /sd/TAP; older instructions incorrectly placed RTYPE at SD root, causing directory status03 before PAGE00 on reviewed firmware. All17 TAP files unchanged from r28; only installation paths/instructions corrected. Hardware confirmation pending. TEST_HISTORY069.



## Demand loading requested after hardware timeout (2026-11-02)
Physical PAGE17/3F thenE0 reported; exact phase unknown because UI can show preceding page during next mount. New requirement: relative-directory files, selected-level startup only, loading screen between levels, verified RAM cache and title-idle preload yielding at complete transaction boundaries. Eight per-level CODE streams staged/byte-verified in build/fullgame/demand_loading by scripts/prepare_level_disk_assets.py. Runtime integration is outstanding; no new playable loader or hardware fix claimed. TEST_HISTORY070.



## Normal-black display candidate r31 (2026-11-02)
Use build/fullgame/true_black_r31/RType_TS2068_disk_r31.zip or Level_N_true_black_r31.dck for normal-black display testing. Corrects palette and native retained restoration brightness, confirmed distinct BLACK/BBLACK in PicoVideo source. All56 sampled scenes across8 levels have zero exposed bright-black; all64 disk pages plus native progression/ending/restart pass. Reproduce scripts/build_true_black.py, verify_true_black.mjs, verify_true_black_release.py. Hardware confirmation pending;64KB read-only ROM not updated. Disk timeout/on-demand loading/current-directory improvements still pending. TEST_HISTORY071.



## Full disk restart fix r32 (2026-11-02)
Use build/fullgame/restart_r32/RType_TS2068_disk_r32.zip. Missed native load callers8631/92B8 now route through0A08, like normal stage transitionC2A3. Old higher-level game-over tape-entry failure reproduced; all8 selected-level game-over/restart cases record zero tape entries. Full progression/ending/restart and64 disk pages/checksums pass. Preservesr31 normal black. Hardware confirmation pending; separate loader/art/64KB work remains outstanding. TEST_HISTORY072.



## Open level3 crash report (2026-11-02)
User reports intermittent corruption/freeze/death after repeated play. Latest r32 natural-collision stress60000frames and late-wave25000frame run did not reproduce a persistent failure on sampled checks; exact build/platform and respawn/new-game distinction requested, pending. Scripts stress_level3.mjs / stress_level3_late.mjs; diagnostics level3_crash and level3_late_waves. No speculative fix published. TEST_HISTORY073.



## Per-level disk loading r33 (2026-11-02)

Use build/fullgame/per_level_r33/RType_TS2068_per_level_r33.zip. Put RTYPE anywhere
under TAP, navigate into it, and load RTFULL.TAP with all companion files beside it.
Startup loads only level1; selecting/advancing levels reads the relevant LEVELnn.TAP
with level/file/page progress and step-specific errors. Relative current directory,
8-stage progression/ending/restart, selected1/3/8 replays, code/stack/state preservation,
CRC/alias/timeout/missing-file controls and72 packaged asset pages pass modeled tests.
Reproduce python scripts/validate_demand_disk.py. Docs/per_level_disk_r33.md and
TEST_HISTORY074 detail memory and validation. Physical confirmation pending.
Idle-title prefetch/caching, minimal asset packing,64KB ROM work and the real-machine
level3 respawn-corruption investigation remain outstanding. Earlier packages preserved.


## Eight resident level cache r34 (2026-11-02)

Use build/fullgame/cached_levels_r34/RType_TS2068_cached_levels_r34.zip. Loaded levels
keep separate regions0..7; all8 revisited without further disk I/O in modeled tests.
Inactive rendering chunks provide loader/workspace scratch and are rebuilt on entry.
Fast path polls a per-bank readiness tag; selected3/8 replays, full progression,
ending, second8-level circuit, native-code/workspace guards and error controls pass.
Reproduce python scripts/validate_cached_disk.py. Details docs/resident_cache_r34.md,
TEST_HISTORY075. Physical confirmation and idle-title prefetch remain pending.

L2 emergence report remains open: user confirms PicoVideo, native output unverified.
1848 primitive direct/background clipping cases match source; actual corrupt pose
not reproduced. See TEST_HISTORY076 and diagnostics/l2_emergence. No creature fix
claimed. Level3 real-hardware life-loss/continue report also remains open.


## L2 mirrored spawn fix r35 (2026-11-02)

Latest disk package build/fullgame/spawn_fix_r35/RType_TS2068_spawn_fix_r35.zip.
Photo matched precisely to bad HOME5D00 bit-reversal table containing high-score
text. Native mirrored descriptor32/33 corrupted; primitive tests had masked it by
injecting the correct table. Rebuild table on every native gameplay initialization
via ROM0DC0 wrapper around86C3, CALL1485 patched in all regions. Normal L2 probe
and complete8-level cache/restart/error gates pass;3725 live table checks across
progression/restarts. Compare image diagnostics/l2_spawn_r35/table_comparison.png.
Reproduce python scripts/validate_spawn_fix.py; TEST_HISTORY077. Hardware retest
pending. Replace entire RTYPE folder. r34/previews/64KB ROM preserved. Separate
level3 life-loss/continue freeze and idle prefetch remain open.


Stuck-down hardware report confirmed onr34 (TEST_HISTORY078). Natural40000refresh
neutral-input runs: r34 6997returns/35ship starts andr35 6879/33, no phantom
directions, one exhausted-credit restart each. No input fix claimed. R35 repairs
shared reversal table, but default keyboard decoder does not use it. Need physical
r35 retest to distinguish remaining issue; do not attribute report to r35 regression.


## Hidden transitions r36 (2026-11-02)

Latest disk: build/fullgame/transition_fix_r36/RType_TS2068_transition_fix_r36.zip.
Old hidden-screen helper at7800 was visible as secondary attributes; exact bad
write reproduced. Helper moved7B00; secondary attrs stayblack, loading/title screens
prepared before reveal, cold copied bitmap/attrs cleared. Retainsr35 creaturefix
and8resident levels. All8progression/ending/cached circuit, selected3/8restarts,
visibility assertions and diskerror gates pass. Reproduce validate_transition_fix.py.
Diagnostics transition_r36; TEST_HISTORY079 includes intermediate stall evidence.
Hardware retest pending; stuck-down andL3freeze still open. Previews/ROM unchanged.


L3 hardware photos12824/12825 (probablyr35) show dotted sky rows and left magenta
block; music continues, movement unavailable. TEST_HISTORY080. Currentr36 selected3
17000refresh captures reach matching giantship entrance without reproduced fault;
large-sprite clipping and26native-vs-optimized background comparisons pass. R35
keyboard/natural-death45000refresh stress has no persistent reproduced stall.
No new package/fix claimed. Need actual hardware reproduction evidence; leaveopen.


## Hardware debug r37 (2026-11-02)

Use build/fullgame/debug_key_r37/RType_TS2068_debug_key_r37.zip for diagnosis.
Caps Shift+D onlevels2-8 captures interrupted PC/SP/registers and controls/render/
bank/audio state from IRQ, then freezes readable screen. Photograph and reset;
not resumable. Chord ignored onlevel1 BOOT region. Exact synthetic and actual
frame-IRQ stuck-loop capture tests pass; all8cache/progression/restart/error gates
pass. Reproduce validate_debug_key.py. Docs/debug_key_r37.md; TEST_HISTORY081.
R37 restores BOOT palette/title source assets incorrectly zeroed byr36. Hardware
L3corruption and stuck-down still open; diagnostic is not a claimed crash fix.


## Hardware snapshot/RAM replay r38 (2026-11-02)

User confirms R37 game not frozen; PicoVideo only, says latestfirmware. PCphoto
is18DE normal enemycolour classification; neutral input. ATTR/DRAW r37 fields
were wrongly read through DOCK4; fixed viaHOMEF910 helper inr38. No crashproof.
Use build/fullgame/debug_ram_r38/RType_TS2068_debug_ram_r38.zip: Caps Shift+D,
photo state, Space, photo RAM redraw, reset. Captures/replays actual bitmap+ECM
byte-exact with audio/game stopped. Levels2-8. Fullreplay/cache/error tests pass;
hardware comparison pending. TEST_HISTORY082/docs/debug_ram_r38.md. Faultopen.


## Completed-frame diagnostic r39 (2026-11-03)

12829/12830 user confirms artifacts survive r38 Space RAM redraw. PC8D43 normal
mid-sprite copy, controlsneutral, validrender mode. Actual captured planes contain
lines, but stillneedexclude mid-update composition. R39 latches Caps Shift+D and
captures after fullmainframe (expectedPC868F), then Space RAM replay asbefore.
Latestdiag build/fullgame/debug_frame_r39/RType_TS2068_debug_frame_r39.zip.
Register/boundary/replay andall8cache/restart/error gates pass. TEST_HISTORY083,
docs/debug_frame_r39.md. No graphics fix claimed. R38 remains better if mainhangs.


## Retained bitmap initialization candidate r40 (2026-11-03)

User confirms persistentlines afterfinished drawing; do not request r39 repeat.
Latest gameplaycandidate build/fullgame/retained_fix_r40/RType_TS2068_retained_fix_r40.zip.
Fixes missing clear of5120retained playfield pixels ongameinit, preserving every
interleaved workspace byte. Oldpoison5102nonzero vsnew0 across8levels. Native
30000refresh replay52starts/51deaths andall8cache/restart/error checks pass.
No per-frame cost. Artificial invulnerability lateprobe diverged; not a valid
proof of playability/fix. TEST_HISTORY084/docs/retained_fix_r40.md. Hardware lines
not yet confirmed resolved; fullreported symptom not reproduced in deterministic RAM.


## Rocket ROM-write root cause fixed r41 (2026-11-03)

Latest gameplay build/fullgame/rocket_fix_r41/RType_TS2068_rocket_fix_r41.zip.
Beep/motor clue led to reproduced native9C3E LD(BC),A with coordinateBC1415.
Spectrum ignores ROMwrites; writableDOCK0accepted them, altering renderer7800
destination toFD00 and later overwriting IRQ. New9C3C guardFCF8 ignoresBC<4000
while preserving legitimate timers, projectile record and exact A/flags.
Oldfirstwrite6757/crash7478; fixedsame17000route passes60blockedstores, unchanged
renderer. All16384ROMdestinations/all256flags/nativeprojectile andall8cache/
restart/error gates pass. TEST_HISTORY085/docs/rocket_fix_r41.md. R40initonly
was insufficient; previous longdivergence actually exposed this rootcause.
Hardwareconfirmation pending. Do not ask for redundant RAM/finishedframe photos.


R41follow-up memory-write audit: partial5483instruction listing528writecandidates;
twoBCstores9C3Efixed/BF3Cstar; no newconfirmedbug. All8stages+cachedrevisits3406
DOCK0immutabilitychecks pass. Assertion retained inrocket_fix_fixture futuregates.
Docs/write_assumption_audit.md givescoverage gaps andlessons; TEST_HISTORY086.
No binary/ZIP change. Do not present this as exhaustive allweapon/code coverage.

Enemy visual trials (2026-11-04): build/graphics/enemy_sierra_trials/index.html compares23 existing arcade-derived components across8levels,115 native-size Sierra Lite alternatives with gamma/saturation/hue-preserving/row-coherent choices. Preview only; no game ZIP change, no new animation integration or timing claim. TEST_HISTORY087. Existing L8 per-scanline >=8px gap plan remains offline; additional terrain integration outstanding.

User selected enemy treatments saved assets/enemy_art_selections.json (TEST_HISTORY088). New geometry trials at build/graphics/enemy_geometry_trials/index.html correct whole-tail/multiple-projectile source compression for L1#16/L3#101. Preview only; r41 playable unchanged; shared palette packing and runtime validation pending.

## Native boss preview r42 (2026-11-04)

Latest playable candidate build/fullgame/boss_preview_r42/RType_TS2068_boss_preview_r42.zip. During gameplay B,release,B restarts near current boss via fullECM/native encounter setup; held keys do not repeat. Levels3/6 use giantship/maze entrance to preserve setup. All8boss artworks rendered across700updates afterjump; full8cache/progression/ending/restart/error and72pagepackaging checks pass. Physical confirmation pending. Graphics remainr41; approvedSierraLite artwork not yet integrated. TEST_HISTORY089/docs/boss_preview_r42.md. User prefers1.2/1.3/1.5 spritegrowth; new offline comparisons build/graphics/enemy_geometry_trials/modest_scales.html separate content size from8pixelstoragepadding.64KBcartridge unchanged.

Level5 material trials: build/graphics/level5_material_trials/index.html compares72 alternatives across4components (six colour treatments at1.0/1.3/1.5), with green/red and turquoise/red constrained ECM pairs plus restrained source-preserving gamma options. Offline only; TEST_HISTORY090. No playable package/art change.

Level5 r42 rectangular animation report confirmed in-game. Controlled actualZ80 overlap test reproduces native cell-priority clipping (37 second-component pixels suppressed,0earlierpixels erased), not exact reported frame. build/diagnostics/level5_overlap/index.html compares native proof and offline masked-group/finalECM composition experiment. No gameplayfix yet; TEST_HISTORY091. Need combined visual composition and single shared-cellpalette decisions without changing collision semantics; masksalone insufficient.

User clarification: white/grey boss animation has black-edged rectangles;091syntheticcelloverlap NOT confirmed cause. New solid shading previews build/graphics/level5_solid_trials/index.html have32options,1.3/1.5scales,zero black interiorpixels/noerror diffusion; may flatten some detail, further refinement needed. TEST_HISTORY092. r42unchanged, reported animationbugopen.

## Selected level5 core artwork trial r43 (2026-11-04)

build/fullgame/selected_art_r43/RType_TS2068_level5_art_trial_r43.zip packs selectedsource/gamma1.35 96x96 level5descriptor8. DoubleBpreserved; allotherlevelart unchanged.113dictionaryrows,1104assetbytes EFA1..F3F1belowAY;888rendererchecks,700updatebossprobe,all8cache/progression/ending/restart/error/72pagespass. Physicalconfirmationpending. Isolatedcore draw1.94xoldcost; explicitlyarttrial, notspeedupgrade. Rectangularanimationfault unresolved. TEST_HISTORY093. Movement/firingstillopen:8pixelnativecoordinate/collisionarchitecture;release-triggerednormalshot canmissquickedgesduringlongupdates. docs/movement_and_firing.md; no input/physicschanges shipped.64KBROMunchanged.

Arcade equivalent ofphoto12860 identified: Bellmite'sgreen/greyred-nodeorbs, frame44700,ROMcodes0B94/0B96/0BA0,palette6,32x32sources reusedfornative9..26. Existingr43modifiesseparatecore8only. Evidence diagnostics/level5_arcade_identity. TEST_HISTORY094. Native1pixelmovementstillpending; browser-onlyphaseproof/cache2304bytes andlogiccheckspass, notfullgameimplementation.

## Bellmite actual sphere frames r44 / native motion proof (2026-11-04)

Latestcolourtrial build/fullgame/bellmite_orbs_r44/RType_TS2068_Bellmite_r44.zip. IMPORTANTcorrectedmapping:liveboss spheresare30..33,not9..26. Replacedactualframes32x32arcadegreen/red;3dedupassets432bytesF3F1..F5A1,127dictionaryrows;prior96corekept.888rendererchecks,700updatebossprobe,8stagecache/progression/ending/restart/error/72pagegatespass. Nativecaptureboss_live.pngshowstruecolourbutblackcellcutsremain;compositorunchanged. Full-game movement/firing/speedstillnotimproved. TEST_HISTORY095.

StandaloneactualZ80onepixelmovementTAP build/diagnostics/native_pixel_movement/Pixel_movement_TS2068.tap supportsQWOK+bothnativejoysticks;emulation20refreshpositions41..60pass. NOTfullgameintegration,noenemies/shooting/collision. Hardwareconfirmationpending. Full1pixelcollision/shot/renderintegrationandfasterplayremainopen;browserproofnotcompletion. Earliernativeorbmappingclaims9..26aresupersededbylivetrace.

Nativepixeltestuserreportsmoothbutflashing;newdeltaTAP build/diagnostics/native_pixel_delta/Pixel_movement_delta_TS2068.tap avoidsvisibleerase,composesinscratchthenonlypublishesXORbitmapchanges/changedECM.825Z80byte-exactframes/commonbitsnevererasedpass,stationary0writes,max40visiblewrites/framevsold128. Nativecontrolsretained;hardwareconfirmationpending. Standaloneonly,notfullgame1pixelintegration. TEST_HISTORY096;oldTAPpreserved.

Hardwarephoto12861confirmsr44colourimprovementbutblockcutsremain. Capturedactualsample200spherepositions/flips:24sphereparts+coreallretainedmode60. Newofflinefeedback build/graphics/bellmite_detail_feedback/index.html comparesA/B/Csource-guideddetailandmaskedgroupcomposition,legal8x1/zerointeriorblackassertions. Notnativefix/dictionarypacked/performancevalidated;coreomittedexplicitly. TEST_HISTORY097. Requestuserstyle/overlapfeedback;latestplayabler44unchanged.

Userapprovednativedeltamovementfeelandauthorizesfullgameintegration;keysQAOP(Qup/Adown/Oleft/Pright). CorrectedstandaloneQAOPTAP diagnostics/native_pixel_qaop/Pixel_movement_QAOP_TS2068.tap;explicitphysicalmatrixkeytests+825framecomparisons/nativejoystickspass. TEST_HISTORY098. Full-gamefractionalcollision/shot/renderintegrationstillpending;doNOTclaimstandalonefinishesrequestoraskmotionapprovalagain. r44gameunchanged.

UserapprovedBellmiteBdeepshadows,requestsarcade-likeedgehighlighting. assets/bellmite_style.jsonrecordsapproval. NewofflineDsubtlesource-guidedwhite/cyanrimandEstrongerrim comparisons build/graphics/bellmite_rim_feedback/index.html;Bretainedbaseline;legal8x1/alphacheckspass,visuallyinspected. TEST_HISTORY099. r44gameunchanged;nativecompositorandfull1pixelintegrationstillpending.

Darkbluetop/right1pixelrimoptions build/graphics/bellmite_blue_rim_feedback/index.html: Gstrictlegalpartialrim,Hplanned1pixeloutlineexpansiononselectedscanlinesforbytealignment,Fcontinuousspillcomparison. Hprovidesmorerealright-edgebluewithoutwidecellspill;alloffline8x1/alphacheckspass,visuallyinspected. TEST_HISTORY100. No nativegamechange.

Userconfirmed darkblueedgesoverwhite. Recordedassets/bellmite_style.json;newJcomparisoninblue_rim_feedbackreplacesresidualwhiteedgepixelswithblue,retainsinteriorhighlights,all3cels0whiteedgepixelsafterlegalfit. TEST_HISTORY101. Offlineonly,r44unchanged;doNOTaskbluepreferenceagain.

PlannededgeHapprovedbyuser;recordedassets/bellmite_style.json. ConservativeKlocalcontourrefinementatgraphics/bellmite_planned_edge_refined/index.html trimsoneedgepixelon0/1/4selectedrowsacross3celsforlegalnarrowbluecontrast,withoutred/yellownoderecolour. TEST_HISTORY102. Offlineonly;Hbaselinepreserved,r44gameunchanged.

CombinedapprovedHplanned-edgespheres+actualselected96pxmechanicalcorepreview graphics/bellmite_complete_preview/index.html/comparison.png. Leftcapturedpositions/layerorder,rightillustrativecutawaywithfrontpartsdeliberatelyhidden. TEST_HISTORY103. Offlineonly,notnewgamebuild.


Native compositor experiment r45 UNRELEASED: approved H spheres packed exactly with dedicated row data, core retained. Interrupt-bank and bitmap-address faults fixed; bank-aware700-actual-update boss test passes41089refreshes after modular tile-index optimization (was43731). Still much slower thanr44 and shared-cell palette inheritance remains a visual compromise. No new ZIP; latest releasedr44. Diagnostics delta_benchmark/sample_200.home.png includes intermediate white-flash failure and later H candidate, recordedTEST_HISTORY104. Full-game1pixel/QAOP integration remainsunfinished.

TSVideoCodec/relocatable delta investigation implemented native paired-plane publisher src/relocatable_delta.asm.6072 actualZ80placement/phase/direction tests pass; matched64playertransitions7036.9cycles vs10461.9existing publisher(32.74%reduction), destination rows included.192templates20280bytes, centrecardinal3120. Fullscreen60consecutivebossframepairs: sparse117410cycles,XOR151459,rawLDIR258088,fullcompare801186; decoder/publicationonly,notgameFPS. docs/relocatable_deltas.md andTEST_HISTORY105. Requires proper local background/overlap composition beforegameintegration; not another releasedmovementdemo.


Future follow-up requested by user (2026-11-04): expand relocatable object deltas as a reusable game concept and consider a future TS2068 AI skill update. Checklist and evidence limits: docs/relocatable_deltas.md, Future expansion and TS2068 AI skill candidate. No skill files changed.


## Current integration work (2026-11-04)

R47 actual full-game pixel candidate now implemented, not merely standalone: src/game_pixel_overlay.asm, game_pixel_gateway.asm, game_pixel_irq.asm; build_pixel_game.py. Native game-defined keys preserved (no fixed QAOP); both native joysticks merge. One-pixel movement is IRQ-driven, paired-plane damage publication preserves shared bits; snapshot-backed local world patch allows movement through scene-copy work. Pixel hit flag feeds real death/respawn; normal releases captured/allocated between main updates; charged beam retained. Native weapon sprites/AI still use rounded original character coordinates; no pixel-aligned weapon rewrite or constant-FPS claim. Three-pose standalone cache narrowed to centre pose for gameplay to fit bank7. Bank7 IRQ entry/exit mirrored; mapped attrs sections remain DI; busy main preparation allows audio IRQ without recursive overlay. Original stock64KB ROM unchanged.

New standalone relocatable-delta trial built at build/diagnostics/native_relocatable/Relocatable_delta_QAOP_TS2068.tap (QAOP only here), 64 centre-pose/direction templates6618bytes+128pointerbytes. Actual825 native byte-exact frames, both joystick ports, stationary0writes/sharedbits preserved.

R48 candidate build/fullgame/compiled_game_r48 derives frozenR47; only level5 changes. Bellmite precomputed row-pair caches1536bytes replace repeated source decoding/reversal; unowned core takes native fast path. 384 native sprite/flip/clip/owner/flash equivalence cases pass againstR47 bitmap+ECM;700 boss updates32341refreshes versusR4736820 on same route (about12% less elapsed emulated time), still more costly than older unmasked artwork. Latest published game stillr44 until final packaging. R47 all8boss routes700updates each/full8cache+ending+secondcircuit/error gates pass; selected restart test corrected to inject at main94F1 rather than arbitrary in-IRQ low-stack frame boundary. R48 final cache/package gates pending. Full history entry to follow on completion.


## Latest packaged build: r48 (2026-11-04)

Local deliverable build/fullgame/compiled_game_r48/RType_TS2068_r48.zip SHA256983a16c97845aa12bc9c32db09c0fa7b7d86986224f5893aaa486430f519076d. Includes full512KB disk game and TRIALS/Relocatable_delta_QAOP_TS2068.tap plus preceding baseline. Full game retains key selection; QAOP fixed only in standalone trials. Actual one-pixel gameplay/IRQ input and background-aware publication now integrated, with pixel collision/hit-to-real-death/respawn checks. Quick-release shot capture8presses->8shots and1held->1beam pass; original16-shot limit and rounded native weapon/AI coordinates retained. Centre ship pose only; no constant FPS or pixel-projectile rewrite claim.

Approved H Bellmite spheres and96px machinery core in actual payload. Cached row pairs1536bytes atDOCK4:8C00/DOCK7:F380 save decoding/reversal;384 native normal/flip/clip/owner/flash equivalence tests pass, caches/code bank remain intact. Boss700update route32341refreshes versusR4736820; still costly versus old unmaskedr44art. All8boss routes, full8cache/ending/secondcircuit(51556refreshes/16520code+reverseaudits/15guards), level3/8cached game-over restarts and four loader-error controls pass.72 packaged asset pages/hash/XOR/ZIP checks pass. validation_summary.json records byte-identical-region test reuse. Hardware validation pending. Earlier stock64KB read-only cartridge output is unchanged. docs/r48_changes.md and TEST_HISTORY107-110.


## Latest packaged build: r49 (supersedes r48, 2026-11-04)

Completed one-pixel game integration, selected-key/dual-joystick input, normal release capture, approved Bellmite artwork/core, cached row-pair composition and standalone relocatable-delta trial. r49 corrects HOME8000 metadata access before DOCK4 mapping, preventing debug-prefix corruption;384full ownership/coverage/foreground/cache cases pass. All8boss routes rerun700updates each; L5 31891refreshes. Full8levelcache/ending/revisit51563refreshes,128blocks,16481bank/reversal audits,15guards. Package72pages/hash/XOR/ZIP checks pass. Game asks for keys; no forcedQAOP. Physical validation pending; stock64KB cartridge unchanged. See docs/r49_changes.md and TEST_HISTORY111.

Deliverable build/fullgame/material_game_r49/RType_TS2068_r49.zip SHA256 c22a9b7f5cf1713e9b7e47131538bd87a235d16b2a6aa5a5306203e3924fe06f


## Latest packaged build: r50 (2026-11-04)

R50 fixes player travel speed (fine1px, held3px/publication), variable damage height/scratch, L1 snake single-joint geometry and links, and title garbage caused by bank7 atlas/player overlap. Title now builds suffix/phases in owned scratch; all116actual disk states exact with player-code/cache guards. Fullgame chosen keys/native joysticks preserved.894component ticks, actual controls/fire/death, all8bosses700updates, fullcache/ending/revisit and selected restarts/errors pass. Full progression 51348refreshes. Original64KB stock cartridge unchanged, physical validation pending.

Boss trials now included: native fixed-pose relocatable comparison (8poses/25parts,105cases) plus arbitrary independent-part interactive host prototype (100arbitrary arrangements verified through native Z80 publisher). The dynamic design handles overlap, cels, flips, depth, removals/clipping/backgrounds; composition/encoding remain host-side and are NOT integrated gameplay speedups. docs/r50_changes.md details architecture/limits and future skill note. No skill/reference project changed.

Deliverable build/fullgame/responsive_game_r50/RType_TS2068_r50.zip SHA256 f0092f0ba13893fbd0a9bd99c76ad12e1181b325b7a3cba1861b6540e6a0fd7c

Final r50 package hash after dynamic normal-black policy/test refresh: a8c8cd0eb86746c58453d812c5f4388531d168e88b8c75d41195c8df87d2715b. This supersedes the intermediate r50 hash above. Actual game binaries unchanged by this trial-only refinement.


## Latest packaged build: r51 (2026-11-04)

L5native shader now765bytes, skips fully hidden cells and streamlines unowned cache rows;384exact r50equivalence cases pass. Defaultcompact24px spheres/80pxcore restores sphere footprint and more room,384independent source/coverage/ownership cases pass.700updateboss elapsed32616→22938refreshes (29.7%less); captured25draw cost40.3%less. Optional32/96larger-artLEVEL05.TAP retains priorart and still saves15.7%elapsed. Compactfull8cache/ending/revisit rerun, all72page+alternate8page checks pass. OtherBOOT/levels/sharedcode identicalr50. Staticclearance15.45%more safe positions in sample, not fight completion proof. Stock64KBcart unchanged; hardware validation pending.

Deliverable build/fullgame/compact_boss_r51/RType_TS2068_r51.zip SHA256 4f0a8d25fb1ac7c4263576466b5b214a1d1fbaa4809f75e8ef0a8d42f5ffa174. docs/r51_boss_speed.md and TEST_HISTORY113.


## Latest packaged build: r52 (2026-11-04)

L8fivebossframes42..46 nowfineSierraLitebitmaps in48x32source slots, user A/gamma1.8 direction;37newpalette rows, otherenemiesprotected.1056allL8nativeflip/clip/flash/sourcecases pass. Playerfine1px thenheld5px,64rasterbackingpatch withsplitDOCK7pixels/DOCK2attrs,65byte damageplanes; empty-sky fastcache path. Actualtravel113vs78pixels/100refreshes; frozen-copyY23vs9. Fullchosenkeys/nativebothjoysticks/fire/death/title/snake/all8boss700/cache/restarts/errors pass. Fullresidentcircuit 53442refreshes. R51compactL5nativeoptimizationretained, matchingnewengine larger-artalternative independentlytested700updates. Normalblack and memoryownership/staticassetcontracts checked. Oldstock64KBROMunchanged; physicaltestingpending.

Deliverable build/fullgame/detail_motion_r52/RType_TS2068_r52.zip SHA256 6b00800321e74be3ce29d19c5e430d2a8706e4bd4d32ace3ea25b6a19e9cbae1. docs/r52_detail_motion.md and TEST_HISTORY114.


## Latest packaged build: r53 (2026-11-04)

Standard compact L5 input starvation repaired with bank/stack-safe interruptible visible-cell drawing. Active-game fire edges sampled even during busy/alternate IRQs; player publication budgeted to alternate IRQs, preserving scene budget and charge timing. Selected keys/both native joysticks retained. Matched L559->162player updates/480refreshes and3->8shortshots; all8levels8shots+1beam. L5covered rows skip source decode/blend; captured25draws2.48%lessCPU,1064->554decodedoverlaprows. Shared all8boss palette lookup about6-7%cheaper in5088exactnative draw cases. Art/dimensions unchanged. No constant worldFPS claim; L5sceneanimation stillslow.

Final serial gates pass:7565IRQ boundary injections,524288source pointers,384independent+384exactL5cases,894player ticks, chosencontrols/joysticks/fire/death/title116/snake/restarts/errors, all8boss700updates and full8residentcache/ending/revisit53389refreshes.72pages+ZIP/staticownedranges verified. Full-rate-publication candidate rejected from standard due sceneCPU tradeoff, retained locally as diagnostic. Stock64KBROM unchanged; hardware validation pending. docs/r53_boss_speed.md and TEST_HISTORY115.

Deliverable build/fullgame/boss_speed_r53/RType_TS2068_r53.zip SHA256 13e5f302e757ea5a9ae9559d56fde44bad4afd4a06340cafd9baa984e8e93563. Replace matching RTYPEfolder and reset before RTFULL.TAP; do not mix old large-art level files.


## Latest packaged build: r54 (2026-11-04)

Normal/spread projectiles travel up to3native steps (normal2->6cells) per world update, stopping at intermediate enemy/terrain, one original final draw/hit. Friendly IDs ignored. Original projectile update clock/charged-beam/other-pool timing retained. Live-world ship/exhaust stale-background spill reproduced and fixed using exact coverage on publication and retained cleanup.128phase/direction/fine+held live-change cases pass. No new flame animation claimed; hardware symptom clarification pending. Player movement settings/input preserved; final L5158ticks vsr53162/480refreshes,8shortshots+1beam,worldupdates10. Final componentmean/max11346.3/49928; noncopy fast paths retained after rejecting slower prototypes.

New helper125bytesF080, engine2427bytes; coverageF740,damagescratchF781,cleanWORLDmovedF83A with static bounds. Art/boss sizes/phasecache/joystick/audio/IRQbanklogic unchanged. Final frozen regionSHA+serial gates:7565IRQ,16slotcapacity,894player ticks,128changedworld,4088projectilesweep,native finaldraw equivalence, controls/fire/death/title116/snake/restarts/errors, all8boss700 and full8cache/ending/revisit53981refreshes;72pages+ZIP verified. Stock64KBROMunchanged, hardware pending. docs/r54_player_weapons.md and TEST_HISTORY116.

Deliverable build/fullgame/player_weapons_r54/RType_TS2068_r54.zip SHA256 315178184438410255074c62c53f2e8ade9641fb641c2e46b87d478e7b73fa6e. Reset/reload complete matching RTYPEfolder.


## Flame clarification (2026-11-04; r54 unchanged)

Resolved the pending symptom clarification: the separate flame-shaped sprite98 behind the ship is an original timer-gated launch/respawn/pickup effect. Native9577draws it only while7A98>0, decrementing that counter; zero intentionally skips it.10native timer/parity cases pass. Keep this disappearance behavior, distinct from r54stale-neighbour repair. Initial assertion that disappearance was unintended was corrected. Diagnostic-only sources/results under scripts/verify_thruster_timer.mjs and build/diagnostics/thruster_r55; no r55game built. Latest release remains unchanged r54, SHA315178184438410255074c62c53f2e8ade9641fb641c2e46b87d478e7b73fa6e. TEST_HISTORY117.


## Latest packaged build: r55 (2026-11-04)

Normal/spread bolts now independently IRQ-clocked/drawn, separate from boss/world and existing player publication phase. One8px native step/phase instead ofr54threeworldsteps/48pxnormaljump.21visibleopen-space positions vsabout3; bounded8active slots/phase withfair16slotservice. Exactvisiblebyteownership/normalblack cleanup and pre-world-copy erase; nativeglyph/ECMbyte checks, five directiontypes, fullcapacity/trail/starbits/nativehitonce/staleactor checks pass. Main-loopA490hit handoff keepsIRQoutofnonreentrantnative hit rendering. Chargedbeam/otherpools and timedlaunchplume unchanged.

Engine575bytes runtimeDOCK2:5880, coldDOCK7F100installedafterHOMEcopyandrestoredbeforecachebankleave. State5F80..5FFF, distinctprivateSP5CA0lowwater5C96. Player engine/settings/art/boss shaders/audio retained. Finalfrozenserialcomponent/7565IRQ/128liveworld/control/fire/death/title116/snake/restart/error/all8boss700/full8cacheendingrevisit55681refreshes pass. All8inputprofiles8shots+1beam. L5player155vsr54158/480refreshes,127projectilephasesvs9worldupdates.72pages/ownedranges/TAP/ZIPverified. No constantrate/hardwareperformance claim; physicalvalidationpending. Stock64KBROMunchanged.

Deliverable build/fullgame/projectile_clock_r55/RType_TS2068_r55.zip SHA256 7784e1643248b8faf87f5c80b33ff28d1a0b1f3cff6c2a8fefe4ea6094ff000d. Reset/reloadcompleteRTYPEfolder; no mixing older cached assets. docs/r55_projectile_clock.md and TEST_HISTORY118.


## Latest packaged build: r56 (2026-11-04)

StaleL5boss fragments around player reproduced/fixed. Unownedretained0/3cells cancarryoldbossgarbage; markingplayerdirty3publishedwhole8x8cells outsideexactshipmask. Sanitizeonlyunownedbytes in10x64backingpatch beforeoverlay, aligntop8rows, retainownedscene. ReuseOLD64cleanunderlay forcleanup; engine2423vs2427bytes, ordinarytickcostunchanged. OnlyE400..ED7F differsr55all9regions; playerfine/heldmotion, independentprojectiles, art/boss/audio/gates/cache unchanged.45nativecopycases695unwantedbytechanges->0;112mixed/edgecachecases preserveowned/outsidebytes. Two sweptstarbytesmissing recorded separately. Correctedzero-filledtestdatagenerator;128realvariedworldcasespass.

Final894playercomponent/7565IRQ/projectilecapacity/control/fire/death/title116/snake/restart/error/all8boss700/full8cacheendingrevisit56490refreshes pass. L5unshifted7/8shorttaps, one-frame-shift8/8; dedicatedfiretest8/8, shorttap heavy-draw timinglimitation recorded.72pages/strictownedranges/TAP/ZIP and separateall9rebuildverified. Physicalhardwarepending; stock64KBROMunchanged. docs/r56_clean_player.md, TEST_HISTORY119, diagnosticbefore/afterimages under build/diagnostics/player_ghost_r56.

Deliverable build/fullgame/clean_player_r56/RType_TS2068_r56.zip SHA256 2649ed1ae8be771e9f832c1c3f764186409c24620544ee51aa937bef0193f386. Reset and reloadentirematchingRTYPEfolder beforeRTFULL.TAP.


## Latest packaged build: r57 (2026-11-04)

L5/PicoVideo userclarifiesgenuineout-of-sequenceprojectile, notjustpause/resume. Exacthardwarebackwardframeunreproduced; emulatormemory/raster/painttracesforward. VerifiedIRQre-entryhazard fixed: input canreturnEIenabled, oldnestedpulsecorruptscontext; sourceguardblocksre-entryandrestoresmode/bank/SP. Cachedshotrepublish validateslive type/x/y; cleared/reusedslotcannotreplayoldposition. Boltsadvanceduringpreparation/hiddenworldcopy andresumeatcurrentpositiononly. One latestrelease, shortexpiry8capturepolls, busyIRQdispatch, nolatecatch-up. Actualrapid15pulses->15shots, queue0/noafterburst;8release+1beamtestpasses. Singleforcedflight238->54refreshes. Playerfine/heldsettings, r56unownedbackgroundfix, art/boss/audio/controlsretained.

Engines2431/640bytes, rawF4+AF'alternategateway96bytes; coldbank7F100..F37FexactlybeforeF380flipcache. Entry/exitguard08E2/0911 mirroredFD20, transitionreturn19FC. Finalfrozennested/L5raster/queue/flight/rapid/112cache/45copy/7565IRQ/894player/128world/control/death/title/snake/restart/error/all8boss700/full8residentrevisit59250refreshespass.72pages/ownedranges/TAP/ZIP/rebuildverified. ExactreportedPicoVideoeventstillneedsphysicalconfirmation; performance/inputworkloaddependent, stock64KBunchanged. docs/r57_shot_sequence.md and TEST_HISTORY120.

Deliverable build/fullgame/shot_sequence_r57/RType_TS2068_r57.zip SHA256 78163450c7385abac3fc844073254313aa9fbb0e4264e919eb3f8823986b96ce. ReplacefullRTYPEfolder, resetbeforeRTFULL.TAP.


## Latest experimental build: r58 L5 phase movement (2026-11-05)

User-requestedL5preshifttrial complete; standardrelease remainsr57. Separate build/fullgame/l5_preshift_r58/RType_TS2068_r58_L5_preshift_trial.zip, SHA256 bebe1f0acb9e0fb89ff769aa7f8f91e82271baa6ab9ca0019330d9ec4e94b387. Ordinarynative8pxL5steps now2px/axisperworldupdate,4horizontalphases+verticalrowrelocation,25parts,original24pxspheres/80pxcore. Larger scripted relocations retained. No newbossclock; matched700route37.14%slowerelapsed thanr57, so doNOTpresentasFPSspeedup/replacestandard automatically.

7152packed/9344expandedphasebytes warmed duringlevelinit, existing512KB, source-shadow/native-tail restoredexactlybeforecachedrevisits. Final256pixelcases+8IM2injections,700L5updates/25actors/16075motionsamples,controls/fire/death/title/snake/errors/order,actualboss-gameover-cachedboss andfull8cache/ending/revisitpass.72pages/strictownedbytes/ZIP/repro15filesverified. Otherbosscoverage200updates(1/2/3/4/6),700(7/8). All16framebefore/aftercapturesandnativeGIFs atbuild/diagnostics/l5_preshift_r58/index.html. Testhistory121/docs/r58_l5_preshift.md. Hardwarepending; r57archive,stock64KB,sourceZIPs/referencesunchanged. Nextperformanceopportunity:phase-specificcompiledcellplans, ratherthan repeatedcellmath/emptychecks.


## Latest experimental build: r59 L5 effects repair / prepared cells (2026-11-05)

r59 supersedes the r58 phase trial; r57 remains standard. Fixed proven DOCK1 phasecache/globalcolour-ID lifetime overlap: separate immutable617-tag/715-byte table DOCK7 E000..E2CA, redirectedL5nativepublisher0040. Sparks and nativeplayerexplosions byteexactr57 in2568comparisons (r58bad840/r59zero). Cellplans onceperpart +earlyclip/verifiedopaque rejection, privatebank2stack/I8F vectors, exactcoldsource restoration. Sizes24pxspheres/80pxcore and25parts unchanged. No changes tostock64KB/reference/sourceZIP/skills;otherregionsbyteexactr58.

Measuredheldinput player141->173/projectiles138->172 in480refreshes; componentmean17.8%lessCPU includingplanning.700bossroute36061->35862 only0.55%better;stillbehindr57=26295. Improvedinterruptopportunities,notnewbossclock/hardwareFPS. Actualdeath/respawn,700L5motion,256phase+96foreground,768clip+288foreground,16IM2,controls/title/snake/fire/error/order/restart,all8cachedprogression59443refreshes,72pages/strictownership/rebuild18files/ZIP pass.16frozenchecks. Hardwareconfirmationpending.

Deliverable build/fullgame/l5_effects_fast_r59/RType_TS2068_r59.zip SHA256 1e45543d1ed10dd4d4e2e3b38f00cbd7603e79dcd21b8e315cb3f3e04a5ba5b4. CopycompleteRTYPEfolder,reset,loadRTFULL.TAP;select5,B-release-Bingame. Keepseparatefromr57. Nativeeffectdiagnosticcomparison build/diagnostics/l5_effects_fast_r59/index.html (isolatedrenderer,notfullgame/hardware). Details docs/r59_l5_effects_fast.md andTEST_HISTORY122. Future optimization must include effectpalette readers/cachelifetimes and actualdeath/respawn paths, notboss-onlyscreenshots.


## r60 work in progress (2026-11-05)

No r60 package yet. See TEST_HISTORY123 and docs/r60_boss_motion.md. Generic2pxbosses,12L5spheres,4posearcadewalkers implemented experimentally. Terrain-safe renderer andrawIRQ fixes pass2084pixel/restorationcases andIM2checks. SustainedL1..5pass;L4verycostly63794refreshes/700updates,L5only1.6%fasterthanr59.L6historyreset discovered;actor-keysourcefixpendingrebuild. Currentfrozenregressionsrunningonpre-history-fixbinary;donotmutateimagesuntilrunnerexits. Lastpackagedr59unchanged.


## Latest experimental disk trial: r60 (2026-11-05)

Packaged build/fullgame/boss_motion_r60/RType_TS2068_r60.zip SHA256458a82915addb4ad98ebc8fe1558713807037fc1da32ecc239304cae56a2cb60. Genericmovingboss2pxphases;L1stationaryboss/L3terrainshipunchanged. L5actualsphereeventspawns24->12,core+12verified,700route35862->25606refreshes(-28.6%elapsedvsr59). L4phasefittingcostly63800refreshes/700;notageneralFPSimprovement. Held480player163/projectile158vsr59173/172;8shots+1beam. Nativecollisioncells/scriptsremain. FourarcadeL1walkerposes/native40x40+shadedsmallwalkers;allotherminorartnotfinished.

17consolidatedchecksPASS:2084pixel,1164clip,200IRQ,20544nativeFX;all8boss700,controls/death/title/snake/fire/errors,ordinary4posewalkers,7bossreplays700before/after,full8ending/residentsecondcircuit60876refreshes.72TAPpages/ownedbanks/unchangedengines/ZIP/32filecleanrebuildPASS. Terrainbank4preserved;genericcodebank5prefix+6tail,rawbank6withI D8,immutablebank1,peractorhistoriesexceptL4multipart. Coldworkspace/nativetail restored. NativeFXfixturemustinstallgenericcodebeforeisolatedcalls. No r60hardwareconfirmation;stock64KBunchanged,r57standard/r59comparisonretained. Reset/replacecompleteRTYPE,RTFULL.TAP;normalkeydefinition,bothjoysticks,Mmusic,B-release-Bbosspreview. TEST_HISTORY123/docs/r60_boss_motion.md;nativepreviewbuild/diagnostics/boss_motion_r60/index.html,assetpreviewbuild/graphics/enemy_upgrades_r60/index.html.


Smallwalkerfollow-up: r60wrongpose23/uprightandduplicate24/25confirmedagainstactualr59graphics/nativeframetrace. CorrectedPREVIEWONLYatbuild/graphics/small_walker_comparison/index.html usesarcade1570/72/74walkand1600/02raise,sharedcrop/anchors,5unique/legalECMposes. NoROM/ZIPchange;integration/gameplayvalidationpending. TEST_HISTORY124.

WalkerhighlightalternativesPREVIEWONLY:build/graphics/small_walker_highlights/index.html,steel/deepblue/warmmetal3stylesx5poses,legalECM/silhouettevalidatedandcomparisoninspected.TEST_HISTORY125.NoROMchange.


## r61 responsive loader WIP (2026-11-05)

UserselectedBbluewalkers+immediatelogo/numberselection/cancellableloading/bigprogress,thenL-numberinplayandShift-Lpreloadall. Candidatebuild/fullgame/startup_r61,NOZIPyet. NewSTART01..08(48x1KBimmutablepages)+RTCORE(22x1KBsharedcolddata),oldLEVELnn8pageformatsforruntime. Loader6115bytes,logo/data/waitpolling,cancelonlyafterdrained1KBpair,normalblack/big16pxprogress,all64fragmentverify. Directcoldstartupall8passedearlier;latestcold1/5andL3/cachedL1overridePASS. ShiftLexactpause/resumeL1+L5PASS,all8banks/screen/high/common/registers/SP/video/native5Epreserved,all8resident,subsequentL3nodisk. Currentbluewalkerassetsintegrated. Needremainingfrozenregression/cancel/error/UI/repro/contracts/package;TEST_HISTORY126fullarchitecture/pitfalls. AvoidFD4C/Dmusicstackbytes;stateFDA5jobFDA7..F freeviaexistingpopupreroute. L5hotkeysourcebank5prefix->HOME7B,sharedC000prefixnowCORE. Currentgamebanks2/3contextscratchother3slots;neverpreload2/3. Snapshot7F/finaltail7C->low0E11bank-safe. Keysmainlooponly,Bpreviewunchanged,M/bothjoysticksnormaluserbinding. LastreleaseR60unchanged.


## Latest experimental disk build: r61 (2026-11-05)

Complete package build/fullgame/startup_r61/RType_TS2068_r61.zip SHA256 aa4a392c2f527181fe8fb784a780410ce87d69f4515e3fbee77213953ff84ae1. Responsive early logo/1..8 selection, safe-boundary interruptible cold loading, largeprogress, approvedbluewalkers. L-release-number leveloverride fixed: abandonoldworldcontinuation8659 andenter8640 fullECM/terrain/actors/shipinit. MissednativeC496->FDAA interiorpopupcall redirected000D; loaderjobbytesno longerexecuted. Completionbitonlyafterfullverification; forcedinvalidL7reloadpasses. ShiftLpreloadmissing/resumeexactcurrentgame; allresidentnoop. Eightfrozencheckgroupspass inclrepeatedL7/L5/samelevel/missingcache,preloadL1/L5,cancel/errors,controls,walkers,20544FXcases;297productrebuild/TAPreconstruction/ZIPCRCpass. ActualUI/gameplaycapturePNGsinbuildfolder. r60archiveunchanged,64KBtargetunchanged;hardwareconfirmationpending. SeeTEST_HISTORY126followupanddocs/r61_responsive_loading.md. Reset/replaceentireRTYPEfolder,loadRTFULL.TAP;donotmixolderfiles.


## Latest experimental disk build: r62 (2026-11-05)

Package build/fullgame/force_loading_r62/RType_TS2068_r62.zip SHA256 e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574. NativeForce/pickup docking repairedbylogicalID3footprintbefore9559, retainsfineplayerdrawingandnativeattachmentrules/sixthdefinedaction. ShiftL AY+beeperoff immediatelyonmainloopacceptance, attribute-onlyLOADING<28000cycles beforebanksnapshot/detailedUI. Activegame/audioresumeexactinL1/L5checks;cachednoop/jumpsretained. HOMEFDC3..FDFFhelper, onlybank7FB98hookchanged; liveE350bosstablepreserved. CountednativeFDEBdelayentryrelocated0002(inadditiontoFDE9/FDAA), common/highcallerspatched. NinefrozencheckgroupsPASSinclForce4levels,preload2levels,repeatedjumps,controls,death,20544FX,ordinarybottomL3 2000updates,title116;300productrebuild/TAP/ZIPcontractsPASS. r61ZIPunchanged.

OPEN: reportedhardwareL3bottomterrainvisualglitchnotidentifiedinthisemulatorroute;doNOTclaimfixed. L6minor13poses5..17stillnative;arcadeA/Bproposalsatbuild/graphics/l6_remaining_r62/index.htmlawaituserreview. Noartinstalledinr62. Stock64KB/referenceprojectsunchanged. docs/r62_force_loading.md/TEST_HISTORY127. Reset/replacewholeRTYPEfolderbeforeRTFULL.TAP;hardwareconfirmationpending.


## L6 art correction previews (2026-11-06)

PriorL6gallerysuperseded:5..8explosionmatchrejected;9..13unverifiedmatchwithdrawn. Correctedproposalbuild/graphics/l6_corrected_sources/index.html: originalwalkingROMcels224/226/228/230againstactualnative5..8,24x24/32x32options; full-height16x32/24x32turretswithindependentroundedblue/cyan/whitedomelights,5nonblackcolours,housingstaticacrossstates. Old32x48sourcefitshrankturretto16x24; fixedframingfills32rows. All16frameslegalECM,4uniquewalkposes/legbands,4independentlightstatesvalidatedandcontactsinspected. Sourceidentityreview/geometryapprovalpending;9..13remainsunmatched. PREVIEWONLY; r62ZIP unchanged. TEST_HISTORY128/scripts/preview_l6_corrected.py.


## L6 complete-assembly review (2026-11-06)

Userplaces224-familywithnative9..13;5..8walkerstillunmatched. Roundbulbs/croppedstripproposalsrejected. Currentbuild/graphics/l6_assembly_review/index.htmlshowscompletearcadepairedpieces320+324,1476+336,1488+340(sameY,adjacent32px)combined64x48visiblebeforeconversion. Originalshallowglassoutlinesretained. Threeaspect-preservedsizeoptions,Sierra/solidmaterialalternatives;41legalnormal8x1arrays. Native1500updateL6traceshows15->16->17->16cycle;prior4IDs=4lampstatesassumptionwithdrawn. Contactsinspected;previewONLY,runtimeunchanged. Exactnativecomponent/pose/collisionintegrationpending. TEST_HISTORY129. r62ZIPpreserved.


## L6 surface refinement (2026-11-06)

Current asset review: build/graphics/l6_surface_refinement/index.html. Selected32x32 head family9..13: fine/deeper gray dithering, source-confined red accents. Machinery actual paired piston poses retained, horizontal/ordered shading alternatives, blue/cyan/white pistons, yellow/cyan/white body, normal-black/white tubing and coloured shallow tips.14 legal8x1 arrays validated; contacts visually inspected. Preview only; no game integration or performance claim. Exact native pose/component mapping pending;5..8 walker still unmatched. TEST_HISTORY130. r62 ZIP unchanged.


## L6 structural shading review (2026-11-06)

Current preview build/graphics/l6_ordered_machinery/index.html: selected deeper gray darkened slightly; machinery returns to original paired source material/shapes with horizontal structural bars or Bayer shading, red/white dome highlights and source side-light accents.10 legal8x1 arrays inspected/validated. Independent side-light blink timing pending. Asset review only; r62 game unchanged. TEST_HISTORY131.


## L6 cylinder highlight alternatives (2026-11-06)

User rejected preceding machinery shape, especially lower cylinder. Current review build/graphics/l6_cylinder_highlights/index.html offers cyan rim/yellow face and cool metal alternatives. Nearest source scaling and explicit dark-stroke preservation; six legal8x1 frames, contact inspected. Pending visual choice, asset preview only; game unchanged. TEST_HISTORY132.


## L6 original light-sequence review (2026-11-06)

Darker32x32 head9..13 accepted by user. Current machinery preview build/graphics/l6_cylinder_flash/index.html corrects lower cylinder shading bounds32..46 and captures actual arcade palette flashing:29 continuous4-frame samples,15 unique source states, paired actor X delta-10/sample. Side lamps no longer forced equally bright: source dim/bright phase validated in both alternatives. Source dome intensity preserved.30 legal8x1 arrays, contact inspected. Approximate normal-black-off/normal-red-on small lamp representation;4-frame temporal sampling. Asset preview only, not native game integration. TEST_HISTORY133. r62ZIP unchanged.


## Cyan rims selected; fast light fill review (2026-11-06)

User selects cyan rims and darker32x32 head9..13. Latest build/graphics/l6_light_fill/index.html: earlier snap-on red middle light, tiny upper-right white glint, red-only/lower-magenta alternatives. Off state unchanged; outside-dome cells including side lamps unchanged.30 legal8x1 frames validated and contact inspected. Asset preview only; game unchanged. TEST_HISTORY134.


## Latest expanded disk release r63 (2026-11-06)

Package build/fullgame/l6_selected_r63/RType_TS2068_r63.zip SHA256739ca53a0e70c7db176275efa2b82d2b00c919c78992084b20277caf4a6c0446. Accepted darker32x32 heads9..13, cyan-rim full paired machinery14..17, immediate red/white/lower-magenta lights with small side lights integrated. Original native AI/event IDs retained; cache-only render aliases. Native13 reuses226 return pose;14 static alias not seen on ordinary route. Native machinery origin retained to avoid old-mount shading overlap;5..8 unchanged. Shared preload5888bytes, compressed payload3522, motion1146, table13entries belowE3F0, helper3A00 preserved. Six frozen test groups pass incl600ordinaryL6updates/allposes,controls,jumps,preload,resume,death,Force. Isolated rebuild30primary binary/TAP products identical; TAP reconstruction/ZIPCRC pass. Old loader-copy length regression fixed in candidate and covered by repeat transitions. All other levels/boot/launcher byte-identicalr62. Stock64KB unchanged; physical hardware confirmation pending. L3 terrain-edge issue still open. Reset/replacewholeRTYPEfolder/loadRTFULL.TAP. TEST_HISTORY135; docs/r63_readme.txt.


## Latest expanded disk release r64 (2026-11-06)

Package build/fullgame/native_fit_r64/RType_TS2068_r64.zip SHA2561f50c30d5fbd79e49f2fcbd1ae31df6b3b65e7f12eb77d05bfcb0128d4c26d41. PlainL title preload; ShiftL gameplay preload; L-number jump retained. L6 moving piston only in original16x32 footprint, no duplicated fixed mount; approved darker32x32 heads retained. L7 ECM upgrades25nativeframes including walker14..17; original geometry/animation preserved, authored native shading except accepted arcade-head family18..22 at24x24. No unverified arcade walker replacement. Repeated bolt redraw ownership fault fixed within original640byte engine; stars/newforeground preserved. User r63PicoVideo L3 photo has persistent screen-fixed fragments: cleanup mechanism reproduced, exact hardware photo not confirmed fixed.14frozen emulator groups pass incl2000L3updates,600L6/L7 each,title1/5,preload5/6,cached/coldjumps,controls,death,Force,rapidfire. Isolated rebuild30primaryproducts identical; bounded edits/TAP reconstruction/ZIPCRCpass. docs/r64_readme.txt;TEST_HISTORY136. r63ZIP/sourcearchives/referenceprojects/stock64KBunchanged. Reset/replace wholeRTYPEfolder/loadRTFULL.TAP; request hardware L3 recheck.


## Latest expanded disk release r65 (2026-11-06)

Package build/fullgame/hardware_fire_r65/RType_TS2068_r65.zip, 511310 bytes, SHA256 27187756c65a85e61e126f32f42315e48283852fa9a21491f7b5afc0f5210ff0. Lowercase rtype/rt.tap; internal relative asset filenames unchanged. Replace whole packaged folder/reset. Hardware joystick fire corrected from raw bit4 to active-low bit7; directions and normalized fire bit4 retained, both sockets/keyboard simultaneous. Pause P with PAUSED overlay; Shift-P when P is defined (QAOP), P resumes. Exact bitmap/ECM restoration, AY volumes muted/restored, world frozen. Load All returns to current level's title with all eight caches valid; already-resident active-game shortcut also returns title. Enter-to-define-keys restored in title polling; BFA9 stale CALL FDEF redirected to native zero-fill0072 because FDC3..FE03 is now Force helper. Repeated key definitions and actual custom-key start/movement tested on1/5. UI315bytes in generic3E40 orL5 9EA0, key bridge50bytes3F80/8F40, glyph48bytes3FC0/8F10; bank/vector protection and boot packed workspace retained. Twelve sequential groups pass, 30 primary products rebuild identically, tape reconstruction/checksums and ZIPCRC pass; r64 ZIP preserved. TEST_HISTORY137/docs/r65_readme.txt. Exact remaining L3 stationary hardware fragment remains unresolved; no asset/stock64KB/reference-project change. Hardware confirmation still required.


## Expanded disk r66 initial-load queue (2026-11-06)

build/fullgame/startup_r66/RType_TS2068_r66.zip, 511569bytes, SHA256 96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60. rtype/rt.tap retained; replace whole folder/reset. Cold Shift-L latches D623 and displays LOAD ALL QUEUED, survives release and startup level changes, passes through cold image to FDA6. First native dispatcher consumes request and starts Load All before title animation, finishes all8resident then title. Required selected-level/core startup still completes/verifies before other levels. Stages READING FILES/VERIFYING MEMORY/PREPARING GAME; snapshot feedback PREP RAM replaces vague big LOADING. Loader6142bytes fits6144, generic hot1012/HOME1024, copy lengths regenerated. Seven regression groups pass plus initialL1 queue and L2 boss diagnostics;30primary rebuild products identical, tape reconstruction/ZIPCRC pass, r65ZIP unchanged. No playable artwork/geometry change. L2 original Spectrum-v-current/isolated arcade32/40head comparison and inventory at build/graphics/l2_geometry_review_r66/index.html; awaiting scale choice. L2 scrolling report remains open: normal approach completed-world measurements show lower boss bands moving1pixel per update, cannot rule out intermediate publication/hardware behaviour. L3 also open. TEST_HISTORY138/docs/r66_readme.txt. Stock64KB/reference projects/source ZIPs unchanged.


## L2 organic boss Sierra Lite body review (2026-11-06)

User supplies RetroPixelConverter reference and requests arcade-derived organic body/holes/shading. Latest asset review: build/graphics/l2_organic_sierra/index.html. Uses complete arcade frame17400 (frame16800 clipped at right), warm-colour/coarse-hull body isolation and proportional scaling before conversion to160x88. Four legal8x1 alternatives, normal0..7 only: A deep material shading gamma1.35, B pink flesh/bronze ribs gamma1.8, C bright material gamma2.2, D unrestricted coverage SierraLite gamma1.8. A-C RGB-error diffusion with material palette restrictions and pink-hue protection; all mask openings stay black. Final comparison.png visually inspected. Body bits+attrs3520bytes per alternative; no runtime/cache allocation or performance claim. r66 archive unchanged. Asset previews and offline scene compositions only; integration/collision/animated-mouth mapping/scenery synchronization still pending. TEST_HISTORY139.


## Preferred L2 body conversion: supplied RPC settings (2026-11-06)

User rejects earlier high-gamma preview in favour of RPC screenshot and settings44brightness/54contrast/71saturation/0.98gamma. Latest comparison build/graphics/l2_rpc_settings/index.html; selected_style.json records supplied settings as preferred future baseline, B native160x88 with bright-nonblackpairs; A normal-only compatibility, C192x104detail trial, Dper-block search. Local ../../retropixel/index.html inspected read-only: actual RPC functions extracted/executed by scripts/convert_l2_rpc_settings.mjs. Parameters -0.12/1.08/1.42/0.98 in linear light around0.18 contrast pivot, not HSV saturation3.5/gamma1.8. Normal black forced at alpha edges; BRIGHT nonblack pairs retained. All assets roundtrip, masks/canonical black bits verified and16files reproduce. B_scene.png inspected. Artwork only, no new playable build; geometry/mouth/collision/BRIGHT-renderer/scenery integration pending. r66 archive unchanged. TEST_HISTORY140.


## Expanded disk r67 - selected L2 RPC boss integrated (2026-11-06)

build/fullgame/l2_rpc_r67/RType_TS2068_r67.zip,513832bytes,SHA256 f35144c6c728f6485fb3fcb658dd26b2a6fa3a4f737d531ba4d4eeb69b94a716. Replace whole rtype folder/reset/run rt.tap. User-selected C192x104, RPC44/54/71/.98 SierraLite body integrated into native scenery map56..63;18tiles,2125compressedbytes in old2160byteboss area.128sharedpalette slots:16common fixed,96body rows,16mouth rows.251/312bodycells exact,61fitted, mean absoluteRGBerror2.2086/255; black/nonblack source geometry preserved. Four sampled arcade weak-point poses replace native41..44 (32x24 at152,64), spawn/hitbox move together; mouth packing exact. Isolated arcade32px heads2470/2464 replace neck-contaminated crop, centered in original40x40box; mirrored5/6 verified against native family,3717bytes of four preshift phases in existing bank1 allocation. Other7levels/boot/launcher/sharedcore byte-identicalr66; stock64KB unchanged.

Seven emulator regression groups pass, including ordinary approach, repeated2/1/2/3/2/5/2/6 cold/cached jumps, pause, key definitions, actualdeath/respawn, LoadAll. Extended700bossupdates render all3..6 and41..44 with protected-code/stack/cache guards. Eleven lower-body8-rowbands move1px in all31successive measured fine-scroll transitions; native stop retained. Controlled160boss-updateCPUtest:108338030Tstates vs104523296r66,3.65percent additional world-loop CPU; not hardwareFPS/player-response claim. No full boss-defeat or hardware playthrough claim. L3 hardware fragment remains open; some other L2 enemies retain earlier conversions. Selected integration finished, not blanket all-level arcade conversion.

Review build/graphics/l2_integrated_r67/index.html; docs/r67_readme.txt; TEST_HISTORY141. All-level future RPC inventory build/graphics/arcade_rpc_inventory_r67/inventory.json:114historicalsourcefiles,68unique per-level sources, identity-review required (withdrawn historical matches exist). Exact accepted settings retained for comparisons; do not automatically replace accepted art or install unverified matches.


## All-level RPC artwork comparison (2026-11-06)

User authorizes conversions/comparison. build/graphics/arcade_rpc_comparison_r68/index.html provides124source entries /248outputs, native-footprint N and1.3x-detail D, aspect-preserved before actual RPC44/54/71/.98 SierraLite. Artwork scale1.3 separate from8px storage padding.114historical source entries plus correctedL2heads/body andL6heads/fullpairedmachinery; uncertain historical matches prominently flagged. Current references91storedr67native,32compiledphase0fromactualimmutablepreload tables (including consolidated blocks),1acceptedpackedL5core. Not fullcompositedscreens; L5wholeassembly separate accepted link. All248exports independently roundtrip bits/attrs/RGB, legal8x1/noFLASH/noBRIGHTblack, maskedblackRGB/bits0. r67ZIPunchanged. Preview-only, no gameplay/assets installed, performance or collision claims. TEST_HISTORY142.


## Interactive artwork review r69 (2026-11-06)

build/graphics/arcade_review_r69/index.html:124entries,64initialsettingsfamilies, exclusiveAccept/Tweak/Misidentified-review/No-change checkboxes, notes, native/detail size, live actualRPC brightness/contrast/saturation/gamma. Family settings/size shared acrossalllistedmembers; knownposes+duplicates linked, editablefamily IDs; explicitapplydecisiontofamily. Changingacceptedfamilysettings marksacceptedmembersTweak. LocalStorageautosave,JSONexport/importwithcompletefamilyparams/entrychoices; no runtimeassets installed. Wide-stripfamilies defaultscrollpolicy; otherassets mayenable. Horizontalrow pair helduntilsourceblackgap>=8, perrowverticalvariation, normalblackedgepolicy; ditheronce,shiftthroughall8phases. Conservativeblack+inkcanlosecolours; optionalpreviewnotuniversalartimprovement. Panoriginalmonochromelevelmapgeometry+arcadebosscontext; notcurrentcolouredcompositedterrain. Familyposecyclelabellednotgamecadence.

248workerbaselineRGBoutputsbyte-identicalr68,settingschangesvalidated;real+synthetic7/8/9/16gapcasesall8phasesno8x1clashes. DOM-stubtests cover124cards,exclusivechecks,familygamma/size,acceptanceinvalidation,autosave,JSONroundtrip,filter; notbrowserQA. Browserautomation explicitlyblockedfile:URL, noalternatebrowser/proxyworkaroundattempted. Localpageprovidedforuseropening. Engine/reviewlogicreports andREADME inoutput; TEST_HISTORY143. r67archiveunchanged.


## Saved review checkpoint and current-r67 size conversion (2026-11-06)

User supplies convref/rtype-art-review-mostlycomplete.json, then directs keeping dimensions of CURRENTgame, not originalSpectrum orDpreviews.124entries:52tweaks/39families,6review,66unmarked,0explicitAccept. OriginalJSON preserved. Reviewcheckpoint build/graphics/review_checkpoint_r70/index.html regenerates52savedproposals and30native-sizealternatives;30enlargements held,16terrain/assemblyrisks. Latestauthoritativeoutput build/graphics/current_size_choices_r71/index.html regeneratesALL52tweaks atmeasuredcurrentr67dimensions, preservescolourparams, scaleoriginalRGBbeforeRPC. All52Nprofiledimensions verifiedagainstcurrentstored/cachefootprints,includingL2terrainbody192x104. L3verticalstripsremain8x104,L3_04080x16,L8boss48x32,L6heads32x32. Notinstalledgame; noassetpacking/performance/collisionclaims.52RGB/bitmap/attrsroundtrips+39familyconsistency pass. r67archiveunchanged.

Resume build/graphics/arcade_review_r69/current_size_review_r71.html preloadsreviewandlocks52selectedentries tocurrentfootprint (Ddisabled), separatestoragesavesfromoriginalform. effective_review_current_size.json retainssavedcoloursandupdatesfamilyvariantN;sourceJSONunchanged. CorrectedL2bodyreferenceusestheinstalledterrainassetratherthanseparateactor41mouth.6flaggedsourceentries remainpending;unreviewedartunchanged. TEST_HISTORY144. ScrollpalettecoordinationforassembledL3stripsstillrequiresreview;resizingalone doesnotvalidatefullassembly/sourceidentity.


## Evaluation holds (2026-11-06)

User directsL2_003/004/005/006 andL3_040 be evaluated,notcommitted. src/art_review_holds.json isstandingreplacementhold;scale_review_to_current_r71.mjs enforcesit. Current-sizegallerynow47candidates+5evaluation-onlypreviews;all52settings/previewsretained. EffectiveJSONdecisionsandstate markfiveReview,11totalReview/47Tweak/66unmarked. OriginaluserJSONandgameunchanged. Resumeformnewseparatestoragekeyloadshelddecisions;gallerylabelsHELD. Noheldreplacementallowedbyimportmanifest;sourceidentity/shape/animation/assemblyevaluationpending. TEST_HISTORY145.


## Latest playable release r72: reviewed artwork at current sizes (2026-11-06)

Expanded disk release: build/fullgame/reviewed_r72/RType_TS2068_r72.zip (513881 bytes; SHA256 e219bfe39e70e42e2cc4784ed8d0f654c3a2f5786240312641279868f8bba9e9). Replace complete lowercase rtype folder, reset, run rt.tap. Applies 47 reviewed choices at current r67 dimensions. Explicit holds L2_003/004/005/006 and L3_040 remain unchanged; earlier review-only choices also preserved. L5/L7 complete level images unchanged. Boot, loader, controls, audio and gameplay logic retained. Stock 64KB cartridge unchanged this release.

Build scripts build_reviewed_r72.py, prepare_l2_reviewed_r72.py and finalize_reviewed_r72.py; validation_summary.json and native_art_report.json record packing. L3 strips retain existing transparent-cell layout and fit the shared palette; some preview pixels outside that layout are omitted. L4 selected cache artwork uses normal-intensity pairs for existing renderer compatibility. L2 body stays 192x104, 19 tiles, 2152 compressed bytes; mouth colours and held head cache preserved. L6/L8 compressed restart backups relocated with artwork and preload pointers. Actual installed examples/game captures: build/graphics/reviewed_game_r72/index.html.

All eight scripted boss tests, nine main regression groups and three additional backup/cache/restart tests pass. L3 ordinary 2000 updates, L6 ordinary 600; custom keys, native joystick combinations, pause, Force, firing, death/restart, Load All and repeated cold/cached jumps checked. TAP checksums/reconstruction and deterministic primary outputs pass. L2 same 160-update CPU sample costs 1.6793% more T-states than r67, not a hardware FPS measurement. Hardware validation pending; known L3 stationary-fragment report not claimed fixed.

New future RPC starting default in src/rpc_default_settings.json: brightness49, contrast65, saturation78, gamma1.13, segment-coverage serpentine Sierra Lite; normal black, legal ECM pairs, current dimensions, no automatic enlargement. Derived from 37 included families across six represented levels using per-family then per-level balanced medians. Does not override individual r72 settings; future autoconversion proposal only. TEST_HISTORY146.


Latest release r73 restores previous r67 terrain colours/scrolling artwork for L1-5. L2body and L3strips reverted; L4/L5 terrain already unchanged. L1 entire shared palette locked, four reviewed enemy streams fitted to existing pairs. L4/L6/L8 reviewed enemies retained. build/fullgame/terrain_restore_r73/RType_TS2068_r73.zip; see validation_summary.json and TEST_HISTORY147. Terrain conversions require assembled scrolling validation, not isolated strip acceptance.


Latest r74: normal-sized loading labels/numbers, giant PREP RAM feedback suppressed, existing normal PREPARING GAME stage retained. build/fullgame/loading_text_r74/RType_TS2068_r74.zip. r73 artwork/terrain unchanged. See TEST_HISTORY149.


Latest r75 restores complete pre-r67 L2 (r66 image plus feedback RET); earlier r73 rollback to r67 did not reach the reported regression. Restores earlier terrain AND earlier L2boss/enemy art. Other levels and small loading UI remain r74. build/fullgame/l2_palette_restore_r75/RType_TS2068_r75.zip. See TEST_HISTORY150. Root cause within r67 integration not isolated; do not claim selective palette fix.


Latest r76 fixes reproduced L3 colour corruption on L2 exit and L2 native terrain colours. Actual root: r67 token keeper cleared terrain bit7; restore trailer reinstated Spectrum RES7 at FF81 rather than ECM NOPs. Preserves tokens, restores NOPs, resets hook after native helper rebuild each initialization using retired CF0padding wrapper. Artwork returns to r74, reinstating upgraded L2 r67 body/head/mouth instead of r75 full rollback. Small loading text retained. build/fullgame/terrain_token_fix_r76/RType_TS2068_r76.zip. TEST_HISTORY151 supersedes root-cause uncertainty in150.


Latest r77 queued Shift-L startup bulk loading runs before game init, avoiding snapshot/handover screen interruption. Visible total restored; queued count continues through406files rather than reset0of336. Normal startup70 unchanged. Small digit renderer/table reclaimed extension space; loader6142 unchanged. Cold worker separate entry preserves core workspace usingE000 bank5buffer, restores buffer selector; all-valid mask retained to title. Gamelevelimages/RTCORE byte-identicalr76. build/fullgame/startup_bulk_r77/RType_TS2068_r77.zip. TEST_HISTORY152.


## Open L2/L3 stationary scenery report after r77 (2026-11-07)
User confirms latest build, visible immediately before firing. Photo12972 L2 columns fragmented/non-scrolling; L3 similar. No fix claimed. Diagnostics in build/fullgame/startup_bulk_r77: scroll_L2/L3_* completed early updates20..180, long_L2/L3_* through700 with firing/vertical movement, raster_L2/L3_* intermediate video frames70..90, queued_game_L2/L3.home.bin. Map geometry comparisons find no persistent displaced terrain cells on these emulator routes; intermediate frames show +/-1pixel partial publication. Actual forced death/respawn L2/L3 restores expected per-level hooks. Queued startup LoadAll with selectedL2/L3, then100 no-fire worldupdates, also renders coherent columns. Need hardware pause persistence result to distinguish retained corruption from display/publication; pending question asks if broken shape remains after P. Do not infer hardware fault or close issue merely from emulator results. r77 archive unchanged. TEST_HISTORY153.


Latest r78 addresses user-confirmed L2/L3 stationary terrain on in-game L-number jumps, not menu start. Jump-only rebuild of initial scenery ownership (640cells, bitmap ->FF/0) before ship setup; resets fine-scroll7A82/83, restoresmap9. Reserved58byte feedbackpadding helper (L5 separate bank), CF0trampoline and D75/D96padding used; originalnative86C3 warmup restored to avoid CF0recursion. Protection countdown now acceptedplayer-update clock; actual joystick terrain collision natural184.93s before vs0.607s after. Artwork/palettes/playerphases/r77loader unchanged. build/fullgame/world_owner_r78/RType_TS2068_r78.zip. TEST_HISTORY154; hardware pending.


Latest r79 supersedes insufficient r78 ownership workaround. Confirmed native star writerBF3D contaminates initial7800attrs because callbackBE62 remains1 onjump. Normalmenu73C2 disablesit. CommonCF0initializer nowCALL73C2 before86C3; existing8721/73BC reenablesafterconstruction. R78ownership/finephase/trampoline patches removed; nativejump8640restored, R78collisionclock retained. Allart/palettes/phasesandR77loaderunchanged. build/fullgame/world_reset_r79/RType_TS2068_r79.zip. Newregression failsr78, passes12initializations (640nativeattrs each) across11jumps; all8bosses andloading/pause/respawnpass. TEST_HISTORY155; hardwarepending.


Latest r80 fixes L3 four stationary fragments: offscreen walkers wrapped into viewport by phase smoother losing positive upper coordinate bits. Preserve X/Y upperE0, sharedlevels2/3/4/6/7/8, padded same size. Allart/palettes/loader/scripts unchanged; L1/L5 unchanged. Matchedgamecapture confirms fragments absent, all8bosses/11jumps/12attributeaudits/staticTAP checks pass. build/fullgame/offscreen_clip_r80/RType_TS2068_r80.zip. TEST_HISTORY156; hardwarepending; stock64KBunchanged.


Latest r81 upgrades L3 enemy36-39 with ECM silver/cyan/blue and magenta/red accents; same24x24bitmaps/frames/code, two spare palette rows. Other levels/terrain/r80clipping unchanged. build/fullgame/l3_enemy_ecm_r81/RType_TS2068_r81.zip. TEST_HISTORY157; hardwarepending; stock64KBunchanged.


Latest r82 L3 yellowbot/pods/detachedengine ECM shading, existing bitmap/size/frames/code unchanged, reuses dictionary; otherlevels/terrain unchanged. build/fullgame/l3_pods_ecm_r82/RType_TS2068_r82.zip. TEST_HISTORY158; hardwarepending; stock64KBunchanged.


Latest r83 restores earlier machinery inside two L1boss openings, surrounding upgraded shell preserved. Same dimensions/storage/code/drawcost. L1boss regression/staticTAP pass. build/fullgame/l1_machinery_r83/RType_TS2068_r83.zip. TEST_HISTORY159; hardwarepending; stock64KBunchanged. Broaderwalker/correctyellowbot/referenceexhaust work remains pending.


Latest r84 broadens L1 opening machinery restoration to original silver rows across three columns, preserving shell elsewhere. L1boss/staticTAP checks pass; build/fullgame/l1_machinery_r84/RType_TS2068_r84.zip. TEST_HISTORY160; hardwarepending; stock64KBunchanged.


Latest artwork review r85: build/graphics/walker_review_r85/index.html,13families54frames127legalECMcandidates. Currentgame remainsr84. Before31/L3yellow94 explicitlyincluded; verifiedarcade versus native/AIproposals labelled. Settingsconsistentwithinvariant, nativefootprints, no runtimeintegration/performanceclaim. ExportperfamilychoicesJSON. TEST_HISTORY161.


Latest playable r86 expanded/disk build:13four-posewalkerfamilies, correctBefore31/elongatedyellow94, restoredgroundwalkers,4referenceexhaustpulses atoriginal48x16pluscompactplayerredflare. Compressedcode/load-timebank5art, existingbank6cache/512KBresidency/nativeAIscripts retained. L1stomach restoration andterrain unchanged. All8routes/4posedispatch/11jumps/12attributeaudits/death/LoadAll pass; finalL3+700ret tested. build/fullgame/walkers_exhaust_r86/RType_TS2068_r86.zip. TEST_HISTORY162. Hardwarepending; stock64KBunchanged. Forfuturebuilds use compressedruntimeimage/extension generator, notlegacyL_motion.asm alone.


Walkerart status: UseracceptsL3yellow/exhaustbutrejectsr86otherwalkers. Preserveblue21..25pendingexactidentityconfirmation. r87restorationdrafttestedbutNOTpublished; userrequestscomparisonsfirst. Latestreview build/graphics/walker_candidates_r88/index.html (8groups,96defaultframes,liveactualRPCsettingssharedacrossposes,baseline/source/candidates,exportJSON). Normalpaletteatconversion,nopostBRIGHTstrip; B/Csource-redguard. No newAIreplacements. CurrentplayableZIPstillr86unchanged; acceptedassetsfrozen. TEST_HISTORY163/164.


Latest playable r89: applyconvref/rtype-walker-candidates-r88.json exactly(L6head32B52/59/82/.87,L1large40C51/67/80/1.44,Before31KEEPbaseline3images4steploop). Blue=no: newreference-inspiredgunwalkerBinstallednative32x24/raised24x24,fourwalk/tworaise; AandlargerCcomparisons build/graphics/walker_selection_r89/index.html. UnreviewedentriesincludingL7headunchangedr86,acceptedL3yellow/exhaustbyte-identical. 30selected/newpalette-indexexactframes,33frozen;5affectedgameplayroutes/11jumps/12attributeaudits/dispatch/TAPscopechecks pass. build/fullgame/walker_selection_r89/RType_TS2068_r89.zip. TEST_HISTORY165; hardwarepending;stock64KBunchanged. Future replacementJSONversion89isdistinctfromappliedr88choices.


Latestplayable r90: userrtype-new-gunwalker-r89.json optionA39/70/100/1.01 installedsharedL1/L4/L7 with4walk+2raise atnativefootprints. 18framesexactindices,45othersandcompletelevels2/3/5/6/8unchangedr89. Priorapprovalsretained. Dispatch/affected1/4/7gameplay/11jumps/12attributeaudits/TAP/staticpass. build/fullgame/walker_choice_r90/RType_TS2068_r90.zip. TEST_HISTORY166; hardwarepending;stock64KBunchanged.


Latest playable r91 fixes confirmed r86+ bank5 native-source overwrite on cached level return. Restore6994nativebytes/header before uninstall; L1 overlapping plan has immutable packed backup. Artwork unchangedr90, levels2/5/8unchanged. 23switches/allmodifiedcachedrevisits/nativebyteaudits/helperZ80/21dispatchgroups/affectedgameplay/L3deathrespawn/TAPboundsZIPpass. build/fullgame/bank5_restore_r91/RType_TS2068_r91.zip. TEST_HISTORY167. Reset and replace complete folder; hardwarepending;stock64KBunchanged. Futurebanktests must cover originalnative/restoration-source lifetime afteroverlay and cachedrevisit.


Latest playable speedtrialr92: L4largecomponents25/26/27 use nativehorizontalsteps/fine2pxvertical, exactcheapvisibility/unshiftedcellfastpaths, IRQlatchedL+number consumedsafe. Same8secworkloadr67/r91=3worldupdates,r92=6; notdisplayFPS, stillheavy. Allart/terrain/hitboxesunchanged. L4gameplay/12cachedrevisits/nativebytes/restorehelper/4096synthcases/21dispatch/short4framekeys/TAPscopeZIPpass. build/fullgame/l4_speed_r92/RType_TS2068_r92.zip; TEST_HISTORY168. r91retainedfinehorizontalcomparison. Reset/replacecompletefolder;hardwarepending;stock64KBunchanged.


Latestplayabler93 repairsconfirmedr92L5bank1overwrite: L5usesHOMEhotkeys, DOCK1isoccupiedbossphasepayload; genericinstallerhadchanged972bytes. EntireL5region/LEVEL05/START05restoredexactr91, allotherlevelsbyte-identicalr92. r92supersededDO_NOT_USE. FreshandL4->L5boss/12repeatbossjumps/12cachedroutes/exactpayloadimagesTAPchecksZIPpass. HardwarehardlockupNOTreproduced, confirmationpending. build/fullgame/l5_bank_guard_r93/RType_TS2068_r93.zip;TEST_HISTORY169. Reset/replacecompletefolder;stock64KBunchanged. Futureinstallers must honorper-levelHOME_VARIANT andimmutablepayloadcontracts.


LatestDIAGNOSTICR94 for L5partlyvisible/upward hardwarefreeze (notreproduced). L5-only guardedcheckpoint/rawDOCK4IRQcallbackisolation; musicIRQnotexplicitlymuted, player/fireupdateratetradeoff. VisibleR94 PREPARING/R94 DEBUG. 12jumps/livegate+returnbytes/508guardedIRQszerogameplaycallbacks/overallAY/fresh+L4->L5/12cachedroutes/TAPscopeZIPpass. L5phasebank and1FF7trampoline/audioF8B0codepreserved. build/fullgame/boss_guard_r94/RType_TS2068_r94_diagnostic.zip;TEST_HISTORY170. Hardwarecause/fixstillunconfirmed. R93baseline retained, stock64KBunchanged.


R94 confirmed stillfreezes on realhardware (photo13000.jpg, L5firstrowsaboveHUD). LatestDIAGNOSTICR95 addsFEborderstagecheckpoints andfirstbossexpandedcore/spherechecksums (solidyellow/white intentionalfailstops); R95 TRACE TEST loaderlabel/R95 DEBUG. No hardwarefixclaimed. L5gameplay/allcheckpoints/112clips/checkerfaultinjection+registerSP/12guardedjumps/12general+9L5residentroutes/2heldchargejumps/lowchargebeam/TAPscopeZIPpass. build/fullgame/l5_trace_r95/RType_TS2068_r95_trace.zip;TEST_HISTORY171. Awaithardwarefrozenborder/photo. Allart/phasepayload/trampolineunchangedR94, stock64KBunchanged.

2026-11-08 R96 L5 hardware regression trial: R95 frozen RED points at whole-actor visibility planner. Replaced planner with exact450byte r58 row selector, retaining current decoder/cache layout/artwork/2px movement; empty rows preserve ownership. Based on r93, removing R94/R95 experiments. Emulation:256phases,96overlaps,112clippedpositions, cache restoration,12bossjumps,9residentroutes/live L4-to-L5, active fire/low charge PASS. Pure raster IRQmasked; live game IRQtested. Hardware freeze remains unreproduced; confirmation pending. Deliver build/fullgame/l5_row_restore_r96/RType_TS2068_r96.zip (ca0c76176ca4e6742ba9f1d55065fb94f42a299550072ac7a28b8123b08627fb). Reset/completefolder replacement, R96 ROW RESTORE startup. See TEST_HISTORY172. Stock64KB target unchanged.

2026-11-08 R96 hardware freeze persists (slightlylater,BLACK, changingborder). Route is loadonlyL5,B/release/B. R96 had no dedicated drawtracing, so blacknotlocalizing. Latest R97 isolationtrial: only selector/compositorEI->NOP whiletemporaryrawbanksvisible, normalIRQsbetweencells; explicitGREENselect/CYANcopy/BLACKreturn checkpoints. DirectL5/doubleB160updates,12jumps,lowcharge,256phases/96overlaps/112clips/ownership,atomicIFFassertions andTAPscopeZIPpass. No hardwarefixclaim; mayaffectresponsiveness. build/fullgame/l5_cell_atomic_r97/RType_TS2068_r97.zip SHA256 e17725407c8ebd2b3ee7242cf69785dc2a40820c30fecccc86e5c61e4b43ecc3. Resetcompletefolder,R97 CELL TEST. TEST_HISTORY173;stock64KBunchanged.

2026-11-08 r98 confirmedcoldstartupfix: selectingL5DURINGinitialloading reproducedblackafter70/70 inr96andr97. WarmupmovedDDDC->DDD9 butcold00D4gatewayretainedoldtarget,enteringLD(MAIN_SP),SP operand; runtimegatewaywasupdated. r98correctscoldtarget/checksbothgateways, revertsr97EIisolation, keepsgreen/cyan/blacktracing. UnmodifiedL1/earlyL5titlebootPASS;earlyL5start/doubleB160updates/12repeatedjumpsPASS;scopeTAPZIPPASS. Originallaterhardwarebossfreezeunresolved. build/fullgame/l5_cold_start_r98/RType_TS2068_r98.zip SHA256 0ee662b3411683c4cbfd6f481d48a9ad9a1ee270c458d116dc118b55bb4cbf29. Reset/completefolder,R98 START FIX. TEST_HISTORY174. Allfuturecode relocationmustcheckcoldANDcachedgateways;startupregressionsmustselectlevelbeforeloadingfinishes.

2026-11-08 R98 hardware startup/fire crash+reboot reported; no emulatorreproduction. R99 conservativecandidate restoresr93L5execution,removesALLr94-r98experiments,retainsgraphicsandassetbankrepair. Confirmedlayoutdefect:I8FvectorpagehadUIglyph/keyboardcode,99entriesbad;emulatorhardcodesFF. UIrelocatedverifiedpadding8B30/8B70,full8F00..8FFF5B. Hardwareactualvectorunknown/causeunconfirmed. UnmodifiedearlyL5startup+threefiretimings399/424/388updatesPASS;160bossupdates/12jumpsPASS,256vectortargets+2actualhandlerreturnsPASS,pause/audio/screen+64joystickcombosPASS,staticassetcode/TAPZIPPASS. build/fullgame/irq_layout_r99/RType_TS2068_r99.zip fa1d6a4d67b854f1acd5e3495dff564eac30bfc6b4d0b2175de00bbfdaa58c5a. R99 PREPARING/resetcompletefolder. TEST_HISTORY175. No hardwarefixclaim;reservefullIM2pageandtestnonFFvectorsinfuture.

2026-11-08 Artworkaudit/r101OFFLINEreview: currentr100L2terrainmostlyyellowconfirmed;generalintegrationheldL2sprites. Playerflamewasmerely2pixelretint;L3largeplumeseparate48x16asset. Actualr100smallL1walker/newgunwalkercomparedtoearlierarcadebluearmour;largekept. build/graphics/l2_art_review_r101/index.html contains18RPCproposals/animations/currentcontext. Coherentterrainlayer8shiftcheckslegalbutoliveflat/redcreamstillbands,explicitlyNOTreadyforgameintegration. r100releaseunchanged. TEST_HISTORY177.

2026-11-08 r102L3large-rocketexhaustpatch: userconfirmedlargeL3notplayer. OrdinaryplumedirectF22Dbypassedcompiledactorhook;25byteL3onlybridge01C8routesexistingphoto4frames224..227throughprovenrenderer. ActualRAMbefore/afterimageconfirms81draws4poses. CallerSP/IY/sharedID/owner80/inputBC/lowcode,3unmodifiedcoldfiretests,12cachedroutes,scopeTAPZIPpass. build/fullgame/photo_exhaust_r102/RType_TS2068_r102.zip df5552efa47174a45b79ef9737010b0e2a4eb89c3703fad9a526c4a90ba27ec4. Other7levels/playerphases/photoconversionidenticalr100. R102 PREPARING;ordinaryL3notBBshortcut. Hardwarepending;lateststable/r100archiveunchanged. TEST_HISTORY179;docs/photo_exhaust_r102.md.

2026-11-08 r103largeL3plumediameter:matches16pixelnozzlemouthacrossall4frames,same48x16bounds/length. Nozzlecolumn/player/renderer/r102bridge/other7levelsidentical. Packedimageoffset2A20->2AE8,end2FF9<3A00;noRAMgrowth/codeentrymoves.81liveplumedraws/statechecks,3coldL3firetests,12cachedroutes,scopeTAPZIPPASS. ActualRAMcomparisonPNGinspected. build/fullgame/plume_diameter_r103/RType_TS2068_r103.zip ef273367cf4ee4a28df5810d035a440c338ea5a3a519d1701fb788ae1cb89a8e. R103 PREPARING;hardwarepending;lateststable r100 preserved. TEST_HISTORY180.

2026-11-08 r104classificationfix:usermarkedr103retainedcheckerbandisexhaustnotnozzle. Complete48x16photoplume4framesnowreplaceslegacycolumn40..47too;mechanicalrim/body/player/renderer/bridge/other7levelsunchanged.81livecalls/statechecks,3coldfirecases,12cachedroutes,scopeTAPZIPPASS. ActualRAMfull_plume_comparison.pnginspected. build/fullgame/full_plume_r104/RType_TS2068_r104.zip daea992fe24347add60b7fba47f5dae49f1a8fab40d0339f9f34056f0748474b. R104 PREPARING;hardwarepending;stablelatest100preserved. TEST_HISTORY181.

2026-11-09 L1photo13021roundwalker=53-56/208-211,actualr104visible16x15in24x24. OfflineA24contentcrop24x23;B24arcade/C32originalL1walkerproposals,4distinctposes/actualRPC/legalECM. build/graphics/l1_walker_snake_r105/index.html. ActualarcadeL1snakeframe004800showsbroadgold/steelconnectedrings; source100x30stripmustnotbecompressedwholeintoonejoint. snake_arcade_context.png/stripandwalker_comparison.png reviewed. No gamechanged;awaitwalkerchoicebeforeintegration. TEST_HISTORY182.

2026-11-09 InteractiveL1arteditorready:build/graphics/l1_art_converter/index.html self-containedfilebrowsertool, actualRPCpipeline,independentwalker/snakefamilycontrols,10snakeorientations/12jointassembly,all-framecrop/scale/colour/dither,autosave/import,JSON/PNG/nativeZIPexports. Engine32cases/browserfunctional/export14frames/mobilePASS. Bundle RType_L1_Art_Converter.zip f98dfb38872b7c529af17969d86057b7bee5948a6f0279558e6d3b4b1515e6bd. src/l1_art_converter.*;docs/l1_art_converter.txt. No gamechanged;awaituserexportedchoicesbeforeintegration. TEST_HISTORY183.

2026-11-09 candidate r107: chosen L1 round walker + arcade snake export integrated; build/fullgame/l1_chosen_r107/RType_TS2068_r107.zip. Other7levels identical r104; startup/fire and12cold/cachedroutes pass. Small diagonal snake-joint gaps remain; hardware pending. Stable release pointer still r100. See TEST_HISTORY184 and docs/l1_chosen_r107.txt.

2026-11-09 candidate r110: selected C32x32 shell walker for L1native30-33; build/fullgame/l1_head32_r110/RType_TS2068_r110.zip. r107artprefix/other7regionsunchanged; full4poses/coldfire/12revisits/staticcontracts pass. Measured32vs24 +5.4%headencountertime,+2.1%controlledhead+snaketime. Hardwarepending;stablelatest remainsr100. TEST_HISTORY188/docs/l1_head32_r110.txt.

2026-11-09 candidate r114: chosen arcadeghost32/native35-37 withprecomputedvisibility; build/fullgame/l1_ghost_r114/RType_TS2068_r114.zip. Exactexport3poses;1800update/coldfire/12revisit/96plan-equivalence/staticcontracts pass. Busyghostencounter+35%updatetimevsr110old24;hardwarepending. Priorart/other7levelsunchanged;stablelatest100preserved. TEST_HISTORY190/docs/l1_ghost_r114.txt.

2026-11-09 candidate r116: exactchosen2pose40x40boostenemy native41; build/fullgame/l1_blue_boost_r116/RType_TS2068_r116.zip. Oldbank5art/other7regionsunchanged. IMPORTANT reserved411bytepackedsource in unusedpalette ranges documentedblue_contract.json: futurepaletteconvertersmustpreservetheseranges. No bank7assetstorage. Native1800update/3coldfire/12revisit/96ghost-equivalence/staticchecksPASS; hardwarepending. TEST_HISTORY192/docs/l1_blue_boost_r116.txt. Stablelatest100preserved.

2026-11-09 L2 offline reviewr117 ready: build/graphics/l2_review_r117/index.html, sevenfamilies/currentarcadereferences/sharedRPCcontrols/gap8andfullrow8phasechecks. No gamechange; r116retained. Uncertaincrawler/chainmatcheslabelled. L2redpatch/bossruntimepaletteandtileassemblyfix remains pending; notclaimedfixed. TEST_HISTORY193.

2026-11-09 correctedL2reviewr118: fullpairedscorpions andactualcapturedsnakechain; alluserexportsettingsnotesretained,approvedCwalkerconfirmed,offlinebossentrance/celldissolveprototype. build/graphics/l2_review_r118/index.html. TEST_HISTORY194. Gameunchangedr116; runtimefix/integrationpending.

2026-11-09 L2v2choices accepted; userrequiresall10scorpionframes. Exactexports/proven4baseposefliprelationships stagedbuild/graphics/l2_scorpion_all10_r119. r119gameplaydraftFAILEDSstartup/transition,DO_NOT_USE; noreleaseZIP. r116unchanged. All10actorintegration/terrain/bosswork remains pending. TEST_HISTORY195.

2026-11-10 r123L2actorintegrationcandidate: all10scorpions/selectedCwalker/whitelegs/snake/emergence integrated;27actualdecoderchecks,1547ordinaryupdates,3coldfire,12general+6longboss/reset/revisitroutes,tape/staticZIPchecksPASS. Nativeprefix/trailer/AFrestorefixes; source/snapshotallocations inL2_actor_contract.json; exactintentionalHOMEplan/tileworkspaces documented. Largeractorscosttime;terrain/bosspaletteintegrationSTILLPENDING;slowfullscanexperimentexcluded. build/fullgame/l2_integrated_r123/RType_TS2068_r123.zip SHAebfba475f3fbf491b39992318504c0ac33b90b707e72ff053aa2f9a770404583;TEST_HISTORY196/docs/l2_integrated_r123.txt. Hardwarepending. Stablelatest100/stock64KBunchanged.

2026-11-10 r124 complete selectedL2integrationcandidate:27actorpackets/all10scorpions retained,34nativeterrainIDs/silhouettes restored,18separatebosstiles,coherentmovingpalette andstoppedbossrichreveal. Nativeprefixsnapshotexpanded1012bytes,ROMfontreclaimsduplicateonly,DOCK7unchanged. 128tile/27actorchecks,1547ordinaryupdates,3coldfire,12general+6boss/reset/revisits,16tapereconstruction/ZIPPASS. Conservativefullrowterraincolourpolicy,notnewarcadesilhouettes. build/fullgame/l2_complete_r124/RType_TS2068_r124.zip SHA574c10a09657682502fe1e89fd464c7d43c856a43021641ecc96a00eaba2af15. TEST_HISTORY197/docs/l2_complete_r124.txt;hardwarepending/stable100/stock64KBunchanged.

2026-11-10 r125 fixesr124L2yellow-scroll/playerprojectilepalette regressions. Regularflat/slowpaths usechosenrowpalette withactualbankmappingpreserved; original96globalpalette rows retainedlosslessly andexpandedonlyAFTERnativebootstrap. Planartilepack5185bytes/52table inretiredauthoringpalette, all128tileoutputs exact. Sustainedfire1547updates,96palette/160rowchecks,27actors,3coldfire,12general+6bossroutes,tape/ZIPchecksPASS;visualfinalcapturesinspected. build/fullgame/l2_scroll_projectile_r125/RType_TS2068_r125.zip SHA728bf4496e9a3c4f801d7cff04e8505592d1c952905b22706efa66e229161959. TEST_HISTORY198/docs/l2_scroll_projectile_r125.txt. Hardwarepending;stable100/stock64KBunchanged. Buildscripts/build_l2_final_r125.py thenfinalize_l2_r125.py; formerexperimentalstaticbank6layoutrejected.

2026-11-10 r126 L2snakebodypartfix: native22/23bothmapcommonarcade2450body199,head/tail25..30unchanged. Oneexpandedruntimebyteonly.455bodydraws/27actors/96palette/160rows/12transitions/tapesZIPchecksPASS;actualRAMimageinspected/hardwarepending. build/fullgame/l2_snake_parts_r126/RType_TS2068_r126.zip SHAcb4eb7f618979d4da24c7b35bbd9f4df618734cafd2561914c95449b6f5ce748;TEST_HISTORY199/docs/l2_snake_parts_r126.txt. Stable100/stock64KBunchanged.


2026-11-10 UNRELEASED r127 snake anatomy/boss-erasure investigation: mixed stable round/spiny chain roles implemented, 700-update intermediate role trace passed; boss repair experiments FAIL strict background/RAM validation. NO release ZIP. build/fullgame/l2_roles_restore_r127/DO_NOT_USE.txt; TEST_HISTORY200. Current prototype is NOT release-ready; prior JSON/captures span experimental revisions. Stable100/released126/stock64KB/reference projects unchanged.

2026-11-10 r127 completed L2 snake anatomy/boss backdrop fix, supersedes entry200 failed prototype. Immutable2592byte DOCK6CB00..D51F cache,122byte copier, stable9round/4spiny chain, originalhead/tail.700firingupdates/5exactbackground+cachechecks/31actors/128tiles/96palette160rows/12transitions6bossroutes/3coldfire/debug/tapesZIP PASS. PerrepairCPUcost reduced79% vsconservative redraw,not hardwareFPS. build/fullgame/l2_roles_restore_r127/RType_TS2068_r127.zip SHA4b25938e18a233a39930d78135527e47944a9536c4c4ee81080f1625aa3a4daf;TEST_HISTORY201/docs/l2_roles_restore_r127.txt. Hardwarepending;stable100/stock64KBunchanged.

2026-11-10 r127 completed L2 snake anatomy/boss backdrop fix, supersedes entries200/201 failed prototype. Immutable2592byte DOCK6CB00..D51F cache,189byte copier, stable9round/4spiny chain, originalhead/tail.700firingupdates/5exactbackground+cachechecks/31actors/128tiles/96palette160rows/12transitions6bossroutes/3coldfire/debug/tapesZIP PASS. PerrepairCPUcost reduced60.9% vsconservative redraw,not hardwareFPS. build/fullgame/l2_roles_restore_r127/RType_TS2068_r127.zip SHAfb0a3ff44bfab1f3eeb6ca2801edd733cd47f42525ff8bae78e13234b69c8330;TEST_HISTORY202/docs/l2_roles_restore_r127.txt. Hardwarepending;stable100/stock64KBunchanged.

2026-11-10 r128 L2 scorpion direction correction: userfalseXright/falseYdown,confirmedFrame3false/true;runtimeframes2/5 X/Ymirrored inexistingpackets;all10sourceorientation families exact andactualdecodes/exportchecksPASS. Snake usesexistingneck role4 then4spiny/9round body,headtailunchanged;2runtimebytes only,size/animationrate unchanged.1547approach/700bossupdates/all13roles/31decodes/12transitions6bossroutes/3coldfire/tapesZIP PASS. build/fullgame/l2_orientations_r128/RType_TS2068_r128.zip SHA7a55a56e7b383ea1ab9b552216ff34ebacc9a13bffb8b229ce8ddb62ad43babf; interactivepreview build/graphics/l2_orientations_r128/index.html; TEST_HISTORY203. Hardwarepending,stable100/stock64KB/referenceprojects unchanged.

2026-11-10 r129 L2 stopped-boss foreground composition8689,218artcells/70empty skipped,actor-ownedbackground restoration;13body/art unchanged;two700update actualvisiblepixeltests/12transitions6bossroutes/3coldfire/contracts PASS. Matched CPU cycles down10.09% vsr128,hardwarepending. build\fullgame\l2_pre_copy_r129\RType_TS2068_r129.zip SHA58dc29c371a9d768e9442e557d519af8c5aede247bed8fd98927ca7ded1590c1. TEST_HISTORY204. Stable100/stock64KB unchanged.

2026-11-10 r130 L2 nativeIRQ star erase/draw occlusion while7A8Estopped,x64..255;leftstarsremain. Noextra redraw/artwork changes.9728nativecases/700liveIRQzero bosswrites;two700visiblepixelruns/12transitions6bossroutes/contractsPASS. HOMEbank5unpatch visibility4F then6Faudited. CPUchange+0.3160%vsr129. build\fullgame\l2_star_guard_r130\RType_TS2068_r130.zip SHA697a6f02faebbb31fb9bf3396220444650c7a1cbd7d71408d2c9f29e691bafa1. TEST_HISTORY205;hardwarepending;stable100/stock64KB unchanged.

r130 final reproducible archive SHA8c3dd11edfbd228cdf1565417953680c1a926b8191f4638a7e568bf4414fc138; TEST_HISTORY206 supersedes205 ZIPchecksum only; binary unchanged.

2026-11-12 r131 L4 reuseexactapprovedghost32/Chead32/round24: native19..21/5..9/28..31.11exportverifiedframes,600ordinary+400bossupdates/12transitions/RAMsource-lifetime/tapesZIPPASS. build\fullgame\l4_shared_r131\RType_TS2068_r131.zip SHAbe0fd3d3e66712d392b6995290e11db4ee2b0ba8bb5c2c328057a3bcaafeef97. TEST_HISTORY207;comparison build/graphics/l4_shared_review_r131/confirmed_families.png. Hardwarepending,other7levels/stable100/stock64KB unchanged.

2026-11-12 L4native33..35 snake arcade1538/1540/1542/1554matched, interactiveeditor build/graphics/l4_snake_converter/index.html;24default/sharedRPCsettings/4orientationexport.32core+Chrome/ZIPchecksPASS,HTMLSHA1aa86d842799181e7ea5e53b1ef4bc240fc04118e722064e715045e8da27fa39. TEST_HISTORY208. Assetpreviewonly; game remainsr131. Awaituserexportbeforeintegration/orientationmapping.

2026-11-12 Twin-launchereditor build/graphics/l4_twin_launcher_converter/index.html usesuserselected1538singleview;1538secondfacing/1042uprightcandidate separate. Corrects208unsupported1540/1542/1554familyclaim: snakeeditorisolates1538andmarksothersunverified;snakeidentity/posemappingpending.32core+Chrome/ZIPchecksPASS,launcherSHAda7b41ae3c7541f878a71a08ce7fd54c364604b61cc26f9ed608c903d352cb46; TEST_HISTORY209. Game remainsr131.

2026-11-12 L4 boss killability NOT verified: three HP32 weak-point actors draw via native fallback but never publish collision owners in400-update probe; occupied-cell compositor rejects their overlays on hull. True victory F59D/7A84=65 not observed. TEST_HISTORY210. Must repair weak ownership/occlusion and test real-shot defeat before claiming playable boss; r131 archive unchanged.

2026-11-12 r132 boss targets: L4matching-parent collision+visible green alignment/rear24x16, actual96shotdecrements+nativeF59Dvictory at237updates; L1openeye/L3gun-engine metadata repaired.8sceneownership audits/252gatewaycases/3coldfire/12transitions/16tapesPASS, other5regionsunchanged. build/fullgame/boss_targets_r132/RType_TS2068_r132.zip SHA4d673a78e55d594c894f2855ff6d8d6053837c6d66014a2a9625afeb6cef98c5. TEST_HISTORY212; hardwarepending; otherbosses notall defeated. New allocation ends in walker_runtime/generic_manifest/l4_shared_contract must be preserved. Stable100/stock64KB/referenceprojectsunchanged.
2026-11-12 twin-launchereditor nowincludes native52/53diagonal/54 with optionalshared symmetric material shading; silhouette/holes preserved, RPCaftershading, browserPASS. TEST_HISTORY211. Preview only, not installedart.

2026-11-12 r133 selectedL4twinlauncher24x24 native52upright/53diagonal/54horizontal ->184/185/186, exactsettings83/39/40/74/1.12. Fourstream safeinitialization, rawB0C0..B270 plusoldB280..BFE0; codeA985/immutable39C7.432new+3424oldRAM/5744cache/600updates/posehooks/12cachedtransitions/coldfire/16tapes/nativeL4victoryPASS. build/fullgame/launcher_r133/RType_TS2068_r133.zip SHA396ec44107bc2d2245b1a5a1da735ad887edf95ba51784862f6016a4566e0de2; TEST_HISTORY213. Other7regions/r132bossfixes/stable100/stock64KBunchanged; hardwarepending.

2026-11-12 snakeconvertercleaned: onlynative33/34/35, allwithdrawnlauncher candidates/gallery/reference removed; arcade matchpending. Savedsliders/notes retained, invalidoldsource->current. Browser/3frameZIPPASS; TEST_HISTORY214. r133gamearchiveunchanged.

2026-11-12 snake reference correction: restored3arcadeframes1540/1542/1554; onlyfirst1538missilelauncherexcluded. Arcade/nativechoices and sharedRPCcontrols available, oldreviewsource/settingsretained. Browser+ZIP PASS; TEST_HISTORY215 supersedes214native-onlydecision. Gameunchanged.

2026-11-12 r134 selected L4 snake integrated: native33/34/35 ->189/188/187 (source2/1Yflip/0),24x24,432exact paired bytes. Final DOCK6 DA00..DBB0 allocation avoids packed reload sources and D800 IM2/D910 scratch. Cold600updates,12cached transitions/exactRAM,unmodifiedfire,real-shotL4nativevictory,16tapes/staticcontracts/ZIP PASS. TEST_HISTORY216. build/fullgame/snake_r134/RType_TS2068_r134.zip; complete folder replacement/reset. Other7regions/r133launcher/r132bossfixes/stable100/stock64KB unchanged; hardwarepending.

2026-11-12 r135 L4 direct prepared-cell copy for empty/same owner, compositor retained for other owners.11bytehelperDOCK6DBB0..DBBB appendedsnakepacket; no art/collision/projectilechanges. Matched nofire emulation+4.595%cadence (modest, significant speedup not achieved).600updates/12transitions/coldfire/real-shotnativeL4victory/16tapes/staticZIP PASS; hardwarepending. Candidatebuild/fullgame/l4_speed_r135/RType_TS2068_r135.zip SHA24e966c25cee8d606e17e0a22dc5b06f61b7cfe786c16fb085a1b19eb14f80f3. Actualtargetimagebuild/fullgame/snake_r134/L4_targets_marked.png. TEST_HISTORY218. Stable100/stock64KB/referencesunchanged.

2026-11-12 r136 L4 BB two natural weapon collectibles, live pickup->power2->rear docking->native rear laser PASS. Force recall everyupdate vs1/4; Bits1samplelag vs3; nativeunit/600updates/12transitions/cold1,4,5/fire/entrancephaseL4victory/16TAP/CORE/L5reservedmemory/ZIP PASS. Candidatebuild/fullgame/boss_pickup_r136/RType_TS2068_r136.zip SHAc19c2843f90c6620524071105f3de2cf4b29943a517f27ed687b707000f17a00; hardwarepending. IMPORTANT targets do not have proven open/close behavior; all-alive120update collision map confirms hull obstruction. Previous entrance kill does NOT establish settled fight reachability. Geometry repair pending user preference(exterior targets vs hull gaps); r136equipment fix does not repair obstruction. TEST_HISTORY219 supersedes218closed/open wording. Stable100/stock64KB/referencesunchanged.

2026-11-12 r137 restores L4 native Spectrum gaps(78emptycells;47hadbeenfilled), original target coordinates/sizes24x8,8x24,24x8 and original motion scripts. Withdraws r135directcopy after actual screenshots exposed repeated rows; proven compositor restored. Actual native-vs-ECM animation comparison/annotated openings inspected. Settled realweapon test waits200updates, native32hits/target thenF59Dvictory613; protectedplayer/noenemyHPtimeredits. Matched settledbenchmark20.34%fewercycles/25.53%highercadence vsr136 (emulationonly).600updates/12cachedtransitions/cold1,4,5/fire/pickups/rearForce/followers/16TAP/staticZIP PASS. Other7regions/CORE bitidenticalr136, L5untouched. Candidatebuild/fullgame/l4_openings_r137/RType_TS2068_r137.zip SHA8e6989a45b79d1b30818141436cf285c6679128025e4989f8bfdd9d83213239d. TEST_HISTORY220; hardwarepending. Supersedes earlier flawed L4target offsets/r135fastpath; stable100/stock64KB/referencesunchanged.


L7 walker review (2026-11-12): native14-17 closest match arcade450/452/454; interactive editor at build/graphics/l7_walker_converter/index.html. Shared RPC settings, actual three arcade poses, 24x24 default/32x32 optional. User selection and native pose mapping pending; no game integration. See TEST_HISTORY entry221.


2026-11-12 r138 high-score candidate: post-death92EF routed through shared19D2 restore; existing17-byte helper restores standard mode and clean standard attrs via1466/0073. No new allocations/art changes. All8 injected post-game score-display probes, L7 attrs/render, tape/ZIP/staticdiff PASS; natural death/name entry and hardware pending. build/fullgame/highscore_r138/RType_TS2068_r138.zip; TEST_HISTORY222. Stable100/prior releases unchanged.

L7 red/yellow/green native37 review: build/graphics/l7_round_enemy_converter/index.html; arcade598 tentative only,36/586 excluded. No integration; user identity review pending. TEST_HISTORY223.

L7 native35 yellow asteroid/orb editor: build/graphics/l7_asteroid_converter/index.html; tentative arcade6/7/5 separate alternatives,16default/24/32proposals. Identity review pending, no game integration. TEST_HISTORY224.

L7 native51 emerging object uses wrong historical49source stretched24x48. Original/current diagnostic and interactive review build/graphics/l7_emergence_converter/index.html; original silhouette default, arcade2248/2982tentative. Identity and replacement pending; no game patch. TEST_HISTORY225.

L7 wall41body/42-45movingparts review build/graphics/l7_wall_converter/index.html; arcade704cyanlensstrongmatch,692relatedview, fullassemblymappingpending. No integration. TEST_HISTORY226.

2026-11-13 L7fourchosenZIPsvalidated/staged; wall692+704confirmedadjacent(+32x,samey), assembledinteractivebuild/graphics/l7_wall_assembled/index.html; native42->43->44->45->44->43holdratio26:1 traced. Optionalcoolwalkerinteractivebuild/graphics/l7_walker_variant/index.html, selectedoriginalretained. Gameintegrationr139experimentFAILEDstartup/cachedintegrity;DO_NOT_USE/noZIP,source-lifetimeauditneeded. Currentr138unchanged. TEST_HISTORY227.

2026-11-13 r140complete6-packL7candidate: white14-17,cyan30-32,orb35,round37,emergence51,splitwall41fixed/42-45animated. Combinedplanarloadpacking,39FBend,5bytesheadroom;nativeD300scriptstorage/IM2preserved;nativeerase/source masksupdated.600firing/2160wall/12cachedroutes/coldfire/highscore/256vectortarget/static20TAP/ZIPchecksPASS;hardwarepending. build/fullgame/l7_all_choices_r140/RType_TS2068_r140.zip SHAd1a29adec8bc131bec1417ed07ea0998db98e2af7a4b56e75b0266bb7175e696. L7preparationadds~4.8scodecCPUtime. TEST_HISTORY228 supersedes227unfinishedintegration; r139notforuse. Stable100/stock64KB unchanged.

2026-11-13 r141L4bossweaponrecovery: column>=73checkpointoffers2ordinaryForcepickupsat12/14,row10whenpower<2andbothslotsfree. Noautoequipment;existingpickupsretained;BBunchanged. Twoactualnative death/respawn/recollect/reardock/rearfirecycles,12cachedroutes,no-bypasscoldL4fire/staticTAP/ZIPchecksPASS. OnlyL4bank0helper/inputandversionchanged;allr140L7artretained. build/fullgame/respawn_pickups_r141/RType_TS2068_r141.zip SHAb5fae1c47d52a60b5f175a660a797418ea25abeaf75294a97d3fbaa3ba2f68bd. TEST_HISTORY229;hardwarepending. Bossauditsmustcoverequipmentlossandrecoveryafterdeath.

2026-11-13 r142 L4 health16per target(previous32),48registeredhits total. Native victory/recovery/staticTAP/ZIP PASS; allr141pickup/artretained. build/fullgame/l4_health_r142/RType_TS2068_r142.zip SHAb7618e84827c9bb63dfeb1c9f45551ca2120f1730646d4cfef60ef158b63add2. TEST_HISTORY230;hardwarepending.

r143 original native score palette restored alongside standard-mode repair; L4/L7 phase/static tests PASS, hardwarepending. build\fullgame\score_colour_r143\RType_TS2068_r143.zip SHA6ca7533e7acbb95bb56c9b8842bc58f103c762a1182a9a4b6d6bebd85bde8a09 TEST_HISTORY231.

r144 clean/silent smalltext L7preparation onbothcold/runtimegateways. Stable293frameprep/realcoldfire/12cachedroutes/allTAP PASS,hardwarepending;other7regionsunchanged. build\fullgame\preparing_r144\RType_TS2068_r144.zip SHAcdd1f75ac85d31ec724c22dd12b285dc98054799a8db92e0542a1d59f89dd5bd TEST_HISTORY232.

r145 fast normal/spread collision now uses existing displayed-frame F880owner map acrossall8levels instead offutureworkingmap. Corrects earlier native-descriptor-only footprint inference. Actualcompiled footprints alreadyowner-expanded; no blanketinflation. Negativecontrols/nativeHP/gaps/reusedactor/14alllevelroutes/coldL1L5/L4victory/L5vectors/staticTAP PASS. Source663bytes retires23obsoleteL5flipcachebytes;currentactiveart/IM2 unchanged. build\fullgame\visible_hits_r145\RType_TS2068_r145.zip SHAbb0c9311569bbb3c688de3fa2cc36816f69b0a2397275c7228d55a45799eefcf TEST_HISTORY234;hardwarepending.

2026-11-13 individualcartridgesrequested; INCOMPLETE r146workarea build/cartridges/r146_work. All8oldnativeall-ROMfoundationsretested150updates/normalkeyrestarts/noROMwrites/no deathbypass. Currentr1458payloadsZ80LZpacked+roundtrip;noneexceed64KBstorage. CurrentECM stockRAM/runtimeadapters unfinished;no newplayablecartridgepublished. docs/individual_cartridges_r146_work.txt. Do NOT confuseoldnativeROMswithECMpreviews(3RAMbanks)orpackedinputswithPicoROMfiles. TEST_HISTORY235.

2026-11-13 r147 stock-ROM actor-cache trial: current L1 actor art70frames/307rows,1497B max HOME frame cache,467B permanent kernel, compressed ROM storage/music relocation.1760exact direct/retained component comparisons+600native updates/no death bypass/0ROMwrites PASS; no hardware/full-level claim. Experimental build/cartridges/r147_work/RType_L1_stock_actor_trial_r147.zip. Latest terrain/player/projectile/title/audio/code parity and other7cartridges unfinished; r145/stable100 unchanged. TEST_HISTORY236.

2026-11-13 USER RELEASE HOLD: integrate all current art/renderer/gameplay acrossall8cartridges before next release; keep component builds internal. integration_work matrix/gate rejects publication. All8 actor-cache internal builds now17632rendercomparisons+150nativeupdates/level/0ROMwrites PASS; L2snake role+3/4/10phase adapters ported. Terrain/currentplayer+projectile/control/title/audio/compositeboss parity stillpending. Rejected direct-terrain capture markednoteligible. No new release, stable100/r145unchanged. TEST_HISTORY237.

2026-11-13 internal stock integration advances: all8 current actor/common caches + actual one-pixel player/native copy/IRQ and independent projectile/main-loop damage hooks now pass23392render comparisons,150native updates/level and2048explicit vector-return probes,0ROM writes. Scripts validate_stock_integration.py; current_component_run.json hash-binds final ROM/evidence. L7 C4palette scratch assumption fixed; retired indexed-CB relocation errors/SFX reclamation/bootstrap stack hazards fixed. NOT release-ready: terrain/group palettes/composite bosses/title/audio/controls/recovery/full-game parity remain pending, full matrix heldfalse. No ZIP/latest changed. TEST_HISTORY238.

2026-11-13 internal stock integration T239: exact ordinary terrain/current gap groups, runtime-generated title delta atlas with safe HOME lifetime restoration, native controls/pause/music/BB pickup, cartridge completion/replay and L2 moving/stopped rich boss body now linked. Selective L2 repair preserves actors and uses320explicit free HOME bytes cleared on reset. Added live boss stress and actual one-pixel colour/bitmap scroll tests; expanded all8 validation running. NO new ZIP/release/latest pointer. Full boss/motion/death/score parity and final publish gate remain unfinished; see TEST_HISTORY239 and hash-bound internal summaries, not component counts alone.

T239 final: all8 rebuilt/hash-bound internal suites PASS, including current title/control/completion/score paths, actual8phase pixel+colour scrolling and240update boss stress;16real native death/respawn cycles after simulated hits pass/no bypass/0ROMwrites. L4 defeat is NOT established (two targets hit16times, front0); parent-specific visibility trial failed pickup integration and was withdrawn. Common perlevel captures with lost palettes rejected. These substantive blockers mean cartridges are still NOT finished or released. No new ZIP/latest pointer. Final current_component_run.json includes all8 final ROM hashes/evidence, matrix remains held.

2026-11-13 T240 finishing: corrected perlevel common capture plane and actual actor write capture; L4 victory now PASS48native hits (pilot aim corrected, original occupancy gate retained). Fixed real native pickup race by synchronously marking fine player ownership before world pickup checks; two actual-death/recollect/rear-fire cycles PASS. L2 all art fits via phase/common lookup dedup and safe ROM6 sparse deltas, no dropped frames. ECM normal-black and real five-life game-over/score flows integrated; final rebuilt suite and package acceptance running. Expanded r145/stable100/reference projects unchanged; see T240 before assuming release completed.


T240 COMPLETE: all8 stock64KB read-only cartridges released separately as r148: build/cartridges/r148/RType_TS2068_64K_cartridges_r148.zip SHA256 f0a0e6573317a3147197007678208eac0a8443ecfb741d9412161f4b9d552f77. Full software suites/data/audio/RAM contracts,96requirement release gate, archived hashes/CRC/ROMBIN/DCK checks PASS. Current art/effects, fine player, independent shots, title/controls/score/recovery/completion integrated; stock native boss event cadence retained. Physical hardware testing and all-boss/name-entry coverage not claimed. Stable disk r100/r99/r145 unchanged. See docs/STOCK_CARTRIDGES.md and TEST_HISTORY240; supersedes prior unfinished-stock status.

T241: r148 hardware regression reported; withdraw completion recommendation. Missing short-shot gateway submission fixed across all8 internal ROMs, baseline0vsfixed6shots verified; L4 both joystick sockets also pass. Targeted L4 r149_shooting_test only, NOT full release. Ghosting/music pacing/enemy and liveBB responsiveness remain unresolved. See TEST_HISTORY241.

T242: cartridge must preserve TAP gameplay rules. Restored current r145 TAP alternate-IRQ player draw and busy-copy fire capture in stock adapter, with reference-binary-anchored tests/all8 component regressions PASS. L4 live150updates/vectors/boss pilotPASS. Targeted r150_tap_schedule_test only; hardware ghosting, audio/world pacing, liveBB and full gameplay parity unresolved. Archives/latest unchanged.

T243: confirmed ghost old_mask page-borrow bug and no-enemy title-restore live-header reset fixed. All8 actual menu-start enemy selection/nonzero eventpointer/150updates +80four-direction publications/no ghost bytes +initialized title-header restore +fire/schedule/vectorsPASS. L4 controls/real5deathgameoverPASS. Targeted r151_ghost_enemy_test L4 only; no full release/latest promotion. Hardware/music pacing/other graphic artifacts pending. See TEST_HISTORY243.

T244 L1 last walker after boss setup verified: all12publishedcells take bullet damage, native missiles3damage bothdirections, moving normal/held pilots8hits+native death flag, actual TAP reference8hits too. All8artownership23392cases and displayed/future/empty/terrain/reuse damage controlsPASS. No new health/collision/runtime edit needed beyondT241..243; L1export r152_l1_collision_test now available. Not all armor/boss/weapon trajectories/hardware coverage; seeTEST_HISTORY244.

T245 L4 block corruption fixed in compact/global color bridge: dictionary IDs no longer become raw neighboring attributes, global refresh resolves actual8x1pairs; art/gameplay unchanged. Archivedr151live negative7blocks vsfinal0. All8rebuilt global/art/ownership/scroll/player/fire/IRQ/damagePASS; L4live/title/scores/gameover/controls/boss240stressPASS. Split84+24bytes fitsL2ROM without droppedart/newRAM. Scoped r153_colour_fix_test all8exports, L4directROM available; hardware/fullrelease pending. SeeTEST_HISTORY245.

T246 actual TAP/cartridge paired audit: all8 early120update actor/event/control tests match (L8controlled ROM RNG), but overall parity FAIL. Fixed internalL5 event arrangement24->12/currentTAP; later bossmotion L1/L2/L5 stilldiffers. L2FBD0-onlypalettecorrection insufficient: unported row-inkpath remains. No newrelease/export. See build/cartridges/tap_comparison/REPORT.md and parity_gate.json; TEST_HISTORY246. Do not declarecartridges equivalent/ready.

T247 L1cold double-B fixed: inheritedFD4B193blockedchord; neutralpollnowclearsinvalidlatch. Actualcoldkeyboardloop/exportedr154L1PASS, controlsall8PASS, L1fire/walkerPASS. build/cartridges/r154_l1_boss_key_test/rt_l1_r154_test.rom. OtherT246parityblockers andL7longinputpollgapremain; notfullrelease.

T249 L4smallwhite/greenchain erasurefixed: nativeFAhitclearedcollisionbutr153transparentblankfragmentsleft35pixels; L4IDs64..95nowretainopaqueblankcells.Nativeerase+ordinarybolt35->0;fullL4regressionPASS,3344art/ownershipoverdrawcasesPASS. Scopedr155_l4_orb_test/rt_l4_r155_test.rom exactexportPASS; notfullrelease/hardware/TAPparity.

T250 L1pilotmessage: confirmedpausebackupoverwrotenativefont. PauseborrowsdecodedframecacheunderDIandinvalidatesbeforeEI;all8pause/font/twodeathmessagebytechecksPASS. Actualmenu-baseddeathfixturecorrected. L1currentregressions+resumedchargedassertion/bossstressPASS; scopedr156_l1_respawn_test/rt_l1_r156_test.rom exactexportpause/twodeathPASS. Nativechargedbeam5postlethalcontactslogged,notruntimefixed. No fullrelease/TAPparity/hardwareclaim.

T251 coordinatedparityworkACTIVE. L2actualrowinksported(global2560checks/bodyPASS); sourceTAPleftedgecolorartifactsremain168samplepixelcomparison, stockmatchesintendedrowinks. L2currenteventEAE9x19ported/all8eventcontracts; L2boss120fullactor/eventstatesnowmatch. L1bullet4/L5HP28statedifferencesunderinvestigation; stockearlyownerpublicationremovedEXPERIMENTALLY,testpending. No release. SeeTEST_HISTORY251/build/cartridges/tap_comparison.

T251 2026-11-14: all8 shared-fix baseline suites PASS, internal t251_static_baseline preserved. L2 initial flipped/direct row shading repaired as well as global/retained paths. HOME8000 occupied. Opt-in exact TAP 2px motion L3/L6/L8 isolated tests PASS, complete post-reset suites running. L2/L4/L5/L7 fractional ports remain; no newrelease/readiness claim. See appended TEST_HISTORY251.

T251 six exact-motion ports L2/3/5/6/7/8 fullsuites PASS; default config enables them. L7 lossless compact snapshot saves480RAM with full64-row player window. L4 full fractional phase storage still fails and is isolated; working default L4 restored. New lossless metadata optimization all8 awaits coordinated rebuild. TAP L7 coarse projectile death bypasses invulnerability; diagnostic shield comparison separate from real gameplay. No newrelease. See appended TEST_HISTORY251.

T251 latest: Default lossless table/palette compaction validated across all8 cartridges. Six moving-boss fractional ports remain enabled; L1 static boss. L4 full fractional artwork unresolved in64KB, default whole-cell path passes component and paired-state checks. L1 optional IRQ-decode pilot failed ROM-write guard and was withdrawn; default L1 rebuilt/fullsuite PASS. Final hash-bound paired runs in progress; scripts/summarize_current_stock_integration.py rejects stale evidence and retains publish_ready=false. No latest/public artifact promotion.

T251 visual acceptance FAIL: completed-frame comparison exposed L2 entrance silhouette and other boss composition differences. All8 components/all16 protected paired actor/event cases pass but do not establish artwork parity. L2 IRQ-cache guard and cleanup metadata fixes retained; naive rich-entrance substitution rejected after live visual corruption and reverted. Need native copied-tile stable96-row palette/header translation. L4 fractional storage still unresolved. No public release; do not describe current internal cartridges as TAP-equivalent.

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
