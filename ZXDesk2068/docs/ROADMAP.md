# TS2068 roadmap

## 1. Native baseline — implemented, hardware acceptance pending

256×192, native HOME ROM font, keyboard and both AY joystick sockets, IM2,
nominal 60 Hz clock, and RAM files. Startup deliberately selects HOME throughout
and standard video with frame interrupts enabled. There are no runtime ROM
services or external memory switches. This takeover does not preserve a prior
application's SCLD state and does not return to BASIC.

Next acceptance checks: load the TAP in native NTSC Fuse and on a TS2068; type,
open/close windows, drag, save/reopen a RAM note, and exercise both joysticks.
Measure frame timing before adding a beam scheduler. Add a separate PAL target
only with an explicit timing profile. Keep the original desktop behavior as the
reference while porting each device layer.

## 2. Cartridge delivery — near term

Build a bootable Dock DCK with a small resident loader that copies mutable code
into HOME RAM, restores HOME mapping, and enters the existing desktop. Test from
power-on ROM discovery, not merely by injecting the entry PC. A copy-to-HOME
cartridge simplifies delivery but does **not** free application RAM by itself.

Then consider a read-only resource/file backend for fonts, icons, help and sample
documents stored in the cartridge. Separate immutable assets from mutable code,
jump operands, application state and scratch buffers before executing from ROM.
Code, stack and interrupt handler must remain visible during any Dock mapping.
Do not advertise ordinary cartridge storage as writable persistent storage.

## 3. 512×192 — initial build implemented; optional extended color pending

The separate `zxdesk2068-512.tap` reserves `$6000–$77FF` for the second bitmap,
starts code at `$7800`, fast code at `$8E00`, and buffers at `$C600`. It trades
1.5 KiB of heap for the new layout. Both builds leave 66 bytes between their
slow and fast regions. Never enable mode 6 in the 256 build: its code overlaps
the second bitmap.

The new renderer handles interleaved byte columns, fills, glyphs, clipped blits,
save-under and the pointer. Pointer X is 16-bit; move events carry byte-column/Y
while their handlers use the full live pointer. Tests cover right-half dragging,
resizing, menus, all byte addresses, 255/256 crossing and native ROM tape boot.
Existing windows retain their initial sizes. Fuse/bench acceptance, speed work,
application layout/clipping refinements and persistent setting migrations remain.
The 256×192 build remains available as the smaller-memory option.

Extended color at 256×192 is a separate optional renderer mode, using the
second plane for per-scanline attributes. It has the same memory collision and
needs attribute painting/restoration for windows and pointer save-under. It is
not an extra color layer that can simply be added to 512×192 mode.

Acceptance: edge/corner pointer movement, cross-plane glyphs and rectangles,
overlap/drag/resize, full-width clipping, settings round trips, and screenshots
on both emulator and hardware. Preserve unrelated SCLD bits on later mode
changes; distinguish the deliberate initial takeover from runtime updates.

## 4. Optional storage backends

Retain the six-vector storage boundary (`Open`, `Close`, `Read`, `Write`, `Dir`,
`Delete`). Register only implemented, explicitly configured devices. Unsupported
selection must fail without changing the current device. Add backend enumeration
to the UI as actual choices arrive; do not hard-code new pane device pairs.

### TS Pico

Follow the version and evidence boundaries in the supplied handoff. Start with
existing firmware and a bounded TAP-container document adapter; no firmware
changes in this phase. Establish the executing firmware, command acknowledgments,
workspace requirements and complete draining of responses before integrating.
The new `$6C00` code origin clears the known `$683E` byte but is **not** proof
that all patched-ROM services can coexist with the desktop.

Test payload round trips, missing files, malformed/oversized blocks, partial
transfers, full buffers, overwrite behavior, and recovery before directory capture.
Deletion remains unsupported without a verified firmware operation. Avoid ROM
directory printing directly onto the desktop. Finish I/O, then repaint as needed.

### Oliger disk system

The user reports an Oliger-capable Fuse build; a local executable exists at
`C:/apps/emulation/Fuse-JLODiskEmulation/fuse-1.9.1-win32/fuse.exe`.
Its controller behavior, DOS interface and media format have not been audited
in this port. Pin its source revision and ROM configuration, obtain a disposable
disk image, establish a native load/save/directory interface, and implement an
optional backend against that verified interface. Test write protection, disk
full, short reads, media errors and reboot persistence in Fuse and on hardware.
Do not treat ordinary upstream Fuse as proof of Oliger support.

### RAM and other storage

Start TS Pico SRAM with one preselected 64 KiB bank and a deliberately reserved
8 KiB Dock window. The present upper RAM is occupied by live buffers and heap:
there is no safe free `$A000` or `$C000` window yet. Design staging and ownership
before exposing one. Use `{bank, offset, length}` descriptors for external data.
Test signatures, aliasing and restoration before using all eight banks.

MEMDOCK selects one external bank; `$F4` only selects its visible segments.
No fast independent bank register or arbitrary page relocation is assumed.
Keep command data and execution resident while changing banks and measure actual
completion. Add RAM disks before considering pageable window backing buffers.

For larger files on any device, revise Commander copy into a checked transfer
loop, propagate close/write errors, and revise document and directory limits.
More physical storage alone does not remove the existing 256-byte file/UI limits.

## Evidence

- [Pinned ZXDesk source](https://github.com/mindbox77/zxdesk/tree/e810812860366986859eca105a406f564d2a1c04)
- [TS2068 technical manual](https://device.report/m/1dc234a90e0a0a4909414d23f9dbfa619954ecb352b23266185180d4a7e167b5.pdf): native font/memory architecture.
- Local TSRun `machine.js`, `ay.js`, `joystick.js`: native ROM tape execution and
  modeled SCLD/AY behavior used in automated tests; not hardware measurements.
- [Project handoff](../ZXDesk_TS2068_TSPico_Port_Handoff.md): pinned TS Pico source,
  schematic evidence and unresolved firmware/hardware questions.
