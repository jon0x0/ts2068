R-TYPE TS2068 - individual64KB ECM cartridges - r161

Each level is a separate true read-only64KB cartridge for a stock TS2068.
Use rt_lN_r161.bin or the identical .rom for PicoROM: exactly65536raw bytes,
DOCK banks0 through7 in ascending8KB order, without a header.
The .dck is for emulation:9byte header plus the same ROM, all8banks marked ROM.
Do not program the DCK header into a cartridge. No writable cartridge RAM is used.

Start with keyboard or native joystick fire; both joystick sockets remain active
alongside the selected keyboard controls. ENTER defines the six gameplay keys.
P pauses (Shift-P if P is one of the selected keys); M toggles music.
Press B, release, then B to preview the boss. Collect the offered weapon pickups;
they are not granted automatically. L4 offers replacements after equipment loss.
On completion, fire replays this cartridge; reset with another cartridge to change
levels. This target does not use a disk loader or load-all/level-jump commands.

Includes restored current r145 actor captures across all levels, corrected L2
painted-body/row-colour paths, L5 overlap composition and per-level AY tracks/effects,
fine player movement, independently clocked shots, title delta animation,
animated score colours, pause, native input and normal black in ECM space.
Release r161 also fixes native title clears/delta edges, both score entry paths,
and flat legacy restoration. Bright black remains valid; black-paper pairs use
normal black. Bright pairs with two nonblack colours are preserved.
No emulator palette flattening is required.
Artwork expands from compressed ROM into a bounded HOME cache when needed.
All seven moving-boss ports L2/L3/L4/L5/L6/L7/L8 include fractional artwork
and two-pixel movement. L1 is static. L4 uses permanent adjacent-row colour
recipes, a bounded expanded-row cache and ROM-backed native font readers.
L4 twin-launcher poses now render in front of their dropped orbs; terrain and
other actors retain native occlusion, and projectile records are unchanged.
Event scripts are preserved. Elapsed world-update cadence differs from the TAP
version; the two editions are not cycle- or pixel-identical in live play.

Validation: all8 cold starts/firing; native direct/retained art comparisons;
8fine-scroll phases with pixel/colour checks; title, input, pause, music toggle;
actual deaths/respawns and five-life game-over-to-score flow; completion/replay;
all256computed IRQ targets per level and zero game writes to ROM.
Boss stress uses player invulnerability and does not prove every boss defeated.
Sixteen paired TAP/cartridge actor/event/control scenarios pass. The L7 paired
comparison has a shared coarse-death bypass and is not natural-survival proof.
L4 has a separate actual48-hit victory and two equipment-recovery tests.
Qualifying score and player-hit flags are seeded only in test fixtures.
IRQ probes explicitly inject computed targets in a fixed-FF emulator.
Physical PicoROM/PicoVideo hardware testing remains pending. Not all boss fights
or name-entry interactions were played through. See each acceptance.json.

The existing expanded-RAM r145 build and hardware-confirmed r99/r100 archives
are unchanged. This is the separate stock cartridge release, not a replacement
for the stable disk-release pointer. Create a new archive without overwriting this one:
python scripts/release_stock_cartridges.py --version r162
