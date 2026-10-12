# Project state / v0.2 handoff

The current UI uses mixed-case TS2068 text. ASCII32-127, including lowercase, was already present in the embedded768-byte font; no extra font allocation was needed. Physical key labels, technical abbreviations and coarse fault glyphs stay uppercase. Case conversion is host asset generation in scripts/suite_assets.py, not a runtime dependency.

The project now builds a runnable ROM-only stock-machine diagnostic suite, not just the earlier RAM-kernel milestone. Read tests/V02_DIAGNOSTIC_SUITE.md for the actual algorithms, memory contracts, controls, fault codes, optional exposures and unfinished advanced modules. The canonical registry distinguishes implemented, partial and specified scope.

## Current implementation

- Register-only cartridge integrity and all48K RAM sweeps; eight patterns, walking bits, March C-, address hash/high/low address planes,16-bit seeded LFSR,55/AA retention holds and continuous RAM soak.
- Large attribute-coded chip-path reports using a qualified surviving display nibble, alongside the established chip/bit border/beeper pulse sequence.
- Main/submenus, full digital+guided sequence, live42-position keyboard layout, normal/BRIGHT/FLASH, second display, ECM dither, hires calibration and128-attribute video cards.
- Beeper; masked AY register/address comparisons plus A/B/C/noise/envelope output and mute recovery.
- Continuous banking combinations with signature/ROM-write/HOME-sentinel comparisons and a pass counter.
- Optional HOME/EXROM CRC32, high-code shadow/gateway validation and bounded fixed-checkpoint SCLD IRQ inhibit/arrival tests. J opens graphical joystick/EAR observation directly, with independent simultaneous contacts on both ports.

All default control remains stackless in low ROM. Optional HOME checksum executes from high ROM; EXROM executes a verified HOME gateway; IRQ entry writes to a sacrificial initialized HOME sink but never reads or returns through it; it remains testable when RAM writes are lost. These explicit exposures are excluded from Full test and RAM overnight mode. NMI/helper/PicoVideo support remains future work.

## Evidence and limits

TSRun and Fuse stock-ROM validation records are image-bound and copied under docs/validation. Physical TS2068/TSPico/PicoROM testing has not occurred. Fuse breakpoints must check cartridge mapping: raw PC addresses can coincide with HOME ROM during startup. The current checks use verified cartridge bytes at0100/0102; the new quick-startup RAM checkpoint must show phase2 (02 hex); explicitly complete healthy sweeps show phase34 (22 hex), not merely a menu-shaped PC.

Initial cartridge integrity checks are additive16 over8144 bytes per chunk, not collision-resistant CRC. RAM random uses seedACE1/polyB400, with immediate first-mismatch exit to prevent LFSR scratch corruption from causing cascaded false reports. Soak counters wrap at65536; no elapsed-time or temperature measurement, persistent logging or arbitrary pause/resume. Keyboard history is optional RAM data and never control flow.

Some registry modules remain broader than their present implementation: varying seeds/dwell profiles, complete timing/whole-chunk banking comparisons, exact Sinistar runtime/interrupt reproduction, combined mixed-load soak, guided physical-key certification, calibrated SCLD contention/pin probing, full tape record/verify and external hardware profiles. Do not describe these as finished or tested.

## Hardware facts and prerequisites

HOME4000-7FFF uses U6 D0-D3/U7 D4-D7;8000-BFFF U12/U13;C000-FFFF U17/U18. Both display files share U6/U7. Second attributes7800-7AFF. DECR bit7 selects DOCK versus EXROM globally; HSR independently overlays fixed8K chunks. Modes0/1/2/6 only. Stock HOME CRC32 BF44EC3F; EXROM AE16233A. Both physical CAPS keys share a matrix contact; BREAK is CAPS+SPACE.

Passive LROS can only report after OS handoff. CPU clock, active opcode fetch and sufficient bank decode are unavoidable dependencies. Border/beeper also share SCLD. All eight cartridge ROM chunks must be supported by the physical/virtual cartridge configuration.

## Work remaining

The next release gate is physical testing: cold/reset launch, actual programmed image hash, cartridge decode, faulty DRAM/report readability, real keyboard/audio/video modes, stock ROM identities, cancellation and an overnight warm run. Record exact hardware/ROM/interface/firmware revisions and observations without upgrading emulator evidence to physical evidence. Continue advanced modules only with their explicit contracts.

Read AGENTS.md before editing. Maintain stable test IDs, implementation locations and honest status/evidence, regenerate TEST_CATALOG.md and retain source credits. Preserve user manuals/schematic and sibling projects. The Sinistar incident remains an unproven hypothesis; its exact failure symptom/interface settings are still unknown.

Current menus use bounded release/press-edge handling: stuck numeric keys do not prevent other keys working, and held H/E/I cannot silently enter optional execution tests. M acknowledges RAM failures to access independent modules; non-RAM mismatch pages retain repeating audible family counts.

