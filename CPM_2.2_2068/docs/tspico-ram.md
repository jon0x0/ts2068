# CP/M with TSPico RAMDisk — legacy or TSPico v2.x storage protocol

## Version and everyday use

See the [firmware/feature matrix](tspico-firmware.md) before choosing a firmware
path. Original 1.00 uses chunk saves; TSPico v2.x single-TAP saves target the inspected
2.3.1 / ROM 2.3 interfaces, not unvalidated intermediate 1.1 firmware.
See [using CP/M](using-cpm.md) for COLOR, HI and the shared software-install steps.

The TAP-only cartridge now detects both transport families. Startup identifies
the protocol and says **RAMDisk: run TPSAVE before power off!** The firmware
1.00 target remains unmodified. A newer compatible protocol can use the same
TAP preload/export operations. For a single cartridge that also offers native
SD files, direct disk images and optional SD-to-RAMDisk copying, see
[the unified cartridge](tspico-dual.md).

This build runs native CP/M 2.2 with the 64-column console, COLOR, the normal
utilities and assembly example, and optionally Planetfall and Zork I. It loads
the initial disk from TAP files into external TSPico SRAM, then accesses that
SRAM through MEMDOCK slot selection. It does not require a firmware extension,
random SD writes, a whole disk in TS2068 HOME RAM, or an EXROM RAM bank.

**Status: CP/M 2.2 has successfully booted and operated on physical TSPico hardware with original firmware 1.00 in
64 columns, alongside native Z80/protocol model tests.** The older PicoVideo V4
display-capture problem and required 4.2 upgrade are documented separately.
TSPico v2.x interfaces and failure cases are primarily model-tested; the frozen
1.00 handler has not itself been executed here. This package does not install
firmware or automatically communicate with a device.

## Memory reservation — read before loading

The supplied build requires **SRAM slots 4 and 5 for the CP/M cartridge**.
The RAM disk replaces SRAM slot pairs **0/1, 2/3, 6/7, 8/9, 10/11, 12/13**.
These slots must all be free to use; their existing contents are lost during
disk loading. Slots 14/15 are unused. Flash and the BOOT ROM selection are not
changed. The MEMDOCK selection changes temporarily during every disk request.

Each pair exposes seven useful 8KB windows. Window 7 stays in HOME so that BIOS,
transport, stack and sector buffer remain accessible. Forty 8KB pages provide
320KB; unused portions of reserved pairs are not another CP/M drive. A private
resident stack protects calls from programs whose own stack is in a switched
window. The normal CP/M TPA remains 52,992 bytes.

The slots are currently fixed in the build. **Do not select a different cartridge
pair in the DCK loader.** Changing the reservation requires rebuilding both the
cartridge and its resident slot table; editing a file name is insufficient.

## SD card and launch

Merge the package's `TAP` directory into the SD card. Preserve your existing
files first, especially any saved exports or edited boot volumes:

```text
/TAP/CPM/CPMRAM.DCK
/TAP/CPM/CPM32000.TAP ... CPM32007.TAP
/TAP/CPM/SAVE/README.TXT
```

The original firmware's public file root corresponds to the card's TAP folder.
The loader uses CD /, CD CPM, and bare filenames; it does not assume that stock
1.00 supports TSPico v2.x absolute SD paths.

From normal TSPico BASIC:

```basic
SAVE "tpi:cd /"
SAVE "tpi:cd CPM"
LOAD "tpi:CPMRAM.DCK"
LOAD ""
```

Use the supplied DCK loader, choose **SRAM**, and select **slot 4** (pair 4/5).
Accept its DOCK selection/restart option. Leave BOOT unchanged. A separate
physical cartridge must not also drive the DOCK bus.

The screen reports that it is loading the eight TAP volumes, then verifies the
SRAM bytes and boots CP/M. No keys are needed during the transfer. The legacy
loader includes conservative delays, so the first load is not expected to be
instantaneous. On a reported load/verify failure it stops without booting from
a partial disk. A slot-restore failure halts in HOME with a red border instead
of returning to an unknown low-memory cartridge.

Why eight files: the original distribution sets BUF_SIZE to 51,200 bytes. Each
boot volume is 41,238 bytes, under 45KB, avoiding reliance on mounting a 320KB
TAP. All volumes carry matching disk-identity metadata and numbered CODE chunks.
Those small volumes are the factory preload. Saved chunks reload directly on
the cartridge. TSPico v2.x storage protocol saves may also reload from one large TAP.
No Pico configuration change is required for the legacy path.

At A>, try DIR, STAT, COLOR, MEMTEST, and SUBMIT DEMO. With the game package,
PLANET and ZORK1 start the games. SAVE inside a game writes to the SRAM disk.
CP/M warm boot retains the disk. Cold cartridge startup reloads the TAPs;
power-off loses SRAM. Export changes before either action.

## Exporting changes

