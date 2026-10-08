# Sinistar TS2068 port

The current playable cartridge is **v58**, with scrolling flight, mining,
Sinibombs, worker combat, Sinistar assembly/pursuit, speech, attract mode and
session high scores. See [port development notes](port/README.md) for the
revision history, measurements and remaining arcade adaptations. Physical
hardware validation is still outstanding.

**New browser player:** run `python -m http.server 8772 --bind 127.0.0.1`, then
open <http://127.0.0.1:8772/play/>. This self-contained player uses Josef's
October 4, 2026 TSRun, pinned separately from the existing emulator copies,
and includes the keyboard guide. See [player setup](play/README.md).

**Virtual D-pad comparison:** <http://127.0.0.1:8772/play-dpad/> uses a separate
copy of Berzerk's modified TSRun, with its circular D-pad, Fire and a Sinistar
bomb button. Full keyboard instructions remain visible below the game.
See [comparison setup](play-dpad/README.md).

For the earlier development viewer, run `python scripts/serve.py`, then open
<http://127.0.0.1:8768/port/mining-web/>. The cartridge is
`port/build/sinistar-mining.dck` (64 KiB payload plus a nine-byte DCK header).
The earlier scripted 60 Hz demo is documented below; its timing does not
describe the playable game.

## Build and verify the playable port

Initialize the pinned original-source submodule with
`git submodule update --init --recursive`. Install Python dependencies
`numpy`, `Pillow` and `scipy`; the Windows SjASMPlus executable is included
under `tools/`. Use a current Node.js runtime for the emulator tests.
The existing directory layout is required by the local server and tests:

```text
Timex/
  TSRun/
  cartridgeconversion/
    berserk/
    elite/
    sinistar/
```

```powershell
python port/scripts/build_mining.py
node port/scripts/verify_frontend.mjs
node port/scripts/verify_playable.mjs --fast
node port/scripts/verify_render_stress.mjs --fast
node port/ay-editor/verify.mjs
```

The build uses the checked-in fitted audio assets. Re-fitting audio requires
the separate speech2ay/Ayumi tools described in the port notes. Some historical
comparison tests also require local saved revisions, which are not checked in.

## Publishing and project organization

