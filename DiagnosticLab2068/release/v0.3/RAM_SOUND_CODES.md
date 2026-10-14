# Identify a RAM chip by sound

Release v0.3 | October 13, 2026

**A readable display is not required for the RAM chip/bit tone code.** It still needs working CPU/cartridge execution and SCLD/beeper output. Silence is not a chip diagnosis.

Listen for the long synchronization tone, then count three separated groups of short bursts:

**2 / chip number / bit number**

| Sound or pause | Approximate duration | Pitch |
|---|---:|---:|
|Long synchronization tone|1.2 seconds|150Hz, lower|
|Silence after sync|0.9 seconds|—|
|Each counting beep|0.6 seconds|430Hz, higher|
|Silence between beeps in one group|0.4 seconds|—|
|Silence between groups|1.3 seconds|—|

The2 /6 /2 example repeats roughly every15 seconds, including the trailing pause and restart. Numbers are encoded by counting, not different pitches. These are nominal-clock model estimates. `verify_fault_timing.mjs` measures actual assembled-ROM FE output timestamps and verifies long/short tone lengths, both pitches and the different gap classes. The shared counting-beep/group pauses also apply to other fault families and training examples.

The first group is always two bursts for a RAM report. The second group identifies the chip below. The last group identifies the bit, or5 for multiple implicated bits. Border flashes mirror the groups when video output works. Wait for another long sync if you lose count. Multiple implicated chips can cycle through different codes.

| Groups after sync | Suspect RAM path | HOME address range (hex) | Last group1 /2 /3 /4 |
|---|---|---|---|
|2 /1 / bit|U6|4000-7FFF|D0 /D1 /D2 /D3|
|2 /2 / bit|U7|4000-7FFF|D4 /D5 /D6 /D7|
|2 /3 / bit|U12|8000-BFFF|D0 /D1 /D2 /D3|
|2 /4 / bit|U13|8000-BFFF|D4 /D5 /D6 /D7|
|2 /5 / bit|U17|C000-FFFF|D0 /D1 /D2 /D3|
|2 /6 / bit|U18|C000-FFFF|D4 /D5 /D6 /D7|

**Last group5 means more than one implicated bit**, not D4/D8 or a fifth bit in the chip. Use the second group to identify the chip path.

Example: long sync → two bursts → pause → six bursts → pause → two bursts means **U18 path, D5**. Long sync →2 /1 /5 means **U6 path, multiple implicated bits**. U6/U7 faults affect both display files, so their sound codes can be especially useful when screen text is unreadable.

Practice on a working TS2068: **0 Help → C Fault codes →1 RAM example** plays the synthetic **2 /6 /2** U18/D5 example. It is explicitly training, not a detected fault.

These are schematic-based chip-path leads. A defective IC, solder/wiring fault, power, decode or shared bus problem can produce the same report. Record the groups and any readable address/data fields, then verify against the original Timex schematic before replacing parts. The existing24-case reporter verifier checks all six chip/four bit combinations and synchronization output; physical sound recognition remains to be checked on hardware. Implementation: src/modules.asm fault reporter, fixed ROM pulse routines; evidence: suite-reporter-verification.json and suite-verification.json.
