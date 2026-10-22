"""Optional TSPico 2.3 extension: directory or image-backed CP/M sectors.

No firmware is installed by the project build. Merge EXT_SA_FUNCT into an
existing dev_extcmd.py; do not replace somebody else's command dictionary.
"""
try:
    import dev_tspico as tp
except ImportError:
    import TS.tspico as tp
from TS import catalog
from cpm_directory import DirectoryVolume, filename
from cpm_tap import TapVolume, save_tap
from cpm_dsk import DskVolume, save_dsk

try:
    from cpm_config import CPM_DIRECTORY, CPM_STORAGE
except ImportError:
    CPM_DIRECTORY = '/CPM/FILES'
    CPM_STORAGE = 'directory'
STORAGE = CPM_STORAGE
try:
    from cpm_config import CPM_DIRECTORY_KB
except ImportError:
    CPM_DIRECTORY_KB=256
if CPM_DIRECTORY_KB not in (256,320):raise ValueError('unsupported directory geometry')

IMAGE = '/CPM/DRIVEA.IMG'
SIZE = 49152
try:
    from cpm_config import CPM_IMAGE_PATH, CPM_IMAGE_SIZE
    IMAGE, SIZE = CPM_IMAGE_PATH, CPM_IMAGE_SIZE
except ImportError:
    pass
if SIZE not in (49152, 163840, 327680):
    raise ValueError('unsupported CP/M image geometry')