Optional menu9/U now runs five stackless Z80 consistency stages and16 localized address-pair probes from ROM2, with low-ROM HOME-access bridges and checkpoint/fault pulse groups. Default startup/Full remain unchanged. Active stages accept any new key after all-key release; results accept any key. Keyboard supports held ENTER+SPACE as well as CAPS SHIFT+SPACE. ECM is an original Sierra Lite gradient/disc constrained to native8x1 pairs. Physical and global CPU-bus-fault validation remain pending.

Power-on now runs cartridge integrity and only00/FF full-address RAM checks, reaching the modeled menu about6 seconds after entry/about7 with native launch. Manual Full/Complete retain extended testing; any new key after all-key release can stop startup at safe boundaries. The menu labels startup limited. BRIGHT colorbar lettering now uses the correct I/G glyph mapping.

PicoROM delivery now includes explicit diagnostic-v02-picorom.bin and loading notes in the release. Four image-format checks confirm raw/BIN identity and skill/TSPico conversion. TSPico external SRAM test EXT-01 remains specified: selector stride/aliases, reserved memory, low-level PIO behavior and physical-cartridge ownership must be established before firmware execution. That packaging-only checkpoint retained its previous image hash; subsequent firmware hashes are in build/manifest-v02.json and immutable validation records.

User reports TSPico labels FW1.00/uPython1.20.0/default ROM1.00/board2.2. Labels may be stale, so actual firmware identity and capabilities remain unverified. Future TSPico tests must permit developmental builds through verified capability profiles, never version-string whitelists; see tspico-user-profile.json and TSPICO_DIAGNOSTIC_PROFILE.md.

AY now has24 guided steps:4 pitches per channel,3 volume levels,3 noise periods,4 envelope shapes, a three-channel chord and silence. Active labels yellow/completed dots green. Fixed ROM2 data4400-457F replaces hardcoded old playback; low-ROM control masks registers/coordinates and keeps mute/cancel bounded. Optional CPU allocation ends43FF. AY-only validation is recorded separately in ay-verification.json.

Startup now accepts held R (complete RAM) or F (Full digital+guided), rejects broad all-low inputs, highlights selection and gives a finite status notice. Default quick timing is approximately7 modeled seconds after entry/9 including native launch. Border colors identify RAM groups; reporter R retry requires release/new press. CPU menu displays expected checkpoint/failure meaning. Normal font bytes reside in cartridge ROM; absent-HOME boot remains a future independently decoded Pico profile.
# Operator guidance / current release additions

Help0/C now provides finite fault-code TRAINING:1 RAM sync/2/6/2,2 bank4,3 CPU8/3; M returns to Help. Low-ROM header helpers preserve fixed vectors/native header and remain stackless. Runtime evidence includes demonstrations with all HOME writes discarded. Colorbar labels are only Normal/Bright.

The packaged release includes TS2068-Diagnostic-Lab-Cartridge-Manual.pdf and offline manual/index.html, with actual emulated U6/U7 fault images and operating/interpretation instructions. Shared content and layout live in scripts/build_manual.py; scripts/check_manual.mjs checks offline images, decoder and desktop/mobile layout. PDF renders reviewed across all20 pages. Explicit diagnostic-v02-eprom-27C512.bin contains the same65536 raw bytes as BIN/PicoROM; EPROM_LOADING.md documents programming and full64K decode. No device programming was performed.

The previous quick baseline used only00/FF; current boot also adds the minimal CPU/qualified address-pair checks documented in BOOT_PATH_DIAGNOSTICS.md. Complete testing already includes55/AA and address-dependent patterns. docs/REPLICATED_RECOVERY_ROM.md assesses future address-fault-resistant layouts and their launch/low-bit/decode limits; no global address-fault survival is claimed. Physical acceptance remains pending.

Current boot adds always-selected ROM0 register/math/shift comparisons before any HOME writes, then qualified55/AA opposing address pairs after successful default00/FF. Boot8/stage or9/address-index pulses repeat without display/keyboard until reset. Font data now resides in DOCK ROM1 at2200-24FF; fixed ROM0 renderers overlay it briefly and restoreHSR01. No optional ROM2 CPU execution was added to boot. See BOOT_PATH_DIAGNOSTICS.md and boot-verification.json.

Full coverage UI: main1 opens overview; new1 starts; F startup remains direct. Keyboard exits/timeouts reach digital-matched summary only for selector7. Unseen/unpressed outputs are not passed, exclusions explicit. New-input edge prevents held keyboard exit chord dismissing summary. FULL_TEST_COVERAGE.md and operator manual preserve exact meaning.

Operator manual now22 pages with Full overview/completion chapters and seven actual capture images. Full sequence claims only covered digital matches plus separately judged outputs.

Current official manual now23 pages. Introduction (first chapter, PDF page3) describes scope, possible faults, degraded-screen/pulse feedback, attribution limits and unavoidable bootstrap/CPU/SCLD dependencies. Same shared content appears in offline HTML. Chapter-title mapping preserves all seven screenshot placements and the fault decoder when chapters are inserted. Firmware unchanged.

