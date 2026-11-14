# r17: coherent moving title and noise-led death explosion

2026-11-02. r16's per-letter palettes were incompatible while six silhouettes
overlapped. Its regression checked the designed OR composite, which did not
establish that the overlapping image looked acceptable. User feedback supersedes
that visual assumption.

The swept cluster is now precomputed once from the same accepted glyph artwork.
Two bitmap phases (0/4pixels,624bytes) support four-pixel movement rather than
r16's16-pixel sweep. The cluster shares one white/cyan vertical colour division,
so letters do not fight over8x1 attributes. During the eight-pixel spread phase,
each letter recovers its source colours only after the moving cluster clears it.
The final E restores its source colours when it reaches its final position.
Offscreen composition and paired-row publication remain; this is not a hardware
page flip or a physical tearing guarantee. Ninety exact motion states are checked
against an independent per-pixel source compositor on both targets.

## Death sound

Yes: the native death event11 at9201 was the 2019 death hook and is mapped to
arcade command53 in this port. The old effect11 and arcade53 are different sounds
for the same gameplay event. The old sample remains in the A/B page as a reference.

r17 fits arcade53's original PCM as an explosion, using the maintained speech2ay
stateful Ayumi simulator. It searches noise period and volume, then a second
noise voice with optional tone gating, penalizing unwanted periodicity. It does
not use speech pitch as the death sound's defining component. Both voices use
the AY's one shared noise generator; B's tone gate supplies distinct texture,
not independent random noise. All56frames (1.12sec) keepA noise active;42frames
use tone-gated B in the selected fit. Objective scores are not listening-quality
claims. The final fitted waveform and native frame outputs are supplied to audition.

Death temporarily borrowsA+B and leaves musicC's registers and note progression
untouched. Ordinary effects continue borrowing onlyA; B resumes the current
music state after death. Death priority still blocks incoming gunshot requests.
The native effect format now permitsBperiod andBvolume deltas for death only.
Coin99,43 and all other non-death source curves remain byte-for-byte identical
to r16. The comparison page retains their existing audition files.

The fitter is scripts/fit_death_noise_r17.py; it reads the preserved r16 effect
reference only as a baseline, never rewrites those accepted effects. Raw fitted
frames and Ayumi previews live in build/audio/death_noise_r17. The build packs
those exact50Hz frames. scripts/build_title_sweep.py regenerates the atlas from
the current accepted source art. Existing build scripts produce r17 variants;
publication remains gated on exact-hash emulator and sound/motion regressions.

Level one only; physical hardware untested. All previews are modeled audio or
captured emulator RAM. This revision makes no new512KB consumer claim.
