# Per-level disk build r33

Use `build/fullgame/per_level_r33/RType_TS2068_per_level_r33.zip`.
Put the complete RTYPE directory anywhere below TAP, navigate into it, and load
RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP through LEVEL08.TAP beside it.
The loader never changes the current directory. Requires512KB expansion RAM;
this is a disk build, not a64KB read-only cartridge.

Startup reads only the level-one boot region (eight8192-byte CODE pages), then
the normal title runs. Keys1-8 select a starting level, Fire/keyboard0 starts,
and M toggles music. Missing levels load on selection or stage transition,
showing LOADING LEVEL n, the filename, and PAGE00..07. Each level file currently
contains one64KB initialized runtime region; asset-only compression and idle
title prefetch are not part of this build. Previously played levels are read
fresh, avoiding treating their mutated rendering buffers as pristine assets.

## Implementation

`scripts/build_demand_disk.py` derives from the preserved r32 image and r27
initialized level-one runtime snapshot. RTBOOT retains cold-boot source chunks;
LEVEL01 uses initialized metadata/cache chunks for a warm handoff. Confusing
those two representations would lose the original boot code or source caches.

Physical RAM region0 holds the current level. Region7 holds a resident
loader (exact size in manifest), saved native workspace, and common-code backup.
Other regions are reserved for later caching, not claimed as active cache.
The actual loader executes at HOME6000 with interrupts disabled. Native
8000..BFFF code is saved before those chunks become disk buffers. Temporary
copy gateways at5E00/7800 avoid their own mapped chunks; a third8-byte gateway
temporarily replaces F900, with the original bytes saved at D3E0 and restored
before returning. The original native stack remains live. At completion the
native metadata, per-level payload, compiled ship and row cache are installed,
SFX/music ownership resets, and the native caller resumes through a stable
5E00 tail. No Spectrum tape-ROM call is used.

Every CODE block is XOR checked. Each RAM write is read back and checked, then
all eight pages receive a second verification sweep. A partial/failed region
is never executed. Error screen steps:01 mount,02 CODE header,03 payload,
04 write,05 readback,06 final verification,07 bank selection. E0 is timeout,
E1 malformed header, E2 checksum/readback mismatch. Firmware status03 on step01
means the requested file could not be opened in the reviewed interface.

## Validation and limits

Run `python scripts/validate_demand_disk.py` to build and run all gates.
The actual Z80 packet model starts in a nested current directory, forbids cd
commands, delays replies, and requires eight read cycles after bank selection.
Startup reads only RTBOOT (16 header/data blocks). All eight native stages,
ending/restart, selected starts1/3/8, and game-over replays pass. Assertions
compare common code, the temporary audio helper, stack and native metadata
before/after each disk handoff. CRC corruption, aliased RAM, timeout and missing
file negative controls halt with the expected diagnostic. All72 distributed
asset pages reconstruct the exact source regions; ZIP payload checksums pass.
Victory/death bypasses are diagnostic and do not establish normal difficulty.

The loading-level3 and missing-file screens were rendered from actual HOME RAM
and inspected. Physical loading remains unconfirmed. The prior intermittent
hardware timeout and level3 life-loss corruption are not claimed fixed by
these model tests. No firmware modification, idle-title prefetch, new artwork
or64KB ROM update is included. r32 remains preserved.
