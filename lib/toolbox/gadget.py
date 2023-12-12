from __future__ import annotations
from collections import namedtuple
from inspect import isclass
from ctypes import windll

def is_number(_) -> bool:
    try: _ = float(_) # @IgnoreException
    except (ValueError, TypeError): return False
    else: return True

def is_integer(_) -> bool:
    try: _ = float(_) # @IgnoreException
    except (ValueError, TypeError): return False
    else: return True if _.is_integer() else False

def apchInt(_) -> int|float:
    return _ if not is_number(_) else int(_) if is_integer(_) else float(_)

class cmdl: ...

cmdl = namedtuple('command_set', ['command', 'value', 'delay'])

class Gadget:
    
    @staticmethod
    def multinput(txt:str, sep:str=None, forceFormat=..., autoFormat:bool=True):
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
    
    @staticmethod
    def formatter(command:str, split:str=None, strip:str=None) -> cmdl:
        final = list()
        command = command.split(split)
        elem:str
        for elem in command if not isinstance(command, dict) else command.values():
            elem = elem.strip(strip)
            match elem.capitalize():
                case ''|'None': elem = None
                case 'True': elem = True
                case 'False': elem = False
                case _: elem = (
                    int(elem)
                        if is_integer(elem) else
                    float(elem)
                        if is_number(elem) else
                    elem
                )
            final.append(elem)

        while len(final) < 3: final.append(None)
        return cmdl._make(final)
    
    @staticmethod
    def argsplit(cmd:str) -> tuple[str, ...]:
        return tuple([
            value.lower()
                if not is_number(value) else 
            int(value)
                if is_integer(value) else
            float(value)
                for value in cmd.split()
        ])
    
    @staticmethod
    def visualize(ntuple:tuple) -> str:
        """a little gadget for namedtuple, displays its key-name with corresponding value conveniently."""
        return ', '.join(map(lambda key: f'{key} = {getattr(ntuple, key)}', ntuple._fields))
    
    @staticmethod
    def setGeometry(width:int=1280, height:int=720, window=...) -> str:

        ratio = windll.shcore.GetScaleFactorForDevice(0)/100

        ## ------------------------------ ##
        #     1080       864               #
        #   original -> scaled             #
        #   original <- scaled (reversed)  #
        ## ------------------------------ ##

        def scaler(length:int, reversed=False):
            nonlocal ratio
            return int(length * ratio) if reversed else int(length / ratio)
        
        class viewport:
            width = scaler(window.winfo_screenwidth(), reversed=True)
            height = scaler(window.winfo_screenheight(), reversed=True)

        return f'{scaler(width)}x{scaler(height)}+{scaler((viewport.width - width)/2)}+{scaler((viewport.height - height)/2)}'
