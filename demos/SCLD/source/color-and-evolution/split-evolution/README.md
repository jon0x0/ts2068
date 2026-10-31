# Split Personality Evolution

Native TS2068 Z80 cartridge for TSRun. Insert `split-personality-evolution.dck` and reset. The previous static `split-personality.dck` is unchanged.

Sequence: full ECM; seam moves left to the center; pause; seam becomes diagonal; pause; seam becomes a sine wave; pause; sine wave travels; seam straightens while the lower half changes orientation; final four-quadrant display holds for 120 frames (about two seconds); a brief black reset transition; the full sequence repeats continuously.

## Corrected high-resolution artwork

ECM and 512-mode graphics now come from independent source images. Whenever the seam crosses an 8-pixel ECM cell / 16-pixel high-resolution span, the cartridge replaces both shared display bytes with the appropriate bitmap/attribute pair or bitmap/bitmap pair. This fixes the alternating vertical bars that occurred when ECM attribute bytes were displayed as high-resolution pixels. Both images remain stationary; the seam reveals the appropriate image at its original coordinates.

The final quadrants have different art and messages: upper-left colorful ECM sphere with green border; upper-right yellow-on-blue 512-mode ribbon; lower-left green-on-magenta 512-mode cube; lower-right ECM color texture with red border. Green is the native ink paired with magenta paper; yellow-on-magenta is not a native pair. High-resolution graphics outside their final quadrants repeat the corresponding ribbon or cube so every revealed area contains valid bitmap artwork.

## Native implementation

Each active scanline executes an unrolled 224T kernel with two timed FF mode writes. The seam moves in 16-high-resolution-pixel increments horizontally and one scanline vertically. Two writable 16KB kernel banks alternate. While one renders, the next kernel is prepared during blanking on an earlier holding frame. On a transition, immutable patch records replace only the cells whose display mode changes. Work is split between the end of the previous frame and the beginning of the next, avoiding visible updates ahead of the old image or behind the new image.

Patches use `POP HL`, `POP DE`, two memory writes, and an attribute-plane address-bit change: 55T per record, with a maximum of 256 records per transition, split into batches of at most 112 and 144. The cartridge stores 69,064 bytes of patch records across HOME, DOCK and EXROM pages. Source mappings exclude the HOME display pages so the CPU can read records while writing real display RAM. Port FF's EXROM selection bit is cleared before rendering. This build is 163,867 bytes and requires a loader supporting the DCK HOME/DOCK/EXROM blocks, as TSRun does.

The timeline retains 101 boundary entries. Moving sine uses 24 phases held for eight frames, and the final quadrant morph uses 25 steps, keeping each graphics update within the blanking budget. Frame timing pads are supplied in `timing-calibration.json`. `calibrate_timing.mjs` can regenerate them for implementation changes against the pinned TSRun core; normal rebuilding does not require recalibration.

During animation, the top and bottom borders remain green on preparation, idle and artwork-update frames. The final active scanline restores FE before bottom-border scanout, and the post-render routine selects ECM before that border becomes visible. This prevents temporary memory-banking modes from making the border flicker. Side borders retain the intentional colors associated with the visible modes. The final holding state renders top and bottom borders with their four quadrant colors; its last-scanline tail retains red for the lower-right ECM border.

At restart, normal-mode attributes make the screen black while initial ECM artwork and both kernels are restored; the border stays green. Three tested resets lasted five black frames each, about 83ms, then the next sequence synchronized to the frame interrupt. The cartridge and preview GIF both repeat.

## Validation and rebuild

The unmodified TSRun core is pinned to `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`. Over 3300 frames, tests checked 322,928,640 active display pixels against the independent source images, covering all six stages and three complete restarts with no mismatches. Every animated scanline's switch time and every visible border pixel on every frame were checked. The final borders remained correct for 360 holding frames. Reset frames were checked for a clean black active display and steady green border. This verifies TSRun behavior; no physical TS2068 test was performed.

Requirements: Python 3 + Pillow for artwork, Node.js for verification.

```
python build_demo.py
python fetch_tsrun.py
node test_demo.mjs
```

The 768-byte font extract supplies the Timex 8x8 glyphs; no full system ROM is included. Emulator modules are downloaded separately. Source images, timing data, validation report and previews are included in the combined source archive.
