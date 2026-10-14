"""Translate numbered TS2068 BASIC listings to Leap V2 BASIC.

Unsupported operations are blocking diagnostics, never silently removed.
Use --segment for exports containing multiple programs separated by a line-number reset.
"""
import argparse
import bisect
from dataclasses import dataclass
import json
from pathlib import Path
import re
from packed_basic_data import pack_data, pointer, reader_source


class Unsupported(ValueError):
    pass


TOKEN = re.compile(r'\s*("[^"\r\n]*"|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[A-Za-z][A-Za-z0-9]*\$?|<>|<=|>=|[()+\-*/^=<>:,;])')
KEYWORDS = {'AND','OR','NOT','TO','THEN'}
FUNCTIONS = {'ABS','SGN','INT','SQR','SIN','COS','TAN','EXP','LN','LEN','CODE','VAL','CHR$','STR$','PEEK','IN','POINT','ATTR'}


def tokens(text):
    out=[]; pos=0
    while pos<len(text.rstrip()):
        m=TOKEN.match(text,pos)
        if not m:
            raise Unsupported(f'Unrecognised character near {text[pos:pos+20]!r}')
        out.append(m[1] if m[1].startswith('"') else m[1].upper())
        pos=m.end()
    return out


def split_statements(text):
    """REM consumes the remainder; colons inside strings are ordinary text."""
    out=[]; start=0; quote=False
    for i,c in enumerate(text):
        if c=='"': quote=not quote
        if c==':' and not quote:
            piece=text[start:i].strip()
            if re.match(r'REM\b',piece,re.I):
                out.append(text[start:].strip()); return out
            if piece: out.append(piece)
            start=i+1
    if text[start:].strip(): out.append(text[start:].strip())
    return out


def split_args(text):
    result=[]; start=0; depth=0; quote=False
    for i,c in enumerate(text):
        if c=='"': quote=not quote
        if not quote:
            depth+=int(c=='(')-int(c==')')
            if c==',' and depth==0: result.append(text[start:i].strip()); start=i+1
    result.append(text[start:].strip())
    return result


@dataclass
class Expr:
    text:str
    constant:object=None
    kind:str='number'


