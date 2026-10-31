# Timex four-screen mixed-resolution wipe

Load `timex-ecm-highres-reveal.dck` with **Dock > Load** in TSRun:
https://josef-jelinek.github.io/TSRun/?crt=0

The demo loops through four stationary screens:

1. Butterfly ECM picture from `morpho1.tap`.
2. High-resolution title: **TIMEX 2068**, with the two display resolutions.
3. Frog ECM picture from `frog.tap`.
4. **TWO MODES, ONE DISPLAY**, with a shaded 3D grayscale scene.

Each wipe chooses an upward or downward direction, one scanline per video frame. Each complete screen
holds for approximately four seconds (240 native video frames). Both the outgoing
and incoming images stay stationary. The boundary resets to its starting edge invisibly
when each new transition starts; no image is scrolled.

The incoming image appears above the boundary for downward wipes and below it for
upward wipes. Both high-resolution-above-ECM and ECM-above-high-resolution arrangements
are used. These are
actual port FF video mode changes, performed in horizontal blanking every frame.
The new row's two sets of bytes are copied during the bottom border.

## Titles and color

Both titles are prepared 512x192 bitmaps with large proportional DejaVu Sans
lettering, rendered at higher resolution and sampled to the actual one-bit bitmap.
Light stationary 2x2 edge dithering approximates antialiasing without temporal
flicker. The preview images correct the narrow Timex high-resolution pixel aspect
ratio. The Z80 does not render fonts during the wipes.

Both titles include a fine proportional-text sample (DejaVu Sans, not the exact
TSWriter font). The first title has three full-width rows in the Timex 64-column format. Those rows
use the actual eight-by-eight ROM glyphs extracted from the TS2068 HOME ROM at 3D00,
with an exact 64-character ruler across all 512 native pixels. The included
`timex-font-8x8.bin` contains only that 768-byte character set.
Between the 64-column samples and the checkerboard, the first title has a
one-native-pixel Celtic-style interlaced braid, with alternating over/under
crossings. It is part of the actual one-bit bitmap, not a preview overlay.

The lower half is a stationary, single-pixel black/white checkerboard field, with
a black inset holding the fine text. This leaves a checkerboard frame 30 native
high-resolution pixels thick on all four sides. Its 50-percent pixel coverage
simulates gray; no actual gray palette entry or temporal flicker is used.
A solid white reference bar spans the bottom part of the field, leaving a
30-native-pixel border on each side for comparison with the checkerboard gray.

The upper half of the second title contains a ray-traced still: two shaded spheres,
a box, and a perspective floor, with highlights and cast shadows. Its continuous-tone
grayscale source is converted to a native one-bit bitmap using Floyd-Steinberg
error diffusion. The hardware still displays only black and white; intermediate
shades come entirely from spatial pixel density. The prepared picture is stationary
and is not ray-traced by the Z80. Both source and native dithered images are included.

Direction choices use an eight-bit maximal-length Galois LFSR (feedback B8, seed
5D), advanced once per transition. The sequence repeats after 255 choices; repeated
directions are allowed. It is deterministic across cold starts, as is common for
a self-contained demo without an external entropy source.

High resolution uses white ink on black paper. The ECM pictures retain their
original per-scanline bitmap and attribute bytes, including BRIGHT/FLASH behavior.
The program uses genuine 8x1 attributes, not ordinary Spectrum 8x8 cells.

## Controls

Click the emulated screen first.

- **Space**: pause or resume the automatic sequence.
- **Q**: move the current boundary upward and pause automatic playback.
- **A**: move the current boundary downward and pause automatic playback.
- **R**: resume automatic playback after manual inspection.
- **Dock > Eject**: return to the normal ROM.

## Build and test

Keep both supplied tape files beside `build_demo.py`, then run:

    python build_demo.py

The builder requires Python 3, Pillow, and NumPy. On systems without the bundled Linux
font path, change `fonts` in `title()` to the installed DejaVu Sans directory.
No assembler is required. Both prepared title PNGs are included.

Optional checks with Node.js:

    python fetch_tsrun.py
    node test_demo.mjs

The tests execute TSRun commit `41dbe3e41c692a1806f2cb900c5a0faa1549ae77` using its
unmodified CPU, cartridge parser, memory map, tape module, and raster renderer.
They checked 4,359 frames, all 193 boundary positions, and 428,507,136 active pixels
with zero differences from the expected stationary images. Two complete four-screen
loops, the image order, both mode arrangements, 240-frame pauses, both title banks,
and manual controls were verified. The checkerboard bits and actual 64-column ROM
glyphs are checked independently as well. Details are in `validation.json`.

`capture_demo.mjs` captures an animation from the same actual emulator renderer.
The GIF samples every second wipe position; the native program advances every frame
at TSRun's approximately 60.1145 Hz. The browser UI and physical hardware were not
tested.

## Storage and compatibility

The first title and butterfly sources reside in HOME RAM. The frog source occupies
part of a 16 KB replacement HOME ROM, alongside the program. The alternate title
occupies two DOCK ROM chunks, mapped by port F4 at CPU addresses 8000/BFFF when
needed. The live video display remains in HOME RAM at 4000 and 6000 throughout.
This adds another title without requiring more than the TS2068's 48 KB HOME RAM.

The DCK uses TSRun's HOME-bank loading support and DOCK ROM chunks. It is a TSRun
test image; it is not a conventional bootable DOCK-only cartridge or a verified
TSPico image. Physical hardware needs a suitable loader/cartridge arrangement and
timing verification. TSRun itself requires no modifications.

The supplied input tapes are included unchanged.
TSRun source: https://github.com/josef-jelinek/TSRun
