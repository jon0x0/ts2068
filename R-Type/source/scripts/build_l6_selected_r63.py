from pathlib import Path
import sys,shutil,json,re
import numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
from boss_motion_assets_r60 import decode as native_decode,phases
BASE=R/'build/fullgame/force_loading_r62';OUT=R/'build/fullgame/l6_selected_r63'
# Approved red+lower-magenta option; normal black only.
ART={9:R/'build/graphics/l6_ordered_machinery/head_darker_0.npy',10:R/'build/graphics/l6_ordered_machinery/head_darker_1.npy',11:R/'build/graphics/l6_ordered_machinery/head_darker_2.npy',12:R/'build/graphics/l6_ordered_machinery/head_darker_3.npy',13:R/'build/graphics/l6_ordered_machinery/head_darker_1.npy'}
for ident,state in [(140,2),(141,1),(142,0),(143,8),(144,6),(145,5)]:ART[ident]=R/f'build/graphics/l6_light_fill/magenta_{state}.npy'
def selected(n,i):return (np.load(ART[i]),0,0) if i in ART else native_decode(n,i)
def minor_phases(im):
 raw=phases(im)
 # Unshifted, X-locked minor sprites never read the extra blank right column.
 return [raw[0][:-im.shape[0]*2]]*4
DISPATCH='''        ; Preserve native animation/AI IDs; alias only the rendering lookup.
        LD A,(MAIN_ID)
        CP 9
        JR C,minor_alias_done
        CP 14
        JR NC,turret_geometry
        LD HL,MAIN_BC+1
        DEC (HL)
        JR minor_alias_done
turret_geometry:
        CP 18
        JR NC,boss_alias
        SUB 15
        JR NC,turret_pose
        XOR A
turret_pose:
        ADD A,140
        LD D,A
        LD A,(IY+8)
        AND 1
        LD A,D
        JR Z,minor_alias_store
        ADD A,3
        JR minor_alias_store
boss_alias:
        CP 26
        JR NC,minor_alias_done
        CP 20
        JR Z,boss_alt
        CP 23
        JR Z,boss_alt
        LD A,18
        JR minor_alias_store
boss_alt:
        LD A,20
minor_alias_store:
        LD (MAIN_ID),A
minor_alias_done:
'''
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 shutil.copytree(BASE/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 for p in BASE.iterdir():
  if p.is_file() and (p.suffix in ['.asm','.sym','.bin'] or p.name in ['global_tags.json','native_compatibility.json']):shutil.copy2(p,OUT/p.name)
 s=(R/'scripts/build_boss_motion_r60.py').read_text();s=s[:s.index(' # L5 retains')]+" (OUT/'generic_manifest.json').write_text(json.dumps(records,indent=2))\n"
 s=s.replace(' l5.OUT=OUT;l5.main();records=[];compat=[]',' records=[];compat=[]')
 s=s.replace("im=np.load(ART_OVERRIDES.get(ident,ROOT/f'build/graphics/enemy_upgrades_r60/{ident}.npy'))if n==1 else decode(n,ident)[0];h,w=im.shape;raws=phases(im);ptrs=[]", "im=decode(n,ident)[0];h,w=im.shape;raws=minor_phases(im) if ident in ART else phases(im);ptrs=[]")
 s=s.replace("sprite['id'],w//8,h//8", "sprite['id'],(w//8)|(128 if sprite['id'] in ART else 0),h//8")
 s=s.replace('assert len(table)<=0x80','assert len(table)<=0xA0')
 s=s.replace('  start=PLANS[n];', '  assert preloaded\n  combined=b"".join(raw_assets.values());payload=bytearray(pack(combined));addresses={};raw_assets={0x2400:combined};raw_ptrs={0x2400:0xc000}\n  start=PLANS[n];')
 s=s.replace('assert motion_ptr+len(image)<= (0x3000 if n==1 else 0x3fe0)', 'assert motion_ptr+len(image)<=0x3a00')

 s=s.replace("(ROOT/'src/boss_phase_motion_r60.asm').read_text()", "(ROOT/'src/boss_phase_motion_r60.asm').read_text().replace('        PUSH IY\\n','        PUSH IY\\n'+DISPATCH,1)")
 # Compile definitions but do not run its original main or overwrite prior release.
 ns={'__file__':str(R/'scripts/build_boss_motion_r60.py'),'__name__':'r63_builder'};exec(compile(s,'r63_generic_builder','exec'),ns)
 ns.update(OUT=OUT,SELECT={6:[9,10,11,12,13,140,141,142,143,144,145,18,20]},decode=selected,minor_phases=minor_phases,ART=ART,DISPATCH=DISPATCH)
 ns['main']()
 # Preserve r62 native-compatibility and preload changes; replace only L6 renderer/asset products.
 b=bytearray((OUT/'level06_region.bin').read_bytes());old=(BASE/'level06_region.bin').read_bytes()
 for lo,hi in [(0xd4,0xf7),(0xdb,0xf7),(0x3a00,0x3fe0),(0xfb98,0xfb9b),(0xaab,0xaad)]:b[lo:hi]=old[lo:hi]
 for at in [0x4abc,0x4c2f,0x5286,0x52e4,0x538f,0xa059,0xa496]:b[at:at+3]=old[at:at+3]
 (OUT/'level06_region.bin').write_bytes(b)
 from build_rocket_fix import code
 (OUT/'RTYPE/LEVEL06.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k) for k in range(8)))
 (OUT/'RTYPE/START06.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[page*8192+sub*1024:page*8192+(sub+1)*1024],k)for k,(page,sub)in enumerate((p,s)for p in [0,1,4,5,6,7]for s in range(8))))
 (OUT/'selected_art.json').write_text(json.dumps({'head_ids':{str(i):str(p.relative_to(R))for i,p in ART.items() if i<14},'turret_ids':{str(i):str(p.relative_to(R))for i,p in ART.items() if i>=140},'native_turret_mapping':{'14':140,'15':140,'16':141,'17':142},'on_offset':3,'light_clock':'native actor animation-cycle counter IY+8 bit0; instant ON' ,'native_ai_unchanged':True,'scope':'expanded disk'},indent=2))
if __name__=='__main__':main()