SIGNATURE = b'CPM1\x01\x80' + bytes((SIZE//128 & 255, SIZE//32768))
_pending = None
_directory = None
_tap = None
_storage = None

def _kind():
    return _storage or STORAGE

def _sectors():
    if _kind()=='tap':return _tap.sectors
    return CPM_DIRECTORY_KB*8 if _kind() == 'directory' else SIZE//128

def _new_directory(tsp):
    root=catalog.resolve(tsp.cur_path,CPM_DIRECTORY)
    if root is None:raise OSError('invalid CP/M directory')
    return DirectoryVolume(root,CPM_DIRECTORY_KB*1024,1024 if CPM_DIRECTORY_KB==256 else 2048)

def _path(tsp):
    real = catalog.resolve(tsp.cur_path, IMAGE)
    if not real:
        raise OSError('invalid image path')
    return real

def _open(tsp, mode):
    f = open(_path(tsp), mode)
    f.seek(0, 2)
    if f.tell() != SIZE:
        f.close()
        raise OSError('wrong CP/M image size')
    return f

def _status(code):
    tp.CMD_PUT(code)
    tp.MQ_READY()

def _packet(data):
    # Use the firmware's proven channel-read framing and DMA machinery.
    out = bytearray(len(data) + 3)
    out[0] = 1
    out[1] = len(data)
    out[2:-1] = data
    x = 0
    for b in data:
        x ^= b
    out[-1] = x
    if tp.tspico_io.CAN_STREAM():
        tp._CMD_ECHO[0] = 0
        # CH_READY also disables command echo while the data phase runs.
        result = tp.STREAM_DMA(tp.MQ, out, tp._CMD_ECHO, tp.CMD_STALL_MS, tp.CH_READY)
        if result is not None:
            if result[0]:
                raise tp.CmdAbort(result[0])
            return
    tp.CMD_PUT(out[0]); tp.CMD_PUT(out[1]); tp.CH_READY()
    for b in out[2:]:
        tp.CMD_PUT(b)

def CAP(mq, tsp, pre, cmd):
    global _pending, _directory, _tap, _storage
    _pending = None
    _directory = None
    _tap=None;_storage=STORAGE
    def check():
        global _directory,_tap,_storage
        if STORAGE == 'directory':
            _directory = _new_directory(tsp)
            return _directory.signature
        if STORAGE in ('dsk','tap'):
            volume=(DskVolume if STORAGE=='dsk' else TapVolume)(_path(tsp))
            _tap=volume;_storage='tap'
            return b'CPM1\x01\x80'+bytes((volume.sectors&255,volume.sectors>>8))
        if STORAGE != 'image':
            raise OSError('unknown CP/M storage configuration')
        with _open(tsp, 'rb'):
            pass
        # Opening r+b checks that this image is writable, without changing it.
        with _open(tsp, 'r+b'):
            pass
        return SIGNATURE
    value, status = tp.CH_CALL(check)
    if status != 1:
        _status(status); return
    _packet(value)

def READ(mq, tsp, pre, cmd):
    global _pending
    _pending = None
    lba, _ = tp.PARAMS(pre)
    if not 0 <= lba < _sectors():
        _status(6); return
    def read():
        if _kind()=='tap':return _tap.read(lba)
        if _kind() == 'directory':
            if _directory is None:
                raise OSError('mount CP/M directory first')
            return _directory.read(lba)
        with _open(tsp, 'rb') as f:
            f.seek(lba * 128)
            data = f.read(128)
        if len(data) != 128:
            raise OSError('short sector')
        return data
    value, status = tp.CH_CALL(read)
    if status != 1:
        _status(status); return
    _packet(value)

def _decode(pre, cmd):
    lba, _ = tp.PARAMS(pre)
    text = tp.getArgs(cmd).strip()
    if not 0 <= lba < _sectors() or len(text) != 128:
        raise ValueError('invalid sector or half length')
    return lba, bytes(int(text[i:i+2], 16) for i in range(0, 128, 2))

def WRITE0(mq, tsp, pre, cmd):
    global _pending
    _pending = None
    try:
        _pending = _decode(pre, cmd)
    except ValueError:
        _status(5); return
    _status(1)

def WRITE1(mq, tsp, pre, cmd):
    global _pending
    pending = _pending
    _pending = None
    try:
        lba, data = _decode(pre, cmd)
        if pending is None or pending[0] != lba:
            raise ValueError('missing/mismatched first half')
        data = pending[1] + data
    except ValueError:
        _status(5); return
    def write():
        if _kind()=='tap':return _tap.write(lba,data)
        if _kind() == 'directory':
            if _directory is None:
                raise OSError('mount CP/M directory first')
            _directory.write(lba, data)
            return None
        with _open(tsp, 'r+b') as f:
            f.seek(lba * 128)
            if f.write(data) != 128:
                raise OSError('short sector write')
            f.flush()
        return None
    _, status = tp.CH_CALL(write)
    _status(status)

def _tap_path(tsp,argument):
    argument=argument.strip().upper()
    directory='/CPM/'
    if argument.startswith('SAVE/'):
        directory='/CPM/SAVE/'
        argument=argument[5:]
    name=filename(argument)
    if name is None or not name.endswith(('.TAP','.DSK')):raise OSError('use an 8.3 TAP or DSK filename')
    path=catalog.resolve(tsp.cur_path,directory+name)
    if path is None:raise OSError('invalid TAP path')
    return path

def MOUNT(mq,tsp,pre,cmd):
    global _pending,_directory,_tap,_storage
    _pending=None
    def mount():
        global _directory,_tap,_storage
        argument=tp.getArgs(cmd).strip()
        if argument.upper()=='DIR':
            if CPM_DIRECTORY_KB!=320:raise OSError('CPMDISK requires the 320KB directory configuration')
            volume=_new_directory(tsp)
            _directory=volume;_tap=None;_storage='directory'
        else:
            path=_tap_path(tsp,argument)
            volume=(DskVolume if argument.upper().endswith('.DSK') else TapVolume)(path)
            _tap=volume;_storage='tap'
    _,status=tp.CH_CALL(mount);_status(status)

def SAVE(mq,tsp,pre,cmd):
    global _pending
    _pending=None
    def save():
        if _sectors() not in (1280,2560):raise OSError('unsupported export geometry')
        if _kind()=='directory':volume=_directory
        elif _kind()=='tap':volume=_tap
        else:
            class ImageReader:
                sectors=SIZE//128
                def read(self,lba):
                    with _open(tsp,'rb') as f:
                        f.seek(lba*128);return f.read(128)
            volume=ImageReader()
        if volume is None:raise OSError('mount volume before SAVE')
        path=_tap_path(tsp,tp.getArgs(cmd))
        (save_dsk if path.upper().endswith('.DSK') else save_tap)(volume,path)
    _,status=tp.CH_CALL(save);_status(status)

def INFO(mq,tsp,pre,cmd):
    count=_sectors()
    _packet(b'CPM1\x01\x80'+bytes((count&255,count>>8)))

EXT_SA_FUNCT = {'TPI:.CPMCAP': CAP, 'TPI:.CPMRD': READ,
                'TPI:.CPMW0': WRITE0, 'TPI:.CPMW1': WRITE1,
                'TPI:.CPMMOUNT': MOUNT,'TPI:.CPMSAVE': SAVE, 'TPI:.CPMINFO': INFO}
