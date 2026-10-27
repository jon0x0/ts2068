# tpzx128 — TSPico Spectrum 128

An experimental, temporary Spectrum 128 configuration for a Timex Sinclair
2068 with TSPico V2.2 / RP2040. This baseline uses banked SRAM and the patched Spectrum ROM, without TSPico SD services while active.

**Current status:** Revision-2 no-reset startup was confirmed working by the user on October 27, 2026. Earlier stock-controller trials also confirmed 128 BASIC PRINT 1+2 and audible PLAY. This does not establish general Spectrum software compatibility.

[Technical description](TECHNICAL.md) · [Source and rebuild instructions](BUILD.md) ·
[Exact status and hashes](STATUS.json) · [Complete package ZIP](downloads/tpzx128-20261027.zip)

## What is included

- `sd/TAP/128/`: the matching ROM, revision-2 handoff TAP, and SD test TAP where applicable.
- `source/`: ROM patchers, Z80 source, MicroPython definitions, current USB
  helper contents, generated runtime files, models, and regression tests.
- `SHA256SUMS.json`: checksums for the unpacked publication files.

The public package is named `tpzx128`. Its existing helper argument remains
`zx128`; the actual ROM filename is `TPZX128.ROM`.

## Temporary operation and recovery

No UF2 upgrade, Pico-file upload, replacement `main.py`, `/TS` override,
saved boot setting, or Flash programming is required. The ROM is staged in
**SRAM slot 4**, and the helper pastes Python definitions into REPL RAM.
Do not select Flash, invoke MEMBOOT, or save a new startup configuration.

Starting this mode discards the current Timex BASIC session and overwrites
the external SRAM bank regions. Save your work first. Normal TSPico cache,
logs, and explicitly saved SD files can still be written; temporary loading
does not mean zero filesystem activity.

To return, wait for any SD write to finish, stop the PC helper with Ctrl-C,
power off the Timex, and **unplug Pico USB power as well**. The next cold
boot runs the unchanged installed firmware/startup. TS Reset alone does not
clear the Pico paging latch. No return-to-Timex mode command is implemented.

## Requirements

- Traced V2.2 TSPico board, RP2040, and the installed stock control timing;
  the corrected adapter expects the stock 270 MHz clock.
- The physically exercised runtime is MicroPython 1.20; do not change firmware
  merely to perform this trial. Other runtime/board combinations need review.
- An installed stock TSPico environment able to stage the ROM and load the TAP. The handoff uses its legacy port-14 FIFO and module layout; other firmware layouts need review.
- Desktop Python 3.10+, a USB serial cable, and exclusive access to the Pico
  COM port. Close Thonny, Tera Term, and other serial clients before the helper.

## Prepare the desktop and SD card

1. Download and extract the complete ZIP, or clone/download the repository.
   Keep this package's directory layout intact; individual helper files
   alone are insufficient.
2. Open PowerShell in this package's `source` directory and install the
   desktop serial dependency. Nothing is installed onto the Pico:

   ```powershell
   python -m pip install --target tools/serial-python -r requirements-serial.txt
   python pico_debug.py ports
   ```

   Use the reported COM port below. `COM14` is an example from the development machine.
3. Stop any old helper, power off the Timex, and unplug Pico USB.
   Copy the contents of `sd/TAP/128` to `TAP/128` on the SD card.
   Use the exact filenames shown by the stock loader; its legacy listing
   is case sensitive. Preserve existing SD files you want to keep.

## Start through the revision 2 handoff

This is the startup path whose baseline no-reset transition was confirmed on hardware.

1. Boot normal Timex/TSPico operation from the unchanged installation.
   Starting at the TAP root, enter:

   ```basic
   SAVE "tpi:cd 128"
   LOAD "tpi:TPZX128.ROM"
   LOAD ""
   ```

   In the stock ROM installer choose **SRAM slot 4**. Do not select Flash or
   save a boot choice. Return to normal Timex BASIC without booting the new
   ROM, resetting, or power-cycling. If the installer's completion screen
   prevents this on your firmware, stop and resolve that version's return
   procedure; do not guess a MEMBOOT command. The reset-held SD alternative
   deliberately stays at the completion prompt instead.
2. Still in normal Timex BASIC and the `TAP/128` directory, load the trampoline:

   ```basic
   CLEAR 32767
   LOAD "tpi:H128.TAP"
   LOAD "" CODE 32768
   ```

   **Do not run USR yet.** Finish these loads before the helper interrupts
   the stock Python dispatcher.
3. Connect USB, close other serial clients, and run from `source`:

   ```powershell
   python start_handoff128.py --port COM14 --mode zx128
   ```

4. Keep **TS Reset released throughout** startup and all seven jobs. Press
   Enter at each desktop prompt. The helper sends the current definition
   files to interpreter RAM; it does not save them as Pico modules.
5. When the live message says `HOME handoff armed`, enter on the Timex:

   ```basic
   RANDOMIZE USR 32768
   ```

6. Expect the Spectrum 128 menu. Select **128 BASIC** (down once, Enter).
   The helper should report `ROM 0 released` and `physical_reset: False`.
   The helper waits for further jobs after startup; PIO/DMA continue running on the Pico. Closing the desktop helper does not restore normal Timex operation.

The helper validates the local ROM against the local handoff manifest, but
cannot check your earlier SD copy or installer slot selection. Copy the ROM
and TAP together from this publication. Never reuse the old revision-1 TAP.

## First checks

```basic
10 PRINT 1+2
RUN
PLAY "C"
```

Expect `3` and an audible note. Report which exact startup path and ROM hash
were used; an earlier pass does not qualify a changed build.


## Errors and unfinished jobs

The starter refuses to replace pending/running jobs under
`source/build/serial-debug`. Preserve the result and queue files for inspection
after an error; a serial timeout does not prove a target write stopped.
Do not run USR twice, replay a running job, or reset a stalled write blindly.
After resolving unfinished writes, stop the helper and perform the complete
power-cycle recovery before a new trial. A red border after handoff means
the expected ROM fingerprint was not obtained, not a successful boot.

## Compatibility boundaries

These personalities do not provide transparent compatibility with arbitrary
Spectrum 128 games. Shadow-screen support, true fixed-bank aliases, timing,
and general software compatibility remain limited. RAM-disk paths exist,
but physical RAM-disk acceptance is still outstanding. The proposed TSPico
mode menu and mode-selection commands are not part of these packages.
See [TECHNICAL.md](TECHNICAL.md) for the mechanism and model limitations.
