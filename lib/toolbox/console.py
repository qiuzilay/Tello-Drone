from types import FunctionType
from typing import Literal
from inspect import getframeinfo, stack, Traceback
from time import sleep

class Console:

    BACKSLASH = '\u005C'
    debug = True

    @classmethod
    def load(cls, func:FunctionType, *text:str, sep=' ', end='\n', dots:int=4, repeat:int=0, mode:Literal['debug']=...):
        cal = getframeinfo(stack()[1][0])
        cbf:str = None
        length:int = 0
        if mode.__ne__('debug') or cls.debug:
            for _i in range(repeat+1):
                print('\r' + ' ' * (length + dots), end='\r')
                if cbf is None:
                    cbf = func(*text, sep=sep, end='', caller=cal)
                    length = len(cbf.encode())
                else:
                    func(*text, sep=sep, end='')
                for i in range(dots):
                    sleep(1)
                    print('.', end='' if (_i < repeat or i+1 < dots) else end)
        else:
            cbf = func(*text, sep=sep, end='', caller=cal, mode=mode)
        return cbf

    @classmethod
    def log(cls, *text:str, sep=' ', end='\n', caller:Traceback=..., mode:Literal['debug']=...) -> str:
        ret = sep.join(map(str, text))
        print(ret, end=end) if (mode.__ne__('debug') or cls.debug) else ...
        return ret

    @classmethod
    def info(cls, *text:str, sep=' ', end='\n', caller:Traceback=..., mode:Literal['debug']=...) -> str:
        cal = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
        ret = sep.join(map(str, text))
        print(f'<{cal.filename.split(cls.BACKSLASH)[-1]}:{cal.lineno}>', ret, end=end) if (mode.__ne__('debug') or cls.debug) else ...
        return ret
    
console = Console