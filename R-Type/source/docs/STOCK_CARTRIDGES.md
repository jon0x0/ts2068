# Individual stock TS2068 cartridges: r162

[Download all eight cartridges](../build/cartridges/r162/RType_TS2068_64K_cartridges_r162.zip).

Use each level's **.bin** or identical **.rom** for PicoROM: exactly 65536 bytes,
eight ascending 8KB DOCK banks, no header. The **.dck** is the emulator version.
[Instructions](../build/cartridges/r162/README.txt) and
[manifest](../build/cartridges/r162/manifest.json) are included.

This consolidates the shooting, ship ghosting, missing-enemy, colour dictionary,
L1 boss shortcut, L4 orb erasure and respawn-font fixes after r148, plus restored
current actor captures across all eight levels, L2 painted-body/row-colour repair,
and L5 overlap composition. Gameplay/event scripts follow the r145 TAP source;
each cartridge is a self-contained level for the stock TS2068 with read-only ROM.

All seven moving bosses now have fractional artwork and two-pixel movement;
L1 is static. L4 uses immutable adjacent-row colour recipes, a bounded156-row
cache and ROM-backed font readers. The native HUD attribute rows stay reserved.
All384 direct/retained L4 phase cases,96 bank-window cases with a failing negative
control,256 actual constructor IRQ-return probes, native victory and two
post-death equipment-recovery cycles pass. L4 stress:240updates in11790emulated
refreshes against the unchanged12000-refresh limit; HUD paper errors0, ROM writes0.

Elapsed update cadence and some dynamic effects still differ from TAP. This is
software acceptance, not cycle/pixel equivalence or complete hardware acceptance.
The comparison report retains publish_ready=false for that broader milestone;
stock_component_package_ready and this package's acceptance matrix pass.

The complete final L4 suite and all eight source/data/RAM/audio contracts pass.
All eight cartridges include normal-black title/score/restoration fixes;
bright nonblack ECM pairs remain unchanged. See [r161 details](NORMAL_BLACK_R161.md).
Sixteen hash-bound early/boss actor/event/control comparisons pass. L7 paired
comparisons use the same explicit coarse-death shield in both builds. Separate
unmodified cold-start tests cover actual enemies and firing. L4 has a native
48-hit victory and two real death/equipment-recovery cycles. Stress tests use
player protection and do not establish all-boss victory or natural survival.
All256 computed interrupt targets are explicitly probed in emulation.

Physical hardware confirmation is still pending. Prior r148/r99/r100/r145
archives and the stable disk-release pointer remain unchanged.

| Level | Stored/derived frames | Native frame bytes, unpacked | Palette rows | RAM frame cache bytes |
|---|---:|---:|---:|---:|
| 1 | 157 | 12138 | 388 | 1597 |
| 2 | 166 | 15895 | 513 | 273 |
| 3 | 219 | 13591 | 291 | 236 |
| 4 | 215 | 47488 | 1939 | 1261 |
| 5 | 172 | 25657 | 911 | 1022 |
| 6 | 211 | 21613 | 395 | 258 |
| 7 | 181 | 18254 | 1048 | 443 |
| 8 | 161 | 16647 | 503 | 1997 |

Frame counts include shared effects and derived fractional variants. L4 reconstructs
these from base artwork and adjacent colour rows. Unpacked byte counts include
native cell headers/transparent markers; they are not ROM storage or RGB sizes.
Terrain dimensions are preserved. See individual acceptance.json files for scope.

Create another version without overwriting this archive:
`python scripts/release_stock_cartridges.py --version r162`.

Archive SHA256: `292725eb5e53efb1f6ce9003164094a2a23b06aeab336893f82308ec792a5c2f`.

The unpromoted r158 package is withdrawn because its L4 cache overwrote HUD
attributes. Use r162. r157 and earlier protected archives remain unchanged.

L4 twin-launcher poses52-54 now draw both rocket sides over orb-owned cells.
Original projectile collision ownership is restored after drawing. All72 pose,
flip and layering cases and263 launcher interrupt/guard cases pass.
[Before/after comparison](../build/cartridges/r162/launcher_comparison.png).

## Earlier releases and regression history
## Historical r148 release

[Download all eight](../build/cartridges/r148/RType_TS2068_64K_cartridges_r148.zip).
Each level contains an exact65536byte raw .bin, identical .rom, and ROM-only .dck.
Use the raw file for PicoROM; the DCK includes an emulator header.
[Instructions](../build/cartridges/r148/README.txt) and
[manifest](../build/cartridges/r148/manifest.json) accompany the files.

These are eight separate read-only cartridges using current r145 selected art,
per-level music/effects and the stock HOME compressed-cache renderer. Fine player
movement, independent shots, current title, native input, pause, music toggle,
L4 weapon recovery and single-cartridge completion/replay are integrated.
Boss event timing remains native. Expanded-memory bank-sized motion caches and
multi-level loading are separate features of the expanded-RAM edition.

