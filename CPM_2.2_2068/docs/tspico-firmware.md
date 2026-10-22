# TSPico firmware and CP/M features

Use this table before following the startup instructions. **Firmware 1.00,
1.1 beta, and the modern 2.3 protocol are different targets.** A newer firmware
number alone does not supply our CP/M SD filesystem service.

The combined cartridge is `CPM.DCK` from the dual package. It detects a protocol
handshake, not the exact installed firmware version. A startup message saying
"1.00 compatible" identifies the legacy protocol path; it is not a version query.

## Feature matrix

| Feature | Original firmware 1.00, unchanged | Inspected firmware 2.3.1 / ROM 2.3, without CP/M service | Same modern interfaces, with optional CP/M service |
|---|---|---|---|
| Cartridge | dual `CPM.DCK`, SRAM slot pair 4/5 | same dual cartridge | same dual cartridge; separate CPMDIR/CPMSD builds also available |
| 160KB / 320KB banked RAMDisk | Yes: load preload TAPs or saved chunks | Yes: load preload TAPs or saved TAP/chunks | Yes: preload, reload, or snapshot the SD service volume |
| Read/write files while working in RAMDisk | Yes; changes are in SRAM | Yes; changes are in SRAM | Yes; changes are in SRAM, separate from the source SD volume |
| TPSAVE output | CPM00..19/39.TAP plus CPMSTATE.TAP | one CPMRAM.TAP containing all CODE blocks | same when working in RAMDisk |
| TPSAVE SPLIT | same legacy chunk set | legacy-compatible chunk set | legacy-compatible chunk set |
| Resume a saved RAMDisk without PC repacking | Yes, directly from the saved chunk set | Yes, complete TAP or chunk set | Yes, choose L to reload |
| Operate directly on a DSK/TAP stored on SD | No | No CP/M sector backend provided by the bare firmware | Yes, through CPMDISK and the service |
| Expose ordinary /CPM/FILES as drive A: | No | No | Yes, through the directory service |
| Snapshot SD disk/native files into RAMDisk | No SD service source | No SD service source | R at startup |
| Save changes before power off | TPSAVE required | TPSAVE required in RAMDisk | TPSAVE for RAMDisk; persistent SD writes go to the service's volume |

"Yes" describes implemented code verified with native Z80/protocol models and,
for SD storage, actual Python service/filesystem tests. **Physical TSPico board
operation and timing are not yet verified.** Existing 1.00 owners can use the
RAMDisk candidate without upgrading or installing Pico-side Python modules.

## What about 1.1, 1.1c, and other 2.3.x builds?

- **1.1 / 1.1c beta:** later source introduces appending SAVEs to a mounted TAP.
  That does not establish compatibility with this cartridge's modern handshake,
  SRAM commands or extension API. These intermediate releases are **not a
  validated CP/M target**. Do not infer single-TAP TPSAVE or native-files support
  from their append feature. We have not tested an intermediate-firmware path.
- **2.3.1 firmware / ROM 2.3:** these are the version labels in the inspected
  `tspico-firmware-build` source and manual. Our modern path targets that
  status-register protocol and the inspected extension interfaces. This is a
  source/protocol compatibility target, not physical-board certification.
- **Other 2.3.x builds:** not automatically validated. They must preserve the
  inspected handshake, TAP/APPEND, MEMDOCK and extension interfaces used here.
  Later version numbers should not be read as an unconditional compatibility
  promise. Firmware and the TS2068 ROM/EXROM version are separate components.

On the inspected modern firmware, normal BASIC `SAVE "tpi:info"` reports the
firmware and ROM versions. Use that information and your installation records;
do not identify a firmware release from the CP/M legacy/modern banner alone.

## Optional CP/M SD service

For direct SD images or native `/CPM/FILES`, the modern firmware must have the
compatible EXT_SA_FUNCT extension hook, CH_CALL and packet/DMA helpers. Install
the package's four modules (`cpm_service.py`, `cpm_directory.py`, `cpm_tap.py`,
`cpm_dsk.py`), merge their handlers into the existing `dev_extcmd.py`, and choose
the backend in `cpm_config.py`. See [service setup](tspico-directory.md).
These modules are not a replacement UF2 and are not installed by copying game
files to the SD card. They are not for original 1.00. No project build or ZIP
updates the firmware, ROM, BOOT setting or device automatically.

After successful detection, the dual cartridge offers **Enter = persistent SD**,
**R = copy the service volume to RAMDisk**, **L = reload a saved RAMDisk**.
Without the service it uses the TAP/RAMDisk path. In SD mode `CPMDISK` handles
mount/export; in RAMDisk mode `TPSAVE` handles export.

## Files exchanged with TSRun and Fuse

- TSRun's **Download TAP** creates one complete disk TAP for the modern path.
  Original 1.00 cannot use its SAVE handler to build that large single file.
- TSRun's **Download 1.00 TAP set** creates a ZIP of chunk TAPs and CPMSTATE.TAP.
  Extract those files into `/TAP/CPM/SAVE/`, preserving the old save separately.
  The cartridge loads them directly; do not mount the ZIP itself.
- Fuse/JLO uses the DSK container. TSRun accepts DSK, complete CP/M TAP, saved
  chunk sets and preload volumes. Neither emulator requires TSPico firmware.

COLOR, the HI example, COM programs and 64-column display operate above the
disk backend and are available in each build. PicoVideo 80-column detection is
a separate video feature; it is not enabled merely by a TSPico firmware upgrade.

## Evidence

Original 1.00 SAVE behavior and the exact UF2 hash are recorded in the
[binary audit](firmware-1.00-storage-audit.md). The modern source inspected is
the owner's local `references/tspico-firmware-build`, whose `src/TS/tspico.py`
declares FW_VERSION 2.3.1 and ROM_VERSION 2.3. Its upstream is
[tspico-firmware-build](https://github.com/timex-sinclair-projects/tspico-firmware-build).
The original distribution is [TS-Pico](https://github.com/timex-sinclair-projects/TS-Pico).
This document records our compatibility boundary, not an assertion that every
build currently published upstream has been tested here.
