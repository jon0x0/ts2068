# Stock TSPico 1.00 status

The new [320KB SRAM-disk build](tspico-ram.md) implements TAP preload and legacy
MEMDOCK bank switching without a firmware extension. It passes native Z80 and
functional wire/memory-model tests. Physical 1.00 operation, SRAM writes and
FIFO/slot-selection timing still need a board test. It is a hardware-test
candidate, not a claim that a physical device has booted CP/M.

The earlier TPLOAD importer remains available in other profiles. It imports a
single bounded TAP CODE file into an already writable CP/M drive.

Stock 1.00 has no established arbitrary in-place SD-sector write command.
The SRAM design avoids needing one. TPSAVE exports complete TAP chunks that
the cartridge reloads directly; host conversion is optional for Fuse/archive.
Direct inspection of the original frozen SAVE_TS confirms that every SAVE
truncates/creates its destination, writes a header, then appends only that SAVE's
data block and closes it. Successive SAVEs cannot accumulate in one TAP through
that handler. The audit and original flash addresses are recorded in
[firmware-1.00-storage-audit.md](firmware-1.00-storage-audit.md).

The separate [modern SD build](tspico-sd320.md) requires a newer compatible
protocol and optional binary-safe CP/M service. It is not stock-1.00 support.
