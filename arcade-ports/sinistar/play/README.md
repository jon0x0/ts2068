# Sinistar browser player

Serve the Sinistar repository with `python -m http.server 8772 --bind 127.0.0.1`
and open <http://127.0.0.1:8772/play/>. The directory is a static deployment
package: the cartridge, emulator, ROMs, shaders and audio worklet are local.
It also works at `arcade-ports/sinistar/play/` in the TS2068 hub; there are no
root-relative asset URLs or dependencies on the older `/tsrun/` server route.

`tsrun/` is an unmodified copy of Josef Jelinek's upstream commit
`41dbe3e41c692a1806f2cb900c5a0faa1549ae77` (October 4, 2026), fetched October 7.
`tsrun-version.json` records every upstream file's SHA-256. The existing shared
TSRun checkout, Berzerk publishing copy and older Sinistar viewers are unchanged.
The wrapper uses upstream's documented `?url=` cartridge-loading feature and
its current host/audio scheduling, keyboard, rendering and emulator code.

To update the cartridge after a verified build, copy
`port/build/sinistar-mining.dck` to `play/assets/sinistar.dck` and run the player
verification. Upstream emulator updates should be explicit and pinned, followed
by the same cartridge and browser tests; never update another project's copy
as part of this procedure.

To exercise this emulator with the existing native regression scripts, set
`TSRUN_ROOT` to the absolute path of `play/tsrun`, then run
`verify_frontend.mjs`, `verify_playable.mjs --fast`,
`verify_render_stress.mjs --fast`, `verify_voices.mjs` and
`verify_gameplay_features.mjs` under `port/scripts/`. Without the environment
variable, those scripts continue to use the existing shared TSRun checkout.
