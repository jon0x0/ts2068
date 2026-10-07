"""Position-independent ECM transitions and shared, padded Sinistar rows."""
import json

def build(out, banks, cursor, poses):
    def alloc(data):
        bank=next(n for n in (0,1,7) if cursor[n]+len(data)<=8192)
        offset=cursor[bank];cursor[bank]+=len(data)
        banks[bank][offset:offset+len(data)]=data
        return bank*8192+offset
    def words(values):
        return b''.join(v.to_bytes(2,'little') for v in values)
    rows={}
    def row_address(row):
        row=bytes(row)
        if row not in rows:
            rows[row]=alloc(bytes([0])+row[:7]+bytes([0,7])+row[7:]+bytes([7]))
        return rows[row]
    blank=row_address(bytes(7)+bytes([7]*7))
    tables=[]
    for pose in poses:
        tables.append(alloc(words(row_address(pose[y*14:y*14+14]) for y in range(52))))
    shut=[[poses[e*3] if p==0 else poses[9+e*7+p-1] for p in range(8)] for e in range(3)]
    cases=[];pairs={};streams={};masks=set();stream_bases=[]
    for eye in range(3):
        for phase in range(8):
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    q=(phase+dx)%8;bx=(phase+dx)//8;x0=min(0,bx)
                    def value(p,x,y,plane):
                        return shut[eye][p][y*14+plane*7+x] if 0<=x<7 and 0<=y<52 else (7 if plane else 0)
                    stream=[];casepairs=[]
                    for y in range(min(0,dy),52+max(0,dy)):
                        pair=tuple(sum(1<<i for i,x in enumerate(range(x0,x0+8))
                                       if value(phase,x,y,plane)!=value(q,x-bx,y-dy,plane)) for plane in range(2))
                        if pair not in pairs:pairs[pair]=len(pairs)
                        masks.update(pair);stream.append(pairs[pair]);casepairs.append(pair)
                    assert len(pairs)<=256
                    stream=bytes(stream)
                    if stream not in streams:
                        padded=stream.ljust(53,b'\0')
                        candidates=[(sum(a!=b for a,b in zip(padded,base)),address,base,depth)
                                    for base,address,depth in stream_bases if depth<3]
                        best=min(candidates,default=(999,0,b'',0),key=lambda x:(x[0],x[3]))
                        changes,parent,base,depth=best
                        if 10+changes<54:
                            mask=bytearray(7);values=bytearray()
                            for j,(a,b) in enumerate(zip(padded,base)):
                                if a!=b:mask[j//8]|=1<<(j%8);values.append(a)
                            data=b'\1'+words([parent])+mask+values;depth+=1
                        else:data=b'\0'+padded;depth=0
                        address=alloc(data);streams[stream]=address
                        stream_bases.append((padded,address,depth))
                    cases.append(dict(eye=eye,phase=phase,dx=dx,dy=dy,address=streams[stream],pairs=casepairs))
    kernels={};costs={}
    for mask in sorted(masks):
        code=bytearray();cost=10
        # No reads or writes for unchanged cells; no runtime pixel comparisons.
        for x in range(mask.bit_length()):
            if mask>>x&1:code.extend([0x1a,0x77]);cost+=14
            if x+1<mask.bit_length():code.extend([0x2c,0x13]);cost+=10
        code.append(0xc9);kernels[mask]=alloc(code);costs[mask]=cost
    pair_table=alloc(words(kernels[m] for pair in pairs for m in pair))
    transitions=alloc(words(case['address'] for case in cases))
    pose_table=alloc(words(tables[e*3] if p==0 else tables[9+e*7+p-1] for e in range(3) for p in range(8)))
    # Publication guard is expressed in T-states of preceding sparse writes.
    # Stack-fed publication costs at most 72 T per nonempty record plus kernel.
    limits=[]
    for case in cases:
        elapsed=3500;slack=65535
        for y,pair in enumerate(case['pairs']):
            elapsed+=sum(72+costs[m] for m in pair if m)
            slack=min(slack,(40+64)*224-elapsed)
        limits.append(max(0,slack)//4)
    budget_table=alloc(words(limits))
    # Common horizontal transitions are fully prepared ROM records, split into
    # four-row chunks so the three eyebrow poses share unchanged body chunks.
    chunks={};horizontal=[]
    # DOCK3 is copied at boot: runtime never hides HOME stack/state at 6000.
    cache_windows=[[0xa000,1680,0,0],[0xc300,1260,1680,0],[0x5900,420,2940,0]]
    # General transition streams remain; replace specialized horizontal templates
    # with compiled, overlap-safe planetoid rows in the playable cartridge.
    horizontal_table=0
    cursor[3]=3360+1792
    boot=[' ld a,$18',' out ($f4),a']
    for dest,size,source,used in cache_windows:
        boot += [f' ld hl,{0x6000+source}',f' ld de,{dest}',f' ld bc,{size}',' ldir']
    boot += [' ld a,$10',' out ($f4),a']
    (out/'fast-cache-init.asm').write_text('\n'.join(boot)+'\n',encoding='utf-8')
    (out/'fast-tables.asm').write_text('\n'.join(f'{k} EQU {v}' for k,v in
        [('fast_blank_row',blank),('fast_pair_table',pair_table),('fast_transition_table',transitions),
         ('fast_pose_table',pose_table),('fast_budget_table',budget_table),('fast_empty_kernel',kernels[0]),
         ('fast_horizontal_table',horizontal_table),('assembly_cache_source',0x6000+3360)])+'\n',encoding='utf-8')
    report=dict(cases=cases,rows=len(rows),pairs=len(pairs),streams=len(streams),kernels=len(kernels),
                budget_bytes_min=min(limits),budget_bytes_max=max(limits),
                source_banks=[0,1,7],bytes=sum(cursor[n] for n in (0,1,7)))
    report['horizontal_template_bytes']=sum(len(payload) for dx,payload in chunks)+len(horizontal)*28
    report['boot_cache_windows']=cache_windows
    (out/'fast-transitions.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return tables,report,alloc
