# Starting CP/M: TSPico, Fuse/Oliger and TSRun

All three run CP/M 2.2. The console defaults to 80 columns with the supported
PicoVideo renderer, otherwise 64; `COLUMNS 64` / `COLUMNS 80` selects the width. These are different storage
paths: the TSPico cartridge needs Pico hardware; the Oliger cartridge needs a
disk controller and a matching DSK. Do not interchange their cartridges.
The OS lives in the cartridge, so disks need no CP/M system tracks.

**TSPico owners:** first read the [firmware/feature matrix](tspico-firmware.md).
Original 1.00 uses RAMDisk and chunk saves; the inspected modern target is
firmware 2.3.1 / ROM 2.3. Direct SD/native files additionally require our optional
CP/M service. Intermediate 1.1 releases are not a validated target.

Once at A>, see [COLOR, HI and installing new software](using-cpm.md) for the
same instructions across TSPico, Fuse and TSRun, including a worked Zork II disk.

## Physical TS2068 with TSPico

Use `build/ts2068-cpm-tspico-dual.zip`. Extract it on the PC and merge its `TAP`
folder into the SD card's existing `TAP` folder, preserving your working saves.
The card should contain:

```text
/TAP/CPM/CPM.DCK
/TAP/CPM/CPM32000.TAP ... CPM32007.TAP
/TAP/CPM/SAVE/
/TAP/CPM/FILES/...
```

The original firmware's public root is the physical TAP folder. Start from
normal TSPico BASIC and enter:

```basic
SAVE "tpi:cd /"
SAVE "tpi:cd CPM"
LOAD "tpi:CPM.DCK"
LOAD ""
```

The last LOAD runs the DCK loader. Choose **SRAM**, **slot 4** (pair 4/5), then
its DOCK selection/restart option. Leave BOOT unchanged. The build reserves
slot pairs **0/1, 2/3, 6/7, 8/9, 10/11 and 12/13** for RAMDisk and overwrites
their RAM contents. Those slots must be available. Do not load CP/M into
another slot; the current bank assignments are fixed. A separate physical
cartridge must not also drive DOCK.

On original **1.00**, it selects the legacy protocol and loads the saved disk
set from `/CPM/SAVE`, or the supplied 320KB preload when no save exists.
Expect a protocol/RAMDisk notice, HELLO's greeting, then `A>`. Run **TPSAVE**
before power off, confirm with Y and wait for completion. Saved chunks reload
directly on the next start; no PC repacking is needed. Missing/incomplete
saved sets stop boot instead of being silently discarded.

With the inspected **modern 2.3.1 / ROM 2.3 interfaces**, a configured optional CP/M service offers
**Enter** for persistent SD, **R** for a RAMDisk snapshot, or **L** to reload a
saved RAMDisk. Without that service, it uses TAP-backed preload/saves through
the newer transport. The optional service is required for native `/CPM/FILES`
or direct DSK/TAP disk access; the package does not install it automatically.
Modern RAMDisk TPSAVE writes one `/CPM/SAVE/CPMRAM.TAP`; legacy mode writes a
reloadable chunk set. Both RAMDisk modes require explicit saving.

The display stays at 64 columns unless the supported PicoVideo extension is
detected. Physical original-1.00 boot and game operation have been reported;
modern interfaces and failure cases are primarily checked with native Z80
and protocol/memory models. See
[TSPico modes and saves](tspico-dual.md), [SRAM reservations](tspico-ram.md), and
[modern service setup](tspico-directory.md).

## Fuse GUI with Oliger/JLO

Use Eduardo Fuentes's **JLO-enabled Fuse**, installed here at:

```text
C:\apps\emulation\Fuse-JLODiskEmulation\fuse-1.9.1-win32\fuse.exe
```

Ordinary Fuse does not provide this Oliger disk interface. No TSPico hardware
or firmware is used. From the project directory, launch the supplied 320KB
Planetfall/Zork disk and its matching cartridge:

