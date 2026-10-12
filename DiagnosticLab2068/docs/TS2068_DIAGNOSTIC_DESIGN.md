# TS2068 diagnostic cartridge design

Design baseline: ROM-only cartridge for the stock TS2068. Future versions may use PicoCartridge2068 resources. This describes the comprehensive target; [the v0.1 implementation record](tests/V01_ROM_KERNEL.md) identifies the smaller executable milestone and its emulator evidence. Physical validation is pending.

The cartridge executes diagnostic code from ROM and starts its own tests without assuming that HOME RAM, the keyboard, display, interrupts, or sound work. Its first stage uses only CPU registers. It reports failures through redundant border and beeper codes, then promotes only tested resources into service. Results identify affected circuits and likely RAM chips without treating every memory error as proof that the chip itself is defective.

## Scope and unavoidable dependencies

[FAULT_CONTAINMENT.md](FAULT_CONTAINMENT.md) is the governing crash-avoidance contract. Default scheduling, RAM/banking/soak control and minimal reporting remain stackless in ROM after resource qualification; richer RAM state must never become essential for recovery. Stack guards reduce risk but cannot protect an imminent RET from an intermittent stack failure. Basic interrupt arrival should use a fixed ROM checkpoint where practical; RAM gateways, execution transfers and advanced interrupt returns are distinct exposed modules.

An ordinary passive DOCK ROM is not a reset-vector replacement. At power-on the CPU starts in HOME ROM; the HOME/EXROM initialization discovers LROS and transfers control after using HOME RAM. Carl Miles' cartridge follows this path. Consequently a passive ROM cartridge cannot guarantee entry when the system ROM, early RAM initialization, clock, or cartridge-selection path is broken. Register-only diagnostics remove RAM dependencies **after entry**, not before it. [S1 §§1.1.2–1.1.3, Figure 1.1-4; S3]

Use a native LROS build for current hardware. Also define a separate direct-reset firmware entry for a future independently decoded cartridge, or for service equipment that actually substitutes its ROM at reset. Do not claim that a DCK ROM descriptor changes the hardware reset mapping. A HOME-ROM substitution build alone does not preserve access to the original HOME ROM; that checksum requires hardware that can expose both separately.

J4 exposes `/BE` on pin 33. An independently decoded ROM-only board could suppress internal memory on its own ROM cycles and supply the reset vector without HOME startup. That needs board logic beyond an ordinary `/ROSCS`-selected ROM and is a future hardware option, not a firmware feature of the present cartridge. J4 lacks reset, NMI, and an independent clock input. [S1 §2.4.2, PDF p70]

The CPU must execute enough instructions, and cartridge address/data paths must work enough to fetch them. Border and beeper share the SCLD and speaker/video circuits; neither is an independent proof that the SCLD works. A fault that stops the CPU clock, corrupts opcode fetches, or removes the executing bank can defeat software recovery. All software waits are bounded, but software cannot promise recovery from every hardware fault.

HOME RAM tests are destructive. Run in an exclusive diagnostic session; never return to an overwritten BASIC environment. Completion offers another diagnostic run or a hardware reset. Default tests use documented built-in ports and leave external-device probing disabled.

## Physical memory and chip attribution

The schematic has six 4416 DRAMs, each 16K × 4 bits. Each pair supplies one 16K × 8-bit region. A chip carries a nibble at **every address** in its region; it does not occupy four contiguous byte ranges. [S1 §§2.1.5, 2.1.10; S2]

| HOME address range | HSR chunks | D0 D1 D2 D3 | D4 D5 D6 D7 | Selection and path |
|---|---|---|---|---|
| `$4000–$7FFF` | 2, 3 | U6 | U7 | `/CAS1`; SCLD video address path, U5 address buffer, U9 data buffer |
| `$8000–$BFFF` | 4, 5 | U12 | U13 | `/CAS2`; U10/U11 address multiplexers and A7R path |
| `$C000–$FFFF` | 6, 7 | U17 | U18 | `/CAS3`; U10/U11 address multiplexers and A7R path |

The supplied schematic marks the display pair 150 ns and upper pairs 200 ns. Its data labels map U6/U12/U17 to D0–D3 and U7/U13/U18 to D4–D7. The 4416 data-pin sequence is pin 2, 3, 15, 17 for the four successive bits; check fitted chip markings and the PCB revision before using pin-level repair instructions. [S2]

For a failure at address `a`, compute `e = expected XOR observed`. If `e & $0F`, name the region's low-nibble chip; if `e & $F0`, name its high-nibble chip. Preserve the individual bit mask even when several bits map to the same package. Example: `$C123`, expected `$AA`, observed `$8A`, error `$20` → D5 in U18's data path.

Report “U18 / D5 path suspect,” with expected/observed bytes, rather than “replace U18.” Shared failures can come from CPU data lines, U9, SCLD control, U10/U11, solder joints, supply, or timing. A recurring D5 error in all three regions suggests a shared data path. All bits failing within one region suggests region selection, strobes, or addressing. Errors separated by a power-of-two address distance suggest an address path; local cell failures in one nibble make that DRAM a stronger suspect. Display data errors with clean CPU readback implicate video fetch/serialization/output paths rather than automatically U6/U7.

U16 is the 16K HOME ROM at `$0000–$3FFF`; U20 is the factory 8K EXROM, documented at `$0000–$1FFF` in the EXROM source. U3 is the SCLD, U19 the Z80, U14 the AY-3-8912. [S1 §§2.1.4, 2.1.6; S2]

### CPU chunks and execution contract

