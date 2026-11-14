# r13: colour motion is a separate contract

The marked building and ground defects were caused by independently chosen source
8x1 pairs. A destination cell can contain pixels from two source cells during fine
scrolling. r12 selected one whole palette, so even correctly moving bitmap bits
changed apparent colour/brightness. The r12 tests verified that choice was copied
correctly; they did not prove that it preserved source colour while moving.

build_live_art.py now jointly fits each32-pixel scanline across the two original
arcade texture crops and both vertical mirrors. Identical pairs across all four
columns and materials remain compatible at horizontal joins. Mirror symmetry keeps
the native vertically flipped32x32 tiles compatible too. A global row fit is a
constraint on the source artwork, not per-frame requantization. Black remains paper;
the texture is quantized once, and native fine scrolling shifts those same bits.
Vertical scanline colour variation and arcade-derived interior detail remain.
Some per-cell horizontal hues are intentionally sacrificed to avoid false motion.
Both palette-preserving and chroma-emphasized output styles are still generated.
The palette symmetry is asserted by the asset compiler.

trace_terrain_motion.mjs compares consecutive actual game updates. For unchanged
terrain ownership, expected byte=(previousByte<<1 | previousRight>>7)&255. Each
foreground pixel's previous colour must move with its source bit. All eight phases
are represented. Actors, ownership changes, sky, staging31 and unrelated rows are
excluded; this is not a general raster-tearing test. Normal2600refresh runs reproduce
r12's5587 colour changes on18016 checked bytes and zero bitmap errors. Final r13
SRAM18304/ROM18016 byte checks have no pixel or foreground-colour errors.

The extended8000refresh diagnostic sets HOME91F2 to RET after handoff to bypass
ship death and reach more terrain. This mutation exists only in the test machine;
the shipping binary is unchanged. r12 shows171245 colour errors/493856 bytes.
The first row-only r13 candidate reduced this to4704 SRAM/2398 ROM errors but
failed at later material joins. Sharing rows across materials and mirrors resolves
the remaining changes: final SRAM540240 and ROM436456 checked bytes, zero errors.
Separate normal runtime validation runs the immutable cartridge without the bypass.

Reports, actual CPU RAM frames and slowed120ms/update GIFs are in
build/diagnostics/terrain_motion_r13. The GIFs illustrate consecutive game updates;
their playback rate is authored, not a performance measurement. r12 artwork and
first r13 palette/atlas are archived there for diagnosis. Publication requires the
exact cartridge hash in the successful extended motion report in addition to the
existing true-ROM, sprite, background, title, orb, art and Fuse phase gates.

The source palette change adds no new runtime code. Renderer sizes remain1496
SRAM/1530 ROM bytes. Mixed-colour work is reduced but no new speed claim is made.
Level-one coverage and physical hardware limitations remain as documented.
