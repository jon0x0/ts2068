# Storage backend contract

The CP/M BIOS jump table and its disk geometry/DMA handling live in bios.asm.
Only blockdev_ramdisk.asm knows about EXROM, F4 or FF. Replace that include with
a real hardware backend when ready; no CP/M or console changes are required
provided the backend satisfies this contract and geometry remains consistent.

`block_read` / `block_write`:

- C = zero-based drive number (currently only 0); HL = 128-byte logical LBA.
- On writes, B = CP/M BIOS write type: 0 normal, 1 directory, 2 unallocated.
- Transfer exactly 128 bytes through the BIOS-owned `bounce` buffer in common
  HOME memory above E600. Do not access CP/M DMA while alternate banks are mapped.
- Return A=0 success, nonzero failure. BC/DE/HL/flags may be destroyed.
- Interrupts are disabled. Code, stack and bounce must remain mapped throughout.
- Restore DOCK selection (FF bit 7 clear) and F4=0F before returning, preserving
  FF video/color bits. The default FF value is 3E; COLOR can change bits 3-5.
- Reject invalid drives and LBAs before changing mappings or writing data.

The BIOS validates track/sector and calculates LBA = track*16 + sector. Its
read/write glue copies between bounce and arbitrary CP/M DMA under the normal
mapping. Disk geometry is generated from config/ramdisk.json. The current drive
has 24 tracks, 16 sectors/track, 128 bytes/sector, 48 allocation blocks of 1KB,
64 directory entries (two reserved blocks), no reserved tracks and identity skew.
DPB: SPT=16, BSH=3, BLM=7, EXM=0, DSM=47, DRM=63, AL0=C0, AL1=0, CKS=0, OFF=0.

## Emulator RAM disk

Six initialized writable EXROM pages, **1–6**, form one 49,152-byte disk. LBA/64
selects the page; LBA%64 selects its sector. Page 0 is deliberately absent so
the original EXROM can perform cartridge startup. Page 7 is never switched:
BIOS, bounce and stack remain in HOME. Mapping page 6 temporarily hides CCP and
part of BDOS, but no instructions execute there during a transfer.

The transfer sets FF bit 7 and F4=1<<page, copies 128 bytes, then clears FF bit 7
and restores F4=0F. Color bits remain unchanged. Logical sectors do not straddle
bank boundaries. This does not consume
additional CP/M TPA. Cold cartridge reload recreates the disk; warm boot retains
it. No persistence is implied by an emulator reset.

## TSPico implementation

The combined cartridge now implements a model-tested modern TSPico image path,
with stock-channel read-only fallback and an optional binary-safe firmware
extension. See tspico.md for its exact interfaces and hardware limitations.
TPIMPORT reads individual ordinary SD files. The owner's preferred directory
backed CP/M drive still needs a filesystem bridge; it is not an alias for the
image backend described here.

### Future extensions

Keep the same logical image and BIOS glue. Implement block_read/write through
the owner's cartridge-safe TSPico protocol, using an SD image or mapped SRAM.
Confirm that protocol routines do not need a BASIC-ROM workspace overwritten by
CP/M. Add bounded timeouts and return BIOS errors on failed commands. Keep the
common buffer and code accessible while switching memory. If a protocol transfers
512-byte sectors, translate LBA into sector=LBA/4 and subrecord=LBA%4. Use a
512-byte cache and read/modify/write for partial writes. The current BIOS-owned
buffer is only 128 bytes; reserve a larger cache explicitly in the memory map.

## Oliger implementation

`src/blockdev_oliger.asm` implements the JLO WD1770 ports with a 256-byte
read/modify/write buffer and synchronous single-sector commands. The `oliger`
profile uses a 160KB floppy and no EXROM RAM disk. See [Oliger setup](oliger.md)
for the exact geometry, generated DSK format, GUI instructions and test evidence.

The Oliger backend retains the unused 128-byte partner of a successful
256-byte physical read. Only the immediately following request for that exact
partner can hit, once. Repeated reads of the same half and intervening sectors
fetch fresh data. Writes always read/modify/write synchronously; there is no
deferred writeback. Initialization, HOME, warm boot, console input, invalid
requests and controller errors invalidate the pending partner.

Exhaustive sequential tests issue 640 rather than 1280 controller READ commands
on the 160KB image, and 1280 rather than 2560 on the 320KB image. This is a 50%
reduction for paired sequential records, not a claim that every game operation
runs twice as fast. Tests cover reverse pairs, repeated halves, interleaved
sectors, invalidation, synchronous writes, preserved half sectors, and CRC,
lost-data, missing-sector and write-protect errors. The existing 256-byte buffer
is reused; the TPA is unchanged.
