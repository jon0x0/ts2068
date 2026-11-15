# r162: coloured blocks beside the moving/firing player

The r161 browser cartridge could leave solid cyan/green paper beside the ship
after firing and movement. The fault is in the compact cartridge renderer,
not the emulator palette or ECM fetch latch.

Native clear marker3 denotes a cleared/unowned cell in this pipeline, just as
in the player backing-cache code. The native bitmap can be erased while its
compact dictionary tag remains. `stock_restore` incorrectly treated every
nonzero marker as a live background and restored that stale two-nonblack
palette. Zero bitmap bits then displayed coloured paper. Trace: original ROM1
line22A7/store22A9, e.g. row325=[29,29,29,01,01,01,01,01]hex; blank pixels
became cyan. This affects legal multicolour pairs, unrelated to bright black.

The fix sends native0/3 through empty-background restoration; native1/2 keep
the original shaded palette exactly. A12-byte dispatch in unused ROM0 F70..F7B
replaces the original4-byte dispatch with CALL/NOP. It discards only its own
return when tail-calling the existing legacy restorer. All registers, outer
stack/IRQ contracts, kernel sizes/entry addresses and RAM layouts are preserved.
No new RAM, full-screen scan, palette flattening or graphics simplification.
A trial that grew the kernel8bytes failed L2's2400 endpoint assertion; it was
rejected, not released. The final uses existing padding belowF80.

## Reproduction and verification

Actual published TSRun core with the archived r161 L1 ROM, cold boot and only
movement/fire inputs:1551frames,229frames with stray paper cells, max5near the
ship. Corrected cartridge: same sequence,0badframes. No game-memory patches in
this natural test. `verify_player_natural_r162.mjs`; actual-RAM/CPU negative
control `verify_player_clear_r162.mjs` proves0/3clear while1/2retain exact rows.

Diagnostics in build/player_paper_r162: before_after.png, paper_3.png and
paper_5.png reproduce cyan strips/blocks. paper_4.png contains nonzero textured
pixels and was not accepted as proof of empty-space corruption. charge_case.png
and green_case.png are legitimate charged-shot/player colours caught by an
initial overly broad green-pixel search; not evidence of this bug. Short
stationary shots alone did not reproduce it. The reliable case combines firing
and movement. CPU/RAM equality under original vs held fetch-latch emulators
also showed that the reproduced stale paper is game data.

The fix applies to all eight stock cartridges/browser levels. Full eight-level
component/IRQ/RAM/audio checks and16TAP/cart early/boss parity scenarios are
required before packaging. The expanded-RAM disk uses a different retained
colour plane; its current r161 archive is unchanged, not relabelled as r162.
Hardware confirmation and natural all-boss playthroughs remain separate.
