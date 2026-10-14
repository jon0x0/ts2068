# Programming a physical EPROM cartridge

Release v0.3 | October 13, 2026

Use `diagnostic-v02-eprom-27C512.bin`: exactly 65,536 bytes, identical to the raw BIN and PicoROM image. It contains no DCK header. Select the programmer's device profile for your actual 27C512-compatible EPROM, load at offset 0000, program the complete image and run the programmer's byte-for-byte verification. Use the programming voltage required by that device's manufacturer. Do not program the `.dck` file.

The image is arranged in ascending CPU-address order: offsets 0000–1FFF are DOCK chunk 0, 2000–3FFF chunk 1, continuing through E000–FFFF chunk 7. A0–A15 select these bytes directly; no swapping, padding or bank reordering is needed for this wiring profile. The first five bytes are the native LROS header; cartridge entry is 0100.

The cartridge board must support a full 64 KiB ROM with all eight DOCK chunks selected, routing CPU A0–A15 and D0–D7 correctly. Qualify ROM enables for DOCK reads; it must release the data bus during writes and unselected cycles. A 32 KiB cartridge layout or board that exposes only selected chunks is insufficient. The BIN does not configure the board's bank decoder. Check your board's schematic, ROM socket pinout and enable polarity before fitting the EPROM; this is a payload for a compatible interface, not a universal plug-in socket conversion.

With a larger EPROM, use a documented adapter/address configuration; do not assume its extra address pins have valid levels. Keep other DOCK drivers out of the bus. Physical coexistence with TSPico has not been qualified. Insert/remove the cartridge with the computer powered off, then cold boot. Passive LROS entry still relies on enough HOME initialization to hand control to the cartridge.

The release's `SHA256SUMS.txt` identifies the supplied EPROM image. Save a programmer readback and compare it byte-for-byte with the original. Emulator/image-format checks establish the bytes and layout; physical board decode, access timing and electrical operation still require testing.

Sources: original TS2068 technical manual and schematic; TS2068 cartridge-development skill; NF6X-derived interface references credited in `CREDITS.md`.
