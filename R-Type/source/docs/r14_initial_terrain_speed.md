# r14: starting buildings and actor update cost

The later similar buildings scroll because native column streaming installs their
attributes/IDs directly. The initial FEEB world draw paints terrain with owner0 to
the direct bitmap, then FF7A classifies scrolling cells from native attribute bit7.
The ECM sprite-overlay protection incorrectly restored/discarded those attributes
in mode2. Every expected starting solid cell consequently had owner0, and native
8842 skipped its fine scrolling. Old r13 tests required ID>=DC and thus excluded
the exact broken geometry. Their zero-error result did not establish this fix.

SRAM now preserves the original selected attribute when owner0 builds the initial
world. Its terrain path also records vertical orientation for this direct draw.
RO helpers1160/11B0 preserve initial native attrs and distinguish terrain palette
tokens with dirty-metadata bit6. The first candidate omitted that category bit:
extended testing found1171 colour-motion errors and Fuse phase0 failed67cells.
The category fix is included in the final image; all final phases pass. Sprite
overlays with nonzero owner continue to preserve the retained background palette.

verify_initial_terrain.mjs records expected coverage from actual raw terrain source
headers during the initial native draw, before IDs exist. It verifies FF8B ownership
and ROM categories, and shifts that independent coverage through actual updates and
column insertion. Movement comparison includes cells with ID0, including missed
building/ground edges. Actor cells and unrelated sky/staging are excluded. r13
SRAM has291/291 missing classifications across3initializations and64257 pixel errors.
Final r14 SRAM291classified/136160 motion byte checks, ROM194/124200: zero missing
tags, category errors or pixel motion errors. Extended normal-scroller colour test
uses diagnostic death bypass only in the emulator:593184 SRAM/531072 ROM byte
checks, zero pixel or foreground-colour motion errors. Immutable shipping ROM is
separately executed without the bypass.

Profiling80active updates identified empty-cell grid scanning and RO front-attribute
token checks as major costs. New immutable kernel1F70 dispatches owner0+clean cells
without native push/repair/pop work. Any dirty or nonzero owner follows the native
repair path. SRAM preserves any-nonzero dirty semantics; RO uses dirty bit0 while
preserving metadata bitsC0. ROM now tests attribute bit7 before reading category
metadata, avoiding that lookup for ordinary flat sky/attributes. Gameplay cadence,
movement amounts, enemy logic and sound timing are unchanged.

verify_clean_scan compares768 CPU cases directly against the native scan entry:
pixels, colours, IDs/dirty bytes, BC/DE/HL, SP, interrupt state and mapping match.
Performance baseline DCKs are the final corrected build with only the scan branch
and RO decoder block reverted. slow_front_copy.asm rebuilds the old path at the
same addresses; there is no source-artwork or initialization difference. Both80-update
runs execute1778tile paints,2552colour repairs,774terrain spans,200new columns,
10coarse scrolls and80input updates per target. SRAM26390568->24911664T, ROM
32528546->29197012T, at3.528MHz:10.69->11.33 and8.68->9.67updates/sec. Includes
interrupts, native wait and sound. Diagnostic death bypass ensures sustained work;
these are measured windows, not full-game FPS guarantees. Baseline and final hashes,
PC samples and counts are saved in diagnostics/actor_rate.

Remaining larger opportunities are background row/run skipping, compiled sprite
mask/blit caches (especially the TSPico512KB target) and nonblocking native AY effects
to replace original beeper busy loops. These need separate implementation and
validation; none is claimed as already active. Native minimum wait is three IRQs,
so simply speeding code also eventually reaches that cap. Current performance
still falls short of smooth high-rate actor animation.

Current main renderer sizes1508 SRAM/1530 ROM bytes. ROM0:1160-11BF holds initial
metadata helpers,1F70 holds scan dispatch. No writable cartridge assumptions added.
Level-one and physical hardware limitations remain. The comparison GIF consists
of actual consecutive CPU game updates at authored120ms/frame, not native timing.
