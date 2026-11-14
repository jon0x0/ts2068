from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path.cwd();O=R/'build/graphics/full_plume_r104';O.mkdir(exist_ok=True);profiles=[]
for k in range(4):
 # r103's first40columns are photo-derived; its last8columns were wrongly retained legacy exhaust.
 im=Image.open(R/f'build/graphics/plume_diameter_r103/L3_exhaust_{k}_source.png').convert('RGBA').crop((0,0,40,16)).resize((48,16),Image.Resampling.LANCZOS);a=np.array(im);name=f'L3_exhaust_{k}';im.save(O/f'{name}_source.png');mask=(a[:,:,3]>=112)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;(O/f'{name}.rgb').write_bytes(rgb.tobytes());(O/f'{name}.mask').write_bytes(mask.astype('uint8').tobytes());profiles.append(dict(id=name,size=name,w=48,h=16,bright=True,strategy='segment-coverage',settings=dict(brightness=56,contrast=54,saturation=78,gamma=1.65)))
(O/'inputs.json').write_text(json.dumps(dict(profiles=profiles),indent=2));s=(R/'scripts/convert_walkers_rpc_r85.mjs').read_text().replace('build/graphics/walker_review_r85','build/graphics/full_plume_r104');(R/'scripts/convert_full_plume_r104.mjs').write_text(s)
s=(R/'scripts/build_plume_diameter_r103.py').read_text().replace("B=R/'build/fullgame/photo_exhaust_r102';O=R/'build/fullgame/plume_diameter_r103'","B=R/'build/fullgame/plume_diameter_r103';O=R/'build/fullgame/full_plume_r104'").replace("p=R/'build/graphics/plume_diameter_r103'","p=R/'build/graphics/full_plume_r104'")
s=s.replace('v[160:192]=raw[off+160:off+192];','').replace('v[4*32+y*2:4*32+y*2+2]','v[5*32+y*2:5*32+y*2+2]').replace('nozzle_bytes_unchanged=True','full_plume_replaced=True').replace("old=b'R102 PREPARING  ';new=b'R103 PREPARING  '","old=b'R103 PREPARING  ';new=b'R104 PREPARING  '")
a=s.index("for stem in ['boss_motion_fixture'");s=s[:a]+'''for stem in ['boss_motion_fixture','verify_photo_exhaust_state','verify_native_revisits','verify_cold_fire']:
 p=R/f'scripts/{stem}_r103.mjs';s=p.read_text().replace('plume_diameter_r103','full_plume_r104').replace('boss_motion_fixture_r103','boss_motion_fixture_r104');(R/f'scripts/{stem}_r104.mjs').write_text(s)
print('Complete48x16photo-derived plume; old checkered exhaust removed. Payload end',hex(end))
'''
(R/'scripts/build_full_plume_r104.py').write_text(s)
