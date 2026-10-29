# ZXDesk on the TS2068 with TS Pico: port concept and RAM banking handoff

Status date: 29 September 2026 (America/Denver).

This is a standalone project handoff. It is not an addition to the primary AI skill or a modification of any skill.

## 1. Goal and current conclusion

The goal is to run ZXDesk on an otherwise stock TS2068 with the existing TS Pico hardware and firmware, initially at 256×192, with a later 512×192 option. Persistent storage and useful access to the TS Pico's external SRAM are desired. Firmware changes are excluded from the initial implementation.

A native ZXDesk port is plausible because the program already separates storage operations and much of its drawing machinery from applications. Its current 48K design does not need extra RAM to display the desktop. A TS Pico backend could expose TAP-contained documents and settings as logical files, using existing command and block-transfer services.

The latest separate source/schematic banking audit establishes more than the early discussion did: the board has 512 KiB of external SRAM, organized for ordinary Dock access as eight selectable 64 KiB banks. The TS2068 can expose selected 8 KiB segments of one chosen external bank alongside HOME memory. That is useful for a custom ZXDesk port, but it is not a Spectrum 128K mapper or an independently selectable page mapper.

No TS2068 ZXDesk port, TS Pico filesystem adapter, or physical RAM test has been completed in this work. The port architecture below is proposed; documented commands and source/wiring findings are identified separately from unresolved behavior.

## 2. Evidence and version boundaries

Two different TS Pico repositories have been discussed:

| Source | Meaning for this project |
|---|---|
| `TSPico/TSPico` | Early 2022 prototype documentation. It should not define the capabilities of the newer 512 KiB board. |
| `timex-sinclair-projects/TS-Pico`, main | Released distribution, manuals, firmware and SD content. The separate audit pinned main at `f79cef005292d9bd5572fa440c95df9ebcaa8d0f`. |
| Same repository, Beta | Newer command and Python control documentation, pinned at `8ec5a79bea23a0ea6dfd319ae207594f01c10239`. |
| `timex-sinclair-projects/TS-Pico-Storage` | Hardware; v2.2 schematic audit pinned at `a41c72cd548282c475bcfec6f8ddfd01c16f0a26`. |

The separate audit identified the inspected Beta UF2 banner as `MicroPython v1.22.0; TS-Pico firmware v1.1c on 2024-09-05`. This identifies the inspected binary, not the firmware installed on the user's board. The repository's formal releases listed v1.0; Beta source, a published UF2 and installed firmware must not be conflated.

The supplied startup script imports a frozen `tspico` module rather than necessarily executing an edited Python file under `/TS`. Copying a Python source file onto a Pico is not proof that the new implementation is executing. Some low-level PIO setup source was absent from the audited trees. Command completion and all ROM/EXROM mapping combinations remain unverified.

## 3. ZXDesk's existing architecture

ZXDesk is a Z80 assembly graphical desktop for the Spectrum 48K. It contains overlapping windows, menus, event dispatch, keyboard/joystick/mouse input, a notepad, clock, calendar, settings and file-management interfaces. It is not a general compatibility environment that automatically runs other Spectrum or TS2068 applications inside windows.

Relevant source files:

| File | Responsibility |
|---|---|
| `src/zxdesk.asm` | Startup, interrupts, screen addressing, graphics, input, memory constants and main loop |
| `src/storage.inc` | Backend registry and six storage vectors; small RAM storage |
| `src/tape.inc` | Buffered load/save through Spectrum ROM cassette routines |
| `src/esxdos.inc` | esxDOS filesystem API adapter |
| `src/bank.inc` | Spectrum 128K RAM-disk backend |
| `src/commander.inc` | Two-pane file manager and copy/delete/open behavior |
| `src/filemgr.inc`, `src/note.inc` | File dialogs and document load/save |

The esxDOS implementation exists in current source. An older statement in the README that esxDOS has only a reserved ID is stale relative to that implementation. On startup, however, ZXDesk selects RAM on a 48K machine and bank storage on a detected Spectrum 128K. Merely attaching a DivMMC does not select the esxDOS backend.

ZXDesk does not use DivMMC/DivIDE RAM as additional application heap or window storage. It invokes esxDOS, which uses interface memory internally. Its explicit extra-RAM backend instead uses the Spectrum 128K's own banks through port `$7FFD`.

## 4. Storage interface the TS Pico adapter must implement

