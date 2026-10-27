# Exact sel_bank/set_ctrl extracts from the local TSPico firmware reference.
# Host-test fixture only; never uploaded to the Pico.
@asm_pio(                                       # Bank selection via A15..A18
    out_init=(PIO.OUT_LOW, ) * 4, 
    out_shiftdir=PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=8,
    )
def sel_bank():
    wrap_target()
    pull(noblock)
    mov(x, osr)
    wait (0, gpio, 13)
    jmp(pin, "low")
    out(null, 4)
    out(pins, 4)
    jmp("fin")
    label("low")
    out(pins, 4)
    label("fin")
    wait (1, gpio, 13)
    wrap()

@asm_pio(                                       # Control lines: set /BE, A14_L; out U10_ENA, U13_ENA (flash, SRAM)
    set_init=(PIO.OUT_HIGH, ) * 2,
    in_shiftdir=PIO.SHIFT_LEFT,
    out_init=(PIO.OUT_HIGH, ) * 2,
    out_shiftdir=PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=8,
    )
def set_ctrl():
    wrap_target()
    mov(pins, invert(null))
    mov(y, null)
    set(pins, 3)
    pull(noblock)
    mov(x, osr)
    wait (0, gpio, 13)
    nop()                  [2]
    jmp (pin, "low")
    out(null, 2)
    out(pins, 2)
    jmp("pass")
    label("low")
    in_(pins, 2)
    mov(y, isr)
    mov(isr, null)
    jmp(y_dec, "home")
    set(pins, 2)
    jmp("wait")
    label("home")
    jmp(y_dec, "pass")
    set(pins, 0)
    label("wait")
    nop()                  [10]
    out(pins, 2)
    label("pass")
    wait (1, gpio, 13)
    wrap()
