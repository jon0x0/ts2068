# CP/M on the Oliger/JLO interface in Fuse

For the current matched 160KB/320KB cartridges and GUI launch sequence, see
[Fuse startup](startup.md#fuse-gui-with-oligerjlo). The project-local
[TSRun page](startup.md#tsrun-browser-emulator-with-the-same-oliger-disks)
can now use these DSKs too.
See [using CP/M](using-cpm.md) for COLOR, HI and installing new software with
the same commands used on TSPico and TSRun.

The `oliger` build uses JLO's WD1770 ports directly. It boots the OS from a
DOCK cartridge and reads drive A: from the floppy image. No TSPico is required.
The display remains 64 columns by 24 rows. This is still CP/M 2.2.

## Build the cartridge and initial disk

```powershell
python tools\build.py --profile oliger --rom ..\..\TSRun\roms\ts2068-0.rom
```

Outputs:

- `build/profiles/oliger/ts2068-cpm.dck`: cartridge (no EXROM RAM disk).
- `build/profiles/oliger/oliger-cpm.dsk`: initial floppy.
- `build/oliger-cpm.dsk`: working copy of the same initial floppy.

The image contains HELLO, MEMTEST, README, STAT, PIP, ED, ASM, LOAD, SUBMIT,
DUMP, DDT, XSUB, TPLOAD and the HI.ASM/DEMO.SUB example. Approximately 109KB
remains free. TPLOAD is an unrelated optional legacy TSPico import transient;
it is not part of the Oliger disk driver.

Rebuilding replaces the initial images. Save working disks under another name.

## Windows GUI

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

## Create a disk from files

After building, make another preloaded disk from the manifest's utilities:

```powershell
python tools\create_oliger_disk.py --output build\my-cpm.dsk --add C:\CPM\MYPROG.COM
```

Or supply a directory containing only the desired CP/M 8.3 files:

```powershell
python tools\create_oliger_disk.py --directory C:\CPM\FILES --output build\my-cpm.dsk
```

The utility validates names/capacity, allocates CP/M directory entries/extents,
and writes both the DSK and a JSON manifest. Existing output requires `--force`.
This creates a CP/M filesystem, not a SAFE filesystem; SAFE CAT is not expected
to list its files. The cartridge supplies the OS, so the floppy needs no boot
tracks or system image.

## Layout and implementation

40 cylinders, one side, 16 physical sectors per track, 256 bytes per sector,
MFM recording. Sector IDs are 1–16. A standard CPC DSK container holds the media.
CP/M sees 80 logical tracks of 16 records each, 128-byte records, 1KB allocation
blocks, 128 directory entries, and no reserved tracks. DPB:
SPT=16, BSH=3, BLM=7, EXM=0, DSM=159, DRM=127, AL0=F0, AL1=0, CKS=0, OFF=0.

The backend maps LBA to cylinder=LBA/32, sector=(LBA/2)%16+1, half=LBA%2.
Each write reads the physical sector, replaces one half and writes it immediately.
No dirty cache persists across BIOS calls. It uses single-sector commands,
bounded polling and checks completion/errors and exact byte counts.

JLO port map: 8F command/status, 9F track, AF sector, BF data, B7 drive/side.
Drive 0 is B7=01, side 0. Board B's low-memory overlay is released with a data
read at address 0008 before cartridge RAM testing. No SAFE DOS routines run
inside CP/M.

## Source and verification

Eduardo's [announcement](https://ts2068.groups.io/g/main/topic/120833431)
led to [Fuse merge request #53](https://sourceforge.net/p/fuse-emulator/fuse/merge-requests/53/).
The inspected `jlo-disk` source revision is
`86199eabac8577c53ac73a37ca950f786fda8270` from
`https://git.code.sf.net/u/efuentes67/fuse-emulator`.
The installed August executable predates that revision.

Host tests validate DSK descriptors, full-image round trips and malformed media.
`tools/test_oliger_backend.mjs` executes actual Z80 BIOS calls against a functional
register model: all 1280 records, partial-sector preservation, cylinder boundaries,
invalid requests, missing sectors, short transfers and write protection. This
model does not establish WD1770 timing. `tools/test_oliger_fuse.py` is the separate
integration test for a newer Fuse with `--jlo0disk`.

The source-built headless Fuse at that revision passed cold cartridge startup,
directory listing, HELLO execution, STAT reporting 109KB free, and the complete
SUBMIT/ASM/LOAD/HI workflow through the real WD1770 implementation. Starting
without a disk also reached the insert-disk/key-retry prompt. Transcripts are
`build/oliger-{boot,hello,stat,submit,no-disk}.txt`. The existing RAM-disk build
also passed its TSRun boot, keyboard, all-sector and utility regression tests.
The WiAny ndows GUI mounting/saving workflow is provided for the owner's manual
test; it was not automated in this session. Host-file save/reopen persistence
has not yet been independently tested.

Physical Oliger hardware, multiple drives/sides, media changes, and SAFE filesystem
compatibility are outside this initial driver. Never use the new filesystem on
a valuable existing disk.
## Disk creation and file copying

Use `python tools/cpm_disk.py create newdisk.dsk --size 160` (or `--size 320`),
then `python tools/cpm_disk.py put newdisk.dsk FILE.COM README.TXT`.
`FORMAT A:` initializes an already mounted disk. See [disk tools](disk-tools.md).

