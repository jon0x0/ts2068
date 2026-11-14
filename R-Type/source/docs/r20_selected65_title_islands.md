# r20: selected death65, faster title and independent terrain colour groups

The SRAM and read-only64KB cartridges both use selected audition65 from
`build/audio/death_triangle_trials/65.json`. The death event remains11 (arcade53).
The packed death records retain the existing eight fields and add three envelope
bytes. A ROM0 helper at0BC0 writes R11/R12 and writes R13 only for a real shape;
255 means skip. Shape14 is written exactly once per death. A/B supply the triangle
and explosion noise; C continues music. The current music does not use the shared
envelope. Future envelope-based music must respect this shared resource.
Silent trailing audition frames are trimmed as before;56 active playback ticks.
The allocator reserves0BC0–0BFF before placing music and effect data.

Title: sweep248→0 now steps8 pixels; spread0→208 steps16. This reduces90 states
to46, preserves the final logo and coherent overlap colours, and keeps the full
screen initialization fromr18. Measured on both targets at3.528MHz: sweep4.303→
2.240sec; spread4.315→2.152sec between publication timestamps. These are timing
measurements, not an increase in gameplay frame rate. Larger motion steps trade
some intermediate positions for a shorter animation. Preview:
`build/diagnostics/title_screen_r20/full_screen_motion.gif`.

Terrain: `scripts/terrain_islands.py` analyses the native map stream offline,
including H/V mirrors and the final arcade-derived bitmap interiors. Source cells
are connected if consecutive foreground pixels have at most8 black pixels between
them on any scanline. Reused source cells conservatively connect their instances;
unchanged native cells anchor their components to the original arrangement.
Six independent populated components remain. Selected components use a second
warm-metal vertical arrangement (three-scanline shift, with symmetric mirrors).
Bit3 selects the second palette bank; the existing128-byte resident cache already
has room for both arrangements and their reversed rows. No game RAM or frame-time
work is added. This conservatively reuses styles rather than assigning a unique
palette to every building instance. Black paper, bitmap geometry and collision
flags remain intact. Preserve/chroma alternatives remain available.

Validation: all46 whole-screen title states match independent expected pixels and
colours on both targets; mid-sweep Fuse captures contain no stray screen data.
All21 sound slots match packed reference curves; dedicated65 tests confirm exactly
one shape14 write and no writes to music C or joystick R14/R15. Two music loops,
live joystick/audio, IRQ register/banking contracts and music/effect mixing pass.
The map-level proof checks738812 occupied8×1 cells across8 phases with0 introduced
foreground colour conflicts. Fuse also passes all8 actual scrolling phases.
Extended8k-refresh traces:599312 SRAM/528192 ROM bytes,0 bitmap or colour motion
errors. Initial-world ownership, complete sprites, restoration, orb animation,
compiled ship cache and keyboard selection pass. The8k-refresh read-only run has
0 game ROM writes; all eight cartridge banks are immutable. Legacy r12/r13 failure
controls still detect their historical defects; these expected failures are kept.

Diagnostics: `build/diagnostics/terrain_islands_r20/terrain_atlas.png`,
`build/diagnostics/terrain_motion_r20/trace_extended_detail.json`,
`build/audio/selected65_validation_r20.json` and versioned title/audio reports.
Build: `python scripts/build_ecm_native.py`, `python scripts/build_rom_ecm.py`;
publication: `python scripts/publish_rom_ecm_r20.py` requires matching checks.
Versioned r20 verification scripts sit beside their r19 controls. Scope remains
level one, physical hardware untested,512KB assets still staging-only.
