"""Typed display-attribute fixes. Never apply to encoded palette IDs or opcodes."""
def normal_attribute(a):
    return a & ~64 if a & 64 and (not a & 7 or not a & 56) else a

def patch_exact(b, at, old, new):
    old, new = bytes.fromhex(old), bytes.fromhex(new)
    assert len(old) == len(new) and b[at:at+len(old)] == old, (hex(at), b[at:at+len(old)].hex(), old.hex())
    b[at:at+len(old)] = new

def patch_score(b, at, fill_call):
    # Native colour cycling, on a black paper background. Preserve its timing,
    # seven-colour sequence and white half; bit6 applies to BOTH endpoints.
    assert b[at:at+3] == bytes.fromhex('210058')
    patch_exact(b, at+9, '3e47cd'+fill_call, '3e07cd'+fill_call)
    patch_exact(b, at+27, 'c640cd'+fill_call, 'c600cd'+fill_call)

def patch_stock_title(b):
    patch_exact(b,0x19f2,'af3200bed3ffc390bcffffff','cdcbbcaf3200bed3ffc390bc')
    at=bytes(b).find(bytes.fromhex('3e40d3ff'),0x1900,0x19b0);assert at>=0
    patch_exact(b,at,'3e40d3ff','3e42d3ff')
    # Fixed ROM0 initializer and final-logo display attributes.
    old=bytes.fromhex('2100600100183e47cdf0fd')
    start=bytes(b).find(old,0xf20,0xf60);assert start>=0
    patch_exact(b,start,old.hex(),old.replace(bytes.fromhex('3e47'),bytes.fromhex('3e07')).hex())
    b[0x9600:0x9c00]=bytes(map(normal_attribute,b[0x9600:0x9c00]))

def patch_stock_home(b):
    old=bytes.fromhex('2100580100033e47cdf0fd')
    at=bytes(b).find(old,0x86c3,0x8721);assert at>=0
    patch_exact(b,at,old.hex(),old.replace(bytes.fromhex('3e47'),bytes.fromhex('3e07')).hex())
    # This is a decompressed HOME image, not the compressed ROM6 container.
    patch_exact(b,0xfcb1,'79d600fe043e4738023e45','79d600fe043e0738023e05')
