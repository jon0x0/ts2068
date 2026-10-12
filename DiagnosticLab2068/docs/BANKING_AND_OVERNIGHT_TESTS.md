# TS2068 banking and overnight diagnostics

This extends the ROM-only diagnostic design with independent banking stress, a Sinistar startup reproduction, and an interruptible overnight RAM test. These are firmware requirements and diagnostic procedures; they have not yet been implemented or validated on physical hardware.

## What Sinistar exercises

The reported incident used the latest published Sinistar on TSPico, working on one TS2068 and failing on another. The precise symptom is not yet available; failure before the initial screen is a working hypothesis. The public player cartridge was fetched and matched the local playable image byte-for-byte: 65,545 bytes, SHA256 `e16a68ead32e6aeed388f1ceb33f62061c45cff4680a89437df12c38e2500617`. The local project identifies this playable build as v58. This establishes the public player identity, not the bytes on the affected user's TSPico.

Inspected source hashes and bank-write line locations are in `sinistar-source-evidence.json`. The original root `MEMORY_MAP.md` describes an earlier scripted demo; it must not be treated as the current playable firmware contract.

### Startup before the title

The playable entry at `$8008` enters `title_boot` in `port/src/mining-scene.asm`. It disables interrupts, sets SP to HOME `$BFFF`, selects HSR `$10` (DOCK4), sets DECR `$02` (ECM), clears the border, and fills HOME `$6000–$77FF` with attribute `$42`. It then selects HSR `$18` (DOCK3+4) and jumps into chunk-3 title code. `port/src/title.asm` decompresses ROM title data into HOME `$A000`, then transposes that temporary bitmap into HOME `$4000–$57FF`. The title path subsequently selects `$98` (DOCK3+4+7) for frontend code. Source copies are supporting evidence for the matched public build; instrumented execution remains necessary to capture the exact failure on the affected machine.

| Early operation | Hardware exercised | Diagnostic separation |
|---|---|---|
| Native cartridge discovery and `$8008` fetch | HOME startup, DOCK selection, cartridge header/address/data | Earliest entry marker before drawing |
| HOME `$BFFF` stack | U12/U13 and upper-RAM control/addressing | Register-only RAM test before enabling a stack |
| `$10 → $18` and chunk-3 instruction fetch | HSR, `/ROSCS`, external ROM response, buffered address/data | Read known chunk-3 signatures before executing its code |
| ECM attribute fill `$6000–$77FF` | U6/U7, write path and second display-plane fetch | Write/read attributes separately from bitmap |
| RLE output/read at `$A000` | U12/U13, RAM addressing and retention during decoding | Compare ROM → temporary RAM → display RAM stages independently |
| Bitmap writes `$4000–$57FF` | U6/U7, bitmap address permutation and pixel fetch/output | CPU readback versus visible image |
| `$18 → $98` frontend transfer | Chunk-7 selection and external fetch | Separate chunk-7 integrity test |

Interrupts are disabled during the initial title drawing. A failure before the first screen therefore does not require an audio ISR fault to explain it. Banking remains plausible, but so do upper RAM, video RAM, virtual-cartridge response timing, contact integrity, power, and failure to enter the cartridge at all.

### Runtime stress after startup

The playable renderer frequently selects ROM data/code while keeping DOCK4 resident. `mining-scene.asm` owns a HOME IM2 table at `$7A00` and trampoline at `$7B7B`. Its ISR first selects `$10`, changes to a temporary HOME audio stack at `$5ED0`, runs audio work that includes `$D0` (DOCK4+6+7) and `$50` (DOCK4+6) selections, restores the normal stack and saved HSR shadow at `$78DF`, and returns. Other frontend/assembly paths map DOCK3 with interrupts disabled and adjusted stacks. ECM continuously fetches both HOME display planes while CPU code accesses cartridge overlays.

This combines external-memory access, interrupt stack activity, RAM state, mode-2 video fetches, and AY I/O. Dense use of all eight ROM chunks exercises address combinations that a small cartridge may never use. Emulator checks support software correctness but do not establish electrical margins on a TS2068/TSPico pair.

## Banking stress modules

Each module starts with its own entry/status marker, checks prerequisites, executes a bounded batch, and reports before proceeding. Keep PC, stack, ISR/vector and workspace visible at every planned mask. Check memory contents as well as HSR readback. A readback match alone is not proof that the expected device answered.

### Static external ROM qualification

Embed distinct chunk identifiers and address-dependent patterns in every supplied DOCK chunk. First qualify CPU access to each chunk using conservative delays and no interrupts. Compare first/last bytes, addresses around `$xxFF/$xx00` boundaries, dispersed samples, and full chunk CRCs. Use both complements and varied data bytes in signature regions; a constant-filled chunk is a weak address/data test. Execute from the opposite ROM anchor when inspecting its counterpart.

Only after stable ROM reads should the test assign a fault to a transition. Otherwise report `EXTERNAL ROM READ PATH`, including chunk, address, expected/observed bytes and whether results change with added delays.