Create the SAVE folder as supplied. Type **TPSAVE**, then **Y** to confirm.
Legacy mode writes CPM00..19/39.TAP and CPMSTATE.TAP. The latter records geometry,
completion and Fletcher-16 checksums so the loader can validate and reload the
set directly on the next cold boot. A failed export remains incomplete; retain
the live RAMDisk and retry before shutting down. It is not an atomic snapshot.
The Pico's current directory becomes CPM/SAVE after export.

TSPico v2.x mode writes one CPMRAM.TAP containing all the metadata/page CODE records.
It uses the firmware's APPEND command after creating and mounting that TAP;
it does not depend on the optional CP/M SD service. `TPSAVE SPLIT` produces
legacy-compatible chunks on either protocol. No PC repacking is required for
either save format. Old exports without CPMSTATE also load directly after an
on-machine 160KB/320KB choice. See [the unified guide](tspico-dual.md) for details.

For optional archival conversion or a Fuse DSK, copy the saved files to the PC:

```text
python tools/tspico_ram_image.py --chunks PATH_TO_SAVE --output saved-disk.tap --dsk-output saved-disk.dsk
```

The tool validates names, CODE sizes, TAP checksums and any saved descriptor
before producing the image. Existing outputs require --force. This conversion
is not needed to resume the RAMDisk. To preload another raw CP/M image:

```text
python tools/tspico_ram_image.py --image drive.img --output disk.tap --volumes new-boot-volumes
```

## Single-sided Oliger disks

The same cartridge also accepts 160KB media. Convert the standard Fuse DSK
to our TAP wrapper and **four** small preload volumes:

```text
python tools/tspico_ram_image.py --dsk disk160.dsk --output disk160.tap --volumes boot160
```

Preserve old volumes, then copy the four generated CPM32000.TAP through
CPM32003.TAP into `/TAP/CPM`. These fixed loader filenames are retained for
both disk sizes. Metadata selects 160KB/1KB blocks or 320KB/2KB blocks; no
cartridge rebuild is needed. Only the declared volumes are loaded. The disk
is writable in SRAM; original firmware still cannot write the DSK directly.
Legacy TPSAVE exports twenty chunks for a single-sided disk, forty for double-sided,
plus the descriptor. TSPico v2.x TPSAVE defaults to one complete TAP of either size.
To return a single-sided export to Fuse:

```text
python tools/tspico_ram_image.py --chunks saved-chunks --chunk-kb 160 --output saved160.tap --dsk-output saved160.dsk
```

Keep each export in a separate host folder. `--chunk-kb 160` selects CPM00..19
even if old CPM20..39 exports remain on the card. New saves infer size from the
descriptor; exports without one default to 320KB unless --chunk-kb is given.
DSK and TAP containers retain the same logical sectors. This supports our
40-track CP/M layout, not arbitrary historical Oliger filesystems.

## Build and verification

```text
python tools/build.py --profile tspico-ram --with-infocom --rom PATH_TO_TS2068_ROM
node tools/test_tspico_sram.mjs build/profiles/tspico-ram
python tools/package_tspico.py --profile tspico-ram
```

Omit --with-infocom for utilities only. The option uses the game/interpreter
files already prepared locally by this project. A normal Fuse build does not
emulate this TSPico memory controller; the test uses TSRun's real Z80 CPU with
the functional single-FIFO/TAP and 512KB SRAM model. It is not a hardware timing
test or a substitute for testing a real 1.00 board.

Tests cover the eight-volume loader, every logical sector, all slot-pair
boundaries, synchronous writes, preserved cartridge mapping, SUBMIT/ASM/LOAD,
binary-safe TPSAVE export, and failure on bad TAP CRC, unavailable image or
failed SRAM readback. Game tests are enabled when the game files are included.
Slot selection commands are relatively expensive; no speed claim is made for
physical hardware. A faster slot-selection interface would be a later feature.

The newer SD-image build is separate: see tspico-sd320.md. Keep the legacy DCK
on firmware 1.00; it never writes the TSPico v2.x SYNC/status port.

## Diagnosing a hardware boot failure

`DOCK RAM OK` confirms the initial low 16KiB test, not all disk SRAM banks or
communication with the Pico. The generic `RAMDisk load/verify failed` message
covers protocol detection, path/file errors, TAP reads and SRAM verification.
Updated cartridges print a preceding diagnostic line with hexadecimal fields:

- `protocol`: 00 undetected, 01 original/legacy, 02 TSPico v2.x.
- `stage`: 01 detection, 02 CD /, 03 CD CPM, 04 saved-disk discovery,
  05 volume mounting/validation, 06 page/chunk setup, 07 TAP header/data handling,
  08 installing/verifying an SRAM page. Nested reads can leave stage 07 active.
- `error`: E0 timeout, E1 synchronization, E2 checksum, E3 unsupported block type,
  E4 buffer capacity, E6 path too long. Lower values may be firmware errors;
  01 is also the loader's generic validation failure. Status 05 means an
  unrecognized command; it never authorizes ignoring saved media.
- `phase` and `token`: last transport phase/ready token (may be zero or from an
  earlier transaction); `page` is the zero-based disk page.

Record the complete diagnostic line, firmware version and selected SRAM pair.
The stage is a progress marker, not proof of the underlying hardware fault.
Do not delete existing saved disks to bypass a failure. A cold restart of the
machine and Pico before retrying avoids inheriting an unfinished FIFO transaction.

The updated report also shows `Command (LOAD=01 / SAVE=00)`, the literal command,
and `Reply:` followed by captured firmware text. Quiet firmware replies leave
that field empty. Missing original-1.00 named files use status 00 and are handled
only in optional saved-file discovery; the factory preload remains mandatory.
The loader does not enable verbose mode or alter firmware settings automatically.

The header diagnostic revision also prints the ten bytes of the most recent
encoded preheader, plus raw reply `Function` and parsed `status`. For the named
`CPMSTATE.TAP` command with zero PMR parameters, the expected header is
`42 01 FF 00 00 00 00 10 00 AC`. This is the host's encoded header, not a
measurement of bytes received by the Pico. A quiet error 05 normally shows
`Function=05 status=05`; a verbose error uses `Function=81 status=05`.

The GETINFO diagnostic revision issues `SAVE "tpi:getinfo"` through the
cartridge transport after printing the original failure details. It clears
command parameters and displays up to 192 bytes of returned information. This
query does not modify firmware, SRAM slots or disk files. `query status=00`
means transport success; other query codes do not replace the original disk
error. A firmware without GETINFO support can return 05 with no information.
Firmware and ROM versions must be distinguished; a reported ROM 1.00 alone
is insufficient to identify the installed UF2. GETINFO is absent from the
command table in the pinned original 1.00 payload inspected here.

## Intermediate firmware: use capabilities rather than version labels

Startup detects the FIFO versus status-register transport, then uses the TSPico v2.x
read-only CP/M capability query when available. A reported FW/ROM revision is
information, not authorization to assume every command is supported. Unsupported
commands retain a bounded failure path; save/append capabilities are not tested
by writing disposable files.

Legacy saved-disk discovery now requests `LOAD "tpi:dir"` first. Only exact
filenames found in the complete captured listing are opened: CPMSTATE.TAP for
a descriptor and CPM00.TAP for old chunks. This avoids opening nonexistent
optional files on versions that return ambiguous error 05 for missing names.
A listed save that cannot be opened or validated still stops boot. Quiet,
unrecognized or truncated directory responses also stop rather than silently
loading a fresh disk. Stage 09 identifies directory capability/list validation.
The cold loader allows up to 2047 captured text bytes, enough for the normal
41-file saved disk set and its directory headers/prompts. Larger directories
may require moving unrelated files elsewhere before retrying.

A cartridge reporting FW 1.00 has been observed returning 05 for the optional
CPMSTATE.TAP request while successfully answering GETINFO. Later legacy source
also explicitly returns 05 for a missing named LOAD. This does not justify
changing all error-05 responses into missing-file responses; directory evidence
removes that ambiguity. Physical boot past this point remains to be confirmed.

## Load progress, screen integrity and volume timeouts

RAMDisk loading prints `Loading disk image to RAMDisk`, followed by
`Loading block NN of TT` before each 8KiB block transfer. Every block is still
read back and compared before proceeding. The optimized CPI comparison loop
models at approximately 4.3 seconds for 40 normal pages at 3.528MHz, down from
5.5 seconds. This is CPU timing, not a physical SD transfer measurement.
The A000 bank window is transferred in 128-byte spans through the resident
bounce buffer, in both directions. Earlier builds temporarily used HOME 4000
as an 8KiB staging buffer; this exposed disk bytes as screen garbage during
preload and TPSAVE. The current implementation leaves both screen planes alone.

A physical test reached page 0A (ten installed pages) and then reported E0,
phase 04 while mounting CPM32002.TAP. That is a transport timeout at the third
factory volume, separate from the screen-staging defect. The cold loader now
allows its full housekeeping guard before each volume mount; the normal sector
I/O guard is unchanged. This guard is a timing precaution, not a verified fix
for the physical timeout. It never retries an uncertain transaction blindly.
After E0 the loader skips GETINFO because the FIFO may not be at a command
boundary, and asks for a power cycle. Failure reports clear the screen first.
Raw function/status fields after a timeout may describe the preceding completed
reply rather than the timed-out request.

## Preload speed

The cold loader retains the original byte pacing, but ordinary command and TAP
block replies now use approximately 60ms of post-reply settling instead of the
old roughly 2.4-second interval. The full long guard remains after DIR and before
volume mounts; resident disk-sector timing is unchanged. This removes avoidable
per-block delays without removing the guards associated with SD/mount transitions.
Physical timing still needs verification on the target board. A slower or faulty
transfer fails closed; it does not continue with unverified pages.
