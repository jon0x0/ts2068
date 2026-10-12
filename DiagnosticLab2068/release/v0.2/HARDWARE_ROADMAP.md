# Future hardware-assisted diagnostics

Release v0.2 | October 12, 2026

Current firmware remains ROM-only. These are design candidates, not supported capabilities or implemented tests. Select an explicit board/firmware profile; do not infer attached hardware by probing arbitrary ports.

## Capabilities and dependencies

| Candidate | Diagnostic value | Required implementation/evidence |
|---|---|---|
| Independent status and latched results | USB/LED reporting survives bad HOME RAM, missing video and a stopped Z80 | MCU-held phase, expected/observed data, masks, first failure and heartbeat; reporting channel independent of SCLD; session identity and explicit result-clear control |
| Passive bus observation | Distinguish absent fetches, missed mapping transitions and unexpected reads from firmware-reported RAM errors | Actual connected address/data/control signals, correctly timed sampling, finite trace buffer and overflow indication; electrical/timing validation |
| CPU-visible replacement RAM | Trusted workspace, stack, gateways and controlled substitution of a suspect region | Write-cycle capture, writable storage, output direction control and deterministic timing; exclusive memory decode and proof HOME drivers are disabled |
| Independent reset boot | Run before HOME ROM initialization and its RAM dependencies | Independently decoded ROM and correctly timed /BE/control arrangement verified against the schematic; readiness/reset coordination |
| Watchdog and triggered capture | Preserve last phase/trace when a test stops progressing | External heartbeat deadline appropriate to each test, capture before intervention, optional bounded reset/NMI policy |
| NMI button or controlled NMI | Manual cancellation or technician event during a qualified test | Reachable $0066 vector, stack-write safety, mapping ownership and compatibility with attached monitor firmware |
| Controlled fault injection | Verify the diagnostic's recovery/reporting, not merely its happy path | Explicit lab mode, narrowly decoded read/write faults, deterministic seed and complete capture; disabled in normal diagnostics |

## Standard PicoROM versus cartridge-specific hardware

The inspected standard PicoROM is a ROM emulator: its internal RAM stores ROM contents, which does not make it writable Z80 RAM. Its documented controllable tri-state reset output can potentially be repurposed, but routing it to NMI requires verified wiring, suitable electrical behavior and a defined pulse protocol. Do not assume stock firmware observes HOME RAM reads/writes, has all bus signals, or can inject NMI through an ordinary ROM socket.

The inspected PicoCartridge2068 revision-1 interface notes expose additional signals for future development but explicitly do not use /WRB for ROM emulation. RAM emulation needs a separate implementation and hardware timing review. Record which signals are actually connected to MCU inputs rather than merely exposed at headers. An NMI feature may require an expansion-bus connection or added wire; verify the cartridge connector rather than assuming NMI is available there.

Memory substitution and passive observation are separate modes. Never drive data while observing HOME reads. Cartridge RAM selected through HSR can provide CPU workspace, but continues to depend on working SCLD banking. Independent decoding is a separate hardware feature. CPU-visible replacement RAM alone does not replace the internal DRAM data path used by SCLD video fetches; ordinary DOCK screen overlays cannot be advertised as a repaired native display. Independent USB/LED reporting or a separately supported video device can avoid that dependency.

## NMI contract and proposed TSPico interaction

Z80 NMI is accepted independently of DI, decrements SP and writes the interrupted PC before fetching $0066. A handler can abandon that return address and jump to a ROM recovery checkpoint without RETN, but this does not undo the two automatic writes. Unqualified HOME stack addresses, write strobes or mapping can still be problematic. A cartridge-controlled RAM stack is useful only when its mapping remains guaranteed throughout the interruption. DI is not an NMI lock.

Reserve a ROM NMI vector only when the profile guarantees it remains visible through the selected test. A TSPico monitor can have its own vector/mapping behavior; verify installed firmware and arbitration before taking ownership. No blanket promise to recover from an arbitrary bank-switch failure or dead CPU.

For a user-selected, verified TSPico profile, offer a menu item such as **NMI button check** and prompt **Press the TSPico NMI button once**. Use a bounded wait with keyboard cancellation; missing response is reported as not observed, not proof the button is defective. The first implementation should use a stable map and qualified write sink, a minimal ROM handler that records the event and restarts a known menu checkpoint, and no return to arbitrary interrupted code. Button bounce/repeated edges must not cause uncontrolled nested handling. Preserve ordinary keyboard stop and existing fault pulses.

An overnight-test NMI stop comes later, after every phase has a documented vector/stack/mapping contract. Preserve first failure outside the interrupted register state where hardware permits. With ROM-only firmware, do not enable this during destructive RAM sweeps merely because the button is present. The existing v0.1 has no NMI recovery feature; users must not treat its button as a safe stop control.

