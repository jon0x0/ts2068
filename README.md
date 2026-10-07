# TS2068

Projects for the Timex Sinclair 2068: development tools, arcade and Spectrum
ports, demos, applications, audio and video.

This repository is a central directory and a home for new project source.
Existing projects keep their repositories and published URLs. Adding a project
here does not require moving it or changing links shared elsewhere.

**[Project hub](https://jon0x0.github.io/ts2068/)** � **[Cartridge downloads](https://jon0x0.github.io/ts2068/ts2068-cartridges/)** — a catalog of `.dck` files for
games, applications, audio and demos, linking to their owning projects.

## Development tools

| Project | Description | Links |
| --- | --- | --- |
| AI skill | Reusable AI skills, tools, examples and technical references for TS2068 development | [Repository](https://github.com/jon0x0/AISkill_TS2068) |
| TSRun | Browser emulator used by the playable ports and demos; upstream project by Josef Jelinek | [Repository](https://github.com/josef-jelinek/TSRun) · [Emulator](https://josef-jelinek.github.io/TSRun/) |

## TS2068 Arcade ports

| Project | Status | Links |
| --- | --- | --- |
| Berzerk | Existing standalone project with TSRun touch controls | [Repository](https://github.com/jon0x0/berzerk_ts2068) · [Play](https://jon0x0.github.io/berzerk_ts2068/) |
| Sinistar | Playable v58 development checkpoint; emulator-verified, physical hardware validation pending | [Play with virtual D-pad](https://jon0x0.github.io/ts2068/arcade-ports/sinistar/play-dpad/) � [Newer TSRun](https://jon0x0.github.io/ts2068/arcade-ports/sinistar/play/) · [Source](arcade-ports/sinistar/) · [Cartridge](arcade-ports/sinistar/play/assets/sinistar.dck) |

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
| Beast demo | Shadow of the Beast inspired parallax cartridge demo | [Repository](https://github.com/jon0x0/beastdemo_ts2068) · [Play](https://jon0x0.github.io/beastdemo_ts2068/) |
| Aqueduct | Aqueduct and speedboat parallax demo | [Repository](https://github.com/jon0x0/aqueduct_ts2068) · [Play](https://jon0x0.github.io/aqueduct_ts2068/) |

## Applications

| Project | Description | Links |
| --- | --- | --- |
| TSWriter | Native word processor with proportional fonts, extended color, pictures and RTF interchange | [Repository](https://github.com/jon0x0/TSWriter) · [Project page](https://jon0x0.github.io/TSWriter/) |

## Audio and video

| Project | Description | Links |
| --- | --- | --- |
| speech2ay | Harmonic AY synthesis for speech and effects, including the TS2068 Audio Lab | [Repository](https://github.com/jon0x0/speech2ay) · [Audio Lab](https://jon0x0.github.io/speech2ay/) |
| TSVideoCodec | SCLD-aware video codec | [Repository](https://github.com/jon0x0/TSVideoCodec) |

## Working with the source

Sinistar's existing Git history is retained. Its source lives under
`arcade-ports/sinistar/`; the original-source submodule is pinned by the
root `.gitmodules` file. Existing development checkouts can remain at their
current paths. See [maintenance notes](MAINTENANCE.md) for how to update this
import without creating competing source copies.

For a fresh checkout, initialize submodules and place the existing compatible
TSRun checkout at `TSRun/` beside `arcade-ports/`. TSRun is a local
dependency and is ignored by this repository. Then follow the
[Sinistar build instructions](arcade-ports/sinistar/README.md).

Project assets and dependencies retain their own attribution and licensing.
This directory does not apply a blanket license to third-party material.
