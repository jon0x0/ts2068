# Building and validation

Release v0.2 | October 12, 2026

The supplied release images are the tested outputs. Firmware source, asset
generators, test scripts and current image-bound emulator evidence are included.
The original development workspace remains authoritative.

The build scripts currently expect the development/reference directory layout:
Python with Pillow; SjASMPlus 1.20.3 (use --assembler with build_suite.py to choose
an executable); and the verified stock TS2068 U16 ROM at the path specified in
build_suite.py and build_home_rom.py. The ROM is used to extract the embedded
character font. Original Timex manuals/schematics and third-party reference
programs are not republished here; see THIRD_PARTY_CREDITS.md for sources.

The complete entry point is python scripts/build_cartridge.py. For a different
assembler path, run python scripts/build_suite.py --assembler PATH, followed by
python -c "from scripts.build_home_rom import build; build()" with scripts on
PYTHONPATH. Verification scripts import a compatible sibling TSRun checkout;
manual generation uses ReportLab. Fuse/native/browser verification also expects
the locally configured tool paths. Adjust paths for a new development machine.

Historical validation snapshots are retained in the original workspace; only
the current image evidence is published here. Some historical registry/source
references therefore require that workspace. Read AGENTS.md and
docs/PROJECT_STATE.md before changing diagnostic behavior. Physical validation
is still pending.