```powershell
.\tools\run_infocom.ps1
```

Or use the utilities disk:

```powershell
.\tools\run_oliger.ps1 -Disk .\build\oliger-cpm.dsk
```

The launcher selects TS2068, enables JLO, supplies `safe265.rom`, selects the
drive side count, and loads the matching 160KB/320KB CP/M cartridge. If using
an extracted package, run its launcher from that package's directory; the
relative build layout is included. Custom installations can pass `-Fuse PATH`.

The installed older GUI cannot insert a JLO disk through a command-line option:

1. Choose **Media > Disk > JLO > Drive A: > Insert...**. Some builds call it
   **Drive 0:**.
2. Select `build/infocom-cpm.dsk` for the game launcher, or `build/oliger-cpm.dsk`
   for the utilities launcher. Use the exact disk printed by the launcher.
3. At CP/M's insert-disk prompt, press **Enter** to retry. If the disk was
   inserted before startup, CP/M may already have booted.
4. Expect `A: Oliger disk`, HELLO's greeting and `A>`.

Type `DIR`, `SUBMIT DEMO`, `HI`, `COLOR`, `PLANET` or `ZORK1` as appropriate.
Use the JLO drive menu's **Save/Save As...** to preserve the changed disk on the
PC before exiting. TPSAVE is for TSPico RAMDisk; it is not the Fuse save path.
Always match the disk size to the cartridge: retained profile `oliger` is 160KB,
`oliger320` is 320KB. The game disk and `infocom-cpm.dck` are a matched pair.
See [Oliger details](oliger.md).

## TSRun browser emulator with the same Oliger disks

The project now supplies a local CP/M page using TSRun's Z80, TS2068 memory,
video and keyboard code plus a functional Oliger adapter. The neighboring
TSRun checkout is read only; no upstream TSRun files are patched.

From this project's directory:

```powershell
python tools/run_tsrun.py
```

Open **http://127.0.0.1:8770/**. It loads the local TS2068 ROMs, matched
`build/infocom-cpm.dck` and `build/infocom-cpm.dsk`, then boots to `A>`.
Click the screen to type, enter a command in the command box, or use the
DIR/demo/game buttons. The example `SUBMIT DEMO` assembles and runs HI.COM.

To choose a utilities disk, another TSRun checkout, or another port:

```powershell
python tools/run_tsrun.py --tsrun ../../TSRun --port 8770 --disk build/profiles/oliger320/oliger-cpm.dsk --cartridge build/profiles/oliger320/ts2068-cpm.dck
```

The page's **Open disk** accepts a standard DSK or a complete CP/M disk TAP,
matching the current cartridge's 160KB/320KB size, and restarts CP/M. It also
accepts a complete 1.00 saved set: select all `CPMnn.TAP` files and
`CPMSTATE.TAP` together. Select all four/eight `CPM3200n.TAP` files to load
factory preload volumes. New saved sets use their descriptor's geometry and
Fletcher checksums; old descriptor-free sets require selecting exactly the
correct twenty/forty pages. Program TAPs and incomplete/mixed sets are refused.

**Reset CP/M** retains the current disk. **Download DSK** saves a copy for Fuse,
and **Download TAP** saves one multi-CODE TAP for the modern TSPico protocol.
**Download 1.00 TAP set** saves a ZIP containing the chunk TAPs and completed
descriptor: extract its contents into the card's `/TAP/CPM/SAVE/` directory,
preserving the previous save separately. That set reloads directly in the
legacy cartridge; it needs no repacking. The ZIP itself is not a TSPico disk.

The server never overwrites the source disk. Download before closing/reloading
the tab. Reopen a downloaded disk with Open disk or the Python tools; Fuse
uses the DSK form. Browser disk memory is not an automatic save to SD or the PC.
The standalone launcher also accepts `--disk PATH_TO_DISK.TAP` at startup.
TSRun still runs the Oliger CP/M cartridge; TAP is another container for its
sector data, not an emulation of the TSPico FIFO or SRAM hardware.