HSR `$F4` is an eight-bit overlay mask, not a relocatable bank number. Bit N=0 selects HOME chunk N; bit N=1 selects its external counterpart. DECR `$FF` bit 7 globally chooses DOCK (0) or EXROM (1). [S1 §2.1.8.1, original PDF pp45–47]

| Chunk | CPU range | HOME contents | Proposed DOCK contents |
|---|---|---|---|
| 0 | `$0000–$1FFF` | U16 lower half, reset/IM1 vectors | LROS header, vectors, low-address register-only kernel and reporting |
| 1 | `$2000–$3FFF` | U16 upper half | ROM constants, chip tables, optional test code/data |
| 2 | `$4000–$5FFF` | U6/U7, first display | Test assets and chunk signature; HOME during display writes |
| 3 | `$6000–$7FFF` | U6/U7, second display/normal OS workspace | Test assets and chunk signature; never selected by startup header |
| 4 | `$8000–$9FFF` | U12/U13 lower half | High-address kernel, ROM-check code, UI and safe handover entry |
| 5 | `$A000–$BFFF` | U12/U13 upper half | UI code/font/assets; selected only when HOME underneath is not under test |
| 6 | `$C000–$DFFF` | U17/U18 lower half | Additional patterns/signatures; otherwise HOME |
| 7 | `$E000–$FFFF` | U17/U18 upper half | Additional patterns/signatures; otherwise HOME |

Baseline physical capacity is 64K ROM; retain a 16K minimal build containing chunks 0 and 4 if the board can decode those positions. A physically contiguous programmer file and a sparse DCK have different layouts. No DCK chunk is declared RAM for a physical ROM-only build. Assets may be generated algorithmically or copied from a different selected ROM chunk into an exposed HOME destination; do not select cartridge ROM over a write target.

Proposed LROS header: unused byte 0, type 1 at byte 1, little-endian entry `$0100` at bytes 2–3, low-active chunk specification `$EE` at byte 4 (chunks 0 and 4 used). Bit 3 remains 1 for the ROM handoff's HOME chunk-3 dependency. Confirm this header and actual entry mapping against stock-ROM execution before release. The low entry immediately executes `DI`, establishes its register contract, and never returns to the OS. [S6]

| Operation | HSR | DECR | Execution and writable state |
|---|---|---|---|
| Initial LROS handoff | expected `$11` | establish `$40` after `DI` | Low ROM entry; no stack use |
| Complete 48K register-only RAM pass | `$01` | `$40` | Execute chunk 0; all HOME `$4000–$FFFF` exposed; no RAM workspace |
| HOME ROM checksum | `$10` | `$40` | Execute chunk 4; HOME chunks 0/1 exposed; no stack required |
| UI with video RAM verified | `$01` or `$11` | `$40 | mode` | ROM code; tested HOME workspace outside selected ROM/video targets |
| ROM data fetch | anchor mask OR `1<<source_chunk` | DOCK, same mode | PC stays in selected ROM anchor; SP/workspace, if used, stay HOME |
| EXROM read | `$01` | `$C0 | mode` | Execute small verified HOME gateway; DOCK is unavailable |
| EXROM exit | `$00`, then restore DOCK, then anchor | `$40 | mode` | Remain in HOME gateway until selected ROM return path is restored |

All baseline interrupts remain disabled. DECR bit 6=1 inhibits the frame interrupt. Establish known complete DECR values when taking over the machine; afterward maintain software shadows. Manual and stock-ROM code support `$F4/$FF` readback, so test it as a separate observation; recovery uses the known shadow rather than trusting a failed readback. The cartridge skill's conservative rule against depending on readback is appropriate for control logic. [S1 §2.1.13; S6]

Transfer low ROM → high ROM with both anchors selected and a direct `JP` to the high entry; the high entry can then clear bit 0. Reverse with both anchors selected, jump low, then clear bit 4. No HOME instruction execution or return stack is required. Keep entry points and return paths explicit. To test RAM underneath chunk 4, execute low; to read HOME ROM or test chunk 0 selection, execute high. A faulty HSR can still invalidate a fetch despite the planned safe mapping.

## Startup and resource promotion

1. **Entry marker.** `DI`; no `CALL`, `RET`, `RST`, `PUSH`, `POP`, RAM variables, or self-modifying code. Establish a known normal video mode, DOCK selection, and FE shadow. Emit a short blue-border/beeper sequence. This marks code entry, not “CPU and SCLD passed.”
2. **Cartridge integrity.** Check executing ROM and later each exposed ROM chunk using stored length and CRC records; add distinct chunk/address signatures to detect aliases. Exclude the CRC storage field from its own checksum. Address/data corruption can also corrupt the checker, so success is supporting evidence rather than an absolute guarantee.
3. **Basic CPU consistency.** Exercise register transfers, arithmetic/logic flags, shifts, compares, alternate registers, and IX/IY with ROM vectors and conditional branches. Stack-dependent instructions are deferred. The result covers exercised instructions only.
4. **HOME RAM discovery and tests.** Force the documented HOME mapping for all RAM and test all three physical regions from low ROM. Poll limited hotkeys between bounded phases; absence of keyboard input must not stop automatic testing.
5. **Select workspace.** After complete passes, choose a small tested block outside both display files, record the specific permitted addresses, and establish stack plus guards. Prefer upper RAM. A passing block can enable limited features even if another chip/region fails; do not give the entire machine a “RAM good” flag. If no reliable block exists, remain in register-only mode.
6. **Select display.** Standard text requires verified bitmap and attribute addresses in U6/U7. A failed display test preserves audio/border reporting and may offer only best-effort degraded text. Upper RAM cannot become screen RAM through HSR, and the SCLD does not fetch video from cartridge ROM.
7. **Run independent modules.** Continue tests whose prerequisites remain available. Gate EXROM/bank-source transitions and interrupts explicitly. Record PASS, FAIL, UNRECOGNIZED, NOT RUN, and NEEDS OBSERVATION separately.

