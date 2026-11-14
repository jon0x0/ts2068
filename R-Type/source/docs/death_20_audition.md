# Twenty death-effect audition choices

2026-11-02. Requested alternatives, not a new cartridge default. Open
`build/audio/death_20/index.html`; the existing comparison page links there too.
20 numbered cards have effect-only and identical-music-context modes, sequential
play-all, stop and temporary shortlist controls. Source references do not count
toward the20. All20solo WAVs also appear in one combined WAV with a JSONtimeline.

Groups:1–4imported2019effect11;5–8arcade-derived;9–12designedexplosions;
13–16hybrids;17–20noise plus tone. The imported effect original and currentr17
fit remain numbered baselines, alongside18other variations. Maximum2effect
channels, Creserved; single-channel choices leave musicB/C. The AY has one shared
noise source; tone gating and different volume curves create the added texture.

All previews use the same local TSRun AY model,22050HzPCM and50Hzregisterframes,
sum all3outputs, and are peak-normalized independently. Solo comparisons are
for character, not final in-game gain. Music mode starts the effect at0.3sec,
preserves C (and B for single-channel effects), then restores borrowed voices.
This is an offline register-composition preview, not cartridge integration or
hardware listening evidence. Final selection may need game-specific gain tuning.

Reproduce: python scripts/build_death_20.py, then the currentNode runtime on
scripts/render_death_20.mjs. manifest.json records names, descriptions, source
hashes, channel counts and register hashes; each numbered JSON stores all11
sound-register curves. validation.json checks20unique, non-silent solo renders,
20context renders, local assets, register ranges and music voice ownership.
Cartridge hashes remain unchanged. Coin99,43 and title/game builds are untouched.
