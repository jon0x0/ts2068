# Schematic aware fault display

The schematic allows a useful best-effort screen even when a RAM chip fails. It does not make the screen a guaranteed fault channel. Border/beeper reports remain active and independent of the text renderer's success.

## Separate upper RAM from display RAM

U12/U13/U17/U18 supply upper HOME RAM; their failure does not physically destroy U6/U7 display storage. If display addresses pass their checks, draw a normal fault page directly from ROM using register-held state and fixed ROM control. Do not place its stack, glyph data, message pointer or return address in the failed upper region. v0.1 already avoids a HOME stack, but currently bypasses the screen for any RAM error; this richer error page is future integration work.

## Use surviving display bit lanes

U6 supplies D0-D3 and U7 D4-D7 at every address in HOME4000-7FFF. Within a bitmap byte, U7's bits are the left four pixels and U6's the right four. Use the tested per-bit error union to select surviving lanes; do not assume the entire opposite package is good without testing it.

The host prototype uses an independently drawn3x5 block font. Each logical font column occupies one byte, and lit cells write only known-good bits. This spreads a large glyph across many bytes while preserving its shape in the surviving positions. The damaged lanes may add stripes or noise, but they do not control code execution. Both panels show RAM FAIL, the suspect chip path and the border/beeper class/item code.

Source: supplied Timex schematic335-B70500 and original technical manual, credited in THIRD_PARTY_CREDITS.md. No font/program code is borrowed for this prototype.

## Attribute bits require their own fallback

A stronger candidate draws the large glyphs with attribute colors while holding the known-good bitmap lanes constant. With U6 faulty/U7 healthy, set healthy high pixel bits to0 so they display PAPER; vary healthy PAPER high bits between0 and6. With U7 faulty/U6 healthy, set healthy low pixel bits to1 so they display INK; vary healthy INK between0 and7 and PAPER's healthy low color bit too. The latter preserves a color difference even if the bad chip forces FLASH inversion. This produces a coarse but substantially larger character image. `attribute-comparison.png` demonstrates this alternative under the same modeled extremes; it should be preferred for target prototyping if bench readability confirms it.

The same U6/U7 pair stores attributes. U6 covers INK bits0-2 and PAPER bit0; U7 covers PAPER bits1-2, BRIGHT and FLASH. Choosing healthy bitmap pixels alone can still make text invisible when corrupted INK and PAPER become equal.

Duplicate the message in two attribute panels: top30h (black ink/yellow paper), bottom07h (white ink/black paper). The host model checks every constant value of a failed U6 or U7 nibble: at least one panel retains distinct observed INK/PAPER values, and all selected healthy pixel lanes retain the written shape. A forced FLASH bit may invert the picture; inversion changes polarity rather than removing contrast. The generated previews include both flash phases.

This contrast property applies to the modeled stable-nibble faults, not arbitrary random failures, address aliasing, missing refresh or bad video fetches. When implementing the renderer, sample relevant pixel/attribute addresses with bounded retries, discard unstable assumptions and keep showing the pulse code regardless of text quality. No wait for a visible image or a keyboard response is allowed on the fault path.

## Prototype and remaining target work

Run `python scripts/prototype_degraded_display.py` to rebuild pixel-lane and attribute-coded comparisons under `assets/degraded-display/`, reference planes and the32-case host report. Previews use illustrative RGB decoding of the simulated faulty bytes; they are not screenshots of target firmware. The existing v0.1 image is unchanged.

UI-03 records the future target renderer. Integrate it only through a fixed stackless ROM path preserving the first-fault registers and active anchor. Validate whole-nibble and individual-bit stuck faults, unstable attributes, late healthy-lane errors, upper-RAM-only failures, both chips failed and lost display output. Include physical readability observations and cancellation/reporting behavior. If no display lanes or stable contrasting attributes remain usable, skip text and continue the existing minimal reporter.

Switching to the second display file cannot avoid U6/U7: both files occupy the same pair. Upper RAM cannot be relocated into the native display by HSR. PicoVideo has a separate captured-display path and needs its own profile-specific evidence; a readable external picture would not certify native RAM/SCLD correctness.

## Target integration

Version0.2 implements the attribute-coded renderer in src/modules.asm::fault_draw, preserving first-fault/result registers and pulse output.32 target stuck-nibble models are covered by scripts/verify_suite.mjs. See tests/V02_DIAGNOSTIC_SUITE.md for exact behavior, both-nibble fallback and physical limitations. Earlier host prototype scope is retained above for provenance.
