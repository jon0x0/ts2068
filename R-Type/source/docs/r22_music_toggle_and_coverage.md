# r22: music control and implementation coverage

Press M to switch music off/on. Music starts enabled. One transition is accepted
per press; holding M does not repeat. Song decoding continues while muted, so
unmuting resumes at the current position rather than restarting. Fire and death
effects remain enabled, including the selected65 triangle/noise death effect.
The preference survives menus and life restarts during the same running session.

| Area | Implemented | Remaining |
| --- | --- | --- |
| Levels | Level1 gameplay in SRAM and read-only64KB builds | Levels2–8 loading, native compatibility, rendering, progression and validation |
| Music | One looping first-level2019 AY arrangement,2305 ticks/46.1sec; M control | Other level/boss/title music selection and resident/banked playback |
| Boss graphics | ECM material shading on the Spectrum-derived level1 boss/enemy shapes | Full arcade-derived geometry/animation conversion for the bosses |
| Arcade graphics | Terrain interiors and three orb animation cels integrated | Remaining enemies/bosses and later-level art |
| Themes | Level1 complementary group palettes; eight authored theme families generated | Apply/refine later themes when their gameplay is converted |
| Expanded RAM |512KB staging/cache assets | Live gameplay consumer and full-game deployment |

Native music comes from the local2019 AY arrangement capture, entry0, not a claim
that all original arcade music is converted. Existing source notes in
docs/r16_logo_music_arcade_sfx.md retain the uncertain MSX/CPC attribution.
All70 level1 enemy descriptors have colour lookup coverage, which is not the
same as converting all arcade boss graphics. Boss geometry is still primarily
Spectrum-derived. Prepared source payloads/theme assets are not playable levels.

Implementation: music_tick polls keyboard row7FFE bit2 at50Hz through ROM0:11D0.
FD93 is the mute preference; FD94 debounces the held key. Both are initialized
once by the AY IRQ startup. These bytes sit beyond the music state FD92 and before
native game code FDA5. The music-owned-volume helper at0ED4 emits zero for R8–10
when muted, after the existing SFX channel-ownership filter. It never silences
an effect-owned channel or writes joystick R14/R15. ROM0:11D0–11EF is separate
from initial_terrain, which ends11C2. Native banking/IFF contracts remain intact.

Validation: both targets pass160 ticks with four held/released press sequences,
140 muted-volume checks and122 SFX-owned-volume checks. Music shadow states match
an unmuted control throughout; boot defaults enabled. Real Fuse native keyboard
port-result injection confirms a held first press mutes and a second press unmutes.
Logs/commands: build/diagnostics/music_toggle_r22; CPU report:
build/audio/music_toggle_validation_r22.json. Standard music loops, selected65,
IRQ contracts, live joystick/music, sprites/restoration, instance palettes, all8
Fuse scroll phases, full title states and read-only execution are revalidated.
Extended scrolling controls remain under build/diagnostics/terrain_motion_r22.

Build with scripts/build_ecm_native.py and scripts/build_rom_ecm.py; the versioned
publisher now also requires matching CPU and Fuse music-toggle reports.
Level1 only; physical hardware untested.
