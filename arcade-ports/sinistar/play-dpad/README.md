# Sinistar with Berzerk's virtual D-pad

Serve the repository and open `/play-dpad/`. This is a separate comparison
player; `/play/` keeps the newer upstream TSRun.

The unchanged emulator files in `tsrun/` come from the Berzerk publishing
checkout at commit `78ddfb6`. Full provenance and file hashes are in
`tsrun-version.json`. Neither the original Berzerk checkout nor the shared
TSRun checkout is edited.

The circular eight-way D-pad, draggable knob, 0.45 dead zone, touch release
handling, CRT and output-audio controls are adapted from Berzerk's
personalization. Sinistar uses joystick 1, native fire bit 7, and a separate
held B-key Sinibomb button. Berzerk's bit-4 fire mirroring and active-player
RAM lookup are removed. Start and restart replace coin/two-player actions.

All keyboard controls are visible beneath the screen, including in fullscreen.
The browser Audio switch and cartridge S toggle are separate; both must be
enabled for gameplay sound. Attract mode remains silent.

The cartridge is byte-identical to `port/build/sinistar-mining.dck`. Use
`TSRUN_ROOT` pointing at this page's `tsrun/` directory to run the configurable
native frontend/playable/voice/render-stress regression scripts against it.
