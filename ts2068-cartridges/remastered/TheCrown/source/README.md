# The Crown — cartridge source package

Original game by Brian Walker, ©1983 Games to Learn By, Inc.
Recovery and cartridge remaster by jon0x0. This is the source snapshot for
the October 14, 2026 release of **TheCrown.dck**.

## BASIC and native source

- [Original recovered TS2068 BASIC](original/TheCrown.bas), including the loader and game segments.
- [Final Leap BASIC](leap/TheCrown.leap.bas), exactly as compiled for this release.
- [Intermediate converted BASIC](leap/converted.leap.bas), before the cartridge adaptations.
- [Native dungeon initializer](assets/intro/native_initializer.asm).
- [Native startup, animation and input routines](assets/intro/combined_native.asm).
- [Conversion profile](conversions/crown_level1.json) and [native adaptation script](scripts/native_crown_init.py).

All three original levels, their character sets, and the recovered original TAP
are included. The historic `crown_level1.json` filename covers all three levels.
The cartridge incorporates the Leap v2 bytecode runtime; it runs with stock
TS2068 HOME ROM and EXROM. No Leap ROM installation or level tape is required.

The animation's locked PNG poses and native ECM planes are build inputs under
`inputs/intro-locked`. They preserve the released animation without requiring
an image generator or video encoder installation. The included TSVideoCodec
modules clean, polish and encode these inputs during the build. The build
creates preview images locally; the public release page remains static.

## Rebuild

The provided driver follows the release's **Windows + WSL** toolchain. It has
not been adapted to native Linux or macOS. Install Windows Python 3.10 or later,
Node.js 18 or later, WSL with Python 3, GCC, G++, and Make, and a Windows Fuse
emulator with TS2068 support. Install Python dependencies in your environment:

```powershell
python -m pip install -r requirements.txt
$env:CROWN_NODE = 'C:\path\to\node.exe'  # optional if node is on PATH
$env:FUSE_EXE = 'C:\path\to\fuse.exe'    # optional if fuse is on PATH
python build_source.py
```

Run from the extracted source directory. Paths should be accessible to WSL.
The driver checks source hashes, builds the included SjASMPlus and ZX0 sources,
prepares the pinned Leap compiler/runtime, converts the recovered BASIC,
compiles bytecode with the emulated Leap compiler, assembles the cartridge,
and runs the TSRun and Fuse verification scripts. Finally it checks that the
regenerated Leap BASIC matches the included release listing and that the DCK
matches this exact release hash:

```
481a5ada28700ce312b5b8388008195701a523da671f7a0fefe7f835a31540cd
```

Outputs are in `build/crown-combined/program.dck` and `program.bin`.
The verification checks startup, key gating, animation decoding, replay and
three-level gameplay in emulators. Physical hardware testing remains outstanding.
Intermediate build manifests contain paths to the machine performing the build.

## Dependencies and rights

[DEPENDENCIES.json](DEPENDENCIES.json) records upstream origins and revisions;
[SHA256SUMS](SHA256SUMS) records the exact included file bytes. Dependencies
are bundled as source so no Git clones are needed during the build. Leap,
SjASMPlus and ZX0 retain their included licenses and notices. Stock TS2068 ROMs
are included for emulator verification; see their provenance in
`tools/tsrun/roms/README.md`.

The original game, artwork, recovered tape and third-party components retain
their respective rights. This package does not assign a blanket open-source
license to the original game or to dependencies without an explicit license.
The browser player is published separately in the release's `play/` directory.
