# r21: separate palettes for terrain group instances

The user correctly observed that r20 did not visibly give separated groups
different palettes. Its graph merged all occurrences of each source tile cell.
It also used C4BE as map end, scanning539 apparent columns including enemy data.
The actual map is E571–E788 (C4BC to C4B4),535 bytes/107 columns, as already
documented by the expanded-cache builder. r21 uses these verified bounds.

The new graph contains level instances rather than source tile identities.
Within each8-row band, foreground cells separated by at most8 black pixels on any
scanline stay connected, preserving colour compatibility for every fine scroll
phase. Larger gaps allow independent arrangements. Alternating independent groups
use warm copper/gold/red or cool cyan/blue machinery, with different vertical
arrangements. Contiguous areas retain compatible colours; row bands can have
different group boundaries because ECM works at8×1 resolution. Shared source
art no longer forces disconnected occurrences into the same palette.

The actual map yields196 populated band groups. Their20-bit column masks compress
to87 five-byte records including a terminating zero mask (435 bytes). ROM0
08C0–0BBF contains the table and helpers, separately reserved from death65 at0BC0.
The selected mask is cached in three bytes of idle title scratch FC50–FC52 once
per incoming8-pixel column. Initial drawing looks up its world position directly.
Only staged RAM tokens are modified; cartridge memory remains read-only.
Terrain repaint/repair reads the retained instance style rather than the source
tile's style. Collision flags and geometry are preserved.

To fit both64KB builds, the unused fine4 title atlas at9EA0–9FEF is reclaimed
for music data. r20's sweep already steps8 pixels; all46 states remain unchanged.
A build assertion rejects a return to a4-pixel sweep without restoring its atlas.
Selected death65 and its music-channel ownership remain unchanged.

Validation:
- Whole-level native helper test:1831 converted instance cells per target;
  181 source cells demonstrably receive different styles in different instances.
- Natural boot checks validate initial cells and actual incoming streamed tokens
  against world positions. Both targets show warm buildings beside cool ground.
- Independent535-byte map composition checks99997 occupied8×1 cells across all8
  fine phases:0 introduced foreground-colour conflicts.
- All8 real Fuse scrolling phases pass on SRAM and read-only ROM.
- Extended8k-refresh traces check596816 SRAM/524592 ROM bytes:0 bitmap or
  foreground-colour motion errors. Historical r12 failure control still fails.
- Initial-world ownership, all3480 sprite cases per target,1160 background sprites,
  8996 restores and erasures,3840 spans, compiled cache, orb animation and IRQ
  contracts pass. Live joystick/audio, two music loops and death65 checks pass.
-46 title states, whole-screen Fuse captures and stable publication pass.
  Fuse flight retraces show no trails or path deaths.
- Read-only8k-refresh run:0 game ROM writes, all eight banks immutable.

Diagnostics: `build/diagnostics/terrain_groups_r21/fuse_terrain.png` is an actual
Fuse capture crop. `whole_level.png` and `group_comparison.png` are offline palette
previews. `instance_groups_r21.json` and `all_group_instances_r21.json` prove native
application, not merely authored palette tables. Versioned traces retain controls.

An initial implementation had a row-mask rotate off by one. The independent
world-position test caught it before publication; corrected and all checks rerun.
The observation script also needed the emulator's XL field and the ROM helper's
actual return point; these test-harness corrections are recorded here.

Rebuild: `python scripts/build_ecm_native.py`, `python scripts/build_rom_ecm.py`.
Publish only after checks: `python scripts/publish_rom_ecm_r21.py`.
Level one only; physical hardware untested;512KB cache remains staging-only.
