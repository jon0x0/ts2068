from pathlib import Path
import json,zipfile,io,hashlib,numpy as np
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l1_blue_enemy_converter';count=0
for filename,expected in [('test_246_assets.zip',1),('test_walk_assets.zip',2)]:
 z=zipfile.ZipFile(O/filename);assert z.testzip()is None;m=json.loads(z.read('choices.json'));assert m['schema']=='rtype-blue-enemy-art-review/1';fam=m['families']['blue'];assert len(fam['frames'])==expected
 for f in fam['frames']:
  w,h=f['width'],f['height'];p=f'blue/frame_{f["frame"]:02d}';bt=np.frombuffer(z.read(p+'.bits.bin'),np.uint8).reshape(h,w//8);at=np.frombuffer(z.read(p+'.attrs.bin'),np.uint8).reshape(h,w//8);pairs=np.frombuffer(z.read(p+'.pairs.bin'),np.uint8).reshape(w//8,h,2);assert np.array_equal(pairs[:,:,0].T,bt)and np.array_equal(pairs[:,:,1].T,at);assert not np.any(at&192);mask=np.unpackbits(np.frombuffer(z.read(p+'.preserve.bin'),np.uint8)).reshape(h,w);im=np.array(Image.open(io.BytesIO(z.read(p+'.png'))).convert('RGBA'));assert np.array_equal(im[:,:,3]==0,mask==1);assert(w,h)==(fam['settings']['width'],fam['settings']['height']);count+=1
for name in ['engine_validation.json','browser_validation.json']:assert json.loads((O/name).read_text())['passed']
records=json.loads((O/'source_candidates.json').read_text());same=[x['pixelSHA']for x in records if x['code']==246];assert len(same)==3 and len(set(same))==1
readme='''R-Type L1 blue enemy - interactive source/conversion comparison

Open index.html in Chrome or Edge. Standalone/offline, no server/API needed.
The picturedcyanenemy is native41, currently40x40. This tool does NOT change
acceptedlargewalker43/44orvirtual201-204, nor the playable game.

A: original246/palette6, actualframe2400. Closest picturedpose.
246/p11at2700and246/p2at3900arebyte-identicalRGBA: verified, not distinct
colourchoices. Changingcapturedpalette-numberalone does not improve it.
B: original256/258 relatedwalkingposes, normalizedunflippedfacing. May provide
betterlegmovement; native41iscurrentlyonepose, so animatingitrequiresgamework.
C: original260/262action/boostposes. Notadditionalwalkingintermediates.
Current: actualr114native41forcomparison.

AllarcadeRGBusesactualverifiedpalettefromframe2400; canonicalROMtilelayout
avoidsalternatingdirectionfromcapturedspriteflipflags. Sourcegalleryincludes
capturedalternatives, whereaseditablewalksourcehasconsistentfacing.
No AIreplacement, no inventedintermediateframes.

Default40x40 matchescurrentgamefootprint. Change32x32fororiginalarcadepixel
size; sourceRGBisscaledbeforeRPCconversion. No integrationorperformancefit
is implied byeditorchoices. Defaultconversionreuseslastghostsettings56/66/89/
gamma0.74. PresetsincludepriorC52/59/82/.87andneutral/soft/RPCchoices.

Brightness/contrast/saturation/gamma/crop/palette/dither apply to ALLposes in
selectedset. Sourcecomparisons,currentart,32/40size,animation,8x1grid/inspector,
SierraLite/FloydSteinberg/orderedBayer/none,normalblack,noFLASH/brightblack.
Localautosaveisindependentofghost/walkereditors. ExportchoicesJSONorblueenemy
assetZIP whenready; ZIPincludesPNGs/preserve masks/bitmap/attributes/column-
majorpairedrows/settings/provenance. Sendexportbackforintegrationreview.

GPLsource/licenceprovided. IllustrativeeditoranimationisnotgameFPS.
''';(O/'README.txt').write_text(readme,encoding='ascii');(R/'docs/blue_enemy_converter.txt').write_text(readme,encoding='ascii');report=dict(passed=True,native=41,source246ExactCaptured=True,duplicatePaletteRGBVerified=True,walkingFacingNormalized=True,exportsChecked=count,nativePairs=True,preserveMaskMatchesPNG=True,htmlSHA256=hashlib.sha256((O/'index.html').read_bytes()).hexdigest());(O/'validation_summary.json').write_text(json.dumps(report,indent=2));pack=O/'RType_L1_Blue_Enemy_Converter.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for name in ['index.html','README.txt','RPC_LICENSE.txt','data.json','worker.js','provenance.json','validation_summary.json','engine_validation.json','browser_validation.json','source_candidates.png','source_candidates.json']:f.write(O/name,name)
 for name in ['blue_enemy_converter.js','blue_enemy_converter.html','l1_art_converter.css']:f.write(R/'src'/name,'source/'+name)
 f.write(R/'scripts/build_blue_enemy_converter.py','source/build_blue_enemy_converter.py')
with zipfile.ZipFile(pack)as f:assert f.testzip()is None
sha=hashlib.sha256(pack.read_bytes()).hexdigest();print(pack);print(sha,pack.stat().st_size)
entry=f'''\n191. Picturedcyancrestednative41 /246comparisoneditor (2026-11-09). User13027.jpg asksbetterarcadematchthan246p6andinteractivecomparison. Exactr114native41visualidentityconfirmed40x40, distinctfromalreadyupgradednative43/44andvirtual201-204. LocalROM/capturedobjectcomparison246p6/frame2400,246p11/2700,246p2/3900haveidenticalRGBA SHAef6baf87a67c..., notgenuinedifferentpalettes. Captured256p11/3000and258p7/3300providesamefamilywalkingalternatives. Captured258facingoppositetocaptured256; editorusescanonicalROMunflipped256/258, notalternatingfacingasfakegait. ROM260/262explicitlylabelledaction/boost, notwalkingintermediates. No claimthesewalkposesautomaticallymatchnative41'ssingleposebehaviour. No forcedsourceidentitywithacceptedotherwalkerfamily.\nGeneratedsource_candidates.png8images/currentnativeandcaptured246variants/256/258/action260/262visuallyinspected; canonical246assertbyteidenticalactualcaptured246p6. canonical246/256/258/260/262.pngsavedfromoriginalROM; noAI/newart. Interactiveonebluefamily editor choices A246single,Bwalk256/258,Caction260/262,currentnative41; default40x40matchescurrentfootprint,32originalsizeoption. Sharedsettingsperselectedposes, default56/66/89/.74aslastghostchoice, presetsinclpriorC/neutral/soft, fullRPC/SierraLite/dither/palette/crop/size/animation/cellinspector/exportcontrols. Blue-onlyautosave/schema/filenames,sourcegalleryembedded,noexternalnetwork/server. No gameplay/bank/cartridgechange.\nWorker32corecombinations/paletterestriction/normalblack/preservemask/legalpairsPASS. FinalheadlessChrome file:// A1/B2/C2/current1pose selection; all4dithers/sharedgamma/32and40sizes/animationplaypause/presets/autosave/reset/JSONroundtrip/actualAandBZIPdownloads/mobile390nooverflow/noJSerrorsPASS. ZIPexports3framesCRC/rowmajorbitsattrs/preserve mask/columnpairedrows/PNGalphaexact/sharedsize/noFLASH/brightblackPASS. blue246_ui.png,walking_alternative_ui.png,blue_mobile.pngcaptured;walkingalternativefullpagevisuallyreviewed. UIanimationNOTgameFPS,nofit/speed/hardwareclaim.\nScriptsidentify_l1_blue_enemy.py,build_blue_enemy_converter.py,verify_blue_enemy_core.mjs,verify_blue_enemy_browser.mjs,finalize_blue_enemy_converter.py;src/blue_enemy_converter.js/.html;docs/blue_enemy_converter.txt. Standalonebuild/graphics/l1_blue_enemy_converter/index.html, ZIPRType_L1_Blue_Enemy_Converter.zip SHA256{sha} {pack.stat().st_size}bytes. OriginalROMZIPs/referenceprojects/gameversionsr114andearlierunchanged. Futureintegrationrequiresuserselectedsource/settings/sizeandperformance/behaviourreview.\n'''
with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
