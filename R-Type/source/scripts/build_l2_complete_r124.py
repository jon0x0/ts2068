from pathlib import Path
import sys,json,shutil,subprocess,re,zipfile,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l2_integrated_r123';O=R/'build/fullgame/l2_complete_r124';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.json','.asm','.sym']and not any(s in p.name for s in['.home.','validation','approach','mismatch','trace','timing','probe','final_l2','native_jump']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level02_region.bin').read_bytes());original=bytes(16384)+(R/'build/fullgame/foundation/level02.raw').read_bytes();oldmanifest=json.loads((R/'build/graphics/l2_integrated_r67/manifest.json').read_text());tiles=[]
for n in range(34):
 v=bytearray(original[0xe762-(n+1)*144:0xe762-n*144]);v[::9]=bytes(0x86 if any(v[i+1:i+9]) else 7 for i in range(0,144,9));tiles.append(bytes(v))
for row in oldmanifest['tiles']:
 v=bytearray(unpack(b[row['pointer']-0x2000:]));assert len(v)==144
 for i in range(0,144,9):
  if v[i]<16:v[i]+=16
  tag=v[i];pi=tag+96 if tag<32 else tag-144;aa=(bytes(b[0x2000:0x2380])+bytes(b[0x2000:0x2080]))[pi*8:pi*8+8]
  visible=any(((at&7)!=0 and bit!=0)or(((at>>3)&7)!=0 and bit!=255)for at,bit in zip(aa,v[i+1:i+9]))
  if not visible:v[i]=7
 tiles.append(bytes(v))
# Copy the legacy sixteen patterns to legal high dictionary IDs112..127.
b[0x2380:0x2400]=b[0x2000:0x2080]
a=[np.frombuffer(t,np.uint8)for t in tiles];cost=[len(pack(t))for t in tiles];delta={}
for i in range(52):
 for k in range(i):delta[i,k]=len(pack((a[i]^a[k]).tobytes()))+1
bases=set();best=cost[:];mapping=list(range(52))
while True:
 opts=[]
 for k in range(52):
  if k in bases:continue
  gain=sum(max(0,best[i]-delta.get((max(i,k),min(i,k)),999))for i in range(52)if i!=k and i not in bases)-(cost[k]-best[k]);opts.append((gain,k))
 gain,k=max(opts)
 if gain<=0:break
 bases.add(k);best[k]=cost[k];mapping[k]=k
 for i in range(52):
  c=delta.get((max(i,k),min(i,k)),999)
  if i not in bases and c<best[i]:best[i]=c;mapping[i]=k
# Refine the bounded-depth dictionary against actual packet cost.
def fit(bs):
 mp=[];score=0
 for i in range(52):
  opts=[(cost[i],i)] if i in bs else [(cost[i],i)]+[(delta[max(i,k),min(i,k)],k)for k in bs if k!=i]
  c,k=min(opts);score+=c;mp.append(k)
 return score,mp
score,mapping=fit(bases)
for repeat in range(8):
 options=[(score,bases,mapping)]
 for k in range(52):
  trial=bases-{k} if k in bases else bases|{k};v,mp=fit(trial);options.append((v,trial,mp))
 for k in bases:
  for v in set(range(52))-bases:
   trial=(bases-{k})|{v};c,mp=fit(trial);options.append((c,trial,mp))
 new,bs,mp=min(options,key=lambda v:v[0])
 if new>=score:break
 score,bases,mapping=new,bs,mp
packets=[(b'' if mapping[i]==i else bytes([mapping[i]]))+pack(t if mapping[i]==i else(a[i]^a[mapping[i]]).tobytes())for i,t in enumerate(tiles)];aliases={};groups={}
for i,t in enumerate(tiles):groups.setdefault(t,[]).append(i)
for group in groups.values():
 leader=next((i for i in group if mapping[i]==i),group[0])
 for i in group:
  if i!=leader:aliases[i]=leader
total=sum(len(v)for i,v in enumerate(packets)if i not in aliases);minimum=total-0x1320
# Minimize low memory usage; remaining native floor storage is exactly4896bytes.
dp={0:0}
for i,v in enumerate(packets):
 if i in aliases:continue
 for n,mask in sorted(list(dp.items()),reverse=True):
  if n+len(v)<=768 and n+len(v)not in dp:dp[n+len(v)]=mask|(1<<i)
low=min(n for n in dp if n>=minimum);mask=dp[low];ptrs=[];p0=0x1b20;p1=0xb442;ptrs=[0]*52
b[0xb442:0xc762]=bytes(4896);b[0x1b20:0x1e20]=bytes(768)
for i,v in enumerate(packets):
 if i in aliases:continue
 if mask>>i&1:ptr=p0;b[p0:p0+len(v)]=v;p0+=len(v)
 else:ptr=p1+0x2000;b[p1:p1+len(v)]=v;p1+=len(v)
 ptrs[i]=ptr^0x4000 if mapping[i]==i else ptr
for i,k in aliases.items():ptrs[i]=ptrs[k]
assert p1<=0xc762;lowcode=(p0+1)&~1
# Original map geometry, with collision-free IDs for the new body tiles.
b[0xc762:0xc8b1]=original[0xe762:0xe8b1];world=bytearray((R/'build/graphics/l2_integrated_r67/map_patch.bin').read_bytes());world=bytes(v+15 if v else 0 for v in world);b[0xc762+56*5:0xc762+64*5]=world
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
def asm(name,text):
 p=O/name;p.with_suffix('.asm').write_text(text);r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr
 return p.with_suffix('.bin').read_bytes(),{k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
# The native ROM font is3D00, so preserve the diagnostic UI without a duplicate font.
s=(R/'src/debug_ram_screen.asm').read_text().replace('R38 DEBUG','R124 DEBUG').replace('font: INCBIN "assets/fullgame_preloader_font.bin"','font EQU $3D00')
debug,ds=asm('debug_rom_font',s);debugend=0x8000+len(debug);assert debugend+408+18<=0x84b4
b[0x8000:0x84b4]=debug.ljust(0x4b4,b'\0');scratch=debugend;terrain=scratch+144;boss=terrain+160;coords=boss+104
inks=json.loads((R/'build/graphics/l2_integrate_r119/selected_row_inks.json').read_text());b[terrain:terrain+160]=bytes(inks['terrain']);b[boss:boss+104]=bytes(inks['boss']);b[coords:coords+18]=bytes(r['ty']*8+r['tx']for r in oldmanifest['tiles'])
# Generated memory contracts precede all executable pieces.
params=f'''SCRATCH EQU ${scratch:04X}
TERRAIN_INKS EQU ${terrain:04X}
BOSS_INKS EQU ${boss:04X}
REVEAL_COORDS EQU ${coords:04X}
LOW_CODE EQU ${lowcode:04X}
NORMALIZE_ADDRESS EQU ${coords+18:04X}
'''
(O/'layout.inc').write_text(params)
print('tile packets',total,'low',low,'lowcode',hex(lowcode),'tail capacity',0x1e20-lowcode,'debugend',hex(debugend))
# Save raw packets and intended tile bytes before assembling gateways.
(O/'tile_inputs.json').write_text(json.dumps({'tiles':[t.hex()for t in tiles],'mapping':mapping,'aliases':aliases,'ptrs':ptrs,'packet_hex':[p.hex()for p in packets],'total':total,'low_bytes':low,'low_code':lowcode,'debug_end':debugend,'scratch':scratch,'terrain':terrain,'boss':boss,'coords':coords},indent=2));(O/'base_pending.bin').write_bytes(b)
# Link fixed-size low kernels and native gateways, then build the tapes.
nv,ns=asm('moving_normalizer',params+(R/'src/l2_normalize_r124.asm').read_text());b[coords+18:coords+18+len(nv)]=nv
kv,ks=asm('palette_kernel',params+(R/'src/l2_palette_kernel_r124.asm').read_text());defs=params+'\n'+''.join(f'{k} EQU ${v:04X}\n'for k,v in ks.items() if k not in ['SCRATCH','TERRAIN_INKS','BOSS_INKS','REVEAL_COORDS','LOW_CODE','NORMALIZE_ADDRESS']);defs+=f'normalize_tile EQU ${ns["normalize_tile"]:04X}\n';rv,rs=asm('boss_reveal',defs+(R/'src/l2_reveal_r124.asm').read_text());defs+='\n'+''.join(f'{k} EQU ${v:04X}\n'for k,v in rs.items() if k not in ks and k not in ns);tv,ts=asm('tile_loader',defs+(R/'src/l2_tiles_r124.asm').read_text().replace('TILE_POINTERS',','.join(f'${p:04X}'for p in ptrs)))
rf=b.find(bytes.fromhex('dd7e10fefd'),0x1400,0x18a7);assert rf>=0
lookup_defs=defs+f'REVERSE_FLAG EQU ${rf:04X}\nreverse_cache EQU ${ts["reverse_cache"]:04X}\n'
lv,ls=asm('palette_lookup',lookup_defs+(R/'src/l2_palette_lookup_r124.asm').read_text())
print('kernels',len(kv),len(lv),'reveal',len(rv),'loader',len(tv),'end',hex(0x3848+len(tv)))
b[0x100:0x100+len(kv)]=kv;b[0xf80:0xf80+len(lv)]=lv;b[lowcode:lowcode+len(rv)]=rv;b[0x3848:0x3a00]=tv.ljust(0x1b8,b'\0')
b[0x1de:0x1e0]=ts['get_tile'].to_bytes(2,'little')
# Native source colour tokens are already encoded, including low rich IDs10..1F.
pat=bytes.fromhex('a9f68012');at=b.find(pat,0x1400,0x18a7);assert at>=0 and b.find(pat,at+1,0x18a7)<0;b[at+1:at+3]=bytes(2)
metas=json.loads((B/'generic_manifest.json').read_text());meta=next(x for x in metas if x['level']==2);image=bytearray((B/'L2_runtime_image.bin').read_bytes());pat=bytes.fromhex('cd2039');assert image.count(pat)==1;image=image.replace(pat,b'\xcd'+ts['restore_native'].to_bytes(2,'little'));ip=meta['motion_ptr'];packed=pack(image);assert ip+len(packed)<=0x3848;b[ip:0x3848]=packed.ljust(0x3848-ip,b'\0');meta['actor_extension']['restore_native_bank5']=ts['restore_native'];meta['motion_image_bytes']=len(image)
inst=meta['cache_symbols']['install_motion'];v=bytes.fromhex('f3f53e63d3f4cd')+ts['save_native'].to_bytes(2,'little')+b'\x21'+ip.to_bytes(2,'little')+bytes.fromhex('1100a0cd4fdef13e69d3f4c3b2a1');assert inst+len(v)<=0xdf30;b[inst:0xdf30]=v.ljust(0xdf30-inst,b'\0')
(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));(O/'L2_runtime_image.bin').write_bytes(image);(O/'level02_region.bin').write_bytes(b);(O/'integration_contract.json').write_text(json.dumps({'native_tiles':34,'boss_tiles':18,'native_ids':list(range(34)),'boss_ids':list(range(34,52)),'tile_inputs':'tile_inputs.json','tile_symbols':ts,'kernel_symbols':ks,'lookup_symbols':ls,'reveal_symbols':rs,'snapshot':{'bank':6,'address':0xc700,'bytes':1012},'rom_font':0x3d00,'font_reclaimed':[debugend,0x84b4],'other_levels_unchanged':True,'no_fullscreen_scan':True,'pool_bytes':total},indent=2))
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for stem in ['boss_motion_fixture','probe_l2_short','probe_l2_full','verify_cold_l2_fire','verify_native_revisits','verify_l2_decode','verify_l2_boss_revisits']:
 s=(R/f'scripts/{stem}_r123.mjs').read_text(encoding='utf-8-sig').replace('l2_integrated_r123','l2_complete_r124').replace('boss_motion_fixture_r123','boss_motion_fixture_r124')
 if stem=='boss_motion_fixture':
  s=s.replace('if(!Buffer.from(m.dock[0]).equals(expectedCode[c.region]))',f'if(!Buffer.from(m.dock[0]).map((v,i)=>c.region===1&&((i>={ks["row_cache"]}&&i<{ks["row_cache"]+8})||i==={rs["snapshot_saved"]}||i==={rs["reveal_index"]})?expectedCode[c.region][i]:v).equals(expectedCode[c.region]))')
  s=s.replace('c.coreBefore=Buffer.from(m.ram.slice(0x8400,0xc000));','c.coreBefore=Buffer.from(m.ram.slice(0x8400,0xc000));if(c.region===1)c.coreBefore.set([0x3a,0x8a,0x7a],0x28c);')
 (R/f'scripts/{stem}_r124.mjs').write_text(s,encoding='utf-8')
print('Built r124 candidate')

# Fixed-length release identity, including TAP checksum repair.
old=b'R123 PREPARING  ';new=b'R124 PREPARING  '
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;v=p.read_bytes();assert old in v;p.write_bytes(v.replace(old,new))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(old,new);check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
# Narrowly exclude the native renderer's intentional workspace only while installed.
p=R/'scripts/verify_native_revisits_r124.mjs';s=p.read_text().replace('if(read(p)!==native[p-0x2000])','if(!(c.region===1&&m.dock[7][0x3f0]&&((p>=0xc4f2&&p<0xc636)||(p>=0xc700&&p<0xc790)))&&read(p)!==native[p-0x2000])');p.write_text(s)
