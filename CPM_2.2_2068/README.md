# TS2068 CP/M cartridge

**CP/M 2.2 · cpm22-v0.1.0** ·
[Project and downloads](https://jon0x0.github.io/ts2068/CPM_2.2_2068/) ·
[Run in browser](https://jon0x0.github.io/ts2068/CPM_2.2_2068/play/) ·
[Public quickstart](docs/quickstart.md).

This directory is published inside `jon0x0/ts2068`. Public cartridges use the
public-domain font8x8 font; local builds can optionally select a private ROM
font. The Infocom collection has [separate attribution and rights](docs/infocom-notice.md).
See [release/build notes](docs/release.md) and the current
[software installation example](docs/software-install.md).

CP/M 2.2 on the TS2068, initially **64 columns x 24 rows**, with utilities,
Planetfall and Zork I. Supported storage paths are the TSPico RAMDisk/optional
modern SD service and the Oliger/JLO disk interface. The supported PicoVideo
extension can select 80 columns; ordinary TSRun/Fuse use 64 columns.

**Start here: [TSPico, Fuse/Oliger and TSRun startup guide](docs/startup.md).**

Read the [TSPico firmware/feature matrix](docs/tspico-firmware.md): original
1.00 supports the RAMDisk path; the inspected modern target is firmware 2.3.1 /
ROM 2.3, and direct SD/native-files operation also requires the optional CP/M
service. Intermediate 1.1 releases are not a validated CP/M target.
See [RAM requirements and how disks work](docs/startup.md#hardware-requirements-and-why-extra-ram-is-needed)
for the 32KiB writable DOCK expansion, possible PicoCartridge/PicoROM changes,
and the difference between TSPico RAMDisk and emulator disk storage.
See [COLOR, HI and installing software](docs/using-cpm.md) for one shared set
of instructions, including preparing and loading Zork II.
See the [sample TSPico session](docs/tspico-session.md) for a complete work,
TPSAVE, power-off and reload example.

| Target | Cartridge / disk | Start | Preserve changes |
|---|---|---|---|
| TSPico 1.00 | dual package CPM.DCK + preload TAPs | BASIC DCK loader, SRAM slot 4/5 | TPSAVE before power off; chunks reload directly |
| Inspected modern TSPico 2.3.1 / ROM 2.3 | same CPM.DCK; SD/native files need optional CP/M service | With service: Enter for SD, R for RAMDisk snapshot, L for saved RAMDisk | SD persists; RAMDisk requires TPSAVE |
| Fuse/JLO GUI | Oliger cartridge + matching 160KB/320KB DSK | tools/run_oliger.ps1 or tools/run_infocom.ps1 | JLO drive Save/Save As |
| TSRun CP/M page | Oliger cartridge + DSK or CP/M TAP | python tools/run_tsrun.py | Download DSK, TAP or 1.00 TAP set before closing/reloading |

The unified TSPico cartridge is **not** the cartridge to load in Fuse or the
TSRun Oliger page. The current default build output can change with the last
build command; use the retained profile paths or the matched game pair below.

## Run now

From the project directory, start the project-local TSRun page:

```powershell
python tools/run_tsrun.py
```

Open **http://127.0.0.1:8770/**. It uses the neighboring ../../TSRun checkout and
its two TS2068 ROMs, and boots build/infocom-cpm.dck with build/infocom-cpm.dsk.
The ordinary TSRun application is unchanged. The project supplies the disk
adapter and browser page. See the startup guide for custom paths and disks.

For the installed Windows Fuse/JLO GUI:

```powershell
.\tools\run_infocom.ps1
```

Insert the printed DSK through **Media > Disk > JLO > Drive A: / Drive 0:** if
this older GUI cannot insert it automatically, then press Enter at CP/M's
retry prompt. This uses Eduardo Fuentes's JLO-enabled Fuse, not ordinary Fuse.

For physical TSPico, extract build/ts2068-cpm-tspico-dual.zip and follow the
[startup guide](docs/startup.md#physical-ts2068-with-tspico). The SRAM slot
reservations matter. Native Z80/protocol-model tests pass; physical hardware
operation and timing remain unverified. Nothing installs firmware automatically.

## At A>

Try DIR, TYPE README.TXT, STAT, COLOR, HELLO, SUBMIT DEMO or HI. The game disk
also provides PLANET and ZORK1. PIP COPY.COM=HELLO.COM copies a program;
ERA COPY.COM removes it. ED edits text; ASM and LOAD build programs.

Backspace/Delete on the TSRun page erase a character; the TS2068 key combination
is CAPS SHIFT+0. CAPS SHIFT+C gives CP/M Ctrl-C. SYMBOL SHIFT+M gives a period.
The TSRun command box handles common punctuation without manual key chords.

## Create disks and copy host files

```powershell
python tools/cpm_disk.py create work.dsk --size 320
python tools/cpm_disk.py put work.dsk ASM.COM README.TXT
python tools/cpm_disk.py list work.dsk
```

Use .tap for a TSPico container or .img for raw sectors. Both 160KB and 320KB
layouts work. FORMAT A: initializes a mounted disk after confirmation;
RAMDisk formatting retains TPSAVE.COM so the disk can still be exported.
See [disk creation, copying and FORMAT](docs/disk-tools.md).

## Build

Python 3 and the bundled sjasmplus 1.20.3 are required. Supply your TS2068 HOME
ROM to extract the font; ROMs are not redistributed in the packages.

```powershell
python tools/build_dual.py --with-infocom --rom ../../TSRun/roms/ts2068-0.rom
python tools/package_dual.py
python tools/build.py --profile oliger --oliger-kb 320 --rom ../../TSRun/roms/ts2068-0.rom
python tools/build_planetfall.py --collection --output build/infocom-cpm.dsk
python tools/package_infocom.py
```

The game build uses the locally prepared story/interpreter inputs documented
in [provenance](docs/provenance.md). Use --oliger-kb 160 for a single-sided
utilities disk. Retained cartridges/disks live in build/profiles/oliger and
build/profiles/oliger320. The game pair is build/infocom-cpm.dck and .dsk.
The separate TSPico profiles remain available: tspico-ram, tspico-sd and
tspico-dir. Their packages use tools/package_tspico.py --profile PROFILE.

The older --profile emulator build is a 48KB volatile cartridge RAMDisk for
ordinary TSRun/Fuse without disk hardware. It is useful for a small standalone
cartridge, but cannot mount Oliger DSKs or use the TSPico's banked RAM.

## Verification and limits

```powershell
python -m unittest discover -s tests
node tools/test_tsrun_oliger.mjs
node tools/test_oliger_backend.mjs
```

Use a recent Node.js (tested with 24.19.0). The TSRun adapter tests boot actual
Z80 CP/M on both disk sizes, copy/run a COM, export/reload the disk, preserve
it through reset, and check write protection. Browser testing also runs the
SUBMIT/ASM/LOAD/HI example. The adapter is functional for this CP/M BIOS; it is
not a full JLO/SAFE or cycle-accurate FDC implementation. Fuse/JLO remains an
independent emulator implementation.

This remains CP/M 2.2. CP/M 3 is future porting work. The cartridge currently
exposes A: only; simultaneous multiple drives and general disk geometries are
not implemented. Physical TSPico/Oliger and PicoVideo hardware tests remain.

More details: [TSPico modes](docs/tspico-dual.md), [Fuse/Oliger](docs/oliger.md),
[PicoVideo](docs/picovideo.md), [original firmware audit](docs/firmware-1.00-storage-audit.md).
