# The Crown — remastered TS2068 cartridge

Release prepared October 14, 2026. Original game by Brian Walker,
©1983 Games to Learn By, Inc. Recovery and remaster by jon0x0.

[Play with the virtual DPad](https://jon0x0.github.io/ts2068/ts2068-cartridges/remastered/TheCrown/play/)
· [Release page](https://jon0x0.github.io/ts2068/ts2068-cartridges/remastered/TheCrown/)
· [Download TheCrown.dck](TheCrown.dck)

The recovered TS2068 BASIC extraction was converted to Leap BASIC and
compiled to bytecode with Leap v2. The cartridge supplies its own execution
runtime derived from official Leap `v2.0.2-emu.1`, revision
`77f1baaf30424f2cec8cf31cae90513faa9c45c5`.

This release includes all three archived levels and their original graphics,
a TSVideoCodec-based eight-frame Extended Colour Mode startup animation,
and a custom Z80 random dungeon initialization routine. Startup takes about
five seconds in emulation. No level cassette or replacement system ROM is needed.

**All three original levels are incorporated into the cartridge. Find the keys!**
No level tape is needed to continue the adventure. To use a key, press
**U** (Use), then **K** (Key); carrying a key alone does not unlock a door.

## Controls

Player 1 joystick works through the real TS2068 AY register 14 input at
`$01F6`; fire is sword attack. The virtual DPad and connected gamepad drive
these same contacts. Diagonals perform one move and creature turn, with
checks against adjacent walls; room-edge transitions use cardinal movement.
This cartridge has been verified in emulators; physical hardware testing is pending.

| Command | Key |
| --- | --- |
| Up / down / left / right | Q / Z / O / P |
| Attack with sword | A, or joystick fire |
| Fire arrow | F |
| Use item | U, then the item key |
| Key / Jump-Ring / Flame-Scroll / Teleport-Gem | K / J / F / T, after U |
| Inventory / Search / Grab / Drink / Wait / Help | I / S / G / D / W / H |
| Start, close a menu, continue | Space or another fresh key |
| Play again | Y: new randomized dungeon; N: animated title |

At the ready startup animation, any game key, virtual game button, joystick
direction or fire/Attack advances to the game. Release a held control before
pressing again; the cartridge also waits for release before entering the room.

Phone controls put the DPad on the left, commands on the lower right and
Y/N above them. Reset, Fullscreen and Audio are in a separate top bar.
Use landscape for more space; portrait remains available.

Attack is a large red thumb button on its own row. Start/Continue sits with
the upper-right controls. On phones the DPad stays centered on the left
edge, and fullscreen expands the game to fit the space between the controls.
The Touch controls toggle hides the DPad and command buttons while retaining
keyboard and gamepad input. A keyboard guide appears outside fullscreen;
fullscreen hides the guide and uses the entire viewport for the game,
preserving its 4:3 picture with letterboxing where needed.

## Package and validation

`TheCrown.dck` is the 65,545-byte DOCK image; `TheCrown.bin` is its exact
65,536-byte physical ROM image. `SHA256SUMS` covers both files.
The cartridge SHA-256 is
`481a5ada28700ce312b5b8388008195701a523da671f7a0fefe7f835a31540cd`.

TSRun checks cover stock-ROM boot, exact decoded animation frames,
decompression and DATA, the held/fresh-key gate, native randomized startup,
all three levels, locked doors, combat, menu graphics, replay and player
redraws. Focused joystick checks cover all eight directions, diagonal corner
collision and fire-as-sword-attack. Fuse independently verifies startup,
prompt, gameplay redraws and return to the intro. Reports are in
`verification/`; build provenance is in `manifest.json`.

The static TSRun player bundles an unmodified emulator snapshot already
used by this hub's Sinistar DPad player. Exact source revision and file hashes
are in `play/tsrun-version.json`; Crown-specific code is in `play/adapter.js`
and `play/controls.js`. Serve from any static HTTP host; no build step is needed.

## History and credits

[Rescuing the Crown — full recovery post](history.html)
· [Original product page](https://www.timexsinclair.com/product/the-crown/)
· [Original cassette media](https://www.timexsinclair.com/computer_media/the-crown/)

TSRun: Josef Jelinek, https://github.com/josef-jelinek/TSRun.
Leap v2: https://github.com/nchiker/2068-Leap-Preview; its MIT license is
retained in `LEAP-LICENSE.txt`. TSVideoCodec:
https://github.com/jon0x0/TSVideoCodec. ZX0's BSD license is retained in
`ZX0-LICENSE.txt`. Stock TS2068 ROM provenance remains in
`play/tsrun/roms/README.md`.

Original title and cassette photographs are from Timex/Sinclair Computers,
with source attribution under the site's CC BY-SA 4.0 terms. Original game
credits and rights are retained; this is not a blanket relicensing of the game.

## Cartridge source

[Download the source package](TheCrown-source.zip) or [read the build instructions](source/README.md). Includes [original recovered BASIC](source/original/TheCrown.bas), [final Leap BASIC](source/leap/TheCrown.leap.bas), all three levels, native Z80 routines, and pinned build dependencies.
