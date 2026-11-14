# r12 graphics and terrain boundary

The user-marked gap is column30 inside the playfield. Bitmap bytes were nonzero
while the visible result was black. Native LDDR front-attribute publication
copies columns1..30 and leaves31 as a black staging sentinel. The fine compositor
incorrectly sampled that sentinel as column30's right-hand palette. It now uses
the real back attribute31 temporarily, restores the sentinel, and never publishes
staging31. Initialization clears its ECM rows too. The original native pixel
scroller and collision-grid layout remain intact.

Terrain headers in D911-E570 carry bit7 plus a six-bit palette-row index; reversed
rows use bit6. ROM4:9C00-9FFF holds immutable eight-line palettes. FF81's old RES7
operation is removed to preserve tags. Source decoder0E00, bulk row copier0E40,
vertical helper0EF0 and cached-boundary helper0100 decode them. All banked reads
restore runtime mappings before native execution or interrupt enable. Read-only
dirty metadata bit6 distinguishes terrain tokens from common-background tokens.
SRAM foreground painting preserves underlying background tags. ROM renderer1530
bytes has only six bytes spare below1A00; SRAM renderer1496bytes.

Original arcade frame2400 supplies platform crop152,208,216,240 and pillar crop
88,192,152,240. Their converted interior textures are fitted to the native terrain
envelope/edge pixels; original solid-cell flags remain. This is material transfer,
not full arcade building reconstruction. Black paper is required at transparent
boundaries. Both preserve and chroma variants are saved; default chroma applies
factor5 around Rec709 luma before TS quantization. Twenty-one eight-line palettes
plus reversed copies provide actual variation within each original8x8 cell.

Original arcade sprite cels175/176/177 supply the orange orb. Native descriptor57
atD550 retains2x2 cell bounds; its bitmap and palette change together in authored
pulse order0,1,2,1. This timing is newly authored, not a recovered arcade sequence.
The remaining common enemy families use consistent shell/material colours instead
of repeating vertical ramps; large boss geometry is still Spectrum-derived.
Source decoder reference: https://raw.githubusercontent.com/mamedev/mame/master/src/mame/irem/m72_v.cpp

The selected239x39 title atx4,y101 replaces the settled logo once after the native
moving intro. Bitmap and attributes are published together; no recolouring in the
input polling loop. Star writes exclude its dirty cells. High-score transitions
restore legacy mode and clear old attributes. Three natural publications per
target match exact assets;3072 polls produce zero changed writes in the title.

Build: python scripts/build_ecm_native.py, python scripts/build_rom_ecm.py,
then run the validation scripts and python scripts/publish_rom_ecm.py. Publication
requires exact hash-matched runtime, sprite, background, terrain phase, live scroll,
terrain art, orb and title reports. RTYPE_ART_PROFILE=preserve selects the retained
alternative artwork and requires rebuilding/revalidating both outputs.

Physical hardware, later-level loading and live512KB asset consumers remain pending.
No new audio conversion or full arcade enemy replacement is claimed in this release.