| Operation | Calling convention / purpose |
|---|---|
| `StOpen` | `HL=name`, `B=mode`; returns `A=handle`, carry on error |
| `StClose` | `A=handle`; finishes and releases the open file |
| `StRead` | `A=handle`, `HL=destination`, `BC=requested count`; returns `BC=bytes read` |
| `StWrite` | `A=handle`, `HL=source`, `BC=requested count`; returns `BC=bytes accepted/written` |
| `StDir` | `A=nth entry`, starting at zero; returns `HL=name`, `DE=length`, carry when absent |
| `StDelete` | `HL=name`; carry when removal fails or is unsupported |

Additional helpers select a backend, return its identity and expose capability bits for write, persistence, random access and directory enumeration. `FA_READ=$01`; `FA_OVERWRITE=$0E` means write/create/truncate. Errors include not found, invalid name, full, invalid handle and unsupported operation.

Although the random-access capability exists, there is no seek vector in this interface. A first TS Pico backend does not need a sector driver, FAT implementation, esxDOS emulation, general folder browser, rename or several simultaneous open disk handles.

Current practical limitations should not be mistaken for hardware limits:

- The stock RAM backend holds four files of 256 bytes.
- The Spectrum 128K backend holds eight files of 8 KiB, with a separate directory bank.
- The existing tape backend buffers a whole file and saves on close; its configured buffer is 512 bytes.
- The file-open panel lists up to eight entries.
- Commander copies one 256-byte chunk, not an arbitrary-length file. Larger copies require a loop and error/short-transfer handling.
- File-name fields currently allow ten usable characters; some old comments say eight.

## 5. TS Pico storage with existing firmware

### Baseline released behavior

The released documentation describes mounting TAP files, loading header/data blocks, saving to a newly created TAP, printing SD and TAP directory listings, changing directories, rewinding/advancing a TAP pointer and unmounting.

A first adapter can map logical file `NOTE1` to SD file `NOTE1.tap`, containing a CODE header and document bytes. CODE is a storage container here: loading the bytes does not execute them. Settings can be stored similarly.

Proposed implementation:

1. Read-open: close the previous mount if needed, mount the corresponding TAP, validate a supported header and length, and load payload into a bounded buffer.
2. Read: copy from that buffer, track position and return short reads/end-of-file correctly.
3. Write-open: initialize a buffer and remember the logical name.
4. Write: accumulate bytes, rejecting or reporting capacity exhaustion explicitly.
5. Close-write: issue the existing save transfer with a valid header and data block; report success only after the operation actually completes.
6. Directory: capture the existing response stream, parse names into records and cache a bounded listing. Distinguish container byte size from payload length.
7. Delete: return unsupported until a working current-firmware operation is established.

Replacement of an existing TAP, zero-length files, failure recovery and transfer completion require tests. No atomic-save guarantee is established.

### Newer Beta commands change the opportunity

The pinned Beta `commands.md`, inspected for this handoff, additionally documents:

| Capability | Published behavior and qualification |
|---|---|
| `TPI:APPEND` | Enables appending subsequent saves to a mounted TAP. Requires a mounted file. This supersedes the blanket earlier claim that TS Pico can never append, but only for firmware that actually implements this command. |
| Binary mount and `TPI:BLKRCV` | Documents mounting a `.bin` from the Pico's internal flash and receiving a byte count from an offset through `IN 14`. It is not established as arbitrary SD-file read/write access. |
| `TPI:FFW` / `TPI:REW` | Documents movement through TAP blocks, including a CODE parameter for skipping blocks. |
| `TPI:VERBOSE` | Toggles command feedback; disabling feedback does not prove synchronous completion or bounded latency. |
| `TPI:DELETE` | Explicitly listed as not implemented. `TPI:RM` is documented for removing directories. |

The binary-stream documentation contains inconsistent spellings (`BLKRCV`, `blkrvc`, and `blckreceive`). The actual executing handler must decide the correct command. All queued stream bytes must be consumed; the document warns that leaving bytes unread can block further operation. This is a candidate service for a Z80 adapter, not a tested driver.

Appending versions to a TAP could support a journal-like document store, but it does not provide deletion, truncation, compaction or a ready-made index. Those semantics would be host-side design work.

### Host integration

Use a native TS2068 host driver to send the existing command/block protocol or invoke verified low-level routines. Running complete BASIC statements inside a desktop is not necessary.

TS Pico's documented `TP_MODE` workspace byte is at `$683E`, inside ZXDesk's `$6000` code region. Therefore an unchanged ZXDesk memory layout cannot safely coexist with every patched-ROM service. Inventory all ROM work areas and either reserve/relocate them, save/restore verified scratch areas, or implement independent Z80 transfer routines with their own workspace. Protecting only one known byte is insufficient.

