# PicoVideo 80-column console

## Upgrade and rollback for CP/M 2.2

PicoVideo is separate from TSPico. For the supported 80-column renderer use
PicoVideo **4.2**. The older V4 source reports register 7F as 10 hex; that value
is not proof of a release named 1.0. Its bank-capture limitations are described
below. Physical verification of a particular board remains necessary.

1. Power off/unplug the TS2068 and remove PicoVideo from its expansion connection.
2. Hold BOOTSEL on PicoVideo's Raspberry Pi Pico while connecting a Micro-USB
   **data** cable to the PC. Release when RPI-RP2 appears. Entering BOOTSEL does
   not erase flash.
3. Preserve the exact installed flash with Raspberry Pi's
   [picotool](https://github.com/raspberrypi/picotool):

   ```text
   picotool save -a -v PicoVideo-original-backup.uf2
   ```

   Wait for save and verification to finish successfully. Keep another copy of
   the backup. RPI-RP2 does not expose the firmware as a file you can drag off.
   If Windows finds the device but cannot connect, the official picotool notes
   describe installing WinUSB with Zadig for **RP2 Boot (Interface 1)** only;
   leave the mass-storage interface alone.
4. Download/extract the official
   [PicoVideo 4.2 package](https://github.com/timex-sinclair-projects/PicoVideo/blob/main/v4.2/picoTsVid4_2.zip).
   Copy its top-level picoTsVid.uf2 to RPI-RP2. The drive disconnects after flashing.
5. Unplug USB, reinstall PicoVideo with the TS2068 powered off, then start CP/M.
   Run VIDEO (expect 7F=42), COLUMNS 80 and COLOR 0. Check loading, typing and
   scrolling on the actual board.

To revert, enter BOOTSEL again and copy your verified backup UF2 to RPI-RP2.
The published older V4 UF2 is a fallback, not proof of an exact match for your
previous installation. BOOTSEL uses the Pico's ROM loader and remains available
when application firmware produces no video. These operations do not update
TSPico or alter CP/M disk files.



CP/M selects 80x24 by default when the supported PicoVideo renderer is detected.

A standard TS2068 starts in 64x24. Startup reports the selected mode. Disk

format, TSPico firmware/protocol and SD/RAMDisk selection are independent of video.



Use the supplied utility at the CP/M prompt:



```text

COLUMNS

COLUMNS 64

COLUMNS 80

```



With no argument it reports the current width and usage. Changing width clears

the screen and preserves disk contents and the COLOR scheme. Warm boots retain

the selection; a cold boot returns to the detected default. Exit applications

before switching, then restart them so they can read the new width. An unavailable

80-column renderer leaves the current mode unchanged. Both the updated cartridge

and COLUMNS.COM are required; copy the utility onto existing disks rather than

replacing disks containing saved work.



A future 80-column renderer could use a reduced-width font in the normal TS2068

512-pixel display. That renderer is not implemented yet. The COLUMNS command is

intended to keep the same interface when that option becomes available; 80 columns

does not need to remain permanently tied to PicoVideo.



Detection uses the PicoVideo extension version register (index 7F returning 42)

and selector readback. Generic ULA+ palette support is insufficient. Unknown

versions and missing devices retain 64 columns; this is not a promise that every

board or differently compiled firmware reporting 42 has the same renderer.



The reviewed 4.2 CMake file selects `coreV/displayProc80.c`, which implements

80 characters per row. The alternative `displayProc.c` has a 64-character

renderer using the same mode number. The implementation targets the distributed

80-character build. It does not install or modify PicoVideo firmware.



The driver selects ULA+ register 41 mode 5, disables the optional mirror through

register 43, initializes ink/paper entries 7/8, and enables the extended mode

through register 40. Characters occupy HOME 4000..477F and attributes

4780..4EFF. The card uses its built-in font. Scrolling preserves the first row

when the existing ADM-3A status-line convention is active. Inverse video remains

unsupported, as in the existing console. COLOR 0..7 updates both the normal

SCLD colors and the PicoVideo palette when the 80-column backend is active.



The card's port-20 text parser is disabled in the inspected `col80.c`; this

driver uses direct screen memory, not that parser. It also avoids allocating

an 80-column bitmap in the CP/M TPA. The existing 64-column bitmap font now

lives in immutable cartridge ROM at 8100..83FF, making room for the backend

inside the BIOS. Character rendering temporarily exposes that ROM and HOME

screen RAM, then restores the DOCK mapping.



The supplied Planetfall and Zork I interpreters inspect the BIOS mode flag at

launch and select their matching 64/80-column configuration. Other CP/M programs

with a configured terminal width must be configured for 80 columns separately.



## Source evidence



Upstream: https://github.com/timex-sinclair-phrojects/PicoVideo/tree/main/v4.2



Local inspected source is under

`D:/T7_Recover/Jon/Personal/Timex/TS2068_TSPicoAnalysis/research/picovideo42/`:



- `picoCode/coreB/busMain.c`: register readback, extension version, mode and

  HOME-memory mirroring.

- `picoCode/macros.h`: register addresses and the 1920-byte attribute offset.

- `picoCode/coreV/displayProc80.c`: 80-character rows and font/attribute rendering.

- `picoCode/coreV/col80.c`: disabled text-port parser.

- `picoCode/CMakeLists.txt`: selects the 80-character renderer.



No PicoVideo source/font is bundled into the CP/M cartridge. The 80-column mode

uses the font already installed on the device.



## Verification limits



Native Z80 model tests cover positive detection, unknown-version fallback,

64-column ROM-font drawing, 80-column wrapping, scrolling and status-row

preservation. Unified-cartridge tests cover both video modes and the games'

width selection. These are register/framebuffer-contract tests, not a new

PicoVideo implementation in stock Fuse/TSRun or physical-board verification.



```text

node tools/test_picovideo.mjs

node tools/test_dual.mjs --sd-only --video80 --games

node tools/test_dual.mjs --sd-only --games

```



## Physical PicoVideo troubleshooting

### Observed older V4 firmware (register 7F = 10 hex)

The hardware report `7F=10, 40=00, 41=00, 43=FF` matches the published
`V4/picoPgmV4.zip` source. Its `macros.h` defines SOFTWARE_VER as 0x10,
and `coreB/busMain.c` implements 40/41/7F but not 43. This does not identify
a product release named "1.0" and is independent of TSPico's version.

In that source the 80-column renderer in `coreV/diaplayProc.c` is commented
out. The capture path copies memory writes to `gDfRam[gZ80Adr & 0x3fff]`
without tracking port F4. CP/M program and RAMDisk writes to DOCK 4000–7FFF
can therefore appear in PicoVideo's displayed copy even when HOME screen RAM
is intact. Moving a loader buffer cannot correct this capture behavior.
The source also has the ink calculation error discussed below, consistent
with blue-on-white COLOR 0.

The cartridge retains 64 columns for this version. Selecting another mode
cannot add missing renderer or bank-filter code. The inspected 4.2 source
provides both the supported 80-column renderer and F4 filtering. A PicoVideo
firmware update, separate from TSPico, is the next hardware remedy to evaluate;
physical verification is still required. CP/M packages do not flash either
device. Follow the manufacturer's instructions appropriate to the board and
retain the previous firmware if available.

Sources: [official repository](https://github.com/timex-sinclair-projects/PicoVideo),
[V4 source](https://github.com/timex-sinclair-projects/PicoVideo/blob/main/V4/picoPgmV4.zip),
[4.2 notes](https://github.com/timex-sinclair-projects/PicoVideo/blob/main/v4.2/readme.md),
[flashing instructions](https://github.com/timex-sinclair-projects/PicoVideo/blob/main/V4/readme.md).
The V4 notes describe a rogue-pixel timing fix for Atmel PLDs, but the V4 source
still lacks F4 filtering; that timing fix alone does not establish CP/M compatibility.



`COLUMNS 80` now retries a missed startup detection using a longer register

settling interval. Startup register selection and palette writes also allow

more settling time. Unknown versions still do not automatically enable an

unverified framebuffer mode.



Run the new read-only `VIDEO` utility and report its output:



- `active` and `capability` are the BIOS flags (00/01).

- `7F` is the extension version; 42 is the inspected implementation.

- `40` is extended-mode enable, `41` the mode and `43` memory mirror.



The utility restores the register selector. It does not change the device's

mode, palette, font or firmware. If VIDEO reports a different version, that

version's bank and text-mode behavior must be checked before enabling it.



The inspected `coreB/busMain.c` contains a 64-column ink calculation:



```c

gTsCol64Ink = ((~gTsRegFF) & 0x3f) | ((gTsRegFF >> 3) & 7);

```



For COLOR 0 (FF=06), this produces attribute 39 hex: blue ink on white paper.

The low three bits of the complemented mode should not be included in ink.

The corrected expression for that calculation would use mask 0x38 instead of

0x3f. This is a source-level explanation, not proof of the firmware installed

on a particular board. The cartridge does not flash or patch PicoVideo.



The same source gates video-memory capture with F4 bits 2/3, so writes to

DOCK 4000–7FFF should not alter its separate video framebuffer. CP/M programs

use those CPU addresses as ordinary RAM; they cannot all be relocated simply

by moving a loader buffer. The updated native model checks that both HOME

screen memory and an F4-aware PicoVideo shadow remain intact during bank

transfers. If a physical PicoVideo still displays program/disk bytes while

HOME remains correct, its bank filtering or bus timing needs investigation.

That symptom alone does not establish corruption of the CP/M program buffer.



COLOR now sets the native border to the complementary paper color. On a

recognized PicoVideo it uses a matching border palette entry. COLUMNS 64 and

COLOR in bitmap mode use ULA+ mode 6 with palette entries that cover both the

original erroneous ink index and a corrected implementation. This provides a

software workaround for the black-to-blue issue without changing PicoVideo

firmware. The BIOS still reports 64 columns because it is drawing the bitmap

console; register 40 may remain enabled in this mode. An unrecognized PicoVideo

is left on the normal TS2068 path until its register layout is identified.



For an existing TSPico RAMDisk, use `build/ts2068-cpm-tspico-display-update.zip`.

It includes only CPM.DCK and small utility TAPs, not a replacement disk image.

Follow its REN/TPLOAD instructions to retain the old utility copies and saved

work. Run TPSAVE afterward if the imported tools should persist across power-off.



### Optional border color



`COLOR scheme` matches the border to the background. `COLOR scheme border`

sets it independently, for example `COLOR 7 2` gives white text on black with

a red border. Both arguments are single digits 0–7. Border numbers are:

0 black, 1 blue, 2 red, 3 magenta, 4 green, 5 cyan, 6 yellow, 7 white.

`COLOR 7` restores a matching black border. Invalid arguments leave colors

unchanged. A width change selects a matching border again; rerun COLOR with

both arguments to restore a custom border after switching widths.

