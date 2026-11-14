"""Complete Bellmite preview, preserving captured draw order and selected core."""
import json
import numpy as np
from PIL import Image,ImageDraw
from preview_bellmite_detail import ROOT,legal
from preview_enemy_sierra import decode
OUT=ROOT/'build/graphics/bellmite_complete_preview'

def main():
    OUT.mkdir(parents=True,exist_ok=True);capture=ROOT/'build/fullgame/bellmite_orbs_r44'
    manifest=json.loads((capture/'manifest.json').read_text());info=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][4]
    native=(capture/'native_level5.bin').read_bytes();table=info['enemy_descriptors_start']+7*4
    descriptor=dict(width=native[table],height=native[table+1],pointer=int.from_bytes(native[table+2:table+4],'little'))
    core,_=decode(descriptor,native[0xc4ce:],(capture/'enemy_palette.bin').read_bytes())
    original=Image.open(ROOT/'build/fullgame/converted/level05/descriptor008_arcade.png').convert('RGBA').resize(core.size,Image.Resampling.LANCZOS)
    alpha=original.getchannel('A').point(lambda a:255 if a>=96 else 0);core=core.convert('RGBA');core.putalpha(alpha);core.save(OUT/'selected_core.png')
    spheres=[Image.open(ROOT/f'build/graphics/bellmite_blue_rim_feedback/H_sphere{i}.png').convert('RGBA')for i in range(3)]
    commands=json.loads((capture/'sample_200.commands.json').read_text());images=[]
    for cutaway in [False,True]:
        canvas=Image.new('RGBA',(256,160))
        for command in reversed(commands):
            pointer=command['pointer'];is_core=pointer==0xefa1
            if is_core:cel=core
            elif pointer in[0xf3f1,0xf481,0xf511]:cel=spheres[[0xf3f1,0xf481,0xf511].index(pointer)]
            else:continue
            x=command['x']*8;y=(command['y']if command['y']<128 else command['y']-256)*8
            # Explicit illustrative opening, not a captured damage state.
            if cutaway and not is_core and 145<x+16<225 and 38<y+16<122:continue
            if command['entry']in[0x8dd3,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            if command['entry']in[0x8d65,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            canvas.alpha_composite(cel,(x,y))
        a=np.asarray(canvas);image=legal(a[:,:,:3],a[:,:,3]>0);image.save(OUT/('cutaway.png'if cutaway else'combined.png'));images.append(image)
    sheet=Image.new('RGB',(1024,350),(12,12,12));draw=ImageDraw.Draw(sheet)
    for i,(label,image)in enumerate(zip(['Combined: captured positions and layer order','Illustrative cutaway: selected front spheres hidden'],images)):
        draw.text((i*512+6,7),label,fill='white');sheet.paste(image.resize((512,320),Image.Resampling.NEAREST),(i*512,28))
    sheet.save(OUT/'comparison.png')
    (OUT/'index.html').write_text('<meta charset="utf-8"><title>Bellmite spheres and mechanical core</title><style>body{background:#151515;color:white;font:17px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>Planned-edge spheres with the selected mechanical core</h1><p>Offline composition preview using the captured positions and draw priority. The left view retains all spheres; the right deliberately hides selected front spheres to expose the 96×96 core. The cutaway is illustrative, not a captured damage state. Final pixels obey legal 8×1 pairs; this is not a new game build.</p><img src="comparison.png"><h2>Selected core by itself</h2><img width="384" src="selected_core.png">',encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps(dict(status='Offline combined preview; right view is illustrative cutaway',sphere_style='H approved planned edge',core='Actual packed r44 selected96x96 descriptor8',native_update=200,native_runtime_changed=False),indent=2));print(OUT/'comparison.png')
if __name__=='__main__':main()
