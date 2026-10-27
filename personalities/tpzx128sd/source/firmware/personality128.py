"""Experimental V2.2 native-128 paging personality for RP2040 MicroPython.

Enter ONLY with the host held in reset and patched ROM pair preinstalled in a
chosen memory slot. Replaces normal TSPico file-service PIO. No SD or status I/O.
Pin map follows the original V2.2 schematic, not inferred firmware pin names.
"""
from machine import Pin, freq, mem32
from rp2 import PIO, StateMachine, asm_pio
import sys as _sys
try:
    from rp2 import DMA as _NativeDMA
except ImportError:
    _NativeDMA = None


def _abort_dma(mask):
    mem32[0x50000444] = mask
    for _ in range(100000):
        if not mem32[0x50000444]:
            return
    raise RuntimeError('DMA abort timed out; keep TS Reset held and power cycle')


class _RegisterDMA:
    """Channel 0 bridge ONLY for this exclusive takeover, not a DMA allocator.

    Construction does not touch hardware. start() stops every existing channel
    before config(). Register layout follows the RP2040 SDK hardware/regs/dma.h.
    """
    def __init__(self):
        if 'RP2040' not in getattr(_sys.implementation, '_machine', ''):
            raise RuntimeError('Register DMA backend requires RP2040')
        self.closed = False

    def pack_ctrl(self, size, inc_read, inc_write, treq_sel, high_pri):
        if (size, inc_read, inc_write, treq_sel) != (2, False, False, 4):
            raise ValueError('Only the personality PIO FIFO bridge is supported')
        # IRQ_QUIET, PIO0 RX0 DREQ, chain-to-self (channel 0), word transfers.
        return (1 << 21) | (4 << 15) | (int(high_pri) << 1) | (2 << 2) | 1

    def config(self, read, write, count, ctrl, trigger=False):
        if self.closed:
            raise RuntimeError('DMA is closed')
        if (read, write, count) != (0x50200020, 0x50300014, 0xffffffff):
            raise ValueError('Unexpected personality DMA endpoints')
        mem32[0x5000000c] = 0x60000000  # Disable; clear read/write error flags (W1C).
        mem32[0x50000000] = read
        mem32[0x50000004] = write
        mem32[0x50000008] = count
        mem32[0x5000000c] = (ctrl & ~1) | int(bool(trigger))

    def active(self, value=None):
        if self.closed:
            raise RuntimeError('DMA is closed')
        if value is None:
            return bool(mem32[0x5000000c] & (1 << 24))
        if value:
            raise ValueError('Start the bridge with config(trigger=True)')
        mem32[0x5000000c] = mem32[0x5000000c] & ~1

    def close(self):
        if not self.closed:
            self.active(0)
            _abort_dma(1)
            self.closed = True


DMA = _NativeDMA if _NativeDMA is not None else _RegisterDMA
DMA_BACKEND = 'rp2.DMA' if _NativeDMA is not None else 'RP2040 registers'
PAGING_TRACE_BYTES = True
# Match the stock V2 I/O controller's clock, rather than its faster memory SMs.
# The first hardware trial used the memory clock here and captured bad bytes.
PAGING_FREQ = 30_000_000


@asm_pio(set_init=(PIO.OUT_HIGH,)*3,out_shiftdir=PIO.SHIFT_RIGHT)
def memory_enable():
    # set_base=19: flash /CE, SRAM /CE, /BE. GP22 belongs to the paging SM.
    wrap_target()
    set(pins,7)
    wait(0,gpio,13)
    jmp(pin,'rom')                 # GPIO26 /ROSCS: 0 DOCK, 1 non-DOCK
    nop() [10]                    # Allow address-selector SM to settle before SRAM /CE.
    set(pins,5)                   # Flash off, SRAM on, HOME suppression unnecessary.
    jmp('finish')
    label('rom')
    mov(osr,pins)
    out(null,1)
    out(x,1)                      # GP1 = A14 OR A15 OR /RD
    jmp(x_dec,'finish')            # No external ROM response outside low-16K reads.
    set(pins,3)                   # /BE low; both external chips still disabled.
    nop() [10]
    set(pins,2)                   # Flash on, SRAM off, internal ROM disabled.
    label('finish')
    wait(1,gpio,13)
    wrap()