The register-only kernel uses direct jumps or `JP (IX)` continuations instead of a memory return stack. Document register ownership per routine. For example, the RAM loop reserves HL for address, DE for remaining length, B for pattern/phase, C for accumulated error bits, and alternate registers/IX/IY for continuation and compact region summaries. Report one region immediately if detailed evidence exceeds register capacity. Do not silently spill to RAM.

User choices in limited mode are direct key combinations selecting full scan, RAM soak, video, and repeat-code mode. Automatic tests never require a working keyboard. The normal menu is enabled only after tested workspace and a usable display exist.

## RAM tests

### Complete automatic pass

| Test | Concrete operation | Main evidence |
|---|---|---|
| Data bus | At several separated addresses write/read `$00,$FF,$55,$AA`, walking 1 and walking 0; read after every write | Stuck bits, shorts and transition errors |
| Address aliases | Base and power-of-two offsets inside each 16K region; perturb one sentinel while checking all others; repeat across `$4000,$8000,$C000` and 8K boundaries | Address aliasing, region/chunk selection |
| Full patterns | Fill entire target with each complementary pattern, then read the entire target; ascending and descending order | Every byte and bit observed; avoids the weakness of only immediate write/read |
| March C minus | `⇕(w0); ↑(r0,w1); ↑(r1,w0); ↓(r0,w1); ↓(r1,w0); ⇕(r0)` with bytes `$00/$FF` | Stuck, transition and selected coupling faults |
| Address data | Address-derived bytes using both low and high address bits and complements, with distinct region salts | Additional address faults and cross-region aliasing |
| Repeatability | Repeat failing patterns at first failure and dispersed addresses without stopping the whole scan | Persistent versus intermittent failure |

Use 16-bit region lengths of `$4000`; include both endpoints and explicitly stop after `$FFFF` without accidentally walking into ROM. Before trusting data, verify that the target reads HOME rather than a cartridge signature. A ROM-overlay failure is a mapping result, not “RAM passed.”

March C minus is useful but does not cover all intra-word/nibble coupling faults. Follow with `$0F/$F0,$33/$CC,$55/$AA` and walking patterns over every byte, changing aggressor bits while reading other bits. Extended mode uses March variants and address-neighbor inversions. Name the exact algorithm and coverage instead of claiming an exhaustive physical-cell test.

### Random and long term modes

Use a specified nonzero 16-bit LFSR (for example right-shift, conditional XOR `$B400`) to generate repeatable data. Record the seed and traversal order; restart the generator for the comparison pass. Never store expected random bytes in the target or seed from unverified frame-counter RAM. Vary seeds, complements, traversal direction, and region salts each pass. Record seed, pass number, algorithm, first failing address, expected/observed values, OR of error bits, and saturating error count when trusted workspace permits.

Provide separate options: continuous March/pattern/random soak; write-once/hold/read; repeated write/read stress; and first-failure freeze versus bounded continuation. Suggested hold choices are 1, 10, 60, and 600 seconds **nominal**, calibrated on real TS2068 timing. A timer based on instruction counts shares the CPU clock; show that limitation if no independently verified timing source exists.

During a hold, run a ROM loop without target memory accesses. Normal instruction fetches continue Z80 refresh activity. `DI` does not turn DRAM refresh off, and `HALT` does not provide a no-refresh retention test. A passive cartridge cannot directly command arbitrary RAS/CAS timing or freeze refresh without risking execution. Report this as retention under normal refresh. [S7]

Separate upper-RAM refresh-path evidence from display-RAM evidence. The SCLD generates multiplexing/refresh-related signals including A7R, and display DMA accesses can mask weaknesses in the display RAM's refresh path. Tests in different documented video modes and different CPU access patterns add evidence; confirming strobe timing requires an instrument. Do not equate a hold failure with a proven SCLD defect.

### Testing the workspace itself

No HOME block is permanently exempt. Before testing a live stack/workspace block, either move state and stack to another freshly verified block in another region, or transition to the register-only kernel, abandon the stack, retest the complete region, and rebuild workspace afterward. Display patterns and system variables are also overwritten during full RAM scans. Save only compact summaries in registers during the final workspace pass. If canaries or workspace readback fail, discard RAM-resident state, `DI`, return through a fixed ROM entry, and resume limited reporting. Do not execute a `RET` through suspect memory.

## Reporting when video RAM fails

[DEGRADED_DISPLAY.md](DEGRADED_DISPLAY.md) specifies UI-03: a normal ROM-rendered page for upper-RAM-only faults and best-effort large pixel-lane or attribute-coded text for U6/U7 failures. Host prototypes check32 stable-nibble fault values, but target rendering/physical readability remain unimplemented/unverified. Minimal pulse reporting is never conditional on text success.

Border and beeper reports are temporal codes generated by ROM loops. They do not read display RAM or wait for interrupts. Timed horizontal stripes may be offered after timing/interrupt validation, but the baseline must be decodable even with distorted sync.

Each repeated frame has a long synchronization tone/white border, a class pulse group, a pause, an item group, a pause, and a detail group. Each pulse is nominally 150 ms on / 150 ms off, group gaps 700 ms, frame gap 2 s. Audio and visible transitions carry the same count. Codes are numbers, so monochrome video remains useful. Never rely exclusively on red/green distinction.

