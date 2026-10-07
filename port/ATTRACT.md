# Current: quiet attract mode and sound toggle v32

Cartridge SHA-256: `5939681f6fb9bbc11ea639804f2baeb5cf5b61d3b966afb3b5a5aeea142fe6e7`.

`reference/original/SAM/NEWTUNE.SRC`, lines 13-17, rejects every non-coin tune while AMDEMO is set. `WITT/ANISINI.SRC` sends speech through that tune system too. This revision therefore suppresses attract speech and gameplay SFX. No coin input is implemented in this port.

Native **S** toggles gameplay audio, once per press. The preference survives new games; muting discards pending speech/SFX rather than accumulating a backlog. The browser Sound ON/OFF button sends the same key and reflects cartridge state. Its first activation (or initial S press) enables browser audio; attract stays silent regardless of the gameplay setting.

The single demo worker now approaches from four alternating sides instead of repeatedly starting 24 pixels above-left. It respects the existing 60-tick post-delivery delay. Signed 9-bit world positioning handles entry offsets across world seams. This remains a serialized adaptation of the original multiple-worker attract task.

HOME 5E6E holds mute, 5E6F holds the S latch, and 5E70..71 saves the IRQ stack. The audio IRQ temporarily uses HOME 5ED0 as its stack top so mapping ROM7 cannot hide the publication stack. Tests observed the audio stack no lower than 5EC8, above the protected roar state at 5E80..8D. Main-stack and publication-stack restoration are checked by existing native tests.

Verification: zero audible attract writes and zero nonzero volume writes while muted; four worker entry sides; 20 deliveries and six bomb impacts; S hold/release and audio resume; browser button/key forwarding and ON/OFF labels; all eight voices/951 AY frames; 18,000-refresh stress with no late raster or ROM writes; mining, earned ammunition, victory, restart and loss. The isolated mining test now releases any crystal already carried by a worker before excluding that worker from the fixture, avoiding a timing-dependent stranded crystal.

Earlier v31 details follow.

---

# Arcade attract and score tables v31

Cartridge SHA-256: `a3cb875b1a38a4588a0dd3178eb6207096aa63bb142263ab6094a9984efd4be7`. Native 64KB DOCK cartridge; no browser AI or score persistence.

## What changed

The title artwork remains pixel-identical. After the title and scores, the native player mines the primary planetoid, follows released crystals, and changes to a Sinistar bombing mission after collecting at least four bombs or reaching the mining timeout. Crystal-carrying workers fly to Sinistar and deliver parts through the existing AddPart path. The player moves around Sinistar and launches bombs roughly every two seconds after assembly. Three seconds after the ammunition and active bomb are exhausted, the demo returns to the title. A 50-second watchdog bounds the demonstration. Fire/Space/Enter takes over with a fresh game.

The three original instruction messages now appear over gameplay, with the original line grouping and yellow/red emphasis. B LAUNCHES SINIBOMBS remains visible underneath each message. Text uses the arcade font and proportional spacing. Coordinates are adapted to 256x192, the existing top scanner and 112-line playfield; this is not a pixel-identical reproduction of the arcade's larger screen.

The score screen has a SINI-STAR champion line, thirty SINIMMORTALS and thirty SURVIVORS TODAY in three columns of ten. Both tables start with the original HSTDIM scores and developer initials. The deterministic seed rotation starts with SAM: 39,045 for immortals, 19,045 for today, followed by KVD 38,780/18,780 and N-F 38,415/18,415. The original has four possible initial-name rotations; this cartridge selects the SAM rotation. Both tables update during the current session. Initials entered once are copied to both qualifying records. O/P changes letters; Enter, Space or joystick fire confirms. No browser persistence.

## Source mapping and adaptations

Pinned source: historicalsource/sinistar, commit dc00bce37e5c5c7947369cf5040c10e4799f4a06, under reference/original.

- MICA/ZZAMSINI.SRC: mining until four bombs or timeout, forced bomber mission, carrier supply, ammunition-empty finish and watchdog.
- WITT/WARRIOR.SRC: mining/bombing mission behavior; WITT/VELOCITY.SRC: existing new_velocity kernel.
- WITT/SINI.SRC: attract-mode stationary Sinistar behavior.
- MICA/ATTMSGS.SRC: instruction wording, line grouping and color emphasis over live play.
- MICA/ZZATTRAC.SRC: champion, three-column SINIMMORTALS and SURVIVORS TODAY layout.
- MICA/HSTDIM.SRC: seeded scores and initials.

This implements the original mission progression, not a complete instruction-for-instruction port of the arcade warrior AI. Steering thresholds and orbit shape fit the smaller viewport. Original simultaneous carriers are serialized through this port's single worker slot; the port retains its 18-planetoid world rather than the original attract population of 21. Native demo invulnerability and its bounds remain adaptations. Warrior combat/population, source Think scheduling and the full original orbit controller remain future work. Current earned scores retain the existing worker/crystal/piece awards; five-point mining awards are not yet counted.

## Space and performance

Compiled planetoid row programs share identical instruction tails, saving 1,103 bytes against v30 (6,190 -> 5,087). Drawing remains compiled. 896 native comparisons produce identical bitmap/attribute output. The average added row-jump cost totals 760 T-states per full rock (about 0.22 ms at 3.528 MHz); worst additional row cost is 50 T-states. Title bitmap storage is column-ordered RLE, transposed only at title time. Frontend font row values use a nibble dictionary. The edited roar is unchanged.

Two score tables occupy HOME 5ED4..5FFF, five bytes per record, with scores in units of five. Radar output records moved to HOME E000..E15E, within the existing unused lower publication-buffer headroom. Title/initials code shares boot ROM3; gameplay AI and text dispatcher use ROM7. Mid-game message drawing disables interrupts briefly, temporarily maps ROM3 and uses a HOME BFFF stack, then restores the normal mapping and stack. It runs only when the instruction phase changes.

## Verification

- Native attract: 23 mining hits, 2 collected crystals, all 20 assembly deliveries, 6 bombs fired and 6 hits. Sinistar's full rectangle was visible in 67 published pictures.
- Exact original title bitmap, all three gameplay instruction phases, automatic return, and demo exclusion from scores.
- All 60 initial records; native score insertion, BBA initials via keyboard/joystick, both tables updated and retained across games.
- 18,000-refresh stress run: 3,697 published pictures, zero late raster writes, zero ROM writes.
- Fast-mode mining/earned ammo, win, restart, contact damage, protection and loss pass.
- All eight voice streams and 951 AY frames match; edited roar completes on repeated hits, with hybrid bomb noise intact.

Reports are in build/frontend-verification.json, build/frontend-compiled-rocks-verification.json, build/stress-fast-verification.json, build/fast-playable-verification.json, build/voices-verification.json and build/taunts-verification.json. Verification used TSRun; physical hardware was not tested in this update.
