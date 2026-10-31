# Eight-cell Dynamic ECM image experiment

Insert `timex-dynamic-ecm-morpho-8.dck` in TSRun and reset. Press and release SPACE to compare the dynamic butterfly (green border) with your exact original ECM TAP (blue border). The original five-cell build is preserved. A seven-cell version with less restrictive color selection is included in the package for comparison.

This build schedules eight cells on every scanline: 1536 cells, 60% more than the five-cell version. It uses a 10,176-byte fully unrolled, image-specific renderer. There are no per-cell loops, attribute-table reads or runtime color searches in active display.

## Faster code

Four old attributes are reset during each row. Another four resets per row are moved into blanking, with 432 prestaged before the screen and 336 after it. The converter chooses two new attributes per scanline and preloads them into B and C. New attribute changes use `LD (HL),B/C` (7T). Between changes, `LD L,nextColumn` (7T) supplies the next address. Successive changes are therefore 14T apart instead of the old 20T immediate-store sequence.

At that cadence, the split alternates between 2/6 and 6/2 pixels; the converter and preview enforce the corresponding split rather than assuming 4/4. The eight-column pattern is `[0,3,7,10,14,17,21,24]` plus a single global horizontal offset selected by the converter. For this image the offset is 2, so the columns are `[2,5,9,12,16,19,23,26]`.

Each timing row is 224T: four immediate preparation stores total 80T; two register loads take 14T; the first HL address takes 10T; eight stores plus seven low-address loads take 105T; a not-taken `RET Z` takes 5T; and the row's jump takes 10T. The dynamic dispatcher sets Z clear and all row instructions preserve it, so the conditional return never returns; it supplies an exact five-cycle pad. The test verifies execution through every row.

The preparation writes here have independent old values: each old store is `LD A,n; LD (nn),A`, 20T. Only the new attributes share the two per-row register values. This distinction is important for image quality. "Reset" in the implementation means restoring the first pair for the next scan; it is an ordinary memory write, not a CPU reset or screen clear. Each frame must begin the cell with the first pair and switch to the second pair during that cell.

The cost of the speedup is that each updated cell's new pair must be one of two per-row choices. Its old pair remains independent. The converter exhaustively chooses those two new attributes from the legal Timex pairs. This is a real color-freedom tradeoff, not a universally better conversion.

## Measured image result

There are exactly 1536 mid-cell attribute stores per frame (8 x 192), plus 1536 preparation stores, totaling 3072. Of the mid-cell stores, 889 write a different attribute value. For the butterfly, the scheduled cells contain 572 one-color cells, 702 two-color cells, 186 three-color cells and 76 four-color cells. Thus **262 cells use more than two colors**, versus 186 in the earlier five-cell image. Instruction counts and visible-color counts are different; all 1536 scheduled stores execute, including identical-value stores. The converter does not force four distinct colors into all scheduled cells.

The 2x2-averaged linear-RGB error measure is about 4.0% lower than the supplied ECM reference against the same reference-tone-matched photographic target. The seven-cell version scores about 5.4% lower on that measure, despite having fewer scheduled cells. The visual comparison is therefore useful; greater coverage does not guarantee better image quality. Unscheduled pixels remain identical to the supplied reference TAP.

## Rebuild

Python 3 + Pillow + NumPy generate the constrained image and native code. Node.js runs the checks.

```
python convert_image.py source.jpg --reference reference.tap --fit stretch
python build_cart.py
python fetch_tsrun.py
node test_cart.mjs
```

Other dithers: `--dither atkinson`, `bayer`, `none`; scaling: `--fit contain`, `crop`, `stretch`. The supplied conversion uses serpentine Floyd-Steinberg, strength 1. Reference tone matching preserves each reference cell's mean color while recovering finer variation from the original JPEG. Pixels outside the schedule are unchanged.

The experimental TDEC container is version 3, count=8, split=0 (meaning the profile's alternating 2/6 pattern), schedule length=4608, total size=16,928 bytes. Header: 32 bytes, `<4sBBBBHHHHIIII`; payload: 6144 bitmap bytes, 6144 old attributes, then 192 24-byte rows (eight columns, eight old values, eight new values). A payload CRC32 is checked. This format requires the matching raster kernel and is not an ordinary ECM file.

Validation checks 360 frames across Dynamic→ECM→Dynamic, both SPACE transitions, 55,296,000 visible pixels, and every one of 3072 attribute writes per dynamic frame. It also checks reference TAP equality and unchanged cells outside the schedule. No mismatches were found. The unmodified TSRun core is pinned to `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`.

This DCK uses HOME initialization and DOCK image storage for TSRun. It is not a conventional physical DOCK-only ROM, and hardware attribute latching/contention/timing are unverified. No public Retro Pixel Converter changes or full system ROM are included.
