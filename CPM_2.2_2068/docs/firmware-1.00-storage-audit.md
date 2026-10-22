# Original TSPico 1.00 storage investigation

Investigated 2026-10-21. No firmware or physical device was changed.

Implementation update: the [TAP-preloaded SRAM build](tspico-ram.md) now supplies
a 320KB disk and TPSAVE export using the legacy transport. Native Z80 models
pass; physical SRAM/slot timing remains unverified. The SD write limitations
below still apply, but they do not prevent a volatile disk in external SRAM.

## Result

### Follow-up: create one TAP and save several files inside it

Checked directly in the original frozen 1.00 bytecode on 2026-10-22. The UF2
hash below matches the inspected original distribution. The extracted flash
payload SHA256 is
`d77de8db3372e7f4c368d17d04facabf295b4fec60c2a24c3d2ac3f166dee5c6`.
The frozen `tspico.py` contains `SAVE_TS` at flash address `0x1004554c`.
Its successful save path is equivalent to:

```python
filename = cur_path + '/' + hdr[4:14].decode().strip() + '.tap'
with open(filename, 'wb') as f1:
    f1.write(hdr)
with open(filename, 'ab') as f1:
    f1.write(blk)
```

This is reconstructed from the binary, not copied from a later firmware:

| Original flash address | Decoded operation |
|---|---|
| `0x100456d2..0x100456f5` | Derive destination from this SAVE's header and current directory |
| `0x10045706..0x1004570f` | Call `open(filename, 'wb')`, enter context |
| `0x10045713..0x1004571e` | Write header, leave context (closes file) |
| `0x1004571f..0x10045729` | Call `open(filename, 'ab')`, enter context |
| `0x1004572d..0x10045738` | Write data, leave context (closes file) |
| `0x1004575d` | Return from SAVE_TS |

The `ab` string in the original firmware is therefore **not** evidence that
multiple SAVE requests can accumulate in a mounted or newly created TAP. It
appends only the data block belonging to the current SAVE, after that same
request has truncated/created the destination and written its header. Another
SAVE with the same filename executes `wb` again. The decoded successful path
has no branch that preserves an existing writable handle or skips truncation
when a TAP is already mounted. Thus create-once/write-many is not available
through this stock SAVE handler. This conclusion is static analysis; no device
or complete firmware emulator was run.

