# Reused cartridge-safe TSPico file library

Originally copied from the owner's prior project; local extensions follow:
`C:/Users/Jon/Documents/ChatGPT/TS2068_TSPicoAnalysis/src/`.
Originating chat: **Document TSPico RAM and disk I/O**.

Local extension: tpi_legacy.asm accepts optional PMR1/PMR2 command parameters
when LEGACY_PARAMETERS is defined, for the stock-firmware MEMDOCK SRAM backend.
Existing importer builds leave that option undefined and retain zero parameters.
Local extension: files_legacy.asm optionally honors SAVE_APPEND/save_append
to omit CLOSE between modern TAP saves. Only TPSAVE enables it, after the
modern protocol handshake and a successful explicit APPEND ON command.
Local correction: tpi_legacy.asm clears captured reply text before reading each
reply, so a quiet status cannot display stale text from a preceding command.
Local cold-loader options: LEGACY_DISCOVERY expands only its directory reply
buffer to 2KiB; LEGACY_FAST_SETTLE shortens ordinary cold reply guards while
keeping the full DIR and volume-transition guards. Resident timing is unchanged.
No upstream TS2068 ROM binary is included or called.

| File | SHA-256 |
| --- | --- |
| files.asm | c8abdf01f9065ed27b785df6bd0394d4b7808300f3966f561833ab56087cda90 |
| tpi.asm | 5f2992727cdbc8e85e07b2f39d8dae86e8008dec36d93d8a65529f4b54e6105f |

The host supplies a relocated workspace and links absolute addresses from
source. The new probe, CP/M image adapter and import utility live in src/.
The library's binary-write restriction is unchanged: normal channel writes
reject byte 17h. The CP/M firmware extension uses independent fixed-sector
handlers and does not change the meaning of ordinary BASIC/channel writes.
