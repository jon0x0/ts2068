# Diagnostic design change log

## Soak stop summary and clearer fault pitches

Stopping RAM soak with no recorded errors now shows **No failures during the test**, preserves the hexadecimal completed-pass count, and waits for a fresh key. Existing errors take priority and enter the chip/bit reporter. The infinite run is not labelled incomplete. Both editions implement the summary; tests cover zero/multiple/wrapped counts, held-key quarantine, fault priority and lost display writes. Cartridge packed loaders now share bounded ROM bank setup routines, freeing ROM0 space without using RAM control or a stack.

Fault synchronization is now approximately153Hz and counting beeps429Hz, giving roughly2.8:1 pitch separation. Sync remains1.18sec, counting0.595sec, and all pauses are unchanged. Actual FE timestamp verification checks pitch separation, envelopes and gaps. Introductory text now explicitly mentions the simplified U16 replacement HOME ROM diagnostic.

## Explicit results for every individual RAM test

Patterns/walking, March C-, address data, random and write/hold/read now show **Selected checks PASS** after successful completion. Complete RAM retains **All 6 RAM chips PASS**. Both pages wait for a fresh key press; the selection key cannot dismiss them. Mismatches still enter the chip/bit reporter, and cancellation does not claim a pass. Actual assembled partial algorithms and persistent-result/new-key behavior are covered by the RAM verifier. The CPU beep guide now explains once-only stage progress versus repeating failures, with a concrete 8/pause/3 example.

Joystick directions and Fire now distinguish green/currently active, cyan/previously observed and released, and white/unseen. Repeated press/release transitions continue to change green/cyan independently on both ports. History is display-only attribute data; it does not control execution. The qualified helper is96 bytes including padding; its checksum follows at3F60. Verification exercises eight consecutive transitions for every combination on both editions.

## U16 HOME reset edition and graphical joystick entry

Added separate16KiB HOME ROM build starting at0000 without stockOS/DOCK/EXROM contents or RAM initialization. Its compact subset reuses stackless RAM, earlyCPU, audio, keyboard, joystick andIRQ routines; forces HSR00 and excludes external transfers/video/CRC. Installation identifies U16, cites the original23128-to27128 incompatibility and gives isolated pin1/27 adapter connections. HOME reset/data-fault/all-writes-lost/Full/IRQ tests and an independent Fuse reset checkpoint are image-bound.

Main J directly opens joysticks in both editions with held-key edge quarantine. Two spatial pads independently show all five contacts, including diagonals/fire/opposites, and retain raw bytes/EAR. A96-byte ROM helper at3F00 is qualified from lowROM before guarded execution; all control/destinations remain registers/ROM and mapping is restored only from the lowROM bridge. Cartridge ROM1 allocator now reserves3F00-3FCF. All32 combinations per port, release/isolation/cancellation and helper corruption are verified on both editions. No automatic presence/contact certification or physical acceptance is claimed.

## Complete RAM result and menu capability

Successful selector0 Complete RAM, including heldR startup, now displays All6 RAM chips PASS with all six ref designators and covered-comparison limits. It waits for a new input edge, quarantining a held startup/selection key. Quick startup, partial algorithms, Full dispatch, overnight counting, failures and cancellation retain separate paths; no broader RAM claim is made for those short tests. RAM menu states that failing chips can be identified. Result dispatch, fault exclusion and acknowledgement are verified; Complete RAM timing is measured to its result rather than automatic menu return.

## Beeper border feedback correction

The three-tone beeper routine previously wrote FE15/05, leaving the border cyan during both waveform halves despite the UI claiming color changes. Now E-derived FE12/02,13/03,14/04 (hex) keep speakerD4 toggling while holding low/red, mid/magenta and high/green. The screen and manual list these colors. Strengthened runtime verification checks700 high and700 low writes for each color in order, rather than only counting speaker-high writes. Cancellation, fixed-ROM control, tone lengths and final silence remain.

