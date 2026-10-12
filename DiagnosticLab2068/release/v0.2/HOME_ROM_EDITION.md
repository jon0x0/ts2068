# HOME ROM edition: U16 reset diagnostic

Release v0.2 | October 12, 2026

## What this adds

`diagnostic-home-u16.bin` is a separate **16384-byte replacement for the16KiB HOME ROM U16**, CPU addresses0000-3FFF. It starts at Z80 reset PC0000 rather than through a cartridge LROS entry. No original HOME operating-system code, cartridge discovery, cartridge /ROSCS selection or EXROM contents are needed. It executes from HOME ROM and keeps HSR at00 throughout supported tests. Embedded fonts and data come from this diagnostic image.

This can test RAM on a machine whose damaged HOME ROM contents or early OS RAM initialization prevent cartridge launch. It can also run without a cartridge connector/decoder or working DOCK selection, provided HOME mapping still works. It does not bypass CPU clock/reset, instruction fetch, shared address/data/control buses, power, SCLD HOME ROM selection, or an external device holding /BE active. A ROM that electrically contends on the bus can still prevent operation even when its contents are not used.

The cartridge remains the comprehensive edition. A replacement at U16 cannot simultaneously checksum the original U16 ROM that was removed. This HOME edition does not implement EXROM checksum or bank-switching tests, optional high-ROM CPU module, video cards or large degraded-screen fault text. RAM chip/bit identification still works through the existing synchronized border/beeper codes, with no RAM stack or RAM-resident code.

## Exact location and compatibility

**Replace U16, not U20.** The supplied original schematic marks **U16:23128(NEC),16Kx8,250ns**, next to **U19, the Z80 CPU**. U20 is the separate **2364,8K EXROM**, lower on that schematic, and is not the target. Locate the board’s U16 reference designator and original chip notch/pin1; do not rely only on case orientation or a photograph. Verify your board revision before fitting anything.

The Technical Manual §2.1.4, printed page18 (PDF page28), explicitly says a27128/2764 EPROM is **not a direct replacement** for the original ROM pinout. Its Figure2.1.4-1, printed page17 (PDF page27), shows the necessary ROM-to-EPROM adaptation. For a standard28-pin27128/27C128 at U16, use a correctly wired socket adapter/interposer or an already verified equivalent board conversion:

| EPROM pin | Adapter connection |
|---|---|
|1 VPP|+5V from pin28 for read operation; isolate from socket pin1|
|27 /PGM|+5V from pin28; isolate from socket pin27|
|28 VCC|U16 socket28,+5V|
|14 GND|U16 socket14,ground|
|Other pins|Corresponding U16 socket pins, preserving address/data and enable wiring; verify against the exact chip datasheet and schematic|

**Do not connect +5V to the motherboard’s pin27 signal.** The chip-side pin27 must be isolated before tying it high. The manual’s motherboard rework cuts that connection; a properly designed removable interposer provides the equivalent chip-side isolation without cutting the board. Never fit an unadapted27128 or arbitrary PicoROM-P28 directly into U16. Larger EPROMs require their own verified adaptation/address wiring, not just this image copied into the bottom of the chip.

## Programming and installation

1. Obtain a compatible27128/27C128 and a verified U16-to-EPROM adapter. Use a part with read access meeting the original250ns requirement. Select the programmer’s exact manufacturer/part profile.
2. Program **diagnostic-home-u16.bin**, exactly16384 bytes, at offset0000. No DCK header, byte swap, cartridge64K payload or UF2 is used. Verify all programmed bytes against the file, then compare its SHA256 with `home-manifest.json` / package checksums.
3. Disconnect TS2068 power and peripherals before opening it. Preserve the original U16 and record its orientation. If U16 is soldered, fitting a socket requires appropriate desoldering skill; do not force it out.
4. Fit the verified adapter and programmed EPROM into **U16**, aligning pin1/notches with the verified adapter/socket orientation. Leave U20 in its normal location. Inspect seating, pin alignment, supply isolation and clearance before restoring power.
5. Remove DOCK cartridges and expansion devices such as TSPico for the initial standalone test, so nothing can override the reset/HOME mapping. Power on: the diagnostic starts directly. No BASIC command is required.
6. Restore the original U16 and remove the adapter when ordinary TS2068 operation is wanted again, with power disconnected. The diagnostic is not a replacement operating system.

A PicoROM can be useful here only with a separately verified U16 electrical adapter and matching ROM-size/profile firmware. The cartridge PicoROM BIN is a different64K image; it must not be confused with this16K HOME image. No U16 PicoROM wiring or USB programming profile has been physically qualified by this project.

## Tests and feedback

Reset runs minimal CPU register/math/shift checks, HOME-image additive16-bit integrity, quick00/FF over all48K RAM and qualified55/AA address-pair checks. Hold R for Complete RAM; hold F for **HOME Full**, whose coverage differs from cartridge Full. Startup selection never waits indefinitely for key release. Complete RAM includes all patterns/walking, March, address data, seeded random and normal-refresh hold/read, with an all-six-chip result only on completion. Main7 repeats complete passes overnight.

HOME Full runs Complete RAM, three beeper tones, AY register/readback and24 guided sound steps, then the simpler keyboard diagram. MainJ opens joystick/EAR raw observation directly;5 is Sound,9/I is SCLD inhibit/arrival,0/C teaches fault codes. Output sounds, keys and joystick movements need user judgement. Unsupported cartridge-only selections show an unavailable notice instead of transferring into RAM/external ROM. Extended U CPU tests are unavailable; early CPU checks still run at every reset.

RAM failure: long low sync, then **2 / chip / bit**. Chip1-6=U6,U7,U12,U13,U17,U18; bit1-4 selects the nibble bit,5 means multiple implicated bits. See [RAM_SOUND_CODES.md](RAM_SOUND_CODES.md). Early CPU mismatch repeats8/stage1-3; qualified address alias repeats9/index1-16. Self-integrity mismatch repeats3. Failure reporting uses border/beeper; there is no large chip-text renderer in this compact edition. Silence cannot identify a failed component. These are chip-path leads, not proof the IC itself is defective.

## Implementation and validation

`scripts/build_home_rom.py` derives a separate source in `build/home/home.asm` from the maintained stackless kernel. It removes external banking, CRC gateways, optional high-ROM CPU and degraded-text code, emits a compact fixed-ROM asset pool, relocates AY records, embeds fonts, changes reset header to JP entry, and forces all HSR writes to00. Normal tests do not read/write a RAM stack; optional IRQ permits the CPU’s hardware saved-PC writes into a sacrificial sink and never returns through it. NMI restarts entry after unavoidable hardware stack writes; it is not a qualified cancellation mechanism.

`scripts/verify_home_rom.mjs` starts at PC0 with no DOCK, all-FF EXROM and dirty RAM. It checks complete/quick RAM, injected nibble data faults and audible chip codes, self-integrity failure, fixed-ROM screen loaders, mainJ inputs, HOME Full and IRQ. This establishes modeled behavior, not physical socket/EPROM timing, refresh or electrical fault survival. Original and transformed source hashes, ROM SHA256 and image-bound evidence are retained. Physical machine/adapter validation remains pending.

Sources: Timex TS2068 Technical Manual §2.1.4/Figure2.1.4-1 and §2.1.8; original TS2000/TS2068 schematic drawing335-B70500 (U16,U19,U20); [David Anderson’s reference library](https://github.com/timex-sinclair-projects/TS2068-Ref-Library); the cartridge’s existing source credits and TSRun emulator by Josef Jelinek. Any EPROM/adapter implementation must also use the actual fitted part’s datasheet.
