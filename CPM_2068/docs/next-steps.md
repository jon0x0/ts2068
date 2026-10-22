# Next implementation work

1. Port the CP/M 3 family to this proven cartridge/console memory architecture.
   CP/M 3 supports a nonbanked system; its system guide describes GENCPM and the
   CPM3.SYS loader. Start there to avoid assuming physical TSPico bank selection.
   It requires a CP/M 3 BIOS contract, loader and its CCP utility; this is not
   achieved by changing the 2.2 version string. Source, build tools, redistribution
   terms and exact version must be pinned before integration. The primary
   reference is https://www.cpm.z80.de/manuals/cpm3-sys.pdf and source archive
   index https://www.cpm.z80.de/source.html .
2. The emulator disk now combines EXROM pages 1-6 into 48 KB and carries
   seven standard utilities plus assembly examples and TPIMPORT. Keep the 5 KB working space
   available; DDT/XSUB remain in the pinned utility ZIP. A larger persistent disk
   will be needed for a complete CP/M 3 distribution.
3. The cartridge-safe TSPico library is now vendored, with a combined detector,
   stock read-only image adapter, raw-file importer and optional binary-safe
   firmware image service. Models/host tests pass; physical testing is pending.
   The owner wants a configured ordinary SD directory exposed as a CP/M drive,
   rather than image-file storage. Implement that filesystem bridge next, with
   explicit 8.3/case, record-length, capacity, metadata and host-editing rules.
4. Add persistent storage using that protocol, or an Oliger backend for the
   installed community Fuse. Controller support in this executable alone does
   not establish its geometry or CP/M compatibility; inspect its source and use
   disposable disk images before writes. Existing RAM disk tests are the oracle.
5. Finish keyboard and terminal controls, add independent Fuse keyboard
   checks, and explicitly characterize hard reset/soft reset/reinsert in both
   emulators. Current reset behavior is inherited from the handoff, not retested.

## Physical target status

**Unverified: emulator-only.** No SRAM enable, write gating, GPIO selection,
EXROM mapping, bus ownership or WAIT timing has been established for the user's
actual board revision in this implementation. No flashable hardware payload is
claimed. The 12 KB system section and AROS source can be reused by a specialized
PicoCartridge/TSPico loader after an equivalent memory/storage contract exists.

Use section 9 of the original handoff for the electrical checklist. Both display
shadow pages require writable RAM in addition to lower 16 KB; this first image
needs 32 KB of DOCK RAM plus 48 KB of independently mapped disk RAM. A ROM-only
PicoCartridge cannot run this image merely by removing its DCK headers.