## Slower fault-code pacing

Increased counting-beep silence from~0.12s to~0.41s, group silence from~0.57s to~1.30s, and sync-following silence from~0.45s to~0.89s. Tone lengths/pitches and code numbers are unchanged. All waits remain bounded, register-only and independent of RAM/interrupts. Shared pulse-group changes affect fault codes and training examples, not normal beeper/AY playback. Added actual FE-output timing verification; updated RAM sound-code guide and manual.

## Expected duration hints

Measured the exact assembled sequence in TSRun and documented nominal-clock model estimates. ROM screen assets now show Complete84s, patterns41s, shorter RAM options, Full~4min to keyboard/~8min total, startupR~1.5min andF timing, keyboard~4min timeout, beeper15s, AY22s, and overnight~1.5min/pass until stopped. Timings are guidance, not a live countdown or physical measurement. No runtime test algorithm, polling budget or control flow changed. Added exact6912-byte execution comparisons for seven changed packed-screen loaders and preserved duration evidence/reproduction scripts.

## Graphical keyboard from Josef's TSRun artwork

Adapted the verified533x191 source PNG into native keycap graphics, preserving stagger/wide keys and adding readable embedded labels. Whole-key green/held, cyan/released and white/unseen PAPER highlighting now uses non-overlapping fixed rectangles. Both CAPS share their contact; BREAK has accurate CAPS+SPACE history distinct from ENTER+SPACE exit.41 optional history bytes remain non-control data. Added44-case keyboard execution evidence, source/provenance credit, manual capture and bounded raw artwork loaders with a safe ROM3 source window. Full/default fault containment and physical-acceptance limits remain.

## Operator introduction

Added an introductory chapter before the operating instructions: purpose and available coverage, detectable fault examples, schematic-aware reports/pulse fallback under failures, interpretation and unavoidable launch/execution/output limits. Current ROM-only capabilities are distinguished from future Pico/NMI/external assistance and physical acceptance. Capture/decoder placement is keyed by chapter title so inserting chapters cannot misplace illustrations. Firmware unchanged.

## Official product name

Adopted TS2068 Diagnostic Lab cartridge in PDF cover/metadata/footer, web manual heading/title and release notes. Canonical PDF and packaged PDF renamed TS2068-Diagnostic-Lab-Cartridge-Manual.pdf; links and packaging script updated. Firmware bytes remain unchanged.

## Explicit Full coverage and completion

Menu1 coverage overview with guarded1-to-start/M-to-return; F startup still direct. Full completion after keyboard exit/timeout states matched digital RAM/bank/AY comparisons, user-observation requirements and excluded tests. Cancelling does not reach completion; held keyboard exit input is quarantined. Added operator coverage/checklist documentation and manual chapters/screenshots, with actual sequence/navigation checks.

## Mixed-case TS2068 interface

Menus, headings and ordinary instructions now use mixed case with the existing embedded96-character stock TS2068 font. No extra glyph storage, runtime HOME font dependency or control-flow change. Hardware abbreviations, key identifiers, physical keyboard legends and large attribute-coded fault glyphs retain their deliberate capitalization. All image formats and manual screenshots are refreshed together.

## Minimal boot CPU and bus-path checks

Added ROM0-only three-stage register/math/shift consistency before HOME writes, then qualified55/AA opposing pairs across16 HOME address bits after successful default00/FF. Preserved families8/9 with boot repeat-until-reset behavior; mixed-data failures join the RAM chip classifier. Moved embedded font toDOCK ROM1 with fixed overlay/restore around rich glyph rendering; no RAM stack or optional ROM2 execution at boot. New27-case boot injection evidence plus full regression/native checks. Native RAM harness now qualifies mapped cartridge bytes before arming, avoiding false HOME0100 matches. Replicated/global opcode-fault survival remains unimplemented and physical validation pending.

## Initial design baseline

