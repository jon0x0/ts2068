# TSPico personalities

Two functional Spectrum 128 BASIC environments for the Timex TS2068 with
TSPico hardware revision V2.2 / RP2040. **tpzx128** is the baseline
implementation; **tpzx128sd** adds TSPico disk-interface handling accessible
from Spectrum 128 BASIC. Neither is guaranteed compatible with all
Spectrum 128 software. Each page lists tested features, memory mapping,
bank-switching behavior and known incompatibilities.
Current firmware/protocol support is v1.00. Provision for the next protocol
version is planned through a separate backend and is not yet implemented or validated.
These packages use temporary SRAM ROM staging and USB REPL definitions;
they do not require permanent Pico firmware or startup changes.

| Package | Current status | Documentation |
| --- | --- | --- |
| [tpzx128](tpzx128/) | Boot and functional BASIC confirmed on hardware; baseline no-reset startup also confirmed | [Procedure](tpzx128/README.md) · [Technical description](tpzx128/TECHNICAL.md) · [Build](tpzx128/BUILD.md) |
| [tpzx128sd](tpzx128sd/) | Boot, functional BASIC, directory listing and file loading confirmed on hardware; other disk operations separately qualified | [Procedure](tpzx128sd/README.md) · [Technical description](tpzx128sd/TECHNICAL.md) · [Build](tpzx128sd/BUILD.md) |

Each directory contains source, current helper scripts, matching ROM/TAP files,
checksums, status, and a complete download ZIP. Starting discards the current
Timex session and SRAM contents. Full recovery requires removing both Timex
and Pico USB power. TS Reset alone is not recovery. Read the package procedure.

The proposed automatic mode directory/menu is not implemented by these trials.
