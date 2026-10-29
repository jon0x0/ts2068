# Public release, 29 October 2026

- Project: https://github.com/jon0x0/ts2068/tree/main/ZXDesk2068
- Pages: https://jon0x0.github.io/ts2068/ZXDesk2068/
- Normal-screen demo: https://jon0x0.github.io/ts2068/ZXDesk2068/?mode=normal#try
- High-resolution demo: https://jon0x0.github.io/ts2068/ZXDesk2068/?mode=hires#try
- Related project: https://jon0x0.github.io/TSWriter/

Both builds are the current development previews, not a new completed OS release.
TSPico filesystem 2.x integration and the Pico-based USB mouse/keyboard interface
are plans. No persistent storage adapter or new physical mouse driver is claimed.

The published page includes the original heading “Time for a 2068 Mouse Interface”
and discusses precise movement packets over the joystick connector, compatible
USB HID receivers, and the need for a driver, protocol and electrical design.

## Reproduce publication

Development remains in the original ZXDesk2068 workspace. `web/` owns the page,
styles and player wrapper. The wrapper leaves upstream TSRun unchanged and sends
ordinary keyboard events for its visible pointer-control buttons.

1. Build with `bash scripts/build.sh` (Pasmo on PATH or set `PASMO`).
2. Obtain TSRun from https://github.com/josef-jelinek/TSRun at
   `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`, the current upstream head when checked.
3. Run `node scripts/test_port.mjs PATH_TO_TSRUN zxdesk2068` and repeat with
   `zxdesk2068-512`. Modern Node is required. The original Spectrum target can
   also be checked against pinned ZXDesk upstream using `--check-spectrum`.
4. Run `python scripts/render_screen.py` and
   `python scripts/render_screen.py --hires --windows` (Pillow required).
5. Run `python scripts/publish_site.py --hub PATH_TO_HUB --tsrun PATH_TO_TSRUN`.
   This stages the explicitly selected project sources and matching tapes,
   generates the source ZIP and download hashes, and records every runtime file
   hash in `tsrun-version.json`. It does not commit or push.
6. Update the hub's `scripts/build_site.py` Applications entry and root README,
   run its generator, inspect the diff, commit, and push the hub's main branch.
   Existing GitHub Pages serves that branch's root.

The downloadable source ZIP includes both assembled builds and the project's
source, build/test scripts, page sources and notes. It excludes the third-party
emulator and ROMs; obtain the pinned TSRun checkout separately for tests or staging.
TSRun is hosted separately under the project's `tsrun/` directory with its
upstream README and ROM provenance retained. ZXDesk's MIT license does not
relicense third-party emulator code or ROMs.

Browser controls: click inside the embedded emulator and use plain arrow keys
for pointer movement, and Space to click or drag. The wrapper captures arrows
before TSRun's cursor-key mapping and sends emulated shifts plus Q/A/O/P.
Do not press Ctrl+Shift+Q: browsers may reserve it for quitting. The player link
opens this wrapper in another tab, retaining the safe mapping. Unmodified TSRun
opened directly does not include it. Fuse additionally supports Tab as the
combined shifts. On-page controls and Hold click remain available.
Switching versions discards volatile RAM state.

The arrow-key workaround is confined to the web wrapper. Space and other typing
keys pass through unchanged; the app source and TAP files are unchanged. On the
real TS2068, hold SHIFT + SYMBOL SHIFT with the arrow-marked keys
(5 left, 6 down, 7 up, 8 right), or Q/A/O/P, to move,
Space for the existing pointer button, or either joystick and its fire button.
