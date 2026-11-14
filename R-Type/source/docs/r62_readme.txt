R-Type 2068 r62 - Force interaction and immediate preload feedback

Replace the complete RTYPE folder, reset, and load RTFULL.TAP. Expanded-memory disk build; stock 64KB cartridge unchanged. Do not mix files from different versions.

The Force pod can dock using the native collision rules again. Player graphics remain independently updated at pixel resolution; the logical collision footprint is now published before weapons and pickups run. Your defined sixth action detaches/recalls the Force (Space in the original default bindings). Keyboard and both native joysticks remain active together.

Shift-L immediately silences all three AY channels and displays LOADING, then saves the game and opens the detailed logo/progress screen. After loading missing levels it restores the game and sound. An all-resident request remains a no-op. The early message uses standard attribute cells without changing the underlying game bitmap or ECM colour plane.

L, release, then 1-8 changes level. Starting selection 1-8 remains available during loading. Fully verified levels stay in RAM; incomplete levels reload. M toggles music; B, release, B previews the boss.

Level-6 minor enemies 5-17 still await an approved arcade-derived replacement; the comparison options are asset previews, not silently installed graphics. Boss graphics remain as before.

See validation_summary.json and project test history for completed emulator checks and limitations. Physical hardware confirmation is still required; no new overall frame-rate claim.