Reproduce with `tools/inspect_legacy_uf2.py`, followed by
`python tools/inspect_legacy_save.py`. The latter rejects other payload hashes
before using version-specific addresses. It uses the official MicroPython
[v1.20.0 decoder](https://github.com/micropython/micropython/blob/v1.20.0/tools/mpy-tool.py)
and `py/makeqstrdata.py` in `build/analysis/micropython-1.20/`.
The generated, address-labelled evidence is
`build/analysis/firmware-1.00-save-bytecode.txt` (also includes SAVE_ZX,
PROCESS_CMD and SA_NOT_IMP).

Stock 1.00 offers more useful positioning than our first extracted library
exposed. Its original manual documents FFW/REW navigation between TAP blocks.
A prepared TAP containing one block per CP/M sector is consequently a plausible
random-read disk. It need not be read from the beginning for each sector at the
Z80 protocol level. Actual latency, navigation parameter limits, and headerless
block transfers still require tests against 1.00.

There is no established in-place overwrite operation for a selected TAP block.
The strongest writable design using established operations is **separate small
TAP files per sector or sector group**, with reads loading a file and writes
replacing that complete small file. This does not require a whole-disk RAM copy.
It is a proposed BIOS backend, not an implemented or hardware-verified drive.

## Evidence and version boundaries

Local original distribution:
`C:/Users/Jon/Documents/ChatGPT/TS2068_TSPicoAnalysis/references/TS-Pico`.
The shipped `firmware/tspicofirmware v1.uf2` has SHA256
`20350721dbc473bac2c4a35c85fe2607d94776cf9fecf9bc55ff6b26dfac7573`.
Address-correct extraction identifies MicroPython 1.20.0, TS-Pico firmware v1.0,
2023-11-23. Reproduce with `tools/inspect_legacy_uf2.py`.

The distribution does not include the main frozen `tspico` module as Python
source. Later source is not an exact substitute. The audit reviewed the original
manual and support sources, extracted all printable frozen-firmware strings,
and compared the subsequent 1.1 source/changelog and the later initial public
firmware-build commit b2758a5. The follow-up above decodes the original SAVE
handlers directly. The whole frozen module was not decompiled or executed;
absence of a string is not proof of absence of a capability.

| Path | Evidence | Assessment for unmodified 1.00 |
|---|---|---|
| TAP load/save | Original manual and UF2 LOAD_TS/SAVE_TS names/messages; prior hardware TAP work | Established interface; payload may contain arbitrary binary data |
| TAP block positioning | Original manual printed page 21; UF2 TPI:FFW at 10041e15, TPI:REW at 10041e0d; matching movement messages at 10042028/1004203f and offset_tbl/tap_idx names | Useful selected-block read candidate; exact count encoding must be verified |
| TAP append | TPI:APPEND string exists at 10041e1d, but 1.1 source changelog explicitly says append was implemented there; original wiki says saves cannot append to mounted TAP | Do not treat 1.00 command-name presence as implementation; journal design cannot depend on it |
| Byte-offset raw reads | Subsequent beta documents BLKRCV with length and offset, labels it new; absent from extracted original command names | Later feature; no established original 1.00 entry point |
| Arbitrary overwrite/seek | Internal filesystem seek exists; later SAVE_TS uses wb or ab, not r+b with chosen offset | No established cartridge-visible in-place write interface |
| SD block driver | Original sdcard.py implements readblocks/writeblocks for MicroPython's filesystem | Internal Pico API, not a demonstrated Z80 command; cannot call it just because it exists |
| User Python extension | Original source includes TPI_extcmd.py sample with static command dictionaries | Requires installing/changing Pico-side code and confirming hook is used; outside unmodified requirement |
| Python exec/eval from cartridge | No documented original command found | No established execution hook; USB REPL is separate from cartridge I/O |
| SRAM selection | UF2 contains MEMBOOT/MEMDOCK and bank-selection state | Promising for RAM backing, but does not establish our emulator EXROM mapping or safe CP/M bank switching |

The 1.1 beta source is dated January 2024. Its changelog explicitly introduces
append, raw binary BLKRCV and new mounting/cache behavior. The b2758a5 source
also contains dual-port changes. Neither should be used to assert exact original
1.00 command semantics. In particular later FFW/REW count formats must not be
silently copied into the stock driver.

## Designs that remain within stock firmware

1. **Read-only base TAP plus separate writable TAP files.** Pack base sectors
   into a navigable TAP, keep changed sectors in a dedicated directory as
   S00000.TAP etc. A Python host utility creates and merges these. BIOS keeps
   a small presence map so missing overlay sectors fall back to the base.
2. **A directory of fixed-size TAP chunks.** For example, 1KB per file gives
   16 files for a 16KB disk and 256 for a 256KB disk. Read/modify/write a chunk
   through a 1KB cache. Larger chunks reduce directory overhead and increase
   write amplification. CP/M's 128-byte sectors remain unchanged.
3. **Whole-image load/save.** Still possible, but requires enough safely mapped
   RAM; no longer the only candidate for writable storage.

These designs replace a complete TAP file on each write; they do not add seeking
to firmware. Their failure behavior matters: original SAVE success timing,
overwrite handling, closing/remounting a saved file, directory refresh, filename
case, and incomplete writes after power loss require explicit physical tests.
Directory listings and mount-time block indexes may limit practical capacity
before the SD card does. Hundreds of tiny files are not performance-neutral.

## Next validation

Prepare a small uniquely patterned multi-block TAP and prove FFW/REW selects
the expected sectors using the original FIFO protocol. Separately save, replace,
close, remount and reload one small TAP and verify every byte. Only after these
pass should a CP/M BIOS backend be built around the operations. Keep modern
firmware models out of these tests. No timing or throughput claim is made here.

## Saved-disk discovery: original wire status and command dispatch

A physical slot-4 boot reported `protocol=01 stage=04 error=05 phase=04 token=40
page=00`. This locates the failure during saved-disk discovery; it does not
establish that the disk SRAM is faulty. The original frozen code shows:

- `PROCESS_CMD`, 100452c8: nonzero preheader byte 1 selects LOAD dispatch; zero
  selects SAVE dispatch. Named TAP mounts use LOAD; `TPI:CD ` uses SAVE.
- 10045347..10045370: named LOAD checks the directory's filename list. A missing
  filename sends `Error! File does not exists! ` with status **00** at 1004536d.
  Status 03 at 10045341 instead belongs to an invalid indexed mount.
- 100453be..100453c8: unrecognized SAVE command sends status **05** and the text
  `81 - Unrecognized command: `. It must not be interpreted as missing media.
- `CDIR`, 10044545..10044561: a nonexistent child directory keeps the current
  directory. A successful chdir then reports status 01. Thus a missing SAVE
  directory may not produce an error; optional filename checks still follow.
- `SEND_MSG`, 10045938 onward: verbose mode sends 40,81,status,text,NUL; quiet
  mode sends 40,status. Quiet replies contain no text to display.

The functional model previously used status 03 for every missing filename and
always changed to a requested child directory. It now models these original
behaviors. The loader accepts original status 00 only for optional named-file
probes under the legacy protocol; unknown-command 05 still stops boot. This
corrects a confirmed compatibility defect, but does not by itself explain the
physical 05 response. Updated diagnostics print the last exact command, its
LOAD/SAVE selection and bounded captured reply text. Plain replies show empty
text instead of an earlier command's message.

Reproduce the static evidence using:

```text
python tools/inspect_legacy_save.py --all --output build/analysis/firmware-1.00-all-bytecode.txt
```

No original firmware code is modified or executed by this decoder.

## Hardware follow-up and intermediate dispatch compatibility

Physical GETINFO reports FW Rev. 1.00 / MicroPython 1.20.0, while an optional
CPMSTATE.TAP LOAD returns quiet status 05 with the correctly encoded header.
GETINFO is not in the pinned image's built-in command table, but command-table
inspection alone cannot identify a running device: external handlers and other
firmware builds exist. The revision label is not a binary fingerprint.

The locally available `TS-Pico-Beta/src/src_new_v1.1/TS/tspico.py`, PROCESS_CMD
lines 2039–2042, explicitly calls SEND_MSG with status 5 when a named LOAD cannot
be resolved. That differs from the pinned frozen image's missing-file 00. This
is evidence for compatibility handling, not proof that the user's device is 1.1.

The cold loader now uses an explicit DIR listing capability check before legacy
optional saved-file opens. It requires a successful textual directory response
containing the directory table marker, matches complete names case-insensitively,
and refuses incomplete/oversized listings. Thus absent files are skipped based
on listing evidence; error 05 on a present file remains fatal. Version numbers
are retained as diagnostics, not used to override these checks.
