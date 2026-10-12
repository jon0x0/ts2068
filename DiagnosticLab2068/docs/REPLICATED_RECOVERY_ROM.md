# Address-fault survival: feasibility and current limits

This is a future design assessment, not implemented recovery firmware. Current default startup adds ROM0 register/arithmetic/shift checks before cartridge integrity, then uniform00/FF HOME RAM and qualified55/AA address pairs. See BOOT_PATH_DIAGNOSTICS.md. Optional menu9/U tests instruction consistency and16 localized HOME address pairs. Neither guarantees a report for a global CPU address/data fault.

## Why55/AA helps and what it misses

00/FF detects many stuck-at data faults.55/AA puts adjacent bits at opposite levels and can expose some coupled or bridged data paths that pass00/FF. The complete RAM suite already includes these patterns plus walking bits, March and address-dependent data. Uniform55/AA fills still assign the same byte to two aliased addresses, so a pure alias can pass. Distinct pair values or address-dependent contents are necessary. Any shortened startup expansion should be explicit about its time cost and retain ROM-only reporting and an any-new-key stop boundary.

## What replication actually requires

For one stuck address bit k, define the physical read mapping f(a)=a AND NOT(1<<k) for stuck-low or f(a)=a OR(1<<k) for stuck-high. A candidate program must fetch the intended byte at f(a) for every opcode and operand it uses, and preserve behavior for data reads, branch targets and I/O. Identical complete short programs on both sides of a high-bit boundary can satisfy the ROM-byte condition when their logical control flow is deliberately constrained. Matching entry points alone does not.

For A0, pairs of consecutive bytes collapse to one physical byte; A1 collapses corresponding positions in adjacent two-byte blocks. Ordinary instruction streams cannot simply be duplicated into these equivalence classes without conflicting opcode/operand requirements. Supporting several unknown failed lines simultaneously can force most of the image into equal-byte classes, destroying a useful general diagnostic. Bit-specific recovery images or carefully proved special instruction streams are more plausible than promising one universal ROM.

Current ROM0 has a native five-byte LROS header at0000, entry0100, IRQ0038 and NMI0066. If A8 is stuck low, logical0100 fetches physical0000: the header is not a recovery entry. The current packed64K image and independently selected8K chunks are intentionally distinct. Replication cannot be overlaid onto them without a redesigned launch/decode contract and fresh verification.

## ROM-only cartridge versus independent boot

A passive cartridge is discovered by HOME firmware; global address faults can break that discovery before cartridge instructions execute. A13–A15 faults may also change HOME/DOCK chunk decode rather than merely select a duplicate EPROM page. Address faults can alter port qualification; even surviving code may fail to reach FE border/beeper. Separate an EPROM-local address fault from a CPU/global-board fault in testing. Z80 software sees the consequences of a read mapping, not a guaranteed identity of the defective physical pin.

An independent reset/boot mapping and external status channel are more promising for a PicoCartridge fixture. A second-stage replicated stub could provide a recognizable bounded heartbeat and selected bus tests even when rich UI and HOME are unavailable. That needs a verified schematic/decode profile; stock PicoROM by itself does not provide that contract.

## Acceptance plan before shipping such a layout

1. Allocate a dedicated recovery image/profile and state exactly which single-line stuck-low/high faults it supports, where the faults lie and which boot assumptions remain.
2. Prove opcode, operand and branch equivalence for each candidate mapping; do not use corruptible target data as a control-flow pointer.
3. Inject faults into all bus reads/writes and port decode, separately from RAM-only aliases. Exercise real reset/bootstrap, not just direct entry into the recovery stub.
4. Verify the expected heartbeat/code or bounded inability to report, document exclusions, and bench-test with a controlled fixture before claiming physical survival.

Source: Timex original technical manual/schematic and [Zilog Z80 CPU User Manual](https://www.zilog.com/docs/z80/z80cpu_um.pdf), which define the fetch, addressing and I/O behavior. Replication feasibility above is a project inference from those contracts, not a Zilog fault-tolerance guarantee.
