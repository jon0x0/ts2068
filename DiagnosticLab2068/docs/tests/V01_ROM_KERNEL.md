# Version 0.1 ROM kernel implementation

This is the first executable bring-up milestone. It implements full HOME RAM pattern/bit/March sweeps and a small healthy-machine menu, with stackless register-held failure reporting. It does not implement the remaining comprehensive tests, random/retention/soak options, cancellation during a sweep, bank-switch torture, runtime ROM checksums or the full menu. Physical TS2068/TSPico validation is pending.

## Build and artifacts

Run `python scripts/build_cartridge.py`. The default assembler is the sibling Sinistar project's SjASMPlus 1.20.3 executable; `--assembler PATH` overrides it. No sibling project is modified. Pillow is not required for the cartridge build. The immutable font comes from the locally verified stock U16 character table; its hash is recorded in the manifest.

- `build/diagnostic-v01.dck`: sparse DOCK ROM chunks 0, 1 and 4, 24,585 bytes.
- `build/diagnostic-v01.bin`: exact contiguous 65,536-byte physical image, unused areas FF-filled.
- `build/manifest.json`: hashes, descriptors and stable phase meanings.
- `build/symbols.txt`: actual assembled entry/phase/report symbols.
- `src/diagnostic.asm`: authored entry, control, compare, menu and report code.
- `scripts/build_cartridge.py::ram_source`: authored algorithm expansion; emitted as `build/ram-tests.asm`.

Current programmer images require hardware capable of decoding ROM chunks 0, 1 and 4 at their fixed addresses. This is a native LROS image, not a reset-vector replacement. Do not burn it into HOME U16 and expect native cartridge semantics. Preserve the passive startup limitation.

## Memory and control contract

LROS header: `00 01 00 01 EE` at DOCK0000, entry0100. Header declares chunks0/4 and leaves chunk3 HOME for OS transfer. Entry immediately executes DI, DECR40 and HSR01. All HOME4000-FFFF becomes writable/testable. Interrupts remain disabled throughout this build.

| Phase | HSR | CPU instructions | HOME access |
|---|---|---|---|
| Native handoff | OS selects declared chunks0/4 | entry0100 | OS handoff dependency exists before entry |
| RAM tests and reporter | 01 | DOCK0 | Every HOME RAM address is exercised; no HOME control state |
| Menu copy | 03 | DOCK0 | ROM1 menu copies to HOME4000-5AFF |
| Menu input | 01 | DOCK0 | Direct keyboard I/O; no RAM state or stack |
| Separate high-anchor entry | 11 then low entry resets01 | DOCK4 then DOCK0 | Stub only; no HOME ROM checksum implementation yet |

SP is never changed or dereferenced after entry. The safety audit rejects CALL, RET variants, PUSH, POP, RST, HALT and EI in the authored/generated kernel. No diagnostic system-ROM routine is called. IY is assigned fixed ROM continuation labels and used by `JP (IY)`. RAM is never used to choose code addresses. There is no writable cartridge RAM.

Main HL is the tested address; D expected byte; B observed byte; E comparison scratch. I is the current phase ID. IX latches the first failing address. Alternate H/L/D accumulate XOR error bits for regions4000/8000/C000; alternate E latches the first failing phase; alternate B/C latch expected/observed bytes. Alternate AF stores menu selection only. Reporter routines preserve IX and all alternate fault registers.

## Exact algorithms

The default scan has 30 phases. Phases1-8 each fill all4000-FFFF, then compare the whole range: 00, FF, 55, AA, 0F, F0, 33, CC. Phases9-24 walk a single one then its complement through each bit, writing/comparing every byte immediately. These supplement full patterns; they do not establish exhaustive coupling or address-alias coverage.

Phases25-30 implement March C minus: ascending w00; ascending r00/wFF; ascending rFF/w00; descending r00/wFF; descending rFF/w00; ascending r00. Ascending loops stop only after FFFF wraps to0000. Descending loops include4000 and stop after decrement to3FFF. No HOME byte is excluded for workspace, font or display.

`compare_byte` computes expected XOR observed, ORs it into the physical region's union, and latches the first failing address/phase/expected/observed only once. It jumps to its fixed IY continuation even on failure, so every phase completes and other regions remain tested. The current build uses no target-controlled count or pointer.

