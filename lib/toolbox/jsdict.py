from __future__ import annotations
from typing import Iterable, Sequence

class json(dict):

    def __init__(self, *args, **kwargs):
        def update(arr:Iterable):
            nonlocal kwargs
            _ = 0
            while str(_) in kwargs: _ += 1
            for elem in arr: kwargs[str(_)], _ = self.__anlys(elem), _ + 1
        
        if kwargs or len(args).__ne__(1):
           update(args)
        else: # kwargs is empty, and args contains one element only
            args, = args
            if isinstance(args, dict):
                kwargs = self.__anlys(args) # type conversion, dict-like -> json
            else:
                update(args)

        super().__init__(kwargs)
    
    def __setattr__(self, name:str, value):
        if value != 'null': self[name] = value
        else:
            try: del self[name]
            except KeyError|AttributeError: ...

    def __getattr__(self, name:str):
        try: return self[name]
        except KeyError: raise AttributeError(name)
        
    def __getitem__(self, key:str):
        return super().__getitem__(key)
    
    def __setitem__(self, key:str, value):
        return super().__setitem__(key, self.__anlys(value))
    
    def __anlys(self, obj):

        match obj:
            case dict():
                for k, val in obj.items():
                    obj[k] = self.__anlys(val)
                obj = self.__class__(**obj)
            case _ if isinstance(obj, str): ...
            case _ if isinstance(obj, Sequence) and not isinstance(obj, tuple):
                for i, elem in enumerate(obj): obj[i] = self.__anlys(elem)
            case _ if isinstance(obj, set):
                for elem in obj:
                    obj.remove(elem)
                    obj.add(self.__anlys(elem))
            case _: ...
            
        return obj