Keyboard now embeds a credited native adaptation of Josef Jelinek TSRun keyboard.png (published bytes verified). Full-key attribute rectangles retain42 positions/40 contacts, shared CAPS and derived BREAK, with41 bounded optional history bytes. ROM3 can source graphics only intoHOME4000-5FFF, never an overlaid destination. keyboard_art.py / KEYBOARD_ART.md preserve conversion contracts, short labels and source hashes; keyboard-verification.json contains44 execution cases.

PicoROM loading instructions now include official executable downloads, Windows folder/PowerShell setup, device-name selection, persistent512KBit upload and SHA256 readback. The PDF is24 pages, including a dedicated PicoROM chapter; offline HTML uses selectable command blocks and clickable upstream links. Firmware is unchanged. Commands are checked against local CLI help; no physical device programming or readback was performed.

Timing guidance adds TEST_DURATIONS.md and a shared PDF/web chapter. The current manual is25 pages. Exact-image TSRun estimates: completeRAM84s; patterns41s; March8.5s; addresses8s; random3s; retention24s. Full reaches keyboard at229s; no-contact timeout adds234s, total462s. measure_test_durations.mjs and image/model-bound evidence are frozen with the release source. These are modeled machine-time estimates, not physical acceptance timing. Firmware remains unchanged.

Duration hints are now encoded in ROM UI assets (Full, RAM menu, extended startup, keyboard, beeper/AY, overnight). No Z80 control/test algorithm changed; kernel_end remains1F4C. Seven actual-ROM-loader display comparisons verify fixed guidance labels; timings are approximate model estimates, not live counters. Current image 6697e7b0ad7b245a81984e930d7aa6133360a7e58068ae3f5e88b9a7f06538fd; current-image verification/release evidence supersedes preceding snapshots.

Current manual is26 pages. Introduction explicitly lists audible RAM-chip identification when the screen is unreadable. PDF page9 and matching web chapter give complete sync/2/chip/bit lookup tables for U6,U7,U12,U13,U17,U18 and bit1-4/multiple5, with U18/D5 example and practice instructions. RAM_SOUND_CODES.md is included in the release and source snapshot. The overnight screen says Repeats until stopped / Press any key to stop. All image-bound checks and PDF/web QA passed; physical acceptance remains pending.

Fault-code silence increased:0.408s between counting tones,1.300s between groups,0.892s after sync. Actual FE-output timing verifier confirms1.180s/203Hz sync and0.591s/304Hz counting tone envelopes, unchanged SP. Shared code/train waits remain bounded and ROM-only; optional CPU verifier budget enlarged for slower audible reporting. Current image d8186dc6689ffcac424f36a4f1da02ac5af82a8705c4a84daac7416f2624abde. Manual/lookup updated; physical timing/recognition remains pending.

Beeper border correction: waveform previously kept cyan for every tone despite UI claim. Low/mid/high now use steady red/magenta/green on both FE speaker states; onscreen labels and manual agree. Runtime verification checks700 high/low writes per color and their order. Current image 4f231f826ee70732e9539b98e726d880df0f14c4c8becef45fb7d2801029de58; control remains ROM-only/stackless, physical observation pending.

Complete RAM selector0, including startupR, now has an All6 RAM chips PASS page listing U6/U7/U12/U13/U17/U18 and limiting it to covered comparisons. Held input is quarantined via the shared Full-summary edge poll. Quick/partial/full/soak/failure/cancel selectors retain separate dispatch. RAM menu advertises chip identification. Eight packed-screen comparisons include rampass, and suite verification adds result dispatch/held-key/fault-exclusion cases. Current image 23284cc69b746faf84016419f65fc241c8d41fdb31c29759c293e80af1112964. Kernel remains within ROM0 bound; physical validation pending.

## Current result and HOME edition contracts

Individual RAM tests now show Selected checks PASS and Complete RAM shows All 6 RAM chips PASS; both require a new key. Failures retain chip/bit reporting and cancellation never claims success. The separate U16 HOME reset ROM bypasses OS/DOCK startup but has reduced coverage; see HOME_ROM_EDITION.md. Graphical joystick painting uses a qualified 96-byte ROM helper at3F00; reserve cartridge ROM1 3F00-3FCF. Packed cartridge loaders share ROM-only bank setup gateways to leave space for the soak stop summary; check kernel_end against1FD0 before adding code. Physical cartridge, U16 adapter and device validation remain pending. Current image hashes are recorded in build/manifest-v02.json and build/home/manifest.json.

Stopping soak with no recorded RAM errors shows No failures during the test and the hexadecimal completed-pass count; a new key returns to the menu. Recorded errors take priority. Both editions preserve register-only state. Fault sync/count pitches are approximately153/429Hz with original durations and gaps. scripts/verify_soak.mjs checks result counts, fault priority, acknowledgement and lost display writes. docs/RELEASE_POST.txt is ready-to-use human release copy and describes the simplified U16 replacement image.
