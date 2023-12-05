from __future__ import annotations
from inspect import signature, isfunction
from typing import Iterable, Callable, NewType
from sys import version_info

try: from typing import Self
except ImportError: print('Failed to import class typing.Self caused your Python Environment version is lower than 3.11.') if version_info < (3, 11) else ...

class Self: ...
class Numeric: ...
Numeric = NewType('Numeric', [int, float])

class array:
    
    def __init__(self, *values) -> Self:
        
        self.core = list()
        self.iter = 0
        
        self.core.extend(self.__unpack(values))
    
    def __len__(self) -> int:
        return len(self.core)
    
    def __getitem__(self, index:int|slice) -> Self:
        return self.__class__(self.core[index.start:index.stop:index.step]) if isinstance(index, slice) else self.core[index]

    def __setitem__(self, index:int, value):
        self.core[index] = value
    
    def __iter__(self):
        for _ in self.core: yield _
    
    def __next__(self):
        if self.iter < self.length:
            self.iter += 1
            return self[self.iter-1]
        else:
            self.iter = 0
            raise StopIteration
    
    def __str__(self) -> str:
        final = str()
        for _ in self:
            final = (
                final + f"{', ' if final else ''}" + f"'{_}'"
                    if isinstance(_, str) else
                final + f"{', ' if final else ''}" + f"{_}"
            )
        return f'[{final}]'

    def __add__(self, values:Iterable) -> array:
        return self.__class__(*self, *values)
    
    def __sub__(self, values:Iterable) -> array:
        def __callback(i, elem):
            nonlocal values
            try: return elem.__ne__(values[i])
            except IndexError: return True
        return self.filter(__callback)
    
    def reverse(self) -> Self:
        self.core = list(reversed(self.core))
        return self
    
    def reversed(self) -> array:
        return self.__class__(reversed(self.core))
    
    def append(self, *args) -> Self:
        self.core.extend(args)
        return self
    
    def prepend(self, *args) -> Self:
        self.core, _ = list(args), self.core
        self.core.extend(_)
        return self
    
    def concat(self, *args) -> Self:
        self.core.extend(self.__unpack(args))
        return self
    
    def splice(self, index:int, delcount:int, *args) -> Self:
        self.core = self.core[:index] + list(args) + self.core[index+delcount:]
        return self

    def extend(self, index:int, delcount:int, *args) -> Self:
        self.core = self.core[:index] + list(self.__unpack(args)) + self.core[index+delcount:]
        return self
    
    def join(self, sep:str='') -> str:
        return sep.join(map(str, self))
    
    def shift(self):
        return self.core.pop(0)
    
    def pop(self):
        return self.core.pop()
    
    def filter(self, callback:Callable) -> array:
        params = len(signature(callback).parameters)
        assert (0 < params < 3), "The callback function can only have at most 1 or 2 parameters only"
        return self.__class__(value for index, value in enumerate(self) if callback(*(index, value) if params > 1 else (value,)))
        
    def any(self, callback:Callable) -> bool:
        params = len(signature(callback).parameters)
        assert (0 < params < 3), "The callback function can only have at most 1 or 2 parameters only"
        try:
            for index, value in enumerate(self):
                assert not callback(*(index, value) if params > 1 else (value,))
        except AssertionError:
            return True
        else:
            return False
        
    def all(self, callback:Callable) -> bool:
        params = len(signature(callback).parameters)
        assert (0 < params < 3), "The callback function can only have at most 1 or 2 parameters only"
        try:
            for index, value in enumerate(self):
                assert callback(*(index, value) if params > 1 else (value,))
        except AssertionError:
            return False
        else:
            return True
    
    def reduce(self, callback:Callable[[Numeric], Numeric], init:Numeric=...) -> Numeric:
        if init is not Ellipsis:
            for value in self:
                init = callback(init, value)
        else:
            for index, value in enumerate(self):
                init = value if not index else callback(init, value)
        return int(init) if float(init).is_integer() else float(init)
    
    def copy(self) -> array:
        return self.__class__(self)
    
    def each(self, callback:Callable|type) -> Self:
        if isfunction(callback):
            params = len(signature(callback).parameters)
            assert params == 1, "The callback function can only have 1 parameter only"
        for i, elem in enumerate(self):
            self[i] = callback(elem)
        return self
    
    @property
    def length(self) -> int:
        return self.__len__()

    @staticmethod
    def __unpack(array:Iterable) -> Iterable:
        if len(array).__eq__(1) and (isinstance(*array, Iterable) and not isinstance(*array, str)):
            array, = array
        return array