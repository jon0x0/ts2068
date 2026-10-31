# Attribute Speed Lab

Separate native TS2068 cartridge experiment for TSRun. Insert `attribute-speed-lab.dck` and reset. Existing cartridges are preserved.

## Result

The cartridge performs back-to-back `LD (HL),A`, `LD (HL),B`, `LD (HL),C` writes to the same attribute address. Three disjoint ink/paper pairs are preloaded, so six distinct colors would be available if all three could appear during one cell. Writes are exactly 7 T-states apart. The test sweeps seven whole-T-state phases down the screen and repeats the experiment at three horizontal locations.

The unmodified pinned TSRun core produced a maximum of FOUR colors per 8x1 cell, not more: 188 target cells have four colors, and 247 have two. The cartridge was verified for 120 frames with 11,796,480 active display samples checked and no mismatches. Every one of the 1728 timed attribute writes per frame was checked for exact address, value and instruction-start timestamp.

An 8-pixel ECM cell spans only 4 T-states. Consequently two successive changes 7T apart cannot both fall within it. Preloading registers removes the value-reload overhead but cannot remove the opcode-fetch and memory-write cycles. Three color pairs would require at least two changes within that 4T window; eight distinct colors would require at least three, assuming attribute writes could affect an already-fetched cell at all.

Independent CPU probes also executed `PUSH BC` (11T) and `EX (SP),HL` (19T), confirming that their two writes target different adjacent addresses. PUSH's two write cycles are only 3T apart on the documented bus schedule, but they do not rewrite the same attribute. TSRun timestamps both callbacks at instruction start, so these probes do not measure their internal bus-cycle spacing.

This result is an emulator experiment. Even the observed four-color cells are not established as a physical TS2068 capability: the actual display fetches attributes with bitmap bytes and may retain them for a complete cell. Physical memory contention and write-cycle timing are not verified. This experiment does not modify the emulator to obtain extra colors.

References:

- Zilog Z80 CPU User Manual UM008011-0816, `LD (HL),r` (7T), `PUSH qq` (11T; 5,3,3 cycles), and `EX (SP),HL` (19T): https://www.zilog.com/docs/z80/um0080.pdf
- TS2068 Technical Reference Manual, section 2.1.8.3, printed p42, paired display-data/attribute fetches: https://device.report/m/3253f371946016a17699f910efcc842ff5b716271ea9c0ddad00e6ef439c547d

## Screen

The retained shaded sphere is a background. The three narrow colored test columns at ECM columns 8, 16 and 24 contain the timed-write experiments; other cells are ordinary ECM. The bottom label reports the measured maximum. The previous cartridge's midpoint divider is removed because this cartridge sweeps timing phases throughout its test region, rather than comparing upper/lower rendering methods.

## Rebuild

Install Python 3, Pillow and NumPy, plus Node.js for testing.

```
python build_speed.py
python fetch_tsrun.py
node test_speed.mjs
```

`scene.bin` contains only the 16KB display data; it contains no system ROM. `cartridge.py` is the shared cartridge builder source, included here so this archive is standalone. TSRun modules are fetched separately at pinned commit `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`.
