"""Small compiled blitters, linked into the low DOCK ROM pages."""
def compile_phase(frames, address):
    code=bytearray(); labels={}; fixes=[]
    def emit(*b): code.extend(b)
    def word(n): emit(n&255,n>>8)
    def jump(op,label):
        emit(op); fixes.append((len(code),label)); word(0)
    def advance(n):
        if n<=3: emit(*([0x2c,0x1c]*n)) # inc hl / inc de
        elif n:
            emit(1);word(n);emit(9,0xeb,9,0xeb)
    def cell(values):
        mask,bits,attr=values
        if mask==255:return
        if mask==0:emit(0x36,bits)
        else:emit(0x7e,0xe6,mask,0xf6,bits,0x77)
        emit(0x3e,attr,0x12)
    cells=[[tuple(f[i:i+3]) for i in range(0,len(f),3)] for f in frames]
    changed={i for i in range(364) if any(c[i]!=cells[0][i] for c in cells)}
    entries=[]
    for pose in range(3):
        entries.append(address+len(code));jump(0xcd,'base');jump(0xc3,f'mouth{pose}')
    labels['base']=address+len(code);emit(0xe5,0xd5)
    for y in range(52):
        previous_x=0
        for x in range(7):
            i=y*7+x
            if i not in changed and cells[0][i][0]!=255:
                advance(x-previous_x);cell(cells[0][i]);previous_x=x
        if y!=51:
            advance(7-previous_x);emit(0xcd,0x10,0x80)
    emit(0xd1,0xe1,0xc9)
    for pose in range(3):
        labels[f'mouth{pose}']=address+len(code);previous=0
        for i in sorted(changed):
            y,x=divmod(i,7)
            py,px=divmod(previous,7)
            if y==py:advance(x-px)
            else:
                advance(7-px);emit(0xcd,0x10,0x80)
                if y-py>1:emit(0x06,y-py-1,0xcd,0x40,0x80)
                advance(x)
            cell(cells[pose][i]);previous=i
        emit(0xc9)
    for offset,label in fixes:
        target=labels[label];code[offset:offset+2]=bytes([target&255,target>>8])
    return bytes(code),entries

