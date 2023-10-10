from types import FunctionType
from typing import Literal, Self, Any
from inspect import isclass, getframeinfo, stack, Traceback
from time import sleep

def is_integer(i):
    try:
        float(i)
    except ValueError:
        return False
    else:
        return float(i).is_integer()
    
def is_number(i):
    try:
        float(i)
    except ValueError:
        return False
    else:
        return True

class Gadget:
    
    @staticmethod
    def multinput(txt:str, sep:str=None, forceFormat:Any=..., autoFormat:bool=True):
        txt = txt.split(sep)
        return (
            tuple(map(forceFormat, txt)) if isclass(forceFormat) else tuple(txt)
        ) if not autoFormat else (
            tuple(map(lambda x: (
                int(x)
                    if is_integer(x) else 
                float(x)
                    if is_number(x) else
                str(x)
            ), txt))
        )
    
class Console:

    BACKSLASH = '\u005C'

    @staticmethod
    def load(func:FunctionType, *text:str, sep=' ', end='\n', dots:int=4, repeat:int=0):
        _caller = getframeinfo(stack()[1][0])
        callback:str = None
        length:int = 0
        for _i in range(repeat+1):
            print('\r' + ' ' * (length + dots), end='\r')
            if callback is None:
                callback = func(*text, sep=sep, end='', caller=_caller)
                length = len(callback.encode())
            else:
                func(*text, sep=sep, end='')
            for i in range(dots):
                print('.', end='' if (_i < repeat or i+1 < dots) else end)
                sleep(1)
        return callback

    @staticmethod
    def log(*text:str, sep=' ', end='\n', caller:Traceback=...) -> str:
        _output = sep.join(map(str, text))
        print(_output, end=end)
        return _output

    @classmethod
    def info(cls, *text:str, sep=' ', end='\n', caller:Traceback=...) -> str:
        _caller = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
        _output = sep.join(map(str, text))
        print(f'<{_caller.filename.split(cls.BACKSLASH)[-1]}:{_caller.lineno}>', _output, end=end)
        return _output

    @classmethod
    def warn(cls, *text:str, sep=' ', end='\n\n', caller:Traceback=...) -> str:
        _caller = getframeinfo(stack()[1][0]) if not isinstance(caller, Traceback) else caller
        _output = sep.join(map(str, text))
        print(f'\n<{_caller.filename.split(cls.BACKSLASH)[-1]}:{_caller.lineno}>', _output, end=end)
        return _output

console = Console