"""Legacy 1.00 service backend, reusing the installed TSPico file handlers.

No filesystem, PIO or SD action happens on import. The gateway supplies an
installed legacy firmware module and a legacy MQ after parking paging PIO.
This backend must never receive a modern SYNC. A 2.3 backend can implement
the same session interface without changing the Spectrum-facing ROM ABI.
"""
try:
    from utime import ticks_ms,ticks_diff,sleep_ms
except ImportError:
    import time
    def ticks_ms():return int(time.monotonic()*1000)
    def ticks_diff(a,b):return a-b
    def sleep_ms(n):time.sleep(n/1000)


LEGACY_100=1
MODERN_23=2
CAP_TAP_LOAD=1
CAP_TAP_SAVE=2
CAP_DIRECTORY=4


def xor_bytes(data):
    result=0
    for value in data:result^=value
    return result


def classify_probe(ack,ready):
    """The skill's cold-loader ACK/MID discriminator; no writes/probing here.

    Caller first sends the valid shared preheader and consumes ACK at 0E.
    FF (floating/idle) is NOT identification. Only a modern MID permits SYNC.
    """
    if ack!=1:raise ValueError('Invalid initial TSPico acknowledgment')
    if ready==0x40:return LEGACY_100
    if ready==0xf7:return MODERN_23
    raise ValueError('Unrecognized TSPico readiness response')


