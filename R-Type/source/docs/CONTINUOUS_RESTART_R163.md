# Resident-level replay r163

The stock cartridge/browser retained the Spectrum post-game-over restart at
92A4. For levels other than1, the conditional jump at92B3 fell through,
wrote level0, and called FE03. FE26 then drew REWIND SIDE2 and entered the
obsolete tape-loading sequence. Level3 was affected, as were other later levels.

Change the single common-code opcode at92B3 from CA (JP Z,8634) to C3
(JP8634). Each cartridge now takes the same resident title restart that level1
already used, preserving its own level number. This changes neither collision,
artwork, animation, input nor audio logic. Compressed HOME images are repacked;
raw ROM differences consequently are not limited to one byte.

The r162 L3 failing control reaches FE26. The fixed native92A4 path reaches
title8634 and ordinary joystick fire starts active gameplay for all eight
cartridges. The test compares common HOME8400..BFFF against the r162 cartridge:
only92B3 differs. Existing death/game-over tests cover the preceding flow up
to the score screen; the new targeted test covers post-score replay. It does
not automate complete high-score name entry or claim physical hardware testing.

The r161 TAP already redirects its native loader calls to the resident disk
handler. Current-disk L3 and L8 restart tests use an instruction boundary on
the main stack, delayed transport replies and cached level reuse. No FE03 tape
entries; selected level restarts. Earlier exploratory probes that jumped from
an arbitrary frame endpoint corrupted bank/stack context and were discarded.
No TAP code or archive change is needed for this reproduced prompt.

Each physical64KB cartridge still contains one level. On completion it offers
replay/reset; automatic cross-level play belongs to the full disk edition or
browser level switching. This fix removes the obsolete tape request, and does
not imply that a physical cartridge can automatically insert another one.
