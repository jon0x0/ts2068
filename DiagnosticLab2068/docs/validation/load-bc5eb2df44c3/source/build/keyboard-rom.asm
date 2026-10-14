 ORG $e000
 INCLUDE "symbols.txt"
keyboard_rom_scan:
 INCLUDE "keyboard-scan.asm"
 jp keyboard_scan_done
 ASSERT $ <= $e600
