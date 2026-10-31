# More coverage in the Dynamic ECM butterfly experiment

Two additional TSRun cartridges preserve the original five-cell version:

| Cartridge | Scheduled cells per scanline | New-attribute choices |
|---|---:|---|
| `timex-dynamic-ecm-morpho-7.dck` | 7 | Independent per selected cell |
| `timex-dynamic-ecm-morpho-8.dck` | 8 | Two shared choices per scanline |

Both boot with the Dynamic ECM image (green border). Press and release SPACE to compare with the exact original ECM TAP (blue border). The seven-cell version provides more independent palette choices; the eight-cell version tests faster register-preloaded writes and greater coverage. Both are image-specific, fully unrolled native Z80 code.

The eight-cell version executes exactly 8 x 192 = 1536 scheduled mid-cell attribute stores per frame, compared with 960 originally. It also executes 1536 preparation stores, for 3072 attribute stores in total. These are instruction counts, distinct from the number of colors actually used by the image.

Of the 1536 mid-cell stores, 889 write an attribute value different from the first pair. In 262 cells the bitmap actually displays more than two distinct colors: 186 three-color cells and 76 four-color cells. Other scheduled stores either repeat the first attribute, use overlapping pairs, or display too little of a pair to add a third visible color. The native code still executes all 1536 stores.

The seven-cell version executes 1344 mid-cell stores, with 677 different attribute values and 193 cells displaying more than two colors. It scores better on the included averaged error metric. Please compare the images rather than assuming the denser schedule always looks better.

Each image needs the first attribute pair before scanning a cell and the second pair during the cell. Restoring the first pair for the next frame is an ordinary memory write. It is not a CPU reset or screen clear. The new versions pre-stage 768 of those writes in the blanking intervals. The screen bitmap is never cleared during steady display.

The main rendering code covers all 192 rows without per-cell loops or runtime image decoding. Unrolling removes loop overhead; instruction timing still limits how many changes can occur within a line's 128T active interval. The eight-cell kernel uses 14T between changes, with alternating 2/6- and 6/2-pixel splits. The seven-cell kernel uses 20T and 4/4 splits.

The package contains independent source directories, source photo/reference TAP copies, experimental TDEC containers, checks and reports for both versions. Each was verified for 360 steady frames and both SPACE transitions, including every visible pixel and every attribute-write address/value/time. Hardware attribute latching and contention remain unverified. These DCKs use HOME initialization plus DOCK image storage; they are not physical DOCK-only cartridge ROMs.
