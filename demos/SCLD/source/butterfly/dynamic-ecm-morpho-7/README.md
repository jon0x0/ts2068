# Seven-cell Dynamic ECM image experiment

Insert `timex-dynamic-ecm-morpho-7.dck` in TSRun and reset. Press and release SPACE to compare the dynamic butterfly (green border) with your original ECM TAP (blue border). The original five-cell cartridge is preserved separately.

This build uses seven scheduled cells on each of the 192 scanlines: 1344 cells, up from 960. Each receives a 4/4-pixel split with independently selected old and new attributes. The converter chooses among the eight possible seven-cell layouts with at least five cells between successive timed writes, covering columns 0..31. Pixels outside the selected cells remain identical to your reference.

The renderer is a fully unrolled, image-specific 10,777-byte Z80 code section. Addresses and attributes are baked into instructions. Three preparation writes and seven timed changes happen in each 224T row. Another 768 preparation writes are prestaged during blanking: 432 before active display and 336 after it. Those blocks are also straight-line code, with no runtime data decoding. Before-display work takes 8640T and after-display work takes 6720T. The kernel begins at scanline 40,T-43; each new attribute write starts at scanline T34+4*column in the pinned TSRun model. There is little CPU time left for other work.

The implementation calls these preparation writes "resets": they simply restore the first color pair for the next scan. They do not reset the CPU or clear the picture. The second pair remains in RAM after a cell is displayed, so a first-pair write is needed before displaying the cell again.

For this image, scheduled cells contain: 611 one-color cells, 540 two-color cells, 112 three-color cells and 81 four-color cells. Thus 193 cells use more than two colors. Natural image conversion does not force four distinct colors into every update. An indicative 2x2-averaged linear-RGB error measure is about 5.4% lower than the reference against a reference-tone-matched photographic target; this is not a universal perceptual quality score.

Rebuild with Python 3, Pillow and NumPy:

```
python convert_image.py source.jpg --reference reference.tap --fit stretch
python build_cart.py
python fetch_tsrun.py
node test_cart.mjs
```

Dithering options: `--dither floyd`, `atkinson`, `bayer`, `none`; scaling options: `--fit contain`, `crop`, `stretch`. The provided comparison uses serpentine Floyd-Steinberg, strength 1, and the reference TAP's framing and local color grade. The Timex palette includes BRIGHT dark gray.

The image container is experimental TDEC version 2. It uses the same 32-byte `<4sBBBBHHHHIIII` header as the earlier prototype, but version=2, updates-per-row=7, split=4 and schedule-length=4032. Payload: 6144 bitmap bytes, 6144 starting attributes, and 192 21-byte records (seven column bytes, seven old attributes, seven new attributes). The payload CRC32 is checked by the compiler. Total size: 16,352 bytes. It is not directly readable by ecmview.

Verification: 360 TSRun frames, both SPACE transitions, 55,296,000 visible pixels, and all 2688 attribute writes per dynamic frame checked for exact address/value/time. The reference image matches the supplied TAP and unscheduled cells remain unchanged. No mismatches were found. Emulator commit: `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`.

This is a HOME/DOCK DCK experiment for TSRun, not a physical DOCK-only ROM. Attribute latching, contention and the very tight timing budget remain unverified on a real TS2068. The public Retro Pixel Converter has not been modified. No full system ROM is included.
