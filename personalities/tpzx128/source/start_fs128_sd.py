"""Queue the complete temporary SD personality, then run the guided USB helper."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from pico_debug import DEFAULT_QUEUE,make_job,dump,serve


def queue_basic_session(root):
    for folder in ('pending','running'):
        if list((root/folder).glob('*.json')):
            raise RuntimeError('Existing '+folder+' jobs need inspection before another SD session')
    definitions=('personality128.py','personality128_stock.py','fs128_legacy.py',
                 'personality128_fs.py','fs128_image.py')
    # Validate all definitions before creating any queued jobs.
    jobs=[make_job('load',name,'%d/6 Definitions only. KEEP TS RESET RELEASED.'%(i+1))
          for i,name in enumerate(definitions)]
    jobs.append(make_job('fs128-basic-run',description=
                '6/6 HOLD TS RESET, Enter, RELEASE AT ARMED. Then use 128 BASIC; service stays running.'))
    # Windows clock resolution can give every job the same timestamp. The
    # helper sorts filenames, so encode dependency order before the UUID.
    batch=jobs[0]['id'].split('-')[0]
    for index,job in enumerate(jobs):
        job['id']=batch+'-%02d-'%(index+1)+job['id'].split('-')[-1]
        dump(root/'pending'/(job['id']+'.json'),job)
    return jobs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',default='COM14')
    args=parser.parse_args()
    queue_basic_session(DEFAULT_QUEUE)
    return serve(SimpleNamespace(directory=DEFAULT_QUEUE,port=args.port,
                                 timeout=180,interrupt=True,once=False))


if __name__=='__main__':
    try:raise SystemExit(main())
    except KeyboardInterrupt:print('\nPC helper stopped. No Pico reboot requested.');raise SystemExit(130)
    except Exception as error:print(error);raise SystemExit(1)
