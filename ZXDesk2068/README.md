# ZXDesk2068

A port of the original [ZX Spectrum version](https://github.com/mindbox77/zxdesk)
by **[mindbox77](https://github.com/mindbox77)** (MIT licensed).

[Try both versions and download the tapes](https://jon0x0.github.io/ts2068/ZXDesk2068/)
· [Public source](https://github.com/jon0x0/ts2068/tree/main/ZXDesk2068)
· [TSWriter](https://jon0x0.github.io/TSWriter/)

The desktop has separate 256×192 and experimental 512×192 builds on stock
48 KiB HOME RAM.
No Spectrum ROM cartridge, extra RAM, or TS Pico firmware change is required.

## Run

Load `build/zxdesk2068.tap` in **native TS2068** mode and enter `LOAD ""`.
The included BASIC loader reserves memory, loads the code, and starts it.
Reset the machine to exit; the desktop takes over the machine.

For **512×192**, reset Fuse in native TS2068 mode, open
`build/zxdesk2068-512.tap`, and enter `LOAD ""`. No manual OUT or extra RAM is
needed. This is a separate boot target, not a runtime mode switch. It provides
64 eight-pixel text columns and a full-width, single-pixel pointer. Existing
windows keep their initial sizes and can be moved into the right half.

The 512 build relocates code above both bitmaps and moves the stack and buffers.
It uses black ink on white paper. Rendering favors correctness over speed for
now; redraws can take multiple frames. There is about 6.4 KiB of heap before
window allocations, compared with about 7.9 KiB in the 256 build. Large/multiple
windows can exhaust that heap. Application content does not automatically
reflow when resized, and very narrow windows can clip poorly.

For the separate `build/zxdesk2068-code.tap`, enter:

```basic
CLEAR 27647
LOAD "" CODE
RANDOMIZE USR 33280
```

The 512 CODE-only tape instead uses `CLEAR 30719` and `RANDOMIZE USR 36352`.

On a **real TS2068**, hold **SHIFT + SYMBOL SHIFT** and use the
**arrow-marked keys: 5 ←, 6 ↓, 7 ↑, 8 →** to move the pointer.
**Q/A/O/P** also work for up/down/left/right. SPACE is the pointer button. Either built-in
joystick moves it; fire is the button. Unshifted letters type into Notes.
Kempston mouse detection is disabled in this native baseline.
In the **browser player**, click inside the emulator and use the **arrow keys**
to move, with **Space** to click or drag. No modifier keys are needed. Avoid
Ctrl+Shift+Q in a browser: it may close the browser.

In **Fuse**, hold **Tab + Q/A/O/P**, or **Ctrl+Shift + Q/A/O/P**. Tab supplies
both emulated shift keys; pressing the two physical PC Shift keys does not.

Files and settings use a **volatile RAM backend: four files, 256 bytes each**.
Reset loses them. Both Commander panes show RAM. Spectrum tape, 128K banking,
esxDOS, and printer backends are excluded from the native registry; they cannot
be selected accidentally. The Print menu remains present but does nothing.
Loading the application from tape does not provide a tape document backend.

## Build

Pasmo 0.5.5 and Python 3 are required. From this directory in WSL or Linux:

```sh
bash scripts/build.sh
# Or choose an assembler explicitly:
PASMO=/path/to/pasmo bash scripts/build.sh
# With the pinned upstream checkout present, also check Spectrum compatibility:
bash scripts/build.sh --check-spectrum
```

On this Windows workspace, use `wsl bash scripts/build.sh`. The default assembler
is `pasmo` on PATH, falling back to the existing sibling
`../PasmoAssembler/pasmo-0.5.5/pasmo`. Set `PASMO` to choose another installation.
The script builds both targets, stops on assembler errors and checks code
boundaries, bitmap space, and stack headroom before packaging. Each target's
`.bin`, `.sym`, autostart `.tap`, and CODE-only `.tap` are written to `build/`.

The port is selected with `--equ TS2068=1`. Original Spectrum branches remain
in the source; the supported build script packages the native target only.

## Validation and limitations

```sh
node scripts/test_port.mjs /path/to/TSRun
node scripts/test_port.mjs /path/to/TSRun zxdesk2068-512
```

Use modern Node.js (tested with 24), the local TSRun checkout, and its native
`roms/ts2068-0.rom` and `roms/ts2068-1.rom`. Neither emulator nor ROMs are bundled.
The test loads the actual tape through the native ROM, then checks desktop
startup, IM2, HOME/video state, absence of `$7FFD` writes, native joystick and
keyboard input, notepad typing, clock/calendar window creation, nominal clock
timing, and RAM file operations. The Spectrum build also remains byte-identical
to pinned upstream. The integration test produces
`build/desktop.scr`; `build/desktop.png` is a rendered capture from this run.
Regenerate the PNG with `python scripts/render_screen.py` (requires Pillow).
The 512 test additionally checks all 12,288 byte addresses, cross-plane fills,
glyphs, clipped blits, pointer restore, X=255/256 crossing, full-width events,
right-half hit testing, dragging/resizing and menu restoration. Render its
captures with `python scripts/render_screen.py --hires` or add `--windows`.

The 256 build has user-reported basic operation in Fuse, with bugs remaining.
The 512 build is tested in TSRun; Fuse and physical hardware acceptance remain.
The Spectrum beam wait is bypassed: dragging may tear and has no measured TS2068
frame budget. The clock counts 60 accepted frame interrupts per second; it is
not crystal-calibrated. Input repeat/acceleration retain upstream frame counts.
The native HOME ROM font at `$3D00` is used (character-address bias `$3C00`).

## Current memory layout

256×192:

| Region | Use |
| --- | --- |
| `$4000–$5AFF` | Standard bitmap and attributes |
| below `$6C00` | Native BASIC/ROM loader workspace before takeover |
| `$6C00–$81BD` | Storage and slower UI code |
| `$8200–$B542` | Main entry, renderer, input, application code and tables |
| `$B543–$BCFF` | Free space and descending stack; stack top `$BD00` |
| `$BDBD`, `$BE00–$BF00` | IM2 trampoline and vector table |
| `$C000–$FEFF` | RAM files, staging space, app state, surfaces and heap |

512×192:

| Region | Use |
| --- | --- |
| `$4000–$57FF`, `$6000–$77FF` | Even and odd bitmap byte columns |
| `$7800–$8DBD` | Storage and slower UI code |
| `$8E00–$C046` | Main entry, renderer, input, application code and tables |
| `$C047–$C2FF` | Free space and descending stack; top `$C300` |
| `$C3C3`, `$C400–$C500` | IM2 trampoline and vector table |
| `$C600–$FEFF` | RAM files, app state, surfaces and heap |

The unused secondary attribute area at `$7800` holds code in 512 mode; this
layout must not be switched to extended color mode without another audit.

The build checks endpoints rather than trusting this table after source changes.
Both code regions are writable because ZXDesk uses self-modifying code.

## Provenance

Imported from `mindbox77/zxdesk` commit
`e810812860366986859eca105a406f564d2a1c04` on 29 September 2026.
`src/` is the port; `upstream/` is the original checkout for comparison.
The upstream MIT license is retained in `LICENSE`.

See [the roadmap](docs/ROADMAP.md) and the supplied
[TS Pico handoff](ZXDesk_TS2068_TSPico_Port_Handoff.md).
