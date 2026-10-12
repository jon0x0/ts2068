# Diagnostic Lab simplified keyboard diagram

The user-requested [published keyboard.png](https://josef-jelinek.github.io/TSRun/keyboard.png) is533x191. Its exact bytes are preserved at assets/keyboard/TSRun-keyboard.png, verified identical to the URL on2026-10-12. See provenance.json for SHA256 and the inspected TSRun keyboard.js geometry snapshot. Artist/source: Josef Jelinek, TSRun.

## Native adaptation

scripts/keyboard_art.py crops each source keycap, extracts the largest connected white key face and fills its horizontal contour to remove unreadable sub-pixel BASIC legends. It scales that contour deterministically into non-overlapping8x8 attribute-cell rectangles. Main letters/numbers and SPACE are drawn with the embedded TS2068 font. The black SYMBOL SHIFT appearance, staggered rows and wider CAPS/ENTER/SPACE regions are retained within the256-pixel display's limits. Short labels: CS=CAPS SHIFT, EN=ENTER, SY=SYMBOL SHIFT, BR=BREAK. This is an adapted view, not a pixel-for-pixel display of the whole533-pixel artwork.

All42 physical positions are present. The40 electrical contacts have separate optional history bytes5B00-5B27; both CAPS positions share the same contact/history. BREAK is derived from CAPS+SPACE and uses one additional history byte5B28. ENTER+SPACE is a diagnostic exit chord and does not falsely mark BREAK.

Unseen keys have bright white PAPER (78 hex), held keys bright green (60), and previously released keys bright cyan (68); INK stays black. The inverse SYMBOL SHIFT legend takes the paper color while its face stays black. Source credit appears on screen. A wide key changes across its entire fixed rectangle, without changing neighbors.

## Firmware and mapping

The graphical keyboard cannot be encoded as ordinary font tiles, so its prebuilt bitmap/attributes are bounded raw data loaders into4000-5AFF. ROM3 may supply data only for destinations entirely in4000-5FFF. ROM2 may supply only destinations entirely in6000-7FFF. The executing ROM0 anchor remains selected throughout, and loaders restoreHSR01. Native video still fetches HOME RAM.

The generated half-row scans remain stackless. src/modules.asm::keyboard_paint paints exactly two rows with a ROM-immediate width and destination. It preserves D (exit hold), E (input bits), IX (scan budget), AF' (selection) and the alternate result registers. History corruption changes only bounded color choices; it cannot set pointers, counts or continuations. The finite scan budget and CAPS+SPACE/ENTER+SPACE exits remain.

## Evidence and remaining limits

scripts/verify_keyboard.mjs checks all40 matrix contacts, exact whole-key attribute coverage, neighbor isolation, shared CAPS, derived BREAK, ENTER+SPACE distinction, corrupt history and exit with all HOME writes lost. It captures W/CAPS held and A released for the manual. Physical contact health, real display readability and timing still require target testing. The artwork does not turn an unpressed key into a passed key or implement the future prompted key-by-key certification.

The original image and source attribution are preserved in the asset/provenance files and THIRD_PARTY_CREDITS.md/CREDITS.md.

## Future extended-color keyboard

The current native diagram is substantially simplified rather than a faithful reproduction of the source image. Consider a separately selectable extended-color-mode presentation of the original keyboard, with its colored legends preserved where legible. Native extended color provides8x1 color cells but remains256x192: it improves color placement, not horizontal resolution. The533-pixel-wide source still needs careful scaling, cropping or a detail view to make small legends readable. Preserve live key feedback with bounded ROM-directed updates to the appropriate attribute plane and retain the existing finite exit handling. This is a future visual option, not an implemented diagnostic mode.
