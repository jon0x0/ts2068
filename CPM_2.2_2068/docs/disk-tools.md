# Create disks and copy files

For a complete download/prepare/copy/run example with Zork II, plus COLOR and
the HI program, see [using CP/M](using-cpm.md).

Run these commands from the project/package directory. Python 3 requires no
extra packages. The tools support this project's 160KB single-sided and 320KB
double-sided CP/M layouts, 128 directory entries and user area 0. The OS lives
in the cartridge; no CP/M system tracks need copying to a new image.

## Python disk utility

Create an empty, formatted disk (choose the size matching the cartridge):

```text
python tools/cpm_disk.py create newdisk.dsk --size 160
python tools/cpm_disk.py create newdisk.tap --size 320
python tools/cpm_disk.py create newdisk.img --size 320
```

The filename extension selects Fuse Oliger DSK, one multi-CODE TAP, or raw
sector data. Existing outputs are refused unless `create --force` is used.

Copy host files onto an existing disk and inspect its contents:

```text
python tools/cpm_disk.py put newdisk.dsk HELLO.COM README.TXT
python tools/cpm_disk.py put newdisk.tap ED.COM ASM.COM
python tools/cpm_disk.py list newdisk.tap
python tools/cpm_disk.py put newdisk.tap README.TXT --replace
python tools/cpm_disk.py put newdisk.tap GAME.COM --output otherdisk.dsk
```

Use CP/M 8.3 filenames. `put` preserves the other files' CP/M records and
attributes, refuses duplicate names without `--replace`, and checks space
before replacing the destination. It rebuilds allocation inside the image;
free/deleted sector contents are not retained. CP/M records are 128 bytes, so
listed lengths include record padding. Other user areas or unsupported/corrupt
directory layouts are refused. Input images remain untouched with `--output`;
that output must be a new filename. Close/unmount the image in Fuse/TSPico
before editing the host copy; copy the finished image back to SD as needed.

For a 1.00 factory preload, create/populate one TAP first, then generate its
small loader volumes using `tspico_ram_image.py --tap newdisk.tap --output
archive.tap --volumes preload`. This is preparing a new disk, not repacking a
saved session. Include TPSAVE.COM and any desired tools when making a blank
RAMDisk image. The stock loader cannot load an arbitrary large TAP directly.

The older `create_oliger_disk.py --blank --size 160 --output newdisk.dsk`
also creates an empty Fuse disk; `--add FILE` can populate it at creation.

## CP/M FORMAT.COM

```text
FORMAT A:
```

Confirm with Y to initialize the mounted disk's directory and verify every
directory sector. Disk size comes from the BIOS; this command neither changes
geometry nor low-level formats physical tracks. Other drive letters are
accepted only if the BIOS supports them (currently A:). It removes files on
all CP/M user areas and resets allocation state. File data is not securely
erased. It does not create an SD container file; Python `create` does that.

In RAMDisk mode, FORMAT first reads TPSAVE.COM into temporary memory, then
restores it onto the formatted disk so the result can still be saved. If that
utility cannot be read, formatting is refused. Run TPSAVE after formatting or
further editing. In persistent SD mode the directory changes persist directly.
On a native `/CPM/FILES` backend, directory deletion removes its exposed CP/M
files too. A write/readback failure reports that the directory may be partly
erased; formatting is not transactional.

The utility removes itself when formatting its own drive, so copy FORMAT.COM
back from the host when it is needed again.
