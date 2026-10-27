"""Define a diagnostic for an already-running personality128.py session.

Pasting this file only defines a function. Hold TS Reset briefly while calling
inspect128(True), then release it after the call returns. No filesystem writes.
The call pauses the address SM and uses its otherwise-unused ISR/RX FIFO to
copy X out. It preserves X, OSR, Y and the program counter. This is an active
PIO diagnostic, not a purely read-only register dump.
"""


def inspect128(host_held_in_reset=False):
    if not host_held_in_reset:
        raise RuntimeError('Hold TS Reset during this diagnostic call')
    if _keepalive is None:
        raise RuntimeError('No active personality in this Python session')
    address = _keepalive[1]
    was_active = address.active()
    address.active(0)
    try:
        if address.rx_fifo():
            raise RuntimeError('Unexpected address RX data; leaving it untouched')
        address.exec('mov(isr,x)')
        address.exec('push(noblock)')
        word = address.get() & 0xffffffff
        gpio = mem32[0xd0000004] & 0xffffffff
        execctrl = mem32[0x502000cc] & 0xffffffff
        bottom = (execctrl >> 7) & 31
        pc = mem32[0x502000d4] & 31
        remaining = mem32[0x50000008] & 0xffffffff
        trace = globals().get('PAGING_TRACE_BYTES', False)
        lock_start = 20 if trace else 21
        result = {
            'last_applied_word': hex(word),
            'last_applied_bank': (word >> 5) & 7,
            'last_captured_byte': hex((word >> 8) & 255) if trace else None,
            'word_rom_slot': word & 15,
            'rom_half_pin': (gpio >> 22) & 1,
            'paging_program_base': bottom,
            'paging_pc': pc,
            'paging_relative_pc': (pc - bottom) & 31,
            'paging_locked_loop': ((pc - bottom) & 31) in (lock_start,lock_start+1,lock_start+2),
            'address_pending_words': address.tx_fifo(),
            'dma_transfers': (0xffffffff - remaining) & 0xffffffff,
            'dma_control': hex(mem32[0x5000000c] & 0xffffffff),
            'paging_clock_divider': hex(mem32[0x502000c8] & 0xffffffff),
        }
        observer=globals().get('_observer')
        if observer is not None:
            samples=[]
            while observer.rx_fifo():
                pair=observer.get() & 65535
                samples.append((hex(pair >> 8),hex(pair & 255)))
            result['first_write_samples_early_late']=samples
    finally:
        address.active(was_active)
    return result
