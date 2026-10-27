"""Temporary isolation test; paste definitions, then hold TS Reset for the call.

Keeps the address GPIO nibble fixed at the SRAM ROM slot. For slot 4, this
also fixes DOCK RAM to physical bank 2. Expected evidence is the first paging
writes, not a working menu. reset(True) restores normal address switching.
"""


def fixed_address128(host_held_in_reset=False):
    if not host_held_in_reset:
        raise RuntimeError('Hold TS Reset during this call')
    if _keepalive is None or _keepalive[5] != 'sram':
        raise RuntimeError('This diagnostic requires an active SRAM personality')
    slot=_keepalive[4]
    if slot % 2:
        raise RuntimeError('This diagnostic requires an even SRAM slot')
    reset(host_held_in_reset=True)
    address=_keepalive[1]
    _keepalive[3].active(0)
    address.active(0)
    address.put(slot)
    address.exec('pull()')
    address.exec('out(pins,4)')
    return {'fixed_address_nibble':slot,'fixed_dock_bank':slot >> 1,
            'dma_paused':True,'address_sm_paused':True}