| Class | Item/detail meaning |
|---|---|
| 1 | Firmware/entry consistency: item 1 ROM checksum, 2 chunk signature, 3 CPU consistency; detail 1 unspecified |
| 2 | RAM: item 1 U6, 2 U7, 3 U12, 4 U13, 5 U17, 6 U18; detail 1–4 local nibble bit 0–3, 5 several bits, 6 shared/region path |
| 3 | Mapping: item 1 HSR readback, 2 HOME/DOCK visibility, 3 EXROM selection; detail 1 mismatch, 2 unstable, 3 unavailable prerequisite |
| 4 | Interrupt/timing: item 1 absent, 2 rate inconsistency, 3 inhibit failure; detail 1 unspecified |
| 5 | I/O: item 1 keyboard path, 2 AY register path, 3 cassette input; detail identifies row/register group when available |
| 6 | Tests complete or limited: item 1 automatic tests passed, 2 failures recorded, 3 limited tests; detail 1 repeat report |

For U18/D5, use class 2, item 6, detail 2: D5 is the second bit of the high nibble. Repeat every affected chip; explain code groups on a printed reference card. Completed automatic tests are not evidence that the user has checked analog audio/video or every key. Cold entry silence means the firmware did not produce an observable signal, with several possible causes; it is not a unique Z80 fault code.

Both `$4000` and `$6000` display planes are in the **same U6/U7 chips**. Switching display files cannot escape a bad U6 or U7. Standard bitmap D7 is the leftmost pixel in a byte; D0 the rightmost. An intact high nibble can show the left four pixels, an intact low nibble the right four. A large 4-pixel glyph duplicated into both nibbles can improve readability under simple stuck-bit faults. Attribute errors can still make it invisible, and arbitrary intermittent errors defeat this approach. Qualify degraded text as best effort; retain the full border/beeper code. Use per-bit masks obtained from multiple patterns and readback, not an assumption that an entire nibble is good.

## SCLD tests by function

| Function | Test and prerequisite | Interpretation and recovery |
|---|---|---|
| HSR latch/read path | Write masks preserving active ROM and workspace; compare `$F4` readback | Latch/read path evidence; restore shadow on mismatch |
| HOME/DOCK selection | Give each DOCK chunk distinct signatures; compare full selected chunk CRC, restore HOME and verify saved HOME sentinel | Readback alone does not prove selection; active chunk tested from the other ROM anchor |
| CPU write isolation | With interrupts off, select DOCK ROM over a sacrificial tested HOME byte, attempt writes, restore HOME and compare | Checks hidden-HOME isolation; failure is destructive to test data only |
| Global EXROM selector | Use verified HOME gateway; compare HOME/DOCK/EXROM signatures and checksums | Requires RAM execution for the transition; skip when unavailable |
| HOME ROM select | Repeat HOME checksums and address-separated reads from high ROM anchor | Includes U16 enable/address/data path; unknown ROM is not proof of select failure |
| DRAM selection/mux/refresh | Independent 16K RAM, alias, hold and stress tests; correlate nibble and region masks | U3 versus DRAM/buffers/supply remains differential diagnosis |
| Display fetch/address generation | Write/read verified screen arrays with row/column IDs, alternating lines, bit lanes, and boundary markers | Clean RAM readback plus wrong image points toward fetch/address/serialization/video paths |
| Arbitration and CPU clock gating | Compare ROM/upper-RAM access loops with display-RAM loops, referenced to validated interrupts; stress simultaneous drawing | Expected contention differences are baseline measurements; stalled clock cannot be timed out by CPU software |
| Interrupt generation | Owned handler and tested stack; finite polling loop counts handler entries | Missing interrupts return FAIL; no unconditional `HALT` |
| Interrupt inhibit | Compare bounded counts with DECR bit 6 cleared/set, after clearing residual pending effects | Test both states, restore inhibit and `DI` on exit |
| Normal/second/ECM/hires modes | Distinct patterns and CPU readback in documented modes | Record user observation separately from digital memory success |
| Attribute decode | Ink/paper combinations, bright pairs, flash controls, 8×1 ECM transitions | Exercises color selection/bright/flash; analog output remains user/instrument judged |
| Border/speaker/tape control | Independent FE bit transitions preserving unrelated FE outputs | Shares U3 and downstream analog components |
| Keyboard scan | Individual half-row reads, no-row and multi-row tests | Row/column correlation distinguishes likely common paths |
| AY bus control and clock | Masked AY register tests plus audible tone/noise/envelope tests | Separates bus/register evidence from clock and analog audio |

All 256 HSR values can be exercised in extended mode only when an anchor remains guaranteed, or from a verified HOME gateway whose HSR bit is clear. Use the union of low- and high-anchor tests for latch bits; avoid switching away the running PC merely to claim exhaustive combinations. A bad readback with correct memory selection and the converse are separate results.

The SCLD's expected clocks derive from 14.112 MHz: CPU 3.528 MHz, AY 1.764 MHz, line 15.75 kHz, frame approximately 60.1145 Hz (`896 × 262` master clocks/frame, 58,688 nominal CPU T-states/frame). The original interrupt paragraph's 15.635 ms conflicts with that counter-chain derivation; use the counter-chain baseline and confirm physically. A CPU/frame ratio test cannot verify absolute oscillator frequency when both clocks derive from the same crystal. Flash changes state every 16 frames, with a full on/off cycle about 1.879 Hz. [S1 §§2.1.8.2–2.1.8.4]

