# r15 audio, rendering and title work

Both outputs remain level-one builds. The 64KB PicoROM has eight read-only
banks; mutable state, palette cache and player code live in HOME RAM. SRAM
uses writable DOCK banks 1â€“3. The demonstrated TSPico 512KB is still available
for future larger caches; this revision does not claim a live 512KB consumer.

## Changes

Clean background rows and runs skip unnecessary restoration work. A 128-byte
resident terrain palette removes ROM4 banking from the gameplay compositor.
The coarse colour copier uses IX instead of a temporarily redirected SP, so
the normal interrupt stack remains usable. IRQ entry saves readable F4 and
selects the runtime mapping; exit restores the interrupted mapping exactly.
The Timex Technical Manual table 2.1.13 documents F4 as R/W:
https://k1.spdns.de/Vintage/Sinclair/82/Timex%20Sinclair%202068/Tech%20Specs%20and%20Repair/Timex%20Sinclair%202068%20-%20Technical%20Manual.pdf

The SRAM compiled cache contains ten frequently drawn 8x8 cells: ship middle
pose and enemy 161. It uses 500 bytes at HOME5B00â€“5CFF, with an identical
copy in DOCK2:5B00â€“5CFF so execution remains valid with the retained colour
plane mapped. ROM7 stores the initial copy at FB00. The native clipping,
collision and dirty metadata paths remain in use; other cells and mirrored
poses fall back. The compact read-only background uses palette tokens, so
the live cache hook is disabled there. This is a small resident cache, not
a pre-shifted sprite set or a full 512KB implementation.

All 21 original Goodboy/Tiboh2019 captured bank-7 AY effect scripts and tone
periods are packed unmodified into ROM holes. The F87C trigger queues an
event; the interrupt-driven interpreter uses native F5/F6, a 1834/2205 phase
scheduler for 50Hz, and reserves AY R14/R15 for joysticks. Effects use channel
A. This is the release's original AY bank; exact menu-selector attribution
to MSX versus CPC remains unresolved. Music and the other selectable bank
have not been ported. Ordered register writes match the original reference
for all effects: 4452 effect ticks and 9420 writes on each target.

Final coloured title artwork reveals one 8-pixel column per interrupt after
the original movement. Each strip publishes bitmap and its 8x1 attributes
together. This avoids sub-cell palette clash; it is a progressive reveal,
not a full-colour translation of the original moving logo. All 32 partial
states and settled title stability are checked on both targets.

Fuse exposed a native input interrupt-state race after the preemptible
renderer increased interrupt availability. LD A,I / PUSH AF / DI could lose
the parity indication and leave IFF disabled before the native HALT delay.
Masking the periodic source at FF before sampling IFF2 fixes the hang.
Diagnostic joystick injection now derives its addresses from the rebuilt
input code, rather than assuming the old offsets.

## Direct screen versus background buffer

`scripts/compare_draw_methods.mjs` compares two successive poses on uniform
empty sky, including old bounding-box erasure, drawing and publication.
Both paths must match complete visible bitmap/ECM planes and owner/dirty
metadata. Shared owner-list traversal is excluded equally; metadata stores
are charged 13T each. Six raster starts have identical timings in this CPU
model; physical contention is not measured.

| Target / actor | Direct T | Buffered T | Direct reduction |
|---|---:|---:|---:|
| SRAM ship | 6239 | 7078 | 11.9% |
| SRAM enemy161 | 17169 | 18685 | 8.1% |
| PicoROM ship | 5771 | 8249 | 30.0% |
| PicoROM enemy161 | 15566 | 22584 | 31.1% |

Production retains the buffered renderer. A direct-screen switch still needs
scrolling, terrain-overlap, actor-overlap and collision-order validation.
The comparison establishes an opportunity, not a whole-game FPS guarantee.

## Reproduction and evidence

Build: `python scripts/build_ecm_native.py`, then
`python scripts/build_rom_ecm.py`. Run the r15 verification scripts and
`python scripts/publish_rom_ecm.py` only after their exact-hash gates pass.
Use the current Node runtime (v24); the system PATH Node is too old.

`build/diagnostics/actor_rate/*_r15_long.json` measures identical 380-update
windows, with a diagnostic death bypass absent from production. Earlier
short-window and preemptibility experiments are superseded by these files.
`build/diagnostics/r15/draw_method_comparison.json` contains the direct test.
`build/audio/{validation,live_validation,irq_banking_validation}.json` contains
source equivalence, simultaneous native joystick operation and IRQ contracts.
The WAV is synthesized from the source-matched register stream using the
local AY model, not a live-game or physical-hardware recording.

`build/diagnostics/title_reveal_r15/title_reveal.gif` renders captured CPU
RAM partial states; its display cadence is slowed for inspection. Fuse
terrain phase captures, retrace/collision tests and key-definition tests
remain separate emulator evidence. Physical hardware is still untested.


## Final measured results

sram: 11.6946 -> 14.0538updates/sec (20.17%); 114637451 -> 95393504T.

rom: 9.8584 -> 10.4107updates/sec (5.60%); 135989530 -> 128774587T.

Identical380-update diagnostic windows; not universal FPS. Cache-only whole-window
SRAM benefit is about1.9%; larger gains come from row skipping, resident palettes,
interrupt availability and replacing beeper waits. Native3IRQ pacing remains.
