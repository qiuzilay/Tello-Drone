from typing import Iterable, Sequence

class CustomFunc:
    
    @staticmethod
    def load(arr:list|Sequence) -> list|Sequence:
        with open('./commands.txt', mode='r', encoding='UTF-8') as _cmds:
            for text in _cmds:
                if not text.startswith('#'):
                    arr.append(text.split())
        return arr
    

class CommandOverrideException(Exception):
    
    def __init__(self):
        self.message = 'Tello was forced to land cause an overriding command was triggered.'
        super().__init__(self.message)