Established the ROM-only scope, physical RAM nibble mapping, low/high ROM execution anchors, resource qualification and border/beeper reporting. Defined RAM, SCLD, ROM, video, keyboard, sound and accessory tests. Generated packed video assets and recorded ROM identities.

Added banking stress, the matched published Sinistar startup profile and interruptible overnight tests with first-failure retention and workspace recovery. Added a canonical test registry, generated catalog and project handoff instructions. All target diagnostic tests remain specified; no target firmware or physical validation is claimed.

Future entries should identify changed test IDs, the behavior/algorithm change, compatibility implications and new validation evidence.

## Crash avoidance requirement

Made stackless ROM scheduling/recovery/reporting mandatory for default RAM, banking and soak paths, including after RAM qualification. Distinguished guarded RAM state from safe control flow, specified fixed-checkpoint basic interrupt testing, and separated exposed gateway/execution/advanced-return modules. Added recoverable-fault outcomes and required fault-injection evidence.

## Firmware version 0.1

Implemented native LROS entry, stackless full RAM patterns/walking bits/March C minus, register-held first fault/error unions, chip/nibble-bit output and three-choice healthy menu. RAM-01/03/04 are implemented; BOOT-01,RAM-05,UI-01,AUD-01 have partial supporting code. Added reproducible build, source/phase manifests and execution checks. TSRun30 scenarios plus24 reporter mappings pass; Fuse1.7.0 stock-ROM boot reaches the menu. Physical validation, runtime integrity, alias/random tests, cancellation, comprehensive menu and soak remain pending.

## Mark Miller 128 Colors reference

Added VID-05 for all128 INK/PAPER/BRIGHT combinations, an independently generated checkerboard overview with exact coverage checks, and a planned bounded full-screen cycle. Credited Mark Miller and the TimexSinclair.com archive, and added a project-wide source/tool/embedded-data credit record. Target firmware v0.1 is unchanged.

## Optional PicoVideo profile

Added PV-01 through PV-06 for documented-profile palette/CLUT tests, native modes, captured display writes and bounded exit/recovery. Tests are opt-in and separate external output from native SCLD evidence. Credited Jeff Burrell, contributors and the referenced format/VGA sources. No target firmware changes.

## Schematic aware fault text prototype

Added UI-03 and host prototypes for surviving pixel lanes, duplicated attribute panels and large attribute-coded glyphs. Check32 stable U6/U7 nibble fault values; retain distinction between modeled contrast and physical readability. Upper-RAM-only faults can use independent display storage with ROM control. v0.1 remains unchanged pending target integration and fault validation.

## Basic color bars and BRIGHT

Expanded VID-01 with an uncluttered eight-color PAPER bar card, normal upper half and BRIGHT lower half. Generated packed planes and preview; host checks verify corresponding attributes differ only by D6 and FLASH is clear. Specify a separate BRIGHT toggle and unchanged black reference. No target firmware changes.

## BRIGHT-independent color-bar labels

VID-01 adds bitmap labels and monochrome boundaries that identify normal/BRIGHT halves even if brightness is suppressed. Added a no-BRIGHT-output preview and documented output-system attribution limits. Firmware integration remains pending.

## Future hardware assistance and NMI

Added a roadmap for independent fault capture/reporting, writable cartridge RAM, independent boot, watchdogs and optional TSPico NMI button checks. Require profile-specific vector/mapping/stack-write ownership; NMI is not a safe general stop in v0.1. No firmware or sibling hardware changes.

## Runnable version0.2 suite

Integrated compressed video planes, immutable-font UI, physical keyboard layout/history, beeper/AY, bank stress,16-bit random/address/retention RAM and continuous soak. Added automatic Full digital+guided sequence, measured HOME/EXROM CRC32 and separately selected fixed-checkpoint IRQ tests. Added schematic-aware large fault glyphs with retained pulses and register-held first fault. Full64K ROM capacity is now required. Preserved v0.1 source/build/evidence; no sibling hardware changes.

