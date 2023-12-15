import enum
class String(str):
    
    def __init__(self, _):
        super().__init__()

    def parentheless(self, sep:str|tuple[str, ...]=',', symbols:tuple[str, str]=('(', ')'), strip:str=None) -> list:
        class symbols:
            nonlocal sep, symbols
            enter, leave = symbols
        flags = list()
        layer = 0
        prev = 0
        for index, char in enumerate(self):
            match char:
                case symbols.enter: layer += 1
                case symbols.leave: layer -= 1
                case _ if (char in sep) and (layer == 0): flags.append(slice(prev, index)); prev = index + 1
        
        flags.append(slice(prev, None))

        retval = list()
        for scope in flags: retval.append(self[scope].strip(strip))
        
        return retval

    @property
    def length(self):
        return len(self)
    
class Enum(enum.Enum):
    def __get__(self, obj, type=...): return self.value