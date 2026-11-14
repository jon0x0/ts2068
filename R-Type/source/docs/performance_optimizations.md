Current first-screen fix and measured scan optimizations: [r14](r14_initial_terrain_speed.md).

r13 terrain motion correction: [coherent palette contract](r13_terrain_motion.md).

Current r12 changes and validation supersede historical details below; see [r12 graphics](r12_graphics.md).

# Renderer optimization implementation (2026-11-01)

Two playable outputs are implemented and tested. The expanded512KB asset compiler
is also implemented, but its cache is not consumed by gameplay yet. Do not call
that staging bundle a completed512KB scrolling runtime.

| Target | Output | Implemented changes |
|---|---|---|
| Stock64KB ROM/PicoROM, original colours | build/optimized/RType_TS2068_64K_PicoROM_r3.rom |84-byte unrolled vertical/mirrored copy kernels, all descriptors ROM2 |
| TSPico live ECM, initial64KB SRAM | build/ecm_native/RType_level1_ECM_TSPico_RAM_r8.dck |Shared copy kernels, deduplicated sprite-colour rows, retained HUD cache, prepared scroll-copy plan |
| Expanded512KB staging | build/expanded_cache/RType_level1_assets.ram512 |All8 raw level payloads plus480 finite terrain phases; not a banked gameplay renderer |

## Shared stock-ROM and ECM copies

src/render_kernels.asm lives at ROM0:1200-1253. Two original seven-iteration vertical
copy loops at8E02/8E5C jump to equivalent unrolled routines and return at8E10/8E6C.
All original registers, flags, bitmap bytes, IXL result and IFF match. No game
workspace, level timing, collision or immunity changes. Original r2 preserved.
Raw .rom and .bin are exactly65536 physical bytes with no DCK header. .dck is the
separate65545-byte Fuse container. These stock-ROM outputs are original-colour,
not ROM-only ECM. Build: python scripts/build_optimized_rom.py.

## ECM cached rows

The617 nonempty source cells reduce to97 distinct eight-byte shaded rows (776
bytes). Source palette, source-local phase/parity, original solid-strip flags and
paired foreground colours are prepared offline. The boot's786 header stream is
stored in unused bootstrap ROM padding and installs deduplicated row indices into
the existing DOCK1 metadata. Runtime loads a row and copies it forwards/backwards;
forced black/paper cases retain original flat-colour behavior. No conflicting
shared-source row identities were found. All617 cells are exercised by the CPU
oracle, not just the ship. Rejected title treatments remain removed.

## HUD and scrolling

HOME7800-787F is an explicitly unused tail after the ECM plane ends77FF. It stages
128 legacy HUD attributes while DOCK3 still contains the game's original logical
workspace. DOCK2:5800-587F, after its4000-57FF retained colour plane, holds previous
HUD values. Only changed cells publish their eight ECM bytes; caches reset at
initialization. FLASH is cleared as before. Full dirty actor repair is retained.

ROM0:1E30-1F6F holds160 prepared scanline pointers. The colour scroller uses those
pointers and30 unrolled LDIs instead of repeated IX-coordinate work and LDIR setup.
With IRQ source masked and interrupts disabled, SP temporarily reads the immutable
pointer stream. Its caller SP is saved in owned DOCK1:3FE0-3FE1; restored before
interrupts are re-enabled. Borders, HUD, original8-pixel scroll cadence and caller
registers remain intact. Colour rows are at ROM0:1B20-1E27. Kernels use1200-1253;
resident renderer1400-175E; native input1A00-1B13; dummy opacity1B18-1B1F staysFF.
Build: python scripts/build_ecm_native.py.

## Measurements and regression coverage

Current Fuse1.7 TS2068 frame period measured with an IRQ-off, uncontended10T JP loop
is58688 T-states, or60.1145038Hz at3.528MHz. This verifies the nominal normalization
used in prior reports; do not substitute the59736-T period from older Fuse evidence.
No physical speed claim follows.

| Measurement | Before | Optimized |
|---|---:|---:|
| Classic game-loop entries, fixed600-refresh natural window |151(r2)|152(ROMr3)|
| ECM entries, same window |113(r7)|122(r8)|
| Mirrored-copy mean in controlled IRQ-off fixture |347T|249T(stock ROM)|
| Representative direct ECM tile-hook mean |1723T(r7)|1123T(cached)|

Whole-game ECM improvement is about8%; classic about0.7%. Natural runs diverge in
simulation state and include death/restart; counts are update entries, not measured
complete raster publications or a universal FPS guarantee. Controlled sky retrace
falls92 to85 displayframes, with zero trails/IDs/deaths. No20/50/60fps claim.

-9872 actual Z80 colour cases:617cells,four mirrors,IFF0/1,both destination bases,
 independent original-palette oracle and CPU/stack/metadata checks.
-32 mirror-kernel cases per image:original,optimized ROM,ECM; exact registers/flags,
 destination bytes,carry and IFF. Average reported across controlled vectors.
-8 scroll/column whole-shadow cases include exact6144-byte results, unchanged
 borders/HUD,live new-column output and restored stack/IFF.
-HUD all-changed/unchanged/one-FLASH-cell cases compare the complete6144-byte plane.
 Current measured totals31508/12233/10627T include contention/IRQ phase; do not
 interpret the third case being lower as a universal changed-cell advantage.
-8 repair-path comparisons, key selection/start for both playable targets,
 metadata8128-byte check, trail-free controlled retrace and ECM frame8000 pass.
-Title trace on r8:6842 menu input calls,zero menu-plane repaints,mode0. r6's
47->45 per-poll oscillation remains reproducible in its preserved image.
-AROS/descriptors validated by the cartridge skill inspector; deterministic rebuilds
 produce identical ROM/ECM images. Source archives/reference projects untouched.

## Expanded512KB data: implementation and remaining boundary

scripts/build_expanded_cache.py decodes actual level-one32x32 terrain cells and all
60 observed orientation codes from the source map. It prepares eight finite phases
per orientation (480 variants) at40-pixel width with transparent spill. Each row
contains four source colour-index bitplanes plus coverage,25 bytes. This preserves
source colours for a future shared-cell compositor; these are NOT final ECM
attribute bytes that can be copied blindly to6000. All480 reconstructed phases
match canonical pixels and padding independently.

15360 prepared rows reduce to5528 unique rows. Pool plus16-bit indices uses168920
bytes instead of384000. The524288-byte staging image contains the exact optimized
r8 initial region0 plus the atlas and all eight unchanged original level payloads
(94886 bytes). Used through339404;184884 bytes remain. Manifest includes every
asset hash,all64 page hashes and chunk-bounded source spans. Reassembly from spans
is checked; region files name even MEMDOCK slots0,2,...14 explicitly.

No native loader/gateway or live cache consumer is shipped for this bundle yet.
Fuse does not model stock TSPico commands. Next implementation must place a stable
HOME gateway outside staged HUD bytes, use the verified MEMDOCK selector-priming
sequence, batch preparation ahead of draw calls, restore region0 before returning
to DOCK code, and compare CPU+bank latency against the resident path. A per-sprite
MEMDOCK switch must not be enabled without a measured benefit. The complete512KB
hardware capability remains established by the user's earlier builds; this
runtime-integration boundary is specific to this R-Type build.

Both playable images remain first-level conversions. ROM-only ECM, full arcade
art, native multi-level loading and enhanced audio remain outstanding.
