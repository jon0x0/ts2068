"""Exercise the generated ROM using real keyboard input in the CPU model."""
import json
from pathlib import Path
from rom_machine import Machine

def smoke():
    out=Path('build/rom')
    m=Machine();m.run_frames(240);m.screenshot(out/'boot.png')
    assert m.rom_switches>0 and m.memory.f4==0xc0
    m.press('shift','6');m.press('enter');m.run_frames(30);m.screenshot(out/'basic.png')
    m.type_text('10 print 1+2\n');m.run_frames(20);m.screenshot(out/'program.png')
    prog=m.memory[0x5c53]|m.memory[0x5c54]<<8
    assert [m.memory[prog],m.memory[prog+1]]==[0,10]
    assert m.memory[prog+4]==0xf5,'PRINT token was not stored'
    m.type_text('run\n');m.run_frames(40);m.screenshot(out/'run.png')
    glyph=m.memory.roms[1][0x3d00+(ord('3')-32)*8:0x3d00+(ord('3')-32)*8+8]
    assert [m.memory.home[y<<8] for y in range(8)]==glyph,'RUN did not print 3'
    m.press('enter');m.run_frames(100)
    before=len(m.ay_events)
    m.type_text('play "C"\n');m.run_frames(120);m.screenshot(out/'play.png')
    assert len(m.ay_events)>before+5,'PLAY did not produce AY events'
    assert any(reg in (0,1,2,3,4,5) and value for reg,value in m.ay_events[before:]),'No tone period was set'
    m.press('enter');m.run_frames(100)
    m.memory.home[0x4000:0x4004]=[0x12,0x34,0x56,0x78]
    m.type_text('save !"t" code 32768,4\n');m.run_frames(60);m.screenshot(out/'ram-save.png')
    m.press('enter');m.run_frames(100)
    m.memory.home[0x4000:0x4004]=[0,0,0,0]
    m.type_text('load !"t" code 32768\n');m.run_frames(60);m.screenshot(out/'ram-load.png')
    assert m.memory.home[0x4000:0x4004]==[0x12,0x34,0x56,0x78],m.memory.home[0x4000:0x4004]
    report=m.report()
    report['checks']=['cold boot with nonzero HOME and SRAM','128 menu and keyboard editor',
                      'tokenized BASIC line','RUN prints 3','PLAY emits tone-period writes',
                      'RAM disk SAVE/LOAD exact four-byte roundtrip']
    (out/'basic-play.json').write_text(json.dumps(report,indent=2))
    return report


if __name__=='__main__':
    print({k:v for k,v in smoke().items() if k!='paging_events'})
