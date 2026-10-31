# How the 512K video player works

## RAM playback and banking

TSPico supplies 512 KiB of external SRAM, organized here as eight 64 KiB
regions, each containing eight fixed-address 8 KiB chunks. Stock firmware
1.00 `MEMDOCK` selects SRAM and even slots 0,2,…14. The TS2068's F4 register
maps the needed chunk; FF chooses DOCK rather than EXROM. This does not
require replacing the Pico's memory-controller PIO.

Each option has sixteen TAP volumes holding four 8 KiB pages apiece, plus
metadata, an index and checksums in the first volume. The loader receives
each page in HOME RAM, installs it in SRAM, reads it back and compares every
byte. A final sweep detects overwritten/aliased banks. All 64 pages are
loaded even where unused bytes are padding.

After loading there are **no SD file reads during playback**. The Pico still
receives MEMDOCK commands to change SRAM regions; RAM playback is not the
same as disconnecting the Pico or continuously streaming the video from SD.
Three 8 KiB HOME caches and mount-ahead scheduling overlap upcoming SRAM
fetches/region commands with playback. All data for the next complete frame
record must be cached before its patches are applied.

Execution stays in HOME RAM: code at E000+, caches at 8000–DFFF, a resident
interrupt handler and HOME stack. A gateway at 5B00 with a private HOME
stack handles chunk 7 without hiding live code or stack. Alias cases copy
through a protected HOME bounce buffer. Interrupt state and mappings are
restored before returning. No runtime ROM library or BASIC calls are needed.

## Menu, quit and safe loading cancellation

Space and Enter stop playback and return directly to the menu. Q is available
at the menu, during loading and during playback. X retains the optional
statistics screen. Controls are shown on the loading screen as well as the menu.

During file transfer, the receiver latches a request while continuing to consume
the payload, checksum, acknowledgement and reply. The request takes effect at
a completed transaction boundary. Keyboard requests during bank-command replies
also wait for the command to drain. This avoids the legacy FIFO becoming stuck.

Menu return and quit disable rendering/interrupts, unmap DOCK and restore Flash
DOCK slot 0. Quit then selects normal display mode, IM1 and a clean stack and
jumps to HOME ROM 0000. It restarts normal ROM/BASIC startup: the full-control
player has overwritten BASIC's workspace, so returning through its original
USR stack would be unsafe. The previous SRAM contents are not restored.

Real matrix-key tests cover Space, Enter and Q during playback and loading,
Q at the menu, X statistics, cancellation during a region reply, and a working
file mount/load after a cancelled transfer. Native Fuse also verifies the ROM
0000 handoff with SP=FFFF, IM1 and both interrupt flip-flops clear.

## The MEMDOCK lesson

The first loader failed its page-00 header readback. A revision with a longer
HOME delay also failed. The working R3 path adds eight read-only DOCK
accesses after MEMDOCK and before writing. The relevant PIO selectors can
be waiting within an access loop when a new selection is queued; command
acknowledgement and elapsed HOME time alone do not establish consumption.
R3 also changed unrolled LDI copies to CP/M-style LDIR. These shipped
together, so their separate effects were not isolated on hardware. An
access-driven selector model reproduces the old failure and passes R3.
Eight reads are the tested sequence, not a universal minimum timing claim.

## Frames, extended color and paired patches

The display uses TS2068 8×1 extended-color mode. At each display-file offset,
one bitmap byte chooses between the two colors specified by the corresponding
attribute byte in the second plane. Each 8×1 cell shares its BRIGHT selection.
Both planes use the ZX/Timex display-address permutation. A full decoded
screen is 6,144 bitmap bytes plus 6,144 attribute bytes: **12,288 bytes**.
The smaller active windows occupy that full layout with blank borders.

The first screen is stored in two SRAM pages. Subsequent frames, including
the exact last-to-first transition, contain only changed pairs of bytes.
Each patch is a 16-bit HOME destination address and a 16-bit replacement:
four stored bytes replace two screen bytes. This is a speed-oriented expanded
delta representation, not the smallest possible compressed stream. Records
are padded to 256-byte blocks, each with 64 patches. Addresses are validated
before playback; padding writes only to a reserved scratch address.

A fixed Z80 kernel borrows SP for POP HL/DE, writes the paired word, and
restores the normal stack before re-enabling interrupts. bitmap and attribute
patches are part of the same frame record. Frames are reconstructed exactly
relative to the offline quantized images; video scaling and palette conversion
are lossy. There is no intentional spreading of a frame's cells across several
playback frames. Display writes are still sequential raster-visible writes,
not an atomic hardware page flip or a guarantee of zero tearing.

