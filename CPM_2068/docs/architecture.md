# Memory and boot architecture

The Z80 runs CP/M directly. No host-side BDOS calls or second emulated CPU are
used. Interrupts stay disabled; keyboard polling does not need the TS ROM.

| Address | CP/M mapping | Purpose |
| --- | --- | --- |
| 0000–00FF | DOCK RAM | Warm boot/BDOS vectors, IOBYTE, FCBs and default DMA |
| 0100–3FFF | DOCK RAM | Transient programs |
| 4000–7FFF | DOCK RAM | Transient programs, shadowing both HOME screen planes |
| 8000–CFFF | HOME RAM | Transient programs |
| D000–D7FF | HOME RAM | CCP (may be overwritten by suitable transients) |
| D800–E5FF | HOME RAM | Digital Research BDOS and workspace |
| E600–EFef | HOME RAM | BIOS, font, disk buffer and directory workspace |
| EFF0–EFFF | HOME RAM | Boot diagnostic/autostart state |
| F000–F5FF | HOME RAM | Combined-build TSPico service code |
| F600–F7FF | HOME RAM | TSPico common workspace |
| F800–FDFF | HOME RAM | Diagnostic transcript ring |
| FE00–FFFF | HOME RAM | System stack; cold/warm initial SP=FF00 |

The ordinary TPA below the CCP is 53,248 minus 256 = **52,992 bytes**. Programs
using the BDOS vector as their upper limit can reclaim the CCP; warm boot
restores CCP and BDOS from immutable cartridge pages. This is a custom 64 KB
address-space layout rather than an unmodified standard 64K CP/M BIOS location.

Normal F4=$0F maps DOCK chunks 0–3. FF=$3E selects white-on-black high resolution
mode 6 with DOCK as the alternate bank. Physical HOME display RAM remains at
$4000–$57FF and $6000–$77FF. Each character is 8 pixels wide; alternating columns
use the first and second plane. Drawing temporarily uses F4=$03, then restores
$0F. BIOS code, font, stack and buffers stay above $E600 throughout.

The AROS descriptor is in DOCK chunk 4, at $8000, entry $8008. It copies a loader
to HOME $5B00. The loader maps source chunk 5 to copy $A000–$BFFF into HOME
$D000–$EFFF, then maps source chunk 6 to copy $C000–$CFFF into HOME $F000–$FFFF.
Source and destination chunks are deliberately different. It writes and verifies
an address-derived pattern across $0000–$3FFF. Failure halts with a red border
and saves the address at $EFF2. It enters BIOS at $E600 with F4=$03, so its own
instructions remain mapped until the jump. BIOS then enables both screen shadows.

The first warm entry installs JP $E603 at 0, JP $D806 at 5, selects DMA $0080,
and executes a seeded CCP command `HELLO`. Subsequent warm boots do not rerun
the automatic command and preserve disk RAM.

## RAM disk and BIOS

The BIOS contains the conventional **17 CP/M 2.2 jump entries**. READ/WRITE
validate geometry and move 128-byte logical sectors through a common buffer.
Storage-specific code is isolated in `src/blockdev_ramdisk.asm`. Drive A uses
six writable EXROM pages (1-6), providing 48 KB without reducing the TPA.
Page 0 remains ROM-owned for cartridge startup; page 7 retains BIOS and stack.
See [storage-backends.md](storage-backends.md) for the complete sector API,
geometry and future TSPico/Oliger contracts.

DPB: SPT=16, BSH=3, BLM=7, EXM=0, DSM=47, DRM=63, AL0=$C0, AL1=0, CKS=0,
OFF=0. Twenty-four tracks, 16 zero-based sectors/track, 1 KB allocation blocks,
64 directory entries, two directory blocks, 46 data blocks. Identity translation.
Invalid drive/track/sector returns an error. Writes remain volatile.

DCK blocks: bank 0 types `[3,3,3,3,2,2,2,0]`, then bank 254 types
`[0,3,3,3,3,3,3,0]`. Seven DOCK payload pages plus six EXROM payload pages and
two nine-byte headers make **106,514 bytes**. Types 2/3 carry 8 KB; type 1 does
not carry data. This supersedes the original diagnostic and 8 KB disk layouts.

CONST polls into a 31-character FIFO; CONIN consumes its oldest character.
Output and each scrolling character row also poll the keyboard. Changed keys
are accepted without requiring an observed all-released interval; repeated
identical keys require release. Input is still polled, so a transient program
that runs without BIOS calls can miss brief presses. Interrupt-driven scanning
and full multi-key rollover remain future work.
The console implements printable ASCII, CR, LF, BS, FF, wrapping and scrolling.
Editing across a wrapped line, tab expansion, terminal escape sequences and
key repeat are not yet complete. Display is 64 columns, but the stock 2.2 CCP
directory formatter still has its original formatting conventions.
