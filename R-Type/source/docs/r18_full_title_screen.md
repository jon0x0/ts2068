# r18: initialize the whole ECM title display

2026-11-02. The user screenshot showed coloured ghost text/stripes outside the
moving title. This was reproducible from the saved r17 CPU RAM. Its bitmap outside
the48-line logo band was already zero, but4604of4608outside attribute bytes were
not47, with207distinct values. Those stale workspace bytes became visible PAPER
colours as soon as mode2was selected. The moving glyph compositor was not writing
those regions. Previous cropped previews/tests missed the full-screen corruption.

At title-animation entry, r18 disables the periodic interrupt source, selects
mode0 and a mapping exposing both HOME display planes. It clears all6144bitmap
bytes and initializes all6144ECM colour bytes to47 before enabling mode2. The
initial loading artwork is untouched before this title transition. Mode shadow
is set once while the actual metadata bank is mapped. Earlier per-step stores at
3FF0underSRAMmapping9 had addressed HOME ROM, not the DOCK1mode shadow; those
ignored stores are removed. The read-only target's shadow remains writable HOME
BE00. Bitmap/colour ownership and native game workspace remain separate.

Every one of90motion states on both targets now checks all off-logo bitmap bytes
are zero, off-logo attributes47, actual mode2, correct native mode shadow, and
exact source-derived logo pixels/colours. Final title and SRAM source restoration
are checked separately. A scripted Fuse probe captures the same mid-sweep x148
position on both targets: mode2and zero off-logo pixel/colour mismatches. New
publication gates require this evidence at the exact output hash.

Captures: build/diagnostics/title_screen_r18/r17_full_sweep.png andr17_control.json;
fuse_{sram,rom}_mid_sweep.png, fuse_validation.json, audio_unchanged.json,
full_screen_motion.gif. Full90-frame RAM captures/validation remain in
title_motion_r18. Fuse rawlogs/commands/RAM/JSON/PNG are probe_1_title_screen_r18
in each target folder. They are whole-screen previews, not cropped substitutes.

No sound selection changed. All20death auditions, accepted coin/43 curves and
r17audio code/data remain unchanged. This is a title initialization fix. The
normal build scripts produce r18; publish_rom_ecm_r18.py requires the full-screen
gates in addition to gameplay/render/audio checks. Level one; hardware untested.