### Rapid HOME and DOCK alternation

For each non-executing target chunk, repeat HOME → DOCK → HOME, reading unmistakably different known data immediately after each change. On HOME RAM chunks, create and verify sacrificial address-dependent sentinels first. On HOME ROM chunks, compare embedded known bytes only after the ROM identity is established, or compare repeatable observed signatures and report identity uncertainty separately.

Vary direction and masks: one bit at a time, simultaneous multiple bits, alternating legal masks, all safe ordered pairs, and a repeatable pseudorandom mask sequence. Always preserve the executing anchor. Use chunk 0 and chunk 4 kernels to cover the other anchor's bit. Masks that leave no DOCK execution path require a verified HOME gateway and are a distinct optional test. HSR `$FF` requires register-only operation with no HOME stack/workspace access. Do not imply one stack-based loop can safely run every mask.

After selecting a chunk, compare multiple offsets rather than a single magic byte. Detect stale previous-bank contents, aliasing, missing selection, unexpected HOME changes and unstable read values separately. Check write isolation by selecting ROM over a sacrificial HOME byte, attempting a write, restoring HOME, and verifying its original value.

### Response timing sweep

Use progressively shorter delays between the HSR write and first target read: long conservative delay, a few NOPs, and the earliest read allowed by a correct Z80 sequence. Do not insert deliberate out-of-spec bus cycles. Vary sequential versus scattered reads, page boundaries, block reads and changing data patterns. Include stable-bank repeated reads without HSR changes as a control.

Run explicit `OUT (C),A` with high port byte zero and, separately, the immediate `OUT ($F4),A` form used by Sinistar. The latter places A in the high I/O-address byte as well as on the data bus. Stock low-byte port decoding should yield the same banking behavior, but reproducing both forms can expose an incompatibility in external decoding. Changes should be logged as protocol/timing observations; they do not uniquely prove a defect in TSPico or SCLD.

Count actual transitions in batches so logging does not dominate the shortest-delay path. Display switches completed and read comparisons performed separately. Throughput is measured for the actual batch, not an assumed theoretical toggle rate.

### Sinistar startup reproduction

Offer an isolated startup profile with the observed `$10 → $18 → $98` sequence, mode 2, no interrupts, and only previously qualified HOME RAM. First run a data-only version: read ROM3, copy/decode a bounded diagnostic payload into `$A000`, verify it, transpose it into `$4000`, verify the display bytes, and then inspect ROM7. Bounds and sentinel checks prevent a corrupt encoded stream from running indefinitely or overflowing RAM.

Add a ROM execution-transfer variant only after the data-only tests pass: run a tiny verified chunk-3 routine that writes a register result and jumps back to the resident anchor, then do the equivalent chunk-7 transfer. Such a test can reveal instruction-fetch timing problems that data reads miss, but a corrupted fetch can defeat software recovery. The UI must distinguish DATA READ and EXECUTION TRANSFER results.

Use separate visible entry markers before mode selection, after external reads, after temporary-RAM verification, and after screen publication. Report the last completed stage even if a subsequent test does not return, insofar as border/speaker operation remains observable. Do not use display text as the only pre-display marker.

### Interrupt and mixed-load stress

Only after standalone banking, RAM and bounded interrupt tests pass, combine foreground bank selections with a ROM-owned interrupt handler that temporarily chooses an alternate data mapping and restores the mapping interrupted. Establish and document the shadow-update protocol; otherwise the stress firmware can create its own software race. The default diagnostic ISR remains ROM-resident and does not need to execute from suspect HOME code.

A closer Sinistar profile may use a verified HOME IM2 table, bank-selected ROM audio work and a tested temporary stack. Avoid copying Sinistar's fixed RAM addresses without auditing all selected chunks. Divide masks into families whose live stack/workspace remain exposed; change families through a stackless ROM transition. Check stack guards, saved mapping and data sentinels at batch boundaries. Deliberately vary foreground phase so interrupts sample different parts of the safe transition protocol. Never intentionally hide an active vector/stack just to generate stress.

Compare normal video, mode 2, and mode 6; ROM reads alone versus alternating cartridge reads/HOME writes; interrupts disabled versus enabled; AY I/O absent versus present. Enable one load at a time before the combined run. Restore mode 0 before FE border reporting, mute AY, inhibit interrupts and enter a fixed ROM recovery path on a detected error.

Global DOCK/EXROM selection is a separate gateway-based test. Do not rapidly toggle DECR bit 7 from DOCK code. Use only documented video modes, and do not sweep undefined DECR values or peripheral ports.

## Overnight RAM and combined soak

The default soak scheduler and minimal alarm obey [FAULT_CONTAINMENT.md](FAULT_CONTAINMENT.md) and remain stackless in ROM. RAM-held progress/history is optional and validated; corrupt counters cannot control addresses, mappings or unbounded loops. Advanced interrupt/stack/execution profiles are separately selected and disclose the hardware-dependent control-flow exposure.

