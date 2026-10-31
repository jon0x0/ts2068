# Prismatic Orbit — Timex Dynamic ECM

Open `timex-dynamic-ecm-prismatic.dck` in TSRun. Press SPACE to alternate between Dynamic ECM (green border) and standard ECM (blue border). Both versions convert the same stationary source at 256×192.

The artwork uses a rainbow torus, glossy spheres and a broad ribbon to provide smooth color ramps and curved highlights. A regular 4×4 Bayer dither was chosen after comparing Floyd–Steinberg and Atkinson conversions. The converter fits pairs in linear light, including their spatial mixtures, and chooses update positions separately for each scanline.

This uses the existing seven-update native raster engine: seven selected cells on each line switch attributes after their fourth pixel. Each half has its own legal Timex ink/paper pair, allowing up to four colors per selected 8×1 cell. Other cells retain the ordinary two-color constraint. There are 1,344 scheduled changes per frame; 427 selected cells actually contain more than two colors in this image. This is not a full-screen four-color-per-cell mode.

Eight-update trials restrict the new attributes to two shared values per scanline. Seven independent updates gave better fidelity for this full-spectrum scene. The chosen conversion reduces 2×2-averaged linear RGB error by 4.15% relative to its standard ECM conversion; this is an image metric, not a claim of a similar perceived improvement.

Validation: 360 steady frames, 55,296,000 visible pixels checked, zero pixel mismatches, every attribute write checked for address/value/timing, two SPACE toggles checked. The pinned TSRun revision is in validation.json. These results depend on TSRun's raster behavior. Physical SCLD fetch/latch behavior and contention have not been verified. This DCK uses HOME preinitialization and DOCK asset pages; it is an emulator test cartridge, not a conventional physical DOCK ROM.

## Reproduce

Requirements: Python 3, NumPy, Pillow, Node.js. The pinned TSRun modules are included.

```sh
python3 convert_image.py source.png --dither bayer --strength 1 --fit stretch
python3 build_cart.py
node test_cart.mjs
python3 package_art.py
```

Conversion also supports `floyd`, `atkinson`, and `none`. Rebuilding replaces the current output files. The generated source is already 4:3, so stretch preserves its aspect ratio.

`dynamic-native.png` and `ecm-native.png` are active-area captures from the tested cartridge, rendered using the converter's Timex palette, enlarged 3× with nearest-neighbor sampling. They are not unrestricted source-art previews.

## Experimental storage format

`image.tdec` is little-endian TDEC v2, seven-update profile. Header: Python struct `<4sBBBBHHHHIIII` (32 bytes): magic TDEC, version 2, updates 7, palette 1, dither 3, width 256, height 192, rows 192, split 4, bitmap length 6144, attribute length 6144, schedule length 4032, CRC32 of payload. Payload: Spectrum-addressed bitmap, ECM attributes, then 192 records of seven column numbers, seven original attributes and seven replacement attributes. Total 16,352 bytes. The standard ECM comparison planes are separate assets. This is a prototype format, not a universal hardware-guaranteed mode.

## Source artwork

`source.png` was created with the built-in image-generation tool. Conversion and cartridge output were produced by the included numerical and Z80 code. The exact source prompt is in `source-prompt.txt`.
