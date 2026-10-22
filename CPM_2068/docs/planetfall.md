# Planetfall on TS2068 CP/M / Oliger

This is a **320KB double-sided 40-track disk**, with the matching updated
64-column CP/M 2.2 cartridge. Use these two files together:

- `build/planetfall-cpm.dck`
- `build/planetfall-cpm.dsk`

The earlier 160KB cartridge has different filesystem geometry and must not be
used with this disk. Its other disks remain available separately.

## Windows GUI

```powershell
.\tools\run_planetfall.ps1
```

The launcher uses the installed JLO-enabled Fuse and selects **Double-sided
40 track**. On the older August GUI, use **Media > Disk > JLO > Drive A: >
Insert...**, select `planetfall-cpm.dsk`, then press Enter at the cartridge's
insert-disk prompt. Newer versions name that drive **Drive 0:**.

At the CP/M `A>` prompt type:

```text
PLANET
```

`LOOK` repeats the room description. `SAVE` and `RESTORE` prompt for a filename;
Enter accepts `PLANET.SAV`. At the subsequent disk prompt, leave this same disk
inserted and press Enter. Use different 8.3 save filenames for multiple games.
Use `QUIT` to leave the game, confirming when asked.

To preserve a saved game across emulator sessions, also use Fuse's JLO drive
**Save/Save As...** to write the virtual medium to the host DSK file. CP/M's
SAVE alone changes the virtual medium in Fuse's memory. Host save/reopen has not
been independently automated here.

## Files and free space

The disk includes Planetfall's `PLANET.COM` interpreter and `PLANET.DAT`, plus
all earlier tools: STAT, PIP, ED, ASM, LOAD, SUBMIT, DUMP, DDT, XSUB, HELLO,
MEMTEST and TPLOAD, the HI.ASM/DEMO.SUB example, and README.TXT.
There are **142KB free** initially. This is the full utility set, rather than
the reduced game-only 160KB prototype.

Geometry: 40 cylinders x 2 sides x 16 sectors x 256 bytes, MFM, sector IDs 1–16.
CP/M uses 160 logical tracks of 16 x 128-byte records, 2KB allocation blocks,
128 directory entries and no reserved tracks. DPB:
SPT=16, BSH=4, BLM=15, EXM=1, DSM=159, DRM=127, AL0=C0, AL1=0, CKS=0, OFF=0.

## Provenance and reproduction

The user supplied [Andrew Plotkin's Infocom catalog](https://eblong.com/infocom/#planetfall).
The disk uses the PC Masterpieces story release 37 / serial 851003, version 3,
and the original CP/M ZIP80 interpreter source from that site's `cpm80.zip`.
The story and interpreter remain their owners' copyrighted works; preparing this
personal test disk does not change their licensing.

The interpreter is assembled with sjasmplus, configured with file prefix
`PLANET`, a 63-character text margin on the 64-column console, no inverse video,
and a clear-screen reset string. The cartridge now handles the ADM-3A cursor
sequences used by the interpreter and preserves the status row while scrolling.
No game story bytes were patched. Source URLs and hashes are recorded in
`build/planetfall-cpm.manifest.json`.

With the downloaded story and interpreter source under `build/planetfall`:

```powershell
python tools\build.py --profile oliger --oliger-kb 320 --rom ..\..\TSRun\roms\ts2068-0.rom
python tools\build_planetfall.py
```

For another 320KB utility disk, `tools/create_oliger_disk.py --size 320` uses the
same geometry. Keep its matching 320KB cartridge.

## Verification

Actual source-built Fuse/JLO/WD1770 tests passed Planetfall startup, LOOK, SAVE,
RESTORE and return to game input. The 64-column screen was captured and visually
checked. Z80 backend tests cover all 2560 logical records, both sides, cylinder
boundaries, preservation of the adjacent half-sector, and error paths. Host tests
cover both DSK sides and CP/M 2KB allocation blocks with 32KB physical extents.

This establishes startup and these operations, not completion of the entire game.
The installed Windows GUI is provided for the owner's manual play test; the
automated integration tests used a newer headless build of the same JLO branch.
