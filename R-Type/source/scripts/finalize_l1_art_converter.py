from pathlib import Path
import json,zipfile,io,hashlib,numpy as np
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l1_art_converter';z=zipfile.ZipFile(O/'test_assets.zip');assert z.testzip()is None;m=json.loads(z.read('choices.json'));count=0
for family,info in m['families'].items():
 s=info['settings'];assert all(v['width']==s['width']and v['height']==s['height']for v in info['frames'])
 for f in info['frames']:
  w,h=f['width'],f['height'];p=f'{family}/frame_{f["frame"]:02d}';bits=np.frombuffer(z.read(p+'.bits.bin'),np.uint8).reshape(h,w//8);attrs=np.frombuffer(z.read(p+'.attrs.bin'),np.uint8).reshape(h,w//8);mask=np.unpackbits(np.frombuffer(z.read(p+'.preserve.bin'),np.uint8)).reshape(h,w);pairs=np.frombuffer(z.read(p+'.pairs.bin'),np.uint8).reshape(w//8,h,2);assert np.array_equal(pairs[:,:,0].T,bits)and np.array_equal(pairs[:,:,1].T,attrs);im=np.array(Image.open(io.BytesIO(z.read(p+'.png'))).convert('RGBA'));assert np.array_equal(im[:,:,3]==0,mask==1);assert not(attrs&128).any();count+=1
assert count==14
report=dict(passed=True,frames=count,zipCRC=True,nativePairLayout=True,preserveMaskMatchesPNG=True,familySettingsShared=True,workerSHA256=m['rpc']['worker_sha256']);(O/'export_validation.json').write_text(json.dumps(report,indent=2))
for name in ['engine_validation.json','browser_validation.json','extra_browser_validation.json','export_validation.json']:assert json.loads((O/name).read_text())['passed'],name
htmlsha=hashlib.sha256((O/'index.html').read_bytes()).hexdigest();workerhash=hashlib.sha256((O/'worker.js').read_bytes()).hexdigest();assert json.loads((O/'engine_validation.json').read_text())['workerSHA256']==workerhash
for name in ['browser_validation.json','extra_browser_validation.json']:assert json.loads((O/name).read_text())['htmlSHA256']==htmlsha
assert report['workerSHA256']==workerhash
readme='''R-Type L1 artwork converter - walker and snake (2026-11-09)

OPEN
Open index.html in Chrome or Edge. No server, installation, API key or internet
connection is needed. Original source pixels, references and the RPC worker
are embedded. The game and cartridge files are never modified.

WORK
Choose Round walker or L1 snake. Each has independent controls and autosave.
Change source, brightness, contrast, saturation, gamma, crop, scale, rotation,
mirrors, dimensions, resampling, palette, BRIGHT policy and dithering. Settings
are shared across ALL frames in that family. Choose a decision and add notes.
Presets include the earlier arcade RPC settings and the gold/steel conversion.
Use manual crop with automatic trimming off. Custom image sheets are optional.

The source menu labels original arcade poses, authored intermediates, the
prior AI-assisted walker, and current installed art separately. Snake sources
are10captured orientations; the connected preview uses12arcade joint positions.
Spacing and overlap-colour diagnostics are previews, not a gameplay simulator.
The current-family pane does not imply matching arcade/Spectrum frame numbers.

CHECKS
Normal black is mandatory for transparent space; bright-black and FLASH are
excluded. Every converted cell uses at most2colours per8x1. Optional horizontal
coherence holds a black/ink pair until a gap of at least8source pixels; all8
horizontal alignments are checked. Shared-cell sprite overlaps can still clash;
inspect the connected preview and validate integration separately.

EXPORT
Export choices: settings/notes/decisions for BOTH families as JSON; import it
to resume or send it back for game integration. Custom source pixels are included
when needed. Autosave is browser-local; JSON is the portable saved copy.
Export frame PNG: current converted frame, original pixel size with transparency.
Export both asset packs: ZIP with frames and sheets as PNG, .bits.bin and
.attrs.bin row-major planes, .preserve.bin (1bitpreservesbackground), and
.pairs.bin column-major bitmap/attribute row pairs. choices.json records exact
settings, sources and frame dimensions. The ZIP is artwork, not a game image.

ENGINE / LICENCE
CPU adjustment, pair-selection and diffusion functions are derived from the
local Retro Pixel Converter snapshot, GPL-3.0. Sierra Lite and Floyd-Steinberg
use its diffusion implementation; nearest-pair and Bayer4are adapters. Alpha
protection, palette restrictions, no-bright-black and optional coherent palettes
are explicit local adaptations. See provenance.json and RPC_LICENSE.txt.
Corresponding UI/build sources are included under source/; worker.js contains
the extracted RPC functions. Original arcade ROM archives are not included.

VALIDATION
32engine combinations/palette restrictions; file://Chrome tests; all4dithers;
independent shared-family state; cropping/scaling/mirroring/rotation; custom
sheet; autosave and JSONroundtrip; realPNG/ZIPdownloads;14exported frames with
CRC/native-byte-layout/PNG-mask checks; mobilelayout; no browserpageerrors.
These are editor tests, not gameplay or hardware performance measurements.
'''
(O/'README.txt').write_text(readme,encoding='ascii')
manifest=dict(passed=True,date='2026-11-09',htmlSHA256=htmlsha,workerSHA256=workerhash,engine=json.loads((O/'engine_validation.json').read_text()),browser=json.loads((O/'browser_validation.json').read_text()),extraBrowser=json.loads((O/'extra_browser_validation.json').read_text()),export=report,gameFilesUnchanged=True)
(O/'validation_summary.json').write_text(json.dumps(manifest,indent=2))
zpath=O/'RType_L1_Art_Converter.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as out:
 for name in ['index.html','worker.js','data.json','RPC_LICENSE.txt','provenance.json','README.txt','validation_summary.json']:out.write(O/name,name)
 for name in ['src/l1_art_converter.html','src/l1_art_converter.css','src/l1_art_converter.js','scripts/build_l1_art_converter.py','scripts/verify_l1_art_converter_core.mjs','scripts/verify_l1_art_converter_browser.mjs','scripts/verify_l1_art_converter_extra.mjs']:out.write(R/name,'source/'+name)
with zipfile.ZipFile(zpath)as out:assert out.testzip()is None
print('Tool bundle:',zpath);print(hashlib.sha256(zpath.read_bytes()).hexdigest(),zpath.stat().st_size)
