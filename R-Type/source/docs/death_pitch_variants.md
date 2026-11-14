# Choices41–60:33noise,37contour and arcade-guided pitch

2026-11-02. User requested20additional choices, using33asbasis,37noise/loudness
components, and the arcade's up/down tone movement. Audition at
build/audio/death_pitch_variants/index.html. References33/37andoriginalarcade are
outside the20newchoices. Solo/music modes, sequential playback, shortlist and
combinedWAV/timeline remain available. No default cartridge effect is selected.

41–44test a measured pitch guide;45–48vary contour depth/timing;49–52vary attack,
noise/loudness/gatedbody;53–60are real speech2ay/Ayumi optimized versions of
41,42,45,46,49,50,51,52 respectively. Some choices use a clearA tone overBnoise;
others retain33's tone/noise gate. All effects useA/B, reservingCformusic.

Arcade PCM analysis:64mswindow/20mshop; whitened harmonic spectral salience on
75–1800Hzloggrid and dynamic-programming continuity. Both rises andfalls are
allowed, with10rises/29falls above.02octave across56activeframes. Threeframe
log-smoothing is a separate option. This is spectral guidance in noisy FM audio,
not a claim of exact FM-note recovery. Noise sweep derives from33; envelope and
noise body blend37withtheactualPCM RMS. No arbitrary monotonic falling ramp is
substituted for the measured shape.

Optimization uses the maintained speech2ay search.Simulator/score_components
and stateful Ayumi worker at882samples/tick (50Hz). Candidate comparisons start
from identical chip/filter state, then commit selected state. Noise period,
boundedvolume and Bgate are fitted against arcadePCM.53–56lockA pitch exactly;
57–60allow2%period movement plus register quantization. Objective includes
spectrum, weighted periodicity androughness; noise waveform phase is not forced.
All8mean selected objective scores improve against their seed evaluated within
the selected history. These scores do not establish subjective listening quality.

Reproduce scripts/build_death_pitch_variants.py, then
scripts/optimize_death_pitch_variants.py, then currentNode runtime with
scripts/render_death_pitch_variants.mjs. Script1creates41–52and resets themanifest;
script2adds53–60. Analysis,parametercurves,source/toolhashes,optimizationevidence,
40WAVs,page andvalidation are retained in thenewfolder. Renderer sums all3AY
outputs,22050HzPCM,50Hzregisters, independentpeak normalization. Musiccontext
uses sameexcerpt, startsFXat.3sec, preservesC andrestoresborrowedvoices.

All20register/audio streams are distinctfromeachother and allprior40. Parent
33/37hashes andr18cartridgehashes unchanged. Previewonly, nohardwarelisteningclaim.