Provide RAM-only, banking-only and combined soak presets, with 1-hour, 8-hour, 24-hour and continuous nominal durations. The first three are available when the timing source is qualified; otherwise present a pass-limited run or clearly label the elapsed estimate. All presets begin with normal resource qualification. A longer run does not compensate for skipping coverage of part of memory.

RAM-only cycles complete March/pattern passes, varied deterministic random seeds, ascending/descending traversals and write-hold-read phases. Test all three physical 16K regions, including RAM formerly used by firmware workspace. Vary hold lengths and patterns across iterations. Holds use ROM execution with normal CPU refresh; neither `DI` nor `HALT` disables refresh. A failing hold indicates a retention/refresh-path problem under the specified conditions, not its unique cause.

For each pass, record its algorithm, seed, region, first failure, affected bit mask/chip paths and saturating error count. Retain the first fault even if later passes succeed. Use 32-bit counters for pass/batch/error totals and qualified elapsed time, with explicit saturation or wrap flags. Count a cancelled or failed partial pass separately from a completed pass.

### Status screen and interruption

The normal 32-column dashboard has a fixed header and stable fields: preset, elapsed/remaining time, current algorithm/region, pass count, bank-transition count where applicable, errors, first-fault summary, and the current reporting/coverage mode. Refresh text at a modest cadence between safe test batches; a small activity indicator should continue even before a full pass completes. Use `RUNNING`, `PAUSED`, `FAILED`, `LIMITED` and `STOPPED` text, not color alone.

Controls: P pauses at the next safe boundary; SPACE resumes; BREAK stops and shows the preserved report; M mutes/unmutes the repeating alarm. Accept keys through direct bounded scans between batches. Aim for a healthy machine to acknowledge pause/stop within one second, and document the actual measured maximum. Do not pause in the middle of a bank handover or freeze a partially written RAM test pattern without recording its state. Resume by restarting that phase if needed. Stopping remains inside the diagnostic UI; returning to overwritten BASIC is unsafe.

During video-RAM tests, screen text is temporarily unavailable or corrupted. Do not reserve the dashboard's memory permanently. Mark this phase with border/beeper activity; after verification, redraw the dashboard. During retention holds, do not write a status screen into the region being held. Display a clear pre-hold message, then use border activity or a timer stored outside the target. If all HOME RAM is under one full-memory test, keep only register state and redraw afterward.

### Failure notification and degraded operation

Default unattended behavior is to latch the first fault, finish the current bounded comparison batch, restore a known mapping, and enter a repeating visible/audible alarm report. The user can acknowledge it and inspect details, resume selected tests, or stop. Optional continue-on-error mode accumulates summaries with a cap on records and retries; it must not overwrite the first fault or silently lose the overflow count. Live “0 errors” is always “so far,” never a final PASS.

If workspace guards/readback fail, immediately abandon stack-based operation through a fixed ROM jump; do not `RET` through suspect RAM. Retain the current first-fault address/expected/observed bytes in reserved registers across the recovery jump. Disable interrupts, restore the low ROM anchor, and use register-only beeper/border codes. Store a compact record into newly requalified RAM only after verification; if none is usable, repeat the compact record and report LIMITED rather than attempting the full UI.

Preserve enough information in registers for the currently detected fault; a rich history cannot be guaranteed when all HOME RAM fails. A physical ROM-only cartridge has no persistent writable log, so power loss/reset erases software records. Future Pico resources can add independent alarms and durable logs. CPU-clock loss, bad opcode fetches, or an SCLD failure affecting both outputs can prevent notification; ROM-only software cannot guarantee an alarm for those cases.

### Intermittent and thermal interpretation

Record time/pass of first failure and whether immediate retries reproduce it. An overnight run may expose failures that correlate with warm-up, but the TS2068 has no temperature reading available to this firmware. Label such faults INTERMITTENT or TIME DEPENDENT, not OVERHEATING CONFIRMED. Correlating them with measured temperature, supply voltage and cooldown/retest results requires an external instrument or future sensor. The firmware should not prescribe obstructing ventilation or otherwise forcing overheating.

## Comparing the affected and working machines

Use the same image hash, TSPico hardware/firmware/settings, power setup and removable accessories on both machines. Record whether stock BASIC starts, whether the earliest diagnostic entry marker appears, and which isolated module first fails. Where available, repeat with a physical ROM cartridge to separate a virtual-dock interaction from a general HOME/DOCK fault. Perform cold-start and warmed repeat runs separately.

If delayed bank reads pass while earliest reads fail, investigate selection/response timing and loading with probes. If RAM-only fails with stable ROM reads, focus on the identified HOME region/path. If CPU bitmap readback passes but the screen is wrong, focus on video fetching/output. If banking fails only with interrupts enabled, examine the mapping/ISR protocol and interrupt/stack paths. These are investigation directions, not automatic component-replacement verdicts.

The next incident evidence needed is the actual image hash/settings and whether it stayed in BASIC, produced a blank screen, corrupted video, stalled, or reset. Pending that information, preserve both startup and runtime stress profiles in the cartridge.
