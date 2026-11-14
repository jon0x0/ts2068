# Current release: r100 (2026-11-08)

r100 promotes the user-confirmed working r99 baseline. Only same-length
version/info text differs; executable behavior and graphics are preserved.

- Download: ../build/releases/r100/RType_TS2068_r100.zip
- Latest copy: ../build/releases/RType_TS2068_latest.zip
- Machine-readable pointer: ../build/releases/latest.json
- Manifest and checksums: ../build/releases/r100/
- Install: replace complete rtype directory, reset, launch rtype/rt.tap.
- Startup text: R100 PREPARING.

The user confirmed r99 was working again after the reported L5 startup,
fire and boss-entry failures. Do not generalize that to all-level hardware
coverage or claim a measured hardware interrupt vector. r100 repeats early
L1/L5 startup and firing tests in emulation with unmodified gameplay.
All level/START tape reconstruction and checksums, version-only identity,
L5 full interrupt page, both startup gateways and ZIP CRC are verified.

## Build and regression requirements

Run python scripts/release_latest.py to build, test and package r100.
The promotion builder verifies the archived r99 SHA256 before using it.
The finalizer rejects gameplay or asset changes beyond fixed-length labels.
Keep the r99 archive unchanged. Develop future gameplay/art changes against
that baseline separately, with explicit review of changed memory ranges.

- Reserve L5 DOCK4:8F00..8FFF exclusively for the temporary IM2 table.
- Address9000 is its temporary final high byte; existing helper sets/restores it.
- Relocated keyboard bridge:8B30..8B61; PAUSED font:8B70..8B9F.
- Compositor live variables through8B21 and row scratch8BF0..8BFF stay intact.
- Current UI assembly: src/l5_ui_release.asm. Do not restore r65's overlapping
  8F10/8F40 font/key placements when rebuilding old conversion stages.
- Both cold00D4 and runtime0DC0 gateways must target the actual warmup symbol.
- Test level selection DURING initial loading, plus cached level switching.
- Reserve all256 interrupt entries; a fixed FF emulator vector is insufficient.
- Separate no-bypass startup/fire coverage from stress tests bypassing game-over.

## Targets

This is the complete eight-level disk/512KB release. The stock64KB read-only
cartridge target is preserved separately and unchanged; this archive does not
claim that all eight levels fit in a stock64KB cartridge. Reference projects
and original arcade/Spectrum ZIPs remain untouched.

## Separate stock cartridge release

Individual64KB read-only cartridges: [r160](STOCK_CARTRIDGES.md).
Create another version with `python scripts/release_stock_cartridges.py --version r161`. The r100 disk
release and its latest pointer above remain unchanged.
