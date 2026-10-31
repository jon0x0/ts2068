# Split Personality Evolution — TS-Pico expanded SRAM TAP

Run **`split-personality-evolution-pico.tap`** through the normal TS-Pico TAP workflow. The file contains its loader, prepared SRAM data, artwork and display engine. No companion files or DCK are required. **Press and release Q or Enter to return to BASIC.** The existing standard-RAM `split-personality-evolution.tap` is still included separately.

This version retains all 101 boundary stages: vertical reveal, diagonal, sine morph, travelling sine and the four-quadrant finale. Both source pictures remain stationary. The raster selects genuine ECM and 512×192 high-resolution modes at the boundary on every scanline. It repeats after a brief black reset.

## Requirements and startup messages

- A TS2068 with **TS-Pico 2.x firmware/ROM supporting dual-port SYNC and `tpi:memdock`**, on the default ports 14/15. The reference firmware is commit `f37fc8ce76af876b6b37fa4ca6f3aee405b85a9e` from [tspico-firmware-build](https://github.com/timex-sinclair-projects/tspico-firmware-build).
- Boot the TS-Pico ROM from **flash**. The startup probe rejects a ROM booted from SRAM before touching the working slots.
- **SRAM slots 2–15 are scratch space for this demo. Existing SRAM images in those slots will be overwritten. Flash is never programmed.** Slots 0–1 are left untouched.

If the Pico or supported interface is absent, the loader prints **`TS-PICO NOT DETECTED OR` / `SUPPORTED FIRMWARE UNAVAILABLE`** and stops in BASIC. It checks the ROM version, performs a bounded live firmware handshake, and queries the current boot/DOCK settings. A responding Pico with unavailable, read-only or aliased RAM prints **`TS-PICO EXPANDED RAM` / `NOT AVAILABLE`**. An SRAM boot prints **`BOOT FROM FLASH ROM REQUIRED`**. Firmware command errors have a separate message.

Each of the seven 64K SRAM DOCK selections is tested with four distinct simultaneous window patterns, preserving the tested bytes. The loader then copies and reads back each 8K data block. This rejects a smaller aliased mapping as well as read-only storage. These probes are deliberately stronger than a single successful POKE/PEEK.

## Why it is faster

The builder prepares the complete 1,344-byte scanline-parameter stream for every stage, plus 69,064 bytes of changed bitmap/attribute pairs. The active raster reads its parameters directly from DOCK. During a transition, `POP HL` / `POP DE` patch records write HOME display RAM in two bounded blanking batches, at 55T per pair. There is no per-stage image comparison or parameter construction on the TS2068.

The CPU maps only DOCK chunks 0, 1, 4 and 5 (`F4=33h`). Its two display planes, controller, state and interrupt handler remain in HOME. Each record fits within one 16K source window, avoiding a pointer crossing the unmapped gap. Seven SRAM DOCK selections provide the storage; the loader leaves the other CPU windows in each selection alone.

Before a firmware bank change, the current parameter stream is copied to a HOME buffer over six frames. The raster then reads that buffer while the nonblocking command client changes the DOCK selection. Thus the firmware can take several frames to answer without changing the visible picture halfway through scanout. Once the new bank is ready, its artwork patches and parameters commit together. The port client uses bounded waits, paced bytes and both bare-status and string-status replies; it does not use OTIR/INIR to the Pico.

The tested model completes a loop in **17.83 seconds**, versus approximately 2½ minutes for the standard-RAM rewrite. Firmware latency and physical-machine timing can affect that result. Current v3 virtual-slot implementations may take substantially longer to change slots.

On exit, normal display/mapping and IM1 are restored, along with BASIC's saved workspace, stack, I, IX/IY and main/alternate registers. The original firmware DOCK selection is restored using the saved memory/page setting. SRAM data overwritten during loading is not restored. Exit remains bounded if the Pico stops responding.

## What was tested

- The missing-Pico path was loaded from the actual TAP through the unmodified stock TS2068 ROM loader, and stopped before SRAM-data loading.
- The positive test uses the unmodified pinned TSRun CPU/video core with a **separate TS-Pico port and bank model**. It executes the native startup probe and every native SRAM installation/readback routine, then the native display engine. It checks two loops, all 101 stages, exact per-row mode values/times and **325,632,000 visible pixels with zero mismatches**. A delayed SRAM-bank change occurs while HOME parameters drive the display.
- Q during the moving sine and Enter at the finale both restore the saved machine/BASIC state and prior DOCK selection.
- Negative cases include absent firmware response, read-only RAM, aliased windows and SRAM boot.
- A separate protocol replay against the **unmodified real TS-Pico firmware running in `pico_host`** verifies NOP, boot/DOCK queries, all seven SRAM selections and restoration of the original flash DOCK selection.

**The positive whole-TAP load on the physical TS-Pico has not been tested.** The model validates the native components and assumed SRAM mapping; the real-firmware replay validates command compatibility. Neither verifies physical SRAM-bus wiring, contention, FIFO margins or hardware raster timing. The loader's window/readback checks are intended to stop with a message if the assumed RAM mapping is unavailable. This is the expanded-memory hardware test build.

## Rebuild and tests

Python 3's standard library builds the TAP and all SRAM data:

```sh
python3 tap-suite/build_evolution_pico.py
node tap-suite/test_evolution_pico.mjs
```

Node testing additionally needs the stock ROM fixtures used by the other TAP tests; full system ROMs are excluded from the source archive. Use `tap-suite/fetch_test_roms.py` if needed. `QUICK=1` skips pixel comparisons. The supplied calibration file pins the timing constants to TSRun commit `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`.

For optional real-firmware command replay, start `tools/emu/pico_host.py` from the pinned firmware checkout with `--tcp 127.0.0.1:12068`, then run `python3 tap-suite/test_pico_protocol.py`. The firmware checkout is not part of this archive. Its [protocol documentation](https://github.com/timex-sinclair-projects/tspico-firmware-build/blob/main/docs/PROTOCOL.md) defines the packet layout, SYNC and byte pacing used here.
