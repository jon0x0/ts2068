# Relocatable object deltas and R-Type update measurements

## Future expansion and TS2068 AI skill candidate

User requested this follow-up on 2026-11-04. Expand relocatable object deltas as a reusable TS2068 game-rendering technique and consider including the validated approach in a future TS2068 AI skill update. This records future work; the skill has not been updated.

- Generalize cached transitions across movement, pose changes, animation, spawning, removal, diagonal motion and clipping.
- Combine local damage tracking, background restoration and priority-correct overlap composition with paired bitmap/ECM publication. Specify when direct XOR is valid.
- Resolve shared 8x1 colour pairs after composition, including scrolling backgrounds; masks alone are insufficient.
- Compare sparse records, XOR runs, compiled transitions and ordinary phase caches using end-to-end game timings.
- Budget templates, bank access and fallbacks separately for the read-only 64KB cartridge and full 512KB RAM targets.
- Validate matching pixel collision/projectile origins, IRQ/stack/bank safety and physical hardware before presenting a proven gameplay recipe.

Include reproducible native code/tests in the eventual skill reference. Preserve current evidence limits: 6,072 native publication tests and 32.74% fewer matched player publication cycles; full-game integration remains pending.

## Result

TSVideoCodec's useful contribution is sparse/skip-literal publication of an already composed image. Offline precomputation avoids finding the differences on the Z80. Full-screen comparison on the machine is counterproductive for this sample.

Actual native r44 boss updates150..210 were captured consecutively at the completed-frame868C point. Sixty adjacent pairs were encoded with the existing TSVideoCodec encoder, imported read-only from ../../TSVideoCodec/src/encoder. All240 native Z80 replay cases reproduce both6144-byte planes exactly.

| Publisher | Mean Z80 cycles | Mean visible byte writes |
|---|---:|---:|
| Two raw LDIR planes |258088|12288|
| Scan both planes, write differences |801186|1629|
| Pre-encoded TSVideoCodec XOR runs |151459|1920|
| Pre-encoded absolute sparse writes |117410|1629|

These are decoder/publication costs, not whole-game frame times. Offline encoding, composition, game logic, IRQ work and bank access are excluded. The sample has about25 boss parts,179.6 dirty8x8 cells per transition and only4.93 unchanged draw commands on average. It is inappropriate to infer that most boss parts can simply be skipped.

## Relocatable paired-plane publisher

src/relocatable_delta.asm is an actual Z80 routine. Input A is the minimum raster Y, C is the left byte column, and HL points at a cached local transition. Nine row groups contain a byte count followed by column/bitmap-XOR/attribute-XOR records. The routine builds nine native Spectrum-layout row addresses, so placement works across8- and64-line boundaries. It never scans the full display.

verify_relocatable_delta.mjs checks6072 placements/transitions,3 actual player poses,8 horizontal phases and8 move directions. Both output planes match exactly. Every bitmap write preserves bits shared by the old/new images. Native destination-address preparation is included. The matched64 centre-pose transitions average7036.90625 cycles versus10461.90625 for the existing QAOP dirty-window publisher:32.74% fewer publication cycles. All192 expanded templates require20280 bytes; centre-pose cardinal transitions alone require3120. This is a real storage tradeoff, particularly for the stock64KB cartridge.

This is a publication benchmark on a black background, not a new game or a replacement movement TAP. It does not establish correct arbitrary-background overlap. Sprite-relative XOR may only be used directly when its backdrop/composition assumptions hold. For normal gameplay, invalidate the union of old/new coverage, restore the retained scene into local scratch, compose intersecting objects in priority order, choose legal8x1 pairs, and publish final changes once. Moving or removing one object must not erase another object. Pair masks alone cannot solve ECM colour conflicts.

The recommended integration is local damage tracking plus cached phases/transition templates, with separate layout budgets for stock cartridge and expanded RAM. Fixed title motion and invariant animation transitions are particularly suitable for pre-encoded relocatable streams. Precomputed full-screen videos are not interchangeable with interactive gameplay or damage-dependent boss arrangements.

## Native Bellmite compositor experiment

build/fullgame/bellmite_compositor_r45 is UNRELEASED. The approved H planned-edge cels are packed exactly, with dedicated source colour rows rather than quantization into the old127-row dictionary. The selected96x96 core remains.

The first candidate exposed unsafe banked interrupt visibility and a retained-bitmap address error; both were corrected before publication. A test counter also initially treated DOCK4 instructions at8B06 as main-loop entries. Native counters now require bit4 unmapped. Earlier misleading counts were rejected. A completed-image diagnostic using an incorrect flash-bank read showed white rectangles; the flash value is now captured before switching banks.

With corrected bank-aware checks, the current candidate completes700 actual boss updates, preserves executable DOCK0 and reversal data, and reaches the expected checkpoint. Latest run41089 emulator refreshes including startup, versus43731 before replacing tile-index repeated division with exact modular multiplication. This is still substantially slower than r44 (14912 for its older art/compositor). Retaining the front shared-cell palette can also flatten/recolour the rear piece. Therefore this candidate has NOT been packaged as a new playable release and has NOT passed full cross-level regression or hardware validation.

Full-game one-pixel movement, pixel collision/weapon origins, IRQ-safe scheduling and retained-background integration remain unfinished. The approved QAOP/native-joystick controls and smooth differential movement direction remain requirements; standalone tests are not completion.

## Reproduce

1. node scripts/capture_delta_benchmark.mjs
2. python scripts/benchmark_delta_encoding.py
3. Assemble src/delta_benchmark.asm and src/relocatable_delta.asm with SjASMPlus into build/diagnostics/delta_benchmark/.
4. node scripts/verify_delta_benchmark.mjs
5. node scripts/benchmark_existing_player_publish.mjs
6. node scripts/verify_relocatable_delta.mjs

No TSVideoCodec, Sinistar, Elite, speech2ay, original arcade or Spectrum archive was changed. Measurements are deterministic emulation, not physical-machine timings.


## Gameplay integration follow-up (r48, 2026-11-04)

The512KB disk game now implements background-aware one-pixel player updates, a local world backing patch and changed-byte bitmap/ECM publication. This is distinct from applying pre-encoded XOR transitions over an arbitrary scene: dynamic overlap needs correct background composition. The pre-encoded relocatable method is included as a separate native QAOP/joystick movement trial, with the earlier differential baseline for comparison. See docs/r48_changes.md and TEST_HISTORY107-110 for evidence, memory ownership and remaining limitations. The future AI-skill expansion note remains open; no skill files were changed.


## R50 follow-up: arbitrary boss states

See docs/r50_changes.md. A fixed-pose native Bellmite comparison now exists, but the recommended gameplay design is the separate independent-part damage/composition prototype, which allows arbitrary arrangements from the start. Its native publisher passes100 changing scene cases; composition and encoding remain host-side. Do not call this integrated gameplay acceleration. Future AI-skill work must preserve this distinction and the corrected title/player memory ownership contract.
