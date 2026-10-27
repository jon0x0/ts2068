"""Temporary CPU low-ROM data probe. Definitions alone do not touch hardware.

Requires personality128.py and fixed_address128.py in the same REPL globals.
Hold TS Reset only during rom_read_probe128(True); release after return.
After two seconds, collect with Reset RELEASED using the serial helper's
rom-read-live action. Do not press Reset again to collect the samples.
The buffer direction is supplied by hardware; this probe enables U6 during
low-ROM read cycles to observe the CPU data bus. It does not drive data pins.
Normal I/O capture and DMA/address switching are disabled for this test.
"""

ROM_PROBE_SAMPLE_BITS=12


@asm_pio(sideset_init=(PIO.OUT_HIGH,),in_shiftdir=PIO.SHIFT_LEFT)
def _rom_read_probe_program():
    wrap_target()
    wait(0,gpio,13) .side(1)
    jmp(pin,'finish') .side(1)  # GP1 high: not a low-ROM read; skip.
    nop() .side(0) [7]
    in_(pins,12) .side(0) [1]   # Data, A0, direction, U6 /OE, /MREQ.
    in_(pins,12) .side(0)       # Two 12-bit samples in low 24 bits.
    push(noblock) .side(0)
    label('finish')
    wait(1,gpio,13) .side(1)
    wrap()


def rom_read_probe128(host_held_in_reset=False):
    global _rom_probe
    if not host_held_in_reset:
        raise RuntimeError('Hold TS Reset during this call')
    fixed_address128(True)
    _keepalive[2].active(0)  # Main paging SM must not control U6 during probe.
    _rom_read_probe_program[1]=-1
    _rom_read_probe_program[2]=-1
    _rom_probe=StateMachine(1,_rom_read_probe_program,freq=30_000_000,
                           in_base=Pin(2),jmp_pin=Pin(1),sideset_base=Pin(12))
    _rom_probe.active(1)
    return 'ROM-read probe armed; release TS Reset'


def read_rom_probe128(host_held_in_reset=False):
    # Snapshot the count: safe to collect live without an unbounded drain.
    values=[];pairs=[];cycles=[]
    for _ in range(_rom_probe.rx_fifo()):
        word=_rom_probe.get() & 0xffffff
        values.append(hex(word & 255))
        pairs.append((hex((word >> 12)&255),hex(word & 255)))
        cycles.append([{'a0':(v>>8)&1,'direction':(v>>9)&1,
                        'u6_disabled':(v>>10)&1,'mreq':(v>>11)&1}
                       for v in ((word>>12)&4095,word&4095)])
    gpio=mem32[0xd0000004] & 0xffffffff
    return {'first_rom_read_bytes':values,
            'rom_read_samples_early_late':pairs,
            'cycle_signals_early_late':cycles,
            'expected':['0xf3','0x1','0x2b','0x69'],
            'actual_address_nibble':(gpio >> 15) & 15,
            'actual_rom_half':(gpio >> 22) & 1,
            'pio0_enabled':mem32[0x50200000] & 15,
            'pio1_enabled':mem32[0x50300000] & 15}


def rom_trace_arm128(host_held_in_reset=False):
    """Trace 4096 qualified reads, retaining the final 256 in internal Pico RAM.

    DMA channel 1 is available after the personality's exclusive DMA takeover.
    The 1 KiB destination is aligned within a pinned bytearray for DMA wrapping.
    This never writes the Timex SRAM/Flash or the Pico filesystem.
    """
    global _rom_trace_storage,_rom_trace_base,_rom_trace_count
    if not host_held_in_reset:
        raise RuntimeError('Hold TS Reset during this call')
    from uctypes import addressof
    rom_read_probe128(True)
    _rom_trace_storage=bytearray(2047)
    _rom_trace_base=(addressof(_rom_trace_storage)+1023)&~1023
    _rom_trace_count=4096
    # Mask only channel 1 IRQs; no Python IRQ callback is involved.
    for address in (0x50000404,0x50000414):
        mem32[address]=mem32[address]&~2
    mem32[0x50000400]=2
    mem32[0x5000004c]=0x60000000
    mem32[0x50000040]=0x50200024  # PIO0 SM1 RX, DREQ=5.
    mem32[0x50000044]=_rom_trace_base
    mem32[0x50000048]=_rom_trace_count
    # Quiet IRQ, RX1 pacing, chain to self, 1KiB write ring, increment write,
    # fixed read, 32-bit transfers, enable. The source never wraps.
    mem32[0x5000004c]=(1<<21)|(5<<15)|(1<<11)|(1<<10)|(10<<6)|(1<<5)|(2<<2)|1
    return {'trace_armed':True,'transfer_limit':4096,'retained_samples':256}


def rom_trace_read128():
    """Stop probe/trace and collect without pressing host Reset again."""
    _rom_probe.active(0)
    _rom_probe.exec('nop().side(1)')
    ctrl=mem32[0x5000004c]&0xffffffff
    mem32[0x5000004c]=ctrl&0x01fffffe
    _abort_dma(2)
    remaining=mem32[0x50000048]&0xffffffff
    count=(_rom_trace_count-remaining)&0xffffffff
    pointer=mem32[0x50000044]&0xffffffff
    if not _rom_trace_base<=pointer<_rom_trace_base+1024 or pointer&3:
        raise RuntimeError('Unexpected trace DMA destination pointer')
    length=min(count,256)
    first=((pointer-_rom_trace_base)//4) if count>=256 else 0
    words=[hex(mem32[_rom_trace_base+4*((first+i)%256)]&0xffffff) for i in range(length)]
    return {'trace_transfers':count,'remaining':remaining,'retained':length,
            'dma_error_bits':hex(ctrl&0xe0000000),'sample_bits':12,
            'trace_words':words}
