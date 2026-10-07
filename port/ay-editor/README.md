# Sinistar AY sound editor

Open `http://127.0.0.1:8768/port/ay-editor/` with the existing `scripts/serve.py` server. The default is **05 · Slow fall**, selected by the user. The other nine +6–10% fits, the original-pitch optimizer, v28 noise fit, and −30% fit are available as starting sounds.

Choose a curve, then draw or drag a straight line. A selection can be set numerically or by dragging in Select time range mode. Playback loops that selection; edits replace the preview at its current time with a short crossfade. Automatic audition after drawing can be disabled. Undo/redo tracks gestures, and Reset sound restores the selected starting version. Compare using Hear starting version.

Controls cover all-channel relative tone pitch, individual tone frequencies, AY volumes, noise period, each channel's tone/noise routing, and shared hardware envelope period/shape. Volume 16 selects the envelope; 0–15 are fixed logarithmic AY levels. Noise period and envelope are shared chip resources. Both tone and noise disabled is a constant output level, not a mute. Envelope shape −1 is the stream's 255 sentinel: do not write/restart R13 on this frame. Other shapes write R13 and retrigger it.

The original optimizer parameters are retained verbatim. The All voices pitch curve changes tone dividers only; hardware-envelope and noise pitch have their own controls. The plot is an editor for register settings, not the original audio's spectral pitch. Noise periods use the chip's 1–31 range. Settings update once per 58,688 CPU T-states, approximately 60.1145 Hz.

The worker uses an unchanged copy of local TSRun's `ay.js`, with the game emulator's 3.528 MHz CPU timing, 1.764 MHz AY clock, amplifier RC filter, and integrated sampling at 44.1 kHz. A 20 Hz DC blocker is applied to the mixed output. This preview can differ from earlier Ayumi optimizer renders. The monitor gain only changes listening volume; WAV output uses the renderer's fixed scale without per-edit normalization.

Projects save editable frames, pitch curve, starting frames and selection in versioned JSON. Browser autosave restores the latest session. Download a project file to preserve a version independently of browser storage. WAV export includes the whole sample. AY export is **raw 14-register bytes per frame**, with 255 meaning skip R13, not the ZXAYEMUL file format. It may require changes to the cartridge's compressed format/player to integrate arbitrary envelope/routing choices. No cartridge assets are modified by this editor.

Validation: `node port/ay-editor/verify.mjs` checks every preset's unedited export, render finiteness and length, WAV headers, frequency shifts, volume, noise, silence, envelope progression and the R13 sentinel. Browser testing also exercised numeric editing, playback, undo, and drawing. Preview audio quality remains a listening judgment.

Gunshot editor: `?preset=player-impact` opens the exact twelve v42 attack frames, with a separate browser autosave and `sinistar-player-impact-edited` export filenames. The source audio reference switches to the reconstructed GUNSHOT. Use channel A fixed volume/tone/noise controls to stay compatible with the current three-byte cartridge format.

Recorded gunshot fits: `?preset=real-gunshot` (12 frames, 36 packed bytes) and `?preset=real-gunshot-full` (30 frames). Channel-A noise-only parameters fitted with the stateful speech2ay/Ayumi worker. Volume/noise curves are editable; tone pitch has no effect while tone is disabled. Both have separate autosaves/filenames and start without looping. Source: RemingtonGunshot.wav by fastson, Freesound 50618, CC BY 3.0. Cropped/level-adjusted reference and optimizer report are in `port/build/real-gunshot`. Cartridge assets unchanged.
