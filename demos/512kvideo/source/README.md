# Portable 512K video source and converter

Requires Python 3.10+, NumPy, Pillow, FFmpeg on PATH, and sjasmplus for player
assembly. Run commands from this source directory. No input movie or system
ROM image is included. The two released player sources and original font
are included; rebuilding does not require access to the development workspace.

```sh
python -m pip install -r requirements.txt
python tools/build_player.py --variant detail2 --assembler /path/to/sjasmplus
python tools/build_player.py --variant original --assembler /path/to/sjasmplus
```

Outputs are `build/SC512.TAP` and `build/SW512.TAP`. The assembler must be
executable by the Python process: use Windows sjasmplus with Windows Python,
or Linux sjasmplus with Linux/WSL Python. `SJASMPLUS` can replace --assembler.

## Player controls

Space or Enter returns to the menu. Q quits by restoring Flash mapping and
restarting normal ROM/BASIC startup; the old BASIC workspace is not preserved.
During loading, a request is latched and the current transaction finishes
before it takes effect. X shows playback statistics. The loading screen and
menu show the controls. These controls also apply to generated custom players.

## Convert another local movie

```sh
python tools/convert_video.py "your-local-video.mp4" --start 44.5 --duration 7.5 --mode 256x108@12 --mode 232x98@15 --prefix CV --output build/custom --assembler /path/to/sjasmplus
```

Use two `--mode WIDTHxHEIGHT@FPS` options; defaults are the two shown. Width
must be in 8-pixel steps, within 256; height within 192; fps must divide 60.
Choose dimensions that approximately preserve the source's aspect ratio.
The current formatter aligns the window to byte columns, so widths with an
odd count of byte columns can have slightly unequal left/right borders.
Each option must fit 512 KiB including the initial image, page headers and
the closing delta. Overflow is reported instead of silently truncating the
interval. Use a smaller window, shorter interval or lower frame rate if needed.

Use `--colour original` for the first neutral-color quantizer, or the default
`--colour detail2` for the revised color emphasis. `--data-only` skips assembly
while still generating data, metadata and player source. The tool independently
reconstructs and checks every frame and the closing transition before release.
It prints progress, accepts no remote URL, and never modifies the input movie.

Use a fresh output directory and a two-letter uppercase prefix distinct from
other demos. The example produces `CV512.TAP`, `CVF000.TAP`–`CVF015.TAP` and
`CVW000.TAP`–`CVW015.TAP`, plus source/index/verification files. Its generated
menu describes those exact modes and frame counts. Copy the **33 TAP files**
directly to the SD card's **`/TAP/` directory; they will not run elsewhere**.
Generated assembly is also kept at `src/cv512_generated.asm`; use another
prefix if that name already exists. No automatic SRAM upload occurs.

## Layout and provenance

`src/`: both released Z80 players and their transport, decoder and display
includes. `tools/`: portable converter, tested memory-layout functions,
both quantizers and BASIC+CODE TAP wrapper. `build/font.bin`: original font
asset. `vendor/svd_ecm.py`: TSVideoCodec's ECM frame model, from commit
54524b93644f938eb34e9e48f9af9cf3cd05fb58, source path
`src/encoder/svd_ecm.py`, SHA256
0cbde1871bebcafe56a5d1bbafcdb1d6adc573c90d43f460e10cc1a17c1a6e59.

The wrapper uses the same Timex BASIC token values as the hardware-working
release, loads CODE at C000 and enters at E100. The optional video player
is separate from the general legacy file library; applications such as
TSWriter need not include it. See ../TECHNICAL.md for the memory map and
ordered-dithering rationale. Original upstream projects and media retain
their attribution; no third-party movie is included in this source archive.
