# Source and emulator provenance

Digital Research CCP/BDOS source is vendored unmodified in `third_party/cpm22`:

- Repository: https://github.com/brouhaha/cpm22
- Commit: `01018abbccce0bdf4874b0b2ed1a048c5fcc2987`
- Redistribution grant: `third_party/cpm22/LICENSE.txt`, including the clarified
  2022 grant for use, redistribution and modification of CP/M and derivatives.
- The original source includes CP/M V2.2 BDOS Patch 01. The Python translator
  makes 8080-to-Z80 syntax changes for sjasmplus and places CCP at D000 and BDOS
  at D800. Its generated files stay in build/. Sources are the build authority.

TSRun local checkout: `../../TSRun`, base commit
`3cfca24b184ebe6106f8e88f9edd94a660dfc68d`. Local modifications may exist;
the tested source hashes, rather than the base commit alone, identify the core:

| File | SHA-256 |
| --- | --- |
| machine.js | 0779183741d082a14464d6a6ae0aeed8aa471d80705faf3d113cc68e7386ba24 |
| dock.js | f9af8105d8e7e44c900387dd62aa46b8fbc44dbd8e25884d35f3211da0767483 |
| z80.js | c11b6deba8b2e20af6f8e4c21b059b87a70a084d7c210df767ae179f8b3ca44b |

`dock.js:parseDck` confirms page types and payload sizes. `machine.js:memRead`,
`memWrite`, and `applyDckBlock` implement writable DOCK/EXROM mapping. The test
imports this actual machine and boots the supplied original ROMs from reset.

Fuse Windows binaries independently tested:

| Version | Executable SHA-256 |
| --- | --- |
| 1.10.0 | 241e4bffed88886d1f7c2c42b03a98ceca23eae0b93beead08b7d9bed79e4658 |
| community 1.9.1 Oliger build | aae787e51d5930a5a09857c91cc51b17d97fee28f74f4eacd02509c960e2dfda |

The community executable is installed under
`C:/apps/emulation/Fuse-JLODiskEmulation/fuse-1.9.1-win32`. Its Oliger controller
is not used by this image. Its exact source revision is not established by a
binary version; do not infer one. Fuse/libspectrum upstream behavior from the
handoff has now also been exercised by actual cartridge boots.

Build assembler: sjasmplus 1.20.3; Node test runtime: 24.19.0; Python: 3.10.6.
The extracted assembler directory retains its upstream license. Fonts are
derived from the user's ROM and generated artifacts should not be redistributed
as a clean-room font implementation. No third-party ROM binaries are vendored.

The preloaded utilities now come from the pinned Digital Research distribution
archive in third_party/cpm22-utilities.zip. See third_party/CPM_UTILITIES_NOTICE.md
for its source, hash and redistribution basis. Utilities are vendored binaries;
the CCP, BDOS, BIOS and cartridge loader continue to build from source.
