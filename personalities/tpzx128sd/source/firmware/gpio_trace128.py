"""Input-only Pico GPIO timeline using internal RAM. No target file writes.

Load definitions with reset released. Hold TS Reset for gpio_trace_arm128(True),
release at DONE, wait two seconds, collect gpio_trace_read128() WITHOUT reset.
The inactive main paging program is removed to free PIO0 instruction space;
the ordinary personality reset reloads it. CPU-memory probe stays active.
"""


@asm_pio(autopush=True,push_thresh=32,in_shiftdir=PIO.SHIFT_LEFT)
def _gpio_trace_program():
    wait(0,gpio,13)             # Trigger only when the CPU resumes memory cycles.
    wrap_target()
    label('sample')
    in_(pins,32)               # Autopush full GPIO snapshot.
    jmp(x_dec,'sample')        # X preloaded with sample count minus one.
    label('done')
    jmp('done')                # Stop producing after exactly the DMA count.
    wrap()


def gpio_trace_arm128(host_held_in_reset=False):
    global _gpio_trace_storage,_gpio_trace_base,_gpio_trace_count,_gpio_trace_sm
    if not host_held_in_reset:
        raise RuntimeError('Hold TS Reset during this call')
    from uctypes import addressof
    rom_read_probe128(True)
    PIO(0).remove_program(paging_write)  # Already inactive; leave ROM probe intact.
    _gpio_trace_program[1]=-1
    _gpio_trace_program[2]=-1
    _gpio_trace_sm=StateMachine(2,_gpio_trace_program,freq=60_000_000,in_base=Pin(0))
    _gpio_trace_count=8192
    _gpio_trace_sm.put(_gpio_trace_count-1)
    _gpio_trace_sm.exec('pull()')
    _gpio_trace_sm.exec('mov(x,osr)')
    _gpio_trace_storage=bytearray(8191)
    _gpio_trace_base=(addressof(_gpio_trace_storage)+4095)&~4095
    for address in (0x50000404,0x50000414):mem32[address]=mem32[address]&~4
    mem32[0x50000400]=4
    mem32[0x5000008c]=0x60000000
    mem32[0x50000080]=0x50200028  # PIO0 SM2 RX, DREQ=6.
    mem32[0x50000084]=_gpio_trace_base
    mem32[0x50000088]=_gpio_trace_count
    mem32[0x50200008]=1<<18     # Clear only SM2 RXSTALL before capture.
    mem32[0x5000008c]=(1<<21)|(6<<15)|(2<<11)|(1<<10)|(12<<6)|(1<<5)|(2<<2)|1
    _gpio_trace_sm.active(1)
    return {'gpio_trace_armed':True,'sample_count':8192,'retained':1024,
            'nominal_sample_interval_ns':1000000000*2/60000000}


def gpio_trace_read128():
    if 'gpio_trace_stream128' not in globals():
        raise RuntimeError('Load gpio_trace_stream128.py before collection')
    return gpio_trace_stream128()