## Implementation sequence and acceptance

1. Inventory exact board revision, connected signals and installed firmware; define read-only capability metadata and explicit operator selection.
2. Add independent status/result capture, then passive bounded trace and heartbeat. Keep baseline ROM diagnostics operational without the helper.
3. Validate cartridge RAM read/write timing, isolation and mapping before using it for workspace or gateways. Compare HOME with substitution and retain shared-path attribution limits.
4. Add a stable-map NMI/button test; validate wrong/unavailable vector, repeated edges, missing button, failed stack sink and absent keyboard paths in emulator and hardware.
5. Add independent boot and watchdog intervention only after electrical ownership and safe recovery states are established.

New executable modules need stable test IDs, register/mapping contracts and image-bound validation in the canonical registry. This roadmap deliberately does not mark proposed hardware features implemented.

## Sources and credits

- TS2068 original technical manual and supplied schematic: HOME/DOCK mapping, video paths and connector/control signals; primary project sources S1/S2.
- Zilog Z80 CPU User Manual: NMI entry, $0066 vector and automatic stack writes; verify fitted CPU behavior and timing before hardware implementation.
- [PicoROM by wickerwaka](https://github.com/wickerwaka/PicoROM), inspected local `../PicoROM-main/README.md`: ROM-emulation operation and reset output. Local snapshot, not a claim about every release.
- Local PicoCartridge2068 `docs/interface-crosswalk.md` and revision-1 architecture/electrical notes: proposed board signal availability and future RAM constraints; not physical validation.
- Local TSPico Altium interface export `tsPico2_2Altium/ts2068Interface-SchDoc/Root Entry/FileHeader.dat.txt`: /NMI and NMI Switch labels. User confirms an NMI button; installed monitor behavior remains unverified.
- [Timex Sinclair Team Projects](https://github.com/timex-sinclair-projects): TS-Pico overview documents programmable SRAM/Flash. Capacity alone does not establish a safe diagnostic mapping or recovery protocol.

See [TSPico diagnostic profile](TSPICO_DIAGNOSTIC_PROFILE.md) for the inspected v1.1 MEMDOCK/GETINFO/DCK source, concrete arbitration and slot-alias constraints and proposed EXT-01 SRAM test. See [PicoROM loading](PICOROM_LOADING.md) for the now-generated physical payload. These format deliverables do not implement SRAM emulation/tests or shared cartridge arbitration.

## Future independent clock, execution and USB logs

User-requested on2026-10-12. A future Pico-based cartridge may measure CPU clock with the MCU oscillator as an external time reference, detect loss/drift/duty-cycle anomalies and correlate heat/load with failures. Verify access to the actual CPU clock through the correct connector or an added probe lead. P28's existing socket pins do not include a dedicated clock input. /M1 or read-enable pulse rates are instruction/bus activity, not a direct CPU-clock measurement. Define input buffering, sample/counter bandwidth, timebase calibration and error bounds before giving measured-frequency claims.

A compatible hardware/firmware profile could capture address/data/control events, classify opcode fetches with /M1 when connected, and compare observed accesses/checkpoints against the known diagnostic ROM. This can preserve the last activity when the Z80 stops, detect unexpected fetch bytes/paths and correlate bank transitions. Without /M1, PicoROM's ROM-read addresses do not uniquely distinguish opcode fetch from operand/data access. Bus observation alone cannot certify internal register/ALU state; firmware self-tests and reported results remain necessary. Verification should include instruction timing/branch context and expected interrupts, not merely matching an address list.

Record session/image hashes, build/hardware profile, timebase, step, first fault, mapping transitions, bounded trace windows and overflow/drop counts. Use a RAM ring buffer and explicit freeze/retrieve operations; later retrieve logs on another computer over USB. Local persistent storage is a future implementation choice, not currently present in this ROM-only cartridge. USB servicing, flash commits and SD writes must not delay deterministic ROM response. RP2040 flash/XIP stalls and buffer overflow require explicit architecture/timing validation; defer persistence until a safe service interval or use storage isolated from the ROM-serving path. Logging must be observable and recoverable, with a documented loss policy. This roadmap does not claim stock PicoROM/PicoCartridge or TSPico firmware already implements these features.

Future no-HOME-ROM boot must provide an independent reset decode/entry and verified /BE/data ownership before any native OS handoff. Today’s LROS header is not a tested reset boot vector. Embedded cartridge font data already avoids live HOME-font reads and can be reused; a separately built/validated reset-boot image and MCU-ready/reset timing are still required.
