from pathlib import Path
import json,sys,hashlib
from PIL import Image
r=Path(r'D:/T7_Recover/Jon/Personal/Timex/cartridgeconversion/R-Type');sys.path.insert(0,str(r/'scripts'));from build_graphics import unpack,screen_offset
o=r/'build/diagnostics/title_screen_r20';o.mkdir(parents=True,exist_ok=True);results=[]
for folder,name in [('ecm_native','sram'),('readonly_ecm','rom')]:
 base=r/'build'/folder/'probe_1_title_screen_r20';b=base.with_suffix('.bin').read_bytes();meta=json.loads(base.with_suffix('.json').read_text());assert meta['video_mode']==2
 outside=[screen_offset(y)+x for y in range(192)if not 96<=y<144 for x in range(32)]
 row=dict(target=name,bin_sha256=meta['cartridge_sha256'],outside_pixels=sum(b[i]!=0 for i in outside),outside_bad_colours=sum(b[8192+i]!=0x47 for i in outside),video_mode=2)
 assert row['outside_pixels']==row['outside_bad_colours']==0;row['passed']=True;results.append(row)
 unpack(b[:6144],b[8192:14336]).resize((768,576),Image.Resampling.NEAREST).save(o/f'fuse_{name}_mid_sweep.png')
(o/'fuse_validation.json').write_text(json.dumps(results,indent=2))
motion=r/'build/diagnostics/title_motion_r20';meta=json.loads((motion/'validation.json').read_text());frames=[];dur=[]
for i,t in enumerate(meta[0]['timings']):
 b=(motion/f'sram_frame{i}.bin').read_bytes();frames.append(unpack(b[0x4000:0x5800],b[0x6000:0x7800]).resize((768,576),Image.Resampling.NEAREST));dur.append(max(20,round((meta[0]['timings'][min(i+1,45)]['tstates']-t['tstates'])/35280)*10))
dur[-1]=1500;frames[0].save(o/'full_screen_motion.gif',save_all=True,append_images=frames[1:],duration=dur,loop=0)
print('Full-screen Fuse verification and animation preview saved')
