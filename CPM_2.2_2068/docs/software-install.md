# Add CP/M software: one disk workflow on all targets

Choose a CP/M-80 executable for an 8080/Z80, not a DOS or CP/M-86 COM file.
Obtain the application and companion files from a source you are entitled to
use. WordStar, dBASE II and SuperCalc often need overlays, installers and
terminal configuration as well as their main COM; check the complete release's
memory/disk requirements. This console implements the ADM-3A subset used by
the supplied interpreter, not every historical terminal.

The workflow is always: collect compatible files, create/copy a supported disk,
put files into it, mount/load it on the target, run the basename, preserve changes.

## Worked example: Zork II (version-3 story)

The public collection contains Planetfall and Zork I, while the utility-only
images contain no games. The [Infocom catalog](https://eblong.com/infocom/#zork2) supplies
historical downloads; availability is not a blanket redistribution grant.
Keep your own downloaded inputs and working disks separate from release files.

From this source checkout on the PC, with Python and sjasmplus installed:

```powershell
python tools/fetch_infocom.py
python tools/build.py --profile oliger --oliger-kb 320 --assembler sjasmplus
python tools/build_planetfall.py --collection --assembler sjasmplus --output build/infocom-cpm.dsk
python tools/prepare_infocom.py --story build/planetfall/zork2-r48-s840904.z3 --name ZORK2 --template build/infocom-cpm.dsk --output build/zork2-files
python tools/cpm_disk.py create build/zork2.dsk --size 320
python tools/cpm_disk.py put build/zork2.dsk build/zork2-files/ZORK2.COM build/zork2-files/ZORK2.DAT
python tools/cpm_disk.py put build/zork2.dsk build/profiles/oliger320/files/HELLO.COM build/profiles/oliger320/files/COLOR.COM build/profiles/oliger320/files/COLUMNS.COM
python tools/cpm_disk.py list build/zork2.dsk
```

The fetch helper downloads the original CP/M interpreter source plus the three
named version-3 stories to build/planetfall. Existing files are retained.
build_planetfall configures and assembles the interpreter for this console;
prepare_infocom checks that exact build and changes its internal data filename.
Renaming a COM alone does not retarget it. `.z3` is story data, not an executable;
later `.z5`/`.z8` stories cannot be converted merely by changing the extension.

The same create/put/list steps apply to other applications; substitute their
actual file set. `put` refuses existing names unless --replace is explicit.
Keep your original disk separately and never edit an image mounted in an emulator.

### Fuse / browser

In JLO-enabled Fuse select the matching 320KB Oliger cartridge and insert
build/zork2.dsk. In the hosted TSRun 320KB page choose Open disk. At A> type
`ZORK2`. SAVE inside the game creates a file in the disk; then save/download
that disk through Fuse or the browser before leaving.

### Original TSPico 1.00 RAMDisk

Add the persistence utility from a TSPico build before loading the disk:

```powershell
python tools/build_dual.py --assembler sjasmplus
python tools/cpm_disk.py put build/zork2.dsk build/profiles/tspico-ram/files/TPSAVE.COM
python tools/tspico_ram_image.py --dsk build/zork2.dsk --output build/zork2.tap --volumes build/zork2-preload
```

Back up the existing physical /TAP/CPM/SAVE directory as a complete set to a
different PC folder. Keep /TAP/CPM/SAVE present but empty when you intentionally
want the new factory preload; otherwise the saved disk takes precedence.
Replace only the factory CPM32000.TAP–CPM32007.TAP files with the generated
matching set. Start CPM.DCK in slot 4 as usual. Type ZORK2. After the game's
SAVE and QUIT, run TPSAVE and wait for success. Do not delete an existing save
as a way to bypass an unexplained loader error.

Alternatively, the browser's Download 1.00 TAP set creates a complete reloadable
save set for the currently open image. After preserving the old set, place all
new files together in /TAP/CPM/SAVE; no PC repacking is necessary to reload it.

### TSPico v2.x

With the optional service, CPMDISK MOUNT ZORK2.DSK selects a persistent image
copied to /TAP/CPM; keep CPMDISK.COM on it if you need to switch back. With
native FILES mode, copy the COM/DAT pair into /TAP/CPM/FILES and refresh/restart.
For RAMDisk snapshots include TPSAVE.COM, choose R at startup and explicitly
export before power-off. Refer to the [firmware matrix](tspico-firmware.md):
newer protocol support by itself does not provide the CP/M SD service.
