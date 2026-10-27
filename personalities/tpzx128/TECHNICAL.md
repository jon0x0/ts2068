# How the Spectrum 128 personalities work

This describes the code in this publication snapshot. It does not describe
the proposed `/MODES` manager, which is not implemented by these packages.

## The Timex runs the Z80 code

This is a patched-ROM personality, not a Spectrum CPU emulator running on
the Pico. The Timex Z80 executes the modified Spectrum ROM. The Pico supplies
the expansion-memory control and, in the SD variant, cooperates with file I/O.
The design targets the traced TSPico V2.2 wiring on RP2040.

The fixed HOME RAM remains separate from the external SRAM. Selecting DOCK
for C000-FFFF exposes a 16 KiB window into one of eight external RAM banks.
The bank windows occupy physical SRAM offsets 0C000, 1C000, through 7C000.
The ROM pair uses SRAM slot 4 in the current stock-sequence adapter; arbitrary
slot relocation is not supported by that adapter. Boot initializes external
RAM banks and HOME memory, so existing contents are lost.

## Guarded ROM modifications

`source/build_rom.py` accepts exact original English Spectrum 128 ROM halves.
It verifies their SHA-256 values and expected instruction bytes before
patching. The patch manifest records before/after bytes and reasons.

The important changes are:

- Move paging operations away from 7FFD to the decoded low port 0F.
- Initialize Timex SCLD mapping and ordinary video, clear the required HOME
  RAM, and select external banked RAM at C000-FFFF.
- Adapt AY register selection/data accesses to Timex ports F5/F6 while
  preserving the required calling and flag behavior.
- Disable unsupported Spectrum serial keypad and MIDI operations.

`source/build_fs128_rom.py` adds the SD variant to the baseline. It inserts
filename and block-transfer hooks, reserves HOME service RAM, and uses the
disabled serial-keypad area for ROM shims while preserving the adjacent BASIC
token extension. The generated driver is assembled from the Python source
strings and the included Z80 `.asm`/`.inc` transport sources. The resulting
`firmware/fs128_image.py` contains the service bytes sent to the Timex.

The modified ROM filename remains `TPZXSD.ROM`; `tpzx128sd` is the published
directory/package name. Renaming the ROM is unnecessary and would require
updating every corresponding manifest and procedure.

## Paging through PIO and DMA

`firmware/personality128.py` supplies shared assembler and DMA support.
`firmware/personality128_stock.py` supplies the corrected stock-sequence
controller used by the documented launch. The original shared module also
contains earlier experimental entry points; do not substitute them for the
documented stock adapter.

The paging PIO captures a write, controls the ROM-half output, and constructs
the packed selection word `(bank << 5) | rom_slot`. DMA bridges the paging
FIFO to the address selector. Memory-control sequencing follows the stock
implementation and its required delays. Paging bit 5 locks further changes
until the personality controller is reinitialized. TS Reset alone does not
reset that Pico state.

The RP2040 MicroPython 1.20 path uses the register-based DMA fallback when
`rp2.DMA` is unavailable. Takeover stops stock state machines and aborts stock
DMA before the replacement uses these resources. This is exclusive ownership,
not concurrent stock file service, and not a general-purpose DMA allocator.

## Revision 2 host handoff without a reset

`build_handoff128.py` assembles a 111-byte HOME-RAM trampoline into a CODE TAP
at 8000h. Its stack is at 9FF0h, outside the ROM being replaced. The helper
first stops the stock Python dispatcher and pastes definitions into the
existing REPL RAM; it does not save them to the Pico filesystem.

When the user calls `RANDOMIZE USR 32768`, the Z80 disables interrupts, sets
HOME mapping, and sends `48 31 mode checksum` through the old port-14 FIFO.
The mode is 1 for the baseline and 2 for SD. The Pico validates the exact
packet, disables old memory controllers, and acknowledges with A7. It holds
ROM half 1 during replacement-controller setup and releases ROM half 0 only
after setup is complete. The Z80 polls a 32-byte ROM-0 fingerprint, initializes
I and IM1, and jumps to the ROM cold-start entry at address 0.

