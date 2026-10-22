# CP/M 2.2 RAMDisk: TSPico implementation and Oliger interchange

The implementation is part of the cartridge, and works with unmodified original
TSPico 1.00. It does not install a new TSPico firmware. The reusable pieces are
the banked block-device driver, loader/export format, transport adaptation, and
host image tools in this source tree.

## Memory and I/O path

CP/M needs writable low memory and a contiguous transient program area. This
port maps 32KiB DOCK RAM at 0000–7FFF and keeps high HOME RAM for the OS, stack
and buffers, giving a TPA of 52,992 bytes (0100–CFFF). Standard TS2068 alone
does not supply this low writable mapping. TSPico SRAM does; a modified
PicoCartridge/PicoROM with appropriate RAM and bank selection could provide it.

CP/M requests a 128-byte sector. `src/sram_disk.asm` translates its linear
record number to an 8KiB page, selects the appropriate SRAM pair through
MEMDOCK, exposes the selected DOCK window through F4, copies the bytes and
restores the CP/M slot/mapping. A private HOME stack prevents a program stack
inside a switched window from disappearing during the operation.

SRAM pair 4/5 contains CP/M. Disk pairs are 0/1, 2/3, 6/7, 8/9, 10/11, 12/13.
Each pair contributes seven usable 8KiB windows; window 7 stays HOME for the
resident driver. The image uses twenty pages for 160KiB or forty for 320KiB.
The slot table and allocations are fixed; unused capacity is not another drive.

Preload data is received at HOME A000. That address overlaps one possible disk
bank window. For this case, installation/fetch uses a 128-byte resident bounce
buffer rather than video memory. Ordinary windows use direct copy/readback.
Each installed page is verified byte-for-byte. The optimized comparison costs
about 4.3 modeled CPU seconds over forty normal pages at 3.528MHz; TAP transport
and firmware guards account for additional time. Resident bank selection still
uses the link, so SRAM access does not mean zero transport overhead.

PicoVideo's older V4 capture code does not filter DOCK writes. It can display
disk/program bytes even while HOME screen RAM is intact. PicoVideo 4.2 tracks
F4 and ignores out-of-bank captures; it also implements the supported 80-column
renderer. See [PicoVideo](picovideo.md).

## Loader, save and failure behavior

`src/sram_loader.asm` validates the legacy/modern handshake and loads geometry,
checksummed data and any saved-state descriptor. Original firmware mounts small
factory TAP volumes because its tape buffer is limited. Saved exports reload
directly without a PC conversion. Directory discovery precedes optional legacy
LOAD probes, so an ambiguous error 05 cannot silently discard an existing disk.

`src/tpsave.asm` exports legacy chunks plus a completion/checksum descriptor, or
one multi-record TAP using modern APPEND. The original media remains a snapshot
until TPSAVE is explicitly run. Completion markers detect interrupted saves;
they do not provide atomic replacement or a second historical backup.

Failures retain protocol, stage, phase, token, page, command and reply diagnostics.
Timeouts do not trigger blind retries into a possibly misaligned FIFO. The
screen is cleared before the error report. Keep this information when filing
hardware reports; VIDEO and MEMTEST are optional transient tools, independent
of the boot failure report.

## Oliger/Fuse disk compatibility

| Geometry | Raw bytes | SRAM pages | CP/M allocation block |
|---|---:|---:|---:|
| 40 tracks, 1 side, 16 × 256-byte sectors | 163840 | 20 | 1024 bytes |
| 40 tracks, 2 sides, 16 × 256-byte sectors | 327680 | 40 | 2048 bytes |

`tools/oliger_image.py` handles the standard CPC DSK container used by this
Fuse/JLO setup. `tools/tspico_ram_image.py` wraps exactly those raw disk bytes
in TAP records or reloadable legacy sets. `tools/cpm_disk.py` edits the same
CP/M filesystem in DSK, TAP or raw containers. Single/double-sided metadata is
preserved; the loader chooses matching CP/M parameters. Fuse and browser
cartridges currently remain geometry-specific.

This is filesystem/image work-alike support, not a WD1770 port emulator for
arbitrary Oliger software on TSPico. Historical disks must match the supported
sector numbering, geometry and CP/M directory layout. Extended DSK and unrelated
Oliger/DOS filesystems are not accepted implicitly.

## Reuse and future extension boundaries

| Layer | Source |
|---|---|
| SRAM block I/O and bank safety | src/sram_disk.asm, src/disk_geometry.asm |
| Loader and explicit snapshot | src/sram_loader.asm, src/tpsave.asm |
| Legacy/modern cartridge transport | third_party/tspico-filelib, tools/dual_transport.py |
| Python image/container access | tools/oliger_image.py, tools/tspico_ram_image.py, tools/cpm_disk.py |
| Optional modern persistent service | firmware/cpm_service.py, cpm_dsk.py, cpm_tap.py, cpm_directory.py |
| Emulator sector adapter | web/tsrun/oliger.mjs |

A general TSPico RAMDisk utility can reuse these mechanisms, but must supply
its own resident memory map/API and avoid other applications' SRAM reservations.
Future multiple drives need per-drive geometry, bank allocation, mount identity,
dirty state and save destinations. Two 160KiB images are feasible within 320KiB,
but the present build exposes one A drive and does not implement that partition.
Full Oliger-controller compatibility would add a separate controller/ROM contract.
