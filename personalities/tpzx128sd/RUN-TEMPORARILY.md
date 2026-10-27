# Run tpzx128sd without permanent TSPico changes

[Back to personality page](README.md) · [How it works](TECHNICAL.md)

This is the current USB-assisted procedure, not the proposed automatic mode
menu. Use the files together from this package. All PC commands below run
from **this package's `source` directory**. BASIC commands run on the Timex;
REPL commands run on the Pico. `COM14` is an example: substitute your port.

**Status:** Working.

**Confirmed disk operations:** The user confirmed directory listing and file loading work on physical hardware on October 27, 2026. SAVE, VERIFY and other operations retain their separate test qualifications.

## What remains temporary

The ROM is staged in expansion **SRAM slot 4**, and additional Python
definitions live in the Pico interpreter's RAM. Do not upload Python files
to the Pico, replace `main.py`, install a `/TS` package, flash a UF2, choose
a Flash ROM slot, run MEMBOOT, or save a boot selection. No installed
firmware change is needed for the documented, supported development setup.

Use the traced TSPico hardware revision V2.2 / RP2040 configuration, stock 270 MHz control
timing, and the installed legacy firmware/module interface used by the trials.
MicroPython 1.20 was physically exercised; other combinations need review.
V2.2 refers to the board. Current firmware/protocol support is v1.00;
provision for the next protocol version is planned, not yet implemented or validated.
The SD backend currently supports the installed v1.00 file-handler contract.

Starting discards the current BASIC session and overwrites external SRAM
banks. Save your work first. Ordinary logs/cache and explicitly saved SD
files may still be written; temporary startup does not mean zero disk writes.

## 1 Prepare the PC and stage the ROM and trampoline

Download/extract the complete package or clone the repository. Open PowerShell
in `personalities/tpzx128sd/source` and run:

```powershell
python -m pip install --target tools/serial-python -r requirements-serial.txt
python pico_debug.py ports
```

These install desktop dependencies only; enumeration does not start the mode.
Close any old helper. With the Timex off and Pico USB unplugged, copy this
package's `sd/TAP/128` contents to `TAP/128` on SD. Keep the filenames intact.

Boot normal Timex/TSPico. Starting at the TAP root, enter on the **Timex**:

```basic
SAVE "tpi:cd 128"
LOAD "tpi:TPZXSD.ROM"
LOAD ""
```

The CD command is relative to the current directory; omit it if already in
`TAP/128`. In the stock ROM installer select **SRAM slot 4**, then return to
normal Timex BASIC without starting the new ROM or saving a boot choice.
Do not power-cycle after staging, since SRAM would be lost. If your installer's
completion screen does not provide a known way back to BASIC, stop and resolve
that firmware-specific step rather than guessing a mapping or boot command.

Still in normal Timex BASIC, load the matching handoff TAP:

```basic
CLEAR 32767
LOAD "tpi:H128SD.TAP"
LOAD "" CODE 32768
```

**Do not run USR yet.** These loads must complete while the stock dispatcher
is still running. Use the revision-2 TAP supplied with this exact ROM.
Now choose **one** of methods A, B, or C below. Do not combine their startup
or queue operations in the same session.

## A Run the guided helper

Connect Pico USB and close Thonny, Tera Term, and other serial clients. In
the desktop `source` directory run:

```powershell
python start_handoff128.py --port COM14 --mode zx128sd
```

Keep **TS Reset released throughout**. The starter refuses existing pending
or running jobs. At the first prompt press Enter to interrupt only the Pico
Python dispatcher with Ctrl-C twice and Ctrl-B. PIO memory service stays active;
this does not reboot the Pico or write a file.

Press Enter for each of the seven jobs. The first six paste definitions;
the seventh arms the handoff. When the live output says **HOME handoff armed**,
enter on the **Timex**:

```basic
RANDOMIZE USR 32768
```

