# TS2068 diagnostic test catalog

Generated from [test-registry.json](test-registry.json) by [build_test_catalog.py](../scripts/build_test_catalog.py). Edit the registry, then regenerate this file.

The registry contains 58 tests and diagnostic UI modules. Firmware status counts: specified 14, partial 28, implemented 16, retired 0. 14 entries reference existing host support; host support is not a target implementation.

The algorithm below describes the intended implementation unless firmware locations are populated. Empty validation evidence means no per-test emulator or physical acceptance evidence has been recorded. Implementation and validation are separate: code can exist while target validation remains pending.

Every entry must obey [FAULT_CONTAINMENT.md](FAULT_CONTAINMENT.md). Declared control-flow exposure identifies limits that qualification cannot eliminate; exposed advanced tests remain separately selectable.

## Inventory

| ID | Test | Firmware | Existing host support |
|---|---|---|---|
| [BOOT-01](#boot-01-native-entry-and-resource-baseline) | Native entry and resource baseline | partial | None |
| [BOOT-02](#boot-02-cartridge-integrity-and-chunk-identity) | Cartridge integrity and chunk identity | partial | None |
| [CPU-01](#cpu-01-register-and-instruction-consistency) | Register and instruction consistency | partial | None |
| [CPU-03](#cpu-03-localized-home-address-pair-consistency) | Localized HOME address-pair consistency | implemented | None |
| [CPU-02](#cpu-02-qualified-stack-operations) | Qualified stack operations | specified | None |
| [RAM-01](#ram-01-data-bus-walking-patterns) | Data bus walking patterns | implemented | None |
| [RAM-02](#ram-02-address-and-region-aliases) | Address and region aliases | implemented | None |
| [RAM-03](#ram-03-complete-complementary-pattern-sweeps) | Complete complementary pattern sweeps | implemented | None |
| [RAM-04](#ram-04-march-c-minus) | March C minus | implemented | None |
| [RAM-05](#ram-05-nibble-and-intra-word-coupling-patterns) | Nibble and intra-word coupling patterns | partial | None |
| [RAM-06](#ram-06-deterministic-random-comparisons) | Deterministic random comparisons | partial | None |
| [RAM-07](#ram-07-write-hold-read-under-normal-refresh) | Write hold read under normal refresh | partial | None |
| [RAM-08](#ram-08-firmware-workspace-and-guard-retest) | Firmware workspace and guard retest | implemented | None |
| [BANK-01](#bank-01-hsr-latch-and-readback) | HSR latch and readback | specified | None |
| [BANK-02](#bank-02-static-dock-selection-and-full-chunk-reads) | Static DOCK selection and full chunk reads | partial | None |
| [BANK-03](#bank-03-rom-overlay-write-isolation) | ROM overlay write isolation | implemented | None |
| [BANK-04](#bank-04-rapid-home-dock-alternation) | Rapid HOME DOCK alternation | partial | None |
| [BANK-05](#bank-05-external-response-timing-sweep) | External response timing sweep | partial | None |
| [BANK-06](#bank-06-global-home-dock-exrom-selection) | Global HOME DOCK EXROM selection | partial | None |
| [BANK-07](#bank-07-sinistar-startup-data-profile) | Sinistar startup data profile | specified | None |
| [BANK-08](#bank-08-verified-cartridge-execution-transfers) | Verified cartridge execution transfers | partial | None |
| [BANK-09](#bank-09-interrupt-and-mixed-load-banking) | Interrupt and mixed-load banking | specified | None |
| [SCLD-01](#scld-01-display-dma-addressing-and-serialization) | Display DMA addressing and serialization | partial | None |
| [SCLD-02](#scld-02-display-arbitration-and-clock-gating) | Display arbitration and clock gating | specified | None |
| [SCLD-03](#scld-03-bounded-interrupt-generation) | Bounded interrupt generation | implemented | None |
| [SCLD-04](#scld-04-interrupt-inhibit-control) | Interrupt inhibit control | implemented | None |
| [SCLD-05](#scld-05-technician-signal-and-solder-probe-mode) | Technician signal and solder probe mode | specified | None |
| [ROM-01](#rom-01-home-identity-and-repeated-checksum) | HOME identity and repeated checksum | partial | None |
| [ROM-02](#rom-02-exrom-identity-and-repeated-checksum) | EXROM identity and repeated checksum | partial | None |
| [VID-01](#vid-01-standard-colors-bright-and-flash) | Standard colors bright and flash | implemented | 7 references |
| [VID-02](#vid-02-second-display-selection) | Second display selection | partial | 3 references |
| [VID-03](#vid-03-ecm-dither-and-per-line-attributes) | ECM dither and per-line attributes | implemented | 3 references |
| [VID-04](#vid-04-hires-geometry-and-plane-ordering) | Hires geometry and plane ordering | partial | 3 references |
| [VID-05](#vid-05-128-ink-paper-bright-combinations) | 128 INK PAPER BRIGHT combinations | partial | 3 references |
| [KEY-01](#key-01-free-keyboard-press-and-release-display) | Free keyboard press and release display | partial | 1 references |
| [KEY-02](#key-02-guided-42-physical-key-test) | Guided 42 physical key test | specified | None |
| [KEY-03](#key-03-keyboard-row-column-isolation) | Keyboard row column isolation | partial | None |
| [AUD-01](#aud-01-beeper-output-and-alarm-path) | Beeper output and alarm path | partial | None |
| [AUD-02](#aud-02-ay-register-and-address-decode) | AY register and address decode | partial | None |
| [AUD-03](#aud-03-ay-tone-noise-mixer-amplitude-envelope) | AY tone noise mixer amplitude envelope | partial | None |
| [IO-01](#io-01-cassette-output-input-and-record-verify) | Cassette output input and record verify | partial | None |
| [IO-02](#io-02-built-in-joystick-input-and-isolation) | Built-in joystick input and isolation | partial | 2 references |
| [SOAK-01](#soak-01-overnight-ram-only) | Overnight RAM only | partial | 1 references |
| [SOAK-02](#soak-02-overnight-banking-only) | Overnight banking only | partial | None |
| [SOAK-03](#soak-03-combined-overnight-mixed-load) | Combined overnight mixed load | implemented | 1 references |
| [UI-01](#ui-01-resource-permissions-and-fallback-reporting) | Resource permissions and fallback reporting | partial | 4 references |
| [UI-02](#ui-02-soak-dashboard-cancellation-and-first-fault) | Soak dashboard cancellation and first fault | partial | None |
| [PV-01](#pv-01-picovideo-palette-register-path) | PicoVideo palette register path | specified | None |
| [PV-02](#pv-02-picovideo-color-channels-and-ramps) | PicoVideo color channels and ramps | specified | None |
| [PV-03](#pv-03-picovideo-attribute-clut-mapping) | PicoVideo attribute CLUT mapping | specified | None |
| [PV-04](#pv-04-picovideo-native-mode-reproduction) | PicoVideo native mode reproduction | specified | None |
| [PV-05](#pv-05-picovideo-display-write-capture-stress) | PicoVideo display write capture stress | specified | None |
| [PV-06](#pv-06-picovideo-cancel-and-mode-recovery) | PicoVideo cancel and mode recovery | specified | None |
| [UI-03](#ui-03-schematic-aware-degraded-fault-text) | Schematic aware degraded fault text | implemented | 3 references |
| [EXT-01](#ext-01-tspico-external-sram-and-slot-isolation) | TSPico external SRAM and slot isolation | specified | None |
| [BOOT-03](#boot-03-u16-home-rom-reset-diagnostic-bootstrap) | U16 HOME-ROM reset diagnostic bootstrap | implemented | 4 references |
| [LOAD-01](#load-01-sinistar-stack-data-load-reproduction) | Sinistar stack-data load reproduction | implemented | 1 references |
| [LOAD-02](#load-02-opt-in-sinistar-interrupt-return-load-reproduction) | Opt-in Sinistar interrupt-return load reproduction | implemented | 1 references |

## Prerequisites

- **native_launch:** OS initializes enough to discover LROS and enter cartridge; this is not independently guaranteed by a passive ROM.
- **rom_execution:** CPU and cartridge fetch path usable; appropriate low/high ROM anchor selected.
- **home_mapping:** ROM execution plus HOME RAM target exposed; memory contents are not presumed correct.
- **qualified_workspace:** One or more explicitly tested HOME blocks with safe mapping, guarded stack and state; display not automatically qualified.
- **qualified_gateway:** Tested HOME opcode block and verified copy of bounded gateway/checker; its chunk remains HOME.
- **usable_display:** Qualified workspace plus verified relevant HOME bitmap/attribute ranges; output requires visual judgement.
- **qualified_interrupts:** Tested stack/vector/ROM ISR and bounded interrupt checks passed; safe shadow protocol.
- **external_instrument:** Technician probe/logic analyzer fixture; any firmware-specific prerequisites still apply.
- **ay_registers_qualified:** AUD-02 passed meaningful masked reads; does not establish analog audio operation.
- **cassette_setup:** User selected cassette test and configured suitable recorder/coupling adapter; appropriate display/workspace gated separately.
- **joystick_setup:** User selected attached joystick and AY port A is configured as input.
- **picovideo_profile:** Explicitly selected PicoVideo board/firmware with verified port/mode capabilities, qualified display ranges and operator viewing external output; no blind probing.
- **tspico_sram_profile:** Operator-selected, verified TSPico board/firmware; SRAM selector/stride/reserved ranges and physical cartridge arbitration established; stable independent opcode anchor, sacrificial range and recovery mapping. Development builds permitted; reported version strings are informational only and never authorize probes.
- **home_reset_rom:** CPU/reset/HOME ROM fetch path and SCLD HOME decode usable; correct16KiB diagnostic installed at U16 with verified electrical adapter. No stockOS, DOCK, EXROM contents or RAM initialization assumed.

## Recovery contracts

- **rom_only:** Keep DI/no stack, emit bounded border/beeper report and direct-jump to the next safe ROM phase.
- **abandon_stack:** Retain compact first-fault data in registers; direct-jump to ROM recovery, DI; never RET through suspect RAM; rebuild only qualified state.
- **mapping_restore:** Finish bounded batch if safe, DI, restore known software-shadow mapping with active ROM anchor, report first mismatch.
- **gateway_restore:** Stay in qualified HOME gateway, clear HSR, select DOCK in DECR, select anchor and JP to fixed ROM entry; no ROM return until visible.
- **interrupt_restore:** DI, inhibit DECR interrupts, restore known ROM mapping through fixed checkpoints and discard unsafe return state; qualify any optional stack before later use.
- **video_restore:** Leave target memory before redraw; restore documented mode0,anchor mapping and DI/inhibit; border report then rebuild qualified display.
- **audio_restore:** Mute AY amplitudes, preserve/input-safe R7, lower FE speaker/tape bits, restore mapping; report with remaining qualified outputs.
- **soak_recovery:** Latch first fault and partial-phase status; pause/stop at safe boundary; no BASIC return; fall back through fixed ROM JP if state/stack fails.
- **picovideo_restore:** ROM-bounded profile-specific palette disable/known recovery palette as needed; restore native mode0 and intended mapping/DI; never wait for external video to resume.

## Test definitions

### BOOT-01 Native entry and resource baseline

**Firmware status:** partial. **Prerequisites:** native_launch.

**Implementation method:** Native LROS stackless entry, DI/known ports and cartridge integrity before RAM; passive OS handoff remains required. Power-on then selects quick00/FF full48K coverage only (phase2 stop); extended RAM is manual. New key after release cancels safely; menu explicitly marks startup limited. Held R/F explicitly chooses complete RAM/normal Full after narrow keyboard checks; finite highlighted status page, no dependency on release, broad all-low matrix rejects extended selection. Every boot choice now runs a separate minimal ROM0 register/arithmetic/shift consistency check before any HOME writes; mismatches repeat8/stage1-3 without display or keyboard. Default quick00/FF success adds qualified55/AA opposing HOME address pairs. Passive launch dependency remains.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** An absent marker cannot uniquely identify CPU, ROM, RAM or SCLD failure.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Passive LROS launch depends on OS initialization before entry; no firmware error report is possible if entry never occurs. Boot still assumes activeROM0 opcode/operand reads and usable comparisons/branches/registers; FE border/beeper share SCLD. Localized HOME injections do not prove global CPU pin-fault survival.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#startup-and-resource-promotion).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/diagnostic.asm](../src/diagnostic.asm) — entry `entry`.
- [src/boot.asm](../src/boot.asm) — entry `boot_cpu_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator checkpoint_completed](../docs/validation/v02-301339832d6f/fuse-v02-ram-result.json) — Fuse1.7.0 stock TS2068, mapped-cartridge quick00/FF completed phase2 checkpoint; not electrical validation..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..
- [emulator PASS](../docs/validation/v02-301339832d6f/boot-verification.json) — TSRun post-entry CPU-result, HOME address-pair/data fault injection; exact scope/limits in record; physical validation pending.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BOOT-02 Cartridge integrity and chunk identity

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Additive16 over first8144 bytes per chunk, excluded checksum/marker tails;8-chunk comparison before RAM; bank signature checks are separate. CRC32 of every cartridge chunk remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Mismatch implicates cartridge/address/data/fetch path; checker corruption can defeat detection.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#startup-and-resource-promotion).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `cartridge_check`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### CPU-01 Register and instruction consistency

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Executable five-stage ROM2 subset: complementary general-register values; arithmetic/carry/zero/sign/overflow examples and logic; shifts/bit ops; EXX and AF exchange; IX/IY byte/inc/dec (includes original NMOS undocumented index-byte operations). Checkpoint8/stage, mismatch8/stage, no RAM/stack control. Not exhaustive instruction/flags certification. Additional always-selected ROM0 boot subset checks general-register constants, arithmetic/carry/zero/sign/overflow/AND/XOR and rotate/shift/carry. No optional ROM2 transfer at boot. Detected boot faults repeat8/stage1-3 until reset.

**Observables:** Pre-stage8/stage border/beeper checkpoints; detected failure repeats8/stage1-5; matched result on completion. No full register dump. Cartridge guide explains each checkpoint and limits before CPU execution.

**Interpretation limits:** Failure identifies exercised instruction/path; passing does not certify all Z80 behavior.

**Recovery:** rom_only.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Optional ROM2 opcode execution and CPU checker/reporter instruction/register dependencies can defeat recovery. Default startup/Full do not run it. Boot still assumes activeROM0 opcode/operand reads and usable comparisons/branches/registers; FE border/beeper share SCLD. Localized HOME injections do not prove global CPU pin-fault survival.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#startup-and-resource-promotion).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/cpu.asm](../src/cpu.asm) — entry `cpu_start`.
- [src/boot.asm](../src/boot.asm) — entry `boot_register_check`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/boot-verification.json) — TSRun post-entry CPU-result, HOME address-pair/data fault injection; exact scope/limits in record; physical validation pending.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### CPU-03 Localized HOME address-pair consistency

**Firmware status:** implemented. **Prerequisites:** rom_execution.

**Implementation method:** For A0-A15 probe HOME pairs differing in one address bit,55/AA and reversedAA/55; first mismatch repeats9 then bit+1. ROM2 calls a fixed low-ROM bridge to expose all HOME RAM without RAM control or a stack. Default boot additionally qualifies each endpoint55/AA, then reads opposing55/AA and reversedAA/55 writes across16 pairs. Qualifier mismatches preserve normal RAM chip/address/expected/observed reporting; pair mismatches repeat9/index1-16 fromROM0 until reset. Only after a successful quick sweep.

**Observables:** Detected mismatch repeats9/bit-index1-16 (A0-A15); first failing pair stops, no screen/RAM state dependency for pulse control.

**Interpretation limits:** Suspect address/data/mux/decoder/storage path, not proof of a Z80 pin or uniquely failed component; only16 selected pairs, complemented by full48K address patterns.

**Recovery:** rom_only.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Optional ROM2 opcode execution and CPU checker/reporter instruction/register dependencies can defeat recovery. Default startup/Full do not run it. Boot still assumes activeROM0 opcode/operand reads and usable comparisons/branches/registers; FE border/beeper share SCLD. Localized HOME injections do not prove global CPU pin-fault survival.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#startup-and-resource-promotion).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/cpu.asm](../src/cpu.asm) — entry `alias_start`.
- [src/modules.asm](../src/modules.asm) — entry `alias_probe`.
- [src/boot.asm](../src/boot.asm) — entry `boot_alias_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/boot-verification.json) — TSRun post-entry CPU-result, HOME address-pair/data fault injection; exact scope/limits in record; physical validation pending.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### CPU-02 Qualified stack operations

**Firmware status:** specified. **Prerequisites:** qualified_workspace.

**Implementation method:** Exercise CALL/RET and PUSH/POP against known values and stack guards only after qualifying writable HOME blocks.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Stack failure may be RAM/mapping/data path rather than CPU alone.

**Recovery:** abandon_stack.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** RAM stack operations are directly exercised; use fixed ROM continuations rather than RET through the test stack. Advanced return checks are separately selected.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#startup-and-resource-promotion).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-01 Data bus walking patterns

**Firmware status:** implemented. **Prerequisites:** home_mapping.

**Implementation method:** At separated HOME addresses write/read 00 FF 55 AA, walking one and walking zero; accumulate expected XOR observed.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Map bit masks to region/nibble chip paths; shared errors can originate outside DRAM.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#ram-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/diagnostic.asm](../src/diagnostic.asm) — entry `ram_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator checkpoint_completed](../docs/validation/v02-301339832d6f/fuse-v02-ram-result.json) — Fuse1.7.0 stock TS2068, mapped-cartridge quick00/FF completed phase2 checkpoint; not electrical validation..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-02 Address and region aliases

**Firmware status:** implemented. **Prerequisites:** home_mapping.

**Implementation method:** Full48K hash fill/read plus separate low/high address-byte fill/read planes; combined address bytes uniquely distinguish all logical addresses and expose aliases.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Aliasing suggests address/mux/select path; not a unique bad-chip verdict.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#ram-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `address_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-03 Complete complementary pattern sweeps

**Firmware status:** implemented. **Prerequisites:** home_mapping.

**Implementation method:** Eight whole48K complementary pattern fills/ascending reads; direction-sensitive coverage is provided by the separate March test.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Unlike immediate comparisons this observes stored data over a complete sweep.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#ram-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/diagnostic.asm](../src/diagnostic.asm) — entry `ram_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator checkpoint_completed](../docs/validation/v02-301339832d6f/fuse-v02-ram-result.json) — Fuse1.7.0 stock TS2068, mapped-cartridge quick00/FF completed phase2 checkpoint; not electrical validation..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-04 March C minus

**Firmware status:** implemented. **Prerequisites:** home_mapping.

**Implementation method:** Entire target: bidirectional w0; up r0/w1; up r1/w0; down r0/w1; down r1/w0; bidirectional r0, using 00/FF bytes.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Detects selected stuck/transition/coupling faults; not exhaustive intra-word coverage.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#ram-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/diagnostic.asm](../src/diagnostic.asm) — entry `ram_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator checkpoint_completed](../docs/validation/v02-301339832d6f/fuse-v02-ram-result.json) — Fuse1.7.0 stock TS2068, mapped-cartridge quick00/FF completed phase2 checkpoint; not electrical validation..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-05 Nibble and intra-word coupling patterns

**Firmware status:** partial. **Prerequisites:** home_mapping.

**Implementation method:** Full-byte sweeps with 0F/F0,33/CC,55/AA and walking aggressor bits while comparing other bits.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Complements March byte patterns; report exact failing bit and affected package.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#ram-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/diagnostic.asm](../src/diagnostic.asm) — entry `ram_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-06 Deterministic random comparisons

**Firmware status:** partial. **Prerequisites:** home_mapping.

**Implementation method:** 16-bit right-shift LFSR seedACE1/polyB400, high byte written across48K, seed restarted for compare; first new random mismatch stops before scratch corruption can cascade. Seed/direction variation remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Record seed/phase so intermittent failures can be reproduced; expected data never stored in target.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#ram-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `random_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-07 Write hold read under normal refresh

**Firmware status:** partial. **Prerequisites:** home_mapping.

**Implementation method:** 55 then AA whole48K fill, finite500x3000 instruction-timed hold with normal refresh and cancellation, then compare. Configurable dwell intervals remain future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Retention/refresh evidence only; DI and HALT do not turn refresh off; temperature unknown.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#ram-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `retention_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### RAM-08 Firmware workspace and guard retest

**Firmware status:** implemented. **Prerequisites:** rom_execution.

**Implementation method:** Every complete sweep tests all48K including UI buffers6400-69FF, keyboard flags5B00-5B28 and both display files; no stack/workspace RAM is exempt and no default RAM stack exists.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** No permanent excluded HOME block; abandon corrupted state without RET.

**Recovery:** abandon_stack.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#testing-the-workspace-itself).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/diagnostic.asm](../src/diagnostic.asm) — entry `ram_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-01 HSR latch and readback

**Firmware status:** specified. **Prerequisites:** rom_execution.

**Implementation method:** Write legal masks preserving active ROM/SP/vector, compare F4 readback, restore software shadow.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Readback success does not prove physical memory selection.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#scld-tests-by-function).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-02 Static DOCK selection and full chunk reads

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Selected chunks1-7 have A5 XOR chunk signatures at their end; boot integrity reads8144 bytes per chunk. Full chunk CRC/timing/scattered comparisons remain future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Classify unstable external reads separately from selection failures.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#static-external-rom-qualification).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `bank_probe`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-03 ROM overlay write isolation

**Firmware status:** implemented. **Prerequisites:** qualified_workspace.

**Implementation method:** HOME sentinels at5FF0/7FF0/9FF0/BFF0/DFF0/FFF0, selected-ROM attempted writes and readback, then unmap and verify sentinels. ROM0 remains resident.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Unexpected hidden-HOME writes implicate selection/write-isolation path.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#scld-tests-by-function).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `bank_home_verify`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-04 Rapid HOME DOCK alternation

**Firmware status:** partial. **Prerequisites:** home_mapping.

**Implementation method:** Continuous bounded batches of single/multiple/combined HSR masks, signature reads and ROM/HOME write isolation; active bit0 stays selected. High-anchor rapid alternation remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Detect stale/aliased selections and corruption; all masks require separate mapping contracts.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#rapid-home-and-dock-alternation).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `bank_pattern`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-05 External response timing sweep

**Firmware status:** partial. **Prerequisites:** home_mapping.

**Implementation method:** Immediate OUT(F4),A then signature reads and ROM-write readback exercise short response paths. Calibrated delay sweep, OUT(C),A comparison and full block reads remain future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Delay-sensitive failures suggest response/selection/loading; cannot uniquely blame TSPico or SCLD.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#response-timing-sweep).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `bank_probe`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-06 Global HOME DOCK EXROM selection

**Firmware status:** partial. **Prerequisites:** qualified_gateway.

**Implementation method:** Explicit optional verified HOME C000 gateway selects DECRC0/HSR01 for EXROM CRC, restores DECR40 and fixed-jumps to low DOCK; not a complete selection matrix.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** DOCK code disappears under EXROM; skip if no tested gateway block exists.

**Recovery:** gateway_restore.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Verified HOME gateway opcodes participate in execution; corruption during that window can prevent software recovery.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#scld-tests-by-function).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `exrom_copy_gateway`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-07 Sinistar startup data profile

**Firmware status:** specified. **Prerequisites:** qualified_workspace.

**Implementation method:** Reproduce 10->18->98, mode2, no IRQ; bounded ROM3 decode to A000, verify, transpose to 4000, verify, inspect ROM7.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Stage markers separate external selection, U12/U13 temporary RAM and U6/U7 display paths.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#sinistar-startup-reproduction).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-08 Verified cartridge execution transfers

**Firmware status:** partial. **Prerequisites:** qualified_workspace.

**Implementation method:** Compare512 high-ROM bytes against separate ROM1 shadow before optional HOME CRC execution transfer at8020; separate ROM3/ROM7 transfer stubs remain future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Instruction-fetch errors can crash despite data-only success; no software recovery guarantee.

**Recovery:** mapping_restore.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Selected external ROM supplies executing opcodes; a failed fetch or disappearance of that anchor can prevent recovery.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#sinistar-startup-reproduction).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `crc_qualify`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BANK-09 Interrupt and mixed-load banking

**Firmware status:** specified. **Prerequisites:** qualified_interrupts.

**Implementation method:** Combine qualified foreground transitions with owned ISR temporary selection/restoration, tested stacks, video modes and optional AY I/O.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Test shadow protocol separately; failures may be software races, RAM, IRQ or external timing.

**Recovery:** interrupt_restore.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Advanced ISR restoration, vectors and stack paths may depend on RAM and selected ROM during control-flow transitions.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#interrupt-and-mixed-load-stress).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SCLD-01 Display DMA addressing and serialization

**Firmware status:** partial. **Prerequisites:** usable_display.

**Implementation method:** Executable normal/second/ECM/hires bit-lane/address/geometry cards with exact host/emulator plane comparisons and user-visible output. Internal DMA/serialization correctness still needs observation/instruments.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Clean CPU readback with wrong video implicates fetch/serialization/output; not automatically DRAM.

**Recovery:** video_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#scld-tests-by-function).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `video_standard_ready`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SCLD-02 Display arbitration and clock gating

**Firmware status:** specified. **Prerequisites:** qualified_interrupts.

**Implementation method:** Compare ROM/upper-RAM versus display-RAM access workloads against qualified interrupts and stress simultaneous writes/fetch.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Relative timing only; stopped CPU clock defeats software timeout; bench confirmation needed.

**Recovery:** interrupt_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#scld-tests-by-function).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SCLD-03 Bounded interrupt generation

**Firmware status:** implemented. **Prerequisites:** rom_execution, home_mapping.

**Implementation method:** Explicit optional IM1/fixed ROM vector, SP=BFFF sacrificial write sink and finite60000-iteration arrival budget; handler discards saved PC and jumps to fixed checkpoint. RAM contents need not work; CPU bus writes must complete. Green border acknowledges arrival.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Absent or inconsistent count identifies IRQ path; common crystal prevents absolute frequency proof.

**Recovery:** interrupt_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#scld-tests-by-function).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `irq_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SCLD-04 Interrupt inhibit control

**Firmware status:** implemented. **Prerequisites:** rom_execution, home_mapping.

**Implementation method:** Explicit optional inhibited IRQ phase followed by enabled arrival phase; unexpected inhibited arrival or missing enabled IRQ fails; finite budgets and DI/DECR40 recovery.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Separate inhibit mismatch from absent interrupt generator.

**Recovery:** interrupt_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#scld-tests-by-function).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `irq_start`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SCLD-05 Technician signal and solder probe mode

**Firmware status:** specified. **Prerequisites:** external_instrument.

**Implementation method:** Repeated single-purpose accesses plus expected-waveform/pin crosswalk; compare SCLD lead with downstream connection using instruments.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** ROM tests identify suspect paths; open solder versus internal failure needs electrical evidence. Exact pin matrix pending.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](PROJECT_STATE.md#work-remaining).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### ROM-01 HOME identity and repeated checksum

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Explicit high-ROM shadow qualification then HOME0000-3FFF CRC32 from DOCK4 at8020; display measured and stock CRC. Repeat manually; automatic stability cycle remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Unknown stable ROM is unrecognized, not automatically faulty; unstable reads implicate ROM path.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#rom-identity-and-integrity).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `home_crc_select`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### ROM-02 EXROM identity and repeated checksum

**Firmware status:** partial. **Prerequisites:** qualified_gateway.

**Implementation method:** Explicit high-code qualification plus copied/readback256-byte HOME C000 gateway; EXROM0000-1FFF CRC32, DOCK recovery and measured/stock display. Repeat manually.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Do not assume higher chunks contain extra stock ROM; skip without gateway.

**Recovery:** gateway_restore.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Verified HOME checker/gateway opcodes participate in execution; corruption during that window can prevent software recovery.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#rom-identity-and-integrity).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `exrom_crc_select`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### VID-01 Standard colors bright and flash

**Firmware status:** implemented. **Prerequisites:** usable_display.

**Implementation method:** Mode0 bitmap4000/attributes5800; first offer solid eight-color PAPER bars, normal top96 lines and BRIGHT bottom96 lines, corresponding attributes differing only by bit6 and FLASH off; separate existing ink/paper and flash cards. Each half starts with a16-pixel monochrome label band rendered in the actual bitmap: NORMAL BRIGHT=0 and BRIGHT BRIGHT=1; remaining80 lines are solid bars. Labels remain legible when output ignores BRIGHT.

**Observables:** Eight aligned bars in order black, blue, red, magenta, green, cyan, yellow, white; lower half brighter for seven nonblack colors; both black bars identical. Planned BRIGHT toggle keeps other attribute bits unchanged; user judges physical output.

**Interpretation limits:** A missing BRIGHT difference can involve attribute D6 (U7), SCLD decode or video output; it is not a component verdict. Black is unchanged by BRIGHT. Preview RGB is illustrative; target integration and physical validation pending. Some video systems intentionally omit extra brightness; record no visible BRIGHT difference without declaring a TS2068 fault. Compare native and external outputs where available.

**Recovery:** video_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#video-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `video_bars_ready`.

**Existing host support:**

- [scripts/generate_design_assets.py](../scripts/generate_design_assets.py) — `standard_card`.
- [scripts/generate_design_assets.py](../scripts/generate_design_assets.py) — `standard_render`.
- [assets/video/standard-pixels.bin](../assets/video/standard-pixels.bin).
- [assets/video/standard-attributes.bin](../assets/video/standard-attributes.bin).
- [scripts/generate_design_assets.py](../scripts/generate_design_assets.py) — `colorbar_card`.
- [assets/video/colorbar-pixels.bin](../assets/video/colorbar-pixels.bin).
- [assets/video/colorbar-attributes.bin](../assets/video/colorbar-attributes.bin).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### VID-02 Second display selection

**Firmware status:** partial. **Prerequisites:** usable_display.

**Implementation method:** Mode1 asymmetric secondary card at6000/7800; switch by menu or Full sequence. One-key live primary/secondary alternation remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Both files share U6/U7; cannot avoid a failed chip by switching.

**Recovery:** video_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#video-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `video_secondary_ready`.

**Existing host support:**

- [scripts/generate_design_assets.py](../scripts/generate_design_assets.py) — `standard_card`.
- [assets/video/secondary-pixels.bin](../assets/video/secondary-pixels.bin).
- [assets/video/secondary-attributes.bin](../assets/video/secondary-attributes.bin).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### VID-03 ECM dither and per-line attributes

**Firmware status:** implemented. **Prerequisites:** usable_display.

**Implementation method:** Executable native ECM diagonal hue/value gradient and hue/saturation disc, host Sierra Lite RGB error diffusion with legal shared-BRIGHT8x1 pairs; palette swatches and exact packed plane comparisons.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** 15 distinct base colors plus perceived mixtures; preview RGB is not NTSC measurement.

**Recovery:** video_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#video-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `video_ecm_ready`.

**Existing host support:**

- [scripts/generate_design_assets.py](../scripts/generate_design_assets.py) — `ecm_card`.
- [assets/video/ecm-pixels.bin](../assets/video/ecm-pixels.bin).
- [assets/video/ecm-attributes.bin](../assets/video/ecm-attributes.bin).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### VID-04 Hires geometry and plane ordering

**Firmware status:** partial. **Prerequisites:** usable_display.

**Implementation method:** Mode6 packed interleaved primary/secondary calibration with grid/circle/gratings; fixed black/white pair. Cycling8 color pairs remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Fine gratings may blur on composite; restore mode0 for FE border fault codes.

**Recovery:** video_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#video-tests).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `video_hires_ready`.

**Existing host support:**

- [scripts/generate_design_assets.py](../scripts/generate_design_assets.py) — `hires_card`.
- [assets/video/hires-primary.bin](../assets/video/hires-primary.bin).
- [assets/video/hires-secondary.bin](../assets/video/hires-secondary.bin).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### VID-05 128 INK PAPER BRIGHT combinations

**Firmware status:** partial. **Prerequisites:** usable_display.

**Implementation method:** Mode0 checkerboard overview includes all128 attributes00-7F with Mark Miller credit; bounded viewer/cancel; full-screen128-step cycle remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** 128 attribute combinations are not128 unique palette colors; visual blending is not a digital pass criterion. Credit Mark Miller and TimexSinclair.com.

**Recovery:** video_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](VIDEO_128_ATTRIBUTES.md#diagnostic-adaptation).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Source credits:**

- Mark Miller — [128 Colors](https://www.timexsinclair.com/computer_media/128-colors/index.html), TimexSinclair.com. Conceptual basis; independent grid/generator, no BASIC listing copied.

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `video_mix128_ready`.

**Existing host support:**

- [scripts/generate_design_assets.py](../scripts/generate_design_assets.py) — `attribute_128_card`.
- [assets/video/attribute-128-pixels.bin](../assets/video/attribute-128-pixels.bin).
- [assets/video/attribute-128-attributes.bin](../assets/video/attribute-128-attributes.bin).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### KEY-01 Free keyboard press and release display

**Firmware status:** partial. **Prerequisites:** qualified_workspace.

**Implementation method:** Poll all8 half-rows, live green held/cyan released/unseen white; optional bounded historical RAM flags, duplicated CAPS and BREAK chord. Dedicated debounce/release history remains future. Graphic adaptation of Josef Jelinek TSRun keyboard.png, with fixed non-overlapping two-row attribute rectangles. Palette PAPER78 unseen,60 held,68 released; both CAPS share history; derived CAPS+SPACE BREAK adds byte5B28 and is distinct from ENTER+SPACE exit. Tiny legends removed; primary embedded Timex glyph labels retained. Painter preserves D/E/IX/alternate AF selector and uses no RAM control data. Detailed conversion/source/exit contracts in KEYBOARD_ART.md; original PNG/provenance hashes preserved. Cartridge fixed keyboard scanning now executes in ROM7 E000-E599 with ROM0 paint/exit bridges; HSR81 during scan,01 at exit; D/E/IX/AF alternate contracts unchanged. HOME keeps its scanner in HOME ROM.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Unpressed keys are untested; shared CAPS position cannot identify physical key.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#keyboard-and-input).

**Actual implementation and remaining scope:** [Implementation record](KEYBOARD_ART.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `keyboard_scan`.
- [src/modules.asm](../src/modules.asm) — entry `keyboard_paint`.
- [build/keyboard-rom.asm](../build/keyboard-rom.asm) — entry `keyboard_rom_scan`.

**Existing host support:**

- [scripts/keyboard_art.py](../scripts/keyboard_art.py) — `draw_keyboard`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/keyboard-verification.json) — TSRun:44 cases covering all40 contacts, exact non-overlapping whole-key attributes, shared CAPS/derived BREAK, ENTER+SPACE distinction, corrupt history and all HOME writes lost; no physical acceptance..
- [emulator PASS](../docs/validation/load-a09b3406d3f1/keyboard-verification.json) — TSRun; all40 matrix contacts, exact rectangles, shared CAPS/BREAK, lost writes/history and exits with unchanged SP and audited ROM0/ROM7 fetches. Physical validation pending..
- [emulator PASS](../docs/validation/load-9db1d0ac08eb/keyboard-verification.json) — TSRun; all40 matrix contacts, exact rectangles, shared CAPS/BREAK, lost writes/history and exits with unchanged SP and audited ROM0/ROM7 fetches. Physical validation pending..
- [emulator PASS](../docs/validation/load-bc5eb2df44c3/keyboard-verification.json) — TSRun; all40 matrix contacts, exact rectangles, shared CAPS/BREAK, lost writes/history and exits with unchanged SP and audited ROM0/ROM7 fetches. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### KEY-02 Guided 42 physical key test

**Firmware status:** specified. **Prerequisites:** qualified_workspace.

**Implementation method:** Prompt physical layout order, left/right CAPS separately, BREAK as CAPS+SPACE, then shifted combinations; require release.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** 42 physical keys map to40 positions; cancelled test is not failure.

**Recovery:** mapping_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#keyboard-and-input).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### KEY-03 Keyboard row column isolation

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Live row/column display provides technician isolation evidence; no-row/multiple-row automated comparison and verdicts remain future. Cartridge fixed keyboard scanning now executes in ROM7 E000-E599 with ROM0 paint/exit bridges; HSR81 during scan,01 at exit; D/E/IX/AF alternate contracts unchanged. HOME keeps its scanner in HOME ROM.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Fault may be contact/diode/connector/common trace/SCLD; no unique solder diagnosis.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#keyboard-and-input).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `keyboard_scan`.
- [build/keyboard-rom.asm](../build/keyboard-rom.asm) — entry `keyboard_rom_scan`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/keyboard-verification.json) — TSRun:44 cases covering all40 contacts, exact non-overlapping whole-key attributes, shared CAPS/derived BREAK, ENTER+SPACE distinction, corrupt history and all HOME writes lost; no physical acceptance..
- [emulator PASS](../docs/validation/load-a09b3406d3f1/keyboard-verification.json) — TSRun; all40 matrix contacts, exact rectangles, shared CAPS/BREAK, lost writes/history and exits with unchanged SP and audited ROM0/ROM7 fetches. Physical validation pending..
- [emulator PASS](../docs/validation/load-9db1d0ac08eb/keyboard-verification.json) — TSRun; all40 matrix contacts, exact rectangles, shared CAPS/BREAK, lost writes/history and exits with unchanged SP and audited ROM0/ROM7 fetches. Physical validation pending..
- [emulator PASS](../docs/validation/load-bc5eb2df44c3/keyboard-verification.json) — TSRun; all40 matrix contacts, exact rectangles, shared CAPS/BREAK, lost writes/history and exits with unchanged SP and audited ROM0/ROM7 fetches. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### AUD-01 Beeper output and alarm path

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Bounded700-cycle low/mid/high FE-D4 tones with steady red/magenta/green borders on both waveform halves; screen lists the corresponding colors. Release/new-key cancellation and final silence. No physical audio loopback; sweep and observation recording remain future.

**Observables:** Listen for low/mid/high, watch red/magenta/green change once per tone; each border stays steady within a tone. Digital writes do not certify physical audio/video outputs.

**Interpretation limits:** No automatic speaker readback; beeper unavailable if output/amplifier/speaker fails.

**Recovery:** audio_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#beeper-ay-cassette-and-joysticks).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `beeper_ready`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### AUD-02 AY register and address decode

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Input-safe R7, differing index-derived masked write/read R0-R13 values to expose storage/address mismatches; R14/R15 excluded; failure mutes. Walking patterns remain future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Register comparison does not verify clock,DAC or speaker; never blindly drive joystick port.

**Recovery:** audio_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#beeper-ay-cassette-and-joysticks).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `ay_test`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### AUD-03 AY tone noise mixer amplitude envelope

**Firmware status:** partial. **Prerequisites:** ay_registers_qualified.

**Implementation method:** Executable guided24-step AY sequence:four periods per A/B/C,volume3/8/15,noise31/8/1,envelopes9/13/10/8,chord,silence; yellow active labels and green progress; fixed bounded ROM table with masked14-register writes and mute/cancel. Analog output requires user observation.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Audible output is user observation; separate AYclock/control and downstream analog possibilities.

**Recovery:** audio_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#beeper-ay-cassette-and-joysticks).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `aylisten_ready`.
- [src/modules.asm](../src/modules.asm) — entry `ay_step`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/ay-verification.json) — TSRun actual24 step registers/highlight bytes,8 cancellation points,corrupt table and lost HOME writes; analog/physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### IO-01 Cassette output input and record verify

**Firmware status:** partial. **Prerequisites:** cassette_setup.

**Implementation method:** Opt-in EAR00/40 raw observation with fixed polling budget and M cancellation. MIC pilot, edge counting and complete record/verify remain future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Separate output/input/full path; direct MIC-to-EAR wire is not a calibrated fixture.

**Recovery:** audio_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#beeper-ay-cassette-and-joysticks).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `input_scan`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### IO-02 Built-in joystick input and isolation

**Firmware status:** partial. **Prerequisites:** joystick_setup.

**Implementation method:** Input-safe R7=3F, AY R14 reads via01F6/02F6. MainJ opens two live spatial pads; five active-low contacts (bits0/1/2/3/7) independently paint six-cell Up/Down/Left/Right/Fire indicators green while active, cyan after observed activation/release, or white if unseen. History is optional display-only attribute data; repeated momentary transitions remain live. Shows all combinations and raw bytes/EAR. Immutable bounded ROM1 helper at3F00 is first-opcode/full96-byte additive qualified before execution; return to ROM0 before restoringHSR. HOME edition uses HOME0/1,HSR00. Finite scan budget and guarded new-key exit; held mainJ quarantined.

**Observables:** Live independent directions/Fire plus per-contact tested history, both ports, diagonals/fire/opposites, rawFF idle or absent, EAR00/40; user observation required, no automatic contact certification.

**Interpretation limits:** Unconnected device is NOT RUN; do not drive pins or assume usable connector logic ground.

**Recovery:** audio_restore.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Guarded optional ROM1 code transfer requires active cartridge bank1 mapping/opcode path; first-opcode/additive qualification detects ordinary corruption, not collisions or late/M1-only faults. Default minimal RAM reporter staysROM0. ROM-fixed rectangles/counts and no HOME stack; failed display writes affect appearance only.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#beeper-ay-cassette-and-joysticks).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `input_joy1`.
- [src/joystick.asm](../src/joystick.asm) — entry `joystick_paint`.

**Existing host support:**

- [scripts/verify_joystick.mjs](../scripts/verify_joystick.mjs).
- [docs/JOYSTICK_TEST.md](../docs/JOYSTICK_TEST.md).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/joystick-verification.json) — TSRun64 contact combinations per port-pair edition; exact highlights/release/isolation/cancellation and3 corrupt-helper guards; physical observation pending..
- [emulator PASS](../docs/validation/home-e09e53177d65/joystick-verification.json) — HOME edition same64 contact combinations plus helper corruption guards; physical observation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SOAK-01 Overnight RAM only

**Firmware status:** partial. **Prerequisites:** qualified_workspace.

**Implementation method:** Continuous complete48K sweeps including address/random/retention and workspace; register-only16-bit completed-pass count wraps at65536. Any new key stops at a safe boundary. Recorded error masks enter the chip/bit reporter; otherwise soakstop displays No failures during the test with the hexadecimal count, then requires a fresh key to return. No incomplete label for this infinite run. Seed/dwell/direction profiles, scheduled hours and pause/resume remain future. Between passes the readable status/count page holds for six nominal seconds at3.528MHz, with all-key-release/new-key cancellation still active; no mid-sweep status redraw.

**Observables:** Phase border colors, completed-pass count and stopped/no-failures summary; RAM failures attempt chip-designator/bit identification with adaptive text and repeating border/beeper codes.

**Interpretation limits:** First failure latched; time dependence does not confirm overheating; no persistent ROM-only log.

**Recovery:** soak_recovery.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#overnight-ram-and-combined-soak).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `soak_ready`.
- [src/diagnostic.asm](../src/diagnostic.asm) — entry `ram_cancel`.
- [src/modules.asm](../src/modules.asm) — entry `soak_count_done`.

**Existing host support:**

- [scripts/verify_soak.mjs](../scripts/verify_soak.mjs).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..
- [emulator PASS](../docs/validation/v02-301339832d6f/soak-verification.json) — TSRun; stop summaries, register counts, fault priority, held-key/new-key behavior and lost display writes. Physical validation pending..
- [emulator PASS](../docs/validation/home-e09e53177d65/soak-verification.json) — TSRun; stop summaries, register counts, fault priority, held-key/new-key behavior and lost display writes. Physical validation pending..
- [emulator PASS](../docs/validation/soak-aae9743a6c6e/cartridge.json) — TSRun; measured six-second status dwell, stack unchanged, immediate cancellation, stop-count/fault priority; physical clock/timing pending..
- [emulator PASS](../docs/validation/soak-aae9743a6c6e/home.json) — TSRun U16 HOME edition; six-second dwell, cancellation and stop summaries; physical timing pending..
- [emulator PASS](../docs/validation/load-a09b3406d3f1/soak-verification.json) — TSRun cartridge; six-second status dwell, guarded stop, first-fault/count/acknowledgement checks. Physical timing pending..
- [emulator PASS](../docs/validation/load-9db1d0ac08eb/soak-verification.json) — TSRun cartridge; six-second status dwell, guarded stop, first-fault/count/acknowledgement checks. Physical timing pending..
- [emulator PASS](../docs/validation/load-bc5eb2df44c3/soak-verification.json) — TSRun cartridge; six-second status dwell, guarded stop, first-fault/count/acknowledgement checks. Physical timing pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SOAK-02 Overnight banking only

**Firmware status:** partial. **Prerequisites:** qualified_workspace.

**Implementation method:** Continuous signature/write-isolation HSR batches with16-bit completed-pass count, M stop and first mismatch page. Timing/mapping-family rotation remains future.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Do not mix thermal diagnosis with unqualified ROM reads; preserve first transition mismatch.

**Recovery:** soak_recovery.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#overnight-ram-and-combined-soak).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `bank_ready`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### SOAK-03 Combined overnight mixed load

**Firmware status:** implemented. **Prerequisites:** rom_execution, home_mapping.

**Implementation method:** Configurable ROM-only mixed-load batches: all48K address-hash/March and data-only PUSH/POP, ECM fetch, fixed DOCK signature/isolation traffic, normal-refresh spacing, bounded IM1 entry and frequent synthetic Speech2AY-style R0-R12 writes/readbacks. Eight independent toggles, baseline/all presets, one-batch/continuous, six-second status/count and guarded new-key stop. IRQ sink BFFD/BFFE receives deferred DI-only00/FF tests. Advanced real-return bursts are separately confirmed, not destructive-March resumption. Menu groups N/C as configurable duration before Begin test with S/R; the selected complete duration phrase is green. Option4 explicitly names60Hz screen interrupts; S uses bounded checkpoints and R confirms actual IRQ returns. Option6 now cycles quiet/busy slices, adds checked00/FF/55/AA traffic after hash comparisons, rotates0/2/6 video when option3 is enabled, and strengthens AY to14 writes with maximum/envelope amplitudes plus bounded beeper when option7 is enabled. P selects all power loads; quiet phases inhibit IRQ and use bounded ROM waits. RAM phase ordering and fixed-ROM recovery remain separate from auxiliary loads. Running notice explicitly announces TEST STARTED and six-second preparation.

**Observables:** First RAM address/expected/observed/XOR region mask/phase and chip/bit pulses; auxiliary4/5/7 class/address-or-index/expected/observed/phase. No-fault stopped batch count wraps65536. Fault fields replace batch count; no persistent log. Analog output needs observation.

**Interpretation limits:** Combined failures require isolated reruns; no deliberate hidden PC/SP/vector.

**Recovery:** soak_recovery.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Register-only ROM0/ROM4 scheduler, bounded option-independent loops and mapping; optional data PUSH/POP never RETs. Basic IRQ saved PC is write-only. CPU/ROM opcode, shared bus/clock/power failures remain unavoidable.

**Specification:** [Detailed design](SINISTAR_LOAD_TEST.md#current-implementation-and-operator-controls).

**Actual implementation and remaining scope:** [Implementation record](SINISTAR_LOAD_TEST.md).

**Firmware locations:**

- [src/load.asm](../src/load.asm) — entry `load_batch_start`.

**Existing host support:**

- [scripts/verify_load.mjs](../scripts/verify_load.mjs).

**Validation evidence:**

- [emulator PASS](../docs/validation/load-bc5eb2df44c3/load-verification.json) — TSRun mapped64K DOCK; all256 safe slice masks, representative batches, D1 POP data loss, missing IRQ/bank/AY faults, UI cancellation and real IM1/IM2 return profiles. Physical timing/supply/thermal replication pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### UI-01 Resource permissions and fallback reporting

**Firmware status:** partial. **Prerequisites:** rom_execution.

**Implementation method:** Stackless menus/control with bounded press-edge quarantine for held numeric and optional keys; RAM error unions select degraded display, M acknowledges faults for independent modules; optional CRC qualifies code/gateway; IRQ uses a write-only saved-PC sink. Active tests use all-key release plus any-key stop; result screens accept any key; keyboard holds CAPS+SPACE or ENTER+SPACE. A stuck initial contact can prevent the broad stop channel arming. Startup selection/progress legends; steady RAM phase border colors without mid-sweep display writes; reporter R retry also requires release/new press. Embedded cartridge font, no live HOME font reads. Help C provides explicit TRAINING: finite synthetic sync/2/6/2 RAM, bank4 and CPU8/3 examples using shared stackless ROM pulse routines; M returns to Help. No fault state or optional CPU test is entered. ROM0 boot fault pulses require neither display nor keyboard. Font bytes now reside inDOCK ROM1 at2200-24FF; ROM0 rich renderers selectHSR03 briefly and restore01. Minimal pulses and attribute-coded degraded glyphs do not depend on font data. Mixed-case menus/instructions use existing embedded96-character TS2068 font; host-only asset case conversion preserves hardware/key identifiers and original author spelling. No additional font storage or live HOME font lookup. Menu1 Full coverage overview uses bounded selection quarantine; new1 starts, M returns, startupF remains direct. Keyboard end on selector7 presents fullsummary: automatic RAM/bank/AY matches, user-observation requirements and exclusions. Held exit chord is captured/excluded until a new input edge. Cancellation and faults do not show completion; keyboard timeout is not key certification. Fixed ROM screen assets show nominal-clock duration estimates: RAM options84/41/8/8/3/24sec; Full4min to keyboard/8min including timeout; startupR1.5min, F4/8min; keyboard4min timeout; beeper15sec, AY22sec; overnight1.5min/pass until stopped. These are model-derived hints, not timers or completion evidence; no control budgets changed. Fault pulse pacing now uses sync-following silence0.89s, intra-group silence0.41s and inter-group silence1.30s at nominal3.528MHz; longsync1.18s/153Hz and counting0.595s/429Hz, with approximately2.8:1 pitch separation. Shared code/train waits remain bounded in ROM, no RAM or interrupts. Selector0 Complete RAM success now loads rampass with All6 RAM chips PASS and all six designators, then reuses Full summary new-key quarantine. Error masks are checked before this dispatch. Quick/partial/full/soak/IRQ selectors remain separate and cancellations cannot show it. RAM menu states chip-identification capability. Individual RAM successes show Selected checks PASS; complete RAM shows All 6 RAM chips PASS. Shared pass_ready/fullsummary_ready input guard requires a fresh key. Cancellation does not claim success and mismatches enter the chip/bit reporter.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Do not equate limited automatic success with whole-machine PASS; best-effort text is secondary.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency. Boot still assumes activeROM0 opcode/operand reads and usable comparisons/branches/registers; FE border/beeper share SCLD. Localized HOME injections do not prove global CPU pin-fault survival.

**Specification:** [Detailed design](TS2068_DIAGNOSTIC_DESIGN.md#reporting-when-video-ram-fails).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/diagnostic.asm](../src/diagnostic.asm) — entry `menu_draw`.
- [src/diagnostic.asm](../src/diagnostic.asm) — entry `soundguide_ready`.
- [src/boot.asm](../src/boot.asm) — entry `boot_fault_group`.
- [src/modules.asm](../src/modules.asm) — entry `fullinfo_ready`.
- [src/modules.asm](../src/modules.asm) — entry `fullsummary_ready`.
- [src/modules.asm](../src/modules.asm) — entry `rampass_ready`.

**Existing host support:**

- [scripts/measure_test_durations.mjs](../scripts/measure_test_durations.mjs).
- [scripts/verify_duration_ui.mjs](../scripts/verify_duration_ui.mjs).
- [docs/TEST_DURATIONS.md](../docs/TEST_DURATIONS.md).
- [scripts/verify_fault_timing.mjs](../scripts/verify_fault_timing.mjs).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..
- [emulator PASS](../docs/validation/v02-301339832d6f/boot-verification.json) — TSRun post-entry CPU-result, HOME address-pair/data fault injection; exact scope/limits in record; physical validation pending.
- [emulator PASS](../docs/validation/v02-301339832d6f/keyboard-verification.json) — TSRun:44 cases covering all40 contacts, exact non-overlapping whole-key attributes, shared CAPS/derived BREAK, ENTER+SPACE distinction, corrupt history and all HOME writes lost; no physical acceptance..
- [emulator PASS](../docs/validation/v02-301339832d6f/duration-ui-verification.json) — TSRun: seven packed ROM screen loaders, all6912 display bytes compared, unchanged SP; model timing estimates in test-duration-estimates.json, physical timings pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/fault-timing-verification.json) — TSRun exact FE timestamps for2/6/2:11 tone envelopes, pitch and sync/intra/inter-group gap assertions; unchanged SP, physical timings pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### UI-02 Soak dashboard cancellation and first fault

**Firmware status:** partial. **Prerequisites:** qualified_workspace.

**Implementation method:** Stable pass-count dashboard between destructive sweeps, M stop at safe boundaries and register-held first failure; no elapsed-time/temperature or resumable pause state.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Latch first fault,mark partial passes,abandon corrupted stack; notification shares CPU/SCLD dependencies.

**Recovery:** soak_recovery.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](BANKING_AND_OVERNIGHT_TESTS.md#status-screen-and-interruption).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `soak_ready`.

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### PV-01 PicoVideo palette register path

**Firmware status:** specified. **Prerequisites:** picovideo_profile.

**Implementation method:** Distinct supported palette values and masked walking patterns; compare supported readback and check index aliases.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** External board/capture/output result does not certify native SCLD; optional extensions need installed-revision evidence.

**Recovery:** picovideo_restore.

**Execution policy:** explicit_external_profile_only.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](PICOVIDEO_TEST_PROFILE.md#test-modules).

**Source credits:**

- Jeff Burrell and PicoVideo contributors — [PicoVideo user manual and project](https://github.com/timex-sinclair-projects/PicoVideo), timex-sinclair-projects. Documented optional interface profile; no firmware source copied.

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### PV-02 PicoVideo color channels and ramps

**Firmware status:** specified. **Prerequisites:** picovideo_profile.

**Implementation method:** Profile-correct pure channels, intensity/grayscale ramps and swatches; separate readback from visual judgement.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** External board/capture/output result does not certify native SCLD; optional extensions need installed-revision evidence.

**Recovery:** picovideo_restore.

**Execution policy:** explicit_external_profile_only.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](PICOVIDEO_TEST_PROFILE.md#test-modules).

**Source credits:**

- Jeff Burrell and PicoVideo contributors — [PicoVideo user manual and project](https://github.com/timex-sinclair-projects/PicoVideo), timex-sinclair-projects. Documented optional interface profile; no firmware source copied.

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### PV-03 PicoVideo attribute CLUT mapping

**Firmware status:** specified. **Prerequisites:** picovideo_profile.

**Implementation method:** Four distinguishable palettes; all ink/paper indices and supported attribute selector combinations.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** External board/capture/output result does not certify native SCLD; optional extensions need installed-revision evidence.

**Recovery:** picovideo_restore.

**Execution policy:** explicit_external_profile_only.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](PICOVIDEO_TEST_PROFILE.md#test-modules).

**Source credits:**

- Jeff Burrell and PicoVideo contributors — [PicoVideo user manual and project](https://github.com/timex-sinclair-projects/PicoVideo), timex-sinclair-projects. Documented optional interface profile; no firmware source copied.

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### PV-04 PicoVideo native mode reproduction

**Firmware status:** specified. **Prerequisites:** picovideo_profile.

**Implementation method:** Compare0/1/2/6 patterns on native and external output; classify deliberate ULA+ palette differences.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** External board/capture/output result does not certify native SCLD; optional extensions need installed-revision evidence.

**Recovery:** picovideo_restore.

**Execution policy:** explicit_external_profile_only.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](PICOVIDEO_TEST_PROFILE.md#test-modules).

**Source credits:**

- Jeff Burrell and PicoVideo contributors — [PicoVideo user manual and project](https://github.com/timex-sinclair-projects/PicoVideo), timex-sinclair-projects. Documented optional interface profile; no firmware source copied.

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### PV-05 PicoVideo display write capture stress

**Firmware status:** specified. **Prerequisites:** picovideo_profile.

**Implementation method:** Verify HOME data after sequential/scattered/burst writes while observing external capture; separately add qualified banking and profile-confirmed ROM overlay behavior.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** External board/capture/output result does not certify native SCLD; optional extensions need installed-revision evidence.

**Recovery:** picovideo_restore.

**Execution policy:** explicit_external_profile_only.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](PICOVIDEO_TEST_PROFILE.md#test-modules).

**Source credits:**

- Jeff Burrell and PicoVideo contributors — [PicoVideo user manual and project](https://github.com/timex-sinclair-projects/PicoVideo), timex-sinclair-projects. Documented optional interface profile; no firmware source copied.

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### PV-06 PicoVideo cancel and mode recovery

**Firmware status:** specified. **Prerequisites:** picovideo_profile.

**Implementation method:** Bounded supported mode changes and palette disable; cancel at safe phase boundaries; recover without readback/output dependency.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** External board/capture/output result does not certify native SCLD; optional extensions need installed-revision evidence.

**Recovery:** picovideo_restore.

**Execution policy:** explicit_external_profile_only.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](PICOVIDEO_TEST_PROFILE.md#test-modules).

**Source credits:**

- Jeff Burrell and PicoVideo contributors — [PicoVideo user manual and project](https://github.com/timex-sinclair-projects/PicoVideo), timex-sinclair-projects. Documented optional interface profile; no firmware source copied.

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### UI-03 Schematic aware degraded fault text

**Firmware status:** implemented. **Prerequisites:** rom_execution.

**Implementation method:** Large attribute-coded chip-path pages select surviving PAPER/INK/pixel lanes from RAM error unions; adapt upper-chip pages too; both-nibble failures skip text while register-preserving pulse reports continue.

**Observables:** Expected/observed comparisons where applicable; first failure and affected bit/path; user judgement separate for physical sound/video.

**Interpretation limits:** Stable-nibble host contrast checks do not guarantee arbitrary-fault readability, healthy-lane stability or SCLD display correctness; both files share U6/U7.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** Default critical control and minimal reporting must remain in stackless ROM. CPU clock and active ROM fetch must remain usable; optional rich RAM state is not a recovery dependency.

**Specification:** [Detailed design](DEGRADED_DISPLAY.md#prototype-and-remaining-target-work).

**Actual implementation and remaining scope:** [Implementation record](tests/V02_DIAGNOSTIC_SUITE.md).

**Firmware locations:**

- [src/modules.asm](../src/modules.asm) — entry `fault_draw`.

**Existing host support:**

- [scripts/prototype_degraded_display.py](../scripts/prototype_degraded_display.py) — `page`.
- [scripts/prototype_degraded_display.py](../scripts/prototype_degraded_display.py) — `attribute_page`.
- [assets/degraded-display/host-validation.json](../assets/degraded-display/host-validation.json).

**Validation evidence:**

- [emulator PASS](../docs/validation/v02-301339832d6f/suite-verification.json) — TSRun stock TS2068, module/full-suite execution and fault injections; see exact cases and limitations. Physical validation pending..
- [emulator PASS](../docs/validation/v02-301339832d6f/suite-ram-verification.json) — TSRun:28 quick-startup and6 explicit complete-sweep all-HOME scenarios;24 quick stuck-bit region faults plus representative complete faults, transient reads and write loss; unchanged SP and ROM-only opcodes..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### EXT-01 TSPico external SRAM and slot isolation

**Firmware status:** specified. **Prerequisites:** tspico_sram_profile.

**Implementation method:** Opt-in exact-profile SRAM patterns/walking/March/address/random/soak; establish slot overlap with unique signatures, protect diagnostic image and runtime areas, keep immutable execution anchor, bounded mapping and recovery. No external SRAM code or probes implemented. Use verified capability profiles independent of displayed version, supporting developmental firmware; unsupported capabilities skip without speculative writes.

**Observables:** Planned physical slot/verified offset, logical address, expected/observed, XOR mask and first-fault pulses; not currently executable.

**Interpretation limits:** TSPico SRAM U13 (board prefix required), selector, bus/decoder/interface path; not a HOME DRAM chip verdict. Slot overlap must be established before claiming capacity coverage.

**Recovery:** rom_only.

**Execution policy:** future_opt_in_verified_hardware_profile.

**Control-flow exposure:** Entire DOCK-slot changes can replace running code. Requires separately decoded immutable anchor or explicitly qualified HOME gateway; physical cartridge/TSPico overlapping decode must be excluded.

**Specification:** [Detailed design](TSPICO_DIAGNOSTIC_PROFILE.md#proposed-opt-in-sram-test).

**Actual implementation and remaining scope:** [Implementation record](TSPICO_DIAGNOSTIC_PROFILE.md).

**Firmware locations:** None yet.

**Validation evidence:** None recorded for the target test.

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### BOOT-03 U16 HOME-ROM reset diagnostic bootstrap

**Firmware status:** implemented. **Prerequisites:** home_reset_rom.

**Implementation method:** 16KiB U16 image beginsJP entry at0000; DI/known DECR40 andHSR00, early register/math/shift checks, full-image additive16-bit integrity beforeRAM, boundedR/F selector, quick48K00/FF plus qualified55/AA alias pairs. CompleteRAM/HOME Full/audio/keyboard/joystick/IRQ subset; no stockOS/DOCK/EXROM contents. Native HOME control remains stackless; minimal faults are border/beeper, no large degraded glyph renderer.

**Observables:** Reset status/menu, audible RAM chip/bit codes, CPU8/stage, address9/index, integrity3, explicit completeRAM result. HOME Full coverage differs from cartridge Full.

**Interpretation limits:** Bypasses OS RAM/ROM/cartridge-launch failures; still requires HOME decode, CPU clock/reset/fetch and shared buses. Silent/frozen machine cannot identify a component. OriginalU16 removed, cannot checksum it in this profile.

**Recovery:** rom_only.

**Execution policy:** run_only_when_declared_prerequisites_hold.

**Control-flow exposure:** HOME ROM0000-3FFF/reset fetch path and CPU instructions must work. HSR00 throughout supported tests. IRQ hardware savesPC to sacrificialsink but firmware never reads/returns through it; NMI is unsupported restart, not qualified cancellation.

**Specification:** [Detailed design](HOME_ROM_EDITION.md#implementation-and-validation).

**Actual implementation and remaining scope:** [Implementation record](HOME_ROM_EDITION.md).

**Firmware locations:**

- [build/home/home.asm](../build/home/home.asm) — entry `entry`.
- [build/home/home.asm](../build/home/home.asm) — entry `home_integrity`.

**Existing host support:**

- [scripts/build_home_rom.py](../scripts/build_home_rom.py).
- [scripts/verify_home_rom.mjs](../scripts/verify_home_rom.mjs).
- [scripts/check_home_fuse.py](../scripts/check_home_fuse.py).
- [docs/HOME_ROM_EDITION.md](../docs/HOME_ROM_EDITION.md).

**Validation evidence:**

- [emulator PASS](../docs/validation/home-e09e53177d65/verification.json) — TSRun PC0, absentDOCK/EXROM, dirtyRAM; quick/completeRAM,12 nibble-fault cases, all writes lost, self-integrity, screen copies, HOME Full andIRQ..
- [emulator checkpoint_completed](../docs/validation/home-e09e53177d65/fuse-verification.json) — Fuse native reset with customU16,noDOCK andallFF EXROM; physical timing pending..

**Required acceptance work:** Static mapping/register/stack audit; TS2068 emulator execution and relevant fault injection; Physical target/cartridge validation for supported behavior; Recoverable-fault injection reaches bounded ROM recovery/reporting without uncontrolled execution.

### LOAD-01 Sinistar stack-data load reproduction

**Firmware status:** implemented. **Prerequisites:** rom_execution, home_mapping.

**Implementation method:** Real PUSH DE/POP BC data-only pairs sweep every byte4000-FFFF using address-derived complementary bytes; D1-rich data and5ED0/BFFF vicinity included. DI pairs; enabled loads interleave every256 bytes. Popped data never chooses PC/SP/continuation; fixed SP reset and ROM JP recovery. Recovery latches the original observed POP/read byte through compare_observed, avoiding a second RAM read that could erase transient faults. Exact XOR masks for D0-D7 and multibit26h are verified in each RAM region.

**Observables:** First RAM address/expected/observed/XOR region mask/phase and chip/bit pulses; auxiliary4/5/7 class/address-or-index/expected/observed/phase. No-fault stopped batch count wraps65536. Fault fields replace batch count; no persistent log. Analog output needs observation.

**Interpretation limits:** Low-nibble RAM/shared data/write/read/timing/supply paths; no unique component verdict. Isolated reruns required for combined failures.

**Recovery:** soak_recovery.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Register-only ROM0/ROM4 scheduler, bounded option-independent loops and mapping; optional data PUSH/POP never RETs. Basic IRQ saved PC is write-only. CPU/ROM opcode, shared bus/clock/power failures remain unavoidable.

**Specification:** [Detailed design](SINISTAR_LOAD_TEST.md#current-implementation-and-operator-controls).

**Actual implementation and remaining scope:** [Implementation record](SINISTAR_LOAD_TEST.md).

**Firmware locations:**

- [src/load_low.asm](../src/load_low.asm) — entry `load_stack_begin`.

**Existing host support:**

- [scripts/verify_load.mjs](../scripts/verify_load.mjs).

**Validation evidence:**

- [emulator PASS](../docs/validation/load-bc5eb2df44c3/load-verification.json) — TSRun mapped64K DOCK; all256 safe slice masks, representative batches, D1 POP data loss, missing IRQ/bank/AY faults, UI cancellation and real IM1/IM2 return profiles. Physical timing/supply/thermal replication pending..

**Required acceptance work:** Static mapping/register/stack audit; Image-bound emulator option combinations and D1/lost-write/IRQ/mapping/AY injections; Cancellation after all-key release; mute and first-fault recovery; Physical cold/warm mixed-load reproduction; optional return-corruption exposure documented.

### LOAD-02 Opt-in Sinistar interrupt-return load reproduction

**Firmware status:** implemented. **Prerequisites:** qualified_workspace, qualified_interrupts.

**Implementation method:** Explicit R warning/release/new-R opt-in, IM1 or freshly readback-qualified257-byte IM2 table7A00 and JP7B7B; qualify5E70-5ED0/BFE0-BFFF, then bounded5F00 foreground accesses with real saved-register/audio-stack frame IRQ returns,5E70 saved-SP comparison/fixed restore,78DF mapping shadow, AY R0-R12 traffic and safe D1/51 banking. At batch end only; excluded from concurrent destructive March and default Full/soak. Late saved-PC/table/opcode corruption can defeat recovery.

**Observables:** First RAM address/expected/observed/XOR region mask/phase and chip/bit pulses; auxiliary4/5/7 class/address-or-index/expected/observed/phase. No-fault stopped batch count wraps65536. Fault fields replace batch count; no persistent log. Analog output needs observation.

**Interpretation limits:** Low-nibble RAM/shared data/write/read/timing/supply paths; no unique component verdict. Isolated reruns required for combined failures.

**Recovery:** soak_recovery.

**Execution policy:** separately_selectable_with_fresh_qualification.

**Control-flow exposure:** Fresh qualification reduces risk but saved PC/stack or IM2/trampoline corruption can derail execution before checker/recovery. This separately confirmed real-return profile is excluded from startup/Full/default soak. No guarantee of survival of arbitrary return corruption.

**Specification:** [Detailed design](SINISTAR_LOAD_TEST.md#current-implementation-and-operator-controls).

**Actual implementation and remaining scope:** [Implementation record](SINISTAR_LOAD_TEST.md).

**Firmware locations:**

- [src/load.asm](../src/load.asm) — entry `load_return_start`.

**Existing host support:**

- [scripts/verify_load.mjs](../scripts/verify_load.mjs).

**Validation evidence:**

- [emulator PASS](../docs/validation/load-bc5eb2df44c3/load-verification.json) — TSRun mapped64K DOCK; all256 safe slice masks, representative batches, D1 POP data loss, missing IRQ/bank/AY faults, UI cancellation and real IM1/IM2 return profiles. Physical timing/supply/thermal replication pending..

**Required acceptance work:** Static mapping/register/stack audit; Image-bound emulator option combinations and D1/lost-write/IRQ/mapping/AY injections; Cancellation after all-key release; mute and first-fault recovery; Physical cold/warm mixed-load reproduction; optional return-corruption exposure documented.

## Updating a test

Keep IDs stable, record actual source/entry symbols when implemented, and attach evidence for the exact image and configuration tested. Use [TEST_IMPLEMENTATION_TEMPLATE.md](TEST_IMPLEMENTATION_TEMPLATE.md) for the register, mapping, algorithm and recovery details of nontrivial firmware. Retire an obsolete ID instead of assigning it to a new algorithm. Record meaningful behavior changes in [CHANGELOG.md](CHANGELOG.md).
