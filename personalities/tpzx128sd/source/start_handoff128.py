"""Temporary no-reset handoff trial; no target file uploads or reboot."""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from pico_debug import DEFAULT_QUEUE,ROOT,make_job,dump,serve

def queue_handoff(root,mode):
    if mode not in ('zx128','zx128sd'):raise ValueError('Unknown mode')
    for folder in ('pending','running'):
        if list((root/folder).glob('*.json')):
            raise RuntimeError('Existing '+folder+' jobs need inspection; no new jobs created')
    name='H128' if mode=='zx128' else 'H128SD'
    manifest=json.loads((ROOT/'build/handoff128'/ (name+'.json')).read_text())
    rom=ROOT/('build/rom/TPZX128.ROM' if mode=='zx128' else 'build/fs128-rom/TPZXSD.ROM')
    if hashlib.sha256(rom.read_bytes()).hexdigest()!=manifest['rom_sha256']:
        raise RuntimeError('Rebuild handoff TAP for the current ROM before staging')
    files=('personality128.py','personality128_stock.py','fs128_legacy.py',
           'personality128_fs.py','fs128_image.py','handoff128.py')
    jobs=[make_job('load',file,description='%d/7 Definitions only. KEEP TS RESET RELEASED.'%(i+1))
          for i,file in enumerate(files)]
    jobs.append(make_job('handoff128-stock-run' if mode=='zx128' else 'handoff128-sd-run',description=
        '7/7 Keep TS Reset RELEASED. At HOME handoff armed, enter RANDOMIZE USR 32768 on Timex.'))
    batch=jobs[0]['id'].split('-')[0]
    for index,job in enumerate(jobs):
        job['id']=batch+'-%02d-'%(index+1)+job['id'].split('-')[-1]
        dump(root/'pending'/(job['id']+'.json'),job)
    return jobs

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',default='COM14')
    parser.add_argument('--mode',choices=('zx128','zx128sd'),required=True)
    args=parser.parse_args()
    print('Before continuing: normal Timex/TSPico running, correct ROM already in SRAM slot 4,')
    print('and matching H128.TAP or H128SD.TAP already loaded as CODE at 32768.')
    print('Do not run this from a live Spectrum 128 personality. No TS Reset hold in this trial.')
    queue_handoff(DEFAULT_QUEUE,args.mode)
    return serve(SimpleNamespace(directory=DEFAULT_QUEUE,port=args.port,timeout=180,interrupt=True,once=False))

if __name__=='__main__':
    try:raise SystemExit(main())
    except KeyboardInterrupt:print('\nPC helper stopped; cold boot before another handoff trial.');raise SystemExit(130)
    except Exception as error:print(error);raise SystemExit(1)
