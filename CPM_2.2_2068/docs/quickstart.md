# CP/M 2.2 on the TS2068: quickstart

This is the CP/M **2.2** port, release **cpm22-v0.1.0**. A future CP/M 3.x
port will have its own release identity. Choose the utilities disk or the
Planetfall/Zork I collection. Game stories and the historical interpreter are
separate third-party material; see the release's Infocom notice.

## Choose a target

| Target | Download | Persistence |
|---|---|---|
| Physical TSPico, including unmodified 1.00 | `cpm22-tspico-dual.zip` | RAMDisk: TPSAVE before power-off |
| JLO/Oliger-enabled Fuse | `cpm22-oliger.zip` | Save/Save As the emulated disk |
| Browser TSRun | Open the project's Run CP/M link | Download DSK, TAP or 1.00 TAP set |

Public builds use a public-domain 8x8 font. Normal TS2068 and browser displays
are 64 columns. Supported PicoVideo 4.2 selects 80 columns by default;
`COLUMNS 64` and `COLUMNS 80` choose the mode. See [video setup](picovideo.md).

## TSPico: original firmware 1.00

Extract the TSPico ZIP and merge TAP onto the card. Retain all existing SAVE
files separately before replacing a disk. The files include:

```text
/TAP/CPM/CPM.DCK
/TAP/CPM/CPM32000.TAP ... CPM32007.TAP
/TAP/CPM/SAVE/
```

This reserves SRAM slots 4/5 for CP/M and pairs 0/1, 2/3, 6/7, 8/9, 10/11,
12/13 for disk data. Their existing SRAM contents will be overwritten. Do not
choose another cartridge slot. From TSPico BASIC:

```basic
SAVE "tpi:cd /"
SAVE "tpi:cd CPM"
LOAD "tpi:CPM.DCK"
LOAD ""
```

In the loader choose SRAM, slot 4, then DOCK selection/restart; leave BOOT
unchanged. Wait through `Loading disk image to RAMDisk` and the block counter.
At A> try:

```text
DIR
STAT
COLOR
COLOR 7
SUBMIT DEMO
HI
TPSAVE
```

Confirm TPSAVE with Y and wait for its success message. Original 1.00 writes
CPMSTATE.TAP plus CPM00.TAP–CPM39.TAP (twenty chunks on a 160KB disk).
They reload directly next time. The save is disk contents, not running CPU
state. Game SAVE is not a substitute for TPSAVE. On an export failure retain
the live machine and resolve it before powering off.

Compatible TSPico v2.x storage protocol builds use the same cartridge; TPSAVE normally
writes one CPMRAM.TAP. Direct SD images/native files additionally require the
optional CP/M service, not just a newer firmware number. Read the
[firmware matrix](tspico-firmware.md) and [complete sample session](tspico-session.md).

## Fuse with Oliger/JLO emulation

Use the community JLO-enabled Fuse, not ordinary Fuse. Background and the
author's distribution are linked in the [community discussion](https://ts2068.groups.io/g/main/topic/120833431?msg=9694#msg9694).
Fuse and its SAFE/JLO ROM are not included in this release.

The Oliger ZIP provides `160/cpm22.dck` + `160/cpm22.dsk` and equivalent
`320/` files. Match both sizes and choose single-sided or double-sided
40-track drive geometry accordingly. Start the TS2068 with the selected DOCK
cartridge, enable JLO and its supplied ROM, then insert the DSK in JLO drive 0
(sometimes labelled A). Press Enter if CP/M asks for a disk.

On Windows the included launcher accepts explicit paths:

```powershell
.\tools\run_oliger.ps1 -Fuse C:\path\to\fuse.exe -Cartridge .\320\cpm22.dck -Disk .\320\cpm22.dsk
```

Try DIR, SUBMIT DEMO and HI. Before exiting, use the JLO drive menu's
Save/Save As. TPSAVE applies to TSPico RAMDisk, not Fuse.

## TSRun in the browser

Open the Run CP/M page. It boots the 320KB Planetfall/Zork I disk automatically.
The 160KB link selects its matching cartridge and disk. Click the display
to type, or use the command box. Try DIR and Build HI example.

Open disk accepts matching-size DSK, complete CP/M TAP, or all files of a
saved TAP chunk set selected together. Changing geometry requires selecting
the other startup size. Download changes before closing/reloading; Reset
retains disk bytes in the current page. Download DSK for Fuse, TAP for TSPico v2.x
transport, or 1.00 TAP set for original TSPico. Browser memory is not persistent
SD storage. The hosted player reuses the hub's pinned TSRun runtime and ROMs.

## Next steps and limits

- [Utility reference, COLOR and HI](using-cpm.md)
- [Add another Infocom game or CP/M application](software-install.md)
- [RAMDisk internals and Oliger compatibility](ramdisk-implementation.md)
- [Python disk tools](disk-tools.md)
- [Build and release provenance](release.md)

Currently A only. No simultaneous B mount, generic Oliger-ROM filesystem
support, physical WD1770 emulation on TSPico, or automatic RAMDisk writeback.
Physical original-1.00 boot and game operation have been reported; TSPico v2.x SD
service and many failure cases are validated through models. PicoVideo 4.2
support is source/model-tested; physical-board results should be reported.
