# tpzx128sd — Spectrum 128 with the TSPico disk interface

**tpzx128sd is a Spectrum 128 implementation for the Timex TS2068
using TSPico, with TSPico disk-interface handling implemented and
accessible from within the Spectrum 128 BASIC environment.** It adds
SD-backed file operations and directory access to the baseline.

Both configurations provide functional Spectrum 128 BASIC environments,
but neither is guaranteed compatible with all Spectrum 128 software.
The Timex Z80 executes the ROM and BASIC code; the Pico supplies memory
control and supporting services. This is not a full Spectrum CPU emulator
running on the Pico. The tested hardware is TSPico board revision V2.2
with RP2040; current firmware/protocol support is v1.00.

**Current status:** Both tpzx128 and tpzx128sd are confirmed by the user to boot and function as BASIC environments on a physical Timex TS2068 with TSPico (October 27, 2026). General Spectrum software compatibility is not established; Directory listing and file loading in tpzx128sd are also hardware-confirmed. SAVE, VERIFY, other disk operations, and RAM-disk coverage remain separately qualified.

[Temporary operation command guide](RUN-TEMPORARILY.md) ·
[Technical description](TECHNICAL.md) · [Source and rebuild instructions](BUILD.md) ·
[Exact status and hashes](STATUS.json) · [Complete package ZIP](downloads/tpzx128sd-20261027.zip)

<a href="images/tpzx128sd.png"><img src="images/tpzx128sd.png" alt="tpzx128sd running on a Timex TS2068 with TSPico" width="20%"></a>

*Screenshot of tpzx128sd running on a Timex TS2068 with TSPico. Click to view full size.*

## What works and what has been tested

"Hardware" below means a physical Timex TS2068 and TSPico. "Desktop model"
means real Z80 ROM execution or PIO/helper contract tests on the PC. A
component diagnostic pass does not qualify every combination or BASIC command.

| Feature | Implemented behavior | Evidence and current qualification |
| --- | --- | --- |
| Spectrum 128 menu | Starts the modified two-ROM environment | Both configurations confirmed by the user to boot and function on physical hardware; supplied photographs show both menus |
| 128 BASIC editor and execution | Keyboard entry, tokenized BASIC, editing and RUN | Both BASIC environments confirmed functional on hardware; earlier baseline `10 PRINT 1+2` / `RUN` produced `3`; both ROMs also execute BASIC in the desktop model |
| AY sound through PLAY | Adapts ROM sound accesses to Timex AY ports | Baseline `PLAY "C"` produced an audible note on hardware; register writes are checked in the desktop model |
| Eight-bank RAM switching | Selects external banks 0–7 at `C000–FFFF` | Dedicated hardware diagnostic passed eight-bank retention; desktop PIO tests cover bank selection |
| ROM-half selection and paging lock | Switches ROM halves and ignores paging writes after lock | Dedicated hardware paging diagnostic passed; controller and handoff tests cover these paths |
| RAM-disk SAVE/LOAD | Retains Spectrum 128 RAM-disk paths | Exact four-byte round trip passed in the baseline desktop ROM model; physical RAM-disk acceptance remains pending |
| No-reset startup | HOME-RAM trampoline coordinates controller replacement | Both environments boot and function on hardware; baseline revision-2 no-reset startup specifically confirmed; the latest SD confirmation does not identify its reset/handoff method |
| Legacy TSPico SD gateway | Temporarily hands shared resources to installed file handlers | Separate hardware diagnostic passed 256-byte load/save/reload and restored ROM/bank state; this is a gateway component result |
| SD file LOAD | Loads files from TSPico SD within Spectrum 128 BASIC | User confirmed file loading works on physical hardware on October 27, 2026; file types and transfer-boundary coverage were not itemized |
| SD SAVE and VERIFY | SD variant provides program/CODE SAVE and VERIFY hooks | CODE byte-pattern and BASIC SAVE/LOAD/RUN round trips pass in the desktop model; separate physical SAVE and VERIFY confirmation remains outstanding |
| SD numeric arrays and MERGE | SD variant preserves the ROM's data/program handling | Numeric-array round trip and MERGE ordering pass in the desktop model; command-specific physical coverage is not separately recorded |
| SD PATH and paged DIR | SD variant displays replies and bounded directory pages | User confirmed directory listing works on physical hardware on October 27, 2026. Desktop tests additionally cover paging, acknowledgement, cancellation and service closure; PATH and each paging control were not separately confirmed on hardware |
| Protected SD service memory | SD variant rejects transfers through its reserved HOME area | Desktop tests check bounds, address wrap and driver protection |
| Calculator, 48 BASIC and Tape Tester menu choices | Choices retained from the Spectrum ROM | Presence is not a claim of complete independent physical acceptance for each facility |

Disk-specific rows apply to **tpzx128sd**, not to the baseline while it is
running. Its startup procedure still needs the PC helper/temporary Pico
definitions; it is not an installed standalone firmware release.

