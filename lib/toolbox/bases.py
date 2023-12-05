class String(str):
    
    def __init__(self, _):
        super().__init__()

    @property
    def length(self):
        return len(self)