Directory output is formatted and paginated rather than a documented binary record API. Capturing it without allowing ROM screen output to damage the desktop remains a protocol task. File I/O can be blocking initially, followed by a controlled desktop repaint; frame-sensitive rendering should not depend on a command completing within one display frame.

## 6. TS Pico SRAM and ordinary Dock banking

The audited v2.2 board has an AS6C4008 512 KiB static RAM chip. This is external Z80-accessible SRAM, distinct from the Pico MCU's internal RAM and from Flash ROM.

The documented selection command is:

```basic
SAVE "tpi:memdock" CODE 1,0
```

The first parameter selects SRAM (`1`) or Flash (`2`). For Dock, the documented selector values are even numbers `0,2,4,...,14`, corresponding to eight 64 KiB banks formed from pairs of 32 KiB slots.

| Bank index | Documented Dock selector |
|---:|---:|
| 0 | 0 |
| 1 | 2 |
| 2 | 4 |
| 3 | 6 |
| 4 | 8 |
| 5 | 10 |
| 6 | 12 |
| 7 | 14 |

The source accepts some values beyond the documented contract. Do not use undocumented odd selectors or memory types as an assumed extra capability.

### Two separate controls

1. **TS Pico bank choice:** `MEMDOCK` selects the external SRAM bank through the Pico command/PIO path.
2. **TS2068 visibility:** port `$F4` (244) selects HOME versus external memory independently for each 8 KiB CPU segment. Port `$FF` bit 7 selects Dock versus EXROM globally. Preserve unrelated `$FF` bits, especially video and interrupt controls.

In ordinary Dock mode, the schematic preserves CPU offsets within the chosen bank:

```text
physical SRAM address = selected_bank_index * 65536 + CPU_address
```

| `$F4` mask | Visible external portion, assuming Dock is selected |
|---|---|
| `$00` | None; HOME throughout |
| `$03` | Selected bank's `$0000–$3FFF` |
| `$20` | Selected bank's `$A000–$BFFF` |
| `$C0` | Selected bank's `$C000–$FFFF` |
| `$0C` | Selected bank's `$4000–$7FFF` |
| `$FF` | Entire selected external 64 KiB bank |

All enabled Dock segments use the same selected external bank. The mask cannot combine segments from two different external banks, and it cannot relocate a bank's `$0000–$3FFF` block into CPU `$4000–$7FFF`.

There is no verified dedicated Z80 register that changes the complete 64 KiB bank with one fast OUT. `$F4` changes visibility; it does not choose among all eight physical banks.

### Timing and alternative overlays remain unresolved

The inspected Beta `MEMDOCK` handler updates packed control state, sends feedback/logs, then queues separate `ROM.put` and `BANK.put` operations. Completion ordering, latency and atomicity have not been measured. Keep driver code, stack, interrupt handler and any live command data in memory that will remain accessible during selection changes.

`MEMBOOT` selects boot/ROM image slots, not a proven general scheduler register. Its audited handler includes configuration writes, feedback and a 100 ms delay. Do not use it for routine window-buffer paging without a separate validated design.

The schematic includes alternative address inputs for ROM/EXROM-related access. Ordinary Dock's fixed-offset limitation does not establish the complete capabilities of those paths. Their writable SRAM overlay behavior and truth table remain unresolved. There is also a board/documentation discrepancy about whether P10 controls SRAM writes as well as Flash writes; establish the actual board revision before prescribing jumper changes.

## 7. Proposed use of SRAM by ZXDesk

Keep a resident kernel, active renderer, interrupt handler and stack in HOME RAM. Use external SRAM for staged documents, undo records, directory records, and eventually window buffers. Treat it as explicitly banked storage rather than extending the existing flat heap transparently.

Use descriptors such as `{bank, offset, length}` for external objects. Never retain an ordinary pointer across a physical bank change. Begin with a preselected SRAM bank and a carefully reserved window; this exercises `$F4` access without depending on rapid runtime `MEMDOCK` switching. Such a window must not cover the executing code, stack or live buffers in ZXDesk's current layout.

Using more banks is plausible under current firmware, but requires a reliable host command driver and measured completion. RAM-disk operations tolerate slower switches better than per-scanline graphics or preemptive scheduling. The separate SymbOS audit found that ordinary Dock cannot directly reproduce its documented Next/CPC mixed-bank layouts; ZXDesk has more freedom because its memory layer can be redesigned around HOME plus one selected Dock bank.

SRAM capacity does not automatically increase document limits: the notepad, file copy routines and object allocator must also change.

## 8. Native port and 512×192 display

