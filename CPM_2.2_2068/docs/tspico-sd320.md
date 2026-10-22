# CP/M with a modern TSPico 320KB SD image

## Firmware requirement

This is the inspected modern 2.3.1 / ROM 2.3 protocol path **with the optional
CP/M service**, not original 1.00 or validated 1.1 support. See the
[firmware/feature matrix](tspico-firmware.md) and [using CP/M](using-cpm.md).

For ordinary files copied into `/CPM/FILES`, use the recommended
[directory build](tspico-directory.md). Both modern builds include `CPMDISK`
for mounting 160KB/320KB DSK or TAP disk files and saving snapshots.

This is a separate experimental build for a compatible newer TSPico protocol
and the optional binary-safe CP/M image service. It is **not compatible with
unmodified firmware 1.00**. Use the SRAM build on the original firmware.

The CP/M cartridge runs from writable DOCK SRAM. Drive A is a CP/M filesystem
inside /CPM/DRIVE320.IMG on the SD card, rather than a native view of the FAT
directory. Both images use the same 320KB CP/M geometry as our Oliger build.
Ordinary modern file channels alone do not provide this writable drive: their
control-byte semantics and 16-bit seek path are insufficient for this profile.

The code probes the modern framed protocol and requires the CP/M service's
exact signature, 128-byte sectors and 2,560-sector geometry. Absent, legacy,
busy, incompatible, corrupt and stock-without-service responses stop with
"No usable disk". It never silently treats an incompatible image as a drive.
This is capability detection, not firmware-version identification.

## Optional installation on an already compatible newer firmware

No installation or firmware upgrade is performed by the build/package tools.
The supplied service requires the EXT_SA_FUNCT extension hook and the matching
CH_CALL, channel packet and DMA interfaces described in docs/tspico.md. An
arbitrary firmware labeled 2.3.x is not automatically proof of compatibility.
The service is host-tested, not physically verified on the owner's board.

Install all four modules: cpm_service.py, cpm_directory.py, cpm_tap.py and
cpm_dsk.py. Update the extension command dictionary as well: CPMINFO is now
required for safe geometry refresh after mounts. CPMDISK accepts 160KB or
320KB DSK/TAP files; see the directory guide for mount/export commands.
To boot directly from a container, set `CPM_STORAGE = 'dsk'` (or `'tap'`) and
`CPM_IMAGE_PATH` to its public `/CPM/...` path. Its header supplies geometry.

Merge `TAP/CPM` into the SD card's public TAP root, preserving an existing
DRIVE320.IMG first. Install the four supplied CP/M service modules
only on firmware that supports those interfaces. Merge the following settings
into cpm_config.py on the Pico flash root (preserve unrelated configuration):

```python
CPM_STORAGE = 'image'
CPM_DIRECTORY = '/CPM/FILES'
CPM_IMAGE_PATH = '/CPM/DRIVE320.IMG'
CPM_IMAGE_SIZE = 327680
```

Merge this into an existing dev_extcmd.py without replacing other handlers:

```python
from cpm_service import EXT_SA_FUNCT as CPM_COMMANDS
EXT_SA_FUNCT.update(CPM_COMMANDS)
```

Load CPMSD.DCK with the normal DCK loader into an unused SRAM even slot pair.
Unlike the legacy SRAM-disk build, this image does not select other SRAM pairs.
Leave BOOT unchanged. The boot screen reports TSPico SD image R/W only after
validating the service and geometry. Sector writes are synchronous. There is
no TPSAVE step; the service writes the SD image directly. It does not journal
or guarantee atomicity across power loss.

The package includes utilities, COLOR, HI.ASM/DEMO.SUB and, when requested,
Planetfall and Zork I. Keep their COM and DAT files together. Document and game
saves occupy the SD image; protect it from replacement by a fresh package.

## Reproduction

```text
python tools/build.py --profile tspico-sd --with-infocom --rom PATH_TO_TS2068_ROM
node tools/test_tspico_sd320.mjs
python tools/package_tspico.py --profile tspico-sd
```

The native Z80/wire-model tests cover boot, incompatible/missing service,
all 2,560 sectors, binary-safe high-LBA writes and SUBMIT/ASM/LOAD. Host tests
also execute the actual Python service handlers against a 320KB temporary file.
Planetfall and Zork I also pass boot, LOOK, SAVE/RESTORE and return to CP/M
through the modern wire model.
Physical FIFO and device behavior remain hardware validation work.
