# Dynamic ECM: image-specific nine- and ten-position raster engines

Start with `timex-dynamic-ecm-macaw-sierra-lite.dck`. SPACE alternates the standard ECM image (blue border) and Dynamic ECM image (green border). The images stay stationary. All tests are cartridges.

The separate `timex-dynamic-ecm-macaw-10-prover.dck` is the density proof: ten different 8×1 cells each contain exactly four colors on each of 64 consecutive test lines (640 four-color cells). The other 128 lines use ordinary ECM. The density is ten of 32 cells on a test line; this is not a full-screen four-color-per-cell mode. All preview images come from the tested cartridge's captured palette indices.

The macaw is a new photographic-style generated source. It is not a photograph of an observed animal. Source generation used the built-in image tool; the complete prompt is in source-prompt.txt. The full-color source is included as source.png. The numerical conversion enforces the legal Timex palettes and the exact raster schedule.

## What changed

The old eight-change code used only two replacement attributes per row and did not span the full width. There are now two new engines, both fully unrolled and generated for the image:

| Engine | Candidate cells per row | Replacement attributes | Split positions |
|---|---:|---|---|
| display10 | 10 | Up to four distinct values per row | 2/6 pixels, alternating |
| display9 | 9 | Every replacement chosen independently | 2,4,6,2,6,2,4,6,2 pixels |

The ten-position code preloads B/C/D/E with image-specific attributes. `LD L,n` (7T) followed by `LD (HL),r` (7T) advances the address and writes at a 14T cadence. Candidate columns are 0,3,7,10,14,17,21,24,28,31. There are two fast attribute restores within each raster line. The full line costs exactly 224T: HL setup 10T + two restores 27T + four register loads 28T + ten update slots 140T + tail 19T.

The nine-position engine mixes five immediate attribute stores with four preloaded register stores. This allows nine independently chosen replacements, instead of limiting them to a shared palette. Candidate columns are 0,4,8,12,15,19,23,27,31. Its update slots total 141T; setup and restores 65T; tail 18T; total 224T.

Other original attributes are restored in row groups outside active display: load HL once, then use immediate stores and low-byte address changes. A group of n restores costs 17n+3 T-states, compared with the former 20n absolute stores. These are preparations for the next frame, not a CPU reset or screen clear. The compiler packs them into measured before/after windows and can remove low-benefit updates if the frame budget is exceeded.

The photographic image does not use every candidate on every row. A scheduled attribute change and a cell visibly containing more than two colors are different measurements; results.json records both. In the selected Sierra Lite display10 conversion there are 1,070 useful attribute changes per frame, up to nine on one row, and 484 cells with more than two colors. The line-only version reaches ten changes on one row but has only 372 cells with more than two colors. The density prover separately demonstrates ten actual four-color cells on each test line. Ten is a demonstrated result, not a proven hardware or instruction-set maximum.

## Dithering and fitting

Sierra Lite uses weights 1/2 to the next pixel, 1/4 down/back, 1/4 down. Two-row Sierra uses same-row weights 4/16,3/16 and next-row weights 1/16,2/16,3/16,2/16,1/16. Both scan serpentine. The adapted `line-sierra` variant sends all error to the next line, with weights 1/4,1/2,1/4; its diffusion fan and edge normalization match Retro Pixel Converter's Sierra Line kernel. This adapts that kernel to the timed-cell palette constraints; it does not reproduce the website's whole conversion pipeline.

Diffusion values and fitting targets are clamped to [0,1] before quantization, matching the converter's bounded-color approach. Sierra Line gives each of the two valid next-row neighbors weight 1/2 at either horizontal image edge. Palette selection runs during diffusion. Each cell fits its colors after incoming error from previously processed pixels/lines is known. Pair scoring combines 85% linear-light segment coverage (representing spatially dithered mixtures) and 15% nearest solid-color error (rewarding actual intermediate levels). For display10, four row-wide replacement pairs are selected by greedy search and coordinate swaps; each old pair remains independent. The standard ECM comparison uses the same adaptive fitting and dither, with the ordinary two-colors-per-cell restriction.

This is still visibly a sixteen-color, 256×192 conversion. Dynamic ECM improvements on this photograph are modest: the selected display10 Sierra Lite variant reduces 2×2-averaged linear RGB error by 2.2% versus its own ECM comparison. Two-row Sierra improves 3.7%; the line-only variant improves 2.7%. These are comparison metrics, not perceptual guarantees. Sierra Lite gives the best measured result of these three. Greater write counts alone do not ensure a better picture.

Additional Floyd–Steinberg, Bayer and no-dither modes are available in the converter CLI. The fixed-plan experiments are omitted from the deliverable; the chosen converter makes palettes aware of diffusion error. The live Retro Pixel Converter website has not been modified.

## Reproduce

Python 3 with NumPy/Pillow and Node.js are required. From display10:

```sh
python3 convert_image.py source.png --dither sierra-lite
python3 build_cart.py
node test_cart.mjs
```

The development cartridge filename is `timex-dynamic-ecm-macaw.dck`; deliverables have descriptive suffixes. For alternate modes:

```sh
python3 convert_image.py source.png --dither line-sierra --out variants/adaptive-line-sierra
python3 convert_image.py source.png --dither sierra2 --out variants/adaptive-sierra2
python3 make_prover.py
```

To build a variant, import build_cart, set its ROOT to that variant directory, and call build(). Test it with `ART_DIR=variants/adaptive-line-sierra node test_cart.mjs` (POSIX shell). display9 is self-contained and uses the same three main build commands, with its own development filename. package_results.py regenerates preview sheets and the delivery archives after all variant builds/tests.

## Storage and validation

TDEC v4 uses a 24-byte little-endian header `<4sB3xIIII`: magic TDEC, version 4, bitmap length, attribute length, metadata length, CRC32 of the complete payload. Payload: 6,144-byte bitmap, 6,144-byte ECM attribute plane, UTF-8 JSON metadata including profile identifier, schedule, candidate columns/splits and dither settings. Each row schedule contains columns, split positions, slot numbers, old attributes and new attributes. The builder verifies the CRC and profile. This is a prototype compiler input; compiled raster code makes playback fast. It is not yet an optimized general-purpose tape/slideshow format.

All five supplied cartridges passed 360 frames each, including two SPACE toggles. Each test checks every visible pixel and every attribute write's address, value and instruction-start timing against the compiled schedule: 1,800 frames and 276,480,000 checked visible pixels in total, with zero mismatches. Pinned TSRun commit: 41dbe3e41c692a1806f2cb900c5a0faa1549ae77. Separate conversion assertions verify all 640 prover cells contain exactly four colors, and native captures match the converted indices.

TSRun's raster reacts to memory writes at instruction-start timestamps. Physical TS2068 SCLD fetch/latch behavior and contention remain unverified. These DCKs use HOME preinitialization plus DOCK art pages; they are emulator test cartridges, not conventional physical DOCK ROMs. CPU time is dedicated to the display and keyboard comparison; no loader, wipes or live website integration is claimed.

Instruction reference: https://www.zilog.com/docs/z80/um0080.pdf

Sierra historical filter reference: https://github.com/SixLabors/ImageSharp/blob/main/src/ImageSharp/Processing/Processors/Dithering/DHALF.TXT

Kernel implementation checked against https://github.com/factus10/retro-pixel-converter/blob/main/index.html (DIFFUSION_KERNELS and the image-edge normalization).