## Memory map and bank switching

Addresses below are hexadecimal. The arrangement provides the ROM's BASIC
environment and eight external RAM banks, but differs from a real Spectrum
128 memory map in important ways.

| CPU address | tpzx128 | tpzx128sd | Spectrum compatibility |
| --- | --- | --- | --- |
| `0000–3FFF` | One selected 16 KiB half of the patched 32 KiB ROM pair | Same arrangement, with additional SD hooks | Two ROM halves are selectable; the bytes are modified for Timex/TSPico |
| `4000–7FFF` | Fixed Timex HOME RAM, including the normal display and attributes | Same | Not an alias of external bank 5 |
| `8000–9FFF` | Fixed Timex HOME RAM | Fixed Timex HOME RAM available below the SD reservation | Not an alias of external bank 2 |
| `A000–BFFF` | Fixed Timex HOME RAM available to the baseline environment | Protected HOME service code, buffers and stack | Reserved in SD mode; BASIC RAMTOP is capped at `9FFF` |
| `C000–FFFF` | Selected external 16 KiB SRAM bank, numbered 0–7 | Same banked window; CODE accesses refer to the current bank | Bank switching works, but mapping bank 2 or 5 here does not mirror the fixed HOME regions |

The normal display uses HOME `4000–57FF` for pixels and `5800–5AFF` for
attributes. There is no automatic Spectrum alternate-screen display from
bank 7. Both configurations retain the Timex display hardware.

The ROM pair is staged in **SRAM slot 4**, occupying physical expansion
SRAM `20000–27FFF`. The eight 16 KiB RAM windows occupy `0C000–0FFFF`,
`1C000–1FFFF`, through `7C000–7FFFF`. They are separate from fixed HOME RAM.
The current corrected controller requires slot 4; arbitrary relocation has
not been implemented. Boot initializes the external banks and HOME memory,
discarding existing contents.

Paging is driven by the Pico PIO/DMA controller through private low port
`0F`, with the ROM's paging accesses patched accordingly. Latch bits 0–2
select RAM bank 0–7, bit 4 selects the ROM half, and bit 5 locks further
paging changes. The Spectrum screen-selection bit does not implement a
shadow screen here. The dedicated hardware paging diagnostic passed bank
retention, ROM-half selection, and lock behavior; desktop PIO tests also
exercise the bank/ROM combinations and ignored writes after lock.

Stock `7FFD` paging is not transparently intercepted. Unmodified machine
code using Spectrum paging ports will need adaptation. The ROM handles its
own patched paging; that does not make arbitrary bank-switching software
compatible. Programs expecting the real Spectrum's fixed bank-2/bank-5
aliases can fail even when simple bank switching works correctly.

In SD mode the 8 KiB HOME reservation also prevents BASIC from treating
`C000–FFFF` as contiguous ordinary BASIC workspace: compared with the
baseline, contiguous BASIC space is reduced by about **24 KiB**. The banked
RAM and RAM-disk paths still exist separately. SD CODE transfers into
`A000–BFFF`, into ROM, or wrapping beyond `FFFF` are rejected.

## Known unimplemented features and incompatibilities

- **General Spectrum 128 software compatibility is not established.** These
  are functional BASIC environments, not cycle-accurate Spectrum replicas.
- **No true fixed bank-2/bank-5 aliases or native bank-7 shadow screen.**
  Software relying on these memory relationships needs changes.
- **No transparent stock Spectrum I/O compatibility.** The ROM's paging
  and AY accesses are adapted, but independent machine code using `7FFD`,
  `FFFD`, or `BFFD` needs suitable patches.
- **Spectrum timing is not reproduced faithfully.** PAL 50 Hz pacing,
  contention, floating-bus behavior, and raster-sensitive effects are not
  implemented as a complete compatibility model.
- **Spectrum serial keypad, RS232 and MIDI interfaces are unavailable.**
  Unsupported ROM paths are disabled or bypassed.
- **No general snapshot/game loader or validated game library is included.**
  Games and timing-sensitive machine-code programs require separate work.
- **Tape transport and RAM-disk hardware coverage remain incomplete.** A
  menu item or retained ROM routine is not proof of a physical round trip.
- **The 48 BASIC choice is retained, but is not the dedicated stock TSPico
  Spectrum 48K mode.** Separate SD acceptance in 48 BASIC is not claimed;
  its paging lock also does not clear when only TS Reset is pressed.
- **The SD backend currently supports v1.00 only.** Provision for the next
  protocol version is planned through a separate backend, not yet implemented
  or validated. The baseline has no active TSPico disk service while running.
- **No automatic personality menu, persistent personality boot, or
  return-to-Timex command is implemented.** Use the temporary helper and
  complete-power-cycle recovery documented below.

The published common source snapshot passed **75 desktop regression tests**,
and exact rebuild comparisons matched the ROMs, service image, and handoff
TAPs. Those checks do not establish electrical timing or replace physical
acceptance. See [STATUS.json](STATUS.json) for artifact identities and
[TECHNICAL.md](TECHNICAL.md) for the implementation.