The first interrupt test uses a ROM-owned IM1 vector in DOCK chunk 0 and a tested stack outside screen RAM. ISR code and all its data must remain visible. Count during a bounded ROM loop, then `DI`; check stack guards. HOME-ROM checksum phases do not enable IM1 into the machine's HOME handler. An optional ROM IM2 vector table can support high-anchor phases, but only with verified interrupt acknowledge/vector behavior and tested stack. NMI is a future explicit service option; J4 provides no NMI button signal.

## ROM identity and integrity

CRC32 means CRC-32/ISO-HDLC: reflected polynomial `$EDB88320`, initial `$FFFFFFFF`, final XOR `$FFFFFFFF`, check value for ASCII `123456789` is `$CBF43926`. Calculate over exact installed ROM bytes, not a DCK header, padded image, or entire CPU map. [S5]

| ROM | Bytes | CPU range for checksum | Stock CRC32 | Stock SHA1 for host validation |
|---|---:|---|---|---|
| HOME U16 | 16384 | HOME `$0000–$3FFF` | `BF44EC3F` | `1446cb2780a9dedf640404a639fa3ae518b2d8aa` |
| EXROM U20 | 8192 | EXROM `$0000–$1FFF` | `AE16233A` | `7e265a2c1f621ed365ea23bdcafdedbc79c1299c` |

The local stock U16/U20 files and TSRun ROMs match these MAME identities. The reference library's `2068Home.BIN` is `7D411FE9`, and `2068Exrom.BIN` is `526F5676`; label these as the library's modified images, not alternative stock checksums. Repeat each checksum at least twice and compare stability. Offer optional byte-for-byte comparison against embedded stock references for mismatch addresses when ROM capacity permits; a mismatch does not distinguish an intentional patch from faulty silicon.

Results: STOCK MATCH; KNOWN MODIFIED MATCH; UNRECOGNIZED STABLE; UNSTABLE READ; NOT RUN. A stable unknown ROM should remain usable for the other diagnostics. Recognized firmware identity does not certify every ROM path or eliminate bus faults.

HOME checksum executes in DOCK chunk 4 with HSR `$10`. EXROM checksum cannot execute from normal DOCK ROM because DECR bit 7 changes the source of **every selected chunk**. Copy a compact standalone checker/gateway into an individually verified HOME block, compare the copy byte-for-byte, `DI`, and enter by `JP`. It keeps all its opcodes, continuations, temporary state and any stack in HOME with that chunk's HSR bit 0. Set HSR `$00`, DECR EXROM/inhibit, then HSR `$01`; checksum only stock chunk 0. Return by clearing HSR, selecting DOCK, selecting the needed ROM anchor, and jumping to its fixed entry. Use no EXROM services or machine OS variables. Revalidate gateway/workspace before the operation; if no block qualifies, report NOT RUN. Keep the RAM routine minimal and disclose this exception to ROM execution.

Some emulators expose stock EXROM aliases in other chunks; do not interpret those as extra physical ROM capacity or depend on them as instruction storage. A verified 16K EXROM is a distinct installed-hardware profile and needs a separate identity/range entry. [S6; local Fuse source]

## Video tests

[VID-05](VIDEO_128_ATTRIBUTES.md) adds a checkerboard overview and planned full-screen cycle inspired by Mark Miller's [128 Colors](https://www.timexsinclair.com/computer_media/128-colors/index.html). Source authors and archive/tool provenance are collected in [THIRD_PARTY_CREDITS.md](../THIRD_PARTY_CREDITS.md). This test covers128 INK/PAPER/BRIGHT combinations rather than128 distinct palette colors; its host grid exists, while target firmware integration remains pending.

Use direct SCLD programming without the OS's screen-open/close or relocation routines. Video tests own the system and keep stack/workspace away from `$4000–$7FFF`. Only documented modes 0, 1, 2 and 6 are used. “High resolution graphics” in older manual wording for mode 2 refers to enhanced color detail; the 512-pixel display is mode 6. [S1 §2.1.13.1, §5.2; S6]

| Mode | DECR low bits | Required HOME bytes | Pattern |
|---|---:|---|---|
| Standard | 0 | `$4000–$57FF` pixels, `$5800–$5AFF` attributes | Eight color bars, all ink/paper pairs, normal/bright comparison, flash and steady controls |
| Second display | 1 | `$6000–$77FF` pixels, `$7800–$7AFF` attributes | Different labels and asymmetric corner markers; switch between first/second files |
| Extended color | 2 | `$4000–$57FF` pixels, `$6000–$77FF` attributes | Rainbow with ordered dithering plus diagnostic swatches and alternating per-line color strips |
| 512×192 | 6 | `$4000–$57FF` and `$6000–$77FF` pixel planes | Calibration grid, circle, diagonals, edge/center markers, 1/2/4/8-pixel gratings and plane identities |

Standard pixel offset at `(x,y)` is `((y & $C0)<<5) | ((y & 7)<<8) | ((y & $38)<<2) | (x>>3)`; mask `$80>>(x&7)`. Attributes use `(y>>3)*32 + (x>>3)` at `$5800` or `$7800`. ECM color bytes use the **same interleaved offset** as their corresponding pixel byte at base `$6000`, one attribute per 8×1 strip. The second display's normal attribute base is `$7800`, not `$7A00`. Verify addresses directly; derived library summaries contain inconsistencies here.

The ECM picture uses two palette colors per 8×1 strip with shared BRIGHT and FLASH fields. It provides 15 distinct base colors (bright black duplicates black) and many perceived mixtures, not hundreds of independently addressable hardware colors. Choose each strip's color pair by error minimization and apply a deterministic ordered dither. Include pure palette swatches, intensity ramps and known bit patterns so an attractive image does not conceal faults. Default FLASH=0 on the rainbow; a separate controlled flash strip tests that feature. Preview palette values are illustrative, not measurements of NTSC output.