The `play/` and `play-dpad/` packages support static hosting, each with its own
local cartridge and pinned TSRun copy. Published players are linked from the
[TS2068 hub](https://jon0x0.github.io/ts2068/). The earlier development viewer
still uses the local server's `/tsrun/` route.

A shared ports repository can contain Sinistar and future ports' source while
linking to Berzerk's existing project and player. Retain the local directories
and existing publishing repositories. Preserve Berzerk's published
URL, <https://jon0x0.github.io/berzerk_ts2068/>, and its
`personalizations/berzerk/` entry path. No repository rename or directory move
is required to add the umbrella page. Import Sinistar's history under
`sinistar/` in a separately prepared umbrella checkout; the current development
checkout can stay in place. The umbrella repository destination has not yet
been configured.

## Earlier 60 Hz cartridge demo

**[Run the original 60 Hz demo on GitHub Pages](https://jon0x0.github.io/ts2068/arcade-ports/sinistar/web/).**
Click **Start with sound**. The `web/` package now includes its emulator and
assets and works with an ordinary static server. See [demo setup](web/README.md).

**Saved version:** `revisions/v3-60hz/WATCH.html` plays the accepted recording
offline. The frozen cartridge, source, and verification evidence are beside it,
with a complete `SHA256SUMS.json`. Live saved viewer:
<http://127.0.0.1:8768/revisions/v3-60hz/web/>.

**Original-source port:** development has started separately in `port/`.
See `port/README.md` for the translated movement kernel and validation.

Open <http://127.0.0.1:8768/web/> and click **Start with sound**. If necessary, start `python scripts/serve.py`. The viewer executes the actual Z80 cartridge in the local TSRun checkout.

The optimized demo updates once per TS2068 refresh: **60.1145 Hz**. MAME's Williams timing is 8 MHz / (512 × 260) = **60.0962 Hz**, so the target is effectively the original arcade display rate. See [MAME's Williams machine driver](https://github.com/mamedev/mame/blob/master/src/mame/williams/williams.cpp).

## What changed

- All eight horizontal pixel phases are precalculated for the original 49×52 Sinistar and all 32 original player-ship headings.
- Unrolled bitmap loops compute `old XOR new`, skip zero differences, and write the final byte. Loading the known final value avoids an unnecessary second XOR; the resulting changed-bit update is identical.
- Only changed color attributes are stored as sparse, absolute-address XOR operations. There is no full attribute scan.
- Star movement, visibility and exposed old sprite edges are also precomputed as sparse XOR operations. No visible erase pass is needed.
- Drawing is ordered to finish each affected region before the emulated display beam reads it. The verifier checks the actual raster as well as both display-RAM planes.
- The scripted 256-frame flight loop takes 4.26 seconds. Sinistar travels a wider, faster horizontal orbit; the player ship circles it with one-pixel positioning and 32 headings. Speech and mouth frames run on the same 60-Hz schedule.

This is an optimized **scripted demonstration**, not evidence that a complete interactive port will run at 60 Hz. The paths avoid sprite overlap, stars are clipped against sprite bounding rectangles, and the precomputed color/background changes depend on this exact sequence. Eighteen white stars use three horizontal depth rates. ECM still permits only two colors per 8×1 cell; original geometry is retained, with palette approximation and dithering. Hardware remains untested.

## Artifacts and verification

- `build/sinistar.dck`: all eight DOCK pages marked ROM; 65,545-byte container.
- `build/sinistar-picorom.bin`: 65,536-byte flat physical cartridge image.
- `build/sinistar-demo.mp4`: actual TSRun raster and emulated AY audio, recorded at 60.1145 fps.
- `build/runtime-report.json`: complete-screen, every-write, raster, timing, and AY-stream checks.
- `build/fuse-trace.txt`: native Fuse verification.
- `build/manifest.json`: ROM placement, audio provenance, and cartridge SHA-256.

The current TSRun run covers 2,264 completed updates and eight full loops. Every update takes exactly one video frame. Maximum rendering work is about 35,500 T-states, below the 58,688-T-state frame budget. Both halves of every displayed pixel match the independent compositor: zero raster mismatches, zero intermediate/unchanged display writes, zero ROM writes. AY ticks are exactly 58,688 T-states apart. Native Fuse independently passed 1,023 consecutive refresh intervals with one completed update per refresh and SP=$7FFF. These are emulator results, not a physical-hardware claim.

Accepted earlier builds are preserved in `revisions/v1/` and `revisions/v2/`.

## Rebuild

Python needs NumPy, Pillow and SciPy. SjASMPlus is under `tools/sjasmplus/`. Audio tooling and TSRun are the existing sibling checkouts.

```powershell
# Only needed when changing original graphics:
python scripts/prepare_assets.py
# Only needed when changing/re-fitting speech; uses local Cygwin GCC and Ayumi:
python scripts/prepare_speech.py
python scripts/build.py
& 'C:\Users\Jon\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' scripts/verify.mjs
python scripts/verify_fuse.py
```

`build.py` delegates to `build_fast.py`, which assembles `src/demo.asm`. `verify.mjs` runs `verify_fast.mjs`. Use `--record` to capture every emulated raster frame, then:

```powershell
ffmpeg -y -f rawvideo -pixel_format rgb24 -video_size 640x240 -framerate 60.114505148 -i build/capture.rgb -i build/emulated-audio.wav -ss 3 -t 30 -vf "scale=960:720:flags=neighbor" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart build/sinistar-demo.mp4
```

## Sources and sound

Original geometry, palette and mouth poses come from [synamaxmusic/sinistar](https://github.com/synamaxmusic/sinistar), preserving the [historical source](https://github.com/historicalsource/sinistar). Assembly inputs are under `references/`.

Complete archival voice WAVs come from [Sean Riddle's Williams sound archive](https://seanriddle.com/willy2.html). The cartridge uses the existing [speech2ay](https://github.com/jon0x0/speech2ay) harmonic player and conservative Ayumi fitting. It is an AY approximation, not PCM playback or the original speech hardware. The viewer's separate original-voice players provide a reference. Source hashes and fit metrics are in `assets/audio.json`.

Browser emulation uses [TSRun](https://github.com/josef-jelinek/TSRun). Original artwork and speech remain the property of their rights holders; no files were published or uploaded.