Revision 1 incorrectly selected low DOCK while polling. Low DOCK bypasses
the ROM-half gate, so it read SRAM instead of the intended ROM. Revision 2
keeps F4=0 during polling. Use the matching revision-2 TAP; changing only
Python definitions cannot repair an old trampoline already in Timex RAM.

No acknowledgement leaves the trampoline waiting in HOME. Acknowledgement
followed by no matching ROM eventually parks with a red border. Recovery is
a complete power cycle, not a retry through the discarded BASIC stack.
The Pico does not electrically assert TS Reset.

## Cooperative SD service

Only `tpzx128sd` enables the filesystem gateway. `personality128_fs.py`
captures service requests and saves the current bank, ROM half, and paging
lock. The Timex executes the driver and stack in HOME while the Pico hands
the shared bus pins over to its installed native SD routines. It then restores
the actual cached mapping and ROM-half initializer, clears stale DMA request
credits, and returns to the personality controller.

`fs128_legacy.py` validates and wraps the installed legacy 1.00 handler
contract. It reuses normal LOAD/SAVE handlers and their ordinary TAP cache.
Wrapped functions are restored after the session, including on exceptions.
SAVE completion is acknowledged after native write cleanup and controller
restoration. The foreground service loop leaves core 1 available to the
installed native SAVE watchdog.

HOME A000-BFFF is reserved for the driver, buffers, and stack. BASIC RAMTOP
and P_RAMT are capped at 9FFFh. Relative to the baseline this reduces
contiguous BASIC space by about 24 KiB, including the baseline's usable
C000-FFFF area; it does not consume the separate RAM-disk banks. CODE loads
and saves into the protected service area, ROM, or across FFFFh are rejected.
Transfers at C000-FFFF refer to the currently selected external bank.

The filename bridge distinguishes `tpi:` requests from tape. An explicit
nonempty filename without that prefix selects tape; subsequent empty names
continue the selected transport. RAM-disk `!` operations retain their own
path. Directory replies use the main screen, with 14 entries per page and
bounded per-page requests; SD sessions close before waiting for a key.

Modern 2.3 storage support has not been implemented. A protocol detector or
an old modern-transport reference is not a tested 2.3 backend. The baseline
`tpzx128` has no active TSPico file service at all.

## Helper behavior and temporary operation

`pico_debug.py` is the complete current desktop runner, including diagnostic
actions and the serial transport. Jobs snapshot code and hashes, ask for a
local acknowledgement, and record results in `source/build/serial-debug`.
Pending or running jobs are not replayed automatically after an error.
Inspect them before considering another operation, especially after SAVE.

`start_handoff128.py` queues six definition loads and one mode-specific run
job; all seven keep TS Reset released. It verifies the local ROM against
the corresponding handoff manifest. It cannot verify which bytes the user
previously copied to SD or which SRAM slot was chosen in the stock installer.

`start_fs128_sd.py` and its PowerShell counterpart queue five definitions
and the reset-held SD entry. Only the final entry requires TS Reset; release
it at the live ARMED message before waiting for completion. The reset-held
argument is the operator's assertion, not a sensed reset signal.

These helpers paste definitions through REPL, without target-file uploads,
Pico soft reset, replacement startup files, or Flash programming. Source files
include other experimental entry points, including Flash-capable bench paths;
the temporary guarantee applies to the documented SRAM launch sequence, not
to arbitrary calls into every included diagnostic function. Keep ROM loading
on SRAM slot 4 and do not use MEMBOOT or save a boot selection.

## Verification and limits

`rom_machine.py` executes the real Z80 code with separate, nonzero HOME and
external RAM. `pio_model.py` assembles real PIO programs using the included
MicroPython assembler reference and checks logical memory/paging behavior.
The SD peer models real TAP bytes and framing independently of native handlers.
Unit tests also exercise helper queue ordering, raw-REPL transport, resource
handoff, paging-lock retention, ROM-half gating, and protected memory regions.

These are functional models. They do not reproduce electrical propagation,
bus contention, analog behavior, instruction-perfect Spectrum timing, or
all software compatibility. The hardware has no transparent stock-7FFD
interceptor, native Spectrum shadow screen, or true bank-2/bank-5 aliases.
Arbitrary games and snapshots need additional work; no snapshot loader is
included in this personality publication. See STATUS.json for the exact
artifact identities and current physical qualification.
