# Triangle-tone experiments based on50and59

User preferred50and59 and proposed triangle waves. Choices61/62 are software-only
linear triangle references mixed with the same Bnoise.63/64 use native repeated
AY amplitude envelope14 onA, tone/noise disabled onA;65/66gate that envelope with
noise;67/68use a lower octave. Bretains noise, musicC uses fixed amplitude and is
preserved. Native envelope is stepped/logarithmic, not an ideal linear triangle.
Peak amplitude is fixed when envelope is enabled, so original Avolume contour is
not independently reproduced; envelope is turned off as originaltonegetsquiet.
R13trigger occurs once,255sentinel meansskip. Subsequentpitchchanges useR11/12.

Primary General Instrument datasheet: https://map.grauw.nl/resources/sound/generalinstrument_ay-3-8910.pdf
It describes envelope shapes and envelope-only output with tone/noise disabled.
Full triangle cycle isclock/(512*period). Period16probe yields215HzinTSRun and
Ayumi, versus215.33/215.42expected from their modeledclocks. Nativepitchquantizes
at high frequencies; lower-octave options reduce quantization. Envelopegenerator
is shared; currentlevel1musicdoesnotuseit, butfuturemusicmayneedarbitration.

Eightunique nonzero solos andeightmusiccontexts; Cownership verified. Source50/59
hashesunchanged. These are previews, not integratedcartridgefiles. Nativeplayer
would needR11–13 support/reservation if an envelope choiceis selected. Software
references would need additional synthesis/DAC timing and are explicitly not
nativeAYwaveforms. Scripts build_death_triangle_trials.py/render_death_triangle_trials.mjs.
Files build/audio/death_triangle_trials:manifest,validation,envelope_frequency_validation,
numberedJSON/WAVs,index,timeline,combinedWAV. No cartridge soundselection changed.
