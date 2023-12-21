from types import FunctionType
from typing import Literal
from inspect import Traceback, getframeinfo, stack
from traceback import format_stack
from collections import namedtuple as ntuple
from time import sleep
from re import search
from dataclasses import asdict

class Console:

    BACKSLASH = '\u005C'
    mode:Literal['normal', 'debug'] = 'debug'

    @classmethod
    def load(cls, func:FunctionType, *text:str, sep=' ', end='\n', dots:int=4, repeat:int=0, mode:Literal['debug']=...):
        cal = getframeinfo(stack()[1][0])
        cbf:str = None
        length:int = 0
        if mode.__ne__('debug') or cls.mode.__eq__('debug'):
            for loop in range(repeat+1):
                if not loop:
                    cbf = func(*text, sep=sep, end='', caller=cal)
                    length = len(' '.join(cbf).encode())                    
                else:
                    sleep(1)
                    print('\r' + ' ' * (length + dots), end='\r')
                    func(*text, sep=sep, end='', caller=cal)

                for i in range(dots):
                    sleep(1)
                    print('.', end='' if (loop < repeat or i+1 < dots) else end, flush=True)
        else:
            cbf = func(*text, sep=sep, end='', caller=cal, mode=mode)
        
        return cbf.result if isinstance(cbf, tuple) else cbf

    @classmethod
    def log(cls, *text:str, sep=' ', end='\n', caller:Traceback=..., mode:Literal['debug']=...) -> str:
        result = sep.join(map(str, text))
        print(result, end=end) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
        
        return result

    @classmethod
    def info(cls, *text:str, sep=' ', end='\n', caller:Traceback=..., mode:Literal['debug']=...) -> str:
        cal = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
        result = sep.join(map(str, text))
        prefix = f'<{cal.filename.split(cls.BACKSLASH)[-1]}:{cal.lineno}>'
        print(prefix, result, end=end) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
        
        return (
            result
                if not isinstance(caller, Traceback) else 
            ntuple('callback', ('result', 'prefix'))(result=result, prefix=prefix)
        )
    
    @classmethod
    def debug(cls, obj:object, end='\n', caller:Traceback=..., mode:Literal['debug']=...):

        def parentheless(string:str, sep:str|tuple[str, ...]=',', symbols:tuple[str, str]=('(', ')'), strip:str=None):
            class symbols:
                nonlocal sep, symbols
                enter, leave = symbols
            flags = list()
            layer = 0
            prev = 0
            for index, char in enumerate(string):
                match char:
                    case symbols.enter: layer += 1
                    case symbols.leave: layer -= 1
                    case _ if (char in sep) and (layer == 0): flags.append(slice(prev, index)); prev = index + 1
            
            flags.append(slice(prev, None))

            retval = list()
            for scope in flags: retval.append(string[scope].strip(strip))
            
            return retval

        varname = None
        name = f'{cls.__name__.lower()}.{stack()[0][3]}'
        for line in reversed(format_stack()):
            if name in line:
                for elem in parentheless(', '.join(map(lambda _: _.strip(), line.splitlines()))):
                    if name in elem:
                        regex = r'(?<=' + r'\.'.join(name.split('.')) + r'\()[A-Z_a-z0-9]+(?=\))'
                        varname = search(regex, elem)
                        break

        cal = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
        print(
            f'<{cal.filename.split(cls.BACKSLASH)[-1]}:{cal.lineno}>',
            f'{varname.group()}: {obj}' if varname is not None else obj, type(obj),
            end=end
        ) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
        
        return obj

    @classmethod
    def viewer(cls, clsname: str = 'dataclass', obj: Literal['<instance dataclass>'] = None, sep='\n', end='\n', caller: Traceback = ..., mode: Literal['debug'] = ...) -> Literal['<object metadata>']:
        cal = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
        if obj is not None:
            attr = asdict(obj)
            print(
                f'<{cal.filename.split(cls.BACKSLASH)[-1]}:{cal.lineno}> (',
                *map(lambda key: '\t'f'{key}: {attr.get(key)}', attr),
                f') <instance {clsname}>', sep=sep, end=end
            ) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...
        else:
            print(obj, type(obj), end=end) if (mode.__ne__('debug') or cls.mode.__eq__('debug')) else ...

        return obj

console = Console