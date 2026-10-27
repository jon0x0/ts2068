"""Temporary legacy-stock -> 128 HOME handoff. Definitions only.

The Z80 trampoline disables interrupts, unmaps DOCK, moves its stack to HOME,
and sends H1/mode/checksum on port 14. Only this handshake authorizes takeover.
No physical reset, firmware files, configuration, or SD writes are performed.
Call only from the normal Timex legacy dispatcher stopped at the USB REPL.
"""

def _handoff128_wait(predicate,timeout_ms=1000):
    import time
    started=time.ticks_ms()
    while not predicate():
        if time.ticks_diff(time.ticks_ms(),started)>=timeout_ms:
            raise RuntimeError('HOME handoff timed out; cold boot to recover')


def handoff128_wait(mode,resume=False):
    import time
    import tspico
    if mode not in ('zx128','zx128sd'):raise ValueError('Unknown trial mode')
    if _stock128 is not None:raise RuntimeError('Start this trial from normal Timex/TSPico, not a running 128 mode')
    if getattr(tspico.TSP,'zx48',False):raise RuntimeError('Leave ZX48 mode first')
    mq=tspico.MQ
    pending=mq.rx_fifo()
    if mq.tx_fifo() or (pending and not resume):raise RuntimeError('Stock FIFO is not idle; no takeover performed')
    if resume and pending!=4:raise RuntimeError('Resume requires exactly four queued trampoline bytes; no takeover performed')
    enabled=mem32[0x50300000]&15
    # PIO1 local SM0/SM1 are global StateMachine(4)/(5).
    if enabled&3!=3:raise RuntimeError('Expected stock memory SM4/SM5 active; PIO1 enable='+hex(enabled))
    expected=1 if mode=='zx128' else 2
    packet=(0x48,0x31,expected,0x48^0x31^expected)
    index=0
    if resume:print('Resuming queued HOME handoff; keep TS Reset RELEASED. Do not run USR again.')
    else:print('HOME handoff armed for '+mode+'. Keep TS Reset RELEASED; run RANDOMIZE USR 32768.')
    while index<len(packet):
        if not mq.rx_fifo():
            time.sleep_ms(1)
            continue
        value=mq.get()&0x1ff
        if value!=packet[index]:
            raise RuntimeError('Unexpected handoff byte '+hex(value)+'; stock mapping was not changed')
        index+=1
    # The request was emitted only after DI, F4=0, FF=0, and a HOME stack.
    # Stop memory service with DOCK unmapped, before acknowledging the host.
    _handoff128_wait(lambda:bool(mem32[0xd0000004]&(1<<14)))
    StateMachine(4).active(0);StateMachine(5).active(0)
    for pin in (19,20,21):Pin(pin,Pin.OUT,value=1)
    Pin(22,Pin.OUT,value=1)  # ROM 1 boot gate; ROM 0 must remain hidden.
    mq.put(0xa7)
    _handoff128_wait(lambda:mq.tx_fifo()==0)
    _handoff128_wait(lambda:bool(mem32[0xd0000004]&(1<<14)))
    mq.active(0)
    Pin(12,Pin.OUT,value=1)
    if mode=='zx128sd':
        result=start_fs128(host_parked=True,initial_rom_half=1)
    else:
        result=start_stock128(host_parked=True,initial_rom_half=1)
    # All PIO/DMA setup is complete. The host is polling ROM from HOME,
    # not issuing selected I/O. Release the gate with an injected OUT.
    latch=_stock128[2]
    latch.exec('mov(osr,null)')
    latch.exec('out(pins,1)')
    print({'handoff':'ROM 0 released','mode':mode,'physical_reset':False})
    if mode=='zx128sd':
        fs128_run_basic()
    return result


@asm_pio(sideset_init=(PIO.OUT_HIGH,),in_shiftdir=PIO.SHIFT_LEFT)
def _handoff128_rom_probe():
    wrap_target()
    wait(0,gpio,13) .side(1)
    jmp(pin,'finish') .side(1)
    nop() .side(0) [7]
    in_(pins,25) .side(0)  # GP2..26: data, address mux, enables, half, ROSCS.
    push(noblock) .side(0)
    label('finish')
    wait(1,gpio,13) .side(1)
    wrap()


def handoff128_probe_arm(host_held_in_reset=False):
    global _handoff128_probe
    if not host_held_in_reset:raise RuntimeError('Hold TS Reset only while arming ROM probe')
    if _stock128 is None:raise RuntimeError('No 128 memory controller to inspect')
    # Preserve the existing PIO1 memory/address controllers. Replace only the
    # paging observer with a passive ROM data sampler; never drive data pins.
    _stock128[2].active(0);_stock128[3].active(0)
    Pin(12,Pin.OUT,value=1);Pin(22,Pin.OUT,value=0)
    PIO(0).remove_program()
    _handoff128_rom_probe[1]=-1;_handoff128_rom_probe[2]=-1
    _handoff128_probe=StateMachine(1,_handoff128_rom_probe,freq=30_000_000,
                                 in_base=Pin(2),jmp_pin=Pin(1),sideset_base=Pin(12))
    _handoff128_probe.active(1)
    return 'ROM probe armed; release TS Reset at DONE. No further reset for collection.'


def handoff128_probe_read():
    samples=[]
    for _ in range(_handoff128_probe.rx_fifo()):
        value=_handoff128_probe.get()&0x1ffffff
        samples.append({'data':hex(value&255),'a0':(value>>8)&1,
                        'address_nibble':(value>>13)&15,'enables':(value>>17)&7,
                        'rom_half':(value>>20)&1,'roscs':(value>>24)&1,
                        'u6_disabled':(value>>10)&1,'mreq':(value>>11)&1})
    return {'first_rom_reads':samples,'expected_data':['0xf3','0x1','0x2b','0x69'],
            'memory_controller_preserved':True,'paging_disabled_for_probe':True}
