# Goodboy / Tiboh R-Type 2019 audio investigation

Investigated 2026-11-01. This is the actual 2019 disk release, separate from the
local Torasoft 1993 TZX. No current TS2068 cartridge images were changed.

## Provenance and added features

Primary release archive: https://vtrd.in/news_arch.php?y=2019 explicitly describes
Kempston Mouse and two additional sound alternatives from Amstrad CPC and MSX.
Release: https://vtrd.in/gamez/r/RTYPE_GT.zip
SHA256: e6d307a87721fd190499c2a257a7c5d33c385acea58da73e274e18d87c529b86
Contains RTYPE_GT.SCL (101161 bytes); SCL checksum and two-file directory checked.
The loader contains goodboy&tiboh'19. source.json and disk_inventory.json preserve
provenance and inventory under build/research/goodboy2019/.

The actual release was booted with scripted electrical keyboard input in an
isolated Fuse Pentagon/TR-DOS session. pentagon_3000.png is its loading picture;
pentagon_4000.png shows 0.START, 1.CHEAT, 2.MOUSE, 3.SOUNDS and MSX / CPC.
This directly confirms the selectable alternatives. Contemporary reporting at
https://www.idpixel.ru/news/2140-igry-dlja-zx-spectrum-s-muzykoj-i-zvukami-ot-amstard-cpc-msx-i-atari-st-chast-5/
describes new title/menu/game melodies and effects. A full per-level musical
inventory and subjective listening comparison have not yet been performed.
Do not interpret two sound alternatives as proof of two complete level scores.

## Extracted code evidence

intro_6000.bin is the 8192-byte loader/patch block at entry $6000.
player_bank3.bin and player_bank7.bin are actual 16KB bank captures, not scans
of compressed disk data. scripts/research_goodboy_audio.py reproduces menu
captures; scripts/research_goodboy_banks.py reproduces the bank captures.
Both use reference firmware recorded in reference_firmware_matched.json,
research-only, never incorporated into native output.

- Intro: bank 3, initialise CALL $C000, refresh CALL $C005, stop CALL $C008.
  Refresh is driven by EI/HALT in wrapper $60AE. The player self-modifies code.
  It writes Spectrum AY ports using BC low byte $FD and high bytes $FF/$BF;
  it also uses OUTI, so a search for OUT (C),A alone would miss outputs.
- Menu sound selection toggles byte $6171. At $6170 a zero flag installs a
  substantial alternate hook set, while a nonzero flag returns. The exact
  source-to-flag mapping and remaining resident branch need further tracing;
  no undocumented inference about default MSX/CPC mapping is relied upon.
- Alternate hooks include replacing the original $F87C sound routine with
  a seven-byte capture stub from $62EC. H becomes the event ID at $8F1F.
  The dispatch wrapper $62C7 pages bank 7 and calls $C220.
- Tune wrapper $6261 pages bank 7 and calls $C253 with an index in L.
  Event hooks select indices 8,10,11,12,13,14,15 and level-related indices.
  The disk bootstrap calls bank-7 $C684 then $C253 with L=8 before $85FD.
- Bank-7 $C000 is a compact verified AY writer: PUSH BC; LD BC,$FFFD;
  OUT (C),A; LD B,$BF; OUT (C),E; POP BC; RET.
  $C220 dispatches effects and updates the player; $C253 selects tune data
  via a pointer table at $C010. $C684 resets state and writes mixer R7=$B8.

Thus this is reusable native Z80 AY music/effects code with real game hooks,
not a PCM recording or speech2ay conversion. It is not a drop-in TS2068 patch.

## Native integration implications

Apply the TS2068 audio skill's native AY workflow. Replace every reachable AY
output path (including OUTI); preserve register-write order and R13 envelope
retrigger semantics. Use native F5/F6 ports and reserve R14/R15 for joysticks.
Audit mixer R7 direction bits for native input: the observed $B8 clears bit6,
but every reachable mixer write still needs checking. Make select/write pairs
atomic relative to joystick reads. Preserve actual music timing with a 50-Hz
scheduler against the TS2068 approximately 60.1145-Hz display, subject to measured
reference cadence. Preserve writable player state/self-modification, stack and
interrupt visibility during bank transitions.

TSPico's demonstrated full 512KB is the natural first integration target.
The stock 64KB cartridge needs a separate measured storage/RAM layout; two
captured 16KB banks do not prove all music or game data fits in that target.
Keep both targets and speech2ay as optional additional effects, rather than
re-synthesizing already-native AY music. Next audio milestone: inventory both
branches and all tunes/effects, capture ordered AY traces, adapt into the existing
native build, then compare traces/timing and simultaneous joystick operation.


## r15 implemented integration

All21 effects from the captured bank7 now play natively on both targets,
with exact source register trace verification and simultaneous joystick tests.
Music and source-menu MSX/CPC attribution remain pending. See
`r15_audio_rendering.md` for implementation, timing, comparison and limits.
