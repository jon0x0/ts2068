# CP/M 2.2 release and build notes

Release: **cpm22-v0.1.0**. Repository path: `jon0x0/ts2068/CPM_2.2_2068`.
Pages entry: <https://jon0x0.github.io/ts2068/CPM_2.2_2068/>.

This is a CP/M 2.2 release, not CP/M 3.x. Source is MIT except attributed
third-party material with its own notices. Digital Research's clarified CP/M
grant is in third_party/cpm22/LICENSE.txt. Public cartridges use font8x8's
public-domain basic Latin font. The requested Infocom collection is distributed
as a separate attributed disk image; game stories/interpreters are not covered
by the project's MIT license. TS2068 ROMs are not included in the downloads.

The hosted player references the hub's already-published, pinned TSRun snapshot
and ROMs; it does not introduce a second emulator fork. TSRun is Josef Jelinek's
project, credited in the page. Its upstream source remains independently owned.

## Rebuild

Install Python 3.10+ and sjasmplus 1.20.3 or a compatible release. With sjasmplus
on PATH, run from CPM_2.2_2068:

```text
python tools/build.py --profile oliger --oliger-kb 160 --assembler sjasmplus
python tools/build.py --profile oliger --oliger-kb 320 --assembler sjasmplus
python tools/build_dual.py --assembler sjasmplus
```

Without --rom these use the public font. An optional private --rom path retains
the original ROM-font build workflow. The public bundle excludes those private
ROM-derived outputs. `build/` is generated; do not rebuild over a working disk.

Downloadable images were assembled from the included CCP/BDOS/BIOS source,
generic pinned Digital Research utility binaries and local examples. SHA256SUMS
identifies the public artifacts. The source includes the Python preparation and
disk conversion tools; tests use Node and an appropriate TSRun checkout. Existing
test scripts default to the historical ../../TSRun layout; the browser adapter
test also accepts TSRUN_PATH.

## Validation and remaining hardware checks

Publication checks for this release passed 61 Python tests, native SRAM screen
preservation/failed-readback checks, TSPico v1.00 and v2.x saved-disk round trips,
160/320KB browser-adapter boot/copy/execute/export/reload, console palette and
64/80-column register contracts, TSPico v2.x SD/game LOOK smoke tests, and static
documentation/download checksum checks. The actual Pages-style browser preview
booted CP/M and Planetfall using the hub's runtime.

Native Z80 tests cover bank safety, saved-disk reload, malformed/incomplete saves,
both transport families, geometry, screen preservation and console mode behavior.
The browser adapter tests boot/copy/run/export/reload 160/320KB media. Original
1.00 hardware has booted and run the games in 64 columns. Its observed PicoVideo
V4 display corruption is explained in the video notes. TSPico v2.x service and
PicoVideo 4.2 test results are primarily source/model evidence, not blanket
certification for every firmware or physical board.

When reporting a problem, include release/tag, target/emulator, firmware GETINFO,
VIDEO output, image size, cartridge filename/slot, full diagnostic screen and
whether a saved disk existed. Preserve that disk rather than erasing it to
make the loader fall back. The 320KB browser/Oliger BIOS supports A: and B: with matching disk geometry;
physical two-drive hardware remains unverified. No CP/M 3.x support is claimed.
