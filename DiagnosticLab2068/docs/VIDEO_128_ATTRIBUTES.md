# 128 attribute combination test

Source credit: **Mark Miller**, [128 Colors](https://www.timexsinclair.com/computer_media/128-colors/index.html), archived by TimexSinclair.com and listed on CATS Library Tape11. The site's date is 198x; do not invent an exact year. The demo uses checkerboard pixels to cycle the INK, PAPER and BRIGHT combinations. This diagnostic adaptation is independently written; the original BASIC listing is not embedded.

## Diagnostic adaptation

VID-05 will exercise all128 combinations formed by eight INK values, eight PAPER values and two BRIGHT settings, with FLASH off. They are attribute combinations, not128 unique palette entries or necessarily distinguishable perceived colors. Same-color INK/PAPER, reversed checkerboard pairs and bright black create equivalent or similar appearances. Pure-color/reference patterns remain necessary for fault isolation.

The host overview already exists: `assets/video/attribute-128-pixels.bin` at HOME4000 and `attribute-128-attributes.bin` at HOME5800, with an illustrative decoded `attribute-128.png` preview. Its16 columns are eight ink values, each with normal then bright; eight rows select paper0-7. Each swatch is16x24 pixels. Alternating55/AA bitmap rows produce a checkerboard. Each of the128 attribute bytes00-7F appears in exactly six character cells; generator assertions check this coverage. This grid arrangement is new to the diagnostic, rather than a reproduction of the original scrolling BASIC screen.

## Planned target implementation

After display prerequisites pass, present a separate overview and full-screen cycling option. The latter uses attribute `(bright<<6)|(paper<<3)|ink`, with fixed bounds on all loops. Preserve clean labels, current combination and a visible reference where screen space permits; a pure ink/paper phase alongside the dither helps distinguish attribute decode from visual blending. Compare CPU readback separately from user visual judgement. Offer a first/second-display comparison only when each required range is qualified.

Write display bytes directly from ROM code with HOME display chunks exposed. Do not call BASIC printing, use SCRCT/UDG system variables, wait indefinitely for PAUSE0, or depend on interrupts for exit. Use qualified frame timing when available and bounded nominal ROM delays otherwise. Scan cancel controls at safe boundaries, then restore normal mode/mapping and return through the ROM scheduler. If display RAM fails, keep the minimal reporter active instead of requiring a readable picture to leave this test.

The grid's labels/legend belong outside the raw full-coverage data plane or in a separate help view so adding labels cannot silently remove attribute combinations. Future firmware should display a short credit on its help/credits page: `128 Colors: Mark Miller / TimexSinclair.com`.

VID-05 remains specified. Host plane generation and coverage assertions are complete; target entry, cancellation, readback, emulated display and physical visual acceptance are not implemented or claimed. This addition does not change the v0.1 RAM-only cartridge.
