"""Test-only subprocess bridge: execute the real MicroPython service handlers.

Pickle is used only for isolated host-test state, never by device firmware.
"""
import json,pickle,sys,types
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'firmware'))
request=json.loads(sys.argv[1]);sd=Path(request['sd']).resolve()
out=[]
tp=types.ModuleType('dev_tspico')
tp.PARAMS=lambda pre:pre
tp.getArgs=lambda cmd:cmd.split(' ',1)[1] if ' ' in cmd else ''
tp.CMD_PUT=out.append;tp.MQ_READY=lambda:None;tp.CH_READY=lambda:None
tp.tspico_io=types.SimpleNamespace(CAN_STREAM=lambda:False)
def call(fn):
    try:return fn(),1
    except (OSError,ValueError) as e:
        with open(sd/'rpc-errors.txt','a') as f:f.write(str(e)+'\n')
        return str(e),3
tp.CH_CALL=call
catalog=types.SimpleNamespace(resolve=lambda cur,name:str(sd/name.lstrip('/')))
ts=types.ModuleType('TS');ts.catalog=catalog
sys.modules['dev_tspico']=tp;sys.modules['TS']=ts
if request.get('directory_kb'):
    config=types.ModuleType('cpm_config');config.CPM_STORAGE='directory';config.CPM_DIRECTORY='/CPM/FILES';config.CPM_DIRECTORY_KB=request['directory_kb']
    sys.modules['cpm_config']=config
import cpm_service
state=sd/'rpc-state.pickle'
if state.exists():
    with state.open('rb') as f:
        saved=pickle.load(f)
        cpm_service._directory,cpm_service._pending=saved[:2]
        if len(saved)>2:cpm_service._tap,cpm_service._storage=saved[2:]
handlers={'tpi:.cpminfo':'INFO','tpi:.cpmcap':'CAP','tpi:.cpmrd':'READ','tpi:.cpmw0':'WRITE0','tpi:.cpmw1':'WRITE1','tpi:.cpmmount':'MOUNT','tpi:.cpmsave':'SAVE'}
handler=handlers[request['command'].split(' ',1)[0].lower()]
getattr(cpm_service,handler)(None,types.SimpleNamespace(cur_path='/'),(request['par1'],request['par2']),request['command'])
with state.open('wb') as f:pickle.dump((cpm_service._directory,cpm_service._pending,cpm_service._tap,cpm_service._storage),f)
print(json.dumps(out))
