from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/player_weapons_r54'
def main():
 s=json.loads((OUT/'validation_summary.json').read_text());assert s['passed'];digest=hashlib.sha256((OUT/'RType_TS2068_r54.zip').read_bytes()).hexdigest();r=s['reports'];p=s['l5_input_profile'];cache=r['cache_progression_validation.json'];boss=r['boss_preview_validation.json']['results'];m=json.loads((OUT/'manifest.json').read_text());comp=r['overlay_component_validation.json']
 doc=ROOT/'docs/r54_player_weapons.md';text=doc.read_text();assert '## Final measured build'not in text;doc.write_text(text+f"""
## Final measured build

Engine {m['overlay_bytes']} bytes; helper {m['damage_bytes']} bytes. Final player component mean/max {comp['mean_tick_cycles']:.1f}/{comp['max_tick_cycles']} cycles versus r53's11132.0/48887. The added correctness work is small in that component after retaining the non-copy fast path and replacing old-mask compositor work with row copies.

L5matched movement/fire route: {p['ticks']} player ticks /480refreshes versus r53's162; all8shortpresses and1chargedhold register. World updates{p['world_updates']}, same as the recorded r53route. This is a workload sample, not a universal unchanged-FPS claim. Full resident-cache/ending/revisit route {cache['frames']}refreshes. All8boss700-update routes pass.

Package `build/fullgame/player_weapons_r54/RType_TS2068_r54.zip`, SHA256 `{digest}`. Physical validation pending.
""",encoding='utf-8')
 history=f"""

## 116 - Projectile travel and live-world ship/exhaust spill, r54 (2026-11-04)

User confirms r53player moves well; requests faster projectiles and reports intermittent L5boss fragments around player/exhaust. Clarified flame behind ship, not Force pod. Reproduced stale-rectangle replay in native component: after snapshot, unrelated byte changedA5->3C/attr2; r53republishesA5/attr7. Exact old/new mask-union publication now preserves live pixels outside ship and untouched ECM cells. Retained cleanup likewise uses current ship-only coverage, avoiding a second stale replay.128changing-world cases across8horizontal phases/eightdirections/fine+held steps protect6271872outside-coverage bit checks after publication+cleanup. Coverage includes cached exhaust footprint. No newly authored flame-animation clock; separate flame-symptom question remains for hardware feedback. Legal shared8x1colour conflicts not claimed eliminated.

Player memory: OLD F6C0..F700,NEXT F700..F740,coverageF740..F781,pairedscratchF781..F803,rowpointersF820..F83A,cleanWORLD F83A..F87A,collisionF880..FB00. Helper{m['damage_bytes']}bytes F080 belowF100backingpixels; engine{m['overlay_bytes']}bytes fitsE400..ED80. Existing phases/flippedcache/palettes/art/IRQgateway/shader/joysticks/audio unchanged. Removed unreachable fast_prepare pixel/attr branches: internal retained-window caller is restore_copy withMETA0; prepare already uses render. Kept ordinary non-copy composition/publication fast path; copied old mask rows withLDI, shared partial-byte merge registers and used full-byte coverage shortcuts. Early mask prototype cost more and reduced input cadence; rejected. Final normal component mean/max {comp['mean_tick_cycles']:.1f}/{comp['max_tick_cycles']} versusr5311132.0/48887; matched L5ticks162->{p['ticks']},8shots+1beam,worldupdates10->{p['world_updates']}. Settings1pxfine/5pxheld retained; no universal equal-FPS claim.

16-slot normal/spread updater takes up to3original travel steps with metadata checks at each native-step endpoint, stops at first enemy/terrain, ignores friendly/dirtyIDs<80, then native final draw/hit path once. Original native stride/collider granularity retained, not a new per-pixel sweep. Normalclear travel2->6cells; actual native slot8->10old/8->14new; bitmap/ECM/metadata match original at same destination. Single-slot example5823->6845cycles.4088native helper direction/bounds/intermediate-blocker/friendly-ID cases pass, full-pool allocator checks pass. Charged beams/other pools retain timing; weapons still world-clocked, not independently higher-rate redraw. Source low-bank FFgaps statically checked. Allnative damage/sound calls retained.

Development diagnostics: baseline replay fail retained as reproduce_player_spill.mjs. First helper tests omitted loading new helper into their fixture and failedSP; fixture corrected. Changing-world comparison initially included injected input byteDOCK3:14FA outside playfield; restored it before comparing. Initial broad retained cleanup also replayed stale neighbours; current-mask cleanup fixes it. Initial sweep stopped on any nonzero cell, corrected to enemy/terrain>=80 to avoid friendly shots/dirty cells. Earlier regression passes during optimization were not release evidence; final serial run freezes all9regionSHA hashes. Diagnostic ship_current.png is an offline packed centre-phase preview, initially blurred then rerenderednearest-neighbour with actual packed colours and viewed; no new gameplay image or physical photo generated. Native HOME/bin/profile captures retained.

Final frozen gates:7565IRQ-boundary injections (scan/audio stubs only in isolated boundary test),16slot capacity,894player ticks plus retained/frozen/empty/collision checks,128live-world-change cases,4088sweep cases,actual native shot comparison, chosen keys/bothjoysticks,8normal+1beam,real death/respawn,title116,snake,restarts3/8,four loader failures,all8boss700updates, full8residentcache/ending/revisit{cache['frames']}refreshes. Bossrefreshes {[(v['level'],v['frame'])for v in boss]}. Source/cache ownership,72pages/hash/XOR/archive integrity checked. Stock64KBROM,originalarchives,referenceprojects unchanged. Hardware validation pending.

Deliverable build/fullgame/player_weapons_r54/RType_TS2068_r54.zip SHA256 {digest}. Replace complete RTYPEfolder and reset before RTFULL.TAP; old or larger-art level files must not be mixed.
"""
 h=ROOT/'TEST_HISTORY.md';assert b'## 116 -'not in h.read_bytes();h.open('ab').write(history.encode('utf-8'))
 state=f"""

## Latest packaged build: r54 (2026-11-04)

Normal/spread projectiles travel up to3native steps (normal2->6cells) per world update, stopping at intermediate enemy/terrain, one original final draw/hit. Friendly IDs ignored. Original projectile update clock/charged-beam/other-pool timing retained. Live-world ship/exhaust stale-background spill reproduced and fixed using exact coverage on publication and retained cleanup.128phase/direction/fine+held live-change cases pass. No new flame animation claimed; hardware symptom clarification pending. Player movement settings/input preserved; final L5{p['ticks']}ticks vsr53162/480refreshes,8shortshots+1beam,worldupdates{p['world_updates']}. Final componentmean/max{comp['mean_tick_cycles']:.1f}/{comp['max_tick_cycles']}; noncopy fast paths retained after rejecting slower prototypes.

New helper{m['damage_bytes']}bytesF080, engine{m['overlay_bytes']}bytes; coverageF740,damagescratchF781,cleanWORLDmovedF83A with static bounds. Art/boss sizes/phasecache/joystick/audio/IRQbanklogic unchanged. Final frozen regionSHA+serial gates:7565IRQ,16slotcapacity,894player ticks,128changedworld,4088projectilesweep,native finaldraw equivalence, controls/fire/death/title116/snake/restarts/errors, all8boss700 and full8cache/ending/revisit{cache['frames']}refreshes;72pages+ZIP verified. Stock64KBROMunchanged, hardware pending. docs/r54_player_weapons.md and TEST_HISTORY116.

Deliverable build/fullgame/player_weapons_r54/RType_TS2068_r54.zip SHA256 {digest}. Reset/reload complete matching RTYPEfolder.
"""
 (ROOT/'PROJECT_STATE.md').open('ab').write(state.encode('utf-8'));print(digest)
if __name__=='__main__':main()
