# PicoROM diagnostic cartridge payload

Use `diagnostic-v02-picorom.bin` for a PicoROM-P28 /27C512-style TS2068 cartridge interface. Every normal build emits it, and the release ZIP includes it. It is exactly65536 bytes, identical to `diagnostic-v02.bin`: eight8K chunks in ascending address order, no DCK header, no byte swap and no relocation. The manifest and SHA256SUMS bind the payload to the emulator-tested DCK. The `.dck` file is65545 bytes and is for a compatible virtual cartridge loader, not PicoROM upload.

## Get the PicoROM executable

Download the controller from [Martin Donlon / wickerwaka’s official PicoROM releases](https://github.com/wickerwaka/PicoROM/releases). For Windows 64-bit, choose **picorom-x86_64-pc-windows-msvc.exe** ([direct latest download](https://github.com/wickerwaka/PicoROM/releases/latest/download/picorom-x86_64-pc-windows-msvc.exe)). Rename it **picorom.exe** and place it in the extracted Diagnostic Lab release directory, beside **diagnostic-v02-picorom.bin**. The controller is not bundled in our release. Other operating-system binaries are available on the same releases page.

Open PowerShell in that directory. The ` .\ ` prefix below runs an executable in the current folder; if installed on PATH, `picorom` alone also works.

Connect PicoROM over a USB data cable using your board’s documented power arrangement. Power the TS2068 off before fitting or removing the cartridge. Match the controller and device firmware major versions: the upstream v2 controller and v1 firmware cannot communicate, and vice versa. Follow the [upstream installation guide](https://github.com/wickerwaka/PicoROM/blob/main/INSTALL.md) if firmware or driver setup is needed, selecting the actual board variant. Do not confuse the PicoROM firmware version with TSPico’s version.

## Identify and upload

From the release directory:

```powershell
.\picorom.exe list
.\picorom.exe upload --help
```

`list` reports device names. **2068** is a device name, not a machine-type parameter or filename. If your device is named **2068**, upload and persist the cartridge with:

```powershell
.\picorom.exe upload 2068 -s diagnostic-v02-picorom.bin 512KBit
```

Otherwise replace **2068** with the name returned by `list`. Optionally rename the device with `.\picorom.exe rename CURRENT_NAME 2068`, replacing CURRENT_NAME with its actual name. Renaming is not required. `-s` stores the image in flash for power cycles; omit it for a volatile trial.

Use **512KBit** with that capitalization, as shown by the installed controller’s `upload --help`: it means **64KiB**, exactly **65536 bytes**. The local P28 firmware contract has16 address inputs and ROM_SIZE0x10000. This BIN contains ROM data, not RP2040 firmware UF2. Use firmware appropriate to the actual PicoROM board.

## Verify the upload

Read back the image and compare SHA256 hashes:

```powershell
.\picorom.exe download 2068 diagnostic-readback.bin
Get-FileHash .\diagnostic-v02-picorom.bin -Algorithm SHA256
Get-FileHash .\diagnostic-readback.bin -Algorithm SHA256
```

Again use your actual device name. Both hashes must match and readback must be65536 bytes. Then cold-start the machine with the cartridge fitted. If `list` finds nothing, check the data cable, matching controller/firmware, and that the device is running normally rather than showing BOOTSEL’s storage volume. Consult the upstream installation guide for version-specific setup; its Windows WinUSB instructions concern firmware-update/PICOBOOT access, not a blanket instruction to replace other USB drivers.

These commands are operator instructions, checked against local CLI help. No hardware upload/readback has been performed by the diagnostic build, which never changes device settings or commits flash automatically.

## Cartridge interface requirements

The cartridge interface must decode all eight DOCK chunks and correctly connect A0-A15, D0-D7 and read/chip enables. On an NF6X-derived open-collector bank decoder, all eight selected-bank outputs must participate in ROM /CE for this image. The image does not configure jumpers or repair an interface that exposes only32K. Keep the upstream electrical/power and startup-readiness requirements; a successful image conversion is not physical validation. The existing LROS HOME-initialization dependency remains.

TSPico is a separate device. Its `.dck` loader and its control of /BE and DOCK selection must be treated independently from the PicoROM's raw bytes. The supplied older TSPico manual explicitly says to remove cartridges before installation; simultaneous physical-cartridge operation has not been verified. Follow TSPICO_PROFILE.md rather than assuming both devices can drive DOCK together.

Sources: [Martin Donlon/wickerwaka PicoROM](https://github.com/wickerwaka/PicoROM), its host `rom_size.rs`/upload command and P28 `system.h`; the inspected PicoCartridge2068 interface crosswalk; TS2068 original technical manual/schematic; and the TS2068 cartridge skill's `dck_to_picorom.py`. Source credits remain in CREDITS.md / THIRD_PARTY_CREDITS.md.
