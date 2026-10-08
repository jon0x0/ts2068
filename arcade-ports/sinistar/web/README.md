# Original 60 Hz Sinistar demo

This directory is a static browser package for the accepted v3 scripted demo.
Serve the repository with any static HTTP server and open `web/`. The published
path is `https://jon0x0.github.io/ts2068/arcade-ports/sinistar/web/`.

The cartridge matches `revisions/v3-60hz/build/sinistar.dck` exactly. Assets,
TS2068 ROMs, shaders, emulator modules, audio worklet and the recorded video are
bundled here; no `/tsrun/` server alias or excluded build directory is required.
Click **Start with sound** to enable browser audio, or **Restart sequence** to
reset the cartridge. This is an autonomous demonstration, not the playable port.

The TSRun modules are an unmodified subset of upstream commit
`41dbe3e41c692a1806f2cb900c5a0faa1549ae77`, also pinned by `play/`.
`tsrun-version.json` records their hashes, the worklet hash and cartridge hash.
The worklet is beside the emulator page because upstream sound.js loads it
relative to the document. Attribution and ROM provenance are in `tsrun/README.md`
and `tsrun/roms/README.md`.

Set `TSRUN_ROOT` to this directory's `tsrun/` and run
`node scripts/verify_fast.mjs` from the repository root to check the bundled
emulator against the original build's reference graphics and sound stream.
The October 7, 2026 check verified 2,264 complete screens, 2,263 consecutive
single-refresh update intervals, and zero raster mismatches or ROM writes.