| Version / mode | Initial image + padded patches | Average padded delta, including loop | Maximum delta |
|---|---:|---:|---:|
| SW 256×108 @ 12 | 464,896 bytes | 5,029.0 bytes | 11,008 bytes |
| SW 240×102 @ 15 | 493,824 bytes | 4,261.4 bytes | 9,984 bytes |
| SC 256×108 @ 12 | 491,008 bytes | 5,319.1 bytes | 11,008 bytes |
| SC 232×98 @ 15 | 480,768 bytes | 4,145.8 bytes | 9,216 bytes |

Each option's full allocation remains 524,288 bytes. The difference between
useful bytes and allocation covers page headers, padding and unused page
space. Only one option is resident at a time.

## Ordered dithering: why the gaps appear

The apparent gaps are deliberate black or dark pixels, not skipped display
positions. Every position exists at the stated active resolution. The source
is separately downscaled to fit the chosen window; dithering does not itself
reduce that resolution.

Each 8×1 cell has only two available colors, so continuous photographic shades
need spatial mixtures. A fixed **8×8 Bayer threshold matrix** decides which
of those colors each pixel uses. A darker gray may be sparse light pixels
against black; skin and warm midtones may need red/yellow/gray mixtures.
At viewing distance these patterns suggest intermediate shades, but at close
range the dots and gaps are visible. Skin remains difficult because the palette
has no native brown or peach and several source colors can share one cell.

Ordered dither was chosen because its deterministic screen-space pattern
avoids independent frame-to-frame random noise, makes unchanged areas stable,
and usually reduces unnecessary changes compared with fresh random dithering.
That helps both flicker and delta storage. It is inexpensive to encode and
adds no dither calculation to the Z80 decoder: all decisions are offline.
Motion crossing the pattern can still shimmer. Error diffusion or temporal
dither could produce different still-image results, but can propagate small
changes across more pixels or require extra display changes; they are not
used in these versions.

The quantizer fits two-color segments in a perceptual working space, applies
fixed Bayer coverage and uses a small previous-attribute tie-breaker. It
excludes the established preview palette's problematic BRIGHT-black entry.
The baseline uses saturation 1.0, gamma 1.06 and a chroma-error penalty to
avoid false cyan/magenta in neutral areas. Colour Detail 2 computes per-pixel
color confidence, weights real colored details more heavily, relaxes the
neutral penalty locally, and adds at most 10% selective saturation. It is
not a global saturation increase. This can preserve cockpit lights and
markings that otherwise lose the cell's color-pair vote to surrounding gray.

## Frame rate and limits

Pacing targets 12 fps (five nominal 60 Hz ticks) or 15 fps (four ticks), with
adaptive delays when preparation runs late. New colors can increase delta
sizes even with an unchanged decoder. The complete 15 fps Colour Detail 2
clip at 240×102 needed 508,928 patch bytes and exceeded the page budget;
232×98 fits with 468,480 patch bytes. The original 240×102 conversion fits
with 481,536 patch bytes. No source frames were silently dropped to fit.

The README lists achieved functional-model averages and hardware-report
boundaries. Individual frames can start late around bank changes, large
updates and the loop transition. MP4 previews show target cadence, not those
modeled stalls. A physical fps measurement requires the player's counters
and a timed hardware run; no such numeric hardware result was supplied.

## TSRun

Checked 2026-10-31: upstream Josef Jelinek TSRun main and the public nchiker
and factus10 forks have no TSPico implementation in their current source or
documentation. In upstream `machine.js`, ports 0E/0F do not dispatch a Pico
device: ordinary even-port keyboard/EAR behavior or floating reads apply.
There is no legacy shared-FIFO transaction engine, mounted SD/TAP service,
MEMDOCK command handling or eight-region 512 KiB SRAM device.

TSRun's TS2068 display modes and ordinary DCK RAM support do not make this
demo runnable. Supporting it would require those TSPico facilities and their
interaction with F4/FF, memory writes and bank-switch completion. A specially
preloaded browser adaptation could avoid some file services but would be a
different integration, not an emulation of this hardware installation.

Sources inspected: [upstream machine.js](https://github.com/josef-jelinek/TSRun/blob/main/machine.js),
[upstream README](https://github.com/josef-jelinek/TSRun/blob/main/README.md),
[nchiker fork](https://github.com/nchiker/TSRun), and
[factus10 fork](https://github.com/factus10/TSRun).
