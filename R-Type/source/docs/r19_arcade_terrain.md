# r19: arcade-guided warmer terrain and buildings

2026-11-02. Current terrain samples come from arcade frame2400 platform and
pillar crops. Black-paper fitting previously absorbed the beige/bronze surfaces
into almost all black/white with two yellow scanlines. r19 adds an arcade profile
with warm-metal row palettes: silver/white, yellow/gold and red/copper hints.
The TS2068 has no native brown; these are constrained metal-tone approximations.

The fitter ignores black holes/sky when deriving robust surface colour. It uses
moderate chroma emphasis and vertical chroma-error diffusion, instead of allowing
black/white coverage to remove nearly every warm hue. Candidate inks stay in the
warm/neutral family. The first16row choices mirror to32rows. Both arcade material
templates and every horizontal column share each scanline pair; compatibility
with vertical flips and fine-scroll joins is therefore retained. Quantization
is performed once. Black paper remains black; no coloured sky rectangles added.
Native tile envelopes and solid flags are retained. The four forward row tokens
and four reverse tokens fit the existing128-byte resident palette allocation.
No renderer code or RAM allocation is added. Asset pixels/colour rows change.

Both earlier preserve/chroma profiles remain generated for comparison. Default
RTYPE_ART_PROFILE is nowarcade; explicitpreserve/chroma selects oldstyles. Atlas,
materialsourcePNG, activeprofilemetadata andpalette/patch hashes are retained.
arcade_terrain_colour.py andbuild_live_art.py reproduce this profile. The sound
engine/default, titlefix and allaudition choices remain unchanged. Triangle trials
61–68 based on preferred50/59 are separate, documented indeath_triangle_trials.md.

Evidence: terrain_colour_r19/arcade_before_after.png compares arcade reference
and actualFusegroundcapturesr18/r19; colour_coverage.json measures asset warmth.
All8Fuse scrollphases pass onboth. Extended8000refresh motionchecks601040SRAM/
529632ROMbytes with0bitmap/colourmotionmismatches. The richer palette remains
attached to moving pixels, including materialjoins. ROMall8banksimmutable,
0gameROMwrites; fulltitle90states/off-logobackgroundclean. Other regressions in
r19_final_checks. Levelone only; physicalhardwareuntested. Arbitrary per-cell
horizontal hues still require a different compositor; this revision respects
the compatible row-colour constraint rather than reintroducing clash.
