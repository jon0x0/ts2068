Release v0.2 | October 12, 2026

TS2068 Diagnostic Lab cartridge v0.2

Power-on: ROM0 CPU consistency, cartridge integrity, quick00/FF all48K RAM, then qualified55/AA opposing address pairs. About7 modeled seconds after entry/about9 including native launch and the brief status page. Startup is limited.
Hold R through startup for complete RAM only; hold F for normal Full digital+guided tests (RAM,banking,beeper/AY,video,keyboard). Release all held keys,then a new key stops. CPU,ROM CRC and IRQ tests remain separately selected.

Screen RAM is tested too,so the startup page explains RAM-phase border colors. Fault text adapts to a surviving RAM nibble; border/beeper codes remain ROM-controlled. CPU menu9/U shows expected checkpoint/failure counts and limits. Fonts are embedded in cartridge ROM; passive LROS launch still needs enough HOME initialization. Independent no-HOME reset boot is future work.

Files:
diagnostic-v02.dck: Fuse/compatible virtual DOCK (nine-byte header +65536 ROM bytes).
diagnostic-v02.bin: exact64K physical ROM layout.
diagnostic-v02-picorom.bin: explicit PicoROM-P28/27C512 payload,identical to BIN. Use PICOROM_LOADING.md for512KBit upload/persistence instructions. Every8K chunk must be decoded.

Read OPERATOR_NOTES.md for algorithms,register contracts,fault codes and remaining scope. Tests overwrite HOME memory. Physical validation remains pending. Use the documented release/new-key stop or keyboard exit chord.

AY has24 guided steps with active yellow labels/green progress dots. TSPICO_PROFILE.md covers unverified SRAM/arbitration and development-firmware profiles; banners may be stale. HARDWARE_ROADMAP.md records future independent clock measurement,execution traces and USB logs. These helper features are not implemented.

EPROM: diagnostic-v02-eprom-27C512.bin is the explicit64KiB programmer image; see EPROM_LOADING.md.
Read TS2068-Diagnostic-Lab-Cartridge-Manual.pdf or open manual/index.html for operating instructions, fault interpretation and actual emulated U6/U7 fault-report examples. Help0 then C provides audible fault-code training. Color bars use Normal and Bright labels.

Boot8/stage1-3 indicates a CPU/instruction-path comparison mismatch; boot9/index1-16 indicates a qualified HOME address-pair mismatch (1=A0 to16=A15). Codes use beeper and white/black border without trusting the screen/keyboard and repeat until reset. See BOOT_DIAGNOSTICS.md. No global opcode/boot failure reporting is guaranteed.

Mixed-case menus use the embedded TS2068 font, including lowercase; no extra font memory or live HOME ROM dependency. Keyboard legends and large RAM-path fault glyphs remain uppercase.

Full: main1 overview, release then1 to start (F startup remains direct). Digital matches cover complete48K RAM,100 bank cycles and AY masked register readback. You must judge sounds, six video cards and every key; timeout is not keyboard certification. See FULL_TEST_COVERAGE.md and TS2068-Diagnostic-Lab-Cartridge-Manual.pdf. Completion lists excluded tests; no whole-machine PASS is claimed.

Manual introduction (page3) explains capabilities, detectable faults, reporting with failed hardware and limits; read it before interpreting results. The same introduction is the first chapter of the offline web manual.

Keyboard uses credited Josef Jelinek/TSRun artwork adapted to native resolution. White unseen, green held, cyan released. CS=CAPS, EN=ENTER, SY=SYMBOL SHIFT, BR=BREAK; both CAPS share one input. BREAK follows CAPS+SPACE, distinct from ENTER+SPACE exit. See KEYBOARD_ART.md.
