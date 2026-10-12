# TSPico diagnostic integration: evidence and proposed tests

Release v0.2 | October 12, 2026

Status: reference research and image-format compatibility checks only. No TSPico SRAM test or physical-cartridge coexistence mode is enabled in current firmware. The stock diagnostic remains ROM-only, with no speculative external-port probes.

## Inspected profile

Local sources: `../TSPico/TS-Pico-1_1.20260717/src/TS/tspico.py`, `src/config.ini`, `firmware_v_1_1c.uf2`, the supplied TS Pico Manual12-03-23.pdf, and the Altium-export Memory/Logic/ts2068Interface sheets. Directory/version labels describe the inspected snapshot, not the user's installed firmware. The MicroPython source imports lower-level `tspico_io` PIO programs; their exact implementation is not present in this source snapshot and has not been reverse engineered from UF2.

The manual and [project site](https://ts-pico.com/) describe512K SRAM plus512K Flash. The exported Memory sheet identifies SRAM as U13 AS6C4008-55PCN and Flash as U10 SST39SF040-70. These are TSPico board reference designators, distinct from HOME DRAM chips. A reported SRAM mismatch implicates its address/data/select path as well as U13; it does not prove that IC alone is defective.

The v1.1 MicroPython command dispatch supports `SAVE "tpi:getinfo"` and `SAVE "tpi:gethelp"`. GETINFO prints firmware and board revision, but this snapshot hardcodesFW Rev1.1/uPython1.22.0/Board RevV2.2, so the text cannot identify the exact build or letter suffix. Do not upgrade firmware just to determine its version.

## Virtual cartridge loading

DCK_IMAGE at source line259 expands a DOCK bank0 image to64K. It accepts descriptors0/2 and rejects other descriptors. Each ROM descriptor2 consumes8192 bytes; missing chunks are zero-filled in this implementation. Our diagnostic uses eight descriptor2 chunks, so no padding or writable descriptor is needed and its expansion is identical to the raw PicoROM payload. The current host image-format check executes this isolated published conversion function with in-memory files and confirms equality. It does not exercise the actual loading TAP, flash/SRAM writes, PIO timing or physical startup.

Source loading routes `.dck` through `/TS/dckupdate.tap`; transfer code sends the expanded image in two32768-byte blocks. Follow the installed version's documented loader workflow; no unverified flash-update command is prescribed here. A virtual diagnostic loaded into writable SRAM is not automatically ROM-protected: existing banking tests deliberately attempt writes to chunk signatures. The backing-memory and write-protection behavior must be established before interpreting such a failure as a TS2068 fault. Keep a reloadable copy of the DCK image.

## Additional slot mapping

MEMDOCK at line1376 accepts MEM1..3 and PAGE0..15, updates ROM_SM bits2..3 and the high nibble of bank_sm, and sends both values to the ROM/BANK PIO state machines. MEMBOOT separately controls their low fields and may persist configuration. ROM_SM default10 is described as Flash for both boot and DOCK. The source does not establish every MEM value's electrical meaning or prove that all16 PAGE values correspond to independent64K RAM banks.

In fact512KiB cannot contain sixteen independent64KiB windows. The schematic has A15_B/A15_I and A16-A18 nets; their gate-level relationship and the PIO selection rules must be resolved before defining slot stride, overlap or reserved areas. Tests must first establish aliasing between slots with distinct signatures. Ordinary TS2068 HSR selection chooses fixed8K HOME/DOCK windows; TSPico's additional slot selection is a separate operation.

## Physical cartridge coexistence

The older supplied manual says to remove physical cartridges. The interface sheet exposes /ROSCS and /BE_IN, /BE_DRV, /BE_OUT, and v1.1 enables a `set_ctrl` state machine for both DCK and ROM mapping. These are evidence of arbitration requirements, not proof of a supported cartridge-disable/bypass command. Confirm installed firmware, actual /BE behavior, TSPico memory output enables and physical DOCK /CE before combining devices. Disabling a software feature alone does not prove the data bus is released.

Our executing code resides in DOCK chunk0. Changing TSPico's entire DOCK slot can replace that very opcode stream, even with HSR bit0 still set. A safe SRAM profile therefore needs a separately decoded immutable ROM anchor, or an explicitly qualified HOME gateway whose complete mapping/recovery contract is verified. The gateway would introduce a RAM-opcode exposure and must remain optional, excluded from startup/Full/overnight HOME tests. A physical cartridge enabled for all eight chunks and TSPico SRAM must not drive the same selected addresses simultaneously. Retaining a physical ROM anchor while mapping external RAM elsewhere requires verified selective arbitration, not merely changing HSR.

## Proposed opt-in SRAM test

1. Operator selects an exact board/firmware profile and a sacrificial RAM range, after confirming mapping and execution anchor. No writes to Flash or configuration storage.
2. Qualify read/write/restore behavior for one window with00/FF/55/AA and walking bits; report physical slot, logical address, expected/observed and XOR mask.
3. Write unique slot signatures; revisit every candidate slot to detect overlap, wrapping and mistaken SRAM/Flash selection. Derive physical offsets only from the verified stride.
4. Run March C-, address-derived and seeded-random tests across confirmed writable SRAM, with bounded mapping/response waits and first-fault capture. Preserve the ROM image, loading/runtime data and active gateway.
5. Offer a separate retention/thermal soak with pass counts and guarded key cancellation; restore mapping and verify the executing anchor after each batch.

This SRAM test supplements HOME DRAM tests. Its static RAM has different refresh behavior and cannot qualify the TS2068's internal DRAM or native display fetch path. Cartridge/TSPico/SCLD/bus faults can affect both independently tested memories. Record exact image, firmware, installed hardware and physical evidence before promoting this profile to executable support.

Credit: TS Pico development team and [TS-Pico project](https://github.com/timex-sinclair-projects/TS-Pico), original Timex documentation, PicoROM contributors, and the local PicoCartridge2068 reference extraction. No TSPico firmware is bundled into this cartridge.

## User-reported configuration and development builds

On2026-10-12 the user reported GETINFO labels: FW Rev1.00, uPython1.20.0, Default ROM version1.00, Board version2.2. The user also states that displayed firmware numbers may not have been updated. Treat these as observed strings only: neither the effective firmware build nor its controller behavior is identified by them. The inspected v1.1 reference snapshot is a separate source, not a match inferred from the display. The current format check does not establish compatibility with the user's installed loading/controller code.

Future test eligibility must use capability profiles rather than a whitelist of release numbers. Developmental firmware is explicitly allowed when the selected profile declares the relevant protocol, memory type/stride, reserved ranges, write-protection semantics, immutable execution anchor and recovery mapping. Unknown or stale labels must not cause a supported capability to be rejected, nor cause an unverified capability to be enabled. Core cartridge tests remain usable to the extent that the installed interface supplies the documented ROM/mapping behavior; this is not a guarantee for arbitrary firmware that removes opcode visibility.

Record source revision and UF2/binary hashes when available, along with observed mapping behavior; all are useful provenance, not substitutes for hardware checks. A developer can supply a profile independently of the banner version. A future capability handshake must be explicitly specified and selected before use; do not invent a discovery port or blindly issue writes looking for it. Treat any returned counts/addresses as untrusted data: clamp to independently verified limits, require a declared sacrificial range, and stop/skips on an unsupported operation or bounded response failure. A claimed capability must still pass narrow read/write/isolation/recovery qualification before destructive extended coverage.

Keep virtual-DCK conformance testing separate from SRAM testing. If a development image intentionally makes DOCK writable, the current ROM-write-protection comparison can fail for that reason; report interface/profile mismatch rather than blaming TS2068 hardware. Likewise a changed physical-cartridge arbitration policy needs its own tested contract. No version label permits a routine to switch away its running code or drive overlapping memories. Hardware-dependent failures which defeat opcode fetch remain externally diagnosable limits.

`docs/tspico-user-profile.json` records the user's observed labels with unverified capabilities. This is documentation for future implementation, not a runtime configuration consumed by the cartridge. External SRAM tests remain specified only.
