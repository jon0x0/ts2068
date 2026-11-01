# Publication validation — November 1, 2026

- Published DCK is byte-for-byte identical to the archived final G4M example-with-menu image.
- DCK header: bank 0, ROM chunks at $8000, $A000 and $C000. Total: 24,585 bytes.
- Raw 24 KB ROM equals the DCK payload. The supplied 32 KB EPROM image starts with that payload.
- SHA256SUMS.txt records all three download hashes.
- TSRun snapshot is isolated from other players, based on upstream commit 41dbe3e41c692a1806f2cb900c5a0faa1549ae77 as already published in this hub. Runtime files match its provenance manifest.
- Browser check: cartridge fetched automatically, loading screen displayed, and VU-3D reached its Create a new figure / Load a data file menu.
- Hub and catalog generated successfully with eleven cartridges. Local release/player links checked.

The original thread reports Fuse testing, including the Shade fix. This publication does not claim exhaustive application or physical cartridge testing. Original conversion source was not recovered; original binary artifacts are preserved unchanged.