class Parser:
    PRECEDENCE={'OR':1,'AND':2,'=':3,'<>':3,'<':3,'>':3,'<=':3,'>=':3,'+':4,'-':4,'*':5,'/':5,'^':7}
    def __init__(self,converter,text,allow_long_string=False):
        self.c=converter; self.t=tokens(text); self.p=0; self.allow_long_string=allow_long_string; self.long_literal=False
    def take(self):
        if self.p>=len(self.t): raise Unsupported('Incomplete expression')
        t=self.t[self.p]; self.p+=1; return t
    def peek(self): return self.t[self.p] if self.p<len(self.t) else None
    def expect(self,t):
        if self.take()!=t: raise Unsupported(f'Expected {t}')
    def parse(self):
        e=self.expression()
        if self.peek() is not None: raise Unsupported(f'Unexpected expression token {self.peek()}')
        if self.long_literal and not isinstance(e.constant,str): raise Unsupported('Only standalone PRINT literals may exceed 31 characters')
        return e
    def compact(self,e):
        if self.c.compact_expressions and len(e.text)>80 and e.constant is None:
            self.c.temp_counter+=1
            name='QZX'+str(self.c.temp_counter)+('$' if e.kind=='string' else '')
            self.c.pending.append(name+' = '+e.text)
            return Expr(name,kind=e.kind)
        return e
    def expression(self,level=0):
        t=self.take()
        if t in ('-','+','NOT'):
            e=self.expression(6 if t!='NOT' else 3)
            value=(-e.constant if t=='-' else e.constant) if isinstance(e.constant,(int,float)) and t!='NOT' else None
            left=Expr(f'({t} {e.text})',value,kind='boolean' if t=='NOT' else 'number')
        elif t=='(':
            left=self.expression(); self.expect(')')
        elif t.startswith('"'):
            value=t[1:-1]
            if len(value)>31 and not self.allow_long_string:
                raise Unsupported('String expression exceeds Leap 31-character scalar capacity')
            if len(value)>31: self.long_literal=True
            if '\\' in value:
                if not self.c.udg_escapes: raise Unsupported('Escaped graphical characters need --udg-escapes and the original UDG bytes')
                pieces=[]; literal=''; i=0
                while i<len(value):
                    if value[i]=='\\' and i+1<len(value) and 'a'<=value[i+1].lower()<='u':
                        if literal: pieces.append('"'+literal+'"'); literal=''
                        pieces.append(f'CHR$({144+ord(value[i+1].lower())-97})'); i+=2
                    else: literal+=value[i]; i+=1
                if literal: pieces.append('"'+literal+'"')
                if not pieces: pieces=['""']
                left=Expr('+'.join(pieces),kind='string')
                self.c.notes.add('Backslash a..u escapes are interpreted as UDG codes 144..164; original glyph bytes are required.')
            else: left=Expr(t,value,'string')
        elif re.fullmatch(r'(?:\d+(?:\.\d*)?|\.\d+)(?:E[+-]?\d+)?',t):
            n=float(t); text=format(n,'.15f').rstrip('0').rstrip('.') if '.' in t or 'E' in t else t
            left=Expr(text,int(n) if n.is_integer() else n)
        elif t=='PI': left=Expr('PI()')
        elif t=='RND':
            self.c.notes.add('RND uses the Leap generator and a 32767-step fraction; random sequences differ.')
            left=Expr('(RND(32767)/32767)')
        elif t=='INKEY$': left=Expr('INKEY$()',kind='string')
        elif t=='FN':
            name=self.take(); self.expect('('); e=self.expression(); self.expect(')')
            left=Expr(f'FN {self.c.name(name,"function")}({e.text})')
        elif (t in FUNCTIONS and t not in self.c.scalar_names) or t=='USR':
            if self.peek()=='(':
                self.take(); args=[self.expression()]
                while self.peek()==',': self.take(); args.append(self.expression())
                self.expect(')')
            else: args=[self.expression(6)]
            if t=='VAL' and args[0].kind=='string' and args[0].constant is not None:
                value=args[0].constant
                try: left=Parser(self.c,value).parse()
                except Unsupported: raise Unsupported('VAL of a string requires a supported numeric expression')
            elif t=='USR' and args[0].kind=='string':
                if args[0].constant and len(args[0].constant)==1 and 'a'<=args[0].constant.lower()<='u':
                    left=Expr(str(61824+8*(ord(args[0].constant.lower())-97)),61824+8*(ord(args[0].constant.lower())-97))
                    self.c.notes.add('USR "a".."u" translated to Leap UDG addresses; UDG bytes must be supplied separately.')
                else: raise Unsupported('USR string argument must identify a UDG from a to u')
            elif t=='INT':
                self.c.need_floor=True; left=Expr(f'FN QZFLOOR({args[0].text})')
            elif t in ('SIN','COS','TAN'):
                left=Expr(f'{t}(DEG({args[0].text}))')
            elif t=='POINT':
                if len(args)!=2: raise Unsupported('POINT requires two coordinates')
                left=Expr(f'POINT({args[0].text},{self.c.graphics_height-1}-({args[1].text}))')
            elif t=='PEEK' and not self.c.allow_hardware:
                raise Unsupported('PEEK needs an audited address contract; use --allow-hardware only for verified addresses')
            elif t=='PEEK':
                self.c.notes.add('Raw PEEK/POKE/OUT were permitted explicitly; stock ROM/system-variable addresses may not be valid under Leap.')
                left=Expr(f'PEEK({args[0].text})')
            elif t=='USR':
                raise Unsupported('Numeric USR needs an audited machine-code address and calling convention')
            else:
                left=Expr(f'{t}('+','.join(a.text for a in args)+')',kind='string' if t.endswith('$') else 'number')
        elif re.fullmatch('[A-Z][A-Z0-9]*\$?',t):
            if self.peek()=='(':
                self.take(); args=[self.expression()]
                if self.peek()=='TO':
                    self.take(); end=self.expression(); self.expect(')')
                    if not t.endswith('$') or t in self.c.arrays: raise Unsupported('Array slicing requires explicit adaptation')
                    left=Expr(f'MID$({self.c.name(t)}, {args[0].text},({end.text})-({args[0].text})+1)',kind='string')
                else:
                    while self.peek()==',': self.take(); args.append(self.expression())
                    self.expect(')')
                    left=self.c.array_access(t,args)
            else: left=Expr(self.c.name(t),kind='string' if t.endswith('$') else 'number')
        else: raise Unsupported(f'Unexpected expression token {t}')
        while self.peek() in self.PRECEDENCE and self.PRECEDENCE[self.peek()]>=level:
            op=self.take(); precedence=self.PRECEDENCE[op]
            right=self.expression(precedence if op=='^' else precedence+1)
            if op=='^':
                if right.constant==2: left=Expr(f'({left.text}*{left.text})')
                elif right.constant==1: pass
                elif right.constant==0: left=Expr('1',1)
                else: raise Unsupported('Only constant powers 0, 1 and 2 are currently translated')
            elif op=='AND':
                if left.kind=='string' or right.kind=='string': raise Unsupported('AND needs numeric operands')
                left=Expr(f'({left.text} AND {right.text})',kind='boolean') if left.kind==right.kind=='boolean' else Expr(f'({left.text}*({right.text}<>0))')
            elif op=='OR':
                if 'RND(' in left.text: raise Unsupported('OR with a random left operand needs a temporary to preserve evaluation')
                left=Expr(f'({left.text} OR {right.text})',kind='boolean') if left.kind==right.kind=='boolean' else Expr(f'({left.text}*({left.text}<>0)+{right.text}*({left.text}=0))')
            else:
                left=Expr(f'({left.text} {op} {right.text})',kind='boolean' if op in ('=','<>','<','>','<=','>=') else left.kind)
            left=self.compact(left)
        return left


