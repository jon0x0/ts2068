# SCLD Display Lab

A curated gallery of TS2068 display experiments, with a minimal TSRun player:

**https://jon0x0.github.io/ts2068/demos/SCLD/** — available after this change is published to `main`.

Click an entry to replace the running cartridge without reloading the page. Related variants share one entry. The player prefetches the small cartridges, creates a fresh emulated machine on selection, and updates the explanation and download links alongside it. Left/Right selects the previous/next experiment. Restart reloads the current cartridge; Pause stops the emulator. Where available, Space or the on-screen button invokes the cartridge's own comparison/pause control. Fullscreen retains the sharp display.

These are native Z80 cartridge programs running in the browser, **not videos or host-drawn approximations**. The player uses an isolated, unmodified TSRun core from commit `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`, by Josef Jelinek. It deliberately omits the newer emulator desk UI. A plain Canvas renderer displays the native palette-index buffer with CRT effects disabled, nearest-neighbor scaling and doubled scanline height. It needs no system ROM download for the selected self-booting DCKs.

## Curated list

| Family | What it demonstrates | Variants |
|---|---|---|
| Split Personality Evolution | Looping vertical, diagonal, sine-wave and four-quadrant ECM/high-resolution boundaries, with synchronized borders | Complete cartridge sequence |
| Triple Personality Mosaic | High-resolution, ECM and standard 8×8 attributes on every scanline; ten regions per line | Three-mode mosaic |
| Split Personality | ECM left / high-resolution right, distinct borders, scanline color strips | Static split |
| Four-screen Resolution Wipe | Stationary ECM pictures and prepared 512-pixel typography/3D images; random-direction scanline reveals | Complete four-image sequence |
| Timex Color Atlas | All eight border colors, native high-resolution color pairs and sixteen ECM palette entries | Atlas |
| Dynamic ECM · Macaw | Image-specific attribute replacements and adapted dithering | Sierra Lite, Sierra Line, two-row Sierra, nine independent replacements |
| Dynamic ECM · Blue Morpho | Image conversion and the palette independence/coverage tradeoff | Seven independent / eight shared updates |
| Dynamic ECM · Prismatic Orbit | Bayer-dithered smooth-color artwork optimized for a seven-position engine | Prismatic Orbit |
| Ten-position Color Prover | Exactly four colors in ten targeted cells on 64 test lines | Ten-position diagnostic |
| Attribute Race Lab | Ordinary two-color ECM above a divider, selected four-color cells below | Five-position comparison |
| Attribute Speed Lab | Seven-phase sweep of back-to-back 7T writes | Three-register test |
| Dynamic ECM Instruction Probes | Single-change sweep, adjacent-address burst and dense triple | STORE16, PUSH, EXCHANGE |

Twelve entries contain eighteen distinct cartridge binaries. The older five-position butterfly, superseded revisions, duplicate output copies, separate DOCK-only probe bootstraps and alternate packaging of the same images are not additional gallery entries. The seven/eight-position butterfly variants are retained because their independence/coverage tradeoff is materially different. Dither and instruction variants remain inside their families.

## Downloads

- [All 18 curated cartridges](downloads/SCLD-cartridges.zip)
- [Cartridge sources, player and recorded checks](downloads/SCLD-sources.zip)
- [Complete 21-TAP portability archive](downloads/TS2068-display-tricks-TAPs.zip), including some earlier experiments omitted from the cartridge gallery
- [TAP guide](downloads/TS2068-TAP-guide.md)
- [Pico Evolution requirements](downloads/Split-Personality-Evolution-Pico-TAP.md)
- [Exact artifact checksums](SHA256SUMS.txt)

Individual DCK/TAP links follow the selected variant in the gallery. The two pair-wise reveal TAPs adapt the four-image cartridge sequence to standard RAM. Standard-RAM Evolution is slower than the cartridge. Its `pico` TAP is an expanded-memory hardware test build requiring supported TS-Pico 2.x firmware and SRAM slots 2–15, which it overwrites; the browser player does not emulate that TSPico arrangement. See the supplied requirements before running it.

## Interpretation and compatibility

The mode-mixing demos perform real port-FF mode changes and timed border writes. Their exact physical timing still needs hardware confirmation. The Dynamic ECM experiments additionally rely on TSRun's instruction-start memory-write timestamps and lazy raster updates. The real SCLD may latch an attribute for a whole byte, and contention can change timing. **The extra colors in those emulator cells do not establish a new physical graphics mode.** Targeted cells may gain a second pair; the whole image does not become four colors per 8×1 cell.

Most DCKs use emulator-supported HOME preloading and additional DOCK/EXROM blocks. They are not conventional EPROM-ready DOCK cartridges. Physical loader variants, when present, remain in the source snapshot; the TAP collection is the separately tested RAM-loading route. Keep the distinctions in the original project notes.

The macaw and Prismatic Orbit source scenes were generated artwork, not photographs of observed subjects. The Blue Morpho and frog inputs are the user-supplied ECM/image assets. Prepared fonts include DejaVu Sans and extracted Timex 8×8 glyphs; attribution and source notes remain with their projects. There is no blanket license over third-party material. TSRun attribution and exact source hashes are recorded in [player/tsrun-version.json](player/tsrun-version.json).

## Serve, test and maintain

From the repository root:

```sh
python3 -m http.server 8772 --bind 127.0.0.1
# Open http://127.0.0.1:8772/demos/SCLD/
```

No npm install, server backend or frontend build step is required. Browsers must serve ES modules over HTTP; `file://` will not work.

```sh
node demos/SCLD/tools/check-gallery.mjs
python3 demos/SCLD/tools/package.py
python3 scripts/build_site.py
```

The native gallery check verifies the pinned emulator hashes, rejects identical cartridge binaries, boots every variant without system ROMs and tests both Space comparison transitions where provided. It produces [validation/gallery-native.json](validation/gallery-native.json). Original project test results are preserved inside `source/`. The real-browser checks in `validation/gallery-browser.json` cover all variants, rapid switching, deep links, keyboard navigation, pause/resume, fullscreen, nearest-neighbor rendering, local links, mobile overflow and failed-fetch recovery. The page was inspected at desktop and mobile sizes. Recorded emulator/browser results are not hardware results.

For optional browser QA, install Playwright as a development tool, serve the repository root and run `node demos/SCLD/tools/check-browser.cjs`. Set `CHROME_EXECUTABLE` to use an existing Chromium binary; `SCLD_URL` can target a preview or the published Pages URL. No browser dependency is shipped to site visitors.

`catalog.json` owns the entries and descriptions. `gallery.js`, `gallery.css` and `player/emulator.js` own the minimal player. Source snapshots retain the original relative paths and build instructions; some builders need Python/Pillow/NumPy and their supplied font/image assets. The gallery modules and downloadable binaries do not depend on those build tools.

GitHub Pages already serves the main branch root. Publishing these files and the regenerated hub index adds the new URL without replacing other emulator snapshots, changing existing Pages entry points, or altering unrelated projects.