Expect the Spectrum 128 menu and `ROM 0 released` / `physical_reset: False`
in the helper. Select **128 BASIC** (down once, Enter).
Leave the foreground service running while using SD BASIC. It is normal for the final job not to finish with DONE while it is serving requests.

## B Use the helper with an AI tool

An AI tool with local filesystem/terminal access can prepare the queue and
read results. It does not run on the Pico, and ordinary chat without access
to your local files cannot operate this helper. A human still performs the
Timex commands and acknowledges each desktop prompt. Only one process may
own the COM port.

After completing section 1, the AI or operator can queue the exact existing
starter sequence without opening the serial port:

```powershell
python -c "from start_handoff128 import queue_handoff; from pico_debug import DEFAULT_QUEUE; queue_handoff(DEFAULT_QUEUE, 'zx128sd')"
```

Then the operator runs this in a visible PowerShell window and leaves it open:

```powershell
python pico_debug.py serve --port COM14 --timeout 180 --interrupt
```

Follow the same Enter prompts and Timex USR command as method A. Do not also
run `start_handoff128.py`: that would attempt to queue another session.

The queued commands are exactly:

| Order | Helper action | Pico operation |
| --- | --- | --- |
| 1 | `load --file personality128.py` | Define shared PIO/DMA support |
| 2 | `load --file personality128_stock.py` | Define the corrected stock-sequence controller |
| 3 | `load --file fs128_legacy.py` | Define the legacy file backend |
| 4 | `load --file personality128_fs.py` | Define the cooperative filesystem controller |
| 5 | `load --file fs128_image.py` | Define the generated HOME service bytes |
| 6 | `load --file handoff128.py` | Define revision-2 handoff functions |
| 7 | `handoff128-sd-run` | `print(handoff128_wait('zx128sd'))` |

All seven jobs have **TS Reset released**. The baseline starter also loads
the shared SD definitions, but does not start their service in `zx128` mode.
Use `queue_handoff` above to preserve ordering, check the ROM hash, and reject
unfinished jobs instead of manually assembling an unchecked queue.

The AI can inspect local files under `build/serial-debug/pending`, `running`,
and `results`, or display completed results with:

```powershell
python pico_debug.py results
```

A long-running SD service may not produce its final result JSON until it
ends; read the live console meanwhile. A result marked `ok` only means no
recorded target traceback or transport error, not proof that the Timex booted.

Suggested instruction to an AI tool:

> Help me run this package temporarily using RUN-TEMPORARILY.md. Inspect the
> current queue before doing anything. Use the included queue_handoff and
> pico_debug helpers; do not upload target files, reset the Pico, flash a ROM,
> change config.ini/main.py, or delete/replay unfinished jobs. I will stage
> SRAM slot 4, enter Timex commands, and acknowledge the visible prompts.
> Keep TS Reset released for this handoff. Read the logs if it fails and
> distinguish a protocol result from a physically confirmed boot.

## C Paste definitions into the Pico REPL manually

This is an alternative to the queue runner, using the same functions and
file order. It has not been separately qualified as a terminal-specific
workflow. The guided helper is preferred because it handles transport,
chunking, dependency order, and error recording.

Complete section 1 first. Use a USB serial terminal that passes control keys
through to MicroPython and does not automatically upload files or reset the
board on connection. Stop the helper so it releases the port. Keep TS Reset
released. In the terminal send **Ctrl-C twice, then Ctrl-B**, and confirm the
normal `>>>` prompt. Do not use a terminal's Run/Restart or firmware-install action.

Paste the **complete contents**, one file at a time, in this order:

1. `firmware/personality128.py`
2. `firmware/personality128_stock.py`
3. `firmware/fs128_legacy.py`
4. `firmware/personality128_fs.py`
5. `firmware/fs128_image.py`
6. `firmware/handoff128.py`

For each file, press **Ctrl-E** at `>>>` to enter paste mode, paste its text,
then press **Ctrl-D while still in paste mode** to execute those definitions.
Wait for `>>>` without a traceback before the next file. Ctrl-D at a normal
prompt instead requests a soft reboot, so verify the paste-mode prompt first.
Do not paste all six files as one large compilation unit.

