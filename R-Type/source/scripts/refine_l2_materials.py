from pathlib import Path
p=Path('scripts/preview_l2_organic_sierra.py');s=p.read_text();s=s.replace('rgba=np.dstack', '''poly=Image.new('1',source.size);ImageDraw.Draw(poly).polygon([(112,96),(156,96),(170,114),(208,114),(232,96),(270,96),(268,156),(264,184),(309,183),(326,207),(302,234),(270,240),(109,240),(74,233),(60,216),(62,195),(95,183),(123,187),(125,155)],fill=1);warm&=np.array(poly,dtype=bool)
rgba=np.dstack''')
s=s.replace("hsv=np.array(canvas.convert('RGB').convert('HSV'));hsv[:,:,1]=np.minimum(hsv[:,:,1].astype(float)*sat,255).astype('uint8');rgb=", "src=np.array(canvas)[:,:,:3].astype(float);flesh=(src[:,:,2]>.78*src[:,:,1])&(src[:,:,0]>=src[:,:,1])&mask;hsv=np.array(canvas.convert('RGB').convert('HSV'));mult=np.where(flesh,1.1,sat);hsv[:,:,1]=np.minimum(hsv[:,:,1].astype(float)*mult,255).astype('uint8');rgb=")
s=s.replace("if visible.all() and np.mean(cell@np.array([.21,.72,.07]))>90:candidates=[v for v in candidates if v[0]!=0]", """if vector:
    is_flesh=np.count_nonzero(flesh[y,x:x+8]&visible)>max(0,np.count_nonzero(visible)//2)
    if is_flesh:
     candidates=[v for v in candidates if v in [(0,2),(0,7),(2,7)]]
    else:candidates=[v for v in candidates if v in [(0,6),(0,7),(6,7)]]
   if visible.all() and np.mean(cell@np.array([.21,.72,.07]))>90:candidates=[v for v in candidates if v[0]!=0]""")
s=s.replace("'Deep shaded'","'Deep material shading'").replace("'Bright organic'","'Pink flesh / bronze ribs'").replace("'RPC-style high gamma'","'Bright material shading'").replace("'Coverage Sierra Lite'","'Coverage / unrestricted palette'")
s=s.replace("'status':'offline asset preview", "'material_policy':'pink tissue hue protected, red-white flesh pairs; yellow-white/dark rib pairs; zero palette at holes', 'status':'offline asset preview")
p.write_text(s)
