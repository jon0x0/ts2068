"""Verify physical payload and known TSPico DCK expansion, without hardware writes."""
from pathlib import Path
import ast, hashlib, io, json, subprocess, sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT/'build'
cart = (BUILD/'diagnostic-v02.dck').read_bytes()
raw = (BUILD/'diagnostic-v02-picorom.bin').read_bytes()
assert len(cart)==65545 and cart[:9]==bytes([0]+[2]*8)
assert len(raw)==65536 and raw==cart[9:]==(BUILD/'diagnostic-v02.bin').read_bytes()
assert (BUILD/'diagnostic-v02-eprom-27C512.bin').read_bytes()==raw
manifest=json.loads((BUILD/'manifest-v02.json').read_text())
assert manifest['picorom']['sha256']==hashlib.sha256(raw).hexdigest()
assert manifest['eprom']['sha256']==hashlib.sha256(raw).hexdigest() and manifest['eprom']['bytes']==65536
cases=[dict(name='eight ROM descriptors, header-free64K payload and BIN identity',result='PASS'),
       dict(name='PicoROM manifest byte length and SHA256',result='PASS')]
sources={}
converter=ROOT.parent/'AISkill_TS2068/skills/ts2068-cartridge-development/scripts/dck_to_picorom.py'
if converter.is_file():
    output=BUILD/'picorom-conversion-check.bin'
    subprocess.run([sys.executable,str(converter),str(BUILD/'diagnostic-v02.dck'),str(output)],check=True,capture_output=True)
    assert output.read_bytes()==raw
    sources['skill_converter_sha256']=hashlib.sha256(converter.read_bytes()).hexdigest()
    cases.append(dict(name='independent TS2068 skill DCK-to-PicoROM conversion matches payload',result='PASS'))
source=ROOT.parent/'TSPico/TS-Pico-1_1.20260717/src/TS/tspico.py'
if source.is_file():
    tree=ast.parse(source.read_text(encoding='utf-8-sig'))
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='DCK_IMAGE')
    class MemoryFile(io.BytesIO):
        def close(self): pass  # Retain in-memory output for comparison; no disk access.
    target=MemoryFile()
    def fake_open(name,mode):
        if (name,mode)==('diagnostic.dck','rb'):return MemoryFile(cart)
        assert (name,mode)==('/TMP/temp.bin','wb'),(name,mode)
        return target
    def fake_remove(name): assert name=='/TMP/temp.bin'
    events=[]
    namespace=dict(TSP=SimpleNamespace(f_name='diagnostic.dck'),
                   os=SimpleNamespace(remove=fake_remove),open=fake_open,
                   LOG=lambda message,level:events.append((message,level)))
    # Only this inspected, isolated conversion function; no imports or startup.
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
    namespace['DCK_IMAGE']()
    assert target.getvalue()==raw and not any(level==3 for _,level in events)
    sources['tspico_source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    cases.append(dict(name='inspected TSPico v1.1 DCK_IMAGE converts diagnostic identically',result='PASS'))
record=dict(image_sha256=hashlib.sha256(cart).hexdigest(),picorom_sha256=hashlib.sha256(raw).hexdigest(),
            result='PASS',cases=cases,sources=sources,
            limitations=['No USB upload, flash commit, SRAM access, PIO timing or physical coexistence tested',
                         'Optional source checks apply only to the recorded local snapshots'])
(BUILD/'image-format-verification.json').write_text(json.dumps(record,indent=2)+'\n')
print('Image format verification PASS:',len(cases),'checks;64K PicoROM payload ready.')