On Windows, this desktop command copies the first file's contents for pasting:

```powershell
Get-Content -Raw firmware/personality128.py | Set-Clipboard
```

Repeat with each remaining filename. Do not enter
`exec(open('firmware/personality128.py').read())` on the Pico: those paths are
on your PC, and there should be no newly installed Pico files to open.

Once all definitions are loaded, enter at the **Pico REPL**:

```python
print(handoff128_wait('zx128sd'))
```

That call waits for the host handshake; it is normal not to get another
`>>>` yet. At `HOME handoff armed`, enter on the **Timex**:

```basic
RANDOMIZE USR 32768
```

Keep TS Reset released. The function selects the correct controller and
enters the SD service loop automatically; do not call fs128_run_basic a second time.
Never substitute `host_held_in_reset=True` to bypass a handoff check while
the Timex is running; that flag is an operator assertion, not a reset signal.

## Check the running environment

Choose 128 BASIC, then enter on the Timex:

```basic
10 PRINT 1+2
RUN
PLAY "C"
```

Expect `3` and an audible note. These are startup checks, not a general
Spectrum compatibility test.


Keep the SD service running. Test the supplied file and a fresh output name:

```basic
LOAD "tpi:FS128.TAP" CODE 32768
PRINT PEEK 32769
SAVE "tpi:SDCHECK" CODE 32768,256
POKE 32769,99
LOAD "tpi:SDCHECK.tap" CODE 32768
PRINT PEEK 32769
VERIFY "tpi:SDCHECK.tap" CODE 32768
LOAD "tpi:path"
LOAD "tpi:dir"
```

Both PRINTs should give `1`. SAVE can overwrite an existing file of that name;
choose another basename if necessary. At directory page prompts, use a key
to continue, N/Space to cancel, and acknowledge the final page.

## SD alternative with a manually held reset

This is a **separate fresh session**, not an additional step after methods
A–C. It uses the current SD BASIC ROM, which is confirmed to boot and function;
the latest confirmation does not identify or separately qualify this startup method.
Power off both sources, boot stock, and stage TPZXSD.ROM in SRAM slot 4 as
above. This time leave the stock installer's completion screen waiting and
do not select restart. Do not load/run H128SD.TAP for this alternative.

From the PC `source` directory run:

```powershell
python start_fs128_sd.py --port COM14
```

Keep TS Reset released for startup and jobs 1–5. For job 6 only, hold **TS
Reset**, press Enter, then release at the live **ARMED** message, before
waiting for completion. Do not press Pico Reset. Select 128 BASIC, leave the
service running, and use the checks above. The helper's final submitted
Python is:

```python
print(start_fs128(True))
print('FS128_RELEASE_RESET')
fs128_run_basic()
```

The helper recognizes that marker and tells the operator to release reset.
Do not paste the three-line block in place of a coordinated reset procedure.
The included PowerShell starter is another equivalent option:

```powershell
.\start_fs128_sd.ps1 -Port COM14
```

Use one starter only. The reset-held alternative and no-reset handoff have
different operator instructions; do not mix them.


## Stop and recover

Wait for any write to finish. Stop the PC helper with Ctrl-C or leave the
manual terminal idle, power off the Timex, and **unplug Pico USB power too**.
The next full cold boot runs the unchanged installed TSPico startup. No
module restoration or firmware reflash is required. Saved SD data remains.

TS Reset alone does not restore the normal Pico controllers. Closing the
desktop helper also does not necessarily stop the Pico foreground loop.
There is no implemented `tpi:mode ts` return command in these packages.

If startup errors, goes red, or leaves an unfinished job, preserve the live
output and queue/results files. Do not run USR twice, replay an uncertain
SAVE, delete running jobs merely to bypass the starter, or claim a timeout
means an operation stopped. Inspect before retrying and begin the next trial
from a complete cold boot after any unfinished write has been resolved.