All-chip failure and address aliases are not yet classified separately. An error names the affected nibble path; it is not a component replacement verdict. Future RAM-02 address-alias and RAM-06 random tests remain essential before claiming broader RAM qualification.

## Menu and fault output

After a zero-error sweep, immutable ROM1 screen data draws a 32-column menu. Key1 repeats the complete suite; key2 performs full patterns and walking bits; key3 performs March only. Menu input polls the numeric half-row directly. The menu loop is intentional idle waiting, not a test waiting for an unavailable peripheral. A held key may repeat a suite when it completes; release the key after selection.

Any nonzero region mask bypasses the menu and enters ROM-only reporting, including when the fault is in video RAM. A long white-border synchronization tone precedes red-border pulse groups: class2, chip index, detail. Chip indices1-6 mean U6,U7,U12,U13,U17,U18. Details1-4 mean local nibble bits0-3; detail5 means several affected bits. Every affected nibble is reported in order, repeating continuously. R restarts a full scan at the end of a complete reporting cycle. Delays and tones are nominal instruction-based timing; physical calibration remains pending. This slower bring-up cadence does not yet match the design's final 150ms pulse target.

The first entry marker is blue border; no entry beep or cartridge self-check is implemented yet. During RAM phases the border is yellow, then black before the menu. The first sweep takes roughly33 seconds of modeled CPU time without injected faults, plus native OS startup. There is no mid-sweep keyboard cancellation in v0.1; each phase is bounded. Do not advertise this build as an overnight runner.

## Evidence

`scripts/verify_cartridge.mjs` executes the assembled image using the sibling TSRun machine/Z80 modules and stock HOME/EXROM ROMs. `build/verification.json` records exact image and engine hashes plus 30 cases: healthy native LROS/direct entry; each of eight stuck-low data bits in each of three regions; one-read transient C123/D5; lost write8123/D2; and both menu-specific reruns. Checks cover every HOME address, ROM-only opcode fetches, unchanged SP, disabled interrupts, retained first transient evidence and continued FE speaker pulses. Faults are armed **after cartridge entry**, because passive OS launch under faulty RAM is not guaranteed.

`scripts/verify_reporter.mjs` seeds register fault state and checks all24 chip/nibble-bit mappings, white synchronization output and preserved first-fault registers. `build/reporter-verification.json` records those results.

`scripts/check_fuse.py` runs Fuse1.7.0 with explicit stock TS2068 ROM paths. `build/fuse-checkpoint.log` records menu PC04CD, SP61FE and frame0841 in the tested build. `build/fuse-result.json` binds the checkpoint to the image. An initial check using Fuse's default TC2068 ROM configuration timed out; the explicit stock configuration succeeds. The check rejects debugger errors. Removing the trailing newline from the debugger command avoids an empty-command syntax error observed in this Fuse build.

`build/dck-inspection.json` validates descriptors and native LROS header. `build/menu-screen.bin` is captured TSRun display RAM; `build/menu-screen.png` is its decoded preview using an illustrative RGB palette. These do not certify analog output or physical timing/refresh behavior.

## Modification and acceptance limits

Keep continuation addresses fixed in ROM and do not reuse alternate result registers without changing the register contract and tests. Menu assets reside in ROM1; copying them must retain DOCK0 and expose HOME2. Add test phases through the authored generator and update phase records/operator documentation together. Do not enable interrupts or introduce CALL-based font code into this kernel.

The initial tests detect the injected fault classes but do not promise all RAM faults or corrupt active-ROM recovery. Missing CPU clock, bad opcode fetch, lost active mapping and pre-entry OS failures remain limits. The next milestone should add address-derived/alias and random coverage, runtime ROM integrity, safe bounded cancellation and richer results while preserving this register-only control path.

## Historical version note

The active src/diagnostic.asm is now v0.2. Rebuild this historical kernel with scripts/build_v01.py using src/archive/diagnostic-v01.asm before using the old verifier scripts; those scripts need the matching build symbols. Earlier Fuse records used address-only breakpoints. Current v0.2 validation additionally confirms cartridge mapping to exclude HOME-ROM PC collisions.
