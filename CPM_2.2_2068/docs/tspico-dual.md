# CP/M cartridge: automatic TSPico v1.00/v2.x protocol selection

For the BASIC launch commands, SD layout and loader choices, start with the
[TSPico startup steps](startup.md#physical-ts2068-with-tspico).
For exact version boundaries, read the [firmware/feature matrix](tspico-firmware.md).
Original 1.00 is the legacy target; the inspected TSPico v2.x interfaces are firmware
2.3.1 / ROM 2.3. Intermediate 1.1 releases are not a validated CP/M target.
The optional CP/M service, not the firmware version alone, supplies native
files/direct SD disks. [COLOR, HI and new software](using-cpm.md) use the same
CP/M commands on either supported storage path.

Load `CPM.DCK` into TSPico SRAM slot pair 4/5. This single cartridge supports
the legacy shared FIFO protocol (including the unmodified 1.00 target) and the
TSPico v2.x status-register protocol. It validates a handshake, not a version string.
Unknown responses stop with a load error; no TSPico v2.x SYNC is sent until the
TSPico v2.x ACK and MID status are verified. No firmware is installed by this package.

The startup screen reports 64 columns or detected PicoVideo 80 columns; see
[PicoVideo setup and limits](picovideo.md). It also names the protocol and
storage mode:

- Legacy: reload a saved chunk set directly, or use the supplied preload when
  no save exists. No host conversion is required to resume a session.
- TSPico v2.x, with the optional CP/M service: press **Enter** for persistent SD,
  **R** to copy the current service volume into **RAMDisk**, or **L** to reload
  a saved RAMDisk from `/CPM/SAVE`.
- TSPico v2.x, without a usable service: reload a saved RAMDisk or use preload TAPs,
  using the TSPico v2.x storage protocol for TAP and memory-selection operations.

RAMDisk uses TSPico's banked SRAM. It accepts a 160KB single-sided or 320KB
double-sided volume. The default supplied preload is 320KB. Loading the whole
volume takes time, but subsequent disk data transfers stay in SRAM; bank
selection still uses the Pico link. This is not a measured hardware speed claim.

**RAMDisk changes are temporary in either protocol. Run TPSAVE before power
off.** Startup explicitly displays this reminder. TPSAVE confirms before saving
under `/CPM/SAVE`. On the TSPico v2.x storage protocol it writes **one `CPMRAM.TAP`**, with
a metadata CODE record and twenty/forty 8KB CODE records appended inside it.
On the legacy protocol it writes `CPM00..19/39.TAP` plus `CPMSTATE.TAP`.
`TPSAVE SPLIT` selects that legacy-compatible set on either protocol.
The original SD image/native
directory is unchanged when a TSPico v2.x service volume is copied into RAMDisk.
Export is explicit; it is not an automatic writeback or an atomic disk save.

The loader reads either save format directly. New chunk sets carry geometry,
a completion marker and Fletcher-16 page checksums. The marker is invalidated
before replacing any page and completed only after all writes succeed. Missing,
incomplete or mismatched pages stop boot instead of silently loading the factory
disk. Existing older exports without a descriptor also load directly: choose
1=160KB or 2=320KB on the TS2068. If both a saved TAP and a chunk set exist on
TSPico v2.x firmware, the loader asks T=TAP or C=chunks so it does not guess which
save you intended. Preserve previous saves separately before replacing them.

The cartridge currently exposes **A:** only. Additional drive letters and
multiple simultaneous SD/RAMDisk volumes are future work.

`FORMAT A:` initializes the mounted disk (retaining TPSAVE.COM in RAMDisk).
Python `tools/cpm_disk.py` creates new DSK/TAP/raw disks and copies files into
them. See [disk tools](disk-tools.md) for commands and limits.

## Card contents

Preserve existing card contents before merging the package's TAP directory:

```text
/TAP/CPM/CPM.DCK
/TAP/CPM/CPM32000.TAP ... CPM32007.TAP
/TAP/CPM/SAVE/
/TAP/CPM/FILES/ ... utilities, games, CPMDISK.COM, TPSAVE.COM
/TAP/CPM/CPM160.DSK
/TAP/CPM/CPM160.TAP
/TAP/CPM/COMPAT.TAP
```

Fixed preload names are retained for both sizes: a 160KB preload uses only
CPM32000.TAP through CPM32003.TAP. Geometry comes from metadata.

For TSPico v2.x persistent SD access, install/merge the optional four CP/M service
modules and command table on an already compatible newer firmware, as described
in [directory setup](tspico-directory.md). The included config defaults to native
`/CPM/FILES`. Alternatively configure a 160KB/320KB DSK or TAP as the service's
startup volume. Selecting R snapshots whichever volume the service supplies.

The supplied native FILES includes TPSAVE.COM so the RAMDisk snapshot can be
exported. When using your own disk image, put TPSAVE.COM from this package on
it **before** selecting R. CPMDISK refuses to switch SD media while in RAMDisk
mode; restart to choose another source. Keep CPMDISK.COM on mounted SD images
to switch back without restarting.

In persistent SD mode, use `CPMDISK MOUNT NAME.DSK` or `NAME.TAP`,
`CPMDISK SAVE NEWNAME.DSK` or `NEWNAME.TAP`, and `CPMDISK DIR`. Both 160KB and
320KB containers are supported with their appropriate CP/M parameters.
TPSAVE is a RAMDisk utility, not an SD-drive export command.

## Convert a disk or recover a RAMDisk export

Conversion is optional for archival or Fuse use, **not a reload prerequisite**.
With the optional TSPico v2.x service, conversion of a saved single TAP to DSK can
also run on the TS2068 in persistent SD mode:

```text
CPMDISK MOUNT SAVE/CPMRAM.TAP
CPMDISK SAVE SAVE/CPMRAM.DSK
```

Copy that DSK to the PC and insert it in the matching Oliger/JLO drive in Fuse.
Use the separate Oliger cartridge, not the TSPico cartridge. On the host:

```text
python tools/tspico_ram_image.py --dsk disk160.dsk --output disk160.tap --volumes preload160
python tools/tspico_ram_image.py --tap CPMRAM.TAP --output archive.tap --dsk-output saved.dsk
python tools/tspico_ram_image.py --chunks saved-chunks --output archive.tap --dsk-output saved.dsk
python tools/tspico_ram_image.py --chunks saved-chunks --chunk-kb 160 --output saved160.tap --dsk-output saved160.dsk
python tools/tspico_ram_image.py --chunks saved-chunks --chunk-kb 320 --output saved320.tap --dsk-output saved320.dsk
```

Use a new host folder for each export. Our DSK adapter supports standard
40-track CPC DSK containers, 16 numbered 256-byte sectors per side and our CP/M
layout. Arbitrary historical Oliger filesystems and extended DSK are not implied.
The host tool automatically obtains geometry and verifies page checksums when
CPMSTATE.TAP is present; `--chunk-kb` is needed only for old untyped exports.

## Build and validation

```text
python tools/build_dual.py --with-infocom --rom PATH_TO_TS2068_ROM
node tools/test_dual.mjs
node tools/test_dual.mjs --single
node tools/test_directory.mjs --native --dual
node tools/test_saved_ramdisk.mjs
node tools/test_saved_ramdisk.mjs --single
python tools/package_dual.py
```

Tests execute native Z80 code against functional TSPico v1.00 and v2.x models.
They do not execute the frozen 1.00 firmware or establish physical FIFO timing.
The two separate, smaller cartridges remain available for users who want an
explicit transport/storage choice.
