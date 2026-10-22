# Planetfall and Zork I on TS2068 CP/M

For the shared COLOR/HI commands and adding another game, see
[using CP/M, with a worked Zork II example](using-cpm.md).

Use the matching `build/infocom-cpm.dck` cartridge and `build/infocom-cpm.dsk`
disk. This is a 320KB double-sided 40-track Oliger/JLO disk and a 64-column
CP/M 2.2 cartridge. The cartridge includes the keyboard scan consistency fix
for Backspace arriving between the modifier and character reads.

Run `tools/run_infocom.ps1` to start the installed JLO-enabled Fuse GUI.
On the older GUI, insert the disk using Media > Disk > JLO > Drive A: > Insert,
then press Enter at the cartridge's insert-disk prompt. Select Double-sided
40 track. Use this updated cartridge, including when trying the keyboard fix.

At `A>`, type `PLANET` or `ZORK1`. SAVE and RESTORE default to PLANET.SAV and
ZORK1.SAV respectively. Accept both prompts with Enter while leaving this disk
inserted. Also use Fuse's JLO Save/Save As menu before exiting to retain changes
on the host. Host save/reopen has not been independently automated.

The disk contains README.TXT, ASM.COM, LOAD.COM, SUBMIT.COM, DEMO.SUB, HI.ASM,
HI.COM, MEMTEST.COM, ED.COM, STAT.COM, HELLO.COM, COLOR.COM, and both games' COM/DAT pairs.
The current package has approximately 54KB free (consult STAT/the manifest).
`HI` runs the preassembled example. `SUBMIT DEMO`
assembles HI.ASM, converts HI.HEX to HI.COM with LOAD, then runs HI.
`TYPE README.TXT` shows the on-disk instructions. Backspace maps to Caps Shift+0;
plain 0 remains a digit. A physical PC Delete key depends on Fuse's key mapping.

Game files come from https://eblong.com/infocom/ : Planetfall release 37,
serial 851003; Zork I release 88, serial 840726. Each uses its own configured
copy of the original CP/M version 3 interpreter. The manifest records hashes.

Rebuild after building the 320KB Oliger cartridge:

```text
python tools/build_planetfall.py --collection --output build/infocom-cpm.dsk
```

Verification: native BIOS keyboard tests cover ordinary zero, Caps+0, a Caps+0
event arriving during matrix scanning, held-key suppression, and Ctrl-C. Both
games boot in the actual Fuse JLO controller; game input and SAVE/RESTORE are
checked separately. The physical Windows GUI keyboard remains a manual check.

## Display performance

The updated cartridge copies contiguous raster strips when scrolling, uses
unrolled LDI transfers, unrolls glyph drawing, and skips empty keyboard rows
quickly. Scrolling polls the keyboard once per raster in each display plane;
the longest copy between polls is approximately 14,000 CPU cycles. The top
status row remains fixed when the game has enabled cursor positioning.

Native Z80 cycle counts from `tools/test_console.mjs`, before / after:

| Operation | Before | After | Fewer cycles |
| --- | ---: | ---: | ---: |
| Full-screen scroll | 397864 | 223819 | 43.7% |
| Scroll preserving status row | 381326 | 215659 | 43.4% |
| Ordinary printable character | 3437 | 2421 | 29.6% |
| Clear screen | 274320 | 213282 | 22.2% |

These are controlled emulator CPU measurements, not wall-clock measurements
or hardware contention measurements. Character timing includes BIOS keyboard
polling and transcript logging, with no key pressed. Scroll timing includes
a held A key to verify typeahead. Display tests compare every bitmap byte,
both planes and all third boundaries, and check that attribute memory is
preserved. Planetfall LOOK and Zork I SAVE/RESTORE also pass in actual Fuse.

The RAM-disk build shares the new scroll and keyboard scanning paths. It
retains compact glyph and clear loops to fit its more constrained low BIOS
layout. The faster glyph and clear paths above apply to the Oliger build.

## Disk read optimization

The cartridge reuses the second 128-byte CP/M record already fetched by a
256-byte Oliger sector read. Sequential paired reads need half as many physical
READ commands. Random access and game computation determine the overall gain.
Writes remain synchronous read/modify/write. The pending partner is discarded
on intervening sectors, initialization, HOME, warm boot, console input or errors.
Both 160KB and 320KB controller-model tests check exact command counts and data;
the two-game image is also tested against the actual Fuse JLO controller.
Use the updated DCK with an existing matching 320KB disk to retain saved games.

## High-resolution colors

Type `COLOR` to list the eight schemes. `COLOR n` selects one for the whole
screen, including existing text and the games' status line:

| n | Text | Background |
| --- | --- | --- |
| 0 | Black | White |
| 1 | Blue | Yellow |
| 2 | Red | Cyan |
| 3 | Magenta | Green |
| 4 | Green | Magenta |
| 5 | Cyan | Red |
| 6 | Yellow | Blue |
| 7 | White | Black |

`COLOR 7` restores the default. Invalid arguments show help without changing
the setting. Disk access, scrolling, screen clearing and CP/M warm boots retain
it; a cold cartridge restart restores the default. The eight pairs are fixed
by the TS2068 hardware; foreground/background cannot be chosen independently.
See the TS2068 Technical Manual, SCLD Port FF register and section 5.2.3:
https://device.report/m/1dc234a90e0a0a4909414d23f9dbfa619954ecb352b23266185180d4a7e167b5.pdf

`src/color.asm` changes only port FF bits 3-5, preserving video mode and banking.
`build/COLOR.COM` is also provided separately for existing disk images. Older
RAM-disk cartridges need the updated BIOS to retain colors across disk reads.
