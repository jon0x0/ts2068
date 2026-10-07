# Recorded gunshot player-death attack (v43)

Uses the `real-gunshot-full` editor preset: 30 AY refresh frames (0.499 seconds), channel-A noise and fixed volume, 90 packed bytes. The existing explosion follows after the complete attack. The first visual burst waits for the matching 30 physics ticks, and does not restart the audio. Later bursts retain existing behavior. Speech retains priority.

This intentionally extends the previous 12-refresh / 0.20-second lead-in to preserve the selected longer sound. Total player death sequencing is 126 physics ticks rather than 108. Sinistar death is unchanged.

The extra 54 bytes occupy resident alignment padding. Scanline tables stay at 0x9300 and resident code ends at 0x9FF5, unchanged from v42. No new RAM or graphics work. The cartridge remains eight 8-KB ROM banks.

Source: **RemingtonGunshot.wav**, recorded by **fastson**.
https://freesound.org/people/fastson/sounds/50618/
Licensed **Creative Commons Attribution 3.0**:
https://creativecommons.org/licenses/by/3.0/

Adaptation: public MP3 preview decoded to mono, cropped at 7.37424 seconds, level adjusted and fitted offline to AY noise period and volume at 60.1145 Hz using speech2ay/Ayumi. This is a synthesized approximation, not PCM playback. Source metadata and fitted rows are preserved in assets/sfx-player-impact-real.json; the original arcade-derived attack is retained separately.

Validation: exact 30-frame cartridge register output, explosion on audio refresh 31, speech priority, no ROM writes, full player/Sinistar death sequences, complete speech streams, and playable win/restart/loss. See build/player-impact-verification.json and the current verification reports.

## v46 visual timing update

The audio timing above is preserved, but visual explosions now start immediately on contact. The player-death sequence is back to 96 physics ticks (about 1.6 seconds), with alternating single bursts. It no longer waits 30 ticks before displaying the first explosion.