class Converter:
    def __init__(self,rows,stack_depth=64,allow_hardware=False,udg_escapes=False,graphics_height=176,data_backend='inline',stream_source=False,hoist_dims=False):
        self.rows=rows; self.numbers=sorted(n for n,_ in rows); self.stack_depth=stack_depth
        self.allow_hardware=allow_hardware; self.udg_escapes=udg_escapes; self.graphics_height=graphics_height
        self.names={}; self.arrays={}; self.string_lengths={}; self.diagnostics=[]; self.notes=set()
        self.output=[]; self.mapping=[]; self.returns=[]; self.labels=set(); self.need_floor=False
        self.data=[]; self.data_lines=[]; self.need_data=False; self.line=0
        self.scalar_names=set(); self.zero_loops={}; self.zero_loop_counter=0
        self.dynamic_jump=False
        self.need_pen=False
        self.data_backend=data_backend; self.stream_source=stream_source
        self.hoist_dims=hoist_dims
        self.compact_expressions=False; self.pending=[]; self.temp_counter=0
        self.levels=[]
        self.notes.add('Numeric array elements remain limited to signed 16-bit integers under Leap; floating-point array storage needs adaptation.')
        self.notes.add('Arrays retain one-based subscripts using an extra element; index zero is not an original-program data element.')
        for _,text in rows:
            masked=re.sub(r'"[^\"]*"','""',text)
            self.scalar_names.update(m[1].upper() for m in re.finditer(r'\b(?:LET|FOR|INPUT)\s+([A-Za-z][A-Za-z0-9]*\$?)\s*(?:=|TO|$)',masked,re.I))
            self.scalar_names.update(m[1].upper() for m in re.finditer(r'(?:^|:)\s*([A-Za-z][A-Za-z0-9]*\$?)\s*=',masked))
        for n,text in rows:
            for statement in split_statements(text):
                dim=re.match(r'DIM\s+([A-Za-z][A-Za-z0-9]*\$?)\s*\((.*)\)$',statement,re.I)
                if dim:
                    name=dim[1].upper()
                    try:
                        sizes=[Parser(self,x).parse().constant for x in split_args(dim[2])]
                        if any(not isinstance(x,int) or x<=0 for x in sizes): raise Unsupported('DIM needs positive constant dimensions')
                        if name.endswith('$') and len(sizes)==1: self.string_lengths[name]=sizes[0]
                        else: self.arrays[name]=sizes
                    except Unsupported as error: self.error(n,str(error),'DIM')
                match=re.match(r'DATA\s+(.*)',statement,re.I)
                if match:
                    self.data_lines.append((n,len(self.data)))
                    for item in split_args(match[1]):
                        try:
                            value=Parser(self,item).parse()
                            if value.constant is None: raise Unsupported('DATA must contain literal values')
                            self.data.append((n,value))
                        except Unsupported as error: self.error(n,str(error),'DATA')
        self.packed_data,self.data_offsets,self.data_end=pack_data(self.data,self.data_lines)
        self.compact_expressions=True

    def error(self,line,message,code='UNSUPPORTED'):
        self.diagnostics.append(dict(line=line,code=code,message=message))
    def name(self,name,kind='scalar'):
        key=(kind,name.upper())
        if key not in self.names:
            prefix={'scalar':'QV','array':'QA','function':'QF'}[kind]
            self.names[key]=prefix+str(len(self.names)+1)+('$' if name.endswith('$') else '')
        return self.names[key]
    def expr(self,text): return Parser(self,text).parse().text
    def array_access(self,name,args):
        if name not in self.arrays:
            if name.endswith('$') and len(args)==1:
                return Expr(f'MID$({self.name(name)},{args[0].text},1)',kind='string')
            raise Unsupported(f'Array {name} has no recognised DIM declaration')
        sizes=self.arrays[name]; numeric=not name.endswith('$')
        dimensions=sizes if numeric else sizes[:-1]
        if len(args)!=len(dimensions): raise Unsupported(f'{name} needs {len(dimensions)} subscripts')
        index=args[0].text
        if len(args)>1:
            index=f'({index}-1)'
            for arg,size in zip(args[1:],dimensions[1:]): index=f'({index}*{size}+({arg.text}-1))'
            index=f'({index}+1)'
        return Expr(f'{self.name(name,"array")}({index})',kind='number' if numeric else 'string')
    def target(self,text):
        value=Parser(self,text).parse().constant
        if not isinstance(value,int):
            self.dynamic_jump=True; self.labels.update(self.numbers)
            return None
        index=bisect.bisect_left(self.numbers,value)
        if index==len(self.numbers): raise Unsupported(f'Branch target {value} is beyond the final line')
        result=self.numbers[index]; self.labels.add(result)
        if result!=value: self.notes.add(f'Branch {value} resolves to the next stored line, {result}.')
        return f'QL{result}'
    def statements(self,parts):
        result=[]
        for i,part in enumerate(parts):
            m=re.match(r'IF\s+(.+?)\s+THEN\s*(.*)$',part,re.I)
            if m:
                condition=self.expr(m[1]); rest=m[2].strip()
                prefix=self.pending; self.pending=[]
                if re.fullmatch(r'(?:VAL\s+)?"?\d+"?',rest): rest='GO TO '+rest
                return result+prefix+[f'IF {condition} THEN']+self.statements(([rest] if rest else [])+parts[i+1:])+['ENDIF']
            block=self.statement(part)
            result+=self.pending+block; self.pending=[]
        return result
    def statement(self,text):
        text=text.strip()
        extension=re.fullmatch(r'CALL\s+QZLEVEL\((.*)\)',text,re.I)
        if extension and self.data_backend=='packed': return ['CALL QZLEVEL('+self.expr(extension[1])+')']
        if re.match(r'(REM|DATA)\b',text,re.I): return []
        branch=re.match(r'GO\s*(TO|SUB)\s+(.*)$',text,re.I)
        if branch:
            target=self.target(branch[2])
            jump=['GOTO '+target] if target else ['QZJUMP = '+self.expr(branch[2]),'GOTO QZDISPATCH']
            if branch[1].upper()=='TO': return jump
            self.returns.append(f'QR{len(self.returns)+1}')
            return [f'IF QZSP >= {self.stack_depth} THEN','PRINT "GOSUB STACK OVERFLOW"','END','ENDIF',
                    'QZSP = QZSP + 1',f'QZSTACK(QZSP) = {len(self.returns)}']+jump+[self.returns[-1]+':']
        if re.fullmatch('RETURN',text,re.I): return ['GOTO QZRETURN']
        m=re.match(r'(?:LET\s+)?([A-Za-z][A-Za-z0-9]*\$?(?:\s*\(.*?\))?)\s*=\s*(.*)$',text,re.I)
        if m:
            lhs=Parser(self,m[1]).parse(); rhs=Parser(self,m[2]).parse()
            if lhs.text.startswith('MID$('): raise Unsupported('Substring assignment needs explicit adaptation')
            name=re.match('[A-Za-z][A-Za-z0-9]*\$?',m[1])[0].upper()
            if name in self.string_lengths:
                w=self.string_lengths[name]; rhs=Expr(f'LEFT$({rhs.text}+"'+(' '*w)+f'",{w})',kind='string')
            if name.endswith('$') and name in self.arrays:
                w=self.arrays[name][-1]; rhs=Expr(f'LEFT$({rhs.text}+"'+(' '*w)+f'",{w})',kind='string')
            if name in self.arrays and not name.endswith('$') and isinstance(rhs.constant,(int,float)):
                if not float(rhs.constant).is_integer() or not -32768<=rhs.constant<=32767:
                    raise Unsupported('Leap numeric arrays cannot hold this floating-point or out-of-range value')
            return [lhs.text+' = '+rhs.text]
        m=re.match(r'DIM\s+([A-Za-z][A-Za-z0-9]*\$?)\s*\((.*)\)$',text,re.I)
        if m:
            name=m[1].upper()
            if name in self.string_lengths:
                if self.string_lengths[name]>31: raise Unsupported('Fixed-length scalar string exceeds Leap capacity of 31')
                return [self.name(name)+' = "'+(' '*self.string_lengths[name])+'"']
            if name not in self.arrays: raise Unsupported('DIM declaration could not be resolved')
            sizes=self.arrays[name]; count=1
            for size in sizes if not name.endswith('$') else sizes[:-1]: count*=size
            width=f',{sizes[-1]+1}' if name.endswith('$') else ''
            out=[f'DIM {self.name(name,"array")}({count+1}{width})']
            if self.hoist_dims:
                out=[]
                if not name.endswith('$'):
                    out=[f'FOR QZINIT = 1 TO {count}',self.name(name,'array')+'(QZINIT) = 0','NEXT QZINIT']
            if name.endswith('$'):
                w=sizes[-1]
                if w>31: raise Unsupported('String array width exceeds supported 31-character assignment capacity')
                out += [f'FOR QZINIT = 1 TO {count}',self.name(name,'array')+'(QZINIT) = "'+(' '*w)+'"','NEXT QZINIT']
            return out
        m=re.match(r'FOR\s+([A-Za-z][A-Za-z0-9]*)\s*=\s*(.*?)\s+TO\s+(.*?)(?:\s+STEP\s+(.*))?$',text,re.I)
        if m:
            step=self.expr(m[4]) if m[4] else '1'
            if step=='0':
                self.zero_loop_counter+=1; label=f'QZW{self.zero_loop_counter}'; limit=f'QZLIMIT{self.zero_loop_counter}'
                self.zero_loops[m[1].upper()]=(label,limit)
                return [f'{self.name(m[1])} = {self.expr(m[2])}',f'{limit} = {self.expr(m[3])}',label+':']
            self.zero_loops.pop(m[1].upper(),None)
            return [f'FOR {self.name(m[1])} = {self.expr(m[2])} TO {self.expr(m[3])} STEP {step}']
        m=re.match(r'NEXT(?:\s+([A-Za-z][A-Za-z0-9]*))?$',text,re.I)
        if m:
            if m[1] and m[1].upper() in self.zero_loops:
                label,limit=self.zero_loops[m[1].upper()]
                return [f'IF {self.name(m[1])} <= {limit} THEN GOTO {label}']
            return ['NEXT'+(' '+self.name(m[1]) if m[1] else '')]
        m=re.match(r'PRINT\b(.*)$',text,re.I)
        if m:
            out=self.print_statement(m[1])
            changed={line.split()[0] for line in out if line.split()[0] in ('INK','PAPER','BRIGHT','FLASH','OVER','INVERSE')}
            if changed:
                symfile=Path(__file__).resolve().parents[1]/'build/host/build/test_basic.sym'
                symbols={a:int(b,16) for a,b in re.findall(r'^(\S+): EQU 0x([0-9a-f]+)',symfile.read_text(),re.M|re.I)}
                pre=[f'QZPA{k} = PEEK({symbols["CURRENT_"+k]})' for k in sorted(changed)]
                out=pre+out+[f'{k} QZPA{k}' for k in sorted(changed)]
            return out
        m=re.match(r'(INK|PAPER|BORDER|BRIGHT|FLASH|OVER|INVERSE|PAUSE)\s+(.*)$',text,re.I)
        if m: return [m[1].upper()+' '+self.expr(m[2])]
        m=re.match(r'(BEEP|SOUND|POKE|OUT|PLOT)\s+(.*)$',text,re.I)
        if m:
            args=[self.expr(x) for x in split_args(m[2])]
            if len(args)!=2: raise Unsupported(f'{m[1]} needs two arguments')
            if m[1].upper()=='PLOT':
                self.need_pen=True
                return ['QZPX = '+args[0],'QZPY = '+args[1],f'PLOT QZPX,{self.graphics_height-1}-QZPY']
            if m[1].upper() in ('POKE','OUT'):
                if not self.allow_hardware: raise Unsupported(f'{m[1].upper()} needs a memory/port contract for the Leap runtime')
                self.notes.add('Raw PEEK/POKE/OUT were permitted explicitly; stock ROM/system-variable addresses may not be valid under Leap.')
            return [m[1].upper()+' '+','.join(args)]
        m=re.match(r'DRAW\s+(.*)$',text,re.I)
        if m:
            args=[self.expr(x) for x in split_args(m[1])]
            if len(args)!=2: raise Unsupported('Curved DRAW requires a graphics-package adaptation')
            self.need_pen=True
            return ['QZDX = '+args[0],'QZDY = '+args[1],f'LINE QZPX,{self.graphics_height-1}-QZPY TO QZPX+QZDX,{self.graphics_height-1}-(QZPY+QZDY)',
                    'QZPX = QZPX + QZDX','QZPY = QZPY + QZDY']
        m=re.match(r'INPUT\s+([A-Za-z][A-Za-z0-9]*\$?)$',text,re.I)
        if m: return ['INPUT '+self.name(m[1])]
        m=re.match(r'READ\s+(.*)$',text,re.I)
        if m:
            self.need_data=True; out=[]
            for v in split_args(m[1]):
                lhs=Parser(self,v).parse(); expected='1' if lhs.kind=='string' else '0'
                rhs='QZS$' if lhs.kind=='string' else 'QZN'
                name=re.match('[A-Za-z][A-Za-z0-9]*\$?',v)[0].upper()
                width=self.string_lengths.get(name) or (self.arrays[name][-1] if name.endswith('$') and name in self.arrays else None)
                if width: rhs=f'LEFT$({rhs}+"'+(' '*width)+f'",{width})'
                out+=['CALL QZREAD(0)',f'IF QZK <> {expected} THEN','PRINT "DATA TYPE MISMATCH"','END','ENDIF',
                      lhs.text+' = '+rhs]
            return out
        m=re.match(r'RESTORE(?:\s+(.*))?$',text,re.I)
        if m:
            self.need_data=True
            value=Parser(self,m[1]).parse().constant if m[1] else 0
            if not isinstance(value,int):
                return ['CALL QZRESTORE('+self.expr(m[1])+')']
            index=next((i for n,i in self.data_lines if n>=value),len(self.data))
            if self.data_backend=='packed': return ['CALL QZRESTORE('+str(value)+')']
            return [f'QZDP = {index}']
        if text.upper() in ('STOP','END'): return ['END']
        if text.upper()=='CLS': return ['CLS']
        if text.upper()=='RANDOMIZE':
            self.notes.add('RANDOMIZE uses Leap startup RNG state; no identical Sinclair sequence is promised.'); return []
        if re.match(r'(LOAD|SAVE|MERGE|ON\s+ERR|DRAW|CIRCLE|CLEAR|NEW|DEF\s+FN)\b',text,re.I):
            raise Unsupported('Needs explicit adaptation: '+text.split()[0].upper())
        raise Unsupported('Unsupported statement: '+text[:65])
    def print_statement(self,text):
        if not text.strip(): return ['PRINT']
        ts=tokens(text); pieces=[]; current=[]; depth=0
        for t in ts:
            depth+=int(t=='(')-int(t==')')
            if t in (';',',') and depth==0:
                pieces.append((' '.join(current),t)); current=[]
            else: current.append(t)
        if current: pieces.append((' '.join(current),''))
        out=[]
        for item,sep in pieces:
            m=re.match(r'(AT|TAB|INK|PAPER|BRIGHT|FLASH|OVER|INVERSE)\s+(.*)',item,re.I)
            if m:
                key=m[1].upper()
                # AT row,col is split by the same comma used for PRINT zones.
                if key=='AT':
                    if sep!=',' or len(pieces)<2: raise Unsupported('PRINT AT needs row and column')
                    # handled below by the sequential parser
                    return self.print_tokens(ts)
                out.append(key+' '+self.expr(m[2])); continue
            if item:
                expr=Parser(self,item,allow_long_string=True).parse()
                if re.search(r'CHR\$\((?:[0-9]|[12][0-9]|3[01])\)',expr.text):
                    raise Unsupported('Embedded PRINT control codes need explicit colour/cursor translation')
                if expr.kind=='string' and isinstance(expr.constant,str):
                    chunks=[expr.constant[i:i+31] for i in range(0,len(expr.constant),31)] or ['']
                    out+=['PRINT "'+chunk+'"'+(';' if i<len(chunks)-1 else sep) for i,chunk in enumerate(chunks)]
                else: out.append('PRINT '+expr.text+sep)
            elif sep: out.append('PRINT '+sep)
        if pieces and pieces[-1][1] and not out: out=['PRINT '+pieces[-1][1]]
        if out and not out[-1].startswith('PRINT') and ts[-1] not in (';',','): out.append('PRINT')
        return out
    def print_tokens(self,ts):
        out=[]; i=0
        while i<len(ts):
            key=ts[i]
            if key in ('AT','TAB','INK','PAPER','BRIGHT','FLASH','OVER','INVERSE'):
                i+=1; start=i; depth=0; fields=[]
                while i<len(ts):
                    t=ts[i]; depth+=int(t=='(')-int(t==')')
                    if depth==0 and t in (';',','):
                        fields.append(' '.join(ts[start:i])); i+=1; start=i
                        if key!='AT' or len(fields)==2: break
                    else: i+=1
                if start<i and (not fields or key=='AT' and len(fields)<2): fields.append(' '.join(ts[start:i]))
                if len(fields)!=(2 if key=='AT' else 1): raise Unsupported(f'Invalid PRINT {key}')
                out.append(key+' '+','.join(self.expr(x) for x in fields))
            else:
                start=i; depth=0
                while i<len(ts):
                    depth+=int(ts[i]=='(')-int(ts[i]==')')
                    if depth==0 and ts[i] in (';',','): break
                    i+=1
                item=' '.join(ts[start:i]); sep=ts[i] if i<len(ts) else ''
                if i<len(ts): i+=1
                out+=self.print_statement(item+sep)
        if out and not out[-1].startswith('PRINT') and ts[-1] not in (';',','): out.append('PRINT')
        return out
    def convert(self):
        translated=[]
        for n,text in self.rows:
            self.line=n
            self.pending=[]
            try: block=self.statements(split_statements(text))
            except Unsupported as error:
                self.error(n,str(error)); block=[f'REM BLOCKED SOURCE LINE {n}']
            translated.append((n,block))
        pre=[]
        if self.hoist_dims:
            for name,sizes in self.arrays.items():
                count=1
                for size in sizes if not name.endswith('$') else sizes[:-1]: count*=size
                width=f',{sizes[-1]+1}' if name.endswith('$') else ''
                pre.append(f'DIM {self.name(name,"array")}({count+1}{width})')
        if self.returns:
            pre+=[f'DIM QZSTACK({self.stack_depth+1})','QZSP = 0']
        if self.need_data:
            if self.data_backend=='packed':
                pre+=['CALL QZLEVEL(1)'] if self.levels else ['QZBASE = 0',f'QZCOUNT = {len(self.data_lines)}',f'QZEND = {self.data_end}',*pointer(self.data_offsets[0] if self.data_offsets else self.data_end)]
            else: pre+=['QZDP = 0']
        if self.need_pen: pre+=['QZPX = 0','QZPY = 0']
        self.output=pre
        for n,block in translated:
            if n in self.labels: self.output.append(f'QL{n}:')
            first=len(self.output)+1; self.output+=block
            self.mapping.append(dict(source_line=n,output_start=first,output_lines=len(block)))
        self.output.append('END')
        if self.returns:
            self.output+=['QZRETURN:','IF QZSP <= 0 THEN','PRINT "RETURN WITHOUT GOSUB"','END','ENDIF',
                          'QZRET = QZSTACK(QZSP)','QZSP = QZSP - 1']
            self.output += [f'IF QZRET = {i} THEN GOTO {label}' for i,label in enumerate(self.returns,1)]
            self.output+=['PRINT "INVALID RETURN"','END']
        if self.need_floor: self.output+=['DEF FN QZFLOOR(QZFX) = INT(QZFX)-(QZFX<INT(QZFX))']
        if self.dynamic_jump:
            self.output+=['QZDISPATCH:']+[f'IF QZJUMP <= {n} THEN GOTO QL{n}' for n in self.numbers]+['END']
        if self.need_data:
            if self.data_backend=='packed':
                self.output+=reader_source(len(self.data_lines),self.data_offsets[0] if self.data_offsets else self.data_end,self.data_end)
                if self.levels:
                    self.output+=['PROC QZLEVEL(QZLV):']
                    for i,level in enumerate(self.levels,1):
                        self.output += [f'IF QZLV = {i} THEN',f'QZBASE = {level["base"]}',f'QZCOUNT = {level["count"]}',f'QZEND = {level["end"]}',
                                        f'QZFIRST = {level["first"]}',f'QZCHARS = {level["chars"]}','ENDIF']
                    self.output += pointer('QZCHARS')+['FOR QZCG = 0 TO 167','POKE 61824+QZCG,USR(62464)','NEXT QZCG']+pointer('QZBASE+QZFIRST')+['ENDP']
            elif len(self.data)>128:
                self.error(0,f'{len(self.data)} DATA items exceed the inline backend limit of 128. Extracted data is in the report; a packed-data runtime backend is required.','DATA_BACKEND')
                self.output+=['REM BLOCKED LARGE DATA BACKEND']
            else:
                self.output+=['PROC QZREAD(QZARG):',f'IF QZDP >= {len(self.data)} THEN','PRINT "OUT OF DATA"','END','ENDIF']
                for i,(n,value) in enumerate(self.data):
                    if value.kind=='string' and len(value.constant)>31:
                        self.error(n,'DATA string exceeds Leap 31-character scalar capacity','STRING_LENGTH')
                    self.output+=[f'IF QZDP = {i} THEN',f'QZK = {int(value.kind=="string")}',
                                  ('QZS$' if value.kind=='string' else 'QZN')+' = '+value.text,'ENDIF']
                self.output+=['QZDP = QZDP + 1','ENDP','PROC QZRESTORE(QZRL):',f'QZDP = {len(self.data)}']
                for n,i in reversed(self.data_lines): self.output += [f'IF QZRL <= {n} THEN',f'QZDP = {i}','ENDIF']
                self.output+=['ENDP']
        for i,line in enumerate(self.output,1):
            if len(line)>127:
                owner=next((m['source_line'] for m in self.mapping if m['output_start']<=i<m['output_start']+m['output_lines']),0)
                self.error(owner,f'Generated line {i} exceeds Leap limit ({len(line)} characters)','LINE_LENGTH')
        source_bytes=sum(len(x)+3 for x in self.output)
        if source_bytes>=13222 and not self.stream_source: self.error(0,f'Generated source needs {source_bytes} bytes before compiler symbols; host pool is 13222 bytes. Packed data/offline staging is required.','SOURCE_BUDGET')
        return dict(buildable=not self.diagnostics,diagnostics=self.diagnostics,notes=sorted(self.notes),
                    source_record_bytes=source_bytes,output_lines=len(self.output),data_items=len(self.data),
                    line_mapping=self.mapping,names=[dict(kind=k[0],original=k[1],leap=v) for k,v in self.names.items()],
                    data=[dict(line=n,value=value.constant) for n,value in self.data])


