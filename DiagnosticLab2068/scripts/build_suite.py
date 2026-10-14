"""Build v0.2 ROM suite with immutable compressed assets and stackless code."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
from PIL import Image
from build_v01 import ram_source as baseline_ram
from generate_design_assets import standard_render
from prototype_degraded_display import attribute_page,FONT
from suite_assets import pack,pages
from release_info import VERSION
FONT={**FONT,'4':['101','101','111','001','001'],'5':['111','100','110','001','110']}
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'build'
DEFAULT_ASSEMBLER=ROOT.parent/'cartridgeconversion/sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'

def extended_ram():
    src,phases=baseline_ram();src=src.replace(' jp tests_done',' jp extended_start')
    # IY is reset at each comparison entry; keyboard polls use ROM callbacks.
    src=re.sub(r' ld iy,(\w+)\n(\w+):\n',r'\2:\n ld iy,\1\n',src)
    i=0
    def insert(m):
        nonlocal i
        i+=1
        return m[0]+f' ld a,l\n or a\n jp nz,ram_poll_done_{i}\n ld iy,ram_poll_done_{i}\n jp ram_key_poll\nram_poll_done_{i}:\n'
    src=re.sub(r' inc hl\n| dec hl\n',insert,src)
    # Startup choice8 stops after the two full00/FF fill/read passes.
    # Insert at the fixed phase boundary; manual choices keep full coverage.
    marker=' ld a,3\n ld i,a\n'
    assert src.count(marker)==1
    src=src.replace(marker," ex af,af'\n ld b,a\n ex af,af'\n ld a,b\n cp 8\n jp z,tests_done\n"+marker)
    for phase in range(1,31):
        color=1 if phase<=8 else 5 if phase<=24 else 6
        src=re.sub(r'( ld a,'+str(phase)+r'\n ld i,a\n ld d,\$[0-9a-f]+\n) ld a,6\n',r'\g<1> ld a,'+str(color)+'\n',src)
    return src,phases

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--assembler',type=Path,default=DEFAULT_ASSEMBLER);args=ap.parse_args();BUILD.mkdir(exist_ok=True)
    rom=(ROOT.parent/'David Anderson/TS2068-Ref-Library/2068 ROMS/TS2068_U16.BIN').read_bytes()
    assert hashlib.sha1(rom).hexdigest()=='1446cb2780a9dedf640404a639fa3ae518b2d8aa'
    font=rom[0x3d00:0x4000];screens,coords=pages(font)
    for name,data in screens.items(): (BUILD/('suite-'+name+'.bin')).write_bytes(data)
    flat=bytearray([255]*65536);flat[0x2200:0x2500]=font
    cursors={2:0x4800,1:0x2500,3:0x6000,4:0x8e00,5:0xa000,6:0xc000,7:0xe600};lines=[];assets=[]
    ay_steps=[]
    def ay_step(name,period=250,mixer=0x3e,volumes=(15,0,0),noise=0,shape=9,envelope=0x0800,row=0,col=0,periods=None):
        periods=periods or (period,period,period)
        values=[v for p in periods for v in (p&255,p>>8)]+[noise,mixer,*volumes,envelope&255,envelope>>8,shape]
        assert len(values)==14 and mixer&0xc0==0
        ay_steps.append(dict(name=name,registers=values,highlight_row=row,highlight_column=col))
    for channel in range(3):
        for note,period in enumerate((1000,500,250,125)):
            volumes=[0,0,0];volumes[channel]=15
            ay_step(f'{"ABC"[channel]} {("LOW","MID","HIGH","TOP")[note]}',period=period,mixer=0x3f^(1<<channel),volumes=volumes,row=channel*2,col=note*8)
    for k,volume in enumerate((3,8,15)):
        ay_step('VOLUME '+('LOW','MID','MAX')[k],volumes=(volume,0,0),row=6,col=8+k*8)
    for k,noise in enumerate((31,8,1)):
        ay_step('NOISE '+('LOW','MID','HIGH')[k],mixer=0x37,noise=noise,row=8,col=8+k*8)
    for k,shape in enumerate((9,13,10,8)):
        ay_step('ENVELOPE '+('DOWN','UP','TRI','SAW')[k],volumes=(16,0,0),shape=shape,row=10,col=k*8)
    ay_step('CHORD',mixer=0x38,volumes=(12,12,12),periods=(500,400,333),row=12,col=0)
    ay_step('SILENCE',mixer=0x3f,volumes=(0,0,0),row=12,col=16)
    assert len(ay_steps)==24
    ay_table=bytes(v for step in ay_steps for v in step['registers']+[step['highlight_row'],step['highlight_column']])
    flat[0x4400:0x4400+len(ay_table)]=ay_table
    for code,chip in enumerate(['U6','U7','U12','U13','U17','U18'],1):
        if chip in ('U6','U7'):_,a=attribute_page(chip,code)
        else:
            a=bytearray(768)
            for cy,text in [(1,'RAM FAIL'),(8,chip+' PATH'),(15,'CODE 2 '+str(code))]:
                start=(32-len(text)*4)//2
                for k,ch in enumerate(text):
                    for y,bits in enumerate(FONT[ch]):
                        for x,on in enumerate(bits):a[(cy+y)*32+start+k*4+x]=7 if on=='1' else 0
        addr=cursors[1];flat[addr:addr+768]=a;cursors[1]+=768;lines.append(f'FAULT_{chip} EQU ${addr:04x}')
    def place(name,data,dest,continuation):
        encoded=pack(data);bank=next((b for b in cursors
            if (b!=2 or 0x6000<=dest and dest+len(data)<=0x8000)
            and (b!=3 or 0x4000<=dest and dest+len(data)<=0x6000)
            and cursors[b]+len(encoded)<=b*8192+(0x1f00 if b==1 else 0x1fd0)),None)
        if bank is None:
            assert len(data)>256,(name,len(encoded),cursors)
            middle=len(data)//2
            tail=name+f'_tail_{dest+middle:04x}'
            place(tail,data[middle:],dest+middle,continuation)
            place(name,data[:middle],dest,'load_'+tail)
            return
        addr=cursors[bank];flat[addr:addr+len(encoded)]=encoded;cursors[bank]+=len(encoded)
        lines.extend([f'load_{name}:',f' ld hl,${addr:04x}',f' ld de,${dest:04x}',f' ld bc,{len(data)}',f' ld iy,{continuation}',f' jp unpack_bank{bank}'])
        assets.append(dict(name=name,bank=bank,address=f'{addr:04X}',packed=len(encoded),unpacked=len(data),destination=f'{dest:04X}'))
    for bank in cursors:
        lines.extend([f'unpack_bank{bank}:',f' ld a,${1|(1<<bank):02x}',' out ($f4),a',f' ld a,${((bank+1)*32)&255:02x}',' ld i,a',' jp unpack'])
    for name,data in screens.items():
        if name=='keyboard':
            # Artwork contains arbitrary bitmap pixels, not font tiles.
            lines.extend(['load_keyboard:',' jp load_keyboard_pixels'])
            place('keyboard_pixels',data[:6144],0x4000,'load_keyboard_attrs')
            place('keyboard_attrs',data[6144:],0x5800,'keyboard_ready')
            continue
        glyphs={font[n*8:n*8+8]:n+32 for n in range(96)}
        glyphs[bytes(8)]=32
        tiles=bytearray(768)
        from generate_design_assets import offset
        for row in range(24):
            for col in range(32):
                glyph=bytes(data[offset(col,row*8+y)] for y in range(8))
                ch=glyphs.get(glyph,45)
                tiles[row*32+col]=0 if ch==32 else ch
        place(name,bytes(tiles)+data[6144:],0x6400,'render_'+name)
        lines.extend(['render_'+name+':',' ld iy,'+name+'_ready',' jp render_tiles'])
    for name,files,mode in [('bars',['colorbar-pixels.bin','colorbar-attributes.bin'],0),('standard',['standard-pixels.bin','standard-attributes.bin'],0),('secondary',['secondary-pixels.bin','secondary-attributes.bin'],1),('mix128',['attribute-128-pixels.bin','attribute-128-attributes.bin'],0),('ecm',['ecm-pixels.bin','ecm-attributes.bin'],2),('hires',['hires-primary.bin','hires-secondary.bin'],6)]:
        place(name,(ROOT/'assets/video'/files[0]).read_bytes(),0x6000 if mode==1 else 0x4000,f'load_{name}_attrs')
        place(name+'_attrs',(ROOT/'assets/video'/files[1]).read_bytes(),0x7800 if mode==1 else 0x6000 if mode in (2,6) else 0x5800,f'video_{name}_ready')
    matrix=[['CS','Z','X','C','V'],list('ASDFG'),list('QWERT'),list('12345'),list('09876'),list('POIUY'),['EN','L','K','J','H'],['SPACE','SY','M','N','B']];kl=[]
    for row,names in enumerate(matrix):
        kl.extend([f' ld bc,${(255^(1<<row)):02x}fe',' in a,(c)',' ld e,a'])
        for bit,name in enumerate(names):
            key=row*5+bit
            kl.extend([f' ld hl,${0x5b00+key:04x}',f' bit {bit},e',f' jr nz,key_up_{key}',' ld (hl),1',' ld a,$60',f' jr key_color_{key}',f'key_up_{key}:',' bit 0,(hl)',' ld a,$78',f' jr z,key_color_{key}',' ld a,$68',f'key_color_{key}:'])
            for n,(cy,cx,width) in enumerate(coords[name]):
                if n:kl.append(' ld a,c')
                label=f'key_painted_{key}_{n}'
                kl.extend([f' ld hl,${0x5800+cy*32+cx:04x}',f' ld b,{width}',f' ld iy,{label}',' jp keyboard_paint',label+':'])
    kl.extend([' ld bc,$fefe',' in a,(c)',' bit 0,a',' jr nz,break_up',' ld bc,$7ffe',' in a,(c)',' bit 0,a',' jr nz,break_up',' ld hl,$5b28',' ld (hl),1',' ld a,$60',' jr break_color','break_up:',' ld hl,$5b28',' bit 0,(hl)',' ld a,$78',' jr z,break_color',' ld a,$68','break_color:'])
    cy,cx,width=coords['BREAK'][0]
    kl.extend([f' ld hl,${0x5800+cy*32+cx:04x}',f' ld b,{width}',' ld iy,keyboard_break_done',' jp keyboard_paint','keyboard_break_done:'])
    (BUILD/'keyboard-scan.asm').write_text('\n'.join(kl)+'\n')
    speech_frames=[]
    for frame in range(16):
        periods=[(97+frame*53+channel*181)&4095 for channel in range(3)]
        values=[v for p in periods for v in (p&255,p>>8)]
        values += [frame*2,0x38 if frame&1 else 0x30,
                   15-(frame%8),8+(frame%8),15,0,8,0,0,0]
        assert len(values)==16 and values[7]&0xc0==0
        speech_frames.append(' DB '+','.join(str(v) for v in values))
    (BUILD/'load-ay.asm').write_text('\n'.join(speech_frames)+'\n')
    lines.append('font_data EQU $2200');(BUILD/'font.bin').write_bytes(font)
    (BUILD/'suite-assets.asm').write_text('\n'.join(lines)+'\n')
    generated,phases=extended_ram();(BUILD/'ram-tests.asm').write_text(generated)
    paths=['src/diagnostic.asm','src/modules.asm','src/crc.asm','src/cpu.asm','src/boot.asm','src/joystick.asm'];source='\n'.join((ROOT/p).read_text() for p in paths)
    code='\n'.join(x.split(';')[0] for x in (source+generated+'\n'.join(lines)+'\n'.join(kl)).splitlines())
    assert not re.search(r'^\s*(call|ret|reti|retn|push|pop|rst|halt)\b',code,re.M|re.I)
    optional_low=(ROOT/'src/load_low.asm').read_text()
    # Only an explicitly gated AF save and data-only PUSH/POP pairs may use SP.
    audited=optional_low.replace(' push af ; Only genuine return profile reads this saved AF, never default tests.','').replace(' push de','').replace(' pop bc','')
    assert not re.search(r'^\s*(call|ret|reti|retn|push|pop|rst|halt)\b', '\n'.join(l.split(';')[0] for l in audited.splitlines()),re.M|re.I)
    optional_high=(ROOT/'src/load.asm').read_text().split('load_return_start:')[0]
    assert not re.search(r'^\s*(call|ret|reti|retn|push|pop|rst|halt)\b', '\n'.join(l.split(';')[0] for l in optional_high.splitlines()),re.M|re.I)
    paths += ['src/load.asm','src/load_low.asm']
    subprocess.run([str(args.assembler),'--nologo','--raw='+str(BUILD/'low.bin'),'--sym='+str(BUILD/'symbols.txt'),str(ROOT/'src/diagnostic.asm')],cwd=ROOT,check=True)
    low=(BUILD/'low.bin').read_bytes();assert len(low)==8192;flat[:8192]=low
    (BUILD/'load-low.asm').write_text((BUILD/'symbols.txt').read_text())
    subprocess.run([str(args.assembler),'--nologo','--raw='+str(BUILD/'load.bin'),'--sym='+str(BUILD/'load-symbols.txt'),str(ROOT/'src/load.asm')],cwd=ROOT,check=True)
    load=(BUILD/'load.bin').read_bytes();assert len(load)<=0xa00
    flat[0x8400:0x8400+len(load)]=load
    (BUILD/'keyboard-rom.asm').write_text(' ORG $e000\n INCLUDE "symbols.txt"\nkeyboard_rom_scan:\n INCLUDE "keyboard-scan.asm"\n jp keyboard_scan_done\n ASSERT $ <= $e600\n')
    subprocess.run([str(args.assembler),'--nologo','--raw=keyboard-rom.bin','keyboard-rom.asm'],cwd=BUILD,check=True)
    scanner=(BUILD/'keyboard-rom.bin').read_bytes();flat[0xe000:0xe000+len(scanner)]=scanner
    (BUILD/'joystick-wrapper.asm').write_text(' INCLUDE "symbols.txt"\n INCLUDE "../src/joystick.asm"\n')
    subprocess.run([str(args.assembler),'--nologo','--raw=joystick.bin','joystick-wrapper.asm'],cwd=BUILD,check=True)
    joystick=(BUILD/'joystick.bin').read_bytes();assert len(joystick)==96
    flat[0x3f00:0x3f00+len(joystick)+1]=joystick+bytes([sum(joystick)&255])
    (BUILD/'cpu-low.asm').write_text((BUILD/'symbols.txt').read_text())
    subprocess.run([str(args.assembler),'--nologo','--raw='+str(BUILD/'cpu.bin'),'--sym='+str(BUILD/'cpu-symbols.txt'),str(ROOT/'src/cpu.asm')],cwd=ROOT,check=True)
    cpu=(BUILD/'cpu.bin').read_bytes();assert len(cpu)<=0x400;flat[0x4000:0x4000+len(cpu)]=cpu
    subprocess.run([str(args.assembler),'--nologo','--raw='+str(BUILD/'crc.bin'),'--sym='+str(BUILD/'crc-symbols.txt'),str(ROOT/'src/crc.asm')],cwd=ROOT,check=True)
    crc=(BUILD/'crc.bin').read_bytes();assert len(crc)<=1024;flat[0x8000:0x8000+len(crc)]=crc;flat[0x2000:0x2200]=crc.ljust(512,b"\xff")
    for bank in range(8):flat[bank*8192+0x1ff0:bank*8192+0x1ff4]=bytes([0xa5^bank,0x5a^bank,bank,255^bank])
    checks=[sum(flat[b*8192:b*8192+0x1fd0])&65535 for b in range(8)]
    flat[0x1fd0:0x1fe0]=b''.join(n.to_bytes(2,'little') for n in checks)
    dck=bytes([0])+bytes([2]*8)+flat
    (BUILD/'diagnostic-v02.bin').write_bytes(flat);(BUILD/'diagnostic-v02.dck').write_bytes(dck)
    # PicoROM uploads take raw ROM bytes, never the nine-byte DCK header.
    (BUILD/'diagnostic-v02-picorom.bin').write_bytes(flat)
    (BUILD/'diagnostic-v02-eprom-27C512.bin').write_bytes(flat)
    manifest=dict(version=VERSION.lstrip('v'),entry='0100',descriptors=[2]*8,dck_sha256=hashlib.sha256(dck).hexdigest(),bin_sha256=hashlib.sha256(flat).hexdigest(),phases=phases,assets=assets,bank_used={str(b):c-b*8192 for b,c in cursors.items()},source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},font_rom_sha256=hashlib.sha256(rom).hexdigest(),limitations=['Passive HOME initialization dependency','Physical validation pending','Optional high-ROM/HOME-gateway/IRQ execution exposures'])
    (BUILD/'manifest-v02.json').write_text(json.dumps(manifest,indent=2)+'\n')
    manifest['picorom']={'file':'diagnostic-v02-picorom.bin','bytes':65536,'sha256':manifest['bin_sha256'],
                        'profile':'PicoROM-P28 / 27C512-style full64K cartridge decode',
                        'upload_size':'512KBit','layout':'A0-A15, chunks0-7 ascending; no DCK header; no byte swap',
                        'physical_validation':'pending'}
    manifest['ay_playback']={'table_address':'4400','step_count':24,'stride':16,'steps':ay_steps}
    manifest['mixed_load']={'menu_key':'L','code_address':'8400','code_limit':'8E00','code_bytes':len(load),
        'options':['RAM address data','March C-','ECM','frame IRQ','DOCK banking','quiet/busy power cycling and video rotation','AY Speech2AY traffic','PUSH/POP data'],
        'default_mask':'83','combined_mask':'FF','ay_frames':16,'ay_registers':'R0-R12',
        'irq_sink':'BFFD-BFFE, deferred DI-only00/FF comparisons','return_profiles':'separate R confirmation; qualified IM1/IM2',
        'physical_validation':'pending','keyboard_scanner_address':'E000','keyboard_scanner_bytes':len(scanner)}
    manifest['eprom']={'file':'diagnostic-v02-eprom-27C512.bin','bytes':65536,'sha256':manifest['bin_sha256'],
                      'profile':'27C512-compatible EPROM / full64K DOCK cartridge',
                      'layout':'Offset0000; ascending A0-A15; all8 chunks; no DCK header',
                      'physical_validation':'pending'}
    manifest['keyboard_art']=json.loads((ROOT/'assets/keyboard/provenance.json').read_text())
    manifest['keyboard_art']['layout']='keyboard-art-layout.json;42 physical positions,40 contacts plus derived BREAK history'
    (BUILD/'manifest-v02.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for name,data in screens.items():standard_render(data[:6144],data[6144:]).resize((768,576),Image.Resampling.NEAREST).save(BUILD/(name+'-v02.png'))
    print('Built v0.2 ROM-only suite; packed assets:',sum(a['packed'] for a in assets),'bytes')
if __name__=='__main__':main()