## Hardware and protocol versions

**V2.2 is the TSPico hardware revision**, using an RP2040. It is not the
firmware or file-protocol version. The current implementation supports
**TSPico firmware/protocol v1.00**. Provision for the next protocol version
is planned through a separate backend; that support is not yet implemented
or validated. The baseline personality has no active SD service while running.

## What is included

- `sd/TAP/128/`: the matching ROM, revision-2 handoff TAP, and SD test TAP where applicable.
- `source/`: ROM patchers, Z80 source, MicroPython definitions, current USB
  helper contents, generated runtime files, models, and regression tests.
- `SHA256SUMS.json`: checksums for the unpacked publication files.

The public package is named `tpzx128sd`. Its existing helper argument remains
`zx128sd`; the actual ROM filename is `TPZXSD.ROM`.

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

- Traced TSPico hardware revision V2.2 board, RP2040, and the installed stock control timing;
  the corrected adapter expects the stock 270 MHz clock.
- The physically exercised runtime is MicroPython 1.20; do not change firmware
  merely to perform this trial. Other runtime/board combinations need review.
- The installed v1.00 firmware/file-protocol contract. Support for the next protocol version is planned, not yet implemented or validated.
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

Both configurations are confirmed to boot and function on hardware. This is the revision-2 no-reset procedure; the latest SD confirmation does not identify which startup method was used. The separate reset-held alternative below remains available.

1. Boot normal Timex/TSPico operation from the unchanged installation.
   Starting at the TAP root, enter:

   ```basic
   SAVE "tpi:cd 128"
   LOAD "tpi:TPZXSD.ROM"
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
   LOAD "tpi:H128SD.TAP"
   LOAD "" CODE 32768
   ```

   **Do not run USR yet.** Finish these loads before the helper interrupts
   the stock Python dispatcher.
3. Connect USB, close other serial clients, and run from `source`:

   ```powershell
   python start_handoff128.py --port COM14 --mode zx128sd
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
   Leave the helper running: its foreground filesystem loop must continue servicing requests.

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


### SD acceptance sequence

Keep the helper running and use 128 BASIC. The included FS128.TAP contains
bytes 0 through 255. Use fresh output names to preserve existing files;
explicit SAVE has the installed firmware's ordinary overwrite behavior.

```basic
LOAD "tpi:FS128.TAP" CODE 32768
PRINT PEEK 32769
SAVE "tpi:SDCHECK" CODE 32768,256
POKE 32769,99
LOAD "tpi:SDCHECK.tap" CODE 32768
PRINT PEEK 32769
VERIFY "tpi:SDCHECK.tap" CODE 32768
```

Both PRINTs should give `1`; VERIFY should finish without error. Then try
`10 PRINT 42`, `SAVE "tpi:SDBASIC"`, delete line 10 by entering `10`,
`LOAD "tpi:SDBASIC.tap"`, and `RUN`; expect `42`.

```basic
LOAD "tpi:path"
LOAD "tpi:dir"
```

DIR uses 14 entries per page. At `scroll?`, press a key to continue, or N/Space
to cancel. Acknowledge the final `End of directory - any key` message.
Replies use the main screen and each SD session closes before the key wait.
The helper prints completed service results; it does not finish with DONE
while the foreground loop is serving BASIC.

### Alternative startup with a manually held TS Reset

This exercises the SD BASIC image with the earlier reset-held entry; the latest confirmation
of functional BASIC does not separately qualify this startup path.
Start with a complete power cycle, boot stock firmware, and use the same ROM
mount commands to stage TPZXSD.ROM in SRAM slot 4. Leave the installer's
completion screen waiting: **do not choose restart**. Keep Timex power on.

From `source` run:

```powershell
python start_fs128_sd.py --port COM14
```

Startup and definition jobs 1–5: TS Reset released; Enter at each prompt.
For job 6 only, hold **TS Reset**, press Enter, and release immediately at the
live **ARMED** message, before waiting for completion. Do not press Pico Reset.
Select 128 BASIC and leave the helper running. Run the acceptance sequence
above. Do not mix reset instructions from this alternative with the seven-job
no-reset handoff.

`start_fs128_sd.ps1 -Port COM14` is the included PowerShell alternative to the
Python starter; use one starter, not both.

### SD limits

HOME A000-BFFF is protected service RAM and BASIC RAMTOP is 9FFFh, reducing
contiguous BASIC workspace by about 24 KiB relative to the baseline. CODE
transfers into that reservation, ROM, or wrapping past FFFFh are rejected.
C000-FFFF CODE uses the current external bank. Use 128 BASIC for acceptance;
separate 48 BASIC SD operation has not been qualified. Support for the next protocol version is planned; its handlers
are not yet supported. Do not interrupt an SD write or replay a partly completed SAVE.


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
