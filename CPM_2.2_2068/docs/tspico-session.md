# Sample TSPico RAMDisk session

This example uses the unified CPM.DCK cartridge, original unmodified TSPico
firmware 1.00, and the supplied CP/M disk. PicoVideo 4.2 is optional; it provides
80 columns and correct filtering of banked video-address writes. Without it,
the standard console is 64 columns. See [PicoVideo](picovideo.md).

## Start and work

Merge the package's TAP folder onto the SD card, retaining existing files and
saved disks. The cartridge occupies SRAM slots 4/5; disk storage uses pairs
0/1, 2/3, 6/7, 8/9, 10/11 and 12/13. Contents of those RAM pairs are replaced.
See the [startup guide](startup.md) for the full setup.

At TSPico BASIC:

```basic
SAVE "tpi:cd /"
SAVE "tpi:cd CPM"
LOAD "tpi:CPM.DCK"
LOAD ""
```

In the DCK loader select SRAM, slot 4, then its DOCK selection/restart option.
Leave BOOT unchanged. CP/M reports the detected protocol and RAMDisk mode,
loads a complete saved disk if one exists, or uses the factory preload if none
exists. Wait for `A>`; the block counter is progress, not a command prompt.

The following lines are entered at `A>`; omit the prompt when typing:

```text
A>DIR
A>STAT
A>VIDEO
A>COLUMNS 80
A>COLOR 7
A>TYPE HI.ASM
A>SUBMIT DEMO
A>HI
A>PIP SESSION.TXT=README.TXT
A>TYPE SESSION.TXT
```

`COLUMNS 80` keeps the current mode if the supported renderer is unavailable.
DEMO assembles HI.ASM, converts the HEX output to HI.COM and runs it. SESSION.TXT
is an example file you can check after a power cycle. Use a different filename
if it already exists and you want to retain that copy.

On the game disk, type `PLANET` or `ZORK1`. The game's SAVE command saves game
progress to the current CP/M RAMDisk; it has not yet saved that RAMDisk to SD.
Exit the game using its QUIT command to return to CP/M before exporting.

## Save before power-off

```text
A>TPSAVE
```

TPSAVE warns that the existing export will be replaced. Type `Y` only when
ready to replace that export; preserve an older SD save separately if needed.
Wait until it prints:

```text
Saved disk chunks. Reload directly; no PC repack needed.
```

For a 320KB disk on original firmware 1.00, physical `/TAP/CPM/SAVE/` now
contains CPM00.TAP through CPM39.TAP and CPMSTATE.TAP. A 160KB disk uses twenty
page files. Keep the descriptor and all matching chunks together. TPSAVE's
completion marker/checksums let the loader reject incomplete or mixed exports;
replacement is not an atomic backup operation.

If it says `SAVE FAILED`, do not power off: retain the live RAMDisk and resolve
the failure before retrying. After a successful export you may power off.
This exports disk contents, not CPU state, the running program or screen.
CP/M's built-in SAVE command is unrelated and does not replace TPSAVE.

## Resume next time

Start CPM.DCK again using the same BASIC and slot-4 procedure. The legacy loader
reloads the saved chunk set directly, without repacking on the PC. At `A>`:

```text
A>DIR SESSION.TXT
A>TYPE SESSION.TXT
A>HI
```

The assembled program and copied file should still be present. Restart the
game and use its RESTORE command to load its saved game. Repeat TPSAVE whenever
you want subsequent RAMDisk changes to survive another cold start/power-off.

## Newer protocol differences

With the inspected TSPico v2.x firmware interfaces and optional CP/M SD service,
choose R at startup to copy the service volume to RAMDisk, or L to reload a
saved RAMDisk. Enter selects persistent SD instead. Without the service the
cartridge still supports TAP-backed RAMDisk through the TSPico v2.x storage protocol.

In TSPico v2.x RAMDisk mode, TPSAVE normally writes one CPMRAM.TAP containing all
records, and reports `Saved one disk TAP: /CPM/SAVE/CPMRAM.TAP`. TPSAVE SPLIT
selects the legacy-compatible chunk set on either protocol. If both formats
exist, the TSPico v2.x loader asks which to reload. Both RAMDisk modes need explicit
TPSAVE; the original source image is not automatically updated.

## Use the saved disk with Fuse/Oliger

Copy the complete SAVE directory to a new PC folder. From this project on the PC:

```powershell
python tools/tspico_ram_image.py --chunks build/session-save --output build/session.tap --dsk-output build/session.dsk
```

Use new output names if they exist. The descriptor supplies geometry and
checksums. Insert session.dsk into JLO-enabled Fuse with the matching 160KB or
320KB Oliger cartridge. This conversion is for interchange, not a requirement
for resuming on TSPico. Supported geometry is our standard 40-track DSK layout,
16 numbered 256-byte sectors per side; arbitrary historical Oliger filesystems
or WD1770 controller emulation on TSPico are not implied.

The current TSPico build exposes A only. A second simultaneous image as B is
not implemented.
