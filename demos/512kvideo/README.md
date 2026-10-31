# 512K video for the TS2068 + TSPico

**Requires a TS2068 and TSPico. The movie is preloaded into the TSPico's
512 KiB SRAM, verified, then played repeatedly from RAM.** No firmware
replacement is required for the tested firmware 1.00 setup.

[Preview and project page](https://jon0x0.github.io/ts2068/demos/512kvideo/) ·
[Latest download: Colour Detail 2](downloads/tspico-starwars-colour2-512k.zip) ·
[Original color version](downloads/tspico-starwars-512k.zip) ·
[Source archive](downloads/512kvideo-source.zip) · [Browse source](source/) ·
[Technical details](TECHNICAL.md)

## Install and run

**Put ALL 33 TAP files directly in the SD card's `/TAP/` directory — they
will not run elsewhere. Do not put them in a subdirectory.** The supplied
player uses fixed sample names and the firmware's TAP directory.

1. Download and extract the latest ZIP. Copy every file inside its `TAP`
   folder into the card's `/TAP/` folder.
2. Start with the normal Flash-based TSPico ROM configuration and power reset
   the TS2068 and TSPico.
3. Enter:

```basic
SAVE "tpi:cd /"
LOAD "tpi:SC512.TAP"
LOAD ""
```

Choose 1 or 2 and wait for all SRAM to load and verify. Space pauses/resumes;
X stops and displays counters. After stopping, any key returns to the menu.
Selecting an option again reloads SRAM.

**Loading replaces all 512 KiB of SRAM, including SRAM cartridges and RAM
disks.** Both options coexist on SD, but only the selected option occupies
SRAM. Switching options reloads it. No audio is included.

## Versions, resolutions and frame rates

Both versions use the entire supplied Star Wars trench-run interval,
44.5–52.0 seconds. The 12 fps option has 90 frames. The 15 fps option has
113 frames because 7.5 seconds rounds up to 113 whole frames: its nominal
loop is 7.533 seconds. Widescreen proportions are preserved approximately
to integer pixels, with black borders in the 256×192 display.

| Version / player | Option | Active resolution | Frames | Target fps | Functional-model fps |
|---|---:|---:|---:|---:|---:|
| Original / `SW512.TAP` | 1 | 256×108 | 90 | 12 | 11.89 |
| Original / `SW512.TAP` | 2 | 240×102 | 113 | 15 | 14.68 |
| Colour Detail 2 / `SC512.TAP` | 1 | 256×108 | 90 | 12 | 11.82 |
| Colour Detail 2 / `SC512.TAP` | 2 | 232×98 | 113 | 15 | 14.53 |

The original conversion favors neutral gray surfaces and suppresses false
cyan/magenta speckles, but loses some helmet, cockpit and control-panel
colors. Colour Detail 2 gives genuine colored source pixels more influence,
protects small highlights, and relaxes that suppression locally. It retains
the same ordered dither and decoder. The 15 fps window is slightly smaller
to fit the extra color information. Skin is still constrained by the limited
hardware palette; there is no native peach or brown.

The original player's sample files are `SWF000.TAP`–`SWF015.TAP` and
`SWW000.TAP`–`SWW015.TAP`. The revised player uses `SCF000.TAP`–`SCF015.TAP`
and `SCW000.TAP`–`SCW015.TAP`. All versions can coexist on the SD card.
Load `SW512.TAP` instead of `SC512.TAP` to compare the original conversion.

## What the numbers establish

The user reported successful playback of the underlying RAM512 R3 loader
and good fast-motion playback of the original trench demo on TSPico firmware
1.00, MicroPython 1.20.0, board V2.2. No physical frame-rate counters were
supplied. Colour Detail 2 has not yet received a separate hardware report.

The fps values above are **functional-model measurements**, not hardware
measurements: two complete loops, a 60 Hz tick basis, access-driven selector
transitions, and an additional 50 ms bank-response delay. Both samples were
fully loaded through the legacy protocol, byte-compared across all 512 KiB,
checked again for bank aliasing, and reconstructed exactly without copy
shortcuts. Native Fuse startup and decoder checks and pause/stop/error tests
also passed. Fuse does not emulate the TSPico filesystem or electrical bus.
Exact reports and hashes are in [validation/](validation/).

## Source and conversion tool

[Download the source](downloads/512kvideo-source.zip) or use [source/](source/).
It includes both Z80 players, quantizers, the paired-patch packer, a portable
local-video converter, the font and the TSVideoCodec ECM frame model. See
[source/README.md](source/README.md) for rebuilding and converting a different
local movie. The input movie is not included.

## Browser support

The embedded videos on the project page are encoded-frame previews at the
target cadence, not recordings of physical hardware and not a browser
emulation of TSPico. As checked on 2026-10-31, upstream
[Josef Jelinek's TSRun](https://github.com/josef-jelinek/TSRun) and its two
public forks have no TSPico implementation. Its video modes and DCK RAM
support alone do not provide the legacy FIFO, file services, MEMDOCK and
512 KiB SRAM needed by these TAPs. See [technical details](TECHNICAL.md#tsrun).

## Credits

Video: the user-supplied Star Wars Episode IV trench-run excerpt; film imagery
retains its owners' rights. TSPico: the
[Timex Sinclair projects](https://github.com/timex-sinclair-projects/TS-Pico).
The ECM frame model and codec investigation build on
[TSVideoCodec](https://github.com/jon0x0/TSVideoCodec). Each dependency and asset
retains its attribution; no blanket license is applied to third-party media.