def read_segments(path):
    segments=[[]]; previous=-1
    for physical,text in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
        if not text.strip(): continue
        m=re.fullmatch(r'\s*(\d+)\s+(.*)',text)
        if not m: raise ValueError(f'Expected numbered BASIC at physical line {physical}')
        number=int(m[1])
        if number<=previous: segments.append([])
        segments[-1].append((number,m[2])); previous=number
    if not segments[0]: raise ValueError('Empty listing')
    return segments


def convert_file(source,output,segment=None,profile=None,**options):
    segments=read_segments(source)
    policy=json.loads(profile.read_text()) if profile else None
    if policy:
        if segment is None: segment=policy.get('segment',0)
        for key in ('data_backend','stream_source','udg_escapes','hoist_dims'): options[key]=policy.get(key,options.get(key))
    if segment is None and len(segments)>1:
        raise ValueError(f'Listing contains {len(segments)} programs; choose --segment 0..{len(segments)-1}')
    segment=segment or 0
    if not 0<=segment<len(segments): raise ValueError('Segment index is out of range')
    rows=segments[segment]
    if policy:
        rows=[(n,policy.get('overrides',{}).get(str(n),': '.join(s for s in split_statements(t) if s not in policy.get('remove_statements',{}).get(str(n),[])))) for n,t in rows]
    c=Converter(rows,**options); report=c.convert()
    if policy and policy.get('level_files'):
        all_data=bytearray(); levels=[]
        base_data={n:t for n,t in rows if re.match('DATA\\b',t,re.I)}
        for entry in policy['level_files']:
            level_rows=read_segments(Path(entry['listing']))[0]
            merged=dict(base_data); merged.update({n:t for n,t in level_rows if re.match('DATA\\b',t,re.I)})
            level=Converter(sorted(merged.items()))
            base=len(all_data); all_data+=level.packed_data
            chars=len(all_data); glyphs=Path(entry['charset']).read_bytes()
            if len(glyphs)!=168: raise ValueError('Expected 168-byte character set')
            all_data+=glyphs
            levels.append(dict(base=base,count=len(level.data_lines),first=level.data_offsets[0],end=level.data_end,chars=chars))
        c=Converter(rows,**options); c.levels=levels; c.packed_data=bytes(all_data); report=c.convert()
        report['levels']=levels
        if len(all_data)>23376:
            report['buildable']=False
            report['diagnostics'].append(dict(line=0,code='ASSET_BUDGET',message=f'Packed levels need {len(all_data)} bytes; cartridge data capacity is 23376'))
    if policy: report['profile']=str(profile.resolve()); report['adaptations']=policy
    report.update(input=str(source.resolve()),segment=segment,segments=len(segments))
    output.parent.mkdir(parents=True,exist_ok=True)
    actual=output if report['buildable'] else output.with_name(output.stem+'.partial'+output.suffix)
    if any(not line.isascii() for line in c.output):
        report['buildable']=False
        report['diagnostics'].append(dict(line=0,code='CHARACTER_SET',message='Non-ASCII listing characters require explicit character mapping'))
        actual=output.with_name(output.stem+'.partial'+output.suffix)
    actual.write_text('\n'.join(c.output)+'\n',encoding='ascii',errors='backslashreplace')
    report['output']=str(actual.resolve())
    if c.data_backend=='packed':
        asset=output.with_suffix('.data.bin'); asset.write_bytes(c.packed_data)
        report['packed_data']=str(asset.resolve()); report['packed_data_bytes']=len(c.packed_data)
    output.with_suffix('.conversion.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--segment',type=int)
    ap.add_argument('--allow-hardware',action='store_true',help='Preserve raw PEEK/POKE/OUT after auditing the Leap memory/port map')
    ap.add_argument('--udg-escapes',action='store_true',help='Interpret backslash a..u listing escapes as UDG characters')
    ap.add_argument('--graphics-height',type=int,choices=(176,192),default=176)
    ap.add_argument('--data-backend',choices=('inline','packed'),default='inline')
    ap.add_argument('--stream-source',action='store_true')
    ap.add_argument('--profile',type=Path)
    args=ap.parse_args()
    try: report=convert_file(args.source,args.output,args.segment,profile=args.profile,allow_hardware=args.allow_hardware,udg_escapes=args.udg_escapes,graphics_height=args.graphics_height,data_backend=args.data_backend,stream_source=args.stream_source)
    except (ValueError,Unsupported) as error: ap.exit(2,str(error)+'\n')
    for issue in report['diagnostics']: print(f'Line {issue["line"]}: {issue["code"]}: {issue["message"]}')
    print(f'{report["output"]}: {report["output_lines"]} lines; {len(report["diagnostics"])} blocking diagnostics')
    return 0 if report['buildable'] else 2


if __name__=='__main__':
    raise SystemExit(main())
