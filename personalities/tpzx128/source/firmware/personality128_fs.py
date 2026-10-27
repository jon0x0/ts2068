"""Filesystem gateway for the stock-sequence 128 adapter (definitions only).

Requires personality128.py and personality128_stock.py in the same namespace.
Only a cooperative Z80 driver with interrupts disabled and a HOME stack may
request service. Stock memory PIO1 stays active. IRQ0=request, IRQ2=locked.
The full Spectrum BASIC hook is separate from this hardware gateway.
"""


@asm_pio(out_init=(PIO.OUT_LOW,),sideset_init=(PIO.OUT_HIGH,),
         in_shiftdir=PIO.SHIFT_LEFT,out_shiftdir=PIO.SHIFT_RIGHT)
def _fs128_latch():
    wrap_target()
    label('idle')
    wait(0,gpio,14) .side(1)
    jmp(pin,'check') .side(1)
    jmp('finish') .side(1)
    label('check')
    mov(osr,pins) .side(1)
    out(null,8) .side(1)
    out(x,1) .side(1)
    jmp(not_x,'service') .side(1)
    mov(isr,null) .side(0) [3]
    in_(pins,8) .side(0)
    mov(osr,isr) .side(0)
    out(x,3) .side(0)
    mov(isr,x) .side(0)
    in_(null,1) .side(0)
    in_(y,4) .side(0)
    push(noblock) .side(0)
    out(null,1) .side(0)
    out(pins,1) .side(0)
    out(x,1) .side(0)
    label('finish')
    wait(1,gpio,14) .side(1)
    jmp(not_x,'idle') .side(1)
    label('locked')
    wait(0,gpio,14) .side(1)
    mov(osr,pins) .side(1)
    out(null,8) .side(1)
    out(x,1) .side(1)
    jmp(not_x,'locked_service') .side(1)
    wait(1,gpio,14) .side(1)
    jmp('locked') .side(1)
    label('locked_service')
    irq(2) .side(1)
    label('service')
    irq(0) .side(1)
    wait(1,gpio,14) .side(1)
    wait(1,irq,1) .side(1)
    jmp('idle') .side(1)
    wrap()


try:
    _fs128_session
except NameError:
    _fs128_session=None


def _fs128_program(half):
    # Preserve GP22's level at StateMachine.init; OUT_LOW would transiently
    # switch ROMs when restoring a session entered from ROM 1.
    program=list(_fs128_latch)
    program[1]=-1;program[2]=-1
    program[5]=(PIO.OUT_HIGH if half else PIO.OUT_LOW,)
    return program


def start_fs128(host_held_in_reset=False,host_parked=False,initial_rom_half=0):
    global _stock128,_fs128_program_live,_fs128_session
    if not (host_held_in_reset or host_parked):raise RuntimeError('Hold TS Reset or use the cooperative HOME handoff')
    reset_stock128(host_held_in_reset,host_parked,initial_rom_half)
    control,address,latch,dma=_stock128
    latch.active(0);dma.active(0)
    Pin(12,Pin.OUT,value=1)
    PIO(0).remove_program()
    mem32[0x50200030]=7  # W1C gateway's internal flags only.
    _fs128_program_live=_fs128_program(initial_rom_half)
    latch=StateMachine(0,_fs128_program_live,freq=30_000_000,in_base=Pin(2),
                       jmp_pin=Pin(11),out_base=Pin(22),sideset_base=Pin(12))
    latch.put(4);latch.exec('pull()');latch.exec('mov(y,osr)')
    ctrl=dma.pack_ctrl(size=2,inc_read=False,inc_write=False,treq_sel=4,high_pri=True)
    dma.config(read=0x50200020,write=0x50300014,count=0xffffffff,ctrl=ctrl,trigger=True)
    _stock128=(control,address,latch,dma)
    _fs128_session=None
    latch.active(1)
    return {'filesystem_gateway':True,'transport':'legacy-1.00',
            'pio0_words':len(_fs128_latch[0]),'entry_port':'0x0e',
            'requires_cooperative_driver':True}


def fs128_enter():
    global _fs128_session
    if _fs128_session is not None:raise RuntimeError('Filesystem session already active')
    flags=mem32[0x50200030]&7
    if not flags&1:raise RuntimeError('No cooperative Z80 service request')
    if _stock128 is None:raise RuntimeError('128 personality inactive')
    control,address,latch,dma=_stock128
    if address.tx_fifo() or latch.rx_fifo():
        raise RuntimeError('Paging transfer still pending; retry after HOME driver fetches')
    latch.active(0);dma.active(0)
    half=(mem32[0xd0000004]>>22)&1
    address.active(0)
    try:
        if address.rx_fifo():raise RuntimeError('Unexpected address RX data')
        address.exec('mov(isr,x)');address.exec('push(noblock)')
        word=address.get()&255
    finally:address.active(1)
    if word&15!=4:raise RuntimeError('Unexpected Spectrum ROM slot')
    _fs128_session={'word':word,'half':half,'locked':bool(flags&4)}
    Pin(22,Pin.OUT,value=half);Pin(12,Pin.OUT,value=1)
    mem32[0x50200030]=7
    PIO(0).remove_program()
    return dict(_fs128_session)


