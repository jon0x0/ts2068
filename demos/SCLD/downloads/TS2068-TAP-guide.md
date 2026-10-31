# TS2068 display tricks — portable TAP collection

This pack contains **21 self-starting TAP files** for the TS2068: **20 standard-RAM demos and one TS-Pico expanded-SRAM version**. Each has a tokenized BASIC loader. The `pico` file requires supported TS-Pico 2.x firmware/ROM and uses SRAM slots 2–15 as scratch space; existing SRAM images in those slots are overwritten. It does not program flash. The other 20 files require no DCK cartridge, replacement HOME ROM or extra cartridge RAM.

Copy the TAP files to your TS-Pico storage and run each through your normal TAP loading workflow. For the 20 standard-RAM files in an emulator, eject display-demo cartridges first, select normal TS2068 ROMs, and load the chosen tape. Run the `pico` file with the supported TS-Pico ROM and expanded SRAM. The BASIC program loads the CODE block and starts the demo automatically. Load the file afresh for each run.

**Q or Enter quits every demo. Release the key to complete the return.** The program restores normal display mode, BASIC's workspace, saved registers, stack and normal interrupts. The BASIC loader then clears the screen, prints `Q/ENTER: DEMO FINISHED`, and returns to the normal BASIC prompt. You can load the next TAP without resetting.

The two wipe demos also support **Space to pause/resume**. Their Q key is now exit, replacing the cartridge's former manual upward-boundary control. The portable Dynamic ECM picture TAPs display the dynamic picture only; the cartridge's Space comparison with a second complete ECM bitmap is omitted to fit the picture, raster engine and saved BASIC workspace into standard RAM.

## Files

| TAP | Display |
|---|---|
| triple-personality-mosaic.tap | Genuine 512-mode, ECM and normal 8×8 mode; ten regions on every line; reversed order in alternate bands |
| split-personality-evolution-pico.tap | Expanded-SRAM version, all 101 stages, approximately 18 seconds per loop in the model; prints a message if the supported Pico/RAM interface is unavailable |
| split-personality-evolution.tap | Looping 101-stage vertical, diagonal, sine-wave and four-quadrant ECM/highres reveal; approximately 2½ minutes per loop |
| split-personality.tap | ECM left, yellow/blue highres right; color strips and checker textures |
| timex-color-atlas.tap | All eight border colors, all highres ink/paper combinations and sixteen ECM palette entries |
| attribute-race-lab.tap | Sphere/floor image and four-color-cell diagnostic with a mid-screen divider |
| attribute-speed-lab.tap | Back-to-back 7T attribute-write phase sweep |
| dynamic-ecm-probe.tap | Single changes, adjacent STORE16 writes and a dense triple |
| dynamic-ecm-push.tap | PUSH version of the adjacent-cell test |
| dynamic-ecm-exchange.tap | EX (SP),HL version of the adjacent-cell test |
| dynamic-ecm-morpho-5.tap | Butterfly, five independently scheduled cells per line |
| dynamic-ecm-morpho-7.tap | Butterfly, seven-update schedule |
| dynamic-ecm-morpho-8.tap | Butterfly, eight-update schedule |
| dynamic-ecm-prismatic.tap | Prismatic Orbit rainbow artwork |
| dynamic-ecm-macaw-sierra-lite.tap | Macaw, adaptive Sierra Lite and ten-position raster engine |
| dynamic-ecm-macaw-sierra-line.tap | Macaw, adapted Sierra Line |
| dynamic-ecm-macaw-sierra2.tap | Macaw, two-row Sierra |
| dynamic-ecm-macaw-9-independent.tap | Macaw, nine independent replacement attributes |
| dynamic-ecm-10-prover.tap | Ten four-color cells on each of 64 consecutive test lines |
| ecm-hires-wipe-morpho-title.tap | Butterfly ↔ first highres title, fine/64-column fonts, Celtic braid, checkerboard and white bar |
| ecm-hires-wipe-frog-scene.tap | Frog ↔ highres shaded 3D scene and fine-text/checkerboard panel |

The wipe pictures remain stationary. The boundary moves one scanline per frame, with 240-frame holds (approximately four seconds). An 8-bit LFSR selects upward/downward reveals, and the loop repeats. All 193 boundary positions, both mode arrangements and Space pause/resume were tested. These two independent TAPs cover the four images from the cartridge sequence while fitting standard RAM.

## Coverage limits

- **The `pico` version is an expanded-memory hardware test build.** Native startup, SRAM installation, display timing, pixels and exits were tested with a separate Pico port/bank model; its commands were also replayed against the real unmodified firmware. The complete positive TAP load on physical TSPico is untested. Boot from flash; the loader rejects an SRAM boot and tests writable, independent RAM windows. See `Split-Personality-Evolution-Pico-TAP.md` for requirements and scope.

