# Twenty more variants based on preferred14

2026-11-02. User selected original choice14 as the basis and requested20more
variants aiming at the arcade's explosive attack, tone shifts and noise.
Choices21–40 are new; original14 is an unmodified reference outside the count.
Open build/audio/death_14_variants/index.html. Solo/music modes, playall, shortlist,
original14solo/music references, originalarcade53 reference and combinedWAV/timeline.

All variants retain14's deep imported-tone / noise-gatedA and noisyB foundation.
Each specifies its parameters in numbered JSON.21–24attack,25–28arcade-tone blend,
29–32tone stages,33–36noise evolution,37–40balanced hybrids. They vary attack width,
doublecrack, decay/time scaling, continuous or stepped noise colour, gated low
body, downward tone, upper-to-lower transition and shrapnel texture. They are not
merely volume variations. Arcade PCM is analyzed in50mswindows at50Hz for RMS,
continuity-weighted low spectral peak, upper peak, centroid and flatness. Spectral
peak tracks guide blends with14's tone; they do not establish recovered FM notes
or perceptual fidelity. Human audition decides the next preferred direction.

Scripts build_death_14_variants.py/render_death_14_variants.mjs. Analysis and source
hashes inarcade_features.json/manifest.json.20unique register streams, all distinct
from first20;20unique non-silent soloPCM hashes and20music renders validated.
All useA/B, reserveC for identical backgroundmusic; borrowed voices restore after
theeffect. SameTSRunAYmodel/22050HzPCM/50Hzcurves, separately peak-normalized.
No final gamegain claim or hardware listening claim. Source14 and firstsetWAVs,
coin43/99, cartridges anddefault effect remain unchanged. Old audition pages link
to thenewset. Details inTEST_HISTORY051.
