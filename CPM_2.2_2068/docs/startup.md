# Starting CP/M: TSPico, Fuse/Oliger and TSRun

All three run CP/M 2.2. The console defaults to 80 columns with the supported
PicoVideo renderer, otherwise 64; `COLUMNS 64` / `COLUMNS 80` selects the width. These are different storage
paths: the TSPico cartridge needs Pico hardware; the Oliger cartridge needs a
disk controller and a matching DSK. Do not interchange their cartridges.
The OS lives in the cartridge, so disks need no CP/M system tracks.

**TSPico owners:** first read the [firmware/feature matrix](tspico-firmware.md).
Original 1.00 uses RAMDisk and chunk saves; the inspected TSPico v2.x target is
firmware 2.3.1 / ROM 2.3. Direct SD/native files additionally require our optional
CP/M service. Intermediate 1.1 releases are not a validated target.

Once at A>, see [COLOR, HI and installing new software](using-cpm.md) for the
same instructions across TSPico, Fuse and TSRun, including a worked Zork II disk.

## Download the version for your target

| Target | Download | Contents |
|---|---|---|
| TSPico v1.00 or compatible v2.x | [TSPico archive](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-tspico-dual.zip) | CPM.DCK cartridge, preload TAP disk volumes, CP/M files and utilities, compatible image containers, optional v2.x service and instructions |
| Modified Fuse with JLO/Oliger | [Fuse/Oliger archive](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-oliger.zip) | Matched 160KB and 320KB CP/M cartridges and utility disk images |
| Fuse/Oliger with Planetfall and Zork I | [Infocom archive](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-infocom-oliger.zip) | Matched 320KB CP/M cartridge and game disk, tools and instructions |
| TSRun locally | [Complete hub ZIP](https://github.com/jon0x0/ts2068/archive/refs/heads/main.zip) | The hub's runnable browser application, shared TSRun runtime/ROM assets and CP/M disk/cartridge images; this is the entire hub, not a small standalone player archive |
| TSRun online | [Run CP/M live](https://jon0x0.github.io/ts2068/CPM_2.2_2068/play/) | Same browser interface, no local installation |

For individual files: [320KB game disk DSK](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-infocom-320.dsk)
and [matching DCK cartridge](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-infocom-320.dck),
[160KB utility DSK](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-utilities-160.dsk)
and [matching DCK](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-utilities-160.dck),
or [320KB utility DSK](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-utilities-320.dsk)
and [matching DCK](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-utilities-320.dck).
[SHA-256 checksums](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/SHA256SUMS) cover the published release files;
the main-branch hub ZIP is a changing source/site snapshot.

The TSPico ZIP does not include a TSPico firmware upgrade. The Fuse ZIP does
not include Fuse itself or its JLO ROM. TSRun is executable JavaScript running
in a browser, not a Windows EXE. Download the complete hub ZIP rather than
only the CP/M subdirectory: the player references the shared runtime elsewhere
in that hub. Use the JLO-enabled Fuse distribution linked below for Fuse.

## Physical TS2068 with TSPico

Use the [TSPico archive](https://jon0x0.github.io/ts2068/CPM_2.2_2068/downloads/cpm22-tspico-dual.zip).
Extract it on the PC and merge its `TAP`
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

With the inspected **TSPico v2.x (inspected 2.3.1) / ROM 2.3 interfaces**, a configured optional CP/M service offers
**Enter** for persistent SD, **R** for a RAMDisk snapshot, or **L** to reload a
saved RAMDisk. Without that service, it uses TAP-backed preload/saves through
the newer transport. The optional service is required for native `/CPM/FILES`
or direct DSK/TAP disk access; the package does not install it automatically.
TSPico v2.x RAMDisk TPSAVE writes one `/CPM/SAVE/CPMRAM.TAP`; legacy mode writes a
reloadable chunk set. Both RAMDisk modes require explicit saving.

The display stays at 64 columns unless the supported PicoVideo extension is
detected. CP/M 2.2 has successfully booted and operated on physical TSPico hardware with original firmware 1.00;
TSPico v2.x interfaces and failure cases are primarily checked with native Z80
and protocol/memory models. See
[TSPico modes and saves](tspico-dual.md), [SRAM reservations](tspico-ram.md), and
[TSPico v2.x service setup](tspico-directory.md).

## Fuse GUI with Oliger/JLO

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

## TSRun browser emulator with the same Oliger disks

**[Run CP/M 2.2 live in TSRun](https://jon0x0.github.io/ts2068/CPM_2.2_2068/play/)**

Open that link in your browser. The hosted page loads the TS2068 emulator,
CP/M cartridge and supplied disk automatically, then boots to **A>**. You do
not need to install Python, download the source, or run a local server.

Click the screen to type, use the command box, or select a command button.
Try `DIR`, `SUBMIT DEMO` and `HI`. The page also offers startup links for the
160KB utilities disk and the 320KB Planetfall/Zork I disk.

The page's **Open disk** accepts a standard DSK or a complete CP/M disk TAP,
matching the current cartridge's 160KB/320KB size, and restarts CP/M. It also
accepts a complete 1.00 saved set: select all `CPMnn.TAP` files and
`CPMSTATE.TAP` together. Select all four/eight `CPM3200n.TAP` files to load
factory preload volumes. New saved sets use their descriptor's geometry and
Fletcher checksums; old descriptor-free sets require selecting exactly the
correct twenty/forty pages. Program TAPs and incomplete/mixed sets are refused.

**Reset CP/M** retains the current disk. **Download DSK** saves a copy for Fuse,
and **Download TAP** saves one multi-CODE TAP for the TSPico v2.x protocol.
**Download 1.00 TAP set** saves a ZIP containing the chunk TAPs and completed
descriptor: extract its contents into the card's `/TAP/CPM/SAVE/` directory,
preserving the previous save separately. That set reloads directly in the
legacy cartridge; it needs no repacking. The ZIP itself is not a TSPico disk.

The page does not overwrite the supplied startup disk. Download your working
disk before closing/reloading the tab. Reopen a downloaded disk with Open disk or the Python tools; Fuse
uses the DSK form. Browser disk memory is not an automatic save to SD or the PC.
TSRun still runs the Oliger CP/M cartridge; TAP is another container for its
sector data, not an emulation of the TSPico FIFO or SRAM hardware.

This project page adds a functional disk adapter for the CP/M BIOS; it is not
a full cycle-accurate JLO/SAFE emulator. Use the CP/M-specific live link above
for its disk controls, rather than the general-purpose upstream TSRun page.

### Optional: run the downloaded TSRun page locally

You can run the same CP/M browser application on your own PC and then load
disk images manually. No compilation is needed.

1. Download the [complete hub ZIP](https://github.com/jon0x0/ts2068/archive/refs/heads/main.zip) and extract it, preserving its
   folder structure. The extracted root is normally named `ts2068-main`.
2. Open a terminal in that root folder, not inside CPM_2.2_2068/play.
3. With Python 3 installed, start a local static server:

   ```powershell
   python -m http.server 8770 --bind 127.0.0.1
   ```

4. Open **http://127.0.0.1:8770/CPM_2.2_2068/play/** in your browser.
   For the single-sided utility environment use
   **http://127.0.0.1:8770/CPM_2.2_2068/play/?size=160**.
5. Wait for A>. Use **Open disk**, select your local `.dsk` or complete CP/M
   disk `.tap`, and let the page restart CP/M with that disk. If a drive
   selector is present, select the intended drive first. The 320KB startup
   needs a 320KB image; choose the 160KB startup for 160KB images.
6. Use **Download DSK**, **Download TAP** or **Download 1.00 TAP set** to retain
   changes before closing/reloading. The server does not update the selected
   host file automatically. Stop it with Ctrl+C when finished.

For a saved chunk set, select all matching CPMnn.TAP files and CPMSTATE.TAP
together. Do not try to load a .dsk through the ordinary upstream TSRun tape
loader: this workflow uses the project's CP/M/Oliger disk adapter.

### Optional: run from a development checkout

The separate Python launcher is useful when supplying a different TSRun
checkout or initial cartridge/disk. It requires this project's source, Python
3, the TSRun checkout with its TS2068 ROMs, and matching built/downloaded images.
From the CP/M source directory, adjust the paths and run:

```powershell
python tools/run_tsrun.py --tsrun C:/path/to/TSRun --cartridge C:/path/to/cpm22.dck --disk C:/path/to/cpm22.dsk
```

Open **http://127.0.0.1:8770/**. This launcher starts with the chosen disk;
Open disk can subsequently replace it with a matching-size image. Use
`python tools/run_tsrun.py --help` for further developer options.

## Create and populate another disk

```powershell
python tools/cpm_disk.py create work.dsk --size 320
python tools/cpm_disk.py put work.dsk ED.COM ASM.COM README.TXT
python tools/cpm_disk.py list work.dsk
```

Use `.tap` for a TSPico disk container. For native TSPico v2.x storage, copy
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
can use a RAMDisk or the documented TSPico v2.x SD service. A standalone modified
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
session**, including on TSPico v2.x firmware. Original 1.00 exports a reloadable set
of chunk TAPs plus a descriptor; the TSPico v2.x storage protocol can export one multi-record
TAP, or a compatible split set. Both reload directly with this loader. With the
optional TSPico v2.x SD service, a mounted SD image can also be copied into RAMDisk
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

### Two disks in the browser

The 320KB browser session mounts the primary game disk on A: and the utility
disk on B:. Type `A:` or `B:` at the CP/M prompt to switch drives. The disk
controls selector chooses which disk to open or download; it does not change
CP/M's current drive. Both disks must use the same geometry as the cartridge.
Download each changed disk separately before closing the page.

For the local two-drive cartridge, run `python tools/build_tsrun_dual.py`, then
start `tools/run_tsrun.py` with `--disk`, `--disk-b`, and
`--cartridge build/tsrun-dual/CPM320.DCK`. The standard 160KB browser profile
continues to boot its single utility disk. TSPico remains a single-drive target.
