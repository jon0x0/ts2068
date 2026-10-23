# CP/M 2.2 on the TS2068: quickstart

This is the CP/M **2.2** port, release **cpm22-v0.1.0**. A future CP/M 3.x
port will have its own release identity. Choose the utilities disk or the
Planetfall/Zork I collection. Game stories and the historical interpreter are
separate third-party material; see the release's Infocom notice.

## Choose a target

| Target | Download | Persistence |
|---|---|---|
| Physical TSPico v1.00, unmodified | `cpm22-tspico-dual.zip` | Disk image loaded into RAMDisk; run TPSAVE before power-off |
| Physical TSPico v2.x: RAMDisk | `cpm22-tspico-dual.zip` | Disk image loaded into RAMDisk; run TPSAVE before power-off |
| Physical TSPico v2.x: native SD files | `cpm22-tspico-dual.zip` + optional CP/M service | Uses the SD filesystem in `/TAP/CPM/FILES`; writes persist directly to SD |
| JLO/Oliger-enabled Fuse | `cpm22-oliger.zip` | Save/Save As the emulated disk |
| Browser TSRun | [Run CP/M live](https://jon0x0.github.io/ts2068/CPM_2.2_2068/play/) | Download DSK, TAP or 1.00 TAP set |

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
CPMSTATE.TAP plus CPM00.TAPâ€“CPM39.TAP (twenty chunks on a 160KB disk).
They reload directly next time. The save is disk contents, not running CPU
state. Game SAVE is not a substitute for TPSAVE. On an export failure retain
the live machine and resolve it before powering off.

Compatible TSPico v2.x storage protocol builds use the same cartridge; TPSAVE normally
writes one CPMRAM.TAP. Direct SD images/native files additionally require the
optional CP/M service, not just a newer firmware number. Read the
[firmware matrix](tspico-firmware.md) and [complete sample session](tspico-session.md).

## Fuse with Oliger/JLO emulation

These steps use **Eduardo Fuentes's modified Fuse with JLO/Oliger disk
emulation**. Ordinary Fuse does not include this interface. Obtain the modified
build from the author's links in the
[community discussion](https://ts2068.groups.io/g/main/topic/120833431?msg=9694#msg9694)
and extract its distribution, including its ROMs folder. No TSPico is involved.

### Download CP/M

From the [project download page](https://jon0x0.github.io/ts2068/CPM_2.2_2068/#downloads),
download and extract **cpm22-oliger.zip**. Start with either matched pair:

| Disk | Cartridge to insert | Disk image to insert | JLO drive 0 type |
|---|---|---|---|
| 160KB utilities | `160/cpm22.dck` | `160/cpm22.dsk` | Single-sided 40 track |
| 320KB utilities | `320/cpm22.dck` | `320/cpm22.dsk` | Double-sided 40 track |

To use the optional Planetfall/Zork I collection instead, extract
**cpm22-infocom-oliger.zip**. Its matching files are `build/infocom-cpm.dck`
and `build/infocom-cpm.dsk`; choose **Double-sided 40 track**. You can also
download the matching 320KB game DCK and DSK directly from the project page.
The operating system is CP/M 2.2 whichever disk contents you choose.

### Configure and load in Fuse

1. Start the modified Fuse executable normally.
2. Open **Machine > Select...** and choose **Timex TS2068**.
3. Open **Options > Peripherals > Disk...**, enable **JLO Disk System
   interface**, and accept the dialog.
4. Open **Options > Select ROMs > Peripheral ROMs > JLO Disk System...**.
   Select the modified Fuse distribution's `roms/safe265.rom` if it is not
   already configured. The emulator needs this JLO ROM; it is not the CP/M
   cartridge and is not included in the CP/M download.
5. Open **Options > Disk options...**. Set **JLO Drive 0** to the 40-track
   type in the table above. Do not leave it at an 80-track default.
6. Open **Media > Disk > JLO > Drive 0: > Insert...** and select the `.dsk`
   from your chosen pair. Some builds label the first drive **Drive A:**.
   Choose **Insert...**, not **Insert New**; the supplied disk is already formatted.
7. Open **Media > Cartridge > Timex Dock > Insert...** and select the
   matching `.dck`. This is the **Oliger CP/M cartridge**, not the TSPico CPM.DCK.
8. If the cartridge does not start automatically, choose **Machine > Reset...**.
   If CP/M displays its insert-disk prompt, check the mounted disk and press
   **Enter** in the emulated screen.

You should see the CP/M 2.2 startup banner, `A: Oliger disk`, HELLO's message
and the **A>** prompt. No PowerShell commands, source checkout, Python or
compilation are required. Do not use BASIC LOAD to start this cartridge.

### Try CP/M and save your work

At A>, type:

```text
DIR
STAT
SUBMIT DEMO
HI
```

`SUBMIT DEMO` assembles and runs the HI example. On the optional game disk,
`PLANET` or `ZORK1` starts the corresponding application.

Before closing Fuse, use **Media > Disk > JLO > Drive 0: > Save As...** to
retain a working disk under a new name, or **Save** to update it. A game's
SAVE command only writes a file into that emulated disk; still save the disk
in Fuse afterward. **TPSAVE is for TSPico RAMDisk, not Fuse.** Reinsert your
saved DSK next time with the same-size cartridge and drive geometry.

If the JLO menu/checkbox is absent, this is not the required modified Fuse.
If a disk cannot be read, check that the DCK, DSK, side count and 40-track
drive setting match before changing or formatting anything.

## TSRun in the browser

**[Open the live CP/M 2.2 page](https://jon0x0.github.io/ts2068/CPM_2.2_2068/play/)**. It boots the 320KB
Planetfall/Zork I disk automatically. No local installation is required.
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
CP/M 2.2 has successfully booted and operated on physical TSPico hardware with original firmware 1.00; TSPico v2.x SD
service and many failure cases are validated through models. PicoVideo 4.2
support is source/model-tested; physical-board results should be reported.
