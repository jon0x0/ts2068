# TS2068

**[Making the Timex do more by drawing less — graphics and optimization article](https://jon0x0.github.io/ts2068/articles/drawing-less/)**

Projects for the Timex Sinclair 2068: development tools, arcade and Spectrum
ports, demos, applications, audio and video.

This repository is a central directory and a home for new project source.
Existing projects keep their repositories and published URLs. Adding a project
here does not require moving it or changing links shared elsewhere.

**[Project hub](https://jon0x0.github.io/ts2068/)** · **[Cartridge downloads](https://jon0x0.github.io/ts2068/ts2068-cartridges/)** â€” a catalog of `.dck` files for
games, applications, audio and demos, linking to their owning projects.

## TSPico personalities

V2.2 denotes the board revision. Current firmware/protocol support is v1.00;
provision for the next protocol version is planned, not yet implemented or validated.

Two functional Spectrum 128 BASIC implementations for the Timex TS2068
using TSPico hardware revision V2.2 / RP2040. The baseline **tpzx128**
provides the ROM and banked-memory environment; **tpzx128sd** adds
TSPico disk-interface handling accessible from Spectrum 128 BASIC.
Uses TSPico's bank-switchable memory to provide a Spectrum 128-style memory layout and banking system on the Timex TS2068.

General Spectrum software compatibility is not guaranteed. Each project
page lists tested features, memory-map differences, bank switching and
known limitations. Both include complete
source, current USB helpers, matching ROM/TAP files, and startup procedures
that leave Pico firmware and saved boot configuration unchanged.

| Package | Status | Links |
| --- | --- | --- |
| tpzx128 | Working | [Procedure and download](personalities/tpzx128/) · [Technical description](personalities/tpzx128/TECHNICAL.md) |
| tpzx128sd | Working | [Procedure and download](personalities/tpzx128sd/) · [Technical description](personalities/tpzx128sd/TECHNICAL.md) |

See the [personality directory](personalities/) for requirements and recovery.
These trial packages do not implement the proposed automatic mode menu.

## Remastered games

| Project | Description | Links |
| --- | --- | --- |
| The Crown | All three recovered dungeon levels, Leap v2 bytecode/runtime, TSVideoCodec startup animation and a native random dungeon initializer; keyboard and eight-direction player 1 joystick support | [Release](ts2068-cartridges/remastered/TheCrown/) · [Play with virtual DPad](ts2068-cartridges/remastered/TheCrown/play/) · [TheCrown.dck](ts2068-cartridges/remastered/TheCrown/TheCrown.dck) |

## Development tools

**[CP/M 2.2 for TS2068](CPM_2.2_2068/)** ·
[Run in browser](https://jon0x0.github.io/ts2068/CPM_2.2_2068/play/) ·
[Quickstart](https://jon0x0.github.io/ts2068/CPM_2.2_2068/docs/quickstart.html).
TSPico banked RAMDisk, 160/320KB Oliger/Fuse images, 64/80-column console,
Python disk tools, utilities, assembly examples and the Planetfall/Zork I disk.

| Project | Description | Links |
| --- | --- | --- |
| TS2068 Diagnostic Lab | ROM-based hardware diagnostics, RAM chip/bit reporting and simplified replacement HOME ROM; v0.3 | [Project](DiagnosticLab2068/) · [Release](DiagnosticLab2068/release/TS2068DiagnosticLab-v0.3.zip) · [Manual](https://jon0x0.github.io/ts2068/DiagnosticLab2068/docs/manual/) |
| AI skill | Reusable AI skills, tools, examples and technical references for TS2068 development | [Repository](https://github.com/jon0x0/AISkill_TS2068) |
| TSRun | Browser emulator used by the playable ports and demos; upstream project by Josef Jelinek | [Repository](https://github.com/josef-jelinek/TSRun) Â· [Emulator](https://josef-jelinek.github.io/TSRun/) |

## TS2068 Arcade ports

| Project | Status | Links |
| --- | --- | --- |
| Berzerk | Existing standalone project with TSRun touch controls | [Repository](https://github.com/jon0x0/berzerk_ts2068) Â· [Play](https://jon0x0.github.io/berzerk_ts2068/) |
| Sinistar | Playable v58 development checkpoint; emulator-verified, physical hardware validation pending | [Play with virtual D-pad](https://jon0x0.github.io/ts2068/arcade-ports/sinistar/play-dpad/) · [Newer TSRun](https://jon0x0.github.io/ts2068/arcade-ports/sinistar/play/) Â· [Source](arcade-ports/sinistar/) Â· [Cartridge](arcade-ports/sinistar/play/assets/sinistar.dck) |

Sinistar includes a self-contained browser player using Josef's October 4,
2026 TSRun, isolated from the versions used by other projects. Serve this
repository with `python -m http.server 8772 --bind 127.0.0.1` and open
<http://127.0.0.1:8772/arcade-ports/sinistar/play/>. Public players are linked above.

For comparison, [Sinistar with Berzerk's virtual D-pad](arcade-ports/sinistar/play-dpad/)
uses a separate copy of the modified emulator, with Fire and Sinibomb touch
buttons and the full keyboard guide visible beneath the game. The newer
TSRun player and the existing Berzerk project are preserved.

## Spectrum ports

Elite conversion work is currently local. Source and a public link will be
added when it is ready for publication.

## Demos

| Project | Description | Links |
| --- | --- | --- |
| SCLD Display Lab | Twelve families of native ECM/high-resolution/standard-mode mixes and attribute-race experiments; quick cartridge switching, CRT off. | [Run the demos](https://jon0x0.github.io/ts2068/demos/SCLD/) · [Cartridges](demos/SCLD/downloads/SCLD-cartridges.zip) · [Source & notes](demos/SCLD/) |
| 512K video | Requires TSPico; complete movie clip preloaded into 512 KiB SRAM and looped in 8×1 extended color, 12/15 fps targets. Put all TAP files directly in `/TAP/`; they will not run elsewhere. | [Preview & instructions](https://jon0x0.github.io/ts2068/demos/512kvideo/) · [Download](demos/512kvideo/downloads/tspico-starwars-colour2-512k.zip) · [Source & converter](demos/512kvideo/source/) |
| Boing Ball | Bouncing ball in Extended Colour Mode with AY sound | [Play](https://jon0x0.github.io/TSVideoCodec/?demo=boing) · [Repository](https://github.com/jon0x0/TSVideoCodec) |
| Juggler | Banked video cartridge with temporal reconstruction | [Play](https://jon0x0.github.io/TSVideoCodec/?demo=juggler) · [Repository](https://github.com/jon0x0/TSVideoCodec) |
| Newton | Tape-loadable RAM-player demo | [Play](https://jon0x0.github.io/TSVideoCodec/?demo=newton) · [Repository](https://github.com/jon0x0/TSVideoCodec) |
| Beast demo | Shadow of the Beast inspired parallax cartridge demo | [Repository](https://github.com/jon0x0/beastdemo_ts2068) Â· [Play](https://jon0x0.github.io/beastdemo_ts2068/) |
| Aqueduct | Aqueduct and speedboat parallax demo | [Repository](https://github.com/jon0x0/aqueduct_ts2068) Â· [Play](https://jon0x0.github.io/aqueduct_ts2068/) |

## Applications

**[ZXDesk2068](https://jon0x0.github.io/ts2068/ZXDesk2068/)** — a TS2068 port of
**[mindbox77’s original ZX Spectrum ZXDesk](https://github.com/mindbox77/zxdesk)**,
a windowed desktop with [normal-screen](https://jon0x0.github.io/ts2068/ZXDesk2068/?mode=normal#try)
and [512×192](https://jon0x0.github.io/ts2068/ZXDesk2068/?mode=hires#try) TSRun demos,
TAP downloads, source archive, and a [2068 mouse-interface proposal](https://jon0x0.github.io/ts2068/ZXDesk2068/#mouse).
TSPico filesystem 2.x support is planned.

| Project | Description | Links |
| --- | --- | --- |
| TSWriter | Native word processor with proportional fonts, extended color, pictures and RTF interchange | [Repository](https://github.com/jon0x0/TSWriter) Â· [Run in browser](https://jon0x0.github.io/TSWriter/play/) · [Project page](https://jon0x0.github.io/TSWriter/) |

## Audio and video

| Project | Description | Links |
| --- | --- | --- |
| speech2ay | Harmonic AY synthesis for speech and effects, including the TS2068 Audio Lab | [Repository](https://github.com/jon0x0/speech2ay) Â· [Audio Lab](https://jon0x0.github.io/speech2ay/) |
| TSVideoCodec | SCLD-aware video codec | [Repository](https://github.com/jon0x0/TSVideoCodec) |

Build instructions and development notes are in each project's README.

Project assets and dependencies retain their own attribution and licensing.
This directory does not apply a blanket license to third-party material.