def fs128_leave():
    global _stock128,_fs128_session,_fs128_program_live
    if _fs128_session is None:raise RuntimeError('No filesystem session')
    saved=_fs128_session
    control,address,old_latch,dma=_stock128
    # The caller must have completed the last I/O cycle and parked the Z80
    # in the return gateway before replacing PIO0. Never call during payload.
    if not mem32[0xd0000004]&(1<<14):raise RuntimeError('I/O cycle still active')
    for i in range(4):StateMachine(i).active(0)
    Pin(12,Pin.OUT,value=1)
    for i in range(2,12):Pin(i,Pin.IN)
    PIO(0).remove_program()
    _fs128_program_live=_fs128_program(saved['half'])
    latch=StateMachine(0,_fs128_program_live,freq=30_000_000,in_base=Pin(2),
                       jmp_pin=Pin(11),out_base=Pin(22),sideset_base=Pin(12))
    latch.put(4);latch.exec('pull()');latch.exec('mov(y,osr)')
    if saved['locked']:
        latch.exec('jmp(%d)'%(_fs128_program_live[1]+20))
    # Restore address cache, not only BANK_M: machine-code clients can page
    # without updating Spectrum system variables.
    address.active(0)
    try:
        if address.tx_fifo():raise RuntimeError('Unexpected address TX data during service')
        address.put(saved['word']);address.exec('pull()');address.exec('mov(x,osr)')
    finally:address.active(1)
    # CPU file-service reads drained RX0 while DMA was paused. Its DREQ
    # credit counter does not track those CPU reads; stale credits otherwise
    # replay empty-FIFO data into the address selector (observed 64 writes).
    # RP2040 CH0_DBG_CTDREQ: any write clears credits/restarts handshake.
    mem32[0x50000800]=0
    ctrl=dma.pack_ctrl(size=2,inc_read=False,inc_write=False,treq_sel=4,high_pri=True)
    dma.config(read=0x50200020,write=0x50300014,count=0xffffffff,ctrl=ctrl,trigger=True)
    _stock128=(control,address,latch,dma)
    mem32[0x50200030]=7
    _fs128_session=None
    latch.active(1)
    return {'paging_restored':True,'bank':(saved['word']>>5)&7,
            'rom_half':saved['half'],'locked':saved['locked']}


def _fs128_sd_crc(command,argument):
    crc=0
    for byte in (0x40|command,(argument>>24)&255,(argument>>16)&255,
                 (argument>>8)&255,argument&255):
        for _ in range(8):
            feedback=((byte>>7)^(crc>>6))&1
            crc=((crc<<1)&127)^(9 if feedback else 0)
            byte=(byte<<1)&255
    return (crc<<1)|1


def _fs128_activate_sd(firmware):
    """Temporary native-handler replacement: report errors instead of blinking.

    Called only at an SD transaction boundary. Reuses the installed card driver.
    """
    import os
    from machine import SoftSPI
    firmware.MQ.active(0)
    Pin(12,Pin.OUT,value=1)  # Disconnect host bus before assigning SPI pins.
    # SRAM shares SPI data pins even when the host transceiver is disabled.
    # The cooperative Z80 client MUST execute entirely from HOME RAM here.
    _stock128[0].active(0)
    for pin in (19,20,21):Pin(pin,Pin.OUT,value=1)
    trace=[]
    class TracedCard(firmware.SDCard):
        def cmd(self,command,argument,crc,*args,**kwargs):
            response=super().cmd(command,argument,_fs128_sd_crc(command,argument),*args,**kwargs)
            if len(trace)>=12:trace.pop(0)
            trace.append((command,argument,response))
            return response
        def readinto(self,buffer):
            try:
                return super().readinto(buffer)
            except Exception as error:
                raise RuntimeError('SD data block failed: %r; bytes=%d; last_token=%s; gpio=%s; pio0=%s; pio1=%s'%(
                    error,len(buffer),hex(self.tokenbuf[0]),hex(mem32[0xd0000004]&0xffffffff),
                    hex(mem32[0x50200000]&255),hex(mem32[0x50300000]&255)))
    spi=None
    try:
        spi=SoftSPI(baudrate=100_000,polarity=0,phase=0,
                    sck=Pin(2),mosi=Pin(3),miso=Pin(4))
        # First isolate shared-bus/clock sensitivity from filesystem logic.
        # The installed driver otherwise switches from 100 kHz to 10 MHz
        # immediately before the failing filesystem-sector reads.
        card=TracedCard(spi,Pin(28,Pin.OUT,value=1),baudrate=100_000)
        os.mount(card,'/sd')
        return spi
    except Exception as error:
        if spi is not None:spi.deinit()
        Pin(28,Pin.OUT,value=1)
        raise RuntimeError('SD initialization/mount failed: %r; last (CMD,arg,response): %r'%(error,trace))


