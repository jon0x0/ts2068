# Source and build instructions

Run these commands in this package's `source` directory using desktop
Python 3.10 or later. They never connect to the Pico.

```powershell
python -m pip install --target tools/python -r requirements-test.txt
python -m pip install --target tools/serial-python -r requirements-serial.txt
```

The ready-to-stage patched ROMs are included. To rebuild the baseline from
scratch, supply the original English Spectrum 128 ROM halves. The originals
are not duplicated in this publication. Required SHA-256 values are:

| Input | SHA-256 |
| --- | --- |
| ROM 0 | `3ba308f23b9471d13d9ba30c23030059a9ce5d4b317b85b86274b132651d1425` |
| ROM 1 | `8d93c3342321e9d1e51d60afcd7d15f6a7afd978c231b43435a7c0757c60b9a3` |

```powershell
python build_rom.py --rom0 /path/to/rom0 --rom1 /path/to/rom1
python build_fs128_rom.py
python build_handoff128.py
python build_fs128_probe.py
```

Build order matters: baseline, SD ROM/service image, then matching handoff
TAPs. The probe build also supplies the small FS128.TAP test file. Its probe
ROM is a diagnostic, not the normal SD BASIC ROM.

```powershell
python -m unittest test_rom test_stock128 test_handoff128 test_fs128_basic test_fs128_paging test_fs128_legacy test_fs128_gateway test_fs128_probe test_pico_debug test_dma_backend test_start_fs128_sd
```

`test_rom` includes original-versus-patched checks and expects the original
files produced by `build_rom.py`. The other included functional tests use
the staged patched ROMs and source. Tests run on the desktop only; a pass
does not constitute physical hardware acceptance.

After changes, rebuild the dependent images and copy matching ROM/TAP files
to SD again. Never mix an older handoff TAP or generated `fs128_image.py`
with a different ROM. Build manifests conservatively default hardware status
to false: rebuilding does not certify a new image. This publication's
STATUS.json records physical evidence separately from generated build metadata.

The two packages intentionally contain the same support-source snapshot,
because the existing helper loads shared definitions for both modes and the
handoff builder builds both TAPs. Their top-level guides select the appropriate
ROM and launch argument. They are not independent firmware forks.

## Source map

- `build_rom.py`: guarded baseline ROM patcher and full byte-change manifest.
- `build_fs128_rom.py`: SD ROM patcher, assembled HOME driver, generated image.
- `build_handoff128.py`: revision-2 host trampoline and TAP packaging.
- `build_fs128_probe.py`, `build_nopaging_rom.py`: supporting diagnostics.
- `firmware/`: complete current MicroPython controllers, gateway, backend,
  generated service bytes, handoff, and diagnostic definitions.
- `start_handoff128.py`, `start_fs128_sd.py`, `start_fs128_sd.ps1`,
  `pico_debug.py`: actual desktop helper contents, not pseudocode.
- `references/fs128/`: Z80 transport and layout sources with provenance.
- `references/rp2*.py`: MicroPython assembler references with their MIT notice.
- `rom_machine.py`, `pio_model.py`, `fs128*_model.py`, `test_*.py`:
  functional models and regression tests.
- `build/rom`, `build/fs128-rom`, `build/handoff128`: checked-in runtime
  artifacts at the paths the current helpers expect.

The source retains original internal names `zx128` and `zx128sd`. Public
package names are `tpzx128` and `tpzx128sd`. There is no `/MODES` discovery,
`tpi:mode` command, or automatic persistent installation in this snapshot.

## Attribution

The patched images derive from the original English Spectrum 128 ROMs;
their original rights and attribution remain. This import does not apply a
new blanket license to those images or third-party dependencies. The
MicroPython assembler reference retains its MIT notice. SkoolKit is a
separately installed GPL host dependency and is not part of Pico runtime code.
Z80 transport provenance is recorded in `source/references/fs128/PROVENANCE.txt`.
The original unmodified ROM halves and unrelated game files are not included.