@asm_pio(set_init=(PIO.OUT_HIGH,)*3,out_shiftdir=PIO.SHIFT_RIGHT)
def memory_enable_sram():
    # set_base=19: flash /CE, SRAM /CE, /BE. GP22 belongs to the paging SM.
    wrap_target()
    set(pins,7)
    wait(0,gpio,13)
    jmp(pin,'rom')                 # GPIO26 /ROSCS: 0 DOCK, 1 non-DOCK
    nop() [10]                    # Allow address-selector SM to settle before SRAM /CE.
    set(pins,5)                   # Flash off, SRAM on, HOME suppression unnecessary.
    jmp('finish')
    label('rom')
    mov(osr,pins)
    out(null,1)
    out(x,1)                      # GP1 = A14 OR A15 OR /RD
    jmp(x_dec,'finish')            # No external ROM response outside low-16K reads.
    set(pins,3)                   # /BE low; both external chips still disabled.
    nop() [10]
    set(pins,1)                   # Flash off, SRAM on, internal ROM disabled.
    label('finish')
    wait(1,gpio,13)
    wrap()


@asm_pio(out_init=(PIO.OUT_LOW,)*4, out_shiftdir=PIO.SHIFT_RIGHT)
def memory_address():
    # TX words: captured byte in bits 8-15 (diagnostic), dock nibble in
    # bits 4-7, ROM slot in bits 0-3. Address output ignores the high byte.
    # Pull AFTER the request starts, avoiding a stale word cached before an OUT.
    wrap_target()
    wait(0,gpio,13)
    pull(noblock)
    mov(x,osr)
    jmp(pin,'rom')
    out(null,4)
    out(pins,4)
    jmp('finish')
    label('rom')
    out(pins,4)
    label('finish')
    wait(1,gpio,13)
    wrap()


@asm_pio(out_init=(PIO.OUT_LOW,), sideset_init=(PIO.OUT_HIGH,),
         in_shiftdir=PIO.SHIFT_LEFT, out_shiftdir=PIO.SHIFT_RIGHT)
def paging_write():
    # in_base=2 D0..D7; out_base=22 ROM half; sideset_base=12 U6 /OE.
    # Y is the immutable Flash slot. X temporarily holds address bit 0 or lock.
    wrap_target()
    label('idle')
    wait(0,gpio,14) .side(1)
    jmp(pin,'check') .side(1)       # GPIO11: 1 on selected I/O writes
    jmp('ignore') .side(1)         # No read/status response in this personality.
    label('check')
    mov(osr,pins) .side(1)
    out(null,8) .side(1)           # MOV PINS is rotated by IN_BASE=2, like IN PINS.
    out(x,1) .side(1)              # GP10 = CPU A0, bit 8 of the rotated input bus
    jmp(not_x,'ignore') .side(1)    # Only odd writes: normal usage is port 0F.
    nop() .side(0) [2]             # Enable host -> Pico data buffer, then settle.
    mov(isr,null) .side(0)
    in_(pins,8) .side(0)
    mov(osr,isr) .side(0)
    out(null,4) .side(0)
    out(pins,1) .side(0)           # 7FFD bit 4 -> GP22 -> ROM A14 through U8.
    out(x,1) .side(0)              # 7FFD bit 5 -> lock
    # ISR still holds the exact captured byte; retain it above the address bits.
    in_(pins,3) .side(0)           # RAM bank bits 0-2
    in_(null,1) .side(0)           # Even DOCK slot = bank * 2
    in_(y,4) .side(0)              # Word = (captured_byte << 8) | (bank << 5) | slot
    push(noblock) .side(0)         # Hardware DMA forwards this to memory_address TX.
    wait(1,gpio,14) .side(1)
    jmp(not_x,'idle') .side(1)
    label('locked')
    wait(1,gpio,14) .side(1)
    wait(0,gpio,14) .side(1)
    jmp('locked') .side(1)
    label('ignore')
    wait(1,gpio,14) .side(1)
    jmp('idle') .side(1)
    wrap()


@asm_pio(in_shiftdir=PIO.SHIFT_LEFT)
def paging_observer():
    # Input-only probe: first four selected writes, early and later samples.
    # No output pins, buffer control, FIFO bridge or paging effect.
    wrap_target()
    wait(0,gpio,14)
    jmp(pin,'capture')
    jmp('finish')
    label('capture')
    mov(isr,null)
    in_(pins,8) [7]
    in_(pins,8)
    push(noblock)
    label('finish')
    wait(1,gpio,14)
    wrap()


# Re-pasting definitions into an active REPL must retain the running objects.
# reset() can then stop the OLD program and start the newly assembled one.
try:
    _keepalive