- **Split Personality Evolution is a standard-RAM rewrite.** It retains the original artwork, all 101 stage shapes and looping sequence, with genuine ECM/highres switching and Q/Enter exit. Its animation is slower than the banked cartridge: approximately 2½ minutes per complete loop. A brief black reset occurs between loops. See `Split-Personality-Evolution-TAP.md` for its memory layout and verification.
- **The original single four-image looping cartridge is adapted into the two pair-wise wipe TAPs above.** Its complete expanded image bank layout does not fit alongside the restored-BASIC runtime in this standard-RAM implementation. The two pair files are not an exact replacement for the original four-image order in one program.
- Older duplicate DCKs, previous revisions and the DOCK-bootstrap variants of the three Dynamic ECM probes are not duplicated; the pack uses their current display effects.
- These are emulator-verified TAPs intended for a TS-Pico command-line workflow. The physical TS-Pico firmware, loading UI and machine timing have not been tested here. In particular, the physical SCLD's attribute latch behavior and contention remain unverified for Dynamic ECM.

## How the RAM versions work

The loader reserves memory with CLEAR 32767 and loads CODE above 0x8000. It avoids loading ECM attributes over the live EXROM tape-loader workspace. At entry, the program saves the BASIC workspace at 0x5B00–0x7FFF, including the loader and its stack. For static pictures, it reuses the image source buffer by swapping the old BASIC attribute-area bytes with the new display attributes. This makes room for the raster code and the saved workspace without requiring banked memory.

The demos use an IM2 vector table and a RET interrupt handler in saved BASIC RAM. This avoids replacing the system ROM interrupt vector. The active scanout timing is adjusted for the 33T IM2/RET/DI path and exit-key scanning. On exit, all saved BASIC bytes are restored, along with the saved main/alternate registers, IX/IY, I and stack; normal IM1 interrupts and mode zero are re-established. The live screen is then cleared by BASIC after the machine-code routine has returned.

The wipe versions keep two row-compressed images above 0x8000. A PackBits decoder expands only the incoming 64-byte row into a small buffer and copies its two display planes after scanout. This preserves the stationary-picture reveal without holding two fully expanded source images in addition to the live display and BASIC backup.

The color atlas prewrites the following line's FE border color while the current line is in highres, which ignores FE's border color. This keeps the next line's entire left border the intended color. Split-mode I/O phases account for TSRun's actual OUT I/O-cycle offsets, rather than using instruction-start timestamps for port changes.

## Verification

Every one of the 20 standard-RAM TAPs was loaded through the stock TS2068 HOME/EXROM tape loader in unmodified TSRun, rather than being tested only by injecting its payload into RAM. Both Q and Enter were tested for every file from equivalent post-load machine states. The return checks verify the original BASIC return address, saved register values, stack, normal mode/mapping and saved BASIC memory (excluding the consumed free stack slots). BASIC subsequently executes its CLS/PRINT line and produces its normal `0 OK` report.

Across those 20 standard-RAM files there are 22,305 checked display frames and 3,423,283,200 visible pixel comparisons, with zero mismatches. Each static effect has 120 checked frames. Each wipe has 1,150 checked frames covering all boundary positions and both mode arrangements. Evolution adds 17,965 frames covering two complete loops and all 101 stages; both per-line mode writes are checked for value and I/O timing. Additional Evolution exit checks cover the moving sine wave and four-quadrant finale. The tests also verify wipe pause/resume. `validation.json` contains the combined per-file results, and the separate Evolution reports preserve its full pixel and late-stage exit results.

The Pico model adds 2,155 frames, two complete loops, all 101 stages and 325,632,000 visible pixel comparisons with zero mismatches. Q/Enter, absent/unresponsive Pico, read-only and aliased RAM, and SRAM-boot rejection were checked. These results are separate from the 20 stock-ROM positive loader tests; the Pico model does not constitute a physical positive loader test. The real-firmware command replay is supplied in its own report.

The native TSRun revision is pinned to 41dbe3e41c692a1806f2cb900c5a0faa1549ae77. Dynamic ECM pixel references come from the previously validated cartridge captures; the split-mode and wipe references calculate expected pixels independently. The actual expanded images, palette constraints and mode-switch effects are preserved; the emulator was not changed to make the TAPs work.

## Build sources

The separate source archive contains the RAM builders, tape writer, tests, pinned emulator modules and the original demo assets needed by those builders. It excludes full system ROM images. Building the TAP files uses Python 3's standard library only:

```sh
python3 tap-suite/build_suite.py
python3 tap-suite/build_wipes.py
python3 tap-suite/build_evolution.py
python3 tap-suite/build_evolution_pico.py
```

Full loader/exit verification additionally needs Node.js and stock TS2068 ROM fixtures. Supply your own ROMs at the paths used by the tests, or use the optional fixture-download helper:

```sh
python3 tap-suite/fetch_test_roms.py
node tap-suite/test_suite.mjs
node tap-suite/test_evolution.mjs
node tap-suite/test_evolution_pico.mjs
```

The fixture helper downloads the public TSRun repository's ROMs. The test-suite cloning step starts the second exit-key test from the same state reached by an actual ROM load; it does not bypass the tape loader. Builders are tailored to the supplied demos and are not a general DCK-to-TAP converter.
