"""Stock-sequence 128 paging adapter; definitions only, no persistent writes.

Load personality128.py definitions first for the RP2040 DMA bridge. The
controller follows stock set_ctrl, but only owns /BE on GP21: GP22 belongs
exclusively to the paging latch. Stock sel_bank remains on SM5. No SD service.
"""


@asm_pio(set_init=(PIO.OUT_HIGH,),in_shiftdir=PIO.SHIFT_LEFT,
         out_init=(PIO.OUT_HIGH,)*2,out_shiftdir=PIO.SHIFT_RIGHT,
         autopull=True,pull_thresh=8)
def _stock128_control():
    wrap_target()
    mov(pins,invert(null))
    mov(y,null)
    set(pins,1)             # Stock SET 3: only /BE remains owned here.
    pull(noblock)
    mov(x,osr)
    wait(0,gpio,13)
    nop() [2]
    jmp(pin,'low')
    out(null,2)
    out(pins,2)
    jmp('pass')
    label('low')
    in_(pins,2)
    mov(y,isr)
    mov(isr,null)
    jmp(y_dec,'home')
    set(pins,0)             # Stock SET 2: /BE low, GP22 untouched.
    jmp('wait')
    label('home')
    jmp(y_dec,'pass')
    set(pins,0)             # Stock SET 0: /BE low, GP22 untouched.
    label('wait')
    nop() [10]
    out(pins,2)
    label('pass')
    wait(1,gpio,13)
    wrap()


@asm_pio(out_init=(PIO.OUT_LOW,),sideset_init=(PIO.OUT_HIGH,),
         in_shiftdir=PIO.SHIFT_LEFT,out_shiftdir=PIO.SHIFT_RIGHT)
def _stock128_latch():
    wrap_target()
    label('idle')
    wait(0,gpio,14) .side(1)
    jmp(pin,'check') .side(1)
    jmp('ignore') .side(1)
    label('check')
    mov(osr,pins) .side(1)
    out(null,8) .side(1)
    out(x,1) .side(1)
    jmp(not_x,'ignore') .side(1)
    nop() .side(0) [2]
    mov(isr,null) .side(0)
    in_(pins,8) .side(0)    # Exactly one data-bus sample, then use its snapshot.
    mov(osr,isr) .side(0)
    out(x,3) .side(0)
    mov(isr,x) .side(0)
    in_(null,1) .side(0)
    in_(y,4) .side(0)       # Byte = (bank << 5) | ROM slot.
    push(noblock) .side(0)
    out(null,1) .side(0)    # Skip Spectrum shadow-screen bit (not implemented).
    out(pins,1) .side(0)    # Snapshot bit 4 -> GP22.
    out(x,1) .side(0)       # Snapshot bit 5 -> lock.
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


try:
    _stock128
except NameError:
    _stock128=None


def start_stock128(host_held_in_reset=False,host_parked=False,initial_rom_half=0):
    global _stock128
    if not (host_held_in_reset or host_parked):raise RuntimeError('Hold TS Reset or use the cooperative HOME handoff')
    if initial_rom_half not in (0,1):raise ValueError('Invalid initial ROM half')
    if _stock128 is not None:raise RuntimeError('Use reset_stock128(True)')
    if freq()!=270_000_000:raise RuntimeError('Expected stock 270 MHz clock')
    from tspico_io import sel_bank
    if len(_stock128_control[0])+len(sel_bank[0])>32:
        raise RuntimeError('PIO1 instruction memory exceeded')
    dma=DMA()
    for i in range(8):StateMachine(i).active(0)
    for i in range(12):
        address=0x5000000c+64*i
        mem32[address]=mem32[address]&~1
    _abort_dma(0xfff)
    PIO(0).remove_program();PIO(1).remove_program()
    for program in (_stock128_control,_stock128_latch,sel_bank):
        program[1]=-1;program[2]=-1
    Pin(12,Pin.OUT,value=1);Pin(28,Pin.OUT,value=1)
    for i in range(2,12):Pin(i,Pin.IN)
    for i in (0,1,13,14,26,27):Pin(i,Pin.IN)
    for i in range(15,19):Pin(i,Pin.OUT,value=(4>>(i-15))&1)
    for i in (19,20,21):Pin(i,Pin.OUT,value=1)
    Pin(22,Pin.OUT,value=initial_rom_half)
    control=StateMachine(4,_stock128_control,freq=150_000_000,
                         in_base=Pin(0),jmp_pin=Pin(26),set_base=Pin(21),out_base=Pin(19))
    address=StateMachine(5,sel_bank,freq=150_000_000,jmp_pin=Pin(26),out_base=Pin(15))
    latch_program=_stock128_latch
    if initial_rom_half:
        latch_program=list(_stock128_latch)
        latch_program[1]=-1;latch_program[2]=-1
        latch_program[5]=(PIO.OUT_HIGH,)
    latch=StateMachine(0,latch_program,freq=30_000_000,
                       in_base=Pin(2),jmp_pin=Pin(11),out_base=Pin(22),sideset_base=Pin(12))
    control.put(5)
    address.put(4);address.exec('pull()');address.exec('mov(x,osr)');address.exec('out(pins,4)')
    latch.put(4);latch.exec('pull()');latch.exec('mov(y,osr)')
    ctrl=dma.pack_ctrl(size=2,inc_read=False,inc_write=False,treq_sel=4,high_pri=True)
    dma.config(read=0x50200020,write=0x50300014,count=0xffffffff,ctrl=ctrl,trigger=True)
    _stock128=(control,address,latch,dma)
    address.active(1);control.active(1);latch.active(1)
    return {'stock_sequence_controller':True,'rom_slot':4,'rom_memory':'sram',
            'paging_port':'0x0f','initial_bank':0,'initial_rom_half':initial_rom_half,
            'pio1_words':len(_stock128_control[0])+len(sel_bank[0]),
            'pio0_words':len(_stock128_latch[0])}


def reset_stock128(host_held_in_reset=False,host_parked=False,initial_rom_half=0):
    global _stock128
    if not (host_held_in_reset or host_parked):raise RuntimeError('Hold TS Reset or use the cooperative HOME handoff')
    if _stock128 is not None:
        for sm in _stock128[:3]:sm.active(0)
        _stock128[3].close()
        _stock128=None
    return start_stock128(host_held_in_reset,host_parked,initial_rom_half)


def status_stock128():
    if _stock128 is None:return {'active':False}
    remaining=mem32[0x50000008]&0xffffffff
    gpio=mem32[0xd0000004]&0xffffffff
    return {'active':True,'dma_transfers':(0xffffffff-remaining)&0xffffffff,
            'rom_half':(gpio>>22)&1,'address_nibble':(gpio>>15)&15,
            'dma_control':hex(mem32[0x5000000c]&0xffffffff),
            'latch_pc':mem32[0x502000d4]&31}
