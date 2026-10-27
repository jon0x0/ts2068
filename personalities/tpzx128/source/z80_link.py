"""Small label/EQU linker around SkoolKit's assembler for our generated drivers.

Supports instructions, DB/DW, EQU and scoped .labels; deliberately not a
sjasmplus preprocessor. SkoolKit remains a host-only test/build dependency.
"""
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'tools/python'))
from skoolkit.z80 import Assembler
from skoolkit.textutils import split_unquoted

TOKEN=re.compile(r'(?<![\w])(?:\.[A-Za-z_][\w]*|[A-Za-z_][\w]*)(?![\w])')
QUOTED=re.compile(r"('[^']*'|\"[^\"]*\")")


def link(source,origin=0,symbols=None):
    symbols={key.lower():value for key,value in (symbols or {}).items()}
    records=[];scope='root';names=set(symbols)
    for number,line in enumerate(source.splitlines(),1):
        # Our sources never put semicolons inside quoted strings.
        line=line.split(';',1)[0].strip()
        if not line:continue
        label=None
        match=re.match(r'^([\w.]+):\s*(.*)$',line)
        if match:
            label,line=match.groups()
            if label.startswith('.'):label=scope+label
            else:scope=label
            label=label.lower();names.add(label)
        match=re.match(r'^([\w.]+)\s+equ\s+(.+)$',line,re.I)
        if match:
            name,expr=match.groups();names.add(name.lower())
            records.append((number,label,'equ',(name.lower(),expr),scope));continue
        if line.lower().startswith(('if','endif','define','include','org','assert')):
            raise ValueError('Unsupported assembler directive at line %d'%number)
        records.append((number,label,'code',line,scope))
    assembler=Assembler()
    def replace(expression,scope,pc,strict):
        parts=QUOTED.split(expression)
        for i,part in enumerate(parts):
            if i%2:
                if len(part)==3:parts[i]=str(ord(part[1]))
                elif part.startswith("'"):parts[i]='"'+part[1:-1]+'"'
                continue
            def resolve(match):
                token=match.group();key=(scope+token if token.startswith('.') else token).lower()
                if key in symbols:return str(symbols[key])
                if key in names:
                    if strict:raise ValueError('Unresolved symbol '+key)
                    return str(pc if expression.lower().startswith(('jr ','djnz ')) else 0)
                return token
            parts[i]=TOKEN.sub(resolve,part)
        return ''.join(parts)
    previous=None
    for iteration in range(10):
        pc=origin;output=bytearray()
        for number,label,kind,value,scope in records:
            if label:symbols[label]=pc
            if kind=='equ':
                name,expr=value
                expanded=replace(expr,scope,pc,False).replace('$','0x')
                if re.fullmatch(r'[\d\sxa-fA-F()+*/%<>&|^~-]+',expanded):
                    symbols[name]=int(eval(expanded,{'__builtins__':{}},{}))
                continue
            if not value:continue
            instruction=replace(value,scope,pc,iteration>0)
            instruction=re.sub(r'^db\s','DEFB ',instruction,flags=re.I)
            instruction=re.sub(r'^dw\s','DEFW ',instruction,flags=re.I)
            if instruction.upper().startswith(('DEFB ','DEFW ')):
                directive,arguments=instruction.split(None,1)
                evaluated=[]
                for item in split_unquoted(arguments,','):
                    item=item.strip()
                    if item.startswith('"'):
                        evaluated.append(item);continue
                    expression=re.sub(r'\$([0-9a-fA-F]+)',r'0x\1',item)
                    if not re.fullmatch(r'[\d\sxa-fA-F()+*/%<>&|^~-]+',expression):
                        raise ValueError('Invalid data expression '+item)
                    evaluated.append(str(int(eval(expression,{'__builtins__':{}},{}))))
                instruction=directive+' '+','.join(evaluated)
            data=assembler.assemble(instruction,pc)
            if not data:
                raise ValueError('Cannot assemble line %d at %04X: %s'%(number,pc,instruction))
            output.extend(data);pc+=len(data)
        state=(bytes(output),dict(symbols))
        if state==previous:return bytes(output),symbols
        previous=state
    raise ValueError('Assembler symbols did not converge')
