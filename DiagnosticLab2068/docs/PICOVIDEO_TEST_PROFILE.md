# Optional PicoVideo diagnostic profile

PicoVideo will be a separately selected external-hardware module, disabled during stock automatic tests. The user chooses the installed board/firmware profile before any ULA+ writes. Unknown optional capabilities produce NOT RUN. This profile is specified only; the v0.1 diagnostic image has no PicoVideo control code.

## Documented interface and source

The [PicoVideo project](https://github.com/timex-sinclair-projects/PicoVideo) and its [manual](https://github.com/timex-sinclair-projects/PicoVideo/blob/main/PicoVideo%20manual.pdf) credit **Jeff Burrell** as designer/programmer. The manual describes register selection at BF3B, data at FF3B, 64 palette entries, palette enable through register64, and GRB332 color data. It describes display-write/FE/FF monitoring and local video memory. SHA256 of the inspected25-page manual is `42ccadcd8ef349d3d39fedd52799b0d37d6336c0540bfc0171ed185f5a801253`.

The manual includes generic optional ULA+ extensions; do not assume every feature is present in every board/firmware revision. Verify the selected profile against its actual source/manual version. Keep Timex FF video-mode selection separate from optional mode-register mirrors. Do not invent a device ID or interpret a floating read as reliable hardware detection.

## Test modules

| ID | Test | Planned method |
|---|---|---|
| PV-01 | Palette register path | Select each supported palette register, use distinct address-dependent values and walking meaningful data bits, compare supported readback; inspect all entries after changes to expose index aliasing |
| PV-02 | Color channels and palette ramps | Pure channels, intensity steps, grayscale and known-color swatches; distinguish numeric register matches from user-observed VGA color/output |
| PV-03 | Attribute to CLUT selection | Give four CLUTs unmistakably different palettes; exercise ink/paper indices and attribute selector bits; compare against the selected profile's expected lookup |
| PV-04 | Native mode reproduction | Compare standard, second display, ECM and hires patterns on PicoVideo and native output; record intentional palette differences separately from timing/fetch failures |
| PV-05 | Display-write capture and load | Row/column IDs, repeated/complementary writes, sequential and scattered/burst updates to both display files; verify HOME bytes and observe external update completeness; add qualified banking load only afterward |
| PV-06 | Mode exit and recovery | Enable/disable supported palette mode, cancel between bounded phases, restore a known native mode and readable reporting; simulate missing responses without hanging |

In PV-03, attributes used as palette selectors in the selected ULA+ profile must not be evaluated using native FLASH/BRIGHT expectations. The TS2068's own output may intentionally look different while PicoVideo uses an enhanced palette. In PV-02, use the documented color encoding for the installed version rather than treating an8-bit entry as eight independent equally weighted RGB bits.

PV-05 should also investigate CPU ROM overlays: compare external capture with CPU-visible HOME readback when DOCK covers a display chunk. Exact expected handling of writes to a selected ROM must be established from PicoVideo firmware before declaring a failure. A write sniffer and the machine's physical RAM can observe different events; this is not automatically a bad SCLD.

## Recovery and attribution

All register/response loops have ROM-held bounds; no external response is required for the diagnostic scheduler to continue. Preserve stackless ROM control and qualified HOME ranges. Treat palette readback as optional evidence rather than a required exit mechanism. Keep a known recovery palette/mode plan in ROM; optional prior settings may be saved in verified RAM, but corrupted saved state cannot control recovery.

On completion, cancellation or detected mismatch, disable enhanced palette use through the confirmed profile interface, restore native mode0 with the intended DECR interrupt/bank bits, and enter normal reporting through a fixed ROM path. The user should be able to use native output or border/beeper reporting if external output becomes unusable, provided those machine paths still work. Do not wait forever for a picture or apply firmware updates as part of the test.

Record separate results for HOME read/write, native SCLD display, PicoVideo palette/register behavior, external write capture and physical output. A correct PicoVideo picture cannot certify native SCLD video generation; a clean CPU readback cannot certify PicoVideo capture. Missing output alone does not uniquely locate board, connector, firmware, cable, converter, monitor or machine faults.

## Prerequisites and acceptance

Required: explicit external-hardware selection, documented board/firmware capability profile, baseline ROM execution, qualified target display ranges and an operator viewing the appropriate output. The diagnostics remain ROM-only; the external hardware does not become writable diagnostic workspace by assumption.

Acceptance needs a supporting emulator/model for actual enhanced registers plus physical PicoVideo testing. Save image hashes, board/firmware version, palette/mode profile, native/external observations and cancellation/recovery outcomes. Verify unrelated stock tests issue no BF3B/FF3B accesses. Current stock TSRun checks cannot establish enhanced PicoVideo behavior.

Credit Jeff Burrell, the PicoVideo project contributors and the TS-Pico team; credit ZX Design and Media for the ULAplus format. The manual also acknowledges V. Hunter Adams' PIO VGA work. No PicoVideo firmware or manual program listing is copied into the diagnostic by this specification.
