# TS2068 color experiments

These are native Z80 .dck cartridges for TSRun. Insert one as a cartridge and reset. They do not depend on BASIC or a system ROM. Each has a different cartridge filename; the previous Split Personality cartridge is preserved.

## Attribute Race Lab — new experimental cartridge

`attribute-race-lab.dck` displays a dithered shaded sphere and checker floor in ECM (256x192, one attribute per 8x1 cell). The upper image uses ordinary two-color cells. In the lower image, five spaced columns (4, 9, 14, 19, 24) receive timed attribute writes halfway across their cells. Independent color pairs are selected for the two four-pixel halves. A diagnostic band below the scene guarantees four distinct colors in each targeted cell. The rest of the screen remains ordinary ECM.

Result in the pinned TSRun core: all 65 diagnostic cells contain four distinct colors; 13 cells in the image use more than two colors. This is an actual running cartridge effect, not a pre-rendered host animation. The image benefit is small and restricted to the five columns; this is a timing experiment, not a general four-color-per-cell image format.

**This does not establish a new physical TS2068 graphics capability.** TSRun flushes its lazy raster renderer on display-memory writes, using the instruction-start time and rereading attributes for subsequent spans. That permits one cell to be rendered using two different attribute values. Real hardware fetches display data and attributes together and may hold the attribute for the whole byte. Contention and actual memory-write-cycle timing also differ. A physical-machine test is needed; a renderer with accurate fetch latches is expected to remove the mid-cell color gain.

The supplied `attribute-race-latched-model.png` is a deliberately simple comparison: it retains the original attribute for the entire cell. It is a model, not a hardware capture or complete SCLD simulation. `attribute-race-lab.png` is captured from the unmodified TSRun core.

Timing: each unrolled row is 224T. Five old-attribute writes take 100T; five replacement writes take 100T; padding and the next-row jump take 24T. Row execution begins at scanline T-57. TSRun places replacement writes at T50, 70, 90, 110, 130, halfway through the targeted 4T-wide cells. CPU speed prevents repeating this sequence for every adjacent cell. Display memory is reset before the beam reaches that row on every frame.

Hardware reference: Timex Sinclair 2068 Technical Reference Manual, May 1984 / second printing January 1986, section 2.1.8.3, printed p42, describes paired pixel/attribute RAM accesses and a new pair every 1.134 microseconds. That passage explicitly describes standard mode; the warning about ECM latch behavior is an inference from the shared display circuitry, not a measured ECM result. Scan: https://device.report/m/3253f371946016a17699f910efcc842ff5b716271ea9c0ddad00e6ef439c547d

## Timex Color Atlas

`timex-color-atlas.dck` displays all eight border colors down the left, every native high-resolution ink/paper pairing down the right, and all sixteen ECM palette entries on the left, with one-pixel checker textures. BRIGHT black and normal black are identical, so sixteen entries produce fifteen distinct RGB colors.

High-resolution pairs, ink / paper:

| Mode color | Ink | Paper |
|---|---|---|
| 0 | black | white |
| 1 | blue | yellow |
| 2 | red | cyan |
| 3 | magenta | green |
| 4 | green | magenta |
| 5 | cyan | red |
| 6 | yellow | blue |
| 7 | white | black |

Each horizontal band is 24 scanlines. The cartridge switches ECM to native 512x192 mode at the horizontal midpoint on every scanline, including the visible border. There is no BRIGHT control for the native high-resolution pairs. Hardware is not verified.

## Rebuild and verify

Python 3, Pillow and NumPy are required for artwork generation; Node.js is required for emulator verification.

```
python build_demo.py
python fetch_tsrun.py
node test_demo.mjs
```

The fetch script pins TSRun to commit `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`. Tests compare every visible pixel against the independent expected mode/attribute calculation for 120 frames per cartridge, check atlas mode-switch timing, and count the four-color diagnostic cells. JSON reports are included. Emulator modules are downloaded separately; no full Timex ROM is included.

Preview PNGs double vertical samples to give the 512-wide active display a 4:3 shape. Each TSRun 512-mode pixel remains distinct horizontally.
