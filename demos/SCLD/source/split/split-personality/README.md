# Split Personality

A native Z80 raster demo for TSRun: ECM on the left, 512x192 high resolution on
the right, with a green left border and a blue right border.

Open https://josef-jelinek.github.io/TSRun/?crt=0 and choose **Dock > Load**, then
select `split-personality.dck`. It runs automatically. There are no controls;
use **Dock > Eject** to return to the normal ROM. Disabling the CRT filter makes
the exact mode seam and one-pixel high-resolution details easier to inspect.

## What is displayed

- Left: genuine extended color mode 2, including per-scanline attributes, a colored
  sphere, all 16 palette entries, single-scanline rainbow stripes, and a colored
  one-pixel checkerboard. This half is 128 ECM pixels wide.
- Right: genuine high-resolution mode 6, yellow ink on blue paper, with text,
  one-pixel Lissajous curves and a checkerboard. This half is 256 high-res pixels wide.
- Border: green on the left half, blue on the right half, including the top and
  bottom border. The display width and physical seam are the same in both regions.

Those are halves of the native 256x192 and 512x192 modes respectively; the program
does not squeeze two full screens into the halves. Both modes use their normal
screen positions and memory addressing. The combined artwork is prepared directly
in the display's two HOME memory areas at 4000 and 6000.

## Raster program

Each visible scanline uses this exact 224-T-state loop:

- At line T8, write FF=02 to select ECM, before the left border begins at T16.
- At line T96, write FF=36 to select high resolution with yellow ink and blue paper.
  The active picture begins at T32 and ends at T160, so T96 is its exact midpoint.
- Repeat on the next line. The loop runs over all 240 visible lines, including
  the top and bottom border. The frame interrupt resynchronizes it each frame.

Port FE is set to green. In high-resolution mode, the paper and border use the
complement of the selected ink: yellow ink gives blue paper and a blue border.
That lets the mode switch produce the matching border split without a second
OUT instruction. The program does not use ULA+.

## ECM diagnostic bands

At the bottom of the left half:

- Rows 148-155: 16 adjacent swatches, eight normal and eight BRIGHT palette entries.
- Rows 158-173: a different palette entry on every scanline, one native pixel high.
- Rows 176-191: a native one-by-one-pixel checkerboard whose ink/paper pairs progress
  through neighboring spectrum hues across columns and down scanlines. Its upper
  half uses normal colors and its lower half BRIGHT colors. Spatial mixing supplies
  intermediate-looking hues; this is not an expanded palette or an animated cycle.

The 16 native palette entries contain 15 distinct RGB colors: normal black and
BRIGHT black look identical. Both black entries are deliberately present. Each ECM
8x1 cell has two colors sharing the same BRIGHT bit, as required by the hardware.
Diagnostic attributes are written directly rather than passed through quantization.

## Validation and limits

Executed with the unmodified TSRun CPU, memory, I/O and video code at commit
`41dbe3e41c692a1806f2cb900c5a0faa1549ae77`. Tests checked 180 frames and every visible
pixel, including both borders, with no differences. All 86,400 mode writes landed
at the expected scanline and T-state. Details are in `validation.json`.

This is a TSRun experiment. Real TS2068 SCLD fetch/latch behavior may place the
transition a few pixels differently or produce a seam artifact; physical hardware
and other emulators have not been tested. The timings are tuned to TSRun's model.
The DCK uses TSRun's HOME-bank support: an 8 KB boot ROM plus initialized display
RAM. It is not yet a conventional DOCK-only cartridge or a verified TSPico image.

## Rebuilding

Python 3, NumPy and Pillow:

    python build_demo.py

The builder expects DejaVu Sans at its Linux font path; change FONT for another
system. The small Timex 8x8 glyph file is included. Optional headless checks require
Node.js; fetch the pinned emulator modules first:

    python fetch_tsrun.py
    node test_demo.mjs

The preview is captured from the actual emulator renderer; it is not a browser
composition of two images. TSRun itself requires no modifications.