class Legacy100Backend:
    protocol=LEGACY_100
    capabilities=CAP_TAP_LOAD|CAP_TAP_SAVE|CAP_DIRECTORY

    def __init__(self,firmware,timeout_ms=20000):
        required=('MQ','TSP','MOUNT_FILE','ACTIVATE_MQ','SEND_MSG','LOAD_TS','SAVE_TS')
        if any(not hasattr(firmware,name) for name in required):
            raise ValueError('Installed firmware does not expose the legacy handler contract')
        if hasattr(firmware,'MQ_READY'):
            raise ValueError('Status-register firmware requires a verified 2.3 adapter')
        self.firmware=firmware
        self.timeout_ms=timeout_ms
        self.closed=False
        self.requests=0
        self.last_preheader=None
        self.last_command=None

    def _get(self):
        start=ticks_ms()
        while not self.firmware.MQ.rx_fifo():
            if ticks_diff(ticks_ms(),start)>=self.timeout_ms:
                raise RuntimeError('Legacy RX timeout; completed=%d; last_preheader=%r; last_command=%r'%(self.requests,self.last_preheader,self.last_command))
            # The four-word FIFO can fill in under 1 ms at the Z80 driver's
            # byte pacing. Poll continuously, like the stock dispatcher.
        return self.firmware.MQ.get()&255

    def _put(self,value):
        start=ticks_ms()
        while self.firmware.MQ.tx_fifo()>=4:
            if ticks_diff(ticks_ms(),start)>=self.timeout_ms:
                raise RuntimeError('Legacy TX timeout; Z80 stopped consuming the response')
            # Keep up with the cooperative Z80; do not sleep across FIFO slots.
        self.firmware.MQ.put(value)

    def _reply(self,status=1,message=''):
        self.firmware.SEND_MSG(message,'',status)

    def _directory_page(self,text):
        # Cached native listing consists of four 32-column header rows and
        # 32-column entries. End each request before waiting for human input.
        try:page=int(text[12:],16)
        except ValueError:
            self._reply(5,'Invalid directory page');return
        if not 0<=page<=65535:
            self._reply(5,'Directory page out of range');return
        listing=self.firmware.lista
        header=listing[:128]
        entries=listing[128:]
        start=page*448
        data=header+entries[start:start+448]
        more=start+448<len(entries)
        for value in (0x40,0x81,1,ord('+') if more else ord('.')):self._put(value)
        for char in data:
            value=ord(char)
            self._put(value if 32<=value<127 else ord('?'))
        self._put(0)

    def _command(self,pre):
        length=pre[7]|pre[8]<<8
        if not 1<=length<=89:raise ValueError('Legacy command length out of range')
        self._put(0x40);self._put(1)
        body=bytes(self._get() for _ in range(length+4))
        if body[0]!=0x44 or body[1:3]!=bytes((pre[7],pre[8])) or xor_bytes(body):
            raise ValueError('Malformed legacy command body/checksum')
        text=body[3:-1].decode('ascii')
        self.last_command=text
        upper=text.upper()
        if not upper.startswith('TPI:'):
            self._reply(5,'Expected tpi: command');return
        # Native legacy handlers parse offsets into D,length,text (not text alone).
        native_command=body[:-1].decode('latin-1')
        fw=self.firmware
        if pre[1]==0:
            if upper=='TPI:FSEND':
                self._reply();self.closed=True
            elif upper=='TPI:CLOSE':fw.UNMOUNT(pre,native_command)
            elif upper.startswith('TPI:CD '):fw.CDIR(pre,native_command)
            elif upper=='TPI:REW':fw.REW(pre,native_command)
            else:self._reply(5,'Command unavailable in Spectrum filesystem mode')
        elif pre[1]==1:
            if upper.startswith('TPI:DIRPAGE '):self._directory_page(upper)
            elif upper=='TPI:DIR':fw.DIR()
            elif upper=='TPI:PATH':fw.PATH()
            else:
                name=text[4:]
                # Existing legacy listing is authoritative. Match canonical
                # spelling; never interpret a truncated UI name as a path.
                matches=[item for item in fw.files if item.upper()==name.upper()]
                if len(matches)!=1 or not matches[0].upper().endswith('.TAP'):
                    self._reply(5,'Expected one listed TAP file');return
                fw.TSP.f_name=fw.TSP.cur_path+'/'+matches[0]
                fw.MOUNT_FILE();fw.ACTIVATE_MQ()
                self._reply(1,'Mounted '+matches[0])
        else:self._reply(5,'Unsupported command direction')

    def step(self):
        if self.closed:raise RuntimeError('Filesystem session is closed')
        # Stock main loop queues ACK after the first RX byte, before collecting
        # the rest. Keep that sequencing for original 1.00 clients.
        first=self._get();self._put(1)
        partial=bytearray([first])
        try:
            for _ in range(9):partial.append(self._get())
        except RuntimeError:
            raise RuntimeError('Legacy preheader RX timeout after %d bytes: %s'%(len(partial),repr(bytes(partial))))
        pre=bytes(partial)
        self.last_preheader=pre
        if xor_bytes(pre):raise ValueError('Invalid preheader checksum')
        if pre[2]!=255:raise ValueError('Legacy HOME transfer required')
        if pre[0]==0x42:
            self._command(pre)
        elif pre[0] in (0,255) and pre[1] in (1,2,3):
            fw=self.firmware
            fw.MQ,fw.TSP,logs=fw.LOAD_TS(bytearray(pre),fw.MQ,fw.TSP)
            fw.log_entries+=logs
        elif pre[0]==0 and pre[1]==0:
            fw=self.firmware
            import tspico_io as native_io
            # Original SAVE sends its final reply before SD work. Capture
            # that reply so the cooperative client cannot race the write.
            original_end_msg=native_io.END_MSG
            final_reply=[]
            def defer_reply(mq,verbose,message,message1,status):
                final_reply.append((verbose,message,message1,status))
            native_io.END_MSG=defer_reply
            try:
                fw.MQ,fw.TSP,logs=fw.SAVE_TS(fw.MQ,fw.TSP)
                fw.log_entries+=logs
                if final_reply and final_reply[-1][-1]==1:
                    fw.DIR_FILES()
                    import os
                    os.umount('/sd')
                fw.ACTIVATE_MQ()
            finally:
                native_io.END_MSG=original_end_msg
            if not final_reply:raise RuntimeError('Native SAVE returned without a final response')
            for reply in final_reply:original_end_msg(fw.MQ,*reply)
        else:raise ValueError('Unsupported legacy preheader')
        self.requests+=1
        return {'protocol':self.protocol,'requests':self.requests,'closed':self.closed}


def select_backend(protocol,firmware,modern_factory=None):
    if protocol==LEGACY_100:return Legacy100Backend(firmware)
    if protocol==MODERN_23 and modern_factory is not None:
        return modern_factory(firmware)
    raise ValueError('No verified backend for the selected protocol')
