from typing import Literal, Any
from inspect import isclass, getframeinfo, stack

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

    backslash = '\u005C'

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
            f'<{_caller.filename.split(__class__.backslash)[-1]}:{_caller.lineno}>', *text
        ))
        print(_output, end=end)
        return _output

    @staticmethod
    def warn(*text:str, sep=' ', end='\n\n') -> str:
        _caller = getframeinfo(stack()[1][0])
        text = map(str, text)
        _output = sep.join((
            f'\n<{_caller.filename.split(__class__.backslash)[-1]}:{_caller.lineno}>', *text
        ))
        print(_output, end=end)
        return _output

console = Console