> Historical 48KB `combined` prototype design, not the current setup guide.
> Use the [firmware/feature matrix](tspico-firmware.md) and
> [current startup guide](startup.md). Its old fixed-size paths/commands below
> describe that prototype; current service configuration is in
> [tspico-directory.md](tspico-directory.md). Original 1.00 uses RAMDisk instead.

# Combined emulator / TSPico cartridge

Explicit `--profile combined` produces one `build/ts2068-cpm.dck`. It contains
both the existing emulator RAM disk and the resident TSPico v2.x adapter.
The copy at `build/sdcard/CPM/CPMBOOT.DCK` is byte-identical. The inspected
TSPico DCK loader consumes its first DOCK block and ignores the later EXROM
block; the latter remains available to emulators.

The same program now has three disk choices, in priority order:

1. Validated optional TSPico CP/M service: drive A is a writable SD image.
2. Stock TSPico v2.x channel interface and a readable supplied image: drive A is
   read-only. Writes fail rather than corrupt binary data containing 17h.
3. No usable TSPico image: use the preloaded emulator EXROM RAM disk, after
   checking its directory signature. If neither disk exists, stop with a clear
   message. Legacy 1.00 is not a raw-file backend.

This selection happens once at cold boot. Warm boots keep the selected image.
The code never changes TSPico BOOT/DOCK slot configuration. It uses SRAM that
has already been assigned to the cartridge, rather than searching and replacing
possibly occupied slots. It still requires writable DOCK pages 0-3, including
the two display shadows. A Flash-loaded or ROM-only cartridge is insufficient.

**Status: hardware-test candidate.** The actual Z80 code passes a functional
TPI model and a simulated first-block-only SRAM cartridge mapping. This is not
a physical FIFO timing, SRAM write-cycle or electrical compatibility result.

## SD card and SRAM setup

The build stages files under `build/sdcard/CPM/`. Copy the directory to the public
SD root only after reviewing it. In particular, preserve an existing
`/CPM/DRIVEA.IMG`: replacing it resets the CP/M filesystem and loses its files.
The project does not copy anything to a device automatically.

Use the TSPico normal DCK loader for `/CPM/CPMBOOT.DCK`. Choose SRAM and an unused
even slot pair, keep the existing BOOT selection, and start that DOCK cartridge.
The owner's earlier virtual-DOCK instructions describe this workflow. Do not
combine it with a separately driving physical cartridge without an appropriate
hardware profile. TSPico's exact SRAM mapping/write qualification remains to be
confirmed on the board; startup tests the lower 16KB before entering CP/M.

TSPico v2.x firmware with ordinary file channels can run the image read-only without
installing the extension. The screen states READ ONLY. `HELLO`, `STAT`, `DIR`
and reading files work; assembler output, SUBMIT scratch files and other writes
require the extension. The 48KB image format is identical on both backends.

## Optional binary-safe writable service

`firmware/cpm_service.py` adds four commands through the TSPico v2.x firmware's
documented `EXT_SA_FUNCT` hook. It does not replace the ROM or channel parser.
Keep that file as `cpm_service.py` on the Pico flash root, and **merge** its
handlers into your existing `dev_extcmd.py`, preserving existing handlers:

```python
from cpm_service import EXT_SA_FUNCT as CPM_COMMANDS
EXT_SA_FUNCT.update(CPM_COMMANDS)
```

The firmware must provide the inspected 2.3 extension hook, `CH_CALL`, channel
packet/DMA helpers, and compatible SD management. These interfaces were checked
in the owner's local `references/tspico-firmware-build` source. The supplied
extension has not been deployed or physically tested. It is opt-in; installation
instructions do not constitute a claim that it supports old firmware 1.00.

Commands are fixed to `/CPM/DRIVEA.IMG`, exactly 49,152 bytes:

| Command | Parameters / answer |
| --- | --- |
| `tpi:.cpmcap` | Validates image size and read/write open, returns signature/geometry |
| `tpi:.cpmrd` | PMR1=LBA 0-383; returns 128 bytes plus XOR |
| `tpi:.cpmw0 <128 hex digits>` | Stages the first 64 bytes for PMR1=LBA |
| `tpi:.cpmw1 <128 hex digits>` | Checks matching LBA, commits all 128 bytes, flushes/closes |

No write occurs after just the first half. Bad hex, range, length or mismatched
halves fails. Reads/capability requests cancel an incomplete staged write. Data
can contain every byte value, including 17h. CP/M sector writes are synchronous;
they are not a journal and are not guaranteed atomic across power loss.

## Import individual existing SD files

With the TSPico v2.x channel service available:

```text
TPIMPORT /CPM/NEW.COM NEW.COM
NEW
```

This reads a raw SD file (up to 32KB) and creates a file in the current CP/M
drive. It refuses to overwrite an existing local file, rejects malformed 8.3
names, and deletes a partial destination on a reported write failure. Source
paths must match the SD filename's case; the current CCP/input uses uppercase.
The destination supports letters/digits and a required extension. SD reads
are binary-safe without the extension. A read-only drive cannot receive imports;
use emulator RAM or the writable SD backend. A normal SD directory is not yet
exposed as a virtual CP/M drive; this command imports files explicitly.

## Detection and build separation

The probe checks TSPico v2.x idle, sends a bounded preheader, validates ACK=1 and
TSPico v2.x MID=F7, and only then uses TSPico v2.x SYNC. A legacy/busy response is declined;
floating FF and stale ACK with idle status do not identify hardware. Device use
must be serialized and probing must start with no transaction in progress.
Legacy reads consume FIFO tokens, so automatic selection is deliberately not a
legacy negotiation or recovery routine. Exact firmware version is not inferred.
The writable capability response must match all eight signature/geometry bytes.

`--profile emulator` omits resident probing and the image backend. Both profiles
still include TPIMPORT as a standalone transient, which probes only when run.
Profile artifacts are retained under `build/profiles/combined/` and
`build/profiles/emulator/`. The top-level build files represent the most recent
build. `ts2068-cpm-tspico.dck` is a DOCK-only container convenience; only the
combined profile has the required physical image backend.

Resident service code occupies F000-F5FF; its workspace is F600-F7FF. BIOS and
stack remain in HOME page 7 during all TSPico transfers. The backend ABI is still
drive/LBA/128-byte bounce buffer, so future Oliger and other disk implementations
remain separate from the transport and console.