Emulator validation found and corrected LD A,I flag interference in degraded fill, a low-to-high CRC mapping transition, and menu release behavior. Fuse PC-only checkpoints could falsely stop in HOME ROM; current checks verify cartridge mapping and completed RAM phase34. Current image acceptance is recorded separately. Physical validation and catalogued advanced modules remain pending.

### Failure independence refinements

Added repeating audible family counts for peripheral/mapping failures, press-edge quarantine for stuck menu keys, explicit input-safe AY direction for joystick observation, and M acknowledgment of RAM faults to run independent modules. The IRQ checkpoint test no longer requires readable RAM: saved-PC writes are discarded by fixed ROM control. Tests cover all HOME writes lost and stuck optional-test keys.

The final v0.2 candidate requires an M release before RAM/timed-stage cancellation, clamps every stress mask to keep the low ROM anchor, and emits countable white/black border envelopes for fault codes even without beeper audio.

Added optional CPU menu9/U: complementary-register, arithmetic/selected flags, shift/bit, alternate-register and IX/IY consistency;16 explicit55/AA reversed address-pair probes; family8/stage and family9/address-bit pulse reports. ROM2 now contains executable optional code4000-47FF and safe-source packed data4800 onward. Broad guarded any-key stops replace M-only stops in active tests; keyboard adds ENTER+SPACE. ECM ordered rainbow replaced by original constrained Sierra Lite diagonal gradient and saturation/hue disc. Earlier image-bound evidence is preserved.

Power-on policy: replace the approximately90-second extended startup suite with cartridge integrity plus00/FF full48K sweeps (selection8, phase2 stop), about6 modeled seconds after entry. Extended tests remain explicitly selectable and guarded any-key cancellation applies to startup. Menu label: STARTUP CHECK IS LIMITED. Correct the colorbar font-table I/G swap that displayed BRGIHT. Fuse RAM checkpoint now checks phase2; TSRun independently exercises complete sweeps.

Packaging: every build emits an explicit64K PicoROM-P28 payload plus manifest metadata; release includes512KBit loading instructions and TSPico integration notes. Four host format checks include the skill converter and isolated published TSPico DCK expansion. Added specified EXT-01 external SRAM profile. Existing firmware/DCK hash and132 emulator cases remain unchanged; no hardware upload, Flash update or SRAM probes were performed.

AY playback expanded to24 guided steps with four octave-related pitches per A/B/C channel, volume3/8/15, noise31/8/1, envelope shapes9/13/10/8, chord and silence. Active labels/progress change with actual output steps. Mute before reconfiguration, fixed register/coordinate masks and guarded cancellation preserve ROM control with corrupt data/display. Added dedicated image-bound AY runtime evidence.

Added R/F startup holds with quick default, broad-keyboard-fault rejection, finite highlighted status page and release-guarded fault retries. Border phase colors distinguish patterns/bits/March/address/random/retention without altering tested display RAM. CPU guide explains expected8/stage checkpoints, repeated8/CPU-stage or9/address-bit codes, success and software-survival limits. Replaced main-menu destructive-RAM phrase with selection guidance. Embedded cartridge-font and absent-HOME boot dependencies documented.
# Operator guidance and programming package

- Help C fault-code training: bounded RAM/bank/CPU examples using actual ROM pulse routines, with all-HOME-write-loss checks. Replaces the unhelpful NMI line in the UI.
- Colorbar labels simplified to Normal/Bright; bit6 comparison remains unchanged.
- Explicit27C512 EPROM image and programming/decode notes; identical raw64KiB bytes across EPROM/PicoROM/BIN profiles.
- Shared-content operator PDF/offline HTML with procedures, expected observations, interpretation, actual U6/U7 injected-fault images and complete development inventory.
- Address-fault replicated-recovery feasibility documented as future work; quick startup stays00/FF and does not claim to detect pure aliases.55/AA/address data remain complete-RAM coverage.