except NameError:
    _keepalive=None
try:
    _observer
except NameError:
    _observer=None


def start(rom_slot, host_held_in_reset=False, rom_memory="flash"):
    """Replace stock PIO. Caller must hold host reset throughout this call.

    A TS Reset does not reset the Pico latch: call reset() with the host held
    in reset for EVERY cold/recovery reset, especially after entering 48 BASIC.
    """
    global _keepalive, _observer
    if not host_held_in_reset:
        raise RuntimeError('Hold TS2068 reset before replacing memory-control PIO')
    if not isinstance(rom_slot,int) or not 0<=rom_slot<16:
        raise ValueError('ROM slot must be 0..15')
    if rom_memory not in ("flash","sram"):
        raise ValueError("rom_memory must be flash or sram")
    if rom_memory == "sram" and rom_slot % 2:
        raise ValueError("SRAM ROM requires an even slot: odd slots overlap boot RAM clearing")
    if _keepalive is not None:
        raise RuntimeError('Already active; use reset() while host is held in reset')
    # Validate/allocate before changing the live memory interface.
    dma=DMA()
    freq(270_000_000)               # Existing V2 operating clock; overclock, validate physically.
    for i in range(8):StateMachine(i).active(0)
    # Stock firmware can leave RX DMA armed on the very FIFO we now need.
    # This is an EXCLUSIVE takeover: no other PIO/DMA consumer may remain running.
    for i in range(12):
        ctrl_address=0x5000000c+0x40*i
        mem32[ctrl_address]=mem32[ctrl_address]&~1
    _abort_dma(0xfff)
    PIO(0).remove_program();PIO(1).remove_program()
    # remove_program() without an argument does not invalidate Python-side
    # cached offsets on MicroPython 1.20. Force real reloads on every restart,
    # including after another diagnostic occupied instruction memory.
    for program in (memory_enable,memory_enable_sram,memory_address,paging_write,paging_observer):
        program[1]=-1
        program[2]=-1
    Pin(12,Pin.OUT,value=1)
    Pin(28,Pin.OUT,value=1)          # SD deselected while GPIO2-4 serve as data inputs.
    for i in range(2,12):Pin(i,Pin.IN)
    for i in (0,1,13,14,26,27):Pin(i,Pin.IN)
    for i in range(15,19):Pin(i,Pin.OUT,value=(rom_slot>>(i-15))&1)
    for i in (19,20,21):Pin(i,Pin.OUT,value=1)
    Pin(22,Pin.OUT,value=0)
    enable_program=memory_enable_sram if rom_memory == "sram" else memory_enable
    enable=StateMachine(4,enable_program,freq=150_000_000,
                        in_base=Pin(0),jmp_pin=Pin(26),set_base=Pin(19))
    address=StateMachine(5,memory_address,freq=150_000_000,
                         jmp_pin=Pin(26),out_base=Pin(15))
    latch=StateMachine(0,paging_write,freq=PAGING_FREQ,in_base=Pin(2),
                       out_base=Pin(22),jmp_pin=Pin(11),sideset_base=Pin(12))
    observer=StateMachine(6,paging_observer,freq=PAGING_FREQ,in_base=Pin(2),jmp_pin=Pin(11))
    address.put(rom_slot);address.exec('pull()');address.exec('mov(x,osr)')
    latch.put(rom_slot);latch.exec('pull()');latch.exec('mov(y,osr)')
    # PIO0 SM0 RX DREQ=4, 32-bit words -> PIO1 SM1 TX FIFO. No Python per paging write.
    ctrl=dma.pack_ctrl(size=2,inc_read=False,inc_write=False,treq_sel=4,high_pri=True)
    dma.config(read=0x50200020,write=0x50300014,count=0xffffffff,ctrl=ctrl,trigger=True)
    observer.active(1);enable.active(1);address.active(1);latch.active(1)
    _observer=observer
    _keepalive=(enable,address,latch,dma,rom_slot,rom_memory)
    return _keepalive


def reset(host_held_in_reset=False):
    global _keepalive
    if not host_held_in_reset:raise RuntimeError('Hold TS2068 reset first')
    if _keepalive is None:raise RuntimeError('Personality is not active')
    enable,address,latch,dma,slot,rom_memory=_keepalive
    latch.active(0);enable.active(0);address.active(0)
    dma.active(0);dma.close()
    _keepalive=None
    return start(slot,True,rom_memory)
