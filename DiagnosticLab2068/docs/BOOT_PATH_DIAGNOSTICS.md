# Minimal boot CPU and HOME-bus checks

Implemented in `src/boot.asm`, always-selected ROM0. Default boot delay remains approximately7 modeled seconds after entry/9 including native launch: these small checks add less than one modeled display frame. They are consistency checks with explicit execution dependencies, not a diagnosis of every CPU/motherboard fault.

## Sequence and codes

Immediately after DI/known ports, before any HOME read/write or cartridge-data check, test general-register constants, arithmetic/carry/zero/sign/overflow/AND/XOR and rotate/shift/carry. No stack, RAM variables, RAM code, HOME calls, display, keyboard or interrupt is used. A detected mismatch repeats8/stage:1 registers,2 arithmetic/flags/logic,3 rotate/shift. Every boot choice runs this early subset; optional ROM2 CPU tests remain separately selected.

Then verify cartridge integrity and perform the established full48K00/FF sweeps. Any mismatch retains the usual RAM chip/nibble reporter. Only a successful default quick sweep proceeds to16 localized HOME address-pair checks; R/F complete sweeps retain their broader address-dependent algorithms instead.

For bit k, base4000 and partner base XOR(1<<k), except A14 uses8000/C000 to avoid0000 ROM. Independently write/read55 thenAA at each endpoint. A qualification failure joins the normal first-fault RAM classifier, capturing expected/observed/address and phase48–63 (48=A0 pair through63=A15 pair). It is not prematurely labelled an address alias. Then write55/AA to the two endpoints and verify both; reverse AA/55 and verify again. A mismatch repeats9/index1–16 (1=A0,16=A15). These are address/data-path candidates; a late data error can still mimic an alias.

Boot CPU/address pulses use only low-ROM control, register-held family/detail, the existing FE tone/white/black envelope and fixed continuations. No image is drawn, and no keyboard acknowledgement is assumed. They repeat until reset/power cycle. A damaged/blank startup screen does not suppress them. Normal RAM reports retain their richer best-effort text/retry/menu controls.

## What this can catch

- Selected register/instruction result inconsistencies, if comparison/branch/report instructions remain usable.
- Stuck data bits/gross RAM read/write faults in all48K via00/FF.
- Some HOME data-bit bridges/coupling missed by uniform00/FF, via55/AA at the selected endpoints.
- Localized address-pair aliases across A0–A15, if cartridge fetch and I/O remain healthy.

No full48K55/AA sweep was added to quick boot. Complete RAM already supplies those and broader March/walking/address/random/retention coverage. The sparse pairs cannot certify all address combinations or all cells.

## What remains unavoidable

Passive HOME launch may fail before entry. Global data faults can corrupt opcodes; low address faults can alter instruction bytes; high address faults can affect DOCK selection and cartridge integrity; branch/register/clock faults can defeat the reporter. Border and beeper both require FE/SCLD output. No signal does not prove CPU failure. A family3 integrity report can reflect cartridge/address/data/decode, not only bad ROM contents. Chip PATH reports similarly include associated wiring/decode.

The boot routines have no deliberate banked execution transfer. Font data moved to DOCK ROM1 at2200–24FF to free ROM0 code space. Rich glyph rendering briefly selects HSR03 while executing ROM0, then restores01; fonts still never come from live HOME ROM or a RAM code pointer. Minimal boot pulses and RAM attribute-coded fallback do not depend on the font.

`scripts/verify_boot.mjs` injects three CPU-stage result faults, sixteen HOME pair aliases, mixed-data failures and dominant-AND data bridges that pass00/FF. It asserts unchanged SP/ROM0 opcodes and no HOME writes on CPU failures. Models are post-entry and scope-limited; they do not establish real global pin-fault/boot survival. Native launch, full suite and degraded-display checks remain separate image-bound evidence. Physical validation is pending.

Replication of code across ROM addresses remains future work: see REPLICATED_RECOVERY_ROM.md. Sources: original Timex technical manual/schematic and Zilog Z80 CPU User Manual; existing diagnostic pulse conventions are preserved.
