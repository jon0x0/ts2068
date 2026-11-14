# r16: replacement logo motion, music and arcade-derived effects

Implemented2026-11-02. r15's original monochrome logo plus an extra reveal was
not the requested animation. r16 replaces the original8A4D routine: six slices
of the accepted new artwork sweep left, then spread to their final positions.
Movement stays on8-pixel columns so bitmap and per8x1 colours remain aligned.
The wider artwork uses adapted final positions0,6,9,15,21,26; the original used
1,6,11,16,21,26. It retains the two movement phases, not subpixel trajectories.

Each frame is composed offscreen at HOMEA600–B1FF, then published in paired
bitmap/colour rows. SRAM saves/restores the underlying graphics through DOCK2;
the read-only target uses its idle relocated workspace. Thirty motion states
on both targets match an independent source-art compositor. This is software
buffer publication, not a hardware page flip or a physical raster-tearing claim.
Final title remains stable over repeated menu publications.

## Music

Web research found Project AY's compiled-driver collections and confirmed the
2019 Goodboy/Tiboh release's additional CPC/MSX sound alternatives:
https://worldofspectrum.net/projectay/gdmusic.htm
https://vtrd.in/news_arch.php?y=2019
The actual local2019 captured bank7 is used rather than an uncertain download.
All16 entries were exercised. Entry0 is the first-level tune: intro6258 reads
the level character at719C, subtractsASCII31 and passes that index toC253.
Entry0 loops after2305ticks (46.1seconds at50Hz), proved by identical complete
driver-bank state. The original tune's nine tone/volume registers are retained;
its mixer isB8 and it uses neither noise nor envelope. Exact menu-selector
MSX/CPC attribution remains uncertain, so the build credits the2019 AY arrangement.

The resident sequencer expands a RePair grammar over deduplicated delta-register
frames. Redundant writes are removed; no note/frame is dropped. Register states
match4611init/tick frames through two complete loops on both targets. Original
music has noR13 retriggers to preserve. The existing1834/2205display-IRQ scheduler
maintains about50Hz independently of foreground rendering.

Music uses A/B/C when idle. Effects borrow A, leaving B/C uninterrupted; original
music state continues advancing so A resumes at the current musical position.
No waveform/DAC summing is attempted. AY noise is shared: the effect owns R6;
R7 combines effect tone/noise enables onA with tone-only musicB/C, preserving
joystick direction bits. Audio never writesR14/R15. Two-channel effect candidates
would leave onlyC for music and are not the default in this build.

State uses obsolete beeper-table space, not native terrain RAM:
FD50–FD7F grammar stack (44bytes observed maximum), FD80/82 stack/sequence
pointers, FD84–FD91 music shadow, FD92 running flag. Title scratch isFC50–FC7F.
Code/tables are immutable ROM; no cartridge RAM is required by the64KB target.
F4 banking helpers live in persistent ROM0. ROM7 fetches restore banking before
touching the temporarily hidden stack. Compilation asserts reservations.

## The rejected effects are replaced

The user's later instruction explicitly rejects the current2019 sound effects.
None of those old note-script effects is the default r16 effect. Eight authentic
arcade sound captures are converted with maintained speech2ay harmonic1, then
resampled from60.1145Hz curves to50Hz delta playback. The library occupies1238
stream bytes plus66directory bytes and covers all21native event slots. Multiple
related game events share a conversion. Death outranks incoming shot requests.

Natural MAME gameplay traces confirm command48 repeatedly follows fire input,
80 accompanies enemy firing,53 follows the death/music-stop sequence, and99
follows coin input.43,49,50,52 provide additional impact/explosion/weapon candidates;
their exact individual event semantics are provisional. The mapping is explicit
in scripts/build_ay_sfx.py. This is a playable first replacement pass, not a claim
that every native event now matches the arcade's event assignment exactly.

The arcade uses YM2151 FM sound, not AY; speech2ay is a constrained approximation.
Its raw harmonic records are14bytes:11tone/noise/volume registers, two envelope
period bytes and a255skip sentinel. They are not17-byte records. Conversion
checks record length and valid volume/period ranges; a mistaken exploratory
17-byte parse was caught and corrected before publication. Command38 is silent
in isolation, so confirmed coin99 replaces that candidate. Silent sources are
excluded. One/two-channel comparisons are supplied with separately normalized
originals. The old effect11 WAV is retained solely as a rejected A/B baseline.

Original capture PCM, converter hashes and source archives remain intact.
MAME uses the existing documented diagnostic PROM/PLD stand-ins; those archival
regions are not sound data. The sound CPU/graphics game ROMs are authentic local
inputs. https://github.com/mamedev/mame/blob/master/src/mame/irem/m72.cpp documents
the YM2151 sound hardware and the command latch on mainCPU I/O0.

## Reproduce / inspect

Use the currentNode runtime, not the old PATH Node.
1. scripts/research_goodboy_banks.py reproduces source-bank capture.
2. Run Node scripts/extract_level1_music_r16.mjs, then
   python scripts/build_music_grammar_r16.py.
3. python scripts/capture_arcade_game_audio_r16.py traces real event IDs;
   python scripts/capture_arcade_sfx_r16.py captures isolated effects;
   python scripts/convert_arcade_sfx_r16.py converts them.
4. python scripts/build_ecm_native.py; python scripts/build_rom_ecm.py.
5. Run r16 verification scripts, then python scripts/publish_rom_ecm_r16.py.

Comparison: build/audio/speech2ay_candidates/compare.html.
Native mixed preview: build/audio/music_and_effects_r16.wav.
Motion preview: build/diagnostics/title_motion_r16/new_logo_motion.gif.
These are captured-RAM / modeled audio artifacts, not physical hardware recordings.
All failures, corrective work and final hash evidence are recorded in TEST_HISTORY.
Level one only. Physical hardware remains untested;512KB consumers remain staging-only.