def _fs128_resume_memory():
    # Return memory-control pins to PIO1 after SD transfers have finished.
    for pin in (19,20,21):
        address=0x40014004+8*pin
        mem32[address]=(mem32[address]&~31)|7  # RP2040 FUNCSEL PIO1
    _stock128[0].active(1)


def fs128_serve_legacy(wait_ms=30000,firmware=None,bootstrap=None):
    """One cooperative legacy session, then restore paging.

    This initial runner is for TPZXFST.ROM, whose stack is fixed HOME and
    whose return path retains the existing legacy settle guard. A general
    Spectrum BASIC return gateway still needs integration and validation.
    """
    from utime import ticks_ms,ticks_diff,sleep_ms
    if firmware is None:
        import tspico as firmware
    import tspico_io as native_io
    TS_IO=native_io.TS_IO
    # Validate the backend before suspending any working PIO.
    backend=Legacy100Backend(firmware)
    if len(TS_IO[0])>32:raise RuntimeError('Installed legacy I/O program exceeds PIO0')
    started=ticks_ms()
    while not mem32[0x50200030]&1:
        if wait_ms is not None and ticks_diff(ticks_ms(),started)>=wait_ms:
            raise RuntimeError('No Z80 filesystem request; paging remains active')
        sleep_ms(1)
    saved=fs128_enter()
    original_activate_sd=firmware.ACTIVATE_SD
    original_activate_mq=firmware.ACTIVATE_MQ
    original_ena_sd=native_io.ENA_SD
    original_ena_mq=native_io.ENA_MQ
    try:
        firmware.ACTIVATE_SD=lambda:_fs128_activate_sd(firmware)
        def resume_mq():
            _fs128_resume_memory()
            return original_activate_mq()
        firmware.ACTIVATE_MQ=resume_mq
        # Native SAVE calls its module's helpers, not tspico.ACTIVATE_SD.
        # Keep that path on the same exclusive bus handoff too.
        native_io.ENA_SD=lambda:firmware.ACTIVATE_SD()
        def resume_native_mq(mq):
            firmware.ACTIVATE_MQ()
            return firmware.MQ
        native_io.ENA_MQ=resume_native_mq
        TS_IO[1]=-1;TS_IO[2]=-1
        firmware.ACTIVATE_MQ()
        # Explicit gateway greeting, not a floating-bus/version guess.
        for value in (0xa5,backend.protocol,backend.capabilities,1 if bootstrap is not None else 0):
            firmware.MQ.put(value)
        if bootstrap is not None:
            for value in (len(bootstrap)&255,len(bootstrap)>>8):firmware.MQ.put(value)
            checksum=0
            for value in bootstrap:
                firmware.MQ.put(value)
                checksum^=value
            firmware.MQ.put(checksum)
        while not backend.closed:backend.step()
        deadline=ticks_ms()
        while firmware.MQ.tx_fifo() or not mem32[0xd0000004]&(1<<14):
            if ticks_diff(ticks_ms(),deadline)>1000:
                raise RuntimeError('Final file I/O cycle did not complete')
        restore_started=ticks_ms()
        result=fs128_leave()
        result.update(protocol=backend.protocol,requests=backend.requests,
                      restore_ms=ticks_diff(ticks_ms(),restore_started),
                      saved_bank=(saved['word']>>5)&7)
        return result
    except Exception:
        # Do not pretend an incomplete protocol/SD transaction is a clean
        # return to Spectrum execution. Preserve the snapshot for diagnosis.
        StateMachine(0).active(0)
        Pin(12,Pin.OUT,value=1)
        raise
    finally:
        firmware.ACTIVATE_SD=original_activate_sd
        firmware.ACTIVATE_MQ=original_activate_mq
        native_io.ENA_SD=original_ena_sd
        native_io.ENA_MQ=original_ena_mq


def fs128_run_basic():
    """Foreground temporary BASIC service; Ctrl-C stops it without file changes.

    Core 1 is deliberately left for the installed native SAVE watchdog.
    The host must run TPZXSD.ROM, with protected HOME service RAM.
    """
    if not isinstance(FS128_BASIC_IMAGE,bytes):raise RuntimeError('Load fs128_image.py definitions first')
    print('TSPico Spectrum 128 SD service ready; enter BASIC commands on the Timex')
    while True:
        print(fs128_serve_legacy(wait_ms=None,bootstrap=FS128_BASIC_IMAGE))