Stop the server with Ctrl+C in its terminal. This is a functional single-drive
adapter for this CP/M BIOS, not a full cycle-accurate JLO/SAFE emulator. The
ordinary TSRun page still lacks this disk UI. The older 48KB `emulator`
cartridge can run there without an adapter, but cannot mount these DSKs.

## Create and populate another disk

```powershell
python tools/cpm_disk.py create work.dsk --size 320
python tools/cpm_disk.py put work.dsk ED.COM ASM.COM README.TXT
python tools/cpm_disk.py list work.dsk
```

Use `.tap` for a TSPico disk container. For native modern TSPico storage, copy
CP/M files directly into `/TAP/CPM/FILES` instead. `FORMAT A:` initializes an
already mounted disk after confirmation; it does not create an SD container.
See [disk creation, copying and FORMAT](disk-tools.md).

## Hardware requirements and why extra RAM is needed

A stock TS2068 has 48KiB of main RAM, but its normal address map is unsuitable
for this CP/M build: ROM occupies 0000–3FFF and video uses part of the RAM above
4000. CP/M needs writable low memory, including its restart vectors and program
entry at 0100, and programs expect a continuous address space. This port supplies
that space through the TS2068's existing DOCK bank selection.

**The current port requires 32KiB of additional writable DOCK RAM, even when
using a real disk controller.** That is the baseline for this implementation,
not a claim that every possible CP/M port needs that much expansion.

| CPU addresses during normal CP/M execution | Backing memory and purpose |
|---|---|
| 0000–3FFF | 16KiB external DOCK RAM replacing the BASIC ROM; CP/M vectors and lower program memory |
| 4000–7FFF | 16KiB external DOCK RAM; program memory while the HOME screen is hidden from the CPU |
| 8000–CFFF | Existing HOME RAM; upper program memory |
| D000–D7FF | Existing HOME RAM; command processor (CCP) |
| D800–E5FF | Existing HOME RAM; disk/file services (BDOS) |
| E600–FFFF | Existing HOME RAM; BIOS, buffers, stacks and workspace |

The display still reads the original HOME screen RAM. For drawing, the BIOS
briefly maps HOME screen memory into the CPU's view, updates it, then restores
the DOCK program RAM. Thus screen clearing and scrolling do not overwrite the
program. The physical machine has 80KiB of RAM in this arrangement: its original
48KiB plus 32KiB expansion. Only 64KiB is visible to the Z80 at once. The program
area is 0100–CFFF: 52,992 bytes (51.75KiB). Adding a larger RAMDisk does not enlarge
that area or allow arbitrarily large programs to run.

The cartridge also provides boot code, font and an immutable OS copy in upper
DOCK pages. On startup these copy the OS into HOME RAM; warm boots can restore
the command processor and BDOS. A ROM-only cartridge cannot provide the required
writable low memory. The DCK file describes both RAM and ROM pages; the emulator
or cartridge hardware must actually implement those page types.

A PicoCartridge/PicoROM modification could provide this baseline by implementing
four writable 8KiB DOCK pages at 0000–7FFF, cartridge ROM pages for boot/OS data,
and the existing F4/FF bank-selection behavior used by the BIOS. Writes must reach
real storage and reads must return the updated bytes at Z80 bus speed. Depending
on the board, this could mean adding SRAM and bus support, or implementing suitable
writable memory in the existing design. A larger flash chip alone is insufficient.
Exact wiring, timing and firmware changes require checking the specific board;
this project does not yet provide a validated PicoCartridge/PicoROM modification.
The current TSPico implementation supplies the writable memory through its SRAM.

A disk backend is a separate requirement. Oliger uses its disk interface; TSPico
can use a RAMDisk or the documented modern SD service. A standalone modified
cartridge could instead preload extra RAM with a disk image. Its bank controls
would need a matching BIOS driver; TSPico MEMDOCK support is not automatically
provided by adding RAM to another cartridge. PicoVideo is optional; the normal
TS2068 supports the existing 64-column console.

