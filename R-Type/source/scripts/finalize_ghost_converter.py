from pathlib import Path
import json,zipfile,io,hashlib,numpy as np
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l1_ghost_converter';z=zipfile.ZipFile(O/'test_assets.zip');assert z.testzip()is None;manifest=json.loads(z.read('choices.json'));assert manifest['schema']=='rtype-ghost-art-review/1';info=manifest['families']['ghost'];assert len(info['frames'])==3;assert info['source']['id']=='arcade'
for f in info['frames']:
 w,h=f['width'],f['height'];assert(w,h)==(32,32);p=f'ghost/frame_{f["frame"]:02d}';bits=np.frombuffer(z.read(p+'.bits.bin'),np.uint8).reshape(h,w//8);attrs=np.frombuffer(z.read(p+'.attrs.bin'),np.uint8).reshape(h,w//8);pairs=np.frombuffer(z.read(p+'.pairs.bin'),np.uint8).reshape(w//8,h,2);assert np.array_equal(bits,pairs[:,:,0].T)and np.array_equal(attrs,pairs[:,:,1].T);assert not np.any(attrs&192);mask=np.unpackbits(np.frombuffer(z.read(p+'.preserve.bin'),np.uint8)).reshape(h,w);a=np.array(Image.open(io.BytesIO(z.read(p+'.png'))).convert('RGBA'));assert np.array_equal(a[:,:,3]==0,mask==1)
for n in ['engine_validation.json','browser_validation.json']:assert json.loads((O/n).read_text())['passed']
readme='''R-Type L1 white-ghost / armoured-enemy converter

Open index.html in Chrome or Edge. Standalone/offline, no server or API needed.
Starts paused on the user-confirmed arcade cel454, palette6. Play cycles through
three genuine captured poses450/452/454. Original32x32source pixels, actual
captured palettes, references and converter worker are embedded.
Currentgame comparison is native35/36/37,24x24 fromr110.

Brightness,contrast,saturation,gamma and all other conversion controls apply
to EVERY animation frame. Default is the prior accepted C settings52/59/82/.87;
the preset menu also offers gentler/neutral/originalRPC choices. Adjust freely.
Choose24x24 or32x32storage with size controls. Source is scaled before conversion.
SierraLite/FloydSteinberg/orderedBayer/none, legal8x1pairs, optionalBRIGHTwithout
brightblack, crop/scale/offset/mirror, palette selection, animation and8x1grid.
Blackspace always normalblack. Alpha preserve masks do not solve shared-cell
colourclash. The optionalhorizontalgap policy is mainly for scrolling scenery.

Export choices saves portableJSON. Export ghost asset pack savesPNGframes,
settings and nativepairedrows/masks inZIP. Send either exportedfile back for
integration. Localautosave is specific to this tool and will not overwrite
walker/snake editor settings. Nothing modifies the playable game/cartridge.

Sources450/452/454 are decoded from local originalM72ROM graphics and captured
object/paletteRAM: frames3600/3900/4200,palette6. No AI replacement or authored
intermediate poses. Converter uses the alreadyverifiedRPC-derived worker with
serpentineSierraLite and documented adapters; GPLsource/licence included.
Editor animation timing is illustrative, not gameplay FPS. Game size, overlap,
collision, RAM and actualupdatecost still need checking after your selection.
''';(O/'README.txt').write_text(readme,encoding='ascii');(R/'docs/ghost_art_converter.txt').write_text(readme,encoding='ascii');report=dict(passed=True,frames=3,source='user-confirmed454palette6; genuine450/452/454',zipCRC=True,nativePairs=True,alphaMaskExact=True,sharedSettings=True,htmlSHA256=hashlib.sha256((O/'index.html').read_bytes()).hexdigest());(O/'validation_summary.json').write_text(json.dumps(report,indent=2))
pack=O/'RType_L1_Ghost_Converter.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for name in ['index.html','README.txt','RPC_LICENSE.txt','worker.js','data.json','provenance.json','validation_summary.json','engine_validation.json','browser_validation.json','identity_comparison.png']:f.write(O/name,name)
 for name in ['ghost_art_converter.js','ghost_art_converter.html','l1_art_converter.css']:f.write(R/'src'/name,'source/'+name)
 f.write(R/'scripts/build_ghost_art_converter.py','source/build_ghost_art_converter.py')
with zipfile.ZipFile(pack)as f:assert f.testzip()is None
sha=hashlib.sha256(pack.read_bytes()).hexdigest();print(pack);print(sha,pack.stat().st_size)
entry=f'''\n189. Interactive arcadeghost conversion editor (2026-11-09). User13026.jpg whiteenemiesright, requestsarcadesource+interactivetweaks; userthenconfirms454palette6. NativeL1family35-37identifiedfromactualr110nativebitmapcontact,24x24. Independentlydecodedall177uniqueearlyL1arcadeobjects1200..8100, generatedarcade_identity_contact.png/inventory, visuallyreviewed; exactlongcrest/arm/sideeye source450/452/454 palette6 matched. Actualcapturedobjects450/frame3600,452/3900,454/4200,32x32; all3genuineposes, no448guess or inventedintermediate. identity_comparison.png topnative/bottomarcadegenerated/visuallyreviewed, wholeobjectimagesnotpartialscreenclip. Userconfirms454p6; editorstartspausedonframeindex2, nativeposeorder450/452/454retained.\nStandalonefile://UIreuseverifiedRPC-derivedworker andcontrols withsingleghostfamily, isolatedautosave/schema/exportfilenames, sourcecurrentvsarcade, samefamilysettingsacrossallframes,24/32sizecontrols,crop/resample/mask/scale/rotation,palettes,4dithermodes,8x1inspection,animation,presetsincludingpriorC52/59/82/.87, JSON/PNG/nativeZIPexports. No gameimagechanges. Genuinegray/gold/redarcadepalette retained asRGBsource; conversionsuser-tweakable. User's32x32previouswalkerisNOTsubstitutedforthisdistinctenemy. Worker32corecombinations/palette/normalblack/preservemask/legalpairs PASS. FinalChromeheadlessfile:// all3poses/confirmed454initialpreview/4dithers/gammasettings/24and32/currentvsarcadesource/preset/reset/autosave/JSONroundtrip/actualZIPdownloads/mobile390nooverflow/noJSerrors PASS. ExportZIP3framesCRC/columnmajorpairs/rowmajorbitsattrs/PNGalpha-preservemask/noFLASH/brightblackPASS. Initialbrowserfoundleftoverexportbothlabel,corrected; theninitialpausedbuttonstillPausecaught,fixedUTF8builderinsert; finalbrowserPASS. No falsegameplay/FPS/hardwareclaim.\nGhost_ui.png fullpagegeneratedandvisuallyreviewed; finalfreshghost_ui.png/ghost_mobile.pngcapturedafterlabelfix (layoutunchanged), allimagesdiagnosticUIonly. Sources src/ghost_art_converter.js/.html plus existingCSS; scriptsidentify_l1_ghost.py,build_ghost_art_converter.py,verify_ghost_converter_core.mjs,verify_ghost_converter_browser.mjs,finalize_ghost_converter.py; docs/ghost_art_converter.txt. build/graphics/l1_ghost_converter/index.html standalone andRType_L1_Ghost_Converter.zip SHA256{sha}, {pack.stat().st_size}bytes. OriginalROMZIPs/referenceprojects/read-onlynativegame/releases/r110unchanged. Futureintegrationrequiresuserexportchoice andsize/performance/overlapreview.\n'''
with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
