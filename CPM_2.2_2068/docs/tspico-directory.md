# Newer TSPico CP/M: ordinary SD files, with TAP compatibility

This page targets the inspected **firmware 2.3.1 / ROM 2.3 interfaces plus the
optional CP/M service**. It is not a recipe for original 1.00 or an assertion
of support for 1.1 beta. Read the [firmware/feature matrix](tspico-firmware.md).

This is the recommended newer-protocol build. Drive A defaults to the ordinary
SD directory `/CPM/FILES`. Copy the COM, DAT, ASM, SUB and TXT files you want
there; no disk image is needed. CP/M creates, edits, renames and deletes those
files through the directory bridge. A compatible newer TSPico firmware and
the optional CP/M service are required; the version number alone does not
provide these CP/M filesystem semantics. Nothing is installed automatically.

**Status: native Z80 plus actual Python service/file tests; not physical-board
verification.** Keep the firmware 1.00 SRAM build for an unchanged original
TSPico. This package does not update firmware or change device settings.

## Card layout and service configuration

Merge the supplied TAP directory onto the card, preserving existing files:

```text
/TAP/CPM/CPMDIR.DCK
/TAP/CPM/FILES/CPMDISK.COM
/TAP/CPM/FILES/PLANET.COM
/TAP/CPM/FILES/PLANET.DAT
/TAP/CPM/FILES/ZORK1.COM
/TAP/CPM/FILES/ZORK1.DAT
/TAP/CPM/FILES/...utilities and examples...
/TAP/CPM/COMPAT.TAP
```

The package includes the other utilities, COLOR, and HI.ASM/DEMO.SUB. Keep both
COM and DAT files for each game. The service uses public paths `/CPM/FILES` and
`/CPM/NAME.TAP`; these are normally under the SD card's TAP root.

On an already compatible newer firmware, install the optional cpm_service.py,
cpm_directory.py, cpm_tap.py and cpm_dsk.py, and merge these cpm_config.py settings:

```python
CPM_STORAGE = 'directory'
CPM_DIRECTORY = '/CPM/FILES'
CPM_DIRECTORY_KB = 320
```

Merge handlers into the existing dev_extcmd.py, preserving other extensions:

```python
from cpm_service import EXT_SA_FUNCT as CPM_COMMANDS
EXT_SA_FUNCT.update(CPM_COMMANDS)
```

The extension needs the matching EXT_SA_FUNCT, CH_CALL, packet and DMA interfaces
listed in the firmware matrix. Arbitrary 2.3.x firmware is not automatically confirmed
compatible. The bare TSPico v2.x file channel interface is not this directory bridge.

Load CPMDIR.DCK with the normal DCK loader into an unused **SRAM even slot pair**.
Leave BOOT unchanged. This build does not reserve the other SRAM disk pairs used
by the firmware 1.00 variant. It verifies the directory capability and geometry
before starting CP/M. The screen says `A: TSPico directory 320K`.

## Working with native files

Use DIR, TYPE, ED, ASM, SUBMIT and PIP normally. Game SAVE creates PLANET.SAV or
ZORK1.SAV as an ordinary file under FILES when the application closes it.
Files written by CP/M are normally rounded to 128-byte records; text may contain
the usual CP/M EOF padding. Renaming an untouched native file preserves its
original byte length.

This version presents a bounded 320KB CP/M volume: 316KB for data, 128 directory
entries shared by file extents, 2KB allocation blocks, and user area 0 only.
The SD card can be larger. Only supported 8.3 filenames are exposed; subfolders
and long names are ignored, case-colliding names are rejected. A private
`.cpm-work` directory holds staging/recovery files. Do not edit it manually.

Do not modify the native files from another host while they are mounted. To
pick up files copied onto the card between sessions, boot again, or close CP/M
files and run `CPMDISK DIR` to remount/refresh the directory. Commit checks reject
detected external changes rather than silently overwriting them.

## DSK and TAP disk mount and save

Both **160KB single-sided** and **320KB double-sided** Oliger CP/M disks
are supported. DSK uses the standard CPC container produced by this project's
Fuse tools: 40 cylinders, 16 numbered 256-byte sectors per side. Extended DSK,
different geometries, unusual sector ordering and error-marked media are rejected.
This describes our CP/M layout, not automatic recognition of every historical
Oliger filesystem. A 160KB disk uses 1KB allocation blocks; 320KB uses 2KB.
The BIOS refreshes these parameters on warm boot after mounting.

```text
CPMDISK                       Show help
CPMDISK SAVE BACKUP.TAP        Snapshot current drive into /CPM/BACKUP.TAP
CPMDISK MOUNT COMPAT.TAP       Switch drive A to /CPM/COMPAT.TAP
CPMDISK MOUNT DISK160.DSK      Mount a single-sided Fuse Oliger disk
CPMDISK SAVE BACKUP.DSK        Export in Fuse-compatible DSK format
CPMDISK DIR                   Return to /CPM/FILES, or refresh its contents
```

The packaged COMPAT.TAP contains the same initial files and includes CPMDISK.
CPM160.DSK and CPM160.TAP provide single-sided utility disks including CPMDISK;
the games remain on the larger initial volume and in the native directory.
SAVE produces a **new** file; it refuses to replace an existing export. Choose
a fresh 8.3 TAP or DSK name. The service publishes the export only after writing and
validating it. Close files before switching or taking a snapshot. A successful
mount resets CP/M's disk state through warm boot; errors leave the old mount.

Mounted TAP sectors are read/written directly in that TAP on SD. Each write
updates the containing TAP block's checksum. SAVE can make a fresh snapshot of
the mounted TAP as well. These in-place writes are synchronous, not journaled
against power loss. Changes in a mounted TAP do not create native FILES entries.
Cold cartridge startup returns to the configured ordinary directory.

TAP contains the same raw CP/M sectors as DSK, wrapped as one metadata CODE
block and twenty or forty 8KB CODE blocks. The host tool can split it into
the stock 1.00 build's four or eight small boot TAP volumes:

```text
python tools/tspico_ram_image.py --tap BACKUP.TAP --output archived.tap --volumes boot-volumes
python tools/tspico_ram_image.py --dsk DISK160.DSK --output disk160.tap --volumes boot160
python tools/tspico_ram_image.py --tap disk160.tap --output archived160.tap --dsk-output disk160.dsk
```

This is a CP/M disk TAP format, not an arbitrary game or BASIC TAP. Boot volume
sets must first be assembled into a single TAP for mounting here. Hardware-bound
utilities remain build-specific: do not run the original SRAM TPSAVE.COM on the
TSPico v2.x SD cartridge. Keep CPMDISK.COM inside a mounted disk if you want to switch back
without restarting; a cartridge restart also returns to the native directory.

## Rebuild and tests

```text
python tools/build.py --profile tspico-dir --with-infocom --rom PATH_TO_TS2068_ROM
node tools/test_directory.mjs --native
node tools/test_directory.mjs --native --dual-only
python tools/package_tspico.py --profile tspico-dir
```

The integration executes the actual Python bridge against real temporary native
files, using TSRun's Z80 and modeled TPI framing. It checks boot, copy, rename,
delete, assembly output, TAP snapshot/mount, writes isolated to TAP, and return
to native files. Host tests cover both geometries, extended files, TAP CRC and
high-sector writes. Physical FIFO timing remains a separate board test.