For hires, each 16-pixel horizontal group is 8 bits from the primary file followed by 8 bits from the second file. Do not alternate files for every single pixel. DECR bits 5–3 select ink, with complementary paper; cycle all eight documented pairs. Include separate plane A/B patterns before the combined test to reveal a stuck fetch source. Gratings reveal serialization/order/bandwidth errors; circles and grids help adjust geometry, while composite output may blur the finest lines. Store readback and user visual judgement separately.

Timed display changes use a validated frame source when available. Otherwise use finite ROM delays and label timing nominal. Missing interrupts must not strand a video test. Restore normal mode, intended HSR, silent sound and inhibited interrupts on every exit.

Hires fixes the border through mode color selection; return to mode 0 before attempting FE-based border fault codes.

## Keyboard and input

Draw the physical TS2068 layout from TSRun's `keyboard.js`: number row; Q–P; A–ENTER; left CAPS, Z–M, SYMBOL, BREAK, right CAPS; wide SPACE below. There are 42 physical keys but 40 matrix positions. Both CAPS keys share one matrix position; BREAK closes CAPS+SPACE. Guided testing is needed to distinguish the physical CAPS keys, and firmware cannot distinguish which one was pressed from raw matrix data alone. [S1 §2.1.9; S8; S3]

| Port BC | Address row | D0 | D1 | D2 | D3 | D4 | Schematic row diode |
|---|---|---|---|---|---|---|---|
| `$FEFE` | A8 | CAPS | Z | X | C | V | CR11 |
| `$FDFE` | A9 | A | S | D | F | G | CR6 |
| `$FBFE` | A10 | Q | W | E | R | T | CR7 |
| `$F7FE` | A11 | 1 | 2 | 3 | 4 | 5 | CR8 |
| `$EFFE` | A12 | 0 | 9 | 8 | 7 | 6 | CR9 |
| `$DFFE` | A13 | P | O | I | U | Y | CR10 |
| `$BFFE` | A14 | ENTER | L | K | J | H | CR12 |
| `$7FFE` | A15 | SPACE | SYMBOL | M | N | B | CR13 |

Use `LD BC,row_port / IN A,(C)`, active-low D0–D4; mask away EAR and unused bits. `IN A,($FE)` uses A as the high address byte, not B. Poll from ROM; debounce through repeated samples without requiring frame interrupts. Verify release as well as press. Guided mode prompts left CAPS, right CAPS and BREAK separately, then shift/cursor combinations. Free mode highlights all raw closures and preserves “seen pressed” plus “seen released.”

No-key read with no rows selected checks stuck columns; single-row and controlled multi-row tests add row isolation evidence. One full failing half-row points toward its address/diode/connector path; the same input column failing across rows suggests KB input/common trace or SCLD. Unpressed keys remain UNTESTED; exit is CANCELLED, not proof of failure. BREAK cannot simultaneously serve as an unconditional exit while being tested; use a long hold after the guided BREAK step, a alternate hotkey, and cartridge restart/reset as fallback.

## Beeper AY cassette and joysticks

Beeper: toggle FE D4 while preserving border D0–D2 and keeping cassette D3 low. Offer nominal low/mid/high tones, silence, and a sweep. Display “Did you hear this?” as an observation; software cannot read the speaker. Speaker-path silence may be U3 output, amplification, speaker, or supply. Beeper fault codes are unavailable if this path fails.

AY U14 uses register select `$F5`, read/write data `$F6`; use explicit 16-bit ports so the high byte does not accidentally strobe joysticks. First silence R8–R10 and set R7 `$3F` (tone/noise disabled, port A input in the documented TS2068 convention). Check R0–R13 with walking and differing per-register patterns, masked to meaningful bits: fine tone FF; coarse tone 0F; noise 1F; R7 only safe tone/noise bits 3F; amplitudes 1F; envelope periods FF; shape 0F. Compare all relevant registers after writes to detect register-address aliases. Preserve port-A direction; never run unrestricted R7 `$FF` patterns. R14 reads physical inputs and is not an ordinary storage-register comparison; R15 is absent on the AY-3-8912. [S1 §§2.1.6, 2.1.7]

With register tests complete, play A, B, C separately, then combined tones, noise at several periods, fixed amplitude steps and representative envelope shapes. Nominal tone frequency is `1,764,000 / (16*period)` Hz; use nonzero periods. Register success cannot prove AY clock, mixer, DAC or amplifier function. Restore amplitudes zero and input direction on every exit. Analog judgement remains NEEDS OBSERVATION until the user confirms.

Cassette tests are opt-in: ROM-generated MIC pilot/data from immutable cartridge bytes, EAR level display and edge counter, and recorded-block verification directly against ROM. Every edge/header/data wait has a software timeout and cancellation check. A MIC→EAR loopback needs the correct coupling/level adapter; do not assume the low-level MIC output is sufficient or prescribe a direct wire as a valid calibrated test. Keep routine operation independent of EXROM cassette services. Test output, input, and complete record/playback paths separately.

Include optional built-in joystick tests now: R14 selected, port A input, read `$01F6` player 1 and `$02F6` player 2; mask active-low `$8F` (up/down/left/right/fire). `$00F6` selects neither; `$03F6` selects both and combines closures. Show press/release per control and cross-port isolation. Do not drive the joystick pins, and do not assume the stock joystick connector has a usable logic ground. Unconnected accessories are NOT RUN, not failed hardware. [S1 §§2.1.7, 4.3 and errata; S2]

## User interface and full test

