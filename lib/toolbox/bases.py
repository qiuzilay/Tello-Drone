import enum
class String(str):
    
    def __init__(self, _):
        super().__init__()

    @property
    def length(self):
        return len(self)
    
class Enum(enum.Enum):
    def __get__(self, obj, type=...): return self.value