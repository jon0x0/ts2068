# Timex Dynamic ECM — cartridge feasibility tests

These are native Z80 cartridge diagnostics, not an image viewer or a claimed new full-screen hardware mode. Each targeted cell receives ONE old-to-new attribute change during the beam test. The earlier discussion of needing two changes concerned obtaining more than four colors in a cell, not obtaining four.

## Start with the TSRun cartridge

Insert `timex-dynamic-ecm-probe.dck` into TSRun and reset. It boots independently of the system ROM. The two companion cartridges, `timex-dynamic-ecm-push.dck` and `timex-dynamic-ecm-exchange.dck`, change only the middle experiment. Reset or remove the cartridge to exit. No tape files are supplied.

Each screen has three bands. Red/blue checker strips on the left and green/yellow strips on the right are static references; the narrow center strip contains the timed tests. Inspect individual horizontal rows, preferably with integer zoom and CRT filtering disabled.

1. **Single change / phase sweep:** one attribute address is reset before its cell, then changed once. The instruction-start phase sweeps eight whole-T-state positions around the cell across successive scanlines. Targets are at column 15, rows 44–79.
2. **Adjacent-cell burst:** two consecutive attribute addresses are reset, then written by one instruction. Instruction-start times sweep 32 positions, including the earlier start times needed for actual bus writes later inside an instruction. Targets are columns 14–15, rows 98–129.
3. **Dense triple:** three adjacent attribute addresses are preloaded in BC, DE and HL. `LD (BC),A`, `LD (DE),A`, `LD (HL),A` change each attribute once, with 7T between changes and no address increment or value reload between them. Targets are columns 14–16, rows 146–177. This tests a denser schedule than the earlier spaced-column demos.

An old-pair reset occurs before each test; it is not an additional mid-cell change. Row timing is 224T in the tested TSRun core. The border stays green; graphics and labels remain stationary.

## What to look for on a physical TS2068

Look for **red, blue, green and yellow within the same eight-pixel horizontal cell**, rather than merely different colors on different rows. A cell that is entirely red/blue or entirely green/yellow still has only two colors. In the middle band, check whether BOTH adjacent cells ever contain four colors on the same row.

The three middle instructions are deliberately different:

| Cartridge | Middle instruction | Nominal time | Destination bytes |
|---|---|---:|---|
| probe | `LD (nn),HL` | 16T | adjacent, ascending |
| push | `PUSH HL` | 11T | adjacent, descending |
| exchange | `EX (SP),HL` | 19T | the two bytes at SP and SP+1 |

The stack variants temporarily point SP into the attribute area with interrupts disabled, then restore it before the next frame. The attribute resets and the sweep are otherwise the same. Zilog's timing tables show PUSH's two 3T write cycles, but those writes address different bytes. The exchange operation also has reads, and its hardware bus order must not be inferred from TSRun's callback order.

TSRun currently places both memory-write callbacks from a two-byte instruction at instruction start. Consequently all three middle tests produce the same emulator color counts. Actual bus-cycle timing can differ; agreement in TSRun does not prove that the instructions behave identically on hardware.

Real display-memory contention can delay writes and shift later rows. The phase sweeps are a diagnostic aid, not a contention-calibrated raster engine. Seeing a split would be positive evidence worth investigating. Seeing no split is not by itself a complete hardware proof unless timing is confirmed. The SCLD's attribute-fetch/latch behavior remains the central uncertainty.

## DOCK-only cartridges for a physical loader

The ordinary names above use DCK HOME preloading, as the previous TSRun demos do. They are not directly burnable EPROM images.

The archive ALSO includes `*-hardware.dck` and matching 64KB `*-hardware.bin` ROM images. These contain only DOCK ROM pages. Their native bootstrap copies the bitmap, attributes and test kernel into HOME RAM and then runs using an uncontended RAM IM2 interrupt handler. They do not depend on a loader preloading HOME RAM.

For a loader that maps the supplied DOCK pages, manual entry from Timex BASIC is:

```
OUT 244,64: RANDOMIZE USR 49160
```

The header at DOCK $8000 follows the documented LROS layout, but automatic ROM startup has not been verified. Use the explicit entry above. A particular TSPico or cartridge board's ROM-mapping setup has not been tested on a physical machine; the 64KB BIN layout and source are provided for that step. Running the diagnostic takes over the display and system-variable RAM; reset to return to BASIC.

## Emulator results

All six DCK variants were tested for 120 steady frames each using unmodified TSRun commit `41dbe3e41c692a1806f2cb900c5a0faa1549ae77`. Tests check every visible pixel and the exact address, value and instruction-start timestamp of every attribute write. The DOCK-only variants are entered at the manual mapping/address above, exercising the real copy bootstrap and RAM interrupt handler. They are not tested by preloading their target RAM.

Each variant gives these TSRun results:

| Band | Target cells with two colors | Target cells with four colors |
|---|---:|---:|
| Single change | 24 | 12 |
| Adjacent burst | 58 | 6 |
| Dense triple | 64 | 32 |

This is not four colors in every cell. It measures which cells in these schedules split in TSRun. Native hardware is unverified. The converter and image-format work remains contingent on establishing a usable display method.

## Rebuild and check

Python 3 + Pillow generate the artwork and native cartridges; Node.js runs the checks:

```
python build_tests.py
python fetch_tsrun.py
node test_tests.mjs
```

The source ZIP contains schedules, RAM snapshots, ROM images, preview PNGs and the validation report. It contains no system ROM. `fetch_tsrun.py` downloads pinned emulator modules separately.

References: Zilog Z80 CPU User Manual UM008011-0816, https://www.zilog.com/docs/z80/um0080.pdf ; TS2068 Technical Reference Manual section 2.1.8.3 (display fetches), https://device.report/m/3253f371946016a17699f910efcc842ff5b716271ea9c0ddad00e6ef439c547d ; LROS layout, https://github.com/timex-sinclair-projects/2068-TAP-To-Cart/blob/main/docs/Creating-TS2068-Cartridges.md .