## How the RAMDisk and emulator disks work

A CP/M disk is a sequence of sectors containing directory entries, allocation
information and file contents. The filesystem is interpreted by CP/M's BDOS.
The BIOS translates sector requests into whichever storage mechanism is selected.
An 8KiB RAM bank is storage for many sectors, not a separate CP/M drive.

### TSPico RAMDisk

At boot the loader reads the supplied TAP disk data, or a previously saved disk,
into additional TSPico SRAM. The disk can be 160KiB (20 pages of 8KiB) or 320KiB
(40 pages). These bytes are separate from the RAM used for running CP/M programs.
The current build reserves SRAM slot pairs 0/1, 2/3, 6/7, 8/9, 10/11 and 12/13
for disk storage; pair 4/5 holds the cartridge. Reservations can exceed the exact
disk size. Each disk pair offers seven usable 8KiB windows; the upper CPU window
stays mapped to HOME so the resident BIOS, private stack and sector buffer remain
available while the other windows change.

For each disk request, the BIOS finds the SRAM pair/window containing the sector,
selects it through MEMDOCK, copies sector bytes to or from the protected buffer,
and restores the normal cartridge mapping. CP/M sees drive A: and ordinary disk
reads/writes. After preload, this does not reread a TAP file from SD for every
sector. TAP headers and checksums are transport packaging; the working SRAM holds
the disk's sector data.

Changes remain in SRAM until exported. **Run TPSAVE before ending a RAMDisk
session**, including on modern firmware. Original 1.00 exports a reloadable set
of chunk TAPs plus a descriptor; the modern transport can export one multi-record
TAP, or a compatible split set. Both reload directly with this loader. With the
optional modern SD service, a mounted SD image can also be copied into RAMDisk
for speed; editing that snapshot does not automatically update its source image.
Native files and direct SD images use the other documented service paths instead.
See the [firmware matrix](tspico-firmware.md) for exact availability and
[RAM reservations](tspico-ram.md) before using SRAM slots containing other data.

### Fuse with Oliger/JLO

The Oliger cartridge still needs the writable DOCK RAM described above; Fuse
creates it from the DCK RAM-page declarations. Disk requests go to the emulated
JLO/Oliger disk controller, which accesses the mounted DSK image on the host.
The guest is using a disk controller rather than the TSPico RAMDisk driver.
Host memory may buffer the image, but this does not consume additional TS2068
program RAM or TSPico SRAM slots. Use the JLO-enabled Fuse build and its disk
Save/Save As controls to preserve the session's disk contents. Fuse uses the DSK
container; convert/export a TAP disk to DSK before mounting it there.

### Project-local TSRun CP/M page

TSRun also creates the writable cartridge pages from the DCK. The project-local
page loads a DSK, a supported CP/M TAP disk, or a legacy saved TAP set into a
browser-memory sector array. Its functional Oliger adapter services the BIOS's
controller requests using that array. It does not emulate the TSPico firmware,
FIFO transport or MEMDOCK SRAM selection. The same sector contents make the disk
compatible even though the access hardware differs.

Writes change the browser's working disk. Download DSK, TAP or a legacy TAP set
before closing/reloading the page; the original host file is not overwritten.
A downloaded DSK can be used in Fuse, while the TAP exports can preload TSPico.
This is why TSRun can use TAP-based disk files without having a TSPico attached.

The older standalone `emulator` cartridge is a different path: its small 48KiB
RAMDisk lives in additional emulated EXROM pages, preloaded inside the cartridge
file. It needs no Oliger adapter but has much less space. That EXROM RAM is an
emulator-provided expansion, not RAM present in a stock TS2068. The current
Oliger/TSRun page and TSPico packages use the larger disk arrangements above.

Physical TSPico timing and any proposed PicoCartridge/PicoROM modification still
need hardware verification; emulator/protocol-model results do not establish that.
