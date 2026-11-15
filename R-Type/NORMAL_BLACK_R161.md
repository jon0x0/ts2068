# r161: normal black in intended space and paper

Bright black is treated as a valid TS2068 colour. The game must choose normal
black for space, transparent sprite edges, erased cells and black text paper.
This fixes game output, not the emulator palette. Bit6 affects both colours of
an 8x1 pair: choosing normal black also selects normal foreground intensity in
that pair. Bright pairs with two nonblack colours remain unchanged.

## Producers fixed

- Stock cartridges: inherited r24 title fill and HOME FC80 delta helper, final
  logo attribute pairs, native initial black-paper fill, and native score cycle.
- Stock title-attract and post-death score entries: prepare the native animated
  attributes before exposing standard video. They are separate gateways.
- Both targets: keep ECM active during the title initializer's native attribute
  copy, instead of exposing its temporary 8x8 plane.
- TAP: fix native initial black-paper fill and score constants in both the CORE
  cold-load image and each LEVEL/START region. L7 preparation text also uses
  normal-black paper.
- Stock restoration: the legacy flat fallback could restore bright cyan on
  black after an actor disappeared. A fixed ROM0 helper at0F50 clears BRIGHT
  only if a decoded colour endpoint is black. All256 inputs and preserved
  registers are tested. It occupies existing padding below0F80; caches and all
  subsequent entry addresses stay fixed. No encoded palette IDs are normalized.

No new RAM buffers, artwork scaling or gameplay/collision changes. L5 IM2/UI
reservations stay intact. Original input archives, reference projects, old
releases and stable r99/r100 latest pointer remain unchanged.

## Verification

The live audit reads bitmap plus actual display attributes with normal black
and bright black distinct, including partially updated frames. It begins at
native cold-launch readiness for TAP / first ECM activation for cartridges;
secondary hidden-loader mode and pre-title ROM-unpacking workspace are outside
that display audit. It uses keyboard/joystick inputs, not game-memory patches.
Title, repeated score cycles, gameplay and respawn/preparation paths are covered
for all eight levels. Before/after image: build/normal_black_audit/before_after.png.

The TAP audit,14cold/cached transitions, coldL1/L5 firing, projectile collision
positive/negative controls and L5 boss160updates/all256vectors pass. Actual IRQ
return probes cover0/255; remaining targets are identical. Stock checks include
all-eight component suites, attribute fallback cases, ROM/RAM/data/audio contracts
and16paired early/boss scenarios. Final manifests bind evidence to image hashes.
These are scripted emulation checks, not hardware confirmation or full all-boss
playthroughs. Browser TSRun retains its published palette/core; BW stays optional.

## Rebuild

TAP: scripts/build_normal_black_r161.py overlays the preserved r145 regions and
CORE using asserted typed instruction locations, regenerates LEVEL/START TAPs,
and verifies all20TAP checksums/reconstructions. Use RTYPE_DISK_TEST_DIR to direct
the existing fixture to build/fullgame/normal_black_r161; the default staysr145.
Run the normal-black audits and transition/cold/collision/vector checks, then
scripts/finalize_normal_black_r161.py.

Cartridges: scripts/validate_stock_integration.py; scripts/refresh_stock_paired.py;
scripts/release_stock_cartridges.py --validated --version r161. Existing archives
are protected. Use a new identifier for any later build.
