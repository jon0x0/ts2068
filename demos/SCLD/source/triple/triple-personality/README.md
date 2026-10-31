# Triple Personality Mosaic

Open triple-personality-mosaic.dck in TSRun. This is a native, stationary, continuously refreshed cartridge demonstration of three genuine TS2068 SCLD modes on the same scanline:

- HIRES: port FF = 0x36, 512×192, yellow ink on blue paper. Fine proportional `512x192` text, one-highres-pixel checkerboard, one-pixel rules, and a solid-paper inset show the horizontal resolution.
- ECM: port FF = 2, 256×192 with 8×1 color attributes. Rainbow scanline text, sixteen one-line palette swatches and an alternating-pixel color pattern show the attribute resolution.
- STD: port FF = 0, standard 256×192 with genuine 8×8 attributes at 0x5800. White text and 8×8 color blocks identify this mode.

Every active scanline has ten regions. The repeating order is HIRES / ECM / STD in bands 1,3,5, and STD / ECM / HIRES in bands 2,4,6. Each band is 32 scanlines high. The first nine regions are 24 low-resolution pixels (48 high-resolution pixels) wide; the final region is 40/80 pixels wide. These are stationary images in shared screen RAM, laid out so that each region's bitmap and attribute interpretation is valid. No raster-time screen-memory patching or mode simulation is used.

There are nine horizontal boundaries on each of 192 active lines: 1,728 horizontal boundaries per frame. Ten port-FF writes per line give 1,920 mode writes per frame. Some first writes repeat the preceding line's last mode; the actual count of changed mode values is 1,734 per steady frame, including the six first-region changes at band/frame boundaries. All three modes appear on every active line.

The raster uses preloaded D/E/H values and 12-T-state OUT (C),r instructions. C stays 0xFF; delay loops can use B because the SCLD decodes the low port byte. Each row is exactly 224 T-states. In the pinned TSRun core, OUT (C),r reaches its I/O cycle eight T-states after instruction start. The first write occurs at line phase 8, before the left border; the remaining nine occur at phases 44,56,68,80,92,104,116,128,140. The program accounts for that I/O-cycle offset. The border follows highres blue paper in HIRES-first bands and the normal green border in STD-first bands.

Normal attributes persist for all eight lines of each 8×8 block. ECM attributes occupy 0x6000 plus the bitmap-style row offset. Hires uses both 0x4000 and 0x6000 bitmap planes. Regions and band boundaries align to the relevant fetch/block boundaries, so these uses do not overwrite one another. No FLASH attributes are used.

## Validation

test_demo.mjs checks every visible pixel, including all borders, and every mode write's value and exact I/O-cycle timestamp. Result: 300 frames, 46,080,000 visible pixels, 576,000 port-FF writes, zero mismatches. The steady raster loops indefinitely. Validation uses the pinned TSRun modules included in tsrun/; the recorded revision is in validation.json. Physical TS2068 hardware behavior and contention remain unverified.

The preview is rendered from the tested emulator's palette-index buffer, enlarged to 1280×960 with nearest-neighbor sampling and doubled scanline height. It is not a drawing of the intended output. Bright palette entry 8 is shown as dark gray, matching the Timex palette used in the recent conversion experiments.

## Reproduce

Python 3 with Pillow is needed to build; Node.js runs validation. Build also uses DejaVu Sans from /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf for the fine hires text. The Timex 8×8 font is bundled.

```sh
python3 build_demo.py
node test_demo.mjs
```

The cartridge is 24,585 bytes, containing an 8K HOME boot ROM and preinitialized HOME display RAM. This is an emulator cartridge experiment, not a conventional physical DOCK-only ROM. There is no special loader or external ROM requirement in the test harness.
