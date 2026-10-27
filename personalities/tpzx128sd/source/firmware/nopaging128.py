"""RAM-only fixed-memory entry point for tspico-nopaging.rom.

Load personality128.py definitions first. No paging setup is started.
Call ONLY with TS Reset held and the diagnostic ROM staged in SRAM slot 4.
No paging capture, DMA bridge, or SD service remains. The optional stock
address selector uses constant ROM/DOCK selections for a separate trial.
"""


def start_nopaging128(host_held_in_reset=False, use_stock_controller=True,
                     use_stock_address_selector=False, dock_bank=2):
    global _nopaging_sm,_nopaging_address
    if not host_held_in_reset:
        raise RuntimeError('Hold TS Reset during this call')
    if type(dock_bank) is not int or not 0<=dock_bank<=7:
        raise ValueError('DOCK bank must be 0..7')
    if dock_bank!=2 and not use_stock_address_selector:
        raise ValueError('Changing DOCK bank requires the address selector')
    if _keepalive is not None:
        raise RuntimeError('Use a fresh REPL session, without an active paging personality')
    if freq()!=270_000_000:
        raise RuntimeError('Expected stock 270 MHz clock; no clock change attempted')
    if use_stock_address_selector and not use_stock_controller:
        raise RuntimeError('Address-selector comparison requires the stock controller')
    control_program=memory_enable_sram
    if use_stock_controller:
        # Reuse the program from this device's installed firmware, not a copy
        # from a newer release. Import before making hardware changes.
        from tspico_io import set_ctrl
        control_program=set_ctrl
    if use_stock_address_selector:
        from tspico_io import sel_bank
        if len(control_program[0])+len(sel_bank[0])>32:
            raise RuntimeError('Installed memory programs exceed PIO1 instruction memory')
    for i in range(8):StateMachine(i).active(0)
    for i in range(12):
        address=0x5000000c+0x40*i
        mem32[address]=mem32[address]&~1
    _abort_dma(0xfff)
    PIO(0).remove_program();PIO(1).remove_program()
    Pin(12,Pin.OUT,value=1)  # U6 data buffer disabled: no I/O capture.
    Pin(28,Pin.OUT,value=1)  # SD deselected.
    for i in range(2,12):Pin(i,Pin.IN)
    for i in (0,1,13,14,26,27):Pin(i,Pin.IN)
    for i in range(15,19):Pin(i,Pin.OUT,value=(4>>(i-15))&1)
    for i in (19,20,21):Pin(i,Pin.OUT,value=1)
    Pin(22,Pin.OUT,value=0)  # First ROM half; diagnostic halves are identical.
    control_program[1]=-1;control_program[2]=-1
    if use_stock_controller:
        _nopaging_sm=StateMachine(4,control_program,freq=150_000_000,
                                  in_base=Pin(0),jmp_pin=Pin(26),
                                  set_base=Pin(21),out_base=Pin(19))
        _nopaging_sm.put(5)  # ROM=SRAM (01), DOCK=SRAM (01): 0101.
    else:
        _nopaging_sm=StateMachine(4,control_program,freq=150_000_000,
                                  in_base=Pin(0),jmp_pin=Pin(26),set_base=Pin(19))
    _nopaging_address=None
    if use_stock_address_selector:
        sel_bank[1]=-1;sel_bank[2]=-1
        _nopaging_address=StateMachine(5,sel_bank,freq=150_000_000,
                                       jmp_pin=Pin(26),out_base=Pin(15))
        # ROM nibble 4, DOCK nibble bank*2; the CPU supplies low 16 bits
        # in DOCK mode. C000-FFFF never overlaps the staged ROM pair.
        _nopaging_address.put((dock_bank<<5)|4)
        _nopaging_address.exec('pull()')
        _nopaging_address.exec('mov(x,osr)')
        _nopaging_address.exec('out(pins,4)')
        _nopaging_address.active(1)
    _nopaging_sm.active(1)
    return {'fixed_address_nibble':4,'fixed_dock_bank':dock_bank,'rom_half':0,
            'rom_physical_base':'0x20000','dock_physical_base':hex((dock_bank<<16)|0xc000),
            'paging_capture_paused':True,'dma_paused':True,
            'address_sm_paused':not use_stock_address_selector,
            'only_active_sm':None if use_stock_address_selector else 4,
            'active_sms':[4,5] if use_stock_address_selector else [4],
            'installed_stock_controller':use_stock_controller}
