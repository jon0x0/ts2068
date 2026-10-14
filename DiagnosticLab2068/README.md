# TS2068 Diagnostic Lab cartridge

Release v0.3 | October 13, 2026

**[Download the complete release](release/TS2068DiagnosticLab-v0.3.zip)** · **[Web manual](https://jon0x0.github.io/ts2068/DiagnosticLab2068/docs/manual/)** · **[PDF manual](output/pdf/TS2068-Diagnostic-Lab-Cartridge-Manual.pdf)**

## Introduction

Diagnostic Lab TS2068 is a new Codex-generated diagnostic tool for checking a Timex Sinclair 2068 and helping track down hardware problems. It offers a guided Full test and a menu of individual tests, so you can check a working machine, investigate a particular symptom, or leave RAM and bank-switching tests running to look for intermittent problems. A simplified diagnostic is also supplied as a replacement HOME ROM image for replacement testing. This version can bypass the original HOME firmware and cartridge-startup dependencies, although it has fewer tests. Pending confirmation that the HOME ROM version may need a remapping to match a TS2068 addressing bug.

A major design goal is to keep testing and reporting when RAM is unreliable. The diagnostic code runs from ROM without relying on a RAM stack. It tests all 48K of internal RAM and can attempt to identify the suspect RAM chip or chips by their motherboard reference designators. The cartridge adapts its fault display where possible when display RAM is failing, and also gives chip/bit codes through beeps and border flashes. The simplified HOME ROM edition uses the sound and border codes for RAM faults. These identify suspect hardware paths; faulty wiring or control signals can sometimes look like a bad RAM chip.

Other tests cover cartridge bank switching, optional HOME ROM and EXROM checksums, selected Z80 and address-line checks, SCLD interrupt behavior, the beeper, and AY sound registers and playback. Video screens include Normal/Bright color bars, FLASH, the second display file, an extended-color gradient and color disc, high-resolution calibration patterns, and 128 attribute combinations. Interactive keyboard and joystick screens show current inputs. Joystick directions and Fire also retain a tested indication while continuing to show live press/release changes. Stopping the RAM soak gives a no-failures message if no errors were recorded, together with the completed-pass count; a detected failure goes to the chip/bit report.

## Usage

Normally, powerup startup runs a short baseline check:

- **Selected Z80 checks:** register, arithmetic and shift comparisons.
- **Cartridge integrity:** checks all eight ROM chunks.
- **Quick RAM check:** writes and reads `00` and `FF` throughout all 48K.
- **Address checks:** exercises 16 address-line pairs with opposing `55`/`AA` patterns.

It then opens the menu—about **9 seconds from normal cartridge launch** in the emulator. This can catch many basic faults, but skips the longer RAM patterns and retention tests.

Optionally hold these keys while booting:

| Key | What runs |
| --- | --- |
| **R** | Complete RAM test: eight patterns, walking bits, March C−, address-derived data, seeded random data and `55`/`AA` write/hold/read. About **84 seconds**, followed by **“All 6 RAM chips PASS”** if successful. |
| **F** | Full sequence: Complete RAM, 100 bank-switching cycles, beeper, AY register checks and sound demonstration, six video screens, then keyboard testing. About **4 minutes to the keyboard**, or **8 minutes unattended**. |
| **Neither** | The short baseline above, then the menu. |

The startup CPU and integrity checks still precede the R/F choices. Release the held selection key, then press a new key to stop at a safe boundary. Failures enter the relevant report.

**F does not include every menu option:** ROM checksums, extended CPU/address tests, SCLD interrupt checks, joysticks and continuous soak remain separately selectable. Sound, video and keyboard results require your observation.

The simplified **HOME ROM edition** supports the same R/F choices, but substitutes its own image-integrity check and omits cartridge banking and video tests from Full.

The release ZIP contains the .dck cartridge image, raw images for EPROM and PicoROM use, the simplified replacement HOME ROM image for testing with a socketed ROM, programming and installation instructions, and an illustrated manual in PDF and offline web formats. The software has passed emulator checks, but physical hardware validation is still needed (it has been tested with PicoROM), so beta testers are needed. A passive cartridge requires enough of the original machine startup circuitry and firmware to work before it can take control.

Special thanks to Carl Miles, whose TS2068 Diagnostics Cartridge documentation helped inspire the coverage and approach, and Dylan Smith and Brendan Alford, whose ZX Spectrum Diagnostics ROM provided valuable inspiration for testing with unreliable RAM and reporting failures. Thanks also to David Anderson and the TS2068 Reference Library contributors, Josef Jelinek for TSRun, Mark Miller for 128 Colors, and the Fuse contributors. Full source and inspiration credits are included in the release.


## Additional documentation and development

For combined activity, open **L**, choose **P Power cycle**, choose N one batch or C continuous, then S. Option6 alternates quiet/busy loads; enabled video rotates normal/ECM/hires, and enabled sound adds stronger AY/envelope traffic plus beeper. The start page explicitly announces TEST STARTED / RUNNING before its six-second notice. RAM reports retain original transient read/POP data and identify D0–D7 or multiple corrupted bits. Physical current draw and supply behavior still require measurement.

RAM soak leaves its between-pass status/count screen readable for six nominal seconds and says **Press any key to stop test**. Cartridge main-menu **L** opens the implemented [configurable load suite](docs/SINISTAR_LOAD_TEST.md): eight independent RAM/March/ECM/IRQ/banking/spacing/AY/stack-data toggles, one-batch or continuous operation, RAM baseline and combined presets. S starts the safe profile; R opens a separate genuine IRQ-return confirmation with optional IM2. AY generates frequent changing Speech2AY-style register traffic. These are emulator-validated workloads; physical replication of the supplied Sinistar D1-loss report remains pending. HOME retains its reduced suite and does not implement L.

Runnable ROM-only **v0.2 diagnostic suite** for the stock TS2068. It tests hardware with minimal RAM assumptions, identifies suspect RAM chip/bit paths, and retains stackless ROM control and border/beeper reports when the screen is damaged. Physical TS2068/cartridge validation is pending; advanced research modules remain explicitly distinguished in the catalog.

**Attempt to identify which RAM chip(s) are failing:** tests report suspect U6, U7, U12, U13, U17 or U18 paths and implicated data bits. When the display is unreadable, long sync followed by2 /chip /bit can identify them by sound; multiple suspect chips are reported in turn. See the [sound-code lookup table](docs/RAM_SOUND_CODES.md). Shared wiring/decode can mimic a failed IC, so chip identification is a troubleshooting lead rather than proof. CPU/cartridge execution and beeper output must still work.

[Download the packaged v0.2 candidate](release/TS2068DiagnosticLab-v0.3.zip), including both images, operator notes, credits, manifest and checksums.

The separate [16K HOME-ROM edition](release/TS2068DiagnosticLab-v0.3-HOME-ROM.zip) replaces **U16** and starts at reset without the original operating system or cartridge launch. Read [U16 installation and pinout instructions](docs/HOME_ROM_EDITION.md): a27128 EPROM requires a verified adapter; it is not a direct plug-in replacement. HOME supports the core RAM/audio/keyboard/joystick/IRQ subset; the cartridge retains the broader video/banking/CRC suite. Physical ROM/adapter validation remains pending.

**J Joysticks / EAR inputs** is a direct main-menu entry in both editions. Its [live graphical pads](docs/JOYSTICK_TEST.md) highlight Up, Down, Left, Right and Fire independently, including combinations on both ports.

[Operator manual (PDF)](output/pdf/TS2068-Diagnostic-Lab-Cartridge-Manual.pdf) and [offline web manual](docs/manual/index.html) explain selection, expected behavior, fault interpretation and actual emulated U6/U7 degraded-screen examples. Help0 then C provides fault-code training on a working machine. [EPROM programming](docs/EPROM_LOADING.md) uses the explicit65536-byte diagnostic-v02-eprom-27C512.bin; raw BIN and PicoROM payloads contain identical bytes.

[Expected durations](docs/TEST_DURATIONS.md): complete RAM about84 seconds; Full about4 minutes to keyboard, or8 minutes including its unattended timeout. Cartridge screens show rounded timing hints; these are nominal-clock emulator estimates, not live countdowns or physical measurements.

See [build dependencies and validation notes](BUILDING.md) before rebuilding.

## Build and run

Run `python scripts/build_cartridge.py`. Load [diagnostic-v02.dck](build/diagnostic-v02.dck) into a TS2068 emulator or compatible virtual DOCK. Program [diagnostic-v02.bin](build/diagnostic-v02.bin) into a compatible full64K fixed-address ROM cartridge/PicoROM configuration. These images contain all eight ROM chunks; the old three-chunk layout is insufficient. Read [v0.2 operator/implementation notes](docs/tests/V02_DIAGNOSTIC_SUITE.md) for mapping, destructive testing and optional execution exposures.

Startup checks minimal CPU register/math/shift behavior and cartridge integrity, then00/FF fill/read over all48K HOME RAM followed by qualified55/AA address pairs. Allow about7 seconds after entry (about9 including modeled native launch), including the brief status page. Extended algorithms are menu-selected. Release all keys, then press any key to cancel an active test at safe boundaries. RAM faults retain chip/bit pulses and, where one display nibble survives, large schematic-aware chip-path text. A new key acknowledges a fault and opens the menu for independent tests. Passive native LROS launch still depends on system initialization before cartridge entry.

The redesigned main menu offers Full digital + guided test; RAM/random/retention; video modes; keyboard; beeper/AY; bank stress; overnight RAM; optional ROM CRC32; optional Z80/address and SCLD IRQ; Help/credits and raw EAR/joystick observation. Menu1 shows the Full coverage overview; release then1 starts. Full runs complete RAM,100 banking cycles, sound, all six video cards and keyboard; completion separates RAM/bank/AY digital matches from user judgement of sound/video/keys. See docs/FULL_TEST_COVERAGE.md. User observations remain necessary for analog video/sound. Optional HOME/EXROM/IRQ tests are separate from that automatic sequence.

![Actual emulated main menu](build/menu-v02-actual.png)

## Verification

- `node scripts/verify_suite_ram.mjs`: native/direct quick startup plus explicitly complete RAM,34 all-RAM scenarios, including every stuck-low bit in each16K region, transient read and lost write.
- `node scripts/verify_suite.mjs`: module data copies, menus/cancellation, banking/AY/IRQ faults, ROM CRCs, gateway qualification, full sequence, soak and32 stuck-nibble renderer cases.
- `node scripts/verify_suite_reporter.mjs`:24 chip/nibble-bit mappings and preserved first-fault fields.
- `python scripts/check_suite_fuse.py` and `python scripts/check_suite_fuse_ram.py`: independent mapped-cartridge menu and completed-RAM checkpoints with stock ROMs.

Evidence binds to image hashes; immutable copies live under [docs/validation](docs/validation). Host previews and emulator checks do not establish real DRAM refresh, electrical timing, analog output or thermal reliability. v0.1 source/build and its original evidence are preserved for comparison.

## Documentation and maintenance

- [Current state](docs/PROJECT_STATE.md), [test catalog](docs/TEST_CATALOG.md), [canonical registry](docs/test-registry.json) and [change log](docs/CHANGELOG.md).
- [Fault containment](docs/FAULT_CONTAINMENT.md), [main design](docs/TS2068_DIAGNOSTIC_DESIGN.md), [banking/overnight research](docs/BANKING_AND_OVERNIGHT_TESTS.md) and [degraded display](docs/DEGRADED_DISPLAY.md).
- [Video assets](assets/video/README.md), [ROM identities](docs/rom-identities.json) and [source credits](THIRD_PARTY_CREDITS.md).
- [Future hardware assistance](docs/HARDWARE_ASSISTED_ROADMAP.md) and [PicoVideo profile](docs/PICOVIDEO_TEST_PROFILE.md) remain future/opt-in development. NMI is not currently a safe stop control.

Rebuild the catalog with `python scripts/build_test_catalog.py`. Generate host video planes with `python scripts/generate_design_assets.py`. Follow [AGENTS.md](AGENTS.md); keep executable implementation, emulator evidence and physical validation distinct.

For remote Fuse input, click its display and use physical key events or Windows On-Screen Keyboard (Start, search `osk`). Remote text/paste boxes may not generate emulator key presses. Current menus ignore already-held numeric/optional keys until a new press.

Menu9 now offers U for optional Z80/address checks, I for IRQ. CPU family8 reports stages1-5; family9 reports A0-A15 as1-16. Keyboard exit: hold CAPS SHIFT+SPACE or ENTER+SPACE. ECM uses a Sierra Lite gradient/color disc; implementation and survival limits are in the operator notes.

Every build also emits [diagnostic-v02-picorom.bin](build/diagnostic-v02-picorom.bin), an explicit65536-byte header-free PicoROM-P28/27C512 payload. [PicoROM loading instructions](docs/PICOROM_LOADING.md) include the512KBit upload command. [TSPico profile notes](docs/TSPICO_DIAGNOSTIC_PROFILE.md) cover inspected SRAM/DCK slot behavior, physical cartridge arbitration and future opt-in tests. Verify formats with `python scripts/verify_image_formats.py` before packaging. No USB upload/flash commit or external SRAM test is automatic.

AY playback now includes24 guided sound steps with yellow active labels and green progress. Run `node scripts/verify_ay.mjs` for the specific runtime checks; see the expanded AY section in operator notes. Future independent CPU-clock measurement, execution tracing and USB-retrievable logs are recorded in the hardware-assisted roadmap.

Hold R through startup for complete RAM; hold F for the normal Full digital+guided suite. The extended startup page highlights the selection; release all keys then press any key to stop. Border colors identify RAM algorithm groups. Menu9/U displays the CPU checkpoint/code guide. Text fonts are embedded in cartridge ROM; passive startup still requires enough HOME ROM function to launch.
