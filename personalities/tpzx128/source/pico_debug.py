"""Local USB REPL job runner. No target file uploads or soft resets.

Run `ports`, then `serve --port COM14` in a user-visible PowerShell window.
Codex queues jobs with `queue ACTION`; results appear under build/serial-debug.
The operator acknowledges each job, holding TS Reset only where requested.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/serial-python'))
DEFAULT_QUEUE=ROOT/'build/serial-debug'
ACTIONS={
    'handoff128-probe-arm':(True,"print(handoff128_probe_arm(True))\n"),
    'handoff128-probe-read':(False,"print(handoff128_probe_read())\n"),
    'handoff128-inspect':(False,"print(status_stock128())\nprint({'gpio':hex(mem32[0xd0000004]&0xffffffff),'pio0_enabled':hex(mem32[0x50200000]&15),'pio1_enabled':hex(mem32[0x50300000]&15),'latch_pc':mem32[0x502000d4]&31,'control_pc':mem32[0x503000d4]&31,'address_pc':mem32[0x503000ec]&31,'latch_pin_config':hex(mem32[0x502000dc]&0xffffffff),'gp22_control':hex(mem32[0x400140b4]&0xffffffff),'dma_remaining':hex(mem32[0x50000008]&0xffffffff)})\n"),
    'handoff128-stock-resume':(False,"print(handoff128_wait('zx128',resume=True))\n"),
    'handoff128-status':(False,"import tspico\nprint({'pio0_enabled':hex(mem32[0x50200000]&15),'pio1_enabled':hex(mem32[0x50300000]&15),'stock_rx_pending':tspico.MQ.rx_fifo(),'stock_tx_pending':tspico.MQ.tx_fifo(),'stock_io':str(tspico.MQ),'personality_active':_stock128 is not None,'gpio':hex(mem32[0xd0000004]&0xffffffff)})\n"),
    'handoff128-stock-run':(False,"print(handoff128_wait('zx128'))\n"),
    'handoff128-sd-run':(False,"print(handoff128_wait('zx128sd'))\n"),
    'fs128-basic-run':(True,"print(start_fs128(True))\nprint('FS128_RELEASE_RESET')\nfs128_run_basic()\n"),
    'fs128-latch-status':(False,"from machine import mem32\n_l=_stock128[2]\n_d=_stock128[3]\n_l.active(0)\n_d.active(0)\ntry:\n _pending=_l.rx_fifo()\n if _pending:raise RuntimeError('Latch RX is not empty')\n _l.exec('mov(isr,y)')\n _l.exec('push(noblock)')\n _y=_l.get()\n print({'slot_y':hex(_y&0xffffffff),'program_base':_fs128_program_live[1],'instruction_memory_write_only':True,'expected_program':[hex(v) for v in _fs128_program_live[0]]})\nfinally:\n _ctrl=_d.pack_ctrl(size=2,inc_read=False,inc_write=False,treq_sel=4,high_pri=True)\n _d.config(read=0x50200020,write=0x50300014,count=0xffffffff,ctrl=_ctrl,trigger=True)\n _l.active(1)\n"),
    'fs128-return-status':(False,"from machine import mem32\n_a=_stock128[1]\n_a.active(0)\ntry:\n _a.exec('mov(isr,x)')\n _a.exec('push(noblock)')\n _cached=_a.get()\nfinally:\n _a.active(1)\nprint({'cached_address_word':hex(_cached&0xffffffff),'gpio':hex(mem32[0xd0000004]&0xffffffff),'pio0_fifo':hex(mem32[0x5020000c]&0xffffffff),'pio1_fifo':hex(mem32[0x5030000c]&0xffffffff),'latch_exec':hex(mem32[0x502000c8]&0xffffffff),'latch_pins':hex(mem32[0x502000dc]&0xffffffff),'address_pins':hex(mem32[0x503000f4]&0xffffffff),'control_pins':hex(mem32[0x503000dc]&0xffffffff),'address_pc':mem32[0x503000ec]&31})\n"),
    'fs128-pin-status':(False,"from machine import mem32\nprint({'gpio_in':hex(mem32[0xd0000004]&0xffffffff),'sio_out':hex(mem32[0xd0000010]&0xffffffff),'sio_oe':hex(mem32[0xd0000020]&0xffffffff),'pio0_enabled':hex(mem32[0x50200000]&255),'pio1_enabled':hex(mem32[0x50300000]&255),'pins':[(p,hex(mem32[0x40014004+8*p]&0xffffffff),hex(mem32[0x40014000+8*p]&0xffffffff)) for p in (2,3,4,12,19,20,21,22,28)]})\n"),
    'fs128-sd-probe':(False,"import os, tspico\nfrom machine import Pin, SPI\n_sdprobe_spi=None\n_sdprobe_mounted=False\ntry:\n Pin(12,Pin.OUT,value=1)\n _sdprobe_spi=SPI(0,sck=Pin(2,Pin.IN),mosi=Pin(3,Pin.IN),miso=Pin(4,Pin.IN))\n _sdprobe_card=tspico.SDCard(_sdprobe_spi,Pin(28,Pin.OUT,value=1))\n os.mount(_sdprobe_card,'/sd')\n _sdprobe_mounted=True\n print({'sd_mount':True,'files':os.listdir('/sd/TAP/128')})\nexcept Exception as _sdprobe_error:\n print({'sd_mount':False,'exception':repr(_sdprobe_error)})\nfinally:\n if _sdprobe_mounted:os.umount('/sd')\n if _sdprobe_spi is not None:_sdprobe_spi.deinit()\n Pin(28,Pin.OUT,value=1)\n Pin(12,Pin.OUT,value=1)\n"),
    'fs128-status':(False,"import os, tspico\nprint({'root':os.listdir('/'),'current_path':getattr(tspico.TSP,'cur_path',None),'log_tail':str(getattr(tspico,'log_entries',''))[-1600:],'session':globals().get('_fs128_session')})\n"),
    'fs128-probe-run':(True,"print(start_fs128(True))\nprint('FS128_RELEASE_RESET')\nprint(fs128_serve_legacy(wait_ms=30000))\n"),
    'stock128-start':(True,'print(reset_stock128(True))\n'),
    'stock128-status':(False,'print(status_stock128())\n'),
    'no-paging-bank7-start':(True,'print(start_nopaging128(True,use_stock_address_selector=True,dock_bank=7))\n'),
    'no-paging-address-start':(True,'print(start_nopaging128(True,use_stock_address_selector=True))\n'),
    'no-paging-status':(False,"from machine import mem32\nprint({'definitions':{n:n in globals() for n in ('start','fixed_address128','start_nopaging128')},'personality_active':globals().get('_keepalive') is not None,'pio0_enabled':hex(mem32[0x50200000]&255),'pio1_enabled':hex(mem32[0x50300000]&255),'dma0_enabled':bool(mem32[0x5000000c]&1)})\n"),
    'no-paging-start':(True,'print(start_nopaging128(True))\n'),
    'paging-samples':(False,"_dbg128_n=_observer.rx_fifo()\n_dbg128_samples=[_observer.get()&0xffff for _ in range(_dbg128_n)]\nprint({'first_write_samples_early_late':[(hex((w>>8)&255),hex(w&255)) for w in _dbg128_samples],'dma_remaining':hex(mem32[0x50000008]&0xffffffff),'dma_control':hex(mem32[0x5000000c]&0xffffffff)})\n"),
    'gpio-trace-arm':(True,'print(gpio_trace_arm128(True))\n'),
    'gpio-trace-read':(False,'print(gpio_trace_stream128())\n'),
    'rom-trace-arm':(True,'print(rom_trace_arm128(True))\n'),
    'rom-trace-read':(False,'print(rom_trace_read128())\n'),
    'rom-read-live':(False,"_dbg128_count=_rom_probe.rx_fifo()\n_dbg128_words=[_rom_probe.get()&0xffffffff for _ in range(_dbg128_count)]\n_dbg128_bits=globals().get('ROM_PROBE_SAMPLE_BITS',8)\n_dbg128_mask=(1<<_dbg128_bits)-1\nprint({'sample_count':_dbg128_count,'rom_read_samples_early_late':[(hex((w>>_dbg128_bits)&255),hex(w&255)) for w in _dbg128_words],'cycle_signals_early_late':[[{'a0':(v>>8)&1,'direction':(v>>9)&1,'u6_disabled':(v>>10)&1,'mreq':(v>>11)&1} for v in ((w>>_dbg128_bits)&_dbg128_mask,w&_dbg128_mask)] for w in _dbg128_words] if _dbg128_bits==12 else None,'expected':['0xf3','0x1','0x2b','0x69'],'gpio':hex(mem32[0xd0000004]&0xffffffff)})\n"),
    'bus-status':(False,"from machine import mem32\nprint({'gpio_samples':sorted({hex(mem32[0xd0000004]&0xffffffff) for _ in range(64)}),'pio0_ctrl':hex(mem32[0x50200000]&0xffffffff),'probe_pc':mem32[0x502000ec],'probe_execctrl':hex(mem32[0x502000e4]&0xffffffff),'probe_pinctrl':hex(mem32[0x502000f4]&0xffffffff),'probe_fifo_level':hex(mem32[0x5020000c]&0xffffffff),'enable_pc':mem32[0x503000d4],'enable_execctrl':hex(mem32[0x503000cc]&0xffffffff),'gp12_ctrl':hex(mem32[0x40014064]&0xffffffff),'gp15_ctrl':hex(mem32[0x4001407c]&0xffffffff),'pio0_padoe':hex(mem32[0x50200040]&0xffffffff),'pio1_padoe':hex(mem32[0x50300040]&0xffffffff)})\n"),
    'preflight':(False,"import sys, gc\ngc.collect()\nprint({'implementation':str(sys.implementation),'free_memory':gc.mem_free(),'personality_active':globals().get('_keepalive') is not None})\n"),
    'inspect':(True,'print(inspect128(True))\n'),
    'restart':(True,'reset(host_held_in_reset=True)\n'),
    'pause-dma':(True,'reset(host_held_in_reset=True)\n_keepalive[3].active(0)\n'),
    'fixed-address':(True,'print(fixed_address128(True))\n'),
    'rom-arm':(True,'print(rom_read_probe128(True))\n'),
    'rom-read':(False,'print(read_rom_probe128())\n'),
}
DEFINITIONS=('personality128.py','inspect128.py','fixed_address128.py','rom_read_probe128.py','gpio_trace128.py','gpio_trace_stream128.py','nopaging128.py','personality128_stock.py','personality128_fs.py','fs128_legacy.py','fs128_image.py','handoff128.py')
PERSISTENT_ACTIONS=('fs128-basic-run','handoff128-stock-run','handoff128-sd-run','handoff128-stock-resume')


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,indent=2),encoding='utf-8')
    os.replace(temp,path)


def make_job(action,file=None,description=None):
    if action=='load':
        if file not in DEFINITIONS:
            raise ValueError('Choose one of: '+', '.join(DEFINITIONS))
        code=(ROOT/'firmware'/file).read_text(encoding='utf-8')
        needs_reset=False;description=description or 'Define '+file+' in RAM'
    elif action=='exec':
        if not file:raise ValueError('exec requires --file with a local source file')
        path=Path(file).resolve()
        if not path.is_relative_to(ROOT):raise ValueError('Custom source must be inside this workspace')
        code=path.read_text(encoding='utf-8')
        needs_reset=True;description=description or 'Execute '+str(path.relative_to(ROOT))
    else:
        needs_reset,code=ACTIONS[action]
        description=description or action
    if any(c in code for c in '\x01\x02\x03\x04\x05'):
        raise ValueError('Source contains REPL control characters')
    if len(code.encode('utf-8'))>65536:raise ValueError('Source exceeds 64 KiB limit')
    stamp=time.time_ns()
    return {'id':time.strftime('%Y%m%dT%H%M%S',time.gmtime(stamp//1_000_000_000))+f'{stamp%1_000_000_000:09d}'+'-'+uuid.uuid4().hex[:8],
        'action':action,'description':description,'requires_reset':needs_reset,
        'code':code,'sha256':hashlib.sha256(code.encode('utf-8')).hexdigest()}


class RawREPL:
    def __init__(self,port,timeout=30):
        self.port=port;self.timeout=timeout;self.entered=False;self.release_notice=False
        self.echo_lines=False
    def interrupt_to_prompt(self):
        # Explicit operator-requested startup only; never retry an active job.
        self.drain_until_quiet()
        self.port.write(b'\x03')
        time.sleep(.1)
        self.port.write(b'\x03')
        time.sleep(.1)
        self.port.write(b'\x02')
        response=self.drain_until_quiet()
        if b'Traceback' in response or b'KeyboardInterrupt' in response:
            print('Pico interruption output:\n'+response.decode('utf-8','replace'),flush=True)
        if not response.rstrip().endswith(b'>>>'):
            raise TimeoutError('Pico normal REPL prompt was not confirmed; queued jobs were not started')
    def drain_until_quiet(self,quiet=.3):
        deadline=time.monotonic()+min(self.timeout,10)
        last=time.monotonic();data=bytearray()
        while time.monotonic()<deadline:
            byte=self.port.read(1)
            if byte:
                data.extend(byte);last=time.monotonic()
                if len(data)>1048576:raise RuntimeError('Serial startup output exceeded limit')
            elif time.monotonic()-last>=quiet:
                return bytes(data)
        raise TimeoutError('Serial startup output did not become quiet; queued jobs were not started')
    def read_until(self,marker,deadline,limit=1048576):
        data=bytearray()
        while time.monotonic()<deadline:
            byte=self.port.read(1)
            if byte:
                data.extend(byte)
                if self.echo_lines and byte==b'\n':
                    print(data.decode('utf-8','replace').splitlines()[-1],flush=True)
                if not self.release_notice and (data.endswith(b'FS128_RELEASE_RESET\r\n') or data.endswith(b'FS128_RELEASE_RESET\n')):
                    self.release_notice=True
                    print('\nARMED -- RELEASE TS RESET NOW. Filesystem service is armed.',flush=True)
                if data.endswith(marker):return bytes(data[:-len(marker)])
                if len(data)>limit:raise RuntimeError('Serial output exceeded limit')
        raise TimeoutError('Timed out waiting for '+repr(marker)+'; no reset or interrupt was sent')
    def execute(self,source,persistent=False):
        # Ctrl-A enters raw REPL; it does NOT interrupt a running main.py.
        # If the device is not already at REPL, fail rather than send Ctrl-C.
        deadline=time.monotonic()+self.timeout
        self.release_notice=False
        self.port.write(b'\r\x01')
        banner=b'raw REPL; CTRL-B to exit\r\n>'
        self.read_until(banner,deadline)
        self.entered=True
        try:
            payload=source.encode('utf-8')
            for offset in range(0,len(payload),128):
                self.port.write(payload[offset:offset+128]);time.sleep(.002)
            # Ctrl-D is sent ONLY after the raw-REPL banner was confirmed:
            # execute submitted source, not a normal-REPL soft reset.
            self.port.write(b'\x04')
            ack=self.read_until(b'OK',deadline,4096)
            if ack:raise RuntimeError('Unexpected raw REPL acknowledgement: '+repr(ack))
            self.echo_lines=persistent
            stdout=self.read_until(b'\x04',float('inf') if persistent else deadline).decode('utf-8','replace')
            self.echo_lines=False
            if persistent:deadline=time.monotonic()+self.timeout
            stderr=self.read_until(b'\x04',deadline).decode('utf-8','replace')
            self.read_until(b'>',deadline,4096)
            return stdout,stderr
        finally:
            # Ctrl-B returns to normal REPL without rebooting or clearing globals.
            if self.entered:self.port.write(b'\x02');self.entered=False


def parse_result(stdout):
    for line in reversed(stdout.splitlines()):
        try:value=ast.literal_eval(line)
        except (ValueError,SyntaxError):continue
        if isinstance(value,dict):return value
    return None


def serve(args):
    try:import serial
    except ImportError:raise RuntimeError('Install requirements-serial.txt into tools/serial-python')
    root=args.directory
    for name in ('pending','running','results'):(root/name).mkdir(parents=True,exist_ok=True)
    if list((root/'running').glob('*.json')):
        raise RuntimeError('An unfinished running job exists. Inspect it; it will not be replayed automatically.')
    print('Close/disconnect Thonny and Tera Term before continuing.',flush=True)
    if not getattr(args,'interrupt',False):
        print('The Pico must already be at >>>. Use --interrupt for guided Ctrl-C/Ctrl-B startup.',flush=True)
    print('Each queued job requires your Enter key. q cancels; Ctrl-C exits this PC helper.',flush=True)
    with serial.Serial(args.port,115200,timeout=.05,write_timeout=3) as port:
        repl=RawREPL(port,args.timeout)
        if getattr(args,'interrupt',False):
            print('KEEP TS RESET RELEASED. This stops the Pico Python dispatcher; PIO remains running. No reboot or file changes.',flush=True)
            if input('Press Enter to send Ctrl-C twice, then Ctrl-B (q cancels): ').strip().lower()=='q':
                return 0
            repl.interrupt_to_prompt()
            print('Pico >>> confirmed. Continuing with queued jobs.',flush=True)
        print('Connected to '+args.port+'. Waiting for a queued job...',flush=True)
        while True:
            pending=sorted((root/'pending').glob('*.json'))
            if not pending:
                time.sleep(.2);continue
            source=pending[0];running=root/'running'/source.name
            source.rename(running)
            job=json.loads(running.read_text(encoding='utf-8'))
            if hashlib.sha256(job['code'].encode('utf-8')).hexdigest()!=job['sha256']:
                raise RuntimeError('Job source hash differs; leaving running job for inspection')
            result={'id':job['id'],'action':job['action'],'description':job['description'],
                'source_sha256':job['sha256'],'port':args.port,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
            print('\nJOB '+job['id']+': '+job['description'],flush=True)
            if job['requires_reset']:
                if job['action'] in ('fs128-probe-run','fs128-basic-run'):
                    prompt='HOLD TS RESET, press Enter; RELEASE at ARMED, before DONE (q cancels): '
                else:prompt='HOLD TS RESET, then press Enter; keep held until DONE (q cancels): '
            else:prompt='KEEP TS RESET RELEASED. Press Enter to execute (q cancels): '
            if input(prompt).strip().lower()=='q':
                result['status']='cancelled'
            else:
                try:
                    if job['action']=='fs128-basic-run':
                        print('This service stays running while you use Timex BASIC. Ctrl-C stops this PC helper; use --interrupt on the next connection to stop Pico Python.',flush=True)
                    stdout,stderr=repl.execute(job['code'],persistent=True) if job['action'] in PERSISTENT_ACTIONS else repl.execute(job['code'])
                    result.update(stdout=stdout,stderr=stderr,parsed=parse_result(stdout),
                                  status='target_error' if stderr else 'ok')
                except KeyboardInterrupt:
                    if job['action'] in PERSISTENT_ACTIONS:
                        dump(root/'results'/source.name,dict(result,status='pc_detached',
                             note='PC helper stopped; Pico foreground service may still be active. Cold boot or guided --interrupt before restarting.'))
                        running.unlink()
                    raise
                except Exception as exc:
                    result.update(status='transport_error',error=str(exc))
            target=root/'results'/source.name
            dump(target,result);running.unlink()
            # Save before showing DONE so Codex can read the complete result.
            print('DONE -- release TS Reset if held. Result: '+str(target),flush=True)
            if result.get('stdout'):print(result['stdout'],end='',flush=True)
            if result.get('stderr'):print(result['stderr'],end='',flush=True)
            if result.get('error'):print(result['error'],flush=True)
            if result['status'] in ('target_error','transport_error'):
                print('Error recorded. No further jobs will run; helper is disconnecting.',flush=True)
                return 1
            if args.once:return 0
            print('Waiting for next job...',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=DEFAULT_QUEUE)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('ports')
    q=sub.add_parser('queue');q.add_argument('action',choices=(*ACTIONS,'load','exec'))
    q.add_argument('--file');q.add_argument('--description')
    s=sub.add_parser('serve');s.add_argument('--port',required=True)
    s.add_argument('--timeout',type=float,default=30);s.add_argument('--once',action='store_true')
    s.add_argument('--interrupt',action='store_true',help='Prompt before sending Ctrl-C twice and Ctrl-B; require >>> before jobs')
    sub.add_parser('results')
    args=parser.parse_args()
    if args.command=='ports':
        from serial.tools import list_ports
        for port in list_ports.comports():print(port.device,port.description,port.hwid)
    elif args.command=='queue':
        job=make_job(args.action,args.file,args.description)
        path=args.directory/'pending'/(job['id']+'.json');dump(path,job);print(path)
    elif args.command=='results':
        for path in sorted((args.directory/'results').glob('*.json')):
            print(path.name);print(path.read_text(encoding='utf-8'))
    else:return serve(args)
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except KeyboardInterrupt:print('\nPC helper stopped; no target reboot requested.');raise SystemExit(130)
    except Exception as exc:print(str(exc),file=sys.stderr);raise SystemExit(1)
