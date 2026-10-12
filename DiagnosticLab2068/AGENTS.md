# Project maintenance

Read README.md, docs/PROJECT_STATE.md, docs/TEST_CATALOG.md, and the relevant design sections before changing diagnostic behavior.

## Preserve the current scope

- Official public name: **TS2068 Diagnostic Lab cartridge**. Use it in operator documentation and product headings. The current manual filename is `TS2068-Diagnostic-Lab-Cartridge-Manual.pdf`, including inside the release package.

- The main target is a ROM-only TS2068 cartridge. A user-requested separate16KiB HOME U16 reset edition is also supported; read docs/HOME_ROM_EDITION.md before changing it. Keep its reduced menu/coverage and HOME-only mapping distinct from the64K cartridge. Pico resources and independent hardware-assisted boot/reporting are future capabilities.
- A passive native LROS cartridge depends on machine initialization before entry. Do not claim stackless post-entry code eliminates that launch dependency.
- v0.2 implements the stock-machine suite documented in docs/tests/V02_DIAGNOSTIC_SUITE.md. Advanced modules remain partial/specified and physical validation is pending. Keep specification, implementation, emulator evidence and physical validation distinct.
- Use the schematic and original technical manual to resolve hardware claims; derived summaries and emulator code can contain errors.

## Keep tests documented

- docs/test-registry.json is the canonical test inventory. IDs are stable; never reuse a retired ID for a different test.
- For every added or changed test record its actual algorithm, prerequisites, tested ranges/signals, observables, fault attribution limits, cancellation/recovery behavior, and source references.
- When implementing firmware, populate firmware_locations with real workspace-relative source paths and entry symbols. Update firmware_status only when executable code exists. Add validation evidence with image hash, tool/hardware configuration, result and limitations.
- When changing an algorithm or fault code, update the registry and operator-facing design together. Preserve compatibility or document the change in docs/CHANGELOG.md.
- Run python scripts/build_test_catalog.py after registry changes. Do not manually edit the generated catalog.
- Do not manufacture emulator or hardware validation. A successful host asset generator validates data formatting only.

## Firmware invariants

- Crash avoidance is a primary acceptance criterion. Follow docs/FAULT_CONTAINMENT.md for every routine and recovery path; ordinary peripheral or RAM failures must produce bounded results, not uncontrolled execution.
- Keep the default scheduler, RAM/banking/soak control and minimal reporter stackless in ROM even after RAM qualification. Guard checks do not guarantee that an intermittently failing stack will survive the next RET.
- Record per-test residual execution/control-flow exposure. Keep RAM gateways, banked execution transfers and advanced interrupt-return tests separately selectable and skip them when prerequisites fail.

- No stack, RAM variables, ordinary ROM calls or interrupts in the initial register-only stage.
- Keep executing code, any enabled interrupt vectors/handler, stack and writable workspace visible through every mapping transition.
- All RAM must eventually be tested, including workspace and screen RAM. Use register-only fallback when writable state is suspect.
- DOCK and EXROM are mutually exclusive external sources; EXROM transitions require the specified verified HOME gateway on passive hardware.
- RAM nibble mapping: U6/U7 at 4000–7FFF, U12/U13 at 8000–BFFF, U17/U18 at C000–FFFF; first chip carries D0–D3, second D4–D7.
- Report suspect paths, not unproven component verdicts. Border/beeper outputs share SCLD dependencies and cannot guarantee reporting after clock/opcode failures.
- Bound software waits and input polling; keep external peripheral probes opt-in and profile-specific.

## Evidence and resources

Credit all source authors, archives, borrowed data/code and tools in THIRD_PARTY_CREDITS.md and the relevant test records. A future firmware help/credits view must preserve the original author credit for adapted demonstrations, including Mark Miller's128 Colors. Do not confuse128 attribute combinations with128 distinct hardware colors.

Preserve supplied manuals, schematic, ROMs and reference images. Do not modify sibling Sinistar, TSRun, AI skill, PicoCartridge or reference-library projects as part of diagnostic work without user authorization. Existing source-evidence hashes describe inspected snapshots; record a new snapshot when comparing a different version.

- Optional CPU code lives in ROM2 at4000-43FF;4000/4003/4006 are fixed entry/failure/alias-resume ABI stubs. Packed data starts4800. Only loaders writing entirely into HOME chunk3 may source ROM2. Default startup/Full must not enter this optional code.
- ROM3 asset data may be sourced only for writes wholly within HOME4000-5FFF; never overlay the destination chunk. UI tile buffers6400-69FF cannot source ROM3. ROM0 stays selected; graphics loaders remain bounded and stackless.
- Graphic keyboard uses fixed-ROM rectangles and two-row paint counts; preserve D hold counter, E input bits, IX scan budget and AF' selector. History5B00-5B28 controls colors only; BREAK is a derived CAPS+SPACE state, not ENTER+SPACE. Preserve Josef Jelinek's source art/credit and provenance.
- Active-test cancellation uses all-key release before any new key; keyboard exits use held CAPS+SPACE or ENTER+SPACE. Document the stuck-contact case that prevents arming.

- AY playback data occupies ROM2 4400-457F (24x16 bytes). Preserve the bounded I counter,14 fixed register writes, R7 input mask, HOME-safe attribute coordinates and mute boundary; corrupt table/display data cannot control execution.

- Startup R/F selector/highlight helper occupies0069-00FF after fixed IRQ/NMI vectors and is size-asserted. R selects complete RAM; F selects the normal Full suite; quick stays default. No startup selection may block waiting for keyboard release. RAM progress colors must not write tested display bytes mid-sweep.