Use a legible 32-column normal display with a simple title, one selected menu row, progress/status lines, and stable footer controls. Main entries: Full test; RAM quick/extended/soak; SCLD and mapping; Video patterns; Keyboard; Beeper and AY; Optional ROM checks; Cassette and joysticks; Results and repeat codes. Use words and symbols as well as colors. Keep technical details on an optional fault detail screen.

Full test runs the automatic bootstrap, complete RAM tests, safe banking, AY register checks and bounded interrupts, then offers guided video/audio/keyboard checks. ROM identity/checksum and connected-device tests remain optional. A full test report lists all skipped dependencies and incomplete user checks; it never announces “machine fully good” merely because automated comparisons passed.

Example fault detail: `U18 D5 PATH SUSPECT`, `$C123 AA -> 8A`, `MARCH DOWN / ERROR 20`, `Check U18, data path, CAS3`. Limited mode repeats the corresponding audio/border frame. In detailed mode retain the first failure, error-bit union, region totals and iteration/seed, rather than flooding the screen.

Choose module prerequisites by resource rather than test order: a failed U6 should not stop upper-RAM tests, beeper or AY register checks; a failed keyboard should not stop automatic RAM tests; missing interrupts should not stop finite-delay video; a ROM mismatch should not change the assumed machine model or trigger Spectrum paging tests.

## Lessons from the existing diagnostics

Carl Miles ART 1.0 tests three 16K RAM regions, CPU, SCLD ports, HOME/EXROM, cassette and guided keys. It explicitly requires passing HOME RAM before its SCLD and ROM tests. Preserve that dependency discipline and native TS2068 knowledge, but replace blanket RAM gating with tested-block permissions and avoid its overly definite “replace the chip” conclusions. [S3]

ZX diagnostics use an initial ROM integrity check, lower-RAM tests before a stack, per-bit border reporting and later workspace-based tests. The supplied first screenshot demonstrates partially readable RAM-failure text plus stripes; the second shows a normal result display. Those are useful UI precedents, but their Spectrum IC numbers, 1-bit DRAMs, PAL timing, paging ports, and model detection do not transfer to the TS2068. The downloaded upstream `testroutines.asm` includes stack-based upper-RAM operations; do not adopt them in the register-only TS2068 stage. The supplied v0.37 binary is 16384 bytes, SHA256 `e38354b6b8f393a65a2512cb622c6f255a4d015e9022244a873f0c6c2b0cf464`; newer upstream source is comparative evidence, not asserted to be the exact source of that binary. [S4]

## Banking and overnight stress

The optional [PicoVideo profile](PICOVIDEO_TEST_PROFILE.md) defines separate palette/CLUT, native-mode reproduction, display-write capture and bounded recovery tests. It remains disabled in stock runs, with board/firmware-specific capability gating. External output results do not replace native SCLD results.

Add separate BANKING STRESS and OVERNIGHT SOAK menu entries. [BANKING_AND_OVERNIGHT_TESTS.md](BANKING_AND_OVERNIGHT_TESTS.md) defines rapid HOME/DOCK alternation, immediate-read timing sweeps, verified execution transfers, a published-Sinistar startup profile, interrupt/mixed-load banking, and interruptible RAM-only/banking-only/combined overnight runs. Keep the first failure latched, retest all RAM including workspace, and fall back to register-only reporting if workspace fails. The normal soak dashboard provides stable elapsed/progress/error fields and pause/stop/alarm controls; display-RAM testing temporarily uses border/beeper status so screen memory is not exempted.

## Implementation and acceptance

1. Implement the low/high ROM kernels, header, register-only reporting and all-48K basic tests. Produce assembly, labels, reproducible DCK/BIN packing and hashes. Validate the native launch limitation explicitly.
2. Add permitted workspace blocks, chip/bit fault details and complete destructive tests including workspace retest. No video dependency is introduced into the error path.
3. Add HOME CRC, controlled HSR tests, verified EXROM gateway and interrupt checks with bounded recovery.
4. Add generated video cards, the physical keyboard UI, AY/beeper/cassette/joystick modules and soak controls.
5. Inject faults in a TS2068 emulator: every RAM data bit in every region; stuck-high/low and intermittent errors; address aliases including 8K/16K boundaries; absent/stuck mapping bits; bad readback; missing interrupts; ROM corruption; stuck keyboard rows/columns; AY aliases; workspace corruption. Confirm that unsupported prerequisites produce NOT RUN and that tests still examine every HOME byte.
6. Validate physical machines and cartridge hardware: cold start/reset, map transitions, sound and video modes, power/timing effects, and reference-designator consistency. Use controlled fault injection on service fixtures rather than assuming an emulator models refresh, bus contention or analog output correctly.

Acceptance requires no implicit stack use before RAM qualification; no normal-ROM calls; no active PC/SP/vector hidden by any successful transition; no unbounded polling; no unscheduled writes to external devices; no permanent untested RAM exclusions; correct physical chip/bit attribution; and continued reporting when screen RAM is corrupt. Run-time timeout cannot protect against a CPU that stops clocking, so record that physical limit in the operator instructions.

Future PicoCartridge integration supplies independent reset capture, ROM anchors, known SRAM, LEDs, buttons and telemetry. Keep those as capability flags in the same test scheduler. Add expansion modules later with an explicit peripheral profile and setup step; do not probe arbitrary ports or auto-enable TS Pico, PicoVideo, Interface 1 or Twister-connected devices during stock tests.

### Design decisions needing bench evidence

