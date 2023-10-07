from types import FunctionType
from typing import Literal, Self, Any
from inspect import isclass, getframeinfo, stack
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
        callback:str = None
        length:int = 0
        for _i in range(repeat+1):
            print('\r' + ' ' * (length + dots), end='\r')
            if callback is None:
                callback = func(*text, sep=sep, end='')
                length = len(callback.encode())
            else:
                func(*text, sep=sep, end='')
            for i in range(dots):
                print('.', end='' if (_i < repeat or i+1 < dots) else end)
                sleep(1)
        return callback

    @staticmethod
    def log(*text:str, sep=' ', end='\n') -> str:
        _output = sep.join(map(str, text))
        print(_output, end=end)
        return _output

    @staticmethod
    def info(*text:str, sep=' ', end='\n') -> str:
        _caller = getframeinfo(stack()[1][0])
        text = map(str, text)
        _output = sep.join((
            f'<{_caller.filename.split(__class__.BACKSLASH)[-1]}:{_caller.lineno}>', *text
        ))
        print(_output, end=end)
        return _output

    @staticmethod
    def warn(*text:str, sep=' ', end='\n\n') -> str:
        _caller = getframeinfo(stack()[1][0])
        text = map(str, text)
        _output = sep.join((
            f'\n<{_caller.filename.split(__class__.BACKSLASH)[-1]}:{_caller.lineno}>', *text
        ))
        print(_output, end=end)
        return _output

console = Console