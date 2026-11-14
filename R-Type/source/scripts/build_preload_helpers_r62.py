from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(out,asm,loader_len,preload_entry,home=False):
 suffix=(ROOT/'src/fullgame_gateway.asm').read_text();suffix=suffix[suffix.index('select_region:'):];suffix=suffix.replace('        ASSERT $ <= $A190','')
 def driver(module,origin):
  return f'''{module}_image:
        DISP ${origin:04X}
{module}:
        MODULE {module}
copy_chunk:
        OUT ($F4),A
        LDIR
        XOR A
        OUT ($F4),A
        RET
select_slot:
        ADD A,A
        LD (command_header+5),A
        JP select_region
'''+suffix+f'''state: DS 9,0
        ENDMODULE
{module}_end:
        ASSERT $ <= ${origin+400:04X}
        ENT
'''
 b=(out/'level01_region.bin').read_bytes();at=b.find(bytes.fromhex('cd d8 73 3a a3 fd'),0xc00,0xd00);assert at>=0
 origin=0x7b00 if home else 0x3a00
 feedback_origin=0xa400 if home else 0x3e00
 feedback,_=asm('preload_feedback_home'if home else'preload_feedback',f'FEEDBACK_ORIGIN EQU ${feedback_origin:04X}\n'+(ROOT/'src/preload_feedback_r62.asm').read_text())
 source=f'LOADING_FEEDBACK EQU ${feedback_origin:04X}\nHOT_ORIGIN EQU ${origin:04X}\nHOME_VARIANT EQU {int(home)}\nNATIVE_SELECT_START EQU ${at:04X}\nNEW_LOADER_LENGTH EQU {loader_len}\nPRELOAD_ENTRY EQU ${preload_entry:04X}\n'+(ROOT/'src/level_hotkeys_r62.asm').read_text()+(ROOT/'src/preload_snapshot_r62.asm').read_text()+driver('preload_driver',0xa000)+driver('final_driver',0x7b00)+f'        ASSERT $ <= ${0x8000 if home else 0x3fe0:04X}\n'
 blob,sy=asm('level_hotkeys_home'if home else'level_hotkeys',source)
 image=lambda label,end,runtime_origin:blob[sy[label]-origin:sy[label]-origin+sy[end]-runtime_origin]
 raw=image('preload_driver_image','preload_driver_end',0xa000);assert len(raw)==sy['preload_driver_end']-0xa000 and len(raw)>0;(out/'preload_driver.bin').write_bytes(raw)
 vals={'PRELOAD_DRIVER_STATE':sy['preload_driver.state'],'PRELOAD_SELECT':sy['preload_driver.select_slot'],'PRELOAD_COPY':sy['preload_driver.copy_chunk'],'FINAL_DRIVER_STATE':sy['final_driver.state'],'FINAL_SELECT':sy['final_driver.select_slot'],'FINAL_COPY':sy['final_driver.copy_chunk']}
 head=''.join(f'{k} EQU ${v:04X}\n'for k,v in vals.items());restore,_=asm('preload_restore',head+(ROOT/'src/preload_restore_r61.asm').read_text())
 return blob,sy,len(raw),len(restore)