Confirm the exact target board's LROS discovery/handoff; actual ROM-only capacity/chunk decoding; no-reset and reset behavior; precise U10/U11 row/column multiplexing and A7R behavior against fitted DRAM datasheets; normal port-readback and decode behavior; interrupt count tolerance and nominal delay calibration; degraded text under U6/U7 faults; and the EXROM gateway under repeated long-term tests. These do not change the chip-to-byte/bit mapping established above, but they govern timing and fault-localization confidence.

## Maintaining test coverage

[TEST_CATALOG.md](TEST_CATALOG.md) tracks stable test IDs, methods, prerequisites, recovery and implementation/validation status. Its canonical source is [test-registry.json](test-registry.json); update that registry and run `python scripts/build_test_catalog.py` when changing a test. [PROJECT_STATE.md](PROJECT_STATE.md) records handoff decisions and outstanding work, while [TEST_IMPLEMENTATION_TEMPLATE.md](TEST_IMPLEMENTATION_TEMPLATE.md) defines the register/mapping/algorithm/evidence record required for future firmware implementations. Keep host pattern generation separate from executable target diagnostics.

## Deliverables included with this design

`scripts/generate_design_assets.py` reproducibly generates eight packed target planes, idealized decoded previews and SHA256 records under `assets/video/`. The overview is `assets/video/testcard-overview.png`. The generator checks address-map coverage, exact plane lengths, hires byte-group interleave, ECM palette and FLASH constraints, and the reference ROM identities. `docs/rom-identities.json` records the measured source-file checksums. These video assets remain future integration inputs. `scripts/build_cartridge.py` now builds the separate v0.1 RAM-kernel milestone as `build/diagnostic-v01.dck` and `build/diagnostic-v01.bin`; it does not implement every test described here.

## Sources

- **S1:** Local `Timex 2068 Technical Manual.pdf`, 309 PDF pages, SHA256 `3253f371946016a17699f910efcc842ff5b716271ea9c0ddad00e6ef439c547d`. Relevant original PDF pages: 11–16 overview/startup; 28 ROM/RAM; 29–44 AY/joysticks; 45–54 SCLD/banking/timing; 55–56 keyboard/display; 59–62 ports; 68–71 J4; §5.2 advanced video. Original PDF page numbers differ from the library's reconstructed edition.
- **S2:** Local `TimexSinclair-2068-schematic.webp`, drawing `335-B70500`, dated FEB 84. RAM nibble labels, CAS connections, U3/U5/U9/U10/U11 paths, U14/U16/U19/U20, and CR6–CR13 keyboard diodes were visually inspected. The schematic says W1/W2 installed and W3/W4 unused for this board revision.
- **S3:** Local `DiagnosticCartRefInfo.txt` and `Carl2_06242021.pdf`, PDF pp10–13, Carl A. Miles ART 1.0 operation manual (1985). Other supplied Carl scans contain related programming material.
- **S4:** Supplied `SpectrumZXDiagnosticROM/testrom.bin`, screenshots `spectrumdiag1.png` and `spectrumdiag2.png`; [ZX diagnostics firmware manual](https://github.com/brendanalford/zx-diagnostics/wiki/Firmware); [upstream source](https://github.com/brendanalford/zx-diagnostics). Comparative source copies are in `tmp/research/zx-*.asm`. Respect upstream licensing if code is reused.
- **S5:** [MAME TS2068 ROM definitions](https://github.com/mamedev/mame/blob/master/src/mame/sinclair/timex.cpp), corroborated by local `TS2068_U16.BIN`, `TS2068_U20.BIN` and TSRun ROMs. Computed identities are retained in `rom-identities.json`.
- **S6:** [TS2068 cartridge development skill](D:/T7_Recover/Jon/Personal/Timex/AISkill_TS2068/skills/ts2068-cartridge-development/SKILL.md), its banking/header/validation references, and [David Anderson reference library](https://github.com/timex-sinclair-projects/TS2068-Ref-Library). Derived Markdown is navigation/supporting evidence; original manual and schematic govern contradictions.
- **S7:** [Zilog Z80 CPU user manual](https://www.zilog.com/docs/z80/z80cpu_um.pdf), refresh and HALT behavior.
- **S8:** Local `D:/T7_Recover/Jon/Personal/Timex/TSRun/keyboard.js` for 42-key physical layout/40-position matrix; `machine.js` for display-plane rendering cross-checks. Emulator behavior is not bench verification.

### Basic color-bar selection (VID-01)

Offer a simple solid color-bar screen before the detailed patterns: eight32-pixel bars ordered black, blue, red, magenta, green, cyan, yellow, white. Upper96 lines use BRIGHT=0; lower96 use BRIGHT=1. Use zero bitmap bytes and PAPER colors, with FLASH clear; each corresponding attribute differs only by D6. Black should remain unchanged. A separate bounded polling control should toggle BRIGHT without altering color fields, then restore mode0 on exit through ROM control. U7 carries attribute D6; a missing intensity change can also be SCLD decode or analog video, so report a suspect path rather than a chip verdict. The generated preview and planes are host assets only.

VID-01 color-bar halves now begin with16-pixel monochrome bands labeled `NORMAL BRIGHT=0` and `BRIGHT BRIGHT=1`, encoded in the target bitmap itself. Each half retains80 lines of solid bars. The label boundary remains visible if a video system omits extra brightness; `colorbar-no-bright.png` models that case. Report "no visible BRIGHT difference" as a visual observation, since output equipment can suppress it; compare native/external output before attributing a machine fault.

## Executable suite status

Version0.2 implements the stock-machine suite described in [actual implementation/operator record](tests/V02_DIAGNOSTIC_SUITE.md). Broader research algorithms remain targets where the registry marks partial/specified. Emulator acceptance is image-specific; physical validation remains pending.
