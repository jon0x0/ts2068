# Expected test durations

These are healthy-run **emulator-model estimates**, not physical stopwatch measurements. `scripts/measure_test_durations.mjs` executes the assembled cartridge in the sibling TSRun machine model, records checkpoint frames, and converts58688 T-states/frame at3.528MHz to machine time. Host execution speed is irrelevant. Clock/contention differences, emulator speed settings, faults and cancellation can change real elapsed time. Firmware image hash and model hashes accompany `build/test-duration-estimates.json`.

## RAM menu (main2)

| Option | Approximate duration |
|---|---:|
| 1 Complete |84 seconds; allow1.5 minutes|
| 2 Patterns and walking bits |41 seconds|
| 3 March C- |8.5 seconds|
| 4 Address-derived data |8 seconds|
| 5 Seeded random |3 seconds|
| 6 Write/hold/read |24 seconds including both normal-refresh dwell periods|

Main7 Overnight repeats complete passes until cancellation or a detected mismatch. Allow roughly1.5 minutes per pass. It has no programmed overnight endpoint, elapsed-time clock or temperature measurement.

Between RAM soak passes, the status/count screen holds for **6 seconds** at the nominal3.528MHz clock (TSRun measured6.000036 seconds in both editions); a new key after all-key release can cancel promptly. This adds six seconds to each repeated pass, without writing status into an active RAM comparison. Physical clock/timing remains pending.

Stopping soak with no recorded errors shows **No failures during the test**, with the hexadecimal completed-pass count, and waits for a new key. A recorded RAM mismatch instead enters the chip/bit report. The infinite run is not labelled incomplete.

These durations end at the result screen. Individual RAM options show **Selected checks PASS**; Complete shows **All 6 RAM chips PASS**. Results wait until a new key is pressed. Mismatches enter the chip/bit reporter; cancelling a test does not produce a pass result.

## Full (main1, then new1)

From starting the sequence:

| Stage | Approximate duration |
|---|---:|
| Complete RAM |84 seconds|
| Banking and transitions |1 second|
| Beeper |15 seconds|
| AY comparisons/playback |22 seconds|
| Six video cards |18 seconds each; about108 seconds total|
| Reach keyboard |3 minutes50 seconds from start|
| Keyboard with every contact released |3 minutes54 seconds before timeout|
| Entire Full, no keys pressed |7 minutes42 seconds; allow8 minutes|

Press/release keys, then hold ENTER+SPACE or CAPS+SPACE to finish keyboard and show the summary earlier. The timeout is a bounded presentation budget, not proof that the keyboard works. Timings include drawing/transition overhead and are rounded; they are not exact per-stage deadlines.

## Power-on and waiting

- Normal quick startup: about9 seconds including native launch, or7 seconds after diagnostic entry, using existing startup evidence.
- Hold R: complete RAM at startup; allow roughly1.5 minutes from power-on.
- Hold F: Full at startup; add a few seconds of native launch, integrity and status setup to the menu-selected times.
- RAM uses screen memory as test data. Border colors identify phases: blue patterns, cyan walking, yellow March, magenta addresses, green random, red retention. A steady color is expected during a sweep/dwell.
- Release all keys, then press a new key to cancel at safe boundaries. Keyboard uses its exit chord/timeout. Stuck contacts can prevent cancellation from arming.
- Individually selected video cards wait for a new key. Banking and overnight keep running until stopped or a fault. Fault pulses may repeat until acknowledgement/reset; this is a report rather than a continuing healthy test.

Use the actual summary/fault report, not elapsed time, to determine completion. Physical timing validation remains pending. TSRun attribution is in THIRD_PARTY_CREDITS.md; stock clock/memory prerequisites follow the original technical manual.

The cartridge’s Full overview, RAM menu, extended-startup notice, beeper/AY screens, keyboard status and overnight dashboard show rounded estimates. These are fixed guidance labels, not elapsed-time meters. RAM destroys its screen during testing; border phase colors remain the minimal progress indication. `verify_duration_ui.mjs` executes the seven changed ROM loaders and checks all6912 display bytes against the generated screens before their test routines run.
