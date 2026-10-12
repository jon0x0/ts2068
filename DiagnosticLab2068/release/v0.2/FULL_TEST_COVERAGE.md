# What Full test runs and what completion means

Release v0.2 | October 12, 2026

Select main menu1 for the coverage overview, release the selection key, then1 to start or M to return. Held F at startup runs the Full sequence directly. Cold boot separately performs the minimal ROM0 CPU and cartridge-integrity checks; menu Full does not rerun those.

## Automatic comparisons

**Allow about4 minutes to reach keyboard, or8 minutes for an unattended Full run.** The healthy model reaches keyboard at about3 minutes50 seconds. Its no-key timeout adds about3 minutes54 seconds, giving7 minutes42 seconds overall. Hold ENTER+SPACE or CAPS+SPACE after testing keys to finish earlier. Complete RAM alone takes about84 seconds. These are nominal-clock emulator estimates, not physical measurements; see [TEST_DURATIONS.md](TEST_DURATIONS.md) for individual options and startup guidance.

1. Complete all48K HOME RAM: eight fill/read patterns, walking-one/complements, March C-, address-derived hash plus low/high address planes, deterministic random and normal-refresh55/AA write/hold/read. Includes both display files and UI storage; no reserved untested workspace.
2. 100 banking cycles, each covering18 HSR masks: selected DOCK signatures, attempted ROM writes and HOME sentinels. This checks the exercised selection and write-isolation behavior; it is not exhaustive timing, whole-chunk comparisons on every transition or exact Sinistar reproduction.
3. Masked AY R0-R13 register/address comparisons with port A kept input-safe. This checks exercised digital register paths, not the actual audio waveform/output.

A detected mismatch stops the sequence and reports. A cancelled sequence returns without a digital-matched completion screen.

## Guided outputs and keyboard

- Beeper: low, mid and high tones.
- AY:24 channel/pitch/volume/noise/envelope/chord/silence steps with active labels/progress.
- Six native video cards: Normal/Bright bars; standard/FLASH/bit lanes; secondary display; ECM dither/disc;512-pixel hires calibration;128 attribute combinations.
- Keyboard press/release display. Both CAPS share one contact; hold ENTER+SPACE or CAPS+SPACE to exit. A finite scan timeout also ends the presentation.

Listen for all sounds, inspect every card and press/release every key. Use separately selected cards/sound tests for longer inspection. These functions are not automatically verified by audio/video loopback or a required all-keys-certified gate. An unpressed key or unseen output remains untested.

## Interpreting completion

The summary states **Automatic comparisons matched** and lists **Still needs your judgement**. It appears after the scheduled checks reach keyboard and keyboard exits/times out. A timeout does not certify the keyboard. The exit chord is quarantined so it cannot immediately dismiss the summary; a new key returns to the menu.

After digital matches and satisfactory guided observations, a useful service record is: “Covered RAM/bank/AY comparisons matched; observed beeper/AY/video/keyboard outputs satisfactory,” with machine configuration, image hash, cold/warm state and any skipped observations. It confirms performance of the covered functions under this workload, not absence of every possible hardware fault.

## Separate tests and limits

Full excludes HOME/EXROM CRC32, optional five-stage CPU/localized address checks, SCLD IRQ inhibit/arrival, raw EAR/joystick observation, overnight runs and expansion/PicoVideo/TSPico tests. It does not certify ROM identity, all CPU instructions, precise clock/contention timing, every SCLD gate/pin or thermal reliability. A good Full run can coexist with a fault outside its patterns, addresses, timing or observation coverage.

Implementation: src/diagnostic.asm::select_full; src/modules.asm::fullinfo_ready/fullsummary_ready/keyboard_finished and each existing stage. All control remains stackless in ROM; richer text still needs working display paths. The canonical registry records partial versus implemented scope. Emulator checks cover overview/start quarantine, actual full sequence, completion chord handling, return and cancellation; physical acceptance remains pending.
