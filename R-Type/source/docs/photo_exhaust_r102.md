# Large L3 rocket: original photo-based exhaust integrated (r102)

The user identified the large L3 rocket, not the player flame.
The approved four-frame photo conversion was already stored as virtual sprites
224-227, mapped from native34/35. Ordinary L3 calls its plume directly at
HOME F22D via8E85 and8CFD, bypassing the normal actor/compiled dispatch.
The boss shortcut skips the ordinary plume event and was the wrong test route.

Only that native call site is rerouted through a25byte helper in verified
unused L3 DOCK0 padding01C8..01E0. The helper preserves native descriptor lookup,
constructs the zero-orientation stack slot required by the existing compiled
gateway, draws via the existing renderer, and restores the shared sprite ID.
Native owner marker80 is preserved. No sprite40/body replacement, no new artwork,
no player-flame changes, no renderer or memory-bank allocation changes.

Source: src/l3_photo_exhaust_bridge.asm. Build/finalize:
python scripts/build_photo_exhaust_r102.py
Run verify_photo_exhaust_state_r102.mjs, verify_cold_fire_r102.mjs and
verify_native_revisits_r102.mjs with the local Node runtime, then
python scripts/render_photo_exhaust_r102.py
python scripts/finalize_photo_exhaust_r102.py

Ordinary L3 play:81draws cycle224/225/226/227. Stack/shared-ID/IY/inputcoordinates
and native marker preserved. Three coldL3startup/fire tests have no game-over
bypass; the separate400update stress uses that bypass. Cached routes pass.
Only L3's helper/callsite and the loader version text differ from r100. Other
seven levels, includingL5, are byte-identical. Player phases and photo art unchanged.
Static contracts, tape checksums/reconstruction and ZIPCRC pass. Before/after
images are decoded from actual HOME bitmap/ECM planes, not composited mockups.

Package: ../build/fullgame/photo_exhaust_r102/RType_TS2068_r102.zip
Comparison: ../build/fullgame/photo_exhaust_r102/plume_gameplay_comparison.png
Hardware confirmation pending. Keep r100 as the working fallback; its archive
and latest-stable pointer remain unchanged. r101 unrelated art proposals omitted.