| Level | Stored frames | Native frame bytes, unpacked | Palette bytes | RAM frame cache bytes |
|---|---:|---:|---:|---:|
| 1 | 160 | 15678 | 3104 | 1417 |
| 2 | 177 | 15147 | 2696 | 236 |
| 3 | 198 | 12045 | 2040 | 236 |
| 4 | 173 | 13041 | 3576 | 1057 |
| 5 | 102 | 9249 | 1184 | 887 |
| 6 | 109 | 7283 | 1304 | 236 |
| 7 | 133 | 8813 | 2408 | 300 |
| 8 | 102 | 11752 | 904 | 1437 |

Frame counts include shared effects; native frame bytes include per-cell headers
and transparent-cell markers, not RGB images. Terrain retains its current32x32
strip dimensions. All selected frames fit; lookup dedup and sparse deltas save
ROM space without resizing artwork.

All8 final software suites and release data/memory/audio contracts pass, as do
ZIP CRC, every archived SHA256, raw ROM/BIN identity and all-ROM DCK checks.
Each level includes the recorded acceptance coverage. Game-over tests seed a
qualifying score and simulate hit flags but use actual native deaths/respawns.
Boss stress uses invulnerability; L4 separately registers48real native hits and
victory, plus two equipment-loss/recollection/rear-fire cycles. All256computed
IRQ targets per level return in explicit-target emulator probes. Physical
hardware tests, all-boss victories and name-entry interaction are not claimed.

Build: `python scripts/release_stock_cartridges.py`.
This does not change `scripts/release_latest.py`, the r100 stable disk pointer,
or the archived r99/r100/r145 files.

Archive SHA256: `f0a0e6573317a3147197007678208eac0a8443ecfb741d9412161f4b9d552f77`.

## Hardware regression / shooting test

r148 L4 has user-reported hardware ghosting, music pacing, enemy/control problems and failed normal shooting. Previous software gates did not establish correct active-input hardware behavior. Do not treat r148 as a completed hardware-validated release. A missing normal-shot handoff is repaired in the internal builds; targeted L4 files are in `build/cartridges/r149_shooting_test`. This test does not claim to resolve the other reported issues. Original archives remain preserved.

## Shared gameplay requirement

Cartridge gameplay must preserve the current TAP game's rules: selected keyboard and simultaneous native joystick inputs, fire press/release and charge behavior, projectile stepping and damage, pickups, enemies, boss events and controls. Stock ROM banking, decompression and compact rendering are platform adapters; differences there do not authorize changes to gameplay rules. The current TAP/art development source for these cartridges is r145; stable r100 remains an unchanged archive.

T242 audit found stock gateway drift beyond the missing short-shot consumer: the TAP r145 gateway publishes the player on alternate interrupts and samples fire edges on alternate/busy interrupts. Stock had published every available interrupt and dropped busy-copy fire edges. Restored those scheduling decisions and added a reference-opcode-anchored schedule test plus keyboard/both-socket repeated-fire tests for all8levels. This is scoped scheduling/input parity, not proof of complete gameplay or hardware timing parity. Renderer, enemy/boss, audio cadence and live control behavior still require end-to-end review before another full release.

## r151 targeted hardware test

`build/cartridges/r151_ghost_enemy_test/rt_l4_r151_test.rom` fixes the reproduced ship-mask page-crossing error and title restoration resetting the initialized enemy-event pointer. All8 internal builds pass genuine menu-start enemy spawning and sustained four-direction movement/copy regressions. This remains a targeted L4 test; hardware confirmation and remaining audio/control/visual reports are pending.

## L1 collision-verified test

`build/cartridges/r152_l1_collision_test/rt_l1_r152_test.rom` exports the corrected current L1 cartridge after verification of the moving last walker following boss setup. Ordinary and held-fire pilots defeat it with eight native damage hits; captured-state missiles inflict three points in both directions. No health/armor changes. All8 actor ownership and selected native collision controls pass; this does not claim exhaustive boss/weapon or hardware coverage. Build/export script: `scripts/package_stock_l1_collision_test.py`.

## r153 color-refresh test

Use `build/cartridges/r153_colour_fix_test/rt_l4_r153_test.rom` for L4. This corrects compact palette IDs leaking into the legacy adjacent-cell/global color refresh and producing solid blocks. Current artwork is preserved. Exact old-file negative control detects7blocks; corrected live test detects0, and all8 shared renderer regressions pass. Per-level test ROMs/DCKs, checksums and static before/after/boss diagnostics are included in that folder and its ZIP. Build/export: `python scripts/package_stock_colour_test.py`. This remains a scoped hardware test, not a full release or hardware-confirmed result.

The r162 cleared-cell fix changes exactly16bytes per ROM from r161; all RAM
layouts and kernel entry addresses stay fixed. See [details](CLEARED_CELLS_R162.md).
