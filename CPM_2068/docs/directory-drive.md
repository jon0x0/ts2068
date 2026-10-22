> Experimental modern-firmware prototype. Incompatible with the required unmodified TSPico firmware 1.00. Excluded from the default package. See [stock 1.00 status](stock-1.00.md).

# Ordinary SD directory as CP/M drive A

The combined cartridge supports a **256KB logical CP/M drive backed by individual
files in a configured TSPico SD directory**. The default is `/CPM/FILES`. Put
CP/M utilities and data files there; no disk image and no import command are
required. `DIR`, `TYPE`, `PIP`, `REN`, `ERA`, the editor and assembler see those
files through the normal CP/M BDOS/BIOS path.

The service is in `firmware/cpm_directory.py`, called by `cpm_service.py`. CP/M
still issues 128-byte sector requests. The service synthesizes directory entries
and allocation mappings from native files at mount, reads their contents on
demand, and converts committed CP/M directory updates back to native files.
It keeps metadata in Pico RAM, not a complete 256KB disk image. The private
`.cpm-work` subdirectory holds unclosed data blocks and recovery bookkeeping.

## Configure and install

The build/package does not install anything or modify an attached device.

1. Copy `CPM/FILES` from the combined package to `/CPM/FILES` on the SD card.
   Merge deliberately and preserve existing files; replacing a file replaces
   its contents. The directory is initially seeded with the standard utilities,
   HELLO, MEMTEST, TPIMPORT and the HI.ASM/DEMO.SUB example.
2. Put `cpm_service.py` and `cpm_directory.py` on the Pico flash root. Copy
   `cpm_config.example.py` as `cpm_config.py`, or edit the existing file:

   ```python
   CPM_STORAGE = 'directory'
   CPM_DIRECTORY = '/CPM/FILES'
   ```

   The path is the public SD path, not a 2068 RAM address. Another directory is
   allowed. It must already exist. Set `CPM_STORAGE='image'` only to use the
   optional older 48KB `/CPM/DRIVEA.IMG` backend.
3. Preserve existing extension commands and merge the new ones in the Pico's
   `dev_extcmd.py`:

   ```python
   from cpm_service import EXT_SA_FUNCT as CPM_COMMANDS
   EXT_SA_FUNCT.update(CPM_COMMANDS)
   ```

   This requires the compatible modern firmware extension hook and SD/channel
   helpers described in tspico.md. It does not support the legacy 1.00 protocol.
4. Load `CPM/CPMBOOT.DCK` into an unused **SRAM** slot pair with TSPico's DCK
   loader, retaining the normal BOOT selection. Start that DOCK cartridge. The
   cartridge still needs writable lower DOCK RAM and both display shadow pages.
   Do not use an occupied SRAM pair or drive the same DOCK with two devices.

At startup a validated directory capability selects the larger DPB. The screen
states **A: TSPico directory 256K**. With the supplied files, STAT reports about
211KB free. If this service is unavailable, existing stock read-only-image and
emulator RAM fallbacks remain. Read the startup line to know which drive is in
use. The configuration does not silently convert a stock channel into a writable
directory service.

## Everyday use

```text
DIR
STAT
PIP COPY.COM=HELLO.COM
COPY
REN OTHER.COM=COPY.COM
ERA OTHER.COM
SUBMIT DEMO
HI
```

`SUBMIT DEMO` creates HI.HEX, HI.PRN and HI.COM as ordinary files in the SD
directory. New and modified files become visible when CP/M closes/commits their
directory metadata. Pending data is staged privately while a file is open.
Normal CP/M programs should close output files before returning or resetting.

## Names, capacity and host edits

- Single CP/M user area **0**; subdirectories and long/incompatible names are
  ignored. Valid short names are case-insensitive in CP/M; lowercase native
  names can be read. Case collisions fail mounting rather than choosing one.
  Extensionless short names are supported. New/renamed files use uppercase.
- Capacity is 256KB, including a 4KB directory: 252KB of allocated data blocks,
  128 directory entries, 1KB allocation blocks, 128-byte records. Large files
  use multiple CP/M extents. Too many valid files/extents or too much content
  fails mounting; valid files are not silently hidden. Capacity depends on
  rounded allocation sizes, not just the sum of native file byte lengths.
- Untouched files and pure renames retain their exact native byte lengths.
  Modified files acquire CP/M's 128-byte record length. Text reads pad a final
  short TXT/ASM/SUB record with Ctrl-Z; binary files pad with zero. FAT attributes
  are not translated; CP/M attributes persist only for that mounted session.
- Add/edit files from another computer while CP/M is stopped, then cold-start
  the cartridge to remount. A warm boot retains the mounted allocation view.
  A metadata snapshot detects many outside changes and refuses further commits,
  but concurrent writers are unsupported and same-size/time edits cannot always
  be detected. Do not modify the directory through another TSPico client while
  CP/M is using it.
- `.cpm-work` is reserved to this backend. Its owner marker prevents accidental
  reuse of a foreign directory. Do not change its files while mounted. A cold
  mount recovers an incomplete metadata transaction, then discards unclosed
  scratch blocks. That can lose output a program had not closed.

## Recovery and limits

All replacement file contents are staged before native names are changed. A
transaction record and backups allow rollback if installation fails, or cleanup
after a completed commit. This is tested with injected rename failures and an
interrupted transaction. It is not a journaled filesystem or a guarantee against
SD corruption/power loss: FAT, card caches, flush/unmount behavior and physical
hardware still matter. Keep backups of valuable files.

The host tests exercise the actual firmware handlers and directory class. The
end-to-end test runs the actual CP/M/Z80/BIOS in TSRun, with a functional TPI wire
model forwarding requests to those handlers and real test directories. Boot,
native create/copy/rename/delete, SUBMIT/ASM/LOAD, remount/recovery, multi-extent
files and a volume larger than 48KB are covered. **Physical TSPico SRAM/FIFO
timing and memory budget are not yet validated.** The adapter avoids buffering
all file data in RAM, but maximum-directory RAM usage must still be measured on
the intended firmware/board.

The transport/storage separation is unchanged. An Oliger controller backend can
continue to expose sectors without using this native-directory translator.
