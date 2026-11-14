from pathlib import Path
import json,base64
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l7_walker_variant';O.mkdir(exist_ok=True);d=json.loads((R/'build/graphics/l7_walker_converter/data.json').read_text());src=d['walker']['sources'][0];cool=json.loads(json.dumps(src));cool['id']='cool';cool['label']='Blue/cyan armour variant - shared selected settings';cool['provenance']='Same three arcade poses, metal tones remapped toward dark blue/cyan before the RPC pass. Original selected variant remains separately available.'
for f in cool['frames']:
 im=Image.frombytes('RGBA',(f['w'],f['h']),base64.b64decode(f['rgba']));px=im.load()
 for y in range(im.height):
  for x in range(im.width):
   r,g,b,a=px[x,y]
   if a and max(r,g,b)-min(r,g,b)<22 and r>35:px[x,y]=(0,g,min(255,b+25),a)if r>=150 else(0,g//3,b,a)
 f['rgba']=base64.b64encode(im.tobytes()).decode();f['label']+=' - cool armour proposal'
d['walker']['sources'].insert(1,cool);d['references']['walker']='data:image/png;base64,'+base64.b64encode((R/'build/graphics/l7_wall_assembled/assembly_and_walker_comparison.png').read_bytes()).decode();(O/'data.json').write_text(json.dumps(d))
app=(R/'src/l7_walker_converter.js').read_text().replace('rtype-l7-walker','rtype-l7-walker-variant').replace('contrast:65,saturation:78,gamma:1.13','contrast:88,saturation:78,gamma:1.29');html=(R/'src/l7_walker_converter.html').read_text();a=html.index('<details open class="source-gallery">');z=html.index('<main>',a);html=html[:a]+'<details open class="source-gallery"><summary>Chosen walker and blue/cyan proposal</summary><p>Original arcade source uses your selected settings49/88/78/1.29 at24x24. Choose the blue/cyan source to compare a distinct material variant; settings stay shared across all three poses.</p><img style="max-width:100%;image-rendering:pixelated" src="'+d['references']['walker']+'"></details>'+html[z:];worker=(R/'build/graphics/l1_art_converter/worker.js').read_text();prov=json.loads((R/'build/graphics/l1_art_converter/provenance.json').read_text());html=html.replace('/*STYLE*/',(R/'src/l1_art_converter.css').read_text()).replace('/*DATA*/',json.dumps(d).replace('<','\\u003c')).replace('/*WORKER*/',json.dumps(worker).replace('<','\\u003c')).replace('/*PROVENANCE*/',json.dumps(prov)).replace('/*APP*/',app);(O/'index.html').write_text(html,encoding='utf-8')
