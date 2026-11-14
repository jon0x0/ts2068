from pathlib import Path
p=Path('scripts/preview_l2_organic_sierra.py');s=p.read_text();s=s.replace("'saturation':sat,'diffusion'", "'saturation':sat,'flesh_saturation':1.1,'material_pairs':bool(vector),'diffusion'")
s=s.replace('<h2>Arcade reference</h2>', '<p>A–C protect the pink tissue hue and separate flesh/rib palette choices. Their saturation setting applies to ribs; flesh uses1.1×. D is the unrestricted-palette coverage comparison. Source masking uses warm colours plus a coarse silhouette guide; the enlarged isolated source is included so any lost contour can be identified.</p><h2>Your RPC reference</h2><img width="691" src="rpc_reference.png"><h2>Arcade reference</h2>')
p.write_text(s)
import shutil
src=Path('C:/Users/Jon/AppData/Local/Temp/codex-clipboard-d2a758cc-b758-4be9-993d-2f67ba02d069.png');shutil.copy2(src,Path('build/graphics/l2_organic_sierra/rpc_reference.png'))
