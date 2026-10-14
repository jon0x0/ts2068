# Load-related faults and 5 V rail investigation

Release v0.3 | October 13, 2026

TS2068 Diagnostic Lab cartridge v0.3 adds configurable combined load tests because a machine can pass isolated RAM/bus tests and still corrupt data during a game. The supplied Sinistar report describes a stack byte losing D1, despite37 ECM March C− passes over5F00h–FFFFh with interrupts off and passing bus tests. This is a user report, not a fault reproduced or measured by this project. The affected image, exact address and electrical measurements are not supplied.

Sinistar combines display fetches, frame IRQ stack saves/returns, an audio stack near5ED0h, bank switching and frequent Speech2AY register updates. The reported March range excludes that audio-stack vicinity and disabling IRQ removes interrupt stack/audio activity. Supply droop/ripple under audio load, intermittent RAM paths, DRAM refresh/timing and other shared control/data paths are plausible investigations; the symptom does not prove any one cause or failed chip.

## Repeatable software workload

Use cartridge main **L**, then **P**, choose **N** for one batch or **C** for continuous, and **S** to begin. P selects all loads. Option6 alternates quiet/busy slices; option3 enables normal/ECM/high-resolution rotation; option7 enables stronger three-channel AY/envelope traffic and bounded beeper toggles. RAM comparisons remain active between auxiliary slices. Disable individual options to compare the baseline with video, AY, IRQ and banking separately. S uses bounded interrupt-arrival checkpoints. For genuine interrupted-work returns, R opens a separate confirmation; fresh IRQ and RAM/table qualification gates its IM1/IM2 burst. Late saved-PC/table corruption can defeat recovery in that exposed profile.

The start notice says TEST STARTED / RUNNING and lasts six nominal seconds before each RAM batch. Yellow border denotes test activity; blue denotes the quieter power-cycle slice. Screen changes during RAM testing are expected. Release all keys, then press a new key to stop; a stuck contact prevents arming. N still ends after its completed batch. Failures stop at the first comparison and retain the actual observed read/POP byte. Expected XOR observed identifies any D0–D7 error or several bits. Chip/bit reports identify suspect paths, not proven defective components.

The profile increases switching activity and introduces repeatable load transitions; the project has not measured how much current changes. A quieter ROM loop still executes instructions and normal refresh. Neither quiet/busy labels nor a passing emulator test establish supply margins. The HOME U16 edition does not include this combined-load module.

## Observe the 5 V rail with an oscilloscope

Use the supplied board schematic and the actual motherboard revision to identify logic **+5 V and GND**. The original Technical Manual §2.1.2 gives a5 V regulation range of4.75–5.25 V. This is a reference for the rail, not a blanket guarantee that every short transient above4.75 V is harmless; device limits and timing also matter.

1. Power off while securing probe connections. For a conventional earth-referenced scope, connect its ground only to verified board GND; verify other connected equipment's ground paths. Never attach the ground clip to a supply rail, defeat the scope's protective earth or open/probe the mains adapter for this procedure.
2. Start with a compensated10× probe and **DC coupling**. Measure the regulator output, then locally across nearby decoupling capacitors at AY and DRAM supply points. Use a short ground spring/lead at the local GND point; a long flying ground can manufacture apparent spikes. Do not infer a bad regulator from one distant measurement.
3. Record the steady rail before testing, during the six-second notice, and during quiet/busy and sound/video transitions. Use acquisition persistence or single-shot capture and a falling-edge trigger just below the observed baseline; choose the level to capture departures, not an arbitrary pass/fail threshold. Try both sub-millisecond and tens-of-milliseconds views, and compare cold with warmed operation.
4. Look for downward steps, ripple, brief dips, ringing or slow recovery that correlate with AY/busy intervals. A20 MHz bandwidth limit can help inspect supply ripple; also check wider bandwidth for short spikes and confirm suspicious captures with the short local ground connection. AC coupling can magnify ripple after the DC level is established, but hides absolute voltage and must not be the only measurement.
5. Compare regulator and local rails at the same workload. A regulator-side dip points toward the supply/regulation path; a local-only departure suggests distribution, connectors, joints or decoupling. These are leads, not component verdicts. A regulator input measurement requires its own voltage range/setup; do not confuse the unregulated adapter input with the5 V logic rail.

A DMM is useful for steady voltage but can miss short dips. Preserve screenshots with probe location, coupling, attenuation, bandwidth, trigger level, timescale and workload settings. If the rail looks clean, that does not rule out a faster/local disturbance or a DRAM timing/refresh fault. Do not change voltage or attach arbitrary dummy loads as part of this software test.

## Isolate causes and record evidence

Repeat with the same supply, cartridge/interface, accessories and game revision as the reported failure. Compare RAM baseline with AY only, video only, IRQ only, banking only, then combinations. Correlate the scope trace with audible/border load transitions and the first error address/expected/observed/XOR. A quiet/busy change can trigger a fault without a large average-current increase; conversely loud audio does not prove maximum supply current.

If measured evidence implicates the supply path, inspect the applicable connector/switch/regulator/distribution joints and decoupling against the schematic, with power removed before mechanical work. Check temperature and cold/warm repeatability. Avoid replacing a named RAM IC solely because one bit failed under load. With a clean verified supply, further DRAM refresh/control timing investigation requires appropriate equipment and a technician familiar with the TS2068; software cannot certify electrical refresh margins.

Record machine/board revision, PSU identity, cartridge/interface/firmware, image SHA256, all options, cold/warm duration, first fault and scope setup. Keep supplied observations, emulator validation and measured physical evidence separate.

Sources: original Timex TS2068 Technical Manual §2.1.2,2.1.6,2.1.8 and supplied original schematic; General Instrument AY-3-8910/8912 data manual; read-only Sinistar source snapshot in sinistar-load-source-evidence.json; user incident report. Source authors and archives are credited in THIRD_PARTY_CREDITS.md. Scope setup guidance is diagnostic practice, not electrical validation of this machine or a repair guarantee.
