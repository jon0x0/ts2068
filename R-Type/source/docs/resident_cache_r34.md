# Eight resident level banks, r34

Package: build/fullgame/cached_levels_r34/RType_TS2068_cached_levels_r34.zip.
Replace the complete RTYPE directory; keep the launcher and companion files from
the same build. Place it anywhere under TAP, navigate into it and load RTFULL.TAP.

Each level retains its own physical64KB RAM region,0..7 for levels1..8. Files are
read only on first use. Cache-valid bits survive deaths, continues and new games
within the running session; a fresh launcher initializes a new cache session.
No cache eviction is required for eight levels. Startup still loads only level1.

To fit both all eight levels and the loader into512KB, only inactive levels'
mutable rendering/workspace chunks2/3 are used as scratch. Their code, artwork,
music and dictionary/cache-table chunks0/1/4/5/6/7 remain resident. Chunk1 has
owned mode-shadow fields reset by initialization. When a level is activated,
its render plane is cleared, compiled ship code republished, and native common
workspace/score state transferred from the departing game. Scratch bytes are
never treated as fresh assets. Holder and backup regions exclude the destination.

The runtime loader resides in an inactive region's chunk2. If the destination
contains that loader, it is relocated using RAM before that region becomes
active. This case involves extra bank operations but no file read. Other cache
hits take the short native bank handoff. Each image has a readiness tag at0D70;
the identical polling helper at0D80 waits for the target tag after selector
priming, replacing the old fixed guard on the short path. It is a bounded check,
not a claim of zero latency on untested hardware. A temporary black alternate
frame hides the native workspace bounce during the switch.

Persistent fields FD48/FD49/FD4A hold resident slot/current slot/valid bits. These
are after IRQ exit code ending FD48 exclusive and before music stack FD50. The
cold-boot source stamps them too, because the native bootstrap copies high RAM.
Do not move them into FD20: that is executable interrupt entry code. The cached
handoff is stored in unused compiled-ship padding FBE0..FCFF; the actual ship code
is169bytes and ends before that reservation. Orb code ends before D40; the cache
helpers occupy D40 onward without replacing its executed instructions.

Reproduce with python scripts/validate_cached_disk.py. The validation executes
actual Z80 code and disk/banking packets with delayed replies and selectors.
All eight levels load once, then a second circuit revisits every level without
any further file mount/read. All eight valid bits remain set. Native code and
workspace assertions pass15 handoffs. Selected3/8 game-over restarts mount only
RTBOOT and their selected file, despite returning through level1. Delayed-selector
tests require more than eight priming reads, exercising the readiness poll.
CRC, RAM alias, missing reply and missing-file controls halt with diagnostics.
All72 distributed asset pages reconstruct the exact manifest region hashes.

Physical confirmation remains pending. Idle-title prefetch is not implemented.
This release changes caching and render-buffer initialization, not the level2
creature artwork. Its reported emergence corruption remains open: direct and
background clipping tests match source data, but the reported real display
sequence has not been reproduced. The level3 hardware life-loss report also
remains open. No64KB ROM or firmware update is included.
