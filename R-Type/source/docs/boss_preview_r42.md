# Boss preview r42

During gameplay, press B, release, then press B again. Holding either press
does not repeat the action. The current stage restarts near its boss encounter;
it does not award a victory, advance to another stage or grant invulnerability.
Use title keys 1–8 to select a stage first. New games still begin normally.

The shortcut uses the native checkpoint and full ECM game initialization,
including retained bitmap clearing and reversal table rebuilding. It changes the
current-life checkpoint, so subsequent lives can retry that encounter. Starting
a new game restores the original stage start. Keyboard and joysticks remain active.

Level 3's giant ship and level 6's moving maze require their early setup scripts:
these previews restart at the encounter entrance rather than manufacturing a
partial boss at the end. Other entry columns are 99, 63, 74, 73, 61 and 32 for
levels 1, 2, 4, 5, 7 and 8 respectively. Native FEEB constructs eight map columns;
entry begins before the first event to avoid losing a phase-zero setup command.

The 84-byte helper occupies previously unused DOCK0 1FA3..1FF6. Four per-region
bytes at 0D71..0D74 contain the script pointer, checkpoint column and prior
native setting. FD4B stores the B-key edge state, outside loader metadata and
the music stack starting FD50. Only the cold shared-code source main-loop call
is patched; common HOME code survives cached level switches. No IRQ work added.
The ordinary released-key path adds approximately 107 Z80 T-states per gameplay
update. This is an instruction count, not a measured overall frame-rate result.

Artwork is unchanged from r41. User-selected Sierra Lite treatments and larger
sprite alternatives are separate pending work. Enlarging both sprite dimensions
can quadruple cell count and increases clipping, restoration and collision review
requirements; it should be done selectively, preserving gameplay readability.

Build: `python scripts/build_boss_preview.py`. Deterministic controller/CPU tests:
`verify_boss_preview.mjs`, `verify_boss_preview_progression.mjs`,
`verify_boss_preview_restart.mjs`, `verify_boss_preview_failures.mjs`.
Tests that bypass death are explicitly diagnostic, not hardware validation or
unassisted playthroughs. Physical testing remains pending.
