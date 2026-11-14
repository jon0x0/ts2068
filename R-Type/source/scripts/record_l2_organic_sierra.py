from pathlib import Path
import json,hashlib
R=Path.cwd();O=R/'build/graphics/l2_organic_sierra';m=json.loads((O/'manifest.json').read_text());assert len(m['profiles'])==4
for r in m['profiles']:
 assert r['bitmap_bytes']==1760 and r['attribute_bytes']==1760 and r['all_8x1_cells_legal']and r['black_is_normal']
p=R/'build/fullgame/startup_r66/RType_TS2068_r66.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()=='96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60'
state='''

## L2 organic boss Sierra Lite body review (2026-11-06)

User supplies RetroPixelConverter reference and requests arcade-derived organic body/holes/shading. Latest asset review: build/graphics/l2_organic_sierra/index.html. Uses complete arcade frame17400 (frame16800 clipped at right), warm-colour/coarse-hull body isolation and proportional scaling before conversion to160x88. Four legal8x1 alternatives, normal0..7 only: A deep material shading gamma1.35, B pink flesh/bronze ribs gamma1.8, C bright material gamma2.2, D unrestricted coverage SierraLite gamma1.8. A-C RGB-error diffusion with material palette restrictions and pink-hue protection; all mask openings stay black. Final comparison.png visually inspected. Body bits+attrs3520bytes per alternative; no runtime/cache allocation or performance claim. r66 archive unchanged. Asset previews and offline scene compositions only; integration/collision/animated-mouth mapping/scenery synchronization still pending. TEST_HISTORY139.
'''
history='''

## 139. L2 arcade organic body shading alternatives from RPC reference (2026-11-06)

User reference codex-clipboard-d2a758cc-b758-4be9-993d-2f67ba02d069.png shows RPC conversion with strong red/pink/white tissue, yellow rib shading and organic openings. Copied unchanged into build/graphics/l2_organic_sierra/rpc_reference.png for comparison. No instructions inferred from image. User wants this direction applied to L2boss body; no chosen profile yet.

scripts/preview_l2_organic_sierra.py generates index.html, comparison.png, A-D.png, A-D_scene.png, scaled_source.png, arcade_body.png, arcade_context.png, bitmap/attribute/npy arrays and manifest.json. Original arcade frame17400 shows full body; earlier16800 clipped at right and was appropriate only as worm context. Warm colour mask vs blue cave plus coarse contour hull, nearby neutral highlight retention, crop55,96,329,240 then body bbox and LANCZOS proportional scaling into160x88 before saturation/gamma/error diffusion. Source alpha included in review so imperfect isolation/contour loss can be corrected rather than concealed. Internal openings remain normal black; no background noise/diffusion outside silhouette. No source/reference-project modifications.

A gamma1.35 / rib saturation2.5, B gamma1.8 /3.5, C gamma2.2 /4.5 use serpentine RGB SierraLite stencil forward1/2,next opposite1/4,next same1/4, with no error diffusion across transparency or flesh/rib material boundaries. Pink source tissue hue protected at1.1saturation. Flesh cell candidates red/white or black-edge pairs; rib candidates yellow/white or black/shadow pairs. Dark rib pairs allowed even for opaque cells to retain true ridges/cavities. D gamma1.8 / rib saturation3.5 compares unrestricted palette with scalar coverage-error SierraLite. D still uses hue protection for flesh input, so it is a pair/diffusion comparison, not raw RPC equivalence. Displayed/profile metadata distinguishes these policies. No assertion of bit-identical RPC algorithm/output.

First unrestricted RGB fit made tissue too yellow/red; rejected visually. First material-constrained pass preserved pink but ribs went flat yellow due interior-black prohibition; rejected visually. Final allows dark rib pairs and blocks cross-material error, restoring ridges. Final comparison.png inspected, A retains darkest rib/cavity detail, B brighter. PNGs were regenerated during refinements; final files supersede earlier diagnostic views. Every final8x1cell asserts<=2colours, attrs have neitherBRIGHT norFLASH, transparent pixels reconstruct black exactly, output independently reconstructs from bits+attrs byte-identically. Four assets each160x88, bitmap1760+attrs1760=3520bytes, legal normal0..7; no BRIGHT black. NPY uses normal palette IDs, no runtime conversion yet.

A-D_scene.png are clearly labelled offline scale compositions, not playable or collision-compatible screenshots: original boss region cleared and new160x88 body placed atx96,y72 over actual r66 scene context. Native terrain tile decomposition, source actor/animated mouth integration, collision mask compatibility, horizontal scrolling shared-cell policies and timings remain pending. Existing r66 gameplay unmodified; archiveSHA still96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60. L2 scrolling and L3 hardware fragments remain open. No performance/hardware improvement claim. Asset review is a separate milestone from game integration.
'''
for name,text in [('PROJECT_STATE.md',state),('TEST_HISTORY.md',history)]:
 with (R/name).open('ab')as f:f.write(text.encode('utf-8'))
print('4 legal160x88 profiles verified; r66 preserved; history139 appended')