The first native build should retain 256×192 while adapting:

- Startup and machine selection, removing Spectrum 128K `$7FFD` probing.
- Font access, embedding a known font or using a verified TS ROM location.
- Tape/storage calls and ROM workspace requirements.
- TS2068 joystick input and keyboard details; pointer events remain the application interface.
- 60 Hz NTSC frame/clock assumptions and the Spectrum-specific beam scheduler.
- HOME/Dock state preservation across calls and interrupts.

ZXDesk's monochrome design fits the TS2068 high-resolution mode well aesthetically, but 512×192 requires real changes. The second bitmap occupies HOME `$6000–$77FF`, overlapping ZXDesk's code starting at `$6000`. Simply enabling the video mode is unsafe.

Relocate that code first; implement the two-plane screen address mapping and blits; revise pointer X handling, clipping, hit testing and layout for 512 pixels. `SCRCOLS=64` alone is insufficient. Window buffers grow with their pixel area, and HOME RAM budgets must be rebuilt. Preserve HOME display access while paging external data, and verify SCLD display fetch behavior separately from CPU visibility.

ZXDesk uses self-modifying code, including storage jump operands and graphics settings. Moving code into Flash/ROM is not generally a drop-in solution; separate mutable code/data or use writable SRAM and a validated mapping layout.

## 9. Emulator and bench plan

1. Run unmodified ZXDesk in Fuse as a plain Spectrum 48K to establish desktop behavior.
2. Test its existing esxDOS backend separately with a configured DivMMC, explicitly selecting that backend.
3. Try the existing TAP on real TS Pico in its documented TC2048-compatible mode: mount in native mode, `SAVE "tpi:zx48"`, `OUT 244,3`, then `LOAD ""`. This is an untested experiment, not the final native backend.
4. Establish a native TS2068 256×192 build with RAM storage before attaching persistent storage.
5. Identify installed firmware and trace low-level command and transfer entry points. Confirm the active frozen/Python implementation.
6. Test a named payload round trip, overwrite semantics, short transfers, missing files and recovery. Add directory capture next.
7. Test one SRAM bank/window with preserved signatures and state restoration; then test all eight banks for aliasing and retained contents.
8. Measure actual bank-change completion; only then use runtime bank changes for external objects.
9. Redesign memory and renderer for 512×192.

Fuse models TS2068 graphics and native banking but is not a faithful TS Pico firmware/PIO emulator. It can verify a renderer and an abstract bank model; it cannot establish real command timing or hardware reliability.

## 10. Sources and next-agent guidance

- [ZXDesk repository](https://github.com/mindbox77/zxdesk)
- [ZXDesk storage vectors](https://github.com/mindbox77/zxdesk/blob/main/src/storage.inc)
- [ZXDesk tape backend](https://github.com/mindbox77/zxdesk/blob/main/src/tape.inc)
- [ZXDesk esxDOS backend](https://github.com/mindbox77/zxdesk/blob/main/src/esxdos.inc)
- [ZXDesk Spectrum 128K RAM backend](https://github.com/mindbox77/zxdesk/blob/main/src/bank.inc)
- [Current TS Pico project](https://github.com/timex-sinclair-projects/TS-Pico)
- [Pinned Beta commands](https://github.com/timex-sinclair-projects/TS-Pico/blob/8ec5a79bea23a0ea6dfd319ae207594f01c10239/commands.md)
- [Pinned Beta Python handlers](https://github.com/timex-sinclair-projects/TS-Pico/blob/8ec5a79bea23a0ea6dfd319ae207594f01c10239/src/src_new_v1.1/TS/tspico.py)
- [Pinned v2.2 hardware](https://github.com/timex-sinclair-projects/TS-Pico-Storage/tree/a41c72cd548282c475bcfec6f8ddfd01c16f0a26/v2.2)
- [TS Pico usage wiki](https://github.com/timex-sinclair-projects/TS-Pico/wiki/Using-the-TS-Pico)
- [Spectrum mode wiki](https://github.com/timex-sinclair-projects/TS-Pico/wiki/ZX-Spectrum-Mode)
- Existing project evidence: `tspico-symbos-banking-audit.md`, dated 29 September 2026; read for the detailed wiring audit, version hashes, mapping model and bench requirements.

Carry forward the constraint of no initial Pico firmware changes. Distinguish documented functionality, source/schematic evidence, proposed code and physical test results. The immediate engineering targets are a safe native memory layout and an acknowledged host-side protocol driver; neither the 512 KiB chip nor the existing command list alone constitutes a completed ZXDesk backend.
