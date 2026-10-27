"""Stream an existing GPIO capture in 64-byte chunks; no new capture needed."""


def gpio_trace_stream128():
    import gc,struct,binascii
    gc.collect()
    _gpio_trace_sm.active(0)
    _rom_probe.active(0)
    _rom_probe.exec('nop().side(1)')
    ctrl=mem32[0x5000008c]&0xffffffff
    mem32[0x5000008c]=ctrl&0x01fffffe
    _abort_dma(4)
    remaining=mem32[0x50000088]&0xffffffff
    count=(_gpio_trace_count-remaining)&0xffffffff
    pointer=mem32[0x50000084]&0xffffffff
    if not _gpio_trace_base<=pointer<_gpio_trace_base+4096 or pointer&3:
        raise RuntimeError('Unexpected GPIO trace DMA destination pointer')
    length=min(count,1024)
    first=(pointer-_gpio_trace_base)//4 if count>=1024 else 0
    block=bytearray(64)
    for offset in range(0,length,16):
        size=min(16,length-offset)
        for j in range(size):
            word=mem32[_gpio_trace_base+4*((first+offset+j)%1024)]&0xffffffff
            struct.pack_into('<I',block,j*4,word)
        print('GPIO128',offset,binascii.hexlify(block[:size*4]).decode())
        gc.collect()
    return {'gpio_trace_transfers':count,'retained':length,'remaining':remaining,
            'dma_error_bits':hex(ctrl&0xe0000000),
            'rx_stall':bool(mem32[0x50200008]&(1<<18)),
            'sample_interval_ns':1000000000*2/60000000,
            'stream_format':'gpio128-le-u32'}
