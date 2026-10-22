"""Translate the pinned Digital Research 8080 sources to sjasmplus syntax.

Only syntax changes; the original files and license remain in third_party.
"""
import re

def convert(text, origin):
    out = [f'    DEFINE origin {origin}']
    pairs = {'b':'bc','d':'de','h':'hl','sp':'sp','psw':'af'}
    regs = lambda s: re.sub(r'\bm\b', '(hl)', s, flags=re.I)
    single = {'mov':'ld','mvi':'ld','lxi':'ld','lda':'ld a,','sta':'ld','lhld':'ld hl,',
              'shld':'ld','xchg':'ex de,hl','xthl':'ex (sp),hl','sphl':'ld sp,hl',
              'pchl':'jp (hl)','jmp':'jp','cma':'cpl','stc':'scf','cmc':'ccf',
              'ral':'rla','rar':'rra','rlc':'rlca','rrc':'rrca','hlt':'halt'}
    conds={'nz':'nz','z':'z','nc':'nc','c':'c','po':'po','pe':'pe','p':'p','m':'m'}
    for line in text.splitlines():
        line=line.replace("';'", '59')
        code = re.split(r';(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line, maxsplit=1)[0].rstrip()
        if not code.strip(): continue
        if code.strip().split()[0].lower() in ('.cpu','title','end'): continue
        match=re.match(r'^(\w+:?\s*)?(\s+)(\w+)\s*(.*)$',code)
        if not match:
            out.append(code); continue
        label,_,op,arg=match.groups(); label=label or ''; op=op.lower(); arg=arg.strip()
        if label and ':' not in label and op not in ('equ','set'): label=label.rstrip()+': '
        a=arg.lower()
        if op in ('lxi','push','pop','inx','dcx','dad'):
            parts=a.split(','); parts[0]=pairs.get(parts[0],parts[0]); arg=','.join(parts)
            if op=='lxi' and len(parts)==2:
                value=parts[1].strip()
                if value.startswith('(') and value.endswith(')'): value=value[1:-1]
                arg=parts[0]+','+value
            op={'lxi':'ld','inx':'inc','dcx':'dec','dad':'add hl,'}.get(op,op)
        elif op in ('inr','dcr'): op={'inr':'inc','dcr':'dec'}[op]; arg=regs(arg)
        elif op in ('ldax','stax'): arg=('a,('+pairs[a]+')') if op=='ldax' else '('+pairs[a]+'),a'; op='ld'
        elif op in ('lda','lhld'): arg=('a,' if op=='lda' else 'hl,')+'('+arg+')'; op='ld'
        elif op in ('sta','shld'): arg='('+arg+'),'+('a' if op=='sta' else 'hl'); op='ld'
        elif op in ('add','adc','sub','sbb','ana','xra','ora','cmp','adi','aci','sui','sbi','ani','xri','ori','cpi'):
            op={'adi':'add','aci':'adc','sui':'sub','sbi':'sbc','sbb':'sbc','ana':'and','ani':'and','xra':'xor','xri':'xor','ora':'or','ori':'or','cmp':'cp','cpi':'cp'}.get(op,op)
            arg=regs(arg)
            if op in ('add','adc','sbc'): arg='a,'+arg
        elif op[0:1] in ('j','c','r') and op[1:] in conds:
            arg=conds[op[1:]]+(','+arg if arg else ''); op={'j':'jp','c':'call','r':'ret'}[op[0]]
        elif op=='out': arg='('+arg+'),a'
        elif op=='in': arg='a,('+arg+')'
        elif op=='set': op='equ'
        elif op in single: op=single[op]; arg=regs(arg)
        if op=='dw': arg=re.sub(r'\b([a-zA-Z_]\w*)\s*\+\s*',r'\1+',arg)
        # AS uses ! as bitwise OR in these sources.
        arg=arg.replace('!','|')
        out.append(f'{label}\t{op} {arg}')
    return '\n'.join(out)+'\